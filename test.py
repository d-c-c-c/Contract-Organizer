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

#TODO: Write a function to determine what file type is being used

def main():
    df = pd.read_csv('testsheet.csv')
    # print(df.keys())
    # for val in df['SAM UEI']:
    #     print(val)

    #print(df['SAM UEI'][2])

    #Response object in the form of a python dictionary
    response = processRequest(df['SAM UEI'][2], payload)
    
    print(getAwardTotal(response))
   
    if exists('data.txt'):
        print('True')
    else:
        print('False')

   

if __name__=="__main__": 
    main() 