import csv
import json

csvfile = open('./static/nutrients_dataset.csv', 'r')
jsonfile = open('./static/nutrients.json', 'w')
data = json.load(jsonfile)

# print(data['Exercise Values'][0]["Activity, Exercise or Sport (1 hour)"d])

# fieldnames = ("Activity, Exercise or Sport (1 hour)","130 lb","155 lb","180 lb","205 lb","Calories per kg")
fieldnames = ("")
reader = csv.DictReader( csvfile, fieldnames)
for row in reader:
    json.dump(row, jsonfile)
    jsonfile.write(',')