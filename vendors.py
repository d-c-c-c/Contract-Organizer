import requests
import pandas as pd

recipient = ""
while len(recipient) <= 2:
    recipient = input("Input the name or SAM UEI number of the desired company: ")
    if len(recipient) <= 2:
        print("Please enter more than two characters.")

payload = {
    "subawards": "false",
    "limit": 60,
    "order": "desc",
    "page": 1,
    "sort": "Award Amount",
    "filters": {
          "award_type_codes": ["A", "B", "C","D"],
          "recipient_search_text":[recipient],
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

request = requests.post("https://api.usaspending.gov/api/v2/search/spending_by_award", json=payload)

request_dict = request.json()

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

print_awards(request_dict)
print(f'Total awards: {get_award_amount(request_dict):.2f}' )

# Pandas Dataframe work
req_data = pd.json_normalize(request_dict['results'])
df = pd.DataFrame(data=req_data)
df2 = df[['Award ID','Recipient Name','Start Date','End Date','Award Amount']].copy()
print(df)
df.to_csv('data.txt', sep="\t", index=False)
#print(df2)
