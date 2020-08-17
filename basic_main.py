import web_reader
import find_basic as fb
import xlwings as xw 
import sys
from fake_useragent import UserAgent
import pandas as pd

#Global Variables initialization

#write_file is the dataframe that stores the data
write_file=pd.DataFrame()

def welcome_display():
    '''
    displays the welcome message and read the data file (xlsx or csv)
    
    Args: 
        None
    
    Returns:
        pandas.Series: the list of ASINs
    '''
    
    read_file = None
    print("====================================================================")
    print("        Welcome to use Amazon Basic Info Collection Tool 1.0        ")
    print("====================================================================")
    print("Instruction: ")
    print("Step 1: ")
    file_option=0
    while True:
        print(" Choose the type of file you just open: ")
        print("1. .xlsx")
        print("2. .csv")
        file_option=input()
        if file_option == '1':
            try:
                wb = xw.books.active.fullname
                read_file=pd.read_excel(wb)['ASIN']
                break
            except:
                print(sys.exc_info())
                input("Please open the Excel file, press return when you are ready")
                continue
        
        if file_option == '2':
            try: 
                wb = xw.books.active.fullname
                read_file=pd.read_csv(wb,encoding = "Latin1",error_bad_lines=False)['ASIN']
                break
            except:
                print(sys.exc_info())
                input("Please open the csv file, press return  when you are ready")
                continue 
            
        input("Please enter a valid option (1/2), press return to continue")
    return read_file

def search_fill(read_file):
    '''
    searchs and fills every ASIN's product information
    
    Args: 
        pandas.Series: the list of ASINs
    '''
    
    print("====================================================================")
    print("======================     Start scraping     ======================")
    print("====================================================================")
    
    global write_file
    ua = UserAgent().random

    for ASIN in read_file:
        print("Start scraping ASIN:", ASIN)
        write_line = {}
        write_line['ASIN']=ASIN
        main_page_link = fb.get_main_page_link(str(ASIN))
        write_line['Link'] = main_page_link
        main_page_response = None
        referer = 'https://www.google.com/'
        try:
            main_page_response = web_reader.get_response(main_page_link,ua,referer)
        except:
            write_line['Brand']='Err'
            write_line['SKU Number'] = 'Err'
            write_line['Title']='Err'
            write_line['Long Description']='Err'
            write_line['Price'] = 'Err'
            failure = 0
            continue 

        #Brand & SKU are in the product detail table
        try:
            product_detail_table = fb.find_table(main_page_response)
            write_line['Brand']=fb.find_brand(product_detail_table,main_page_response)
            write_line['SKU Number'] = fb.find_SKU(product_detail_table)
        except:
            print("Unexpected error for product_detail_table:", sys.exc_info())
            write_line['Brand']='Err'
            write_line['SKU Number'] = 'Err'
        try: 
            write_line['Title']=fb.find_title(main_page_response)
            write_line['Long Description']=fb.find_long_description(main_page_response)
            write_line['Price'] = fb.find_price(main_page_response)
        except:
            print("Unexpected error for Description & Price:", sys.exc_info())
            write_line['Title']='Err'
            write_line['Price'] = 'Err'
            write_line['Long Description']='Err'
        write_line_df = pd.DataFrame(write_line,index=[ASIN])
        write_file = write_file.append(write_line_df)

def end_display():
    '''
    displays the ending message and save the scraped data into Excel file
    '''
    
    global write_file
    write_file.to_excel("ASIN_Basic_Info.xlsx", sheet_name='Data')
    print("====================================================================")
    print("Task finished. The file is saved as \"ASIN_Basic_Info.xlsx\". Thank you for using Amazon Data Collection Tool.")
    print("====================================================================")

def main():
    '''
    starts the entire operation that collects basic information for given ASINs
    '''
    
    read_file = welcome_display()
    search_fill(read_file)
    end_display()