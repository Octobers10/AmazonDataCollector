import web_reader
import xlwings as xw 
import sys
import datetime
from fake_useragent import UserAgent
import pandas as pd
from scrapy import Selector

#Global Variables initialization

#write_file is the dataframe that stores the data
write_file=pd.DataFrame(columns=['Scrape Term','ASIN','Rank'])

def welcome_display():
    '''
    displays the welcome message and read the data file (xlsx or csv)
    
    Returns:
        pandas.Series: the list of ASINs
    '''
    print("====================================================================")
    print("    Welcome to use Amazon Search Term Result Collection Tool 1.0    ")
    print("====================================================================")
    print("Instruction: ")
    print("Step 1: ")
    file_option=None
    read_file=None
    while True:
        print('Open the file with the "Search Terms" column, and choose the type of your file')
        print("1. .xlsx")
        print("2. .csv")
        file_option=input()
        wb=None
        if file_option == '1':
            try:
                wb = xw.books.active.fullname
                read_file=pd.read_excel(wb)['Search Terms'].tolist()
                break
            except:
                print(sys.exc_info())
                input("Please open the Excel file, press return when you are ready")
                continue
        
        if file_option == '2':
            try: 
                wb = xw.books.active.fullname
                read_file=pd.read_csv(wb)['Search Terms'].tolist()
                break
            except:
                print(sys.exc_info())
                input("Please open the csv file, press return  when you are ready")
                continue 
            
        input("Please enter a valid option (1/2), press return to continue")
    return read_file

def set_num_product():
    '''
    sets the number of product that the user want to count for one search term
    
    Returns:
        list of int: list of year number in descending order
    '''
    while True:
        print("Enter the number of review you want to collect for each search term (it has to be a positive integer):")
        num = input()
        try:
            num = int(num)
            if num > 0:
                num_of_product = num
                break
            else: 
                input("Please enter a valid number, press return to continue")
        except: 
            input("Please enter a valid number, press return to continue")

def first_page_url_generator(search_term):
    '''
    generates the link to Amazon search result page 1 for the given search term
    
    Args:
        search_term (str): the given search term
    
    Returns: 
        string: the link to Amazon search result page 1 for the given search term
    '''
    
    part1 = "https://www.amazon.com/s?k="
    part2=search_term.replace(" ", "+")
    part3="&ref=nb_sb_noss"
    url = part1+part2+part3
    return url

def following_page_url_generator(search_term, page_num):
    '''
    generates the link to Amazon search result page for the given search term and page number
    
    Args:
        search_term (str): the given search term
        page_num (int): page number
        
    Returns: 
        string: the link to Amazon search result page for the given search term and page number
    '''
    page = str(page_num)
    part1="https://www.amazon.com/s?k="
    part2=search_term.replace(" ", "+")
    part3="&page="+page
    part4 = "&qid="+ str(int(datetime.now().timestamp()))
    part5 = "&ref=sr_pg_"+str(page_num-1)
    url = part1+part2+part3+part4+part5
    return url

def parser(seach_term, response_data, counter):
    all_list=Selector(text=response_data).xpath('//div[@data-asin]').extract()
    data = pd.DataFrame()
    for item in all_list:
        new_sel = Selector(text=item)
        asin = "".join(new_sel.xpath('//div/@data-asin').extract())
        index = "".join(new_sel.xpath('//div/@data-index').extract())
        if "Sponsored" in str(new_sel.xpath('//span[@class="a-size-base a-color-secondary"]/text()').extract()): #filter sponsered products
            continue
        if((asin == "") or (index == "")): continue
        counter =  counter + 1 
        data = data.append({'Scrape Term': seach_term, 'ASIN': asin, "Rank": counter}, ignore_index=True)
    return data, counter

def end_display(rank):
    '''end_display() function display the ending message'''
    global write_file
    by_range = write_file['Rank'] <= rank
    write_file = write_file[by_range]
    current_time = str(datetime.datetime.now())
    file_name = "Search_Result_ASIN " + current_time + ".xlsx"
    write_file.to_excel(file_name, sheet_name='Data',index=False)
    print("====================================================================")
    print("Task finished. The file is saved as \"" +file_name +"\". Thank you for using Amazon Data Collection Tool.")
    print("====================================================================")

def main():
    global write_file
    raw_search_term_list = welcome_display()
    num_of_product = set_num_product()
    print("====================================================================")
    print("======================     Start scraping     ======================")
    print("====================================================================")
    
    ua = UserAgent().random
    for search_term in raw_search_term_list:
        counter=0
        first_page_link = first_page_url_generator(search_term)
        response = web_reader.get_response(first_page_link,ua)
        data, counter = parser(search_term, response,counter)
        write_file = write_file.append(data, ignore_index=True)
        page_num=2
        while (counter < num_of_product):
            new_link = following_page_url_generator(search_term, page_num)
            response = web_reader.get_response(new_link,ua)
            data, counter = parser(search_term, response, counter)
            write_file = write_file.append(data, ignore_index=True, sort=False)
            page_num = page_num + 1
    
    end_display(num_of_product)