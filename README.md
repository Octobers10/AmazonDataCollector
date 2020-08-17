# AmazonDataCollector
AmazonDataCollector is a project I wrote to automate and optimize data collection/analysis process during work. Currently it supports 
1. collecting product ranking data by keywords  
2. collecting product basic information (title, description, price, brand, etc.) by ASINs
3. collecting product review information (number of review, date of review, rating of review) by ASINs and given year range

## Usage
1. Download this folder and fill the template CSV file with the keywords/ASINs
2. run '''$ pip install -r requirements.txt'''
3. run '''$ ./main.py'''
Then you just need to follow the instruction given by the program and get your .xlsx/.csv file ready.
You can download the template.xlsx file for filling the information required for data collection (keywords or ASINs).
The sample cleaned output of all three kinds of data (merged) is in the demo.xlsx file. 

## Workflow
1. Create keywords that you are interested in
2. Collect product ranking data by keywords to see what products are ranked high under these keywords
3. Remove duplicated ASINs, and collect product basic information
4. Collect product review information
(Optional) If you want to classify products using the data collected and you have labelled trainning data available, this tool is designed for product classification:
https://github.com/Octobers10/AmazonProductClassification

