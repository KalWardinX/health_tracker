import csv
import json

# csvfile = open('nutrients_csvfile.csv', 'r')
jsonfile = open('file.json', 'r')
data = json.load(jsonfile)

print(data['Nutrition Values'])

# fieldnames = ("Food", "Grams", "Calories", "Protein", "Fat", "Sat.Fat", "Fiber", "Carbs")
# reader = csv.DictReader( csvfile, fieldnames)
# for row in reader:
#     json.dump(row, jsonfile)
#     jsonfile.write(',')