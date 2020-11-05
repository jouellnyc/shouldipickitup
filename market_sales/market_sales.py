#!/usr/bin/python3

import re
import os
import sys
import argparse
import requests
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup as bsoup
from bokeh.io import output_file, show, save
from bokeh.layouts import gridplot
from bokeh.plotting import figure


parser = argparse.ArgumentParser()
parser.description = "Get Stock Data and Return Growth Rates"
parser.epilog = "Example: " + sys.argv[0] + " -s AAPL -m local"
parser.add_argument("-s", "--stock")
parser.add_argument("-m", "--mode", help="(web or local)", choices=["local", "web"])
parser.add_argument("-k", "--keep", help="Keep data locally", action="store_true")
parser.add_argument("-d", "--debug", help="debug", action="store_true")
parser.add_argument("-p", "--plot", help="Save Plot Data", action="store_true")
namespace = parser.parse_args(sys.argv[1:])

if namespace.stock:
    stock = namespace.stock
else:
    stock = "GOOG"
ustock = stock.upper()

if namespace.keep:
    save_data_locally = True
else:
    save_data_locally = False

if namespace.debug:
    debugon = True
else:
    debugon = False

if namespace.plot:
    plot = True
else:
    plot = False

if namespace.mode:
    if namespace.mode == "local":
        web_mode = False
    elif namespace.mode == "web":
        web_mode = True
else:
    web_mode = True


""" Globals  """
lo_pe = 4
hi_pe = 25
mynan = np.nan
plot_dir = "data"
prefillna = "-9999"
popup_browser_plot = True


""" URLS """
url_sales_ninc_eps = (
    "http://www.marketwatch.com/investing/stock/" + stock + "/financials/"
)
url_roic = "http://www.marketwatch.com/investing/stock/" + stock + "/company-profile"
url_fcf = (
    "http://www.marketwatch.com/investing/stock/" + stock + "/financials/cash-flow/"
)
url_bvps = (
    "https://www.gurufocus.com/term/Book+Value+Per+Share/"
    + stock
    + "/Book-Value-per-Share"
)
url_ni_ttm = "https://ycharts.com/companies/" + ustock + "/net_income_ttm"
url_pe_ttm = "https://www.gurufocus.com/stock/" + ustock
url_rev_ttm = "https://ycharts.com/companies/" + ustock + "/revenues_ttm"


""" Functions """


def err_web(url):
    """ Catch the Errors from the Web Connections             """
    """ All or nothing here: If not 200 OK - exit the program """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1)"
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 "
            "Safari/537.36"
        }
        r = requests.get(url, timeout=10, allow_redirects=True, headers=headers)
        # raise_for_status() never execs if request.get above has connect error/timeouts
        r.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        print("HTTP Error:", errh)
        sys.exit(1)
    except requests.exceptions.ConnectionError as errc:
        print("Fatal Error Connecting:", errc)
        sys.exit(1)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
        sys.exit(1)
    except requests.exceptions.RequestException as err:
        print("OOps: Something Else", err)
        sys.exit(1)
    else:
        return r


def get_web_data():
    """ Get Web Data """
    print("Retrieving HTML for ", stock)
    r_sales_ninc_eps = err_web(url_sales_ninc_eps)
    r_roic = err_web(url_roic)
    r_url_fcf = err_web(url_fcf)
    r_bvps = err_web(url_bvps)
    r_ni_ttm = err_web(url_ni_ttm)
    r_pe_ttm = err_web(url_pe_ttm)
    r_rev_ttm = err_web(url_rev_ttm)

    content_dict = {
        "sales": r_sales_ninc_eps,
        "fcf": r_url_fcf,
        "bvps": r_bvps,
        "roic": r_roic,
        "ninc": r_ni_ttm,
        "pe": r_pe_ttm,
        "revttm": r_rev_ttm,
    }
    return (
        r_sales_ninc_eps,
        r_roic,
        r_url_fcf,
        r_bvps,
        r_ni_ttm,
        r_pe_ttm,
        r_rev_ttm,
        content_dict,
    )


def write_content(content_dict):
    for name, request in content_dict.items():
        file = plot_dir + "/" + ustock + "-" + name + "-" + "data.html"
        try:
            with open(file, "w") as fh:
                fh.write(request.text)
        except FileNotFoundError:
            print("File not found:", file)


def read_content():
    content_list = ["sales", "fcf", "bvps", "roic", "ninc", "pe", "revttm"]
    soup_list = []
    for name in content_list:
        file = plot_dir + "/" + ustock + "-" + name + "-" + "data.html"
        try:
            with open(file) as fh:
                soup = bsoup(fh, "lxml")
                soup_list.append(soup)
        except FileNotFoundError:
            print("File not found:", file)
            print("Run with -m web -k first!\nExiting")
            sys.exit(1)
    return soup_list


def make_soup(
    r_sales_ninc_eps, r_url_fcf, r_bvps, r_roic, r_ni_ttm, r_pe_ttm, r_rev_ttm
):
    """ Soup Setup """
    print("Parsing HTML")
    # Note: if you make it here, soup objects will be assigned ok
    soup_sales_ninc_eps = bsoup(r_sales_ninc_eps.content, "lxml")
    soup_fcf = bsoup(r_url_fcf.content, "lxml")
    soup_bvps = bsoup(r_bvps.content, "lxml")
    soup_roic = bsoup(r_roic.content, "lxml")
    soup_ni_ttm = bsoup(r_ni_ttm.content, "lxml")
    soup_pe_ttm = bsoup(r_pe_ttm.content, "lxml")
    soup_rev_ttm = bsoup(r_rev_ttm.content, "lxml")
    print("Pulling Data out of HTML")
    print("")
    return (
        soup_sales_ninc_eps,
        soup_fcf,
        soup_bvps,
        soup_roic,
        soup_ni_ttm,
        soup_pe_ttm,
        soup_rev_ttm,
    )


def calc_growth(last, first, period):
    """ Simple cagr calculation """
    return (last / first) ** (1 / period) - 1


def calc_cagr(years, data):
    """ Calcuate CAGR and make data frame """
    df = pd.DataFrame(
        {"years_strings": years, "years": [int(x) for x in years], "data": data}
    )
    # Use variables to help from going cross eyed
    last_data_value = df["data"][len(df["data"]) - 1]
    last_year_value = df["years"].max()
    growth = (last_data_value / df["data"]) ** (1 / (last_year_value - df["years"])) - 1
    return growth.apply(prettify_num)


def check_data(data):
    """ Return a Number and a Denomination Value (typically M or B) """

    """ Ensure each list is filled by returning NaN if no match     """

    if data is None:
        return None, None
    else:
        data_pat = re.compile("([-(]?[-(]?[0-9,]+\.?[0-9]{,3})([mMbB]?)")
        data_is_valid = data_pat.search(data)
        if data_is_valid:
            num = data_is_valid.group(1)
            denom = data_is_valid.group(2)
            brc_pat = re.compile("\(")
            braces = brc_pat.search(num)
            num = num.replace("(", "")
            num = num.replace(")", "")
            num = num.replace(",", "")

            if denom:
                denom_val = denom
            else:
                denom_val = mynan

            if braces:
                neg_pat = re.compile("-")
                is_neg_already = neg_pat.search(num)
                if is_neg_already:
                    return float(num), denom_val
                else:
                    return -float(num), denom_val
            else:
                return float(num), denom_val
        else:
            return mynan, mynan


def check_growth_rate(data_name, data_master, denom_master, years):
    """ Given the data name,list,denomination and years, return a data """
    """ frame with growth rates                                        """

    data = True
    df = pd.DataFrame({data_name: data_master, "Denoms": denom_master, "Years": years})
    # Note: NA and NaN get promoted to float64 which don't print well
    # Year is the key, if it DNE drop the whole row.
    df.drop(df.index[df.Years == -9999], inplace=True)
    # EPS and BVPS are per share and not needing a denomination
    if data_name not in ["EPS", "BVPS"]:
        df.loc[df["Denoms"].isnull(), "Millions"] = df[data_name] / 1000000
    else:
        df.loc[df["Denoms"].isnull(), "Millions"] = df[data_name]
    df["Denoms"].fillna("d", inplace=True)
    df["Denoms"] = df["Denoms"].str.upper()
    df.loc[df["Denoms"] == "B", "Millions"] = df[data_name] * 1000
    df.loc[df["Denoms"] == "M", "Millions"] = df[data_name]
    last_data_value = df.Millions.iloc[-1]
    last_year_value = df.Years.iloc[-1]
    df["Years_delta"] = last_year_value - df["Years"]
    df["Growth"] = (last_data_value / df["Millions"]) ** (
        1 / (last_year_value - df["Years"])
    ) - 1
    df["Growth"] = df["Growth"].apply(prettify_num)
    df.loc[df["Growth"] == "inf%", "Growth"] = "NA"
    df.loc[df["Growth"] == "nan%", "Growth"] = "NA"
    return data, df, df["Growth"].head(1).values[0]


def debug(data, data_master, *args):
    """ Print out extra info on the passed list for the Big 5 numbers """
    if debugon:
        print("===========", stock.upper(), data.title(), "==========")
        print("=debug():")
        print(data.lower() + "master:")
        print("\tData:", data_master)
        print("\tTypes:", [type(x) for x in data_master])
        if args:
            for each in args:
                print("Arg to be sent:")
                print("\tData:", each)
                print("\tTypes:", [type(x) for x in each])


def summarize(data_name, df):
    """ Print out the Big 5 Numbers Cleanly """
    zipped = zip(df["Millions"], df["Years"], df["Years_delta"], df["Growth"])
    for data, year, delta, grwth in zipped:
        if data_name in ("EPS", "BVPS"):
            print(
                stock,
                "had",
                "{:,}".format(data),
                data_name,
                "in",
                year,
                delta,
                "GR Rate = ",
                grwth,
            )
        else:
            print(
                stock,
                "had",
                "{:,}".format(data),
                "M",
                data_name,
                "in",
                year,
                delta,
                "GR Rate = ",
                grwth,
            )
    print("")


def prettify_num(num):
    """ Pretty print Growth Rate """
    return "%.2f" % (num * 100) + "%"


def get_links():
    """ Links """
    links = {
        url_sales_ninc_eps: "Sales,NetInc,EPS",
        url_roic: "Roic",
        url_fcf: "Fcf",
        url_bvps: "Bvps",
        url_ni_ttm: "Net Inc TMM",
        url_pe_ttm: "PE TTM",
        url_rev_ttm: "Revenue TTM",
    }
    for link, text in links.items():
        print(link + " =", text)
    print("")


def get_years_rev_ninc_eps(soup_sales_ninc_eps):
    """ Years (Revenue,Net Inc and EPS) - including USD and EUR """
    years_rev_ninc_eps = []
    rev_text_pattern = re.compile("Fiscal year is \w+-\w+. All values \w+ millions")
    years_main_th_tag = soup_sales_ninc_eps.find("th", text=rev_text_pattern)
    try:
        years_links = years_main_th_tag.find_next_siblings()
    except AttributeError as e:
        print("No Rev-EPS-NINC web data patterns found - exiting")
        get_links()
        sys.exit(0)
    else:
        max = 5
        for tag in years_links:
            year_raw_data = tag.string
            if year_raw_data is not None:
                match = re.search("20[0-9][0-9]", year_raw_data)
                if match:
                    year_data = match.group()
                    years_rev_ninc_eps.append(int(year_data))
            else:
                years_rev_ninc_eps.append(int(prefillna))
        if len(years_rev_ninc_eps) == max:
            return years_rev_ninc_eps


def get_rev(soup_sales_ninc_eps, years_rev_ninc_eps):
    """ Revenue """
    rev_rn1 = "0"
    revenue = True
    revenue_master = []
    revenue_denom_master = []

    a_href_sales = soup_sales_ninc_eps.find(
        "a", attrs={"data-ref": "ratio_SalesNet1YrGrowth"}
    )
    """ If we got here the http call succeeded so we will have a valid
    soup object. But if no content found in a soup obj it returns a
    NoneType. Worst case a_href_sales becomes NoneType, but we don't
    kick up an AttributeError here.
    """
    try:
        """ If the soup object is null we will kick up the AttributeError
        here so we try and group together.
        """
        sales_td_parent = a_href_sales.find_parent()
        sales_data_links = sales_td_parent.find_next_siblings(
            "td", attrs={"class": "valueCell"}
        )
    except AttributeError as e:
        print("No Revenue data found")
        print("")
        revenue = False
        return revenue, revenue_master, rev_rn1
    else:
        if sales_data_links is not None:
            for link in sales_data_links:
                rev_val = link.string
                rev, denom_val = check_data(rev_val)
                revenue_master.append(rev)
                revenue_denom_master.append(denom_val)

        debug("revenue", revenue_master, years_rev_ninc_eps, revenue_denom_master)
        revenue, revdf, rev_rn1 = check_growth_rate(
            "revenue", revenue_master, revenue_denom_master, years_rev_ninc_eps
        )
        summarize("Revenue", revdf)
        return revenue, revdf["Millions"], rev_rn1


def get_ninc(soup_sales_ninc_eps, years_rev_ninc_eps):
    """ Net Income """
    net_inc_rn1 = "0"
    net_inc = True
    net_inc_master = []
    net_inc_denom_master = []

    net_inc_link = soup_sales_ninc_eps.find(
        "td", attrs={"class": "rowTitle"}, text="Net Income Available to Common"
    )
    try:
        net_inc_values = net_inc_link.fetchNextSiblings("td", class_="valueCell")
    except AttributeError as e:
        print("No Net Income data found")
        print("")
        net_inc = False
        return net_inc, net_inc_master, net_inc_rn1
    else:
        for link in net_inc_values:
            net_income_val = link.string
            safe, denom_val = check_data(net_income_val)
            net_inc_master.append(safe)
            net_inc_denom_master.append(denom_val)

        debug("Net Income", net_inc_master, years_rev_ninc_eps, net_inc_denom_master)
        net_inc, net_inc_df, net_inc_rn1 = check_growth_rate(
            "Net Income", net_inc_master, net_inc_denom_master, years_rev_ninc_eps
        )
        summarize("Net Income", net_inc_df)
        return net_inc, net_inc_df["Millions"], net_inc_rn1


def get_eps(soup_sales_ninc_eps, years_rev_ninc_eps):
    """ EPS """
    eps_rn1 = "0"
    eps_master = []
    eps_denom_master = []

    main_eps_a_tag = soup_sales_ninc_eps.find(
        "a", attrs={"data-ref": "ratio_Eps1YrAnnualGrowth"}
    )
    try:
        main_eps_td_tag_parent = main_eps_a_tag.find_parent()
        eps_data = main_eps_td_tag_parent.find_next_siblings(
            "td", attrs={"class": "valueCell"}
        )
    except AttributeError as e:
        print("No EPS data found")
        print("")
        eps = False
        return eps, eps_master, eps_rn1
    else:
        if eps_data is None:
            print("No EPS data found at all")
            print("")
            eps = False
            return eps, eps_master, eps_rn1
        else:
            for tag in eps_data:
                eps_val = tag.string
                safe, denom_val = check_data(eps_val)
                eps_master.append(safe)
                # Expected to be 'None's
                eps_denom_master.append(denom_val)

            debug("EPS", eps_master, eps_denom_master, years_rev_ninc_eps)
            eps, eps_df, esp_rn1 = check_growth_rate(
                "EPS", eps_master, eps_denom_master, years_rev_ninc_eps
            )
            summarize("EPS", eps_df)
            return eps, eps_df["Millions"], esp_rn1


def get_fcf(soup_fcf):
    """ Free Cash Flow """
    fcf = True
    fcf_rn1 = "0"
    years_fcf = []
    fcf_master = []
    fcf_denom_master = []

    pattern = re.compile("\s+Free Cash Flow")
    fcf_text = soup_fcf.find(text=pattern)
    try:
        fcf_link_parent = fcf_text.find_parent()
        fcf_data = fcf_link_parent.find_next_siblings(attrs={"class": "valueCell"})
    except AttributeError as e:
        print("No FCF data found")
        print("")
        fcf = False
        return fcf, fcf_master, years_fcf, fcf_rn1
    else:
        for tag in fcf_data:
            fcf_val = tag.string
            safe, denom_val = check_data(fcf_val)
            fcf_master.append(safe)
            fcf_denom_master.append(denom_val)

        """Fcf Years"""
        fcf_years_text_h2 = soup_fcf.find("h2", text="Financing Activities")
        try:
            fcf_years_data_th = fcf_years_text_h2.find_next(
                "th", attrs={"class": "rowTitle"}
            )
            fcf_years_data = fcf_years_data_th.find_next_siblings()

        except AttributeError as e:
            print("No FCF years found")
            print("")
            fcf = False
            return fcf, fcf_master, years_fcf, fcf_rn1
        else:
            max = 5
            for tag in fcf_years_data:
                """ HTML here is 6 of the same th/td elements """
                """ 5 housing the target years                """
                fcf_raw_years = tag.string
                if fcf_raw_years is None:
                    years_fcf.append(int(prefillna))
                else:
                    match = re.search("20[0-9][0-9]", fcf_raw_years)
                    if match:
                        fcf_year_data = match.group()
                        years_fcf.append(int(fcf_year_data))
        if len(years_fcf) == max:
            pass

        debug("FCF", fcf_master, years_fcf, fcf_denom_master)

        fcf, fcf_df, fcf_rn1 = check_growth_rate(
            "FCF", fcf_master, fcf_denom_master, years_fcf
        )
        summarize("FCF", fcf_df)
        return fcf, fcf_df["Millions"], years_fcf, fcf_rn1


def get_bvps(soup_bvps):
    """ BVPS """
    bvps = True
    bvps_rn1 = "0"
    years_bvps = []
    bvps_master = []
    bvps_denom_master = []

    main_bvps_td_tag = soup_bvps.find("td", text="Book Value per Share")
    main_bvps_years = soup_bvps.find("div", attrs={"id": "target_def_historical_data"})
    try:
        bvps_data_in_links = main_bvps_td_tag.find_next_siblings()
        bvps_years_data = main_bvps_years.find_next("td").find_next_siblings()
    except AttributeError as e:
        print("No BVPS data found")
        print("")
        bvps = False
        return bvps, bvps_master, years_bvps, bvps_rn1
    else:
        bvps_data_pat = re.compile("-?[0-9]{1,9}.[0-9]{1,2}")
        for tag in bvps_data_in_links:
            bvps_val = tag.string
            if bvps_val is not None:
                matched_bvps_data = bvps_data_pat.search(bvps_val)
                bvps_data = matched_bvps_data.group()
                safe, denom_val = check_data(bvps_data)
                bvps_master.append(safe)
                # Expected to be 'None's
                bvps_denom_master.append(denom_val)

    """Bvps Years"""
    bvps_years_pat = re.compile("[0-9]{2}")
    if bvps_years_data is not None and len(bvps_years_data) > 0:
        for year in bvps_years_data[-5:]:
            # year will break w/html \'s, use year.string
            # just get the last 5 values
            matched_bvps_year = bvps_years_pat.search(year.string)
            if matched_bvps_year:
                bvps_year = "20" + matched_bvps_year.group()
                years_bvps.append(int(bvps_year))
    else:
        bvps = False
        print("No BVPS years data found")
        print("")
        return bvps, bvps_master, years_bvps, bvps_rn1

    debug("BVPS", bvps_master, years_bvps)
    bvps, bvps_df, bvps_rn1 = check_growth_rate(
        "BVPS", bvps_master, bvps_denom_master, years_bvps
    )
    summarize("BVPS", bvps_df)
    return bvps, bvps_df["BVPS"], years_bvps, bvps_rn1


def get_roic(soup_roic):
    """ ROIC """
    pattern = re.compile("Return on Invested Capital")
    roic_p_tag = soup_roic.find("td", text=pattern)
    try:
        roic_data = roic_p_tag.find_next_sibling(
            "td"
        )
        # ROIC is just one value. Leave as NavString
    except AttributeError as e:
        print("No Roic data found")
        roic = False
        return roic
    else:
        roic = roic_data.string
        print(stock, "had", roic, "ROIC")
        return roic


def get_ni_ttm(soup_ni_ttm):
    """ Net Income TTM """
    net_inc_ttm = soup_ni_ttm.find("span", attrs={"id": "pgNameVal"})
    try:
        net_inc_ttm_data = net_inc_ttm.string
    except AttributeError as e:
        print("No NetInc TTM found")
    else:
        ni_ttm, ni_ttm_denom = check_data(net_inc_ttm_data)
        print(stock, "had", ni_ttm, ni_ttm_denom, "NetInc TTM")
        return ni_ttm


def get_pe_ttm(soup_pe_ttm):
    """ Get Trailing TTM for PE """
    web_patt = re.compile("P/E\s+\(TTM\).*?:.*?[0-9]{1,9}?\.[0-9]{0,2}", re.DOTALL)
    pe_data_tag = soup_pe_ttm.find("th", text=web_patt)
    if pe_data_tag:
        pe_data = pe_data_tag.string
        local_patt = re.compile("(-?[0-9]{1,9}?\.[0-9]{0,2})")
        pe_ttm_match = local_patt.search(pe_data)
        if pe_ttm_match:
            pe_ttm = pe_ttm_match.group(1)
            print(stock, "has", pe_ttm, "PE")
            return pe_ttm
    else:
        print("No PE TTM data found for " + stock)
        return "NA"

def get_mcap(soup_pe_ttm):
    """ Get Total Market Cap
    Create a list of child div tags of the 'hook text'.
    Note the 'next' item (+2 index b/c of tags vs strings) is market cap.

    <div class="stock-summary-table fc-regular" data-v-fa982d3a>
    SNIP...
        <div data-v-fa982d3a> Avg Vol (1m): </div>
        <div data-v-fa982d3a> 1,980,804 </div>
        <div data-v-fa982d3a> Market Cap $: </div>
        <div data-v-fa982d3a> 969.35 Bil </div>
    SNIP...
    """
    wanted_text  = 'Market Cap'
    hook_text = 'stock-summary-table fc-regular'
    market_cap = list(soup_pe_ttm.find('div',attrs={"class" : hook_text }).children)
    for index, div_tag in enumerate(market_cap):
        if wanted_text in str(market_cap[index]):
            market_cap_text = market_cap[index+2].text.lstrip()
            print(f"{stock} Market Cap: {market_cap_text}")

def get_rev_ttm(soup_rev_ttm):
    "Get Trailing TTM for Revenue"
    rev_ttm_tag = soup_rev_ttm.find("span", attrs={"id": "pgNameVal"})
    try:
        rev_ttm_data = rev_ttm_tag.string
    except AttributeError as e:
        print(e, "error")
    else:
        rev_ttm, rev_ttm_denom = check_data(rev_ttm_data)
        # return rev_ttm
        print(
            stock + " had " + str(rev_ttm) + " " + str(rev_ttm_denom) + " Revenue TTM"
        )

""" Data Checks """


def check_years(years_bvps, years_rev_ninc_eps, years_fcf):
    """ Quick data quality check #1 """
    if not any([years_rev_ninc_eps, years_bvps, years_fcf]):
        print("Not enough year data to proceed - check the data")
        sys.exit(0)

    if len(years_bvps) == len(years_rev_ninc_eps) == len(years_fcf):
        print(
            "OK: years_bvps, years_rev_ninc_eps,years_fcf,"
            "years_rev_ninc_eps are equal"
        )
        return True
    else:
        print("Check years - something may be off")


def check_data_blocks(
    eps_master, revenue_master, fcf_master, bvps_master, net_inc_master
):
    """ Quick data quality check #2 """
    if (
        len(eps_master) == 5
        and len(revenue_master) == 5
        and len(fcf_master) == 5
        and len(bvps_master) == 5
        and len(net_inc_master) == 5
    ):
        print("OK: EPS, Revenue, FCF, BVPS, and Net Income have 5 years data")
        return True
    else:
        print("Check overall data - some data is missing")


def data_is_filled(
    years_bvps,
    years_rev_ninc_eps,
    years_fcf,
    eps_master,
    revenue_master,
    fcf_master,
    bvps_master,
    net_inc_master,
):
    """ Quick data quality check #3 """
    if check_years(years_bvps, years_rev_ninc_eps, years_fcf) and check_data_blocks(
        eps_master, revenue_master, fcf_master, bvps_master, net_inc_master
    ):
        print("GREAT: Data for " + stock + " is filled for all years and big 5 numbers")


def check_rn1(rev_rn1, net_inc_rn1, eps_rn1, fcf_rn1, bvp_rn1, roic, pe_ttm):
    """ Are all the Big 4, 4 years of compounded growth rate at least 10%? """
    """ Is the PE within our current acceptable range?                     """
    mylist = [rev_rn1, net_inc_rn1, eps_rn1, fcf_rn1, bvp_rn1, pe_ttm]
    if any(x == "NA" for x in mylist):
        return
    mylist = [float(x.rstrip("%")) for x in mylist]
    if all(x >= 10 for x in mylist):
        print("Awesome: (5)", stock, " - Big 4 have 4 year CAGR of 10% and ROIC %10")
        if lo_pe <= float(pe_ttm) <= hi_pe:
            print("Bonus: (RN1) : PE is between", lo_pe, "and", hi_pe)


""" Plotting  """


def plot_or_not(
    stock,
    roic,
    revenue,
    years_rev_ninc_eps,
    revenue_master,
    net_inc,
    net_inc_master,
    eps,
    eps_master,
    bvps,
    years_bvps,
    bvps_master,
    fcf,
    years_fcf,
    fcf_master,
):
    """ Bokeh Plotting """
    if plot:
        if not os.path.exists(plot_dir):
            os.makedirs(plot_dir)
        if (
            (not roic)
            and (not revenue)
            and (not net_inc)
            and (not bvps)
            and (not eps)
            and (not fcf)
        ):
            print("No data - plot will not be generated")
            print("")
            sys.exit(0)
        else:
            stock = stock.upper()
            print("Plotting details for", stock)
            print("")
            output_file("data/" + stock + ".html", title=stock + " Financials")

            plot_net_inc = figure(
                plot_width=400,
                plot_height=400,
                title=stock + " Net Income",
                x_axis_label="Years",
                y_axis_label="Net Income",
            )
            plot_net_inc.line(
                years_rev_ninc_eps, net_inc_master, legend="Millions", line_width=2
            )

            plot_rev = figure(
                plot_width=400,
                plot_height=400,
                title=stock + " Revenue",
                x_axis_label="Years",
                y_axis_label="Revenue",
            )
            plot_rev.line(
                years_rev_ninc_eps, revenue_master, legend="Millions", line_width=2
            )

            plot_eps = figure(
                plot_width=400,
                plot_height=400,
                title=stock + " EPS",
                x_axis_label="Years",
                y_axis_label="EPS",
            )
            plot_eps.line(
                years_rev_ninc_eps, eps_master, legend="Dollars per Share", line_width=2
            )

            plot_bvps = figure(
                plot_width=400,
                plot_height=400,
                title=stock + " BVPS",
                x_axis_label="Years",
                y_axis_label="BVPS",
            )
            plot_bvps.line(
                years_bvps, bvps_master, legend="Book Value per Share", line_width=2
            )

            plot_fcf = figure(
                plot_width=400,
                plot_height=400,
                title=stock + " Free Cash Flow",
                x_axis_label="Years",
                y_axis_label="Free Cash Flow",
            )
            plot_fcf.line(years_fcf, fcf_master, legend="Millions", line_width=2)

            plot_roic = figure(plot_width=400, plot_height=400, title=stock + " Roic")
            plot_roic.line([1, 2, 3, 4, 5], [1, 2, 3, 4, 5], legend=roic)

            p = gridplot(
                [[plot_rev, plot_net_inc, plot_eps], [plot_bvps, plot_fcf, plot_roic]]
            )
            save(p)
            if popup_browser_plot:
                show(p)


def main():
    """" Start Here """
    if web_mode:
        (
            r_sales_ninc_eps,
            r_roic,
            r_url_fcf,
            r_bvps,
            r_ni_ttm,
            r_pe_ttm,
            r_rev_ttm,
            content_dict,
        ) = get_web_data()

        if save_data_locally:
            write_content(content_dict)
        (
            soup_sales_ninc_eps,
            soup_fcf,
            soup_bvps,
            soup_roic,
            soup_ni_ttm,
            soup_pe_ttm,
            soup_rev_ttm,
        ) = make_soup(
            r_sales_ninc_eps, r_url_fcf, r_bvps, r_roic, r_ni_ttm, r_pe_ttm, r_rev_ttm
        )

    else:
        # local mode- get data from disk
        (
            soup_sales_ninc_eps,
            soup_fcf,
            soup_bvps,
            soup_roic,
            soup_ni_ttm,
            soup_pe_ttm,
            soup_rev_ttm,
        ) = read_content()
    # Do the following *regaahhdless* -in a thick Boston accent.
    years_rev_ninc_eps = get_years_rev_ninc_eps(soup_sales_ninc_eps)
    revenue, revenue_master, rev_rn1 = get_rev(soup_sales_ninc_eps, years_rev_ninc_eps)
    net_inc, net_inc_master, net_inc_rn1 = get_ninc(
        soup_sales_ninc_eps, years_rev_ninc_eps
    )
    eps, eps_master, eps_rn1 = get_eps(soup_sales_ninc_eps, years_rev_ninc_eps)
    fcf, fcf_master, years_fcf, fcf_rn1 = get_fcf(soup_fcf)
    bvps, bvps_master, years_bvps, bvp_rn1 = get_bvps(soup_bvps)
    roic = get_roic(soup_roic)
    get_ni_ttm(soup_ni_ttm)
    pe_ttm = get_pe_ttm(soup_pe_ttm)
    #No need to store Revenue TTM as it's never used in a calculation
    get_rev_ttm(soup_rev_ttm)
    mcap   = get_mcap(soup_pe_ttm)
    print("")
    get_links()
    check_rn1(rev_rn1, net_inc_rn1, eps_rn1, fcf_rn1, bvp_rn1, roic, pe_ttm)
    plot_or_not(
        stock,
        roic,
        revenue,
        years_rev_ninc_eps,
        revenue_master,
        net_inc,
        net_inc_master,
        eps,
        eps_master,
        bvps,
        years_bvps,
        bvps_master,
        fcf,
        years_fcf,
        fcf_master,
    )
    if debug:
        data_is_filled(
            years_bvps,
            years_rev_ninc_eps,
            years_fcf,
            eps_master,
            revenue_master,
            fcf_master,
            bvps_master,
            net_inc_master,
        )


if __name__ == "__main__":
    main()
