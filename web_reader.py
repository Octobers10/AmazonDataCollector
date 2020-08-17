#Web Request
import urllib3

#Web Request Enhancer
import certifi

#Other
import random
import sys
import time
import logging


def get_response(url, ua, referer=None):
    '''
    downloads webpage of the given url
    
    Args:
        url (str): link that needed to be download
        ua (str): user-agent 
        referer (str): link that specify the referer
    
    Returns:
        byte string: downloaded webpage
    '''
    
    #ua='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36'
    ran=random.randint(5,10)
    print("         Start scraping")
    
    my_headers = {
        "User-Agent":ua, 
        "Accept-Encoding":"gzip, deflate", 
        "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", 
        "DNT":"1",
        "Connection":"close", 
        "Upgrade-Insecure-Requests":"1"
        #will add cookies in the future
    }
    
    if (referer):
        my_headers['referer'] = referer
        
    https = urllib3.PoolManager(
        cert_reqs='CERT_REQUIRED',
        ca_certs=certifi.where()
    )
                
    try:
        response = https.request(
            'GET',
            url, 
            headers=my_headers,
            redirect=True,
            timeout=urllib3.Timeout(total = 15.0),
            assert_same_host=True
        )
        logging.info("         Start sleeping:", ran)
        time.sleep(ran)
        logging.info("         Stop sleeping")
        return response.data
    except:
        logging.error("!!!   Unexpected error from web_reader.get_response:", sys.exc_info(), "   !!!")
        return None
        