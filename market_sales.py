#!/usr/bin/python3

import re
import sys
import requests
import pandas as pd
from bs4 import BeautifulSoup as bsoup
from bokeh.io import gridplot, show, output_file
from bokeh.plotting import figure

#Years from each link all match each other- done
#Length of data sets are filled to 5 - done
#Data Check for negative net inc, fcf, and bvsp - done  
#Blanks for values and None/Nonetype - done 
#Legend - millions vs billion - done 
#Normalize data w/mixed B and M - done
#Calc growth rate - use pandas df
#Get html for USD or EUR  - done
#If he soup objects are null - done

#TBD - fix up plot labels
#TBD - put into html table and 
#TBD - lable plot for USD or  EUR
#TBD can't find the page/can't connect/bad stock symbol
#TBD function to reuse local data vs web

if len(sys.argv) > 1:
    stock = sys.argv[1]
else:
    stock = 'shop'
#plot="False"
plot="True"


""" URLS """ 
url_sales_ninc_eps="http://www.marketwatch.com/investing/stock/"+stock+"/financials/"
url_roic="http://www.marketwatch.com/investing/stock/"+stock+"/profile"
url_fcf="http://www.marketwatch.com/investing/stock/"+stock+"/financials/cash-flow/"
url_bvps="https://www.gurufocus.com/term/Book+Value+Per+Share/"+stock+"/Book-Value-per-Share"

""" Get Data """
print ("Retrieving HTML for ",stock)
r_sales_ninc_eps = requests.get(url_sales_ninc_eps)
r_roic = requests.get(url_roic)
r_url_fcf = requests.get(url_fcf)
r_bvps = requests.get(url_bvps)

"""         Soup Setup        """
print ("Parsing HTML")
soup_url_sales_ninc_eps  = bsoup(r_sales_ninc_eps.content,"lxml")
soup_roic = bsoup(r_roic.content,"lxml")
soup_fcf  = bsoup(r_url_fcf.content,"lxml")
soup_bvps = bsoup(r_bvps.content,"lxml")
print ("Pulling Data out of HTML")
print ("")

"""         Functions           """  
num_pat=re.compile("-?[0-9]{1,9}[\.,]?[0-9]{0,2}")

def calc_growth(last,first,period):
    """ Simple cagr calculation """
    return ((last/first)**(1/period)-1)

def prettify_num(num):
    """ Pretty print Growth Rate """
    return '%.2f'%(num*100)+"%"
 
def check_data(data):
    """ Return a Number and a Denomination Value (typically M or B)    """
    """ Ensure each list is filled by returning NAJO if no match       """
    
    data_pat=re.compile("([-(]?[-(]?[0-9,]+\.?[0-9]{,2})([mMbB]?)")
    data_is_valid=data_pat.search(data)
    
    if data_is_valid:
        num   = data_is_valid.group(1)
        denom = data_is_valid.group(2)
        #print ("num",num)
        brc_pat=re.compile("\(")           
        braces=brc_pat.search(num)
        #print ("num1",num)
        num = num.replace('(',"")
        #print ("num2",num)
        num = num.replace(')',"")
        #print ("num3",num)
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
        return "NaJO","NaJO"

     
"""                      Revenue                       """
revenue_master=[]
years_rev_ninc_eps=[]
revenue_denom_master=[]
revenue_growth_master=[]
a_href_sales = soup_url_sales_ninc_eps.find('a',attrs={'data-ref':'ratio_SalesNet1YrGrowth'})
if a_href_sales:
    sales_td_parent = a_href_sales.find_parent()
    if sales_td_parent: 
        sales_data_links = sales_td_parent.find_next_siblings("td",attrs={'class':'valueCell'})
    if sales_td_parent:
        for link in sales_data_links:
             rev_val=link.string
             safe,denom_val = check_data(rev_val)
             if safe is not 'NaJO':
                 revenue_master.append(safe)
             if denom_val is not 'NaJO':
                 revenue_denom_master.append(denom_val)
    
        if all( x==revenue_denom_master[0] for x in revenue_denom_master):
            revenue_inc_denom=revenue_denom_master[0]+"illions"
        elif ( 'B' or 'b' ) in revenue_denom_master and ( 'M' or 'm' )  in revenue_denom_master:
            for i,(x,y) in enumerate(zip(revenue_denom_master,revenue_master)):
                if 'b' in x or 'B' in x:
                    revenue_master[i]=revenue_master[i]*1000
            revenue_inc_denom="Millions"
        else:
            revenue_inc_denom="Dollars"
            
        """ Years (+ Net Inc and EPS) """
        """ USD and EUR """
        rev_text_pattern = re.compile("Fiscal year is \w+-\w+. All values \w+ millions")
        years_main_th_tag = soup_url_sales_ninc_eps.find('th',text=rev_text_pattern)
        years_links=years_main_th_tag.find_next_siblings()
        rev_years_pattern = re.compile("201[0-9]")
            
        for tag in years_links:
            year_link_data=tag.string
            if year_link_data:
                if rev_years_pattern.match(tag.string):
                    years_rev_ninc_eps.append(tag.string)
        #years_rev_ninc_eps = ['2017','2016','2015','2014','2013']
        
        
        revdf = pd.DataFrame( { 'years' : years_rev_ninc_eps, 'years_strings': [ int(x) for x in years_rev_ninc_eps ], 'data' : revenue_master } )
        revenue_growth_master = ((revdf['data'].max()/revdf['data']) ** (1/(revdf['years_strings'].max()-revdf['years_strings']))-1)
        revenue_growth_master = revenue_growth_master.apply(prettify_num)
    
        zipped_years=zip(years_rev_ninc_eps,revenue_master,revenue_growth_master)
        for year,revenue,gr in zipped_years:
            print (stock,"had",revenue,"Revenue in",year," Rate = ",gr)
else:
    revenue_inc_denom="NA"
    print("No Sales data found at all")
print("")    


"""                    Net Income                      """
net_inc_master=[]
net_inc_denom_master=[]
net_inc_growth_master=[]
main_net_income_link = soup_url_sales_ninc_eps.find('td',attrs={'class':'rowTitle'},\
text="Net Income Available to Common")
if main_net_income_link:
    net_income_values = main_net_income_link.fetchNextSiblings('td',class_="valueCell")
    if net_income_values:
        for link in net_income_values:
                net_income_val=link.string
                safe,denom_val = check_data(net_income_val)
                if safe is not 'NaJO':
                     net_inc_master.append(safe)
                if denom_val is not 'NaJO':
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
        
        netincdf = pd.DataFrame( { 'years' : years_rev_ninc_eps, 'years_strings': [ int(x) for x in years_rev_ninc_eps ], 'data' : net_inc_master } )
        net_inc_growth_master = ((netincdf['data'].max()/netincdf['data']) ** (1/(netincdf['years_strings'].max()-netincdf['years_strings']))-1)
        net_inc_growth_master = net_inc_growth_master.apply(prettify_num)
         
        """ Net Income Summary """ 
        zipped_ninc=zip(years_rev_ninc_eps,net_inc_master,net_inc_growth_master)
        for year,ninc,gr in zipped_ninc:
            print (stock,"had",ninc,"Net Income in",year," Rate = "+gr)
        print("")
else:
    net_inc_denom="NA"
    print("No Net Income data found at all")
print("")   



"""              EPS                       """
eps_data=''
eps_master=[]
eps_denom_master=[]
eps_growth_master=[]
main_eps_td_tag_parent=''

main_eps_a_tag = soup_url_sales_ninc_eps.find('a',attrs={'data-ref':'ratio_Eps1YrAnnualGrowth'})
if main_eps_a_tag:
    main_eps_td_tag_parent = main_eps_a_tag.find_parent()
    if main_eps_td_tag_parent:
        eps_data=main_eps_td_tag_parent.find_next_siblings('td',attrs={'class':'valueCell'})
    if eps_data:
        for tag in eps_data:
                eps_val=tag.string
                safe,denom_val = check_data(eps_val)
                if safe is not 'NaJO':
                    eps_master.append(safe)
                if denom_val is not 'NaJO':
                    eps_denom_master.append(denom_val)
                           
        epsdf = pd.DataFrame( { 'years' : years_rev_ninc_eps, 'years_strings': [ int(x) for x in years_rev_ninc_eps ], 'data' : eps_master } )
        eps_growth_master = ((epsdf['data'].max()/epsdf['data']) ** (1/(epsdf['years_strings'].max()-epsdf['years_strings']))-1)
        eps_growth_master = eps_growth_master.apply(prettify_num)
     
        """Summary"""
        zipped_eps=zip(years_rev_ninc_eps,eps_master,eps_growth_master)
        for year,es,gr in zipped_eps:
            print (stock,"had",es,"EPS in",year," Rate = ",gr)
else:
    eps_master=[]
    print("No EPS data found at all")
print("")    



"""                                      Free Cash Flow                 """
fcf_data=''
fcf_denom=''
years_fcf=[]
fcf_master=[]
fcf_link_parent=''
fcf_growth_master=[]
fcf_denom_master=[]

pattern = re.compile("\s+Free Cash Flow")
fcf_text = soup_fcf.find(text=pattern)
if fcf_text:
    fcf_link_parent = fcf_text.find_parent()
    if fcf_link_parent:     
        fcf_data = fcf_link_parent.find_next_siblings(attrs={'class':'valueCell'})
    for tag in fcf_data:
            fcf_val=tag.string
            safe,denom_val = check_data(fcf_val)
            if safe is not 'NaJO':
                fcf_master.append(safe)
            if denom_val is not 'NaJO':
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
    
    """Years"""  
    fcf_years_text_h2 = soup_fcf.find('h2',text="Financing Activities")
    fcf_years_data_th=fcf_years_text_h2.find_next('th',attrs={'class':'rowTitle'})
    fcf_years_data = fcf_years_data_th.find_next_siblings()
    fcf_years_pattern = re.compile("201[0-9]")
    for fcf_year in fcf_years_data:
        if fcf_year.string is not None and fcf_years_pattern.match(fcf_year.string):
                years_fcf.append(fcf_year.string)
            
    fcfdf = pd.DataFrame( { 'years' : years_fcf, 'years_strings': [ int(x) for x in years_fcf ], 'data' : fcf_master } )
    fcf_growth_master = ((fcfdf['data'].max()/fcfdf['data']) ** (1/(fcfdf['years_strings'].max()-fcfdf['years_strings']))-1)
    fcf_growth_master = fcf_growth_master.apply(prettify_num)
             
    """Summary"""       
    zipped_fcf=zip(years_fcf,fcf_master,fcf_growth_master)
    for year,fcf,gr in zipped_fcf:
        print (stock,"had",fcf,"Free Cash Flow in",year," Rate = "+gr)
    print("")
else:
    fcf_inc_denom="NA"
    print("No FCF data found at all")

print("")
  
"""                                        BVPS                """
#No great source of BVPS except for GF
years_bvps=[]
bvps_master=[]
main_bvps_td_tag=''
bvps_denom_master=[]
bvps_data_in_links=''
bvps_growth_master=[]
main_bvps_td_tag=soup_bvps.find('td',text="Book Value per Share")
if main_bvps_td_tag:
    bvps_data_in_links = main_bvps_td_tag.find_next_siblings()
if bvps_data_in_links:
    for tag in bvps_data_in_links:
        if (tag.string) is not None:
            bvps_val=tag.string
            safe,denom_val = check_data(bvps_val)
            bvps_master.append(safe)
            bvps_denom_master.append(denom_val)
    
    """Years"""
    #There really is no great way to reliably get this. From GUfocus.
    bvps_years_pat=re.compile('[0-9]{2}')
    main_bvps_years = soup_bvps.find('div',attrs={'id':'target_def_historical_data'})
    bvps_years_data = main_bvps_years.find_next('td').find_next_siblings()
    for year in bvps_years_data[-5:]:
        #year will break w/html \'s, use year.string
        #just get the last 5 values
        matched_bvps_year = bvps_years_pat.search(year.string)
        if matched_bvps_year:
            bvps_year = "20"+matched_bvps_year.group()
            years_bvps.append(bvps_year)  
    
    bvdf = pd.DataFrame( { 'years' : years_bvps , 'years_strings': [ int(x) for x in years_bvps ], 'data' : bvps_master } )
    bvps_growth_master = ((bvdf['data'].max()/bvdf['data']) ** (1/(bvdf['years_strings'].max()-bvdf['years_strings']))-1)
    bvps_growth_master = bvps_growth_master.apply(prettify_num)
else:
    print("No BVPS data found at all")

"""Summary"""                              
zipped_bvps=zip(years_bvps,bvps_master,bvps_growth_master)
for year,bv,gr in zipped_bvps:
    print (stock,"had",bv,"BVPS in",year," Rate = ",gr)
print("")



"""               ROIC                     """
roic=''
roic_data=''
pattern= re.compile("Return on Invested Capital")
roic_p_tag=soup_roic.find('p',attrs={'class':'column'},text=pattern)
if roic_p_tag:
    roic_data=roic_p_tag.find_next_sibling('p',attrs={'class':'data lastcolumn'})
if roic_data:
    #We are not actually plotting RIC as it's just one value. Leave as NavString
    roic=roic_data.string
    print (stock,"had",roic,"ROIC")
    print("")
else:
    print("No ROIC data found at all")
print("")   

""" Data Checks """
def check_years():
    if years_bvps ==  years_rev_ninc_eps == years_fcf == years_rev_ninc_eps:
        print ("OK: years_bvps,years_rev_ninc_eps,years_fcf, years_rev_ninc_eps are equal")
        return True
    else:
        print("Check years - smthing may be off" )
    
def check_data_blocks():
    if len(eps_master) == 5 and len(revenue_master) == 5 and len(fcf_master) == 5 and len(bvps_master) == 5 and len(net_inc_master) == 5:
        print ("OK: EPS, Revenue, FCF, BVPS, and Net Income all have 5 years of data")
        return True
    else:
        print("Check data - some data missing" )
        
if check_years() and check_data_blocks():
        print ("GREAT: Data for "+stock+" is filled for all years and big 5 numbers")

if (not roic_data) and (not a_href_sales) and (not main_net_income_link) and (not bvps_data_in_links)\
and (not main_eps_a_tag) and (not fcf_text):
    plot = False
    print ("No data - plot will not be generated")

print("")

"""         Links                                     """
links={ url_sales_ninc_eps:"Sales,NetInc,EPS", url_roic : "Roic", url_fcf : "Fcf", url_bvps:"Bvps" }
for link,text in links.items():
    print(link+" =",text)
print("")

""" Plot """
if plot == "True":
    stock=stock.upper()
    #Bokeh is ***awesome****
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
    plot_bvps.line(years_rev_ninc_eps,bvps_master,legend="Book Value per Share", line_width=2)
    
    
    plot_fcf = figure(plot_width=400, plot_height=400,title=stock+" Free Cash Flow", x_axis_label='Years',\
    y_axis_label='Free Cash Flow')
    plot_fcf.line(years_fcf,fcf_master,legend=fcf_denom, line_width=2)
    
    plot_roic = figure(plot_width=400, plot_height=400,title=stock+" Roic")
    plot_roic.line([1,2,3,4,5],[1,2,3,4,5],legend=roic)
    
    # put all the plots in a grid layout
    p = gridplot( [[plot_rev,plot_net_inc,plot_eps],[plot_bvps,plot_fcf,plot_roic]] )
    show(p)