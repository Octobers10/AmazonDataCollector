import web_reader
import find_review as fr

import xlwings as xw 
import sys
import logging
from datetime import datetime
import time

import numpy as np
import pandas as pd

#Global Variables initialization

#write_file is the dataframe that stores the data
write_file=pd.DataFrame()

def welcome_display():
    '''
    displays the welcome message and read the data file (xlsx or csv)
    
    Returns:
        pandas.Series: the list of ASINs
    '''
    
    read_file=None
    file_option=0
    print("====================================================================")
    logging.info("          Welcome to use Amazon Data Collection Tool 1.0              ")
    print("          Welcome to use Amazon Data Collection Tool 1.0              ")
    print("====================================================================")
    print("Instruction: ")
    print("Step 1: ")
    while True:
        print(" Choose the type of file you just open: ")
        print("1. .xlsx")
        print("2. .csv")
        file_option=input()
        wb = xw.books.active.fullname
        if file_option == '1':
            try:
                read_file=pd.read_excel(wb)['ASIN']
                return read_file
            except:
                print(sys.exc_info())
                input("Please open the Excel file, press return when you are ready")
                continue
        
        if file_option == '2':
            try: 
                read_file=pd.read_csv(wb,encoding = "Latin1",error_bad_lines=False)['ASIN']
                return read_file
            except:
                print(sys.exc_info())
                input("Please open the csv file, press return when you are ready")
                continue 
            
        input("Please enter a valid option (1/2), press return to continue")
        
    print("Step 2: ")



def var_list_generator(year_list, count_month=False):
    '''
    generates the variable list for output data
    
    Args: 
        year_list (tuple of int): the list of year intended to be counted
        count_month (bool): whether to collect review data in monthly basis
        
    Returns:
        tuple of str: the list of variable names
    '''
    
    var = ['ASIN']
    for year in year_list: 
        str_year = str(year)
        if count_month: 
            for month in np.arange(12,0,-1):
                str_month = str(month) if month/10 >= 1 else '0'+str(month)
                var.append(str_year+'-'+str_month)
            var = var + [str_year+' total review', str_year+' avg rating']
        else:
            var = var + [str_year]
    return tuple(var)

def set_count_year():
    '''
    sets the year that the user want to count 
    
    Returns:
        tuple of int: list of year number in descending order
    '''
    
    year_list = None
    this_year  = datetime.today().year
    while True:
        print(" Enter the year you want to count, seperated by comma (e.g. 2019,2018,2017)")
        year_string=input()
        try:
            year_list=year_string.split(",")
            for i, year in enumerate(year_list):
                year_list[i] = int(year)
                if int(year) > this_year:
                    print("Invalid year included, please try again (press enter key to continue)")
                    input()
                    continue
        except:
            print("Invalid year included, please try again (press enter key to continue)")
            input()
            continue
        
        year_list.sort(reverse=True)
        return tuple(year_list)

def set_count_month():
    '''
    set whether to collect review data in monthly basis
    
    Returns:
        bool: whether to collect review data in monthly basis
    '''
    while True:
        print(" Enter '1' if you want to count monthly data, '2' if you don't: ")
        count_month=input()
        if count_month == '1':
            return True
        
        if count_month == '2':
            return False
        
        input("Please enter a valid option (1/2), press return to continue")


def search_fill(read_file, count_month, year_list, var_list):
    '''
    searchs and fills every ASIN's product information
    
    Args: 
        read_file (pandas.Series): the list of ASINs
        count_month (bool): whether to count data on monthly basis
        year_list (tuple of int): the list of years the user want to count
        var_list (tuple of string): the list of names of variables that will be collected
    '''
    global write_file
    
    logging.info("======================     Start scraping     ======================")
    

    for ASIN in read_file:
        logging.info("Start searching for ASIN:", ASIN)
        write_line = {}
        write_line['ASIN']=ASIN
        if count_month:
            all_review_data = fr.find_all_reviews(ASIN, year_list[-1])
            if (isinstance(all_review_data,pd.DataFrame)):
                orgd_review_df = fr.organize_review(all_review_data,year_list)
                str_year_list=list(map(str,year_list))
                for index, row in orgd_review_df.iterrows():
                    if (index in str_year_list):
                        year_total_review_name =  index + ' total review'
                        year_avg_rating_name = index + ' avg rating'
                        write_line[year_total_review_name] = row['# of reviews']
                        write_line[year_avg_rating_name] = row['avg rating']
                    else:
                        write_line[index]=row['# of reviews'] 
            else:
                orgd_review_df = fr.organize_review(pd.DataFrame(),year_list)
                str_year_list=list(map(str,year_list))
                for index, row in orgd_review_df.iterrows():
                    if (index in str_year_list):
                        year_total_review_name =  index + ' total review'
                        year_avg_rating_name = index + ' avg rating'
                        write_line[year_total_review_name] = 'Err'
                        write_line[year_avg_rating_name] = 'Err'
                    else:
                        write_line[index]='Err'
                
        else:
            upper_bound=1
            for year in year_list:
                year_total_review_name =  str(year) + ' total review'
                if (upper_bound):
                    try:
                        total_review, upper_bound = fr.quick_count(ASIN, year, upper_bound)
                        write_line[year_total_review_name] = total_review
                    except: 
                        logging.error(sys.exc_info())
                        write_line[year_total_review_name] = 'Err'
                else: 
                    write_line[year_total_review_name] = 0
        write_line_df = pd.DataFrame(write_line,index=[ASIN])
        write_file = write_file.append(write_line_df, ignore_index=True)


def end_display():
    '''
    displays the ending message and save the scraped data into Excel file
    '''

    global write_file
    current_time = str(datetime.now())
    file_name = "Total Reviews " + current_time + ".xlsx"
    write_file.to_excel(file_name, sheet_name='Data')
    print("====================================================================")
    logging.info("Task finished. The file is saved as \"" +file_name +"\". Thank you for using Amazon Data Collection Tool.")
    print("Task finished. The file is saved as \"" +file_name +"\". Thank you for using Amazon Data Collection Tool.")
    print("====================================================================")

def main():
    read_file = welcome_display()
    count_month = set_count_month()
    year_list = set_count_year()
    var_list = var_list_generator(year_list,count_month)
    search_fill(read_file, count_month, year_list, var_list)
    end_display()