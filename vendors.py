import requests
import pandas as pd

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



"""
Finds the total amount of contract rewards when given a request dictionary.
"""
def get_award_amount(dict):
    awardTotal = 0
    for i in range(len(dict['results'])):
        awardTotal += dict['results'][i]["Award Amount"]
    return awardTotal

"""
Prints the awards in descending order when given a request dictionary.
"""
def print_awards(dict):
    if len(dict['results']) == 0:
        print("No results found.")
        return
    else:
        for i in range(len(dict['results'])):
            print(f"Award #{int(i+1)}: {dict['results'][i]['Award Amount']:.2f} ")
        return


"""Pandas Dataframe work"""

def generateDataFile(dict):
    
    if len(dict) == 0:
        print("No results found.")
        return
    else:
        try:
            #Normalizing content from Results column
            res_data = pd.json_normalize(dict['results'])

            #Creating a Pandas dataframe for the json data and then copying desired columns
            df = pd.DataFrame(data=res_data)
            df2 = df[['Award ID','Recipient Name','Start Date','End Date','Award Amount']].copy()

            #Porting data to a csv
            df2.to_csv('data.txt', sep="\t", index=False)
            return
        except KeyError as e:
            print("ERROR: Company name or SAM UEI not found.")




def main():
    #Accepting user input for the desired company
    recipient = ""
    while len(recipient) <= 2:
        recipient = input("Input the name or SAM UEI number of the desired company. ")
        if len(recipient) <= 2:
            print("Please enter more than two characters.")

    payload['filters']['recipient_search_text'] = [f'{recipient}']

    #TODO: HTTP Error handling
    request = requests.post("https://api.usaspending.gov/api/v2/search/spending_by_award", json=payload)

    request_dict = request.json()

    

    generateDataFile(request_dict)
    

if __name__=="__main__": 
    main() 