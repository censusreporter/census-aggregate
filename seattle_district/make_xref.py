import csv

with open("seattle.csv") as infile:
    reader = csv.DictReader(infile)
    with open("xref.csv","w") as outfile:
        w = csv.writer(outfile)
        w.writerow(['tract','nd_id','nd_name'])
        seen = set()
        for row in reader:
            tract = row['GEOID10'][:-4] 
            if tract not in seen:
                nd_id = row['NEIGHBORHOOD_DISTRICT_NUMBER']
                nd_name = row['NEIGHBORHOOD_DISTRICT_NAME']
                w.writerow([tract, nd_id, nd_name])
                seen.add(tract)
