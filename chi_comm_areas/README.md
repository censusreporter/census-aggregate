# Chicago Community Areas aggregation

Data prep:
* fetch Rob Paral's Excel spreadsheet, from http://robparal.blogspot.com/2012/04/census-tracts-in-chicago-community.html
* convert it to CSV using `csvkit`
* fetch Community Area JSON from Chicago Tribune Crime API: http://crime.chicagotribune.com/api/1.0-beta1/communityarea/?format=json&limit=0
* rewrite just the 'objects'
(these were done separately to avoid adding more python dependencies to this library)
* run make_xref.py to knit them together in a slightly more friendly form

