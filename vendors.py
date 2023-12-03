import requests
import os.path
import pandas as pd
import time
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
Sends a call to the API after being given the recipient name from a DataFrame object and a POST request payload.
Returns "request_dict": The response object from the API Call in the form of a python dictionary.
"""
def processRequest(recipient, payload):
    payload['filters']['recipient_search_text'] = [f'{recipient}']
    try:
        request = requests.post("https://api.usaspending.gov/api/v2/search/spending_by_award", json=payload) #Rememebr to add back timeout=10
        request.raise_for_status()
        request_dict = request.json()
        time.sleep(0.25)   
    except requests.exceptions.HTTPError as errh:
        print(errh)
    except requests.exceptions.ConnectionError as errc:
        print(errc)
    except requests.exceptions.Timeout as errt:
        print(errt)
    except requests.exceptions.RequestException as erre:
        print(erre)
    return request_dict



           
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

def main():
    # Reading in and sanitizing the data from the csv file
    pd.options.display.float_format = '{:.2f}'.format
    df = pd.read_csv('vendorssheet.csv')
    df = df[['Vendor', 'SAM UEI']]
    #Drops NaN values from the table
    df = df.dropna()
    #Resetting index to 6
    #NOTE: Hard-coded value. Need to find a way to make this value dynamic
    df.index = df.index-6
    print(df)
    #Response dictionary: Final dictionary to be used to build the csv file

    """
    NOTE: Pretty slow execution, especially if we'll be dealing with hundreds/thousands of companies.
    Function calls slow down execution, so maybe just do everything inside main? Leads to messier code but potentially faster execution times
    """
    start = time.time()
    res_dict = {'results':[]}
    for i in range(len(df['SAM UEI'])):
        
        #Response object in the form of a python dictionary
        
        response = processRequest(df['SAM UEI'][i], payload)
        
        #Current award total being processed
        curAwardTotal = getAwardTotal(response)
       
        #Current company being processed
        curCompany = df['Vendor'][i]

        #Appends the company name and total award amount to the dictionary
        res_dict['results'] += [{"Company Name": curCompany,"Total Awards": curAwardTotal}]

        print(f"Processed {i+1}/{len(df['SAM UEI'])} items...")

    pf2 = pd.DataFrame.from_dict(res_dict['results'])
    
    print(pf2)

    # #TODO: Check if data.txt exists and then make a txt file

    pf2.to_csv("data.txt", sep='\t', index=False)
    end = time.time()

    print(f"Process finished in: {end - start:2f} seconds")

if __name__=="__main__": 
    main() 