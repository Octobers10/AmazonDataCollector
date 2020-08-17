#Web Parser
from datetime import datetime
import random
from string import ascii_letters, digits
from scrapy import Selector


#2. Variation Table
manufacture_variation_list = ('Brand Name', 'manufacturer', 'Manufacturer')


def text_cleaner(old_string):
    '''
    does data cleaning for a string; specifically, take out new line characters and extra whitespaces
    
    Args:
        old_string (str): the string that needed to be cleaned
        
    Returns:
        a string that is cleaned (without extra whitespaces and new line characters)
    '''
    cleaned_string = " ".join("".join(old_string).replace('\n',"").split())
    return cleaned_string






def get_main_page_link(ASIN):
    '''
    generates the link to a Amazon product's main page
    
    Args:
        ASIN (str): the Amazon code for the product
    
    Returns: 
        string: the link to a Amazon product's main page
    '''
    
    def rand_code(length=8):
        '''
        generates a string composed by randomly chosen ascii characters with specified length

        Args:
            length (int, optional): the specified length of the string; default value is 8

        Returns:
            a string of randomly chosen ascii characters with specified length
        '''
        generate_code = ''.join([random.choice(
            ascii_letters + digits) for n in range(length)])
        return generate_code

    
    part1 = "https://amazon.com/"
    random_string2 =rand_code(8)+"/"
    dp3 = "dp/"
    ASIN4 = str(ASIN)
    ref5 = "/ref=sr_1_1?keywords="+ASIN
    lang6=""
    #"&language=en_US"
    time_stamp_now = datetime.now().timestamp()    
    qid7="&"+ str(int(time_stamp_now))
    sr8="&sr=8-1"
    url = part1 + random_string2 + dp3 + ASIN4 + ref5 + lang6 + qid7 + sr8
    print("     main page url: ", url)
    return url







def find_table(response_data):
    '''
    extract the product detail table part of the Amazon product page
    
    Args:
        response_data (byte string): the downloaded Amazon product webpage
    
    Returns:
        dictionary: elements in the production detail table if they are found 
        or 
        None: if ihe table is not found
    '''
    
    sel = Selector(text=response_data)
    keys = [text_cleaner(key) for key in sel.xpath('//table[@id="productDetails_techSpec_section_1" or @id="productDetails_techSpec_section_2" or @id="productDetails_detailBullets_sections1"]//tr/th/text()').extract()]
    old_vals = [text_cleaner(val) for val in sel.xpath('//table[@id="productDetails_techSpec_section_1" or @id="productDetails_techSpec_section_2" or @id="productDetails_detailBullets_sections1"]//tr/td/text()').extract()]
    vals = [val for val in old_vals if val not in [')', '']]
    table = dict(zip(keys,vals))
    return table


def find_brand(table_dictionary, response_data):
    '''
    find the manufacturer/brand of the product 
    
    Args:
        table_dictionary (dictionary): a dictionary of elements in the production detail table
        response_data (byte string): the downloaded Amazon product webpage
    
    Returns:
        string: the manufacturer's name 
        or 
        None if it is not found
    '''
    
    #step 1: check if it is shown in the dictionary
    brand = None
    for manfacturer in manufacture_variation_list:
        brand = table_dictionary.get(manfacturer)
        if brand is not None: return brand
    
    #step 2: check if it is shown under the product title
    sel = Selector(text=response_data)
    new_sel = Selector(text=response_data)
    brand = text_cleaner(sel.xpath('//a[@id="bylineInfo"]/text()').extract())
    return brand


def find_SKU(table_dictionary):
    '''
    find the SKU of the product 
    
    Args:
        table_dictionary (dictionary): a dictionary of elements in the production detail table
    
    Returns:
        string: SKU
        or 
        None: if it is not found
    '''
    SKU = table_dictionary.get('Item model number', 'N/A')
    return SKU

def find_price(response_data):
    '''
    find the price of the product 
    
    Args:
        response_data (byte string): the downloaded Amazon product webpage
    
    Returns:
        string: price
        or 
        None: if it is not found
    '''
    sel = Selector(text=response_data)    
    price = text_cleaner(sel.xpath('//span[@id="priceblock_saleprice" or @id="priceblock_ourprice"]/text()').extract())

    return price

def find_title(response_data):
    '''
    find the title of the product 
    
    Args:
        response_data (byte string): the downloaded Amazon product webpage
    
    Returns:
        string: title
        or 
        None: if it is not found
    '''
    
    sel = Selector(text=response_data)
    title = text_cleaner(sel.xpath('//span[@id="productTitle" and @class="a-size-large"]/text()').extract())
    return title


def find_long_description(response_data):
    '''
    find the description of the product 
    
    Args:
        response_data (byte string): the downloaded Amazon product webpage
    
    Returns:
        string: description
        or 
        None: if it is not found
    '''
        
    sel = Selector(text=response_data)
    description = sel.xpath('//div[@id="feature-bullets"]/descendant::span[@class="a-list-item"]/text()').extract()
    cleaned_description = [item for item in [text_cleaner(line) for line in description] if item != ""]
    description = "\n".join(cleaned_description)
    return description
