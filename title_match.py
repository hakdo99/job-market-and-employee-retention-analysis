from difflib import SequenceMatcher
import json
import csv

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

dict_from_csv = {}

# with open('C:/Users/dokha/school-projects/dummy_IBM.csv', mode='r') as inp:
#     reader = csv.reader(inp)
#     dict_from_csv = {rows[0]:rows[1] for rows in reader}

# print(dict_from_csv)

#df['score']= df.apply(lambda x: similar(x['job_title'], x['search_kw']), axis=1)
#print(similar('sales manager', 'sales executive'))
with open("C:/Users/dokha/school-projects/job-market-and-employee-engagement-dashboard/web/deployment/sample_data_select.json") as jsonfile:
    data = json.load(jsonfile)
print(data[0])
print(type(data[0]))
print(len(data))
