import requests
import os.path
import pandas as pd
from vendors import payload

"""
Sends a call to the API after being given the recipient name from a DataFrame object and a POST request payload.
Returns "request_dict": The response object from the API Call in the form of a python dictionary.
"""
def processRequest(recipient, payload):
    payload['filters']['recipient_search_text'] = [f'{recipient}']
    try:
        request = requests.post("https://api.usaspending.gov/api/v2/search/spending_by_award", json=payload, timeout=5)
        request.raise_for_status()
        request_dict = request.json()   
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
Generates a csv file to import into a spreadsheet program.
Input: A dictionary object and a file name
Returns: None
"""
# def generateDataFile(dict, file):
#     #Check if the file exists
#     if exists(file):

           
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
    df = pd.read_csv('testsheet.csv')

    #Response dictionary: Final dictionary to be used to build the csv file
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

    pf2 = pd.DataFrame.from_dict(res_dict['results'])
    print(pf2)



   

if __name__=="__main__": 
    main() 