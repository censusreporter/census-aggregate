census-aggregate
----------------
A tool to aggregate American Community Survey data to non-census geographies.

Aggregated data for Chicago community areas and New York city neighborhood tabulation areas can be found at http://j.mp/public_census_data

The generated tables for medians, quintiles and quartiles are NOT CORRECT. See https://github.com/censusreporter/census-aggregate/issues/1

Status
------
At the moment, the library is tuned towards producing data for Chicago's community areas, but it's pretty generalized.

To use the tool, create a cross-reference table which lists all the census tracts in your city and matches each one to the area it's part of. Something like this: 

tract|area_id|area_name
-----|-------|---------
17031010100|01|Rogers Park
17031010201|01|Rogers Park
17031010202|01|Rogers Park
17031010300|01|Rogers Park

It's assumed that every tract fits into a single area, but the code takes advantage of the **080** summary level, which accounts for tracts which are only partially within a given place (city/town/etc).

Right now the tool is dependent upon having direct SQL access to a copy of the Census Reporter database. What that probably means is you should send me your cross-reference file and I'll run the job for you -- it's not a lot of work.

But if you really wanted to fool with the code or run this yourself, here's a writeup on [how to set our database up for yourself in the AWS cloud](http://censusreporter.tumblr.com/post/55886690087/using-census-data-in-postgresql). You can also [import the data into your existing Postgres DB](http://censusreporter.tumblr.com/post/73727555158/easier-access-to-acs-data) but be warned that the expanded ACS 5-year data uses over 160GB of storage.

Using the data
--------------
At the moment, I'm just going to put the aggregated files on Github. The column headers in the files are coded, so you will probably want to look at the accompanying `.txt` file to know what the columns represent. There's also an `all_tables.txt` file you can use to find specific tables if you don't know what you're looking for.

