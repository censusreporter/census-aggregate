import csv

with open("seattle.csv") as infile:
    reader = csv.DictReader(infile)
    with open("xref.csv","w") as outfile:
        w = csv.writer(outfile)
        w.writerow(['tract','area_id','area_name'])
        seen = set()
        for row in reader:
            tract = row['GEOID10'][:-4] 
            if tract not in seen:
                cra_id = row['CRA_NO']
                cra_name = row['CRA_NAME']
                w.writerow([tract, cra_id, cra_name])
                seen.add(tract)
