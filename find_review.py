from time import sleep
import numpy as np
import pandas as pd
import web_reader
from fake_useragent import UserAgent
from scrapy import Selector
from math import ceil, floor
import re
from datetime import datetime
import random
from string import ascii_letters, digits


def get_review_page_link_with_number(ASIN, pageNumber):
    '''
    generates the link to the Amazon product's U.S. review page for a specific page number
    
    Args:
        ASIN (str): the Amazon code for the product
        pageNumber (int): the page number
    
    Returns: 
        string: the link to a Amazon product's U.S. review page
    '''
    
    def rand_code(length=8):
        '''
        generates a string composed by randomly chosen ascii characters with specified length

        Args:
            length (int): the specified length of the string; default value is 8

        Returns:
            string: randomly chosen ascii characters with specified length
        '''
        
        generate_code = ''.join([random.choice(
            ascii_letters + digits) for n in range(length)])
        return generate_code


    part1 = "https://www.amazon.com/"
    random_string2 =rand_code(8)+"/"
    part3 ="product-reviews/"
    ASIN4=str(ASIN)
    part_ref5=""
    if (pageNumber == 1):
        part_ref5 = "/ref=cm_cr_arp_d_viewopt_rvwer?"
    else: 
        part_ref5 = "/ref=cm_cr_getr_d_paging_btm_next_"+str(pageNumber)+"?"
    conditions6="ie=UTF8&reviewerType=avp_only_reviews&sortBy=recent&pageNumber="+str(pageNumber)
    format_type = "&formatType=current_format"
    url = part1 + random_string2 + part3 + ASIN4 + part_ref5 + conditions6 + format_type
    print("     review page url:", url)
    return url


def find_all_reviews(ASIN, earliest_yr):
    '''
    finds all reviews' date and rating from the beginning to the specified earliest year of the review
    (e.g. if the earliest year specified is 2019, then any review before 2019.01.01 won't be counted)
    Note: the design of the function allows adding new functionalities, such as collecting review contents for text analysis
        
    Args:
        ASIN (str): the Amazon code for the product
        earliest_yr (int): the earliest year of the review
            
    Returns:
        pandas.DataFrame: all reviews' date and rating
    '''
    start=1
    df = pd.DataFrame(columns=['Date','Rate'])
    stop_date = datetime(earliest_yr-1,12,31)
    ua = UserAgent().random
    referer=None
    
    while True:
        review_link=get_review_page_link_with_number(ASIN,start)
        response = web_reader.get_response(review_link,ua,referer)

        start = start + 1

        sel = Selector(text=response)
        dates_raw = sel.xpath('//span[@data-hook="review-date"]/text()').extract()
        rates_raw = sel.xpath('//i[@data-hook="review-star-rating"]/span/text()').extract()
        date_pattern = re.compile('\w+\s\d+,\s\d+')
        rate_pattern = re.compile('\d\.0')

        table_date = [date_pattern.search(date).group() for date in dates_raw]
        table_rate = [rate_pattern.search(rate).group() for rate in rates_raw]

        if len(table_date) == 0: return df
        for date_item, rate_item in zip(table_date, table_rate):
            date = pd.to_datetime(date_item)

            if ((stop_date != None) and (date < stop_date)): return df
            rate = float(rate_item)
            a_line = {
                'Date':date, 
                'Rate':rate
            }
            df.loc[len(df)] = a_line
        referer = review_link

    return df


def organize_review(dataframe, list_yrs):
    '''
    count # of reviews for every month in every year & average rating for every year
    Note: more or different feature engineering functionalities can be added such as counting monthly average rating, NLP, etc.
    
    Args:
        dataframe (pandas.DataFrame): collection of all review data
        list_yrs (tuple of int): a list of years intended to be counted
    
    Returns:
        pandas.DataFrame: organized data
    '''
    
    orgd_df = pd.DataFrame(columns=['# of reviews', 'avg rating'])
    dataframe.set_index('Date', inplace=True)
    for yr in list_yrs:
        yr_name = str(yr)
        this_yr_df = dataframe[yr_name]
        this_yr_line = pd.DataFrame(index=[yr_name],columns=['# of reviews', 'avg rating'])
        this_yr_line['# of reviews'][yr_name] = len(this_yr_df)
        this_yr_line['avg rating'][yr_name] = np.mean(this_yr_df['Rate'])
        orgd_df = orgd_df.append(this_yr_line)
    return orgd_df



def quick_count(ASIN, counted_year, lower_bound=None):
    '''
    count # of review in this specific year for the given ASIN 
    note: this method is efficient only based on the following assumptions:
        1. you are counting the past year # of reviews
        2. the ASIN you are counting has large # of reviews
    
    Args:
        ASIN (str): the Amazon code for the product
        counted_year (int): the year of review that is counted
        lower_bound (int, optional): given lower_bound number    
    Returns:
        int: # of reviews in the given year
    '''
    
    date_pattern = re.compile('\w+\s\d+,\s\d+')
    ua = UserAgent().random
    
    def find_upper_bound(ASIN, counted_year, num, prev=False, referer=None):
        '''
        find the page where the year of reviews transist from the given year to the given year's previous year
        and the number of this year's review in this page 
        (e.g. if you want to count 2019's review, this function will find you the page that transists from 2019 to 2018;
         if the page number is 10 and there are 4 reviews written in 2019, page 10 and count 4 will be returned)
        this also considers the case when one page is full of this year's reviews and next page is full of previous year's reviews
        (e.g. page 10's all reviews were written in 2019, and page 11's all reviews were written in 2018)
        
        Args:
            ASIN (str): the Amazon code for the product
            counted_year (int): the year of review that is counted
            num (int): the page number that is checked
            prev (bool, optional): whether the previous page has the year's review
            referer (str, optional): the referer url
        Returns:
            int: # of this year's reviews in the page number
            int: the page number that transist from the given year to the given year's previous year
        '''
        
        nonlocal date_pattern
        nonlocal ua
        page_link = get_review_page_link_with_number(ASIN,num)
        response = web_reader.get_response(page_link,ua)
        sel = Selector(text=response)
        
        dates_raw = sel.xpath('//span[@data-hook="review-date"]/text()').extract()
        dates = [pd.to_datetime(date_pattern.search(date).group()).year for date in dates_raw]
        
        if (dates[0] < counted_year):
            if (prev):
                bound = num
                count = 0
                return count, bound
            else:
                return find_upper_bound(ASIN, counted_year, num-1, referer=page_link)
        elif (dates[0] == counted_year):
            if (dates[-1] < counted_year):
                bound = num
                count = dates.count(counted_year)
                return count, bound
            elif (dates[-1] == counted_year):
                return find_upper_bound(ASIN, counted_year, num+1, prev=True, referer=page_link)
        else:
            if dates[-1] <= counted_year:
                bound = num
                count = dates.count(counted_year)
                return count, bound
            return find_upper_bound(ASIN, counted_year, num+1, referer=page_link)
                
                
    def find_lower_bound(ASIN, counted_year, num, prev=False, referer=None):
        '''
        find the page where the year of reviews transist from the given year to the given year's next year
        and the number of this year's review in this page 
        (e.g. if you want to count 2019's review, this function will find you the page that transists from 2019 to 2020;
         if the page number is 10 and there are 4 reviews written in 2019, page 10 and count 4 will be returned)
        this also considers the case when one page is full of this year's reviews and next page is full of previous year's reviews
        (e.g. page 10's all reviews were written in 2019, and page 9's all reviews were written in 2020)
        
        Args:
            ASIN (str): the Amazon code for the product
            counted_year (int): the year of review that is counted
            num (int): the page number that is checked
            prev (bool): whether the previous page has the year's review
            referer (str, optional): the referer url
        Returns:
            int: # of this year's reviews in the page number
            int: the page number that transist from the given year to the given year's next year
        '''
        
        nonlocal date_pattern
        nonlocal ua
        page_link = get_review_page_link_with_number(ASIN,num)
        response = web_reader.get_response(page_link,ua)
        sel = Selector(text=response)
        
        dates_raw = sel.xpath('//span[@data-hook="review-date"]/text()').extract()
        dates = [pd.to_datetime(date_pattern.search(date).group()).year for date in dates_raw]
        
        if (dates[-1] > counted_year):
            if (prev):
                bound = num
                count = 0
                return count, bound
            else:
                return find_lower_bound(ASIN, counted_year, num+1, referer=page_link)
        elif (dates[-1] == counted_year):
            if (dates[0] > counted_year):
                bound = num
                count = dates.count(counted_year)
                return count, bound
            elif (dates[0] == counted_year):
                return find_lower_bound(ASIN, counted_year, num-1, prev=True, referer=page_link)
        else:
            if dates[0] >= counted_year:
                bound = num
                count = dates.count(counted_year)
                return count, bound
            
            return find_upper_bound(ASIN, counted_year, num+1, referer=page_link)
            
        
    #total_count: total this year reviews
    total_count = 0
    #count_low: # of this year review on the lower_bound page
    #lower_bound: the page where the target year ends (e.g. target = 2019: 2019->2020)
    count_low=0
    #count_up: # of this year review on the upper_bound page
    #upper_bound: the page where the target year starts (e.g. target = 2019: 2018->2019)
    count_up=0
    
    response_first = web_reader.get_response(get_review_page_link_with_number(ASIN,1),ua)
    sel_first = Selector(text=response_first)
    
    first_dates_raw = sel_first.xpath('//span[@data-hook="review-date"]/text()').extract()
    
    #case 1: no reviews
    if len(first_dates_raw) == 0: return 0, None
    first_dates = [pd.to_datetime(date_pattern.search(date).group()).year for date in first_dates_raw]
    
    #case 2: only one page
    if len(first_dates) < 10: return first_dates.count(counted_year), 1
    
    
    total_review_line = sel_first.xpath('//span[@data-hook="cr-filter-info-review-count"]/text()').extract()[0]
    digit_pattern = re.compile('\s(\d+(?:,\d+)*)\s')
    total_review = int(digit_pattern.search(total_review_line).group().replace(',',''))
    if total_review > 5000: total_review = 5000
    print("Total reviews:", total_review)
    last_page_number = ceil(total_review/10)

    response_last = web_reader.get_response(get_review_page_link_with_number(ASIN,last_page_number),ua)
    sel_last = Selector(text=response_last)
    last_dates_raw = sel_last.xpath('//span[@data-hook="review-date"]/text()').extract()
    last_dates = [pd.to_datetime(date_pattern.search(date).group()).year for date in last_dates_raw]
    
    #first_last_diff = the year of first review - the year of last review
    first_last_diff = first_dates[0] - last_dates[-1]
    
    #first_count_diff = the year of first review - the counted year
    first_count_diff = first_dates[0] - counted_year
    
    today_month = datetime.now().month
    percent = today_month/12.0
    

    if (not lower_bound):
        lower_bound= max(floor(last_page_number * (first_count_diff + percent -1) /first_last_diff), 1)
    
    upper_bound = floor(last_page_number * (first_count_diff+percent) /first_last_diff)
    
    #case 3: the year of first review < the counted year
    if (first_count_diff < 0): return 0, None
    
    #case 4: if total page number < 10: count one by one
    if last_page_number <= 10:
        data = find_all_reviews(ASIN, counted_year)
        data.set_index('Date',inplace=True)
        try:
            data = data[str(counted_year)]
            total_count = len(data)
            print("ASIN:", ASIN, "total review:", total_count)
            return total_count, None
        except:
            print("ASIN:", ASIN, "total review:", 0)
            return 0, None
        
    #case 3: first review year = last review year = counted year => all reviews are from the counted year
    if ((first_last_diff == 0) and (last_dates[-1] == counted_year)):
        print("ASIN:", ASIN, "total review:", total_review)
        return total_review, None
        '''
        #case 4: first review year = last review year ≠ counted year => all reviews are not from the counted year
        elif first_last_diff == 0:
        print("ASIN:", ASIN, "total review:", 0)
        return 0
        '''
    #case 4: last review's year > counted year => all reviews are written after the counted year
    elif (last_dates[-1] > counted_year): 
        print("ASIN:", ASIN, "total review:", 0)
        return 0, None
    
    #case 5: last review's year = counted year => upper bound is the last page
    elif (last_dates[-1] == counted_year): 
        count_up = last_dates.count(counted_year)
        upper_bound = last_page_number
        count_low, lower_bound = find_lower_bound(ASIN, counted_year, lower_bound)
    
    #case 5: first page's last review's year = counted year => lower bound is the first page
    elif (first_dates[-1] == counted_year):
        count_low = first_dates.count(counted_year)
        lower_bound = 1
        count_up, upper_bound = find_upper_bound(ASIN, counted_year, upper_bound)
    else:
        #this case will assume year_diff >= 3 and you just want to count the last year review
        count_low, lower_bound = find_lower_bound(ASIN, counted_year, lower_bound)
        count_up, upper_bound = find_upper_bound(ASIN, counted_year, upper_bound)
    
    if upper_bound == lower_bound:
        total_count =  count_up
    else:    
        total_count = 10 * (upper_bound - lower_bound - 1) + count_low + count_up
        
    print("ASIN:", ASIN, "lower_bound:", lower_bound, "upper_bound:", upper_bound, "total review:", total_count)
    return total_count, upper_bound