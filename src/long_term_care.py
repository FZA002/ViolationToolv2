import pandas as pd

def download_data():
    ''' Downloads data related to Home Health Care organizations and returns the dataframes to be saved
       by the main download method in utilities.py as a dictionary. '''

    # Download data for long term care hopsitals for organizations and states as a csv, turn it into a dataframe
    # with only relevant columns
    ldf = pd.read_csv("https://data.cms.gov/provider-data/api/1/datastore/query/fp6g-2gsn/0/download?format=csv", encoding="iso_8859-1")
    ldf = ldf[['state', 'facility_name', 'city', 'address_line_1','address_line_2',
       'phone_number', 'measure_code', 'score', 'footnote', 'start_date', 'end_date']]
        
    # Rename the columns
    ldf = ldf.rename(columns={
        'state':'provider_state',
        'facility_name':'provider_name',
        'city':'provider_city'
    })

    # Download hlong term care hopsitals data related to ownership type and number of beds  
    odf = pd.read_csv("https://data.cms.gov/provider-data/api/1/datastore/query/azum-44iv/0/download?format=csv", encoding="iso_8859-1")
    odf = odf[['state', 'facility_name', 'city', 'address_line_1','address_line_2',
       'phone_number', 'ownership_type', 'total_number_of_beds']]

    # Rename the columns
    odf = odf.rename(columns={
        'state':'provider_state',
        'facility_name':'provider_name',
        'city':'provider_city'
    })

    # Combine the dataframes here
    ldf['ownership_type'] = odf[odf['ownership_type'] if ldf['provider_name'] == odf['provider_name'] else None]

    return {"ldf":ldf, 'odf':odf}
    

# frames = download_data()
# ldf, odf= frames['ldf'], frames['odf']
# print(ldf.head(), odf.head())



        