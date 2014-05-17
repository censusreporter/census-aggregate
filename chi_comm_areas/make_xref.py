import json
import csv

ca_list = json.load(open("comm_area_list.json"))

ca_names = dict((str(x['area_number']).zfill(2),x['name']) for x in ca_list)

r = csv.DictReader(open("Tract_to_Community_Area_Equivalency_File.csv"))

with open("xref.csv","w") as f:
    w = csv.writer(f)
    w.writerow(['tract','area_id','area_name'])
    for row in r:
        if row['CHGOCA']: # lots of blank rows in Rob's source
            tract = '17' + row['COUNTY'] + row['TRACT']
            w.writerow([tract, row['CHGOCA'], ca_names[row['CHGOCA']]])
