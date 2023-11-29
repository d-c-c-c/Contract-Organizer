import requests

payload = {
    "subawards": "false",
    "limit": 60,
    "order": "desc",
    "page": 1,
    "sort": "Award Amount",
    "filters": {
          "award_type_codes": ["A", "B", "C","D"],
          "recipient_search_text":["HFHGBMAR2NH6"],
          "time_period": [{"start_date": "2020-10-01", "end_date": "2023-10-01"}]
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

#print(request.json())
request_dict = request.json()
print(len(request_dict['results']))
for i in range(len(request_dict['results'])):
    print(request_dict['results'][i]["Award Amount"])