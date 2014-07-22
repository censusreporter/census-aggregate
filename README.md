census-aggregate
----------------
A tool to aggregate American Community Survey data to non-census geographies.

The generated tables for medians, quintiles and quartiles are NOT CORRECT. See https://github.com/censusreporter/census-aggregate/issues/1

Status
------
At the moment, the library is tuned towards producing data for Chicago's community areas, but it's pretty generalized.

Aggregated data for local geographies in Chicago, New York and Seattle can be found at http://j.mp/public_census_data, along with some more explanation of the data. If you know of other locally relevant cross-reference data, please file a [GitHub issue](http://github.com/censusreporter/census-aggregate/issues)

More Details
------------
Right now the tool is dependent upon having direct SQL access to a copy of the Census Reporter database. What that probably means is you should send me your cross-reference file and I'll run the job for you -- it's not a lot of work.

But if you really wanted to fool with the code or run this yourself, here's a writeup on [how to set our database up for yourself in the AWS cloud](http://censusreporter.tumblr.com/post/55886690087/using-census-data-in-postgresql). You can also [import the data into your existing Postgres DB](http://censusreporter.tumblr.com/post/73727555158/easier-access-to-acs-data) but be warned that the expanded ACS 5-year data uses over 160GB of storage.

To use the tool, create a cross-reference table which lists all the census tracts in your city and matches each one to the area it's part of. Something like this: 

tract|area_id|area_name
-----|-------|---------
17031010100|01|Rogers Park
17031010201|01|Rogers Park
17031010202|01|Rogers Park
17031010300|01|Rogers Park

Right now, the column names are hard coded, and in fact, aggregate.py has some hard-coded bits since this only gets run once in a while.

It's assumed that every tract fits into a single area, but the code takes advantage of the **080** summary level, which accounts for tracts which are only partially within a given place (city/town/etc).

Using the data
--------------
At the moment, I'm just going to put the aggregated files on Github. The column headers in the files are coded, so you will probably want to look at the accompanying `.txt` file to know what the columns represent. There's also an `all_tables.txt` file you can use to find specific tables if you don't know what you're looking for.

Even more generally
-------------------
If you've read this far you're a data nerd and probably a census data nerd. One of the goals of our Census Reporter project is to make tools to lower barriers to public use of Census data. We're not here to do your data analysis for you, but we don't want people reinventing the wheel for common data use cases. Drop a line if you have ideas for tools or want to help. For more general questions about "where can I find X in the Census", please use the [OpenData Stack Exchange](http://opendata.stackexchange.com/) and be sure to tag your question ["census"](http://opendata.stackexchange.com/questions/tagged/census).