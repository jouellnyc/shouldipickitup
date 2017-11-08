#!/usr/bin/python3

import re
import sys
import requests
import pandas as pd
from bs4 import BeautifulSoup as bsoup
from bokeh.io import output_file,show
from bokeh.layouts import gridplot
from bokeh.plotting import figure


if len(sys.argv) > 1:
    stock = sys.argv[1]
else:
    stock = 'goog'
    
plot=True
debug=True
mynanstring="NAAN"
num_pat=re.compile("-?[0-9]{1,9}[\.,]?[0-9]{0,2}")

""" URLS """ 
url_sales_ninc_eps="http://www.marketwatch.com/investing/stock/"+stock+"/financials/"
url_roic="http://www.marketwatch.com/investing/stock/"+stock+"/profile"
url_fcf="http://www.marketwatch.com/investing/stock/"+stock+"/financials/cash-flow/"
url_bvps="https://www.gurufocus.com/term/Book+Value+Per+Share/"+stock+"/Book-Value-per-Share"

"""         Functions           """  
def err_web(url):
    """ Catch the Errors from the Web Connections             """
    """ All or nothing here: If not 200 OK - exit the program """
    try:
        r = requests.get(url,timeout=10)
        #raise_for_status() never execs is connect/timeout occurs
        r.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        print ("HTTP Error:",errh)
        sys.exit(1)
    except requests.exceptions.ConnectionError as errc:
        print ("Fatal Error Connecting:",errc)
        sys.exit(1)
    except requests.exceptions.Timeout as errt:
        print ("Timeout Error:",errt)
        sys.exit(1)
    except requests.exceptions.RequestException as err:
        print ("OOps: Something Else",err)
        sys.exit(1)
    else:
        return r
            
def get_web_data():
    """ Get Data """
    print ("Retrieving HTML for ",stock)
    r_sales_ninc_eps = err_web(url_sales_ninc_eps)
    r_roic = err_web(url_roic)
    r_url_fcf = requests.get(url_fcf)
    r_bvps = requests.get(url_bvps)
    return r_sales_ninc_eps,r_roic,r_url_fcf,r_bvps 

def make_soup(r_sales_ninc_eps,r_url_fcf,r_bvps,r_roic):
    """         Soup Setup        """
    print ("Parsing HTML")
    #if you make it here, soup objects will be assigned ok
    soup_sales_ninc_eps  = bsoup(r_sales_ninc_eps.content,"lxml")
    soup_fcf  = bsoup(r_url_fcf.content,"lxml")
    soup_bvps = bsoup(r_bvps.content,"lxml")
    soup_roic = bsoup(r_roic.content,"lxml")
    print ("Pulling Data out of HTML")
    print ("")
    return soup_sales_ninc_eps,soup_fcf,soup_bvps,soup_roic

def nreny():
    """ Save some typing on a deeply nested if """
    print("No rev/eps/netinc years")

def calc_growth(last,first,period):
    """ Simple cagr calculation """
    return ((last/first)**(1/period)-1)

def prettify_num(num):
    """ Pretty print Growth Rate """
    return '%.2f'%(num*100)+"%"
 
def check_data(data):
    """ Return a Number and a Denomination Value (typically M or B)    """
    """ Ensure each list is filled by returning NAJO if no match       """
    
    if data is None:
        return None,None
    else:
        data_pat=re.compile("([-(]?[-(]?[0-9,]+\.?[0-9]{,2})([mMbB]?)")
        data_is_valid=data_pat.search(data)
        if data_is_valid:
            num   = data_is_valid.group(1)
            denom = data_is_valid.group(2)
            brc_pat=re.compile("\(")           
            braces=brc_pat.search(num)
            num = num.replace('(',"")
            num = num.replace(')',"")
            num = num.replace(",","")
                    
            if denom:
                denom_val=denom
            else:
                denom_val=None
            
            if braces:
                neg_pat=re.compile("-")
                is_neg_already=neg_pat.search(num)
                if is_neg_already:
                    return  float(num),denom_val
                else:
                    return -float(num),denom_val
            else:
                #print ("else",float(num))
                return float(num),denom_val
        else:
            return mynanstring,mynanstring


def get_years_rev_ninc_eps(soup_sales_ninc_eps):
    """ Years (Revenue,Net Inc and EPS - including USD and EUR """
    
    years_rev_ninc_eps=[]
    rev_text_pattern = re.compile("Fiscal year is \w+-\w+. All values \w+ millions")
    years_main_th_tag = soup_sales_ninc_eps.find('th',text=rev_text_pattern)
    try:
       years_links=years_main_th_tag.find_next_siblings()
    except AttributeError as e:
        print("No Rev-EPS-NINC web data patterns found")
        print("") 
        years_rev_ninc_eps=False
        return years_rev_ninc_eps
    else:
        rev_years_pattern = re.compile("201[0-9]")
        if years_links is not None:
            max=5
            for tag in years_links:
                if len(years_rev_ninc_eps) == max:
                    return years_rev_ninc_eps
                else:
                    years_link_data=tag.string
                    if years_link_data is not None:
                        if rev_years_pattern.match(years_link_data):
                            years_rev_ninc_eps.append(years_link_data)
                        else:
                            years_rev_ninc_eps.append(mynanstring)
        return years_rev_ninc_eps
                                     
def get_rev(soup_sales_ninc_eps,years_rev_ninc_eps):    
    """                      Revenue                       """
    revenue_master=[]
    revenue_inc_denom=''
    revenue_denom_master=[]
        
    a_href_sales = soup_sales_ninc_eps.find('a',attrs={'data-ref':'ratio_SalesNet1YrGrowth'})
    """ If we got here the http call succeeded so we will have a valid soup object  
        However, if no content found in a soup obj, bsoup returns a NoneType.
        So worst case a_href_sales becomes NoneType, but we don't kick up an AttributeError here.
    """
    try:
        """ if the soup object is null we will kick up the AttributeError here, so we try and group together."""
        sales_td_parent = a_href_sales.find_parent()
        sales_data_links = sales_td_parent.find_next_siblings("td",attrs={'class':'valueCell'})
    except AttributeError as e:
        print("No Sales data web patterns found")
        print("")    
        revenue=False
        return revenue,revenue_master,revenue_inc_denom
    else:
        if sales_data_links is not None:
            for link in sales_data_links:
                     rev_val=link.string
                     safe,denom_val = check_data(rev_val)
                     revenue_master.append(safe)
                     revenue_denom_master.append(denom_val)
        
        #Kludgily find the denominations we are looking for
        if all( x==revenue_denom_master[0] for x in revenue_denom_master):
            revenue_inc_denom=revenue_denom_master[0]+"illions"
        elif ( 'B' or 'b' ) in revenue_denom_master and ( 'M' or 'm' )  in revenue_denom_master:
            for i,(x,y) in enumerate(zip(revenue_denom_master,revenue_master)):
                if 'b' in x or 'B' in x:
                    revenue_master[i]=revenue_master[i]*1000
            revenue_inc_denom="Millions"
        else:
            revenue_inc_denom="Dollars"
           
        """ Extra checks to avoid script blow up         """
        """ And create our dataframe to calculating CAGR """
        if all(isinstance(item, float) for item in revenue_master)  and mynanstring not in years_rev_ninc_eps and \
        len(revenue_master) == len (years_rev_ninc_eps):
            revincdf = pd.DataFrame( { 'years' : years_rev_ninc_eps, 'years_strings': [ int(x) for x in years_rev_ninc_eps ], 'data' : revenue_master } )
            revenue_growth_master = ((revincdf['data'].max()/revincdf['data']) ** (1/(revincdf['years_strings'].max()-revincdf['years_strings']))-1)
            revenue_growth_master = revenue_growth_master.apply(prettify_num)
            revenue=True
        else:
            revenue=False
            revenue_growth_master=['NA', 'NA', 'NA', 'NA', 'NA']
            
        zipped_years=zip(years_rev_ninc_eps,revenue_master,revenue_growth_master)
        for year,rev,gr in zipped_years:
            print (stock,"had",rev,"Revenue in",year," Rate = ",gr)
        print("")
        return revenue,revenue_master,revenue_inc_denom
    
        
def get_ninc(soup_sales_ninc_eps,years_rev_ninc_eps):
    """                    Net Income                      """
    net_inc_denom=''
    net_inc_master=[]
    net_inc_denom_master=[]
    
    main_net_income_link = soup_sales_ninc_eps.find('td',attrs={'class':'rowTitle'},\
    text="Net Income Available to Common")
    try:
        net_income_values = main_net_income_link.fetchNextSiblings('td',class_="valueCell")
    except AttributeError as e:
        print("No Net Income data web patterns found")
        print("") 
        net_inc=False
        return net_inc,net_inc_master,net_inc_denom
    else:        
        for link in net_income_values:
            net_income_val=link.string
            safe,denom_val = check_data(net_income_val)
            net_inc_master.append(safe)
            net_inc_denom_master.append(denom_val)
                                   
        if all( x==net_inc_denom_master[0] for x in net_inc_denom_master):
            net_inc_denom=net_inc_denom_master[0]+"illions"
        elif ( 'B' or 'b' ) in net_inc_denom_master and ( 'M' or 'm') in net_inc_denom_master:
            for i,(x,y) in enumerate(zip(net_inc_denom_master,net_inc_master)):
                if 'b' in x or 'B' in x:
                    net_inc_master[i]=net_inc_master[i]*1000
            net_inc_denom="Millions"
        else:
            net_inc_denom="Dollars"
      
        if all(isinstance(item, float) for item in net_inc_master) and mynanstring not in years_rev_ninc_eps\
        and len(net_inc_master) == len (years_rev_ninc_eps):
            netincdf = pd.DataFrame( { 'years' : years_rev_ninc_eps, 'years_strings': [ int(x) for x in years_rev_ninc_eps ], 'data' : net_inc_master } )
            net_inc_growth_master = ((netincdf['data'].max()/netincdf['data']) ** (1/(netincdf['years_strings'].max()-netincdf['years_strings']))-1)
            net_inc_growth_master = net_inc_growth_master.apply(prettify_num)
        else:
             net_inc_growth_master= ['NA', 'NA', 'NA', 'NA', 'NA']
        
        """ Net Income Summary """ 
        zipped_ninc=zip(years_rev_ninc_eps,net_inc_master,net_inc_growth_master)
        for year,ninc,gr in zipped_ninc:
            print (stock,"had",ninc,"Net Income in",year," Rate = "+gr)
        print("")
        net_inc=True
        return net_inc,net_inc_master,net_inc_denom

def get_eps(soup_sales_ninc_eps,years_rev_ninc_eps):
    """              EPS                       """
    eps_master=[]
    eps_denom_master=[]
    eps_growth_master=[]
    
    main_eps_a_tag = soup_sales_ninc_eps.find('a',attrs={'data-ref':'ratio_Eps1YrAnnualGrowth'})
    try:
        main_eps_td_tag_parent = main_eps_a_tag.find_parent()
        eps_data=main_eps_td_tag_parent.find_next_siblings('td',attrs={'class':'valueCell'})
    except AttributeError as e:
        print("No EPS data web patterns found")
        print("") 
        eps=False
        return eps,eps_master
    else:
        if eps_data is None:
            print("No EPS data found at all")
            print("")    
            eps=False
            return eps,eps_master
        else:
            for tag in eps_data:
                        eps_val=tag.string
                        safe,denom_val = check_data(eps_val)
                        eps_master.append(safe)
                        eps_denom_master.append(denom_val)
                    
            if all(isinstance(item, float) for item in eps_master) and mynanstring not in years_rev_ninc_eps and \
            len(eps_master) == len (years_rev_ninc_eps):
                epsdf = pd.DataFrame( { 'years' : years_rev_ninc_eps, 'years_strings': [ int(x) for x in years_rev_ninc_eps ], 'data' : eps_master } )
                eps_growth_master = ((epsdf['data'].max()/epsdf['data']) ** (1/(epsdf['years_strings'].max()-epsdf['years_strings']))-1)
                eps_growth_master = eps_growth_master.apply(prettify_num)
            else:
                eps_growth_master= ['NA', 'NA', 'NA', 'NA', 'NA']
          
            """Summary"""
            zipped_eps=zip(years_rev_ninc_eps,eps_master,eps_growth_master)
            for year,es,gr in zipped_eps:
                print (stock,"had",es,"EPS in",year," Rate = ",gr)
            print("")
            eps=True
            return eps,eps_master
     
    
def get_fcf(soup_fcf):
    """                                      Free Cash Flow                 """
    fcf_denom=''
    years_fcf=[]
    fcf_master=[]
    fcf_denom_master=[]
    
    pattern = re.compile("\s+Free Cash Flow")
    fcf_text = soup_fcf.find(text=pattern)
    try:
        fcf_link_parent = fcf_text.find_parent()
        fcf_data = fcf_link_parent.find_next_siblings(attrs={'class':'valueCell'})
    except AttributeError as e:
        print("No FCF data web patterns found")
        print("")
        fcf=False
        return fcf,fcf_master,fcf_denom,years_fcf
    else:        
        for tag in fcf_data:
                fcf_val=tag.string
                safe,denom_val = check_data(fcf_val)
                fcf_master.append(safe)
                fcf_denom_master.append(denom_val)     
        
        if all( x==fcf_denom_master[0] for x in fcf_denom_master):
            fcf_denom=fcf_denom_master[0]+"illions"
        elif ( 'B' or 'b' ) in fcf_denom_master and ( 'M' or 'm' )  in fcf_denom_master:
            for i,(x,y) in enumerate(zip(fcf_denom_master,fcf_master)):
                if 'b' in x or 'B' in x:
                    fcf_master[i]=fcf_master[i]*1000
                    fcf_denom="Millions"
        else:
            fcf_denom="Dollars"
        
        """Fcf Years"""  
        fcf_years_text_h2 = soup_fcf.find('h2',text="Financing Activities")
        try:
            fcf_years_data_th=fcf_years_text_h2.find_next('th',attrs={'class':'rowTitle'})
            fcf_years_data = fcf_years_data_th.find_next_siblings()
            fcf_years_pattern = re.compile("201[0-9]")
        except AttributeError as e:
            print("No FCF years web patterns found")
            print("")
            fcf=False
            return fcf,fcf_master,fcf_denom,years_fcf
        else:
            for fcf_year in fcf_years_data:
                if fcf_year.string is not None and fcf_years_pattern.match(fcf_year.string):
                        years_fcf.append(fcf_year.string)
          
            if all(isinstance(item, float) for item in fcf_master) and mynanstring not in years_fcf and \
            len(fcf_master) == len (years_fcf) and all( item > 0 for item in fcf_master):
                fcfdf = pd.DataFrame( { 'years' : years_fcf, 'years_strings': [ int(x) for x in years_fcf ], 'data' : fcf_master } )
                fcf_growth_master = ((fcfdf['data'].max()/fcfdf['data']) ** (1/(fcfdf['years_strings'].max()-fcfdf['years_strings']))-1)
                fcf_growth_master = fcf_growth_master.apply(prettify_num)        
            else:
                fcf_growth_master= ['NA', 'NA', 'NA', 'NA', 'NA']
                 
            """Summary"""       
            zipped_fcf=zip(years_fcf,fcf_master,fcf_growth_master)
            for year,fcfl,gr in zipped_fcf:
                print (stock,"had",fcfl,"Free Cash Flow in",year," Rate = "+gr)
            print("")
            fcf=True
            return fcf,fcf_master,fcf_denom,years_fcf

def get_bvps(soup_bvps):
    """                                        BVPS                """
    years_bvps=[]
    bvps_master=[]
    bvps_denom_master=[]
    
    main_bvps_td_tag=soup_bvps.find('td',text="Book Value per Share")
    main_bvps_years = soup_bvps.find('div',attrs={'id':'target_def_historical_data'})
    try:
        bvps_data_in_links = main_bvps_td_tag.find_next_siblings()
        bvps_years_data = main_bvps_years.find_next('td').find_next_siblings()
    except AttributeError as e:
        print("No BVPS data web patterns found")
        print("")
        bvps=False
        return bvps,bvps_master,years_bvps
    else:   
        if bvps_data_in_links is not None:
            for tag in bvps_data_in_links:
                #print ("tag:",tag)    
                #print ("tag.string:",tag.string)
                bvps_val=tag.string
                safe,denom_val = check_data(bvps_val)
                if safe is not None:
                    bvps_master.append(safe)
                    bvps_denom_master.append(denom_val)
        else:
            bvps=False
            print("No BVPS data found")
            return bvps,bvps_master,years_bvps                
        
        """Years"""
        bvps_years_pat=re.compile('[0-9]{2}')
        if bvps_years_data is not None and len(bvps_years_data) > 0:
            for year in bvps_years_data[-5:]:
                #year will break w/html \'s, use year.string
                #just get the last 5 values
                matched_bvps_year = bvps_years_pat.search(year.string)
                if matched_bvps_year:
                    bvps_year = "20"+matched_bvps_year.group()
                    years_bvps.append(bvps_year)
                else:
                    bvps=False
                    print("No BVPS years data pattern found")
                    print('')
                    return bvps,bvps_master,years_bvps                
        else:
            bvps=False
            print("No BVPS years data found")
            print('')
            return bvps,bvps_master,years_bvps                
    
        if all(isinstance(item, float) for item in bvps_master) and mynanstring not in years_bvps and \
        len(bvps_master) == len(years_bvps) and len(bvps_master) > 0 and all( item > 0 for item in bvps_master):
            bvdf = pd.DataFrame( { 'years' : years_bvps , 'years_strings': [ int(x) for x in years_bvps ], 'data' : bvps_master } )
            bvps_growth_master = ((bvdf['data'].max()/bvdf['data']) ** (1/(bvdf['years_strings'].max()-bvdf['years_strings']))-1)
            bvps_growth_master = bvps_growth_master.apply(prettify_num)
            bvps=True
        else:
            bvps_growth_master= ['NA', 'NA', 'NA', 'NA', 'NA']                              
            
        """Summary"""
        bvps=True
        zipped_bvps=zip(years_bvps,bvps_master,bvps_growth_master)
        for year,bv,gr in zipped_bvps:
            print (stock,"had",bv,"BVPS in",year," Rate = ",gr)
        print("")
        return bvps,bvps_master,years_bvps
    
def get_roic(soup_roic):
    """               ROIC                     """
    pattern= re.compile("Return on Invested Capital")
    roic_p_tag=soup_roic.find('p',attrs={'class':'column'},text=pattern)
    try:
        roic_data=roic_p_tag.find_next_sibling('p',attrs={'class':'data lastcolumn'})
        #We are not actually plotting RIC as it's just one value. Leave as NavString
    except AttributeError as e:
        print("No Roic data web patterns found")
        print("")    
        roic=False
        return roic
    else:
        roic=roic_data.string
        print (stock,"had",roic,"ROIC")
        print("")
        return roic

""" Data Checks """
def check_years(years_bvps,years_rev_ninc_eps,years_fcf):
    if years_bvps ==  years_rev_ninc_eps == years_fcf == years_rev_ninc_eps:
        print ("OK: years_bvps,years_rev_ninc_eps,years_fcf, years_rev_ninc_eps are equal")
        return True
    else:
        print("Check years - something may be off" )
        
        
def check_data_blocks(eps_master,revenue_master,fcf_master,bvps_master,net_inc_master):
    if len(eps_master) == 5 and len(revenue_master) == 5 and len(fcf_master) == 5 and len(bvps_master) == 5 and len(net_inc_master) == 5:
        print ("OK: EPS, Revenue, FCF, BVPS, and Net Income all have 5 years of data")
        return True
    else:
        print("Check data - some data missing")

def get_links():
    """         Links                                     """
    links={ url_sales_ninc_eps:"Sales,NetInc,EPS", url_roic : "Roic", url_fcf : "Fcf", url_bvps:"Bvps" }
    for link,text in links.items():
        print(link+" =",text)
    print("")


def data_is_filled(years_bvps,years_rev_ninc_eps,years_fcf,eps_master,revenue_master,fcf_master,bvps_master,net_inc_master):
    if check_years(years_bvps,years_rev_ninc_eps,years_fcf) and check_data_blocks(eps_master,revenue_master,fcf_master,bvps_master,net_inc_master):
            print ("GREAT: Data for "+stock+" is filled for all years and big 5 numbers")

def plot_or_not(stock,roic,revenue,years_rev_ninc_eps,revenue_master,revenue_inc_denom,net_inc,net_inc_master,net_inc_denom,eps,eps_master,bvps,years_bvps,bvps_master,fcf,years_fcf,fcf_master,fcf_denom):
    """ Bokeh is ***awesome**** """
    ###print (roic,revenue,net_inc,bvps,eps,fcf)
    if plot:
        if (not roic) and (not revenue) and (not net_inc) and (not bvps) and (not eps) and (not fcf):
            print ("No data - plot will not be generated")
            print("")
        else:
            stock=stock.upper()
            print ("Plotting details for",stock)
            print ("")
            output_file("data/"+stock+".html", title=stock+" Financials")
            plot_net_inc = figure(plot_width=400, plot_height=400,title=stock+" Net Income", x_axis_label='Years',\
            y_axis_label='Net Income')
            plot_net_inc.line(years_rev_ninc_eps,net_inc_master,legend=net_inc_denom, line_width=2)
            
            
            plot_rev = figure(plot_width=400, plot_height=400,title=stock+" Revenue", x_axis_label='Years',\
            y_axis_label='Revenue')
            plot_rev.line(years_rev_ninc_eps,revenue_master,legend=revenue_inc_denom, line_width=2)
            
            
            plot_eps = figure(plot_width=400, plot_height=400,title=stock+" EPS", x_axis_label='Years',\
            y_axis_label='EPS')
            plot_eps.line(years_rev_ninc_eps,eps_master,legend="Dollars per Share", line_width=2)
            
            
            plot_bvps = figure(plot_width=400, plot_height=400,title=stock+" BVPS", x_axis_label='Years',\
            y_axis_label='BVPS')
            plot_bvps.line(years_bvps,bvps_master,legend="Book Value per Share", line_width=2)
            
            
            plot_fcf = figure(plot_width=400, plot_height=400,title=stock+" Free Cash Flow", x_axis_label='Years',\
            y_axis_label='Free Cash Flow')
            plot_fcf.line(years_fcf,fcf_master,legend=fcf_denom, line_width=2)
            
            plot_roic = figure(plot_width=400, plot_height=400,title=stock+" Roic")
            plot_roic.line([1,2,3,4,5],[1,2,3,4,5],legend=roic)
            
            # put all the plots in a grid layout
            p = gridplot( [[plot_rev,plot_net_inc,plot_eps],[plot_bvps,plot_fcf,plot_roic]] )
            show(p)

def main():
      
    r_sales_ninc_eps,r_roic,r_url_fcf,r_bvps                    = get_web_data()
    soup_sales_ninc_eps,soup_fcf,soup_bvps,soup_roic            = make_soup(r_sales_ninc_eps,r_url_fcf,r_bvps,r_roic)
    years_rev_ninc_eps                                          = get_years_rev_ninc_eps(soup_sales_ninc_eps)
    revenue,revenue_master,revenue_inc_denom                    = get_rev(soup_sales_ninc_eps,years_rev_ninc_eps)
    net_inc,net_inc_master,net_inc_denom                        = get_ninc(soup_sales_ninc_eps,years_rev_ninc_eps)
    eps,eps_master                                              = get_eps(soup_sales_ninc_eps,years_rev_ninc_eps)
    fcf,fcf_master,fcf_denom,years_fcf                          = get_fcf(soup_fcf)
    bvps,bvps_master,years_bvps                                 = get_bvps(soup_bvps)
    roic                                                        = get_roic(soup_roic)
    get_links()
    plot_or_not(stock,roic,revenue,years_rev_ninc_eps,revenue_master,revenue_inc_denom,net_inc,net_inc_master,net_inc_denom,eps,eps_master,bvps,years_bvps,bvps_master,fcf,years_fcf,fcf_master,fcf_denom)
    if debug:
        data_is_filled(years_bvps,years_rev_ninc_eps,years_fcf,eps_master,revenue_master,fcf_master,bvps_master,net_inc_master)
    
main()