import requests, requests_cache
from requests_cache import CachedSession
import os.path
import pandas as pd
import time
from datetime import timedelta
import re

#Session Caching settings

session = CachedSession(allowable_methods=('Get, POST'), expire_after=timedelta(days=7)) #Change to multiple hours/days

"""Constant Values"""
# List of import key words in the program. Used for determining the primary key for a file, or used for obtaining vendor information.
POSSIBLE_KEY_NAMES = ['SAM UEI','SAMUEI','Company Name','Organization Name','Name','Vendor','Vendor Name']
POSSIBLE_VENDOR_NAMES = ['Company Name','Organization Name','Name','Vendor','Vendor Name']

#POST request to send to the API
payload = {
    "subawards": "false",
    "limit": 60,
    "order": "desc",
    "page": 1,
    "sort": "Award Amount",
    "filters": {
          "award_type_codes": ["A", "B", "C","D"],
          "recipient_search_text":[''], #Empty pending user input
          "time_period": [{"start_date": "2021-01-01", "end_date": "2023-10-01"}]
      },
    "fields": [
         "Award ID",
          "Recipient Name",
          "Start Date",
          "End Date",
          "Award Amount",
          "Awarding Agency",
          "Awarding Sub Agency",
          "Contract Award Type",
          "Award Type",
          "Funding Agency",
          "Funding Sub Agency"
    ]
}


"""Pandas Dataframe work"""

"""
Find and set the primary key in a dataset based on the list of column names.
TODO: Currently using hardcoded values. Find a way to make this dynamic.
"""
def findPrimaryKey(lst):
    
    pKey = None
    # SAM UEI is the desired value. Check for that first
    if 'SAM UEI' in lst:
        pKey = 'SAM UEI'
        return pKey
    
    #If SAM UEI is not in the list, check for alternatives
    for item in lst:
        if item.lower() in [name.lower() for name in POSSIBLE_KEY_NAMES]:
            pKey = item
            break
    return pKey

"""
Finds the name of the column containing the names of all companies. Returns None if the name in the user supplied file doesn't match the current
list of possible names.
"""
def findCompanyColumn(lst):
    cName = None
    for item in lst:
        if item.lower() in [name.lower() for name in POSSIBLE_VENDOR_NAMES]:
            cName = item
            break
    return cName
"""
Calculates the total amount of contract award money for a specific company
"""
def getAwardTotal(dict):
    awardTotal = 0
    if len(dict['results']) == 0:
        return awardTotal
    else:
        for i in range(len(dict['results'])):
            awardTotal += dict['results'][i]['Award Amount']
    return awardTotal

"""
Checks if the data file already exists for not
"""
def exists(file):
    path = f'./{file}'
    check_file = os.path.isfile(path)
    return check_file

"""Cleans a string of excess characters such as '', \n, and \t"""
def cleanStr(str):
    str = str.replace('\t', '').replace('\n', '').replace('"', '')
    return str

def main():
    # Reading in and sanitizing the data from the csv file
    pd.options.display.float_format = '{:.2f}'.format

    # Check user input to determine if the file is valid, if it is, check the file extension to determine which function to use
    while True:
        try:
            # List of columns in the resulting dataframe; To be used later
            columnList = []
            file = input("Input the file name here (.txt, .csv, .xlsx): ")
            # Isolating the file extension to determine which Dataframe function to use

            #TODO: !!!Re-add csv files as an option. Super buggy right now!!!

            match = re.search(r'(xlsx|XLSX|txt|TXT)$', file)
            extension = match.group(0)

            if extension == "xlsx":
                df = pd.read_excel(f'{file}', engine='openpyxl')
                columnList = list(df.columns)
            else:
                df = pd.read_csv(f'{file}', sep="delimiter")
                columnList = list(df.columns)
                # csv column names seem to all be in one string
                # Clean csv data
                # TODO: Add a check in case there's more than one item in the csv list
                # TODO: Find a way to split even if there's no comma
                columnList = columnList[0].split(',')
                if '' in columnList:
                    columnList.remove('')
                for item in range(len(columnList)):
                    columnList[item] = cleanStr(columnList[item])
            break
        except AttributeError:
            print("ERROR: Please enter a file with a valid extension (.txt, .csv, .xlsx).")
            time.sleep(0.25)
            continue
   
    
   
    #Value for the Primary Key; Whichever column will be used for parsing through the Dataframe and the Response data
    pKey = findPrimaryKey(columnList)
    #Removing NaN rows at the beginning of the file
    for i in range(len(df[pKey])):
        value = df[pKey][i]
        if type(value) == float:
            df = df.drop([i])
        else:
            continue
    #print(df)

    cName = findCompanyColumn(columnList)

    print(pKey)
    print(cName)
    print(columnList)
    #Response dictionary: Final dictionary to be used to build the csv file

    """
    NOTE: Pretty slow execution, especially if we'll be dealing with hundreds/thousands of companies.
    Function calls slow down execution, so maybe just do everything inside main? Leads to messier code but potentially faster execution times
    """
    start = time.time()
    res_dict = {'results':[]}
    for i in range(len(df[pKey])):
        
        #Response object in the form of a python dictionary
        
        payload['filters']['recipient_search_text'] = [f'{df[pKey][i]}']
        try:
            request = session.post("https://api.usaspending.gov/api/v2/search/spending_by_award", json=payload) #Rememebr to add back timeout=10
            request.raise_for_status()
            response = request.json()
 
        except requests.exceptions.HTTPError as errh:
            print(errh)
        except requests.exceptions.ConnectionError as errc:
            print(errc)
        except requests.exceptions.Timeout as errt:
            print(errt)
        except requests.exceptions.RequestException as erre:
            print(erre)
        except Exception as e: #Catch generic exceptions
            print(e)

        #response = processRequest(df['SAM UEI'][i], payload)
        
        #Current award total being processed
        curAwardTotal = getAwardTotal(response)
       
        #Current company being processed
        curCompany = df[cName][i]

        #Appends the company name and total award amount to the dictionary
        res_dict['results'] += [{"Company Name": curCompany,"Total Awards": curAwardTotal}]

        print(f"Processed {i+1}/{len(df[pKey])} items...")

    pf2 = pd.DataFrame.from_dict(res_dict['results'])
    

    # # #TODO: Check if data.txt exists and then make a txt file

    pf2.to_csv("data.txt", sep='\t', index=False)
    end = time.time()

    print(f"Process finished in: {end - start:2f} seconds")

if __name__=="__main__": 
    main() 