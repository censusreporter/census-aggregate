import csv

with open("nyc2010census_tabulation_equiv.csv") as infile:
    reader = csv.reader(infile)
    for x in range(0,5): # skip five rows of headers
        header = reader.next()
    with open("xref.csv","w") as outfile:
        w = csv.writer(outfile)
        w.writerow(['tract','area_id','area_name'])
        for borough_name, county_fips, borough_code, tract, puma, area_id, area_name in reader:
            w.writerow(['36%s%s' % (county_fips,tract), area_id, area_name])
