# Seattle Neighborhood Districts

The city of Seattle maintains a mapping of each census block to a number of local areas. Specifically, there are 53 "community reporting areas," or "CRAs" which are based on neighborhoods. These CRAs are grouped into 13 "neighborhood districts." CRAs and districts are aligned with census tracts, so that each tract is completely within one neighborhood and one district.

Seattle comprises 136 census tracts. CRAs range in size from 1 to 7 tracts (median 2 tracts) and neighborhood districts are 5 to 17 tracts (median 10 tracts).

Seattle also has a concept of "urban village," but urban villages can divide tracts, and so are not currently being aggregated.

http://www.seattle.gov/dpd/cs/groups/pan/@pan/documents/web_informational/dpdd017073.xlsx

Data prep:
* fetch "Seattle Census Blocks and Neighborhoods Correlation" from http://www.seattle.gov/dpd/cityplanning/populationdemographics/geographicfilesmaps/2010census/default.htm
* convert it to CSV using `csvkit`'s `in2csv dpdd017073.xlsx > seattle.csv`
* run make_xref.py to knit them together in a slightly more friendly form


