# Home Health Details

The main dataframe will be from:
hhq = pd.read_csv("https://data.cms.gov/provider-data/api/1/datastore/query/6jpm-sxkc/0/download?format=csv", encoding="iso_8859-1")

The state by state quality breakdown will be an optional sheet:
hhs = pd.read_csv("https://data.cms.gov/provider-data/api/1/datastore/query/tee5-ixt5/0/download?format=csv", encoding="iso_8859-1")

The date range data will be suplementary data to the other two
mdr = pd.read_csv("https://data.cms.gov/provider-data/api/1/datastore/query/c886-nwpj/0/download?format=csv", encoding="iso_8859-1")
    - I will have to make date ranges and use them when filtering~
    - I will have to match the measures to the other data frames, probably manually

Will not let the user filter on dates, but will provide them with which measures have a date range as a forced sheet in the optional page


Options to implement 
    ~~Show averages for an org per measure~~
    ~~Exclude certain types of ownership~~
    Star range (could do a picker for 0 to 5 stars)
    