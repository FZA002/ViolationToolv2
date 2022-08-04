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
    odf = odf.rename(columns={'facility_name':'provider_name'}) # Rename the columns
    ldf = ldf.merge(odf[['provider_name', 'ownership_type', 'total_number_of_beds']], on='provider_name') # Combine the dataframes here
    ldf = ldf[['provider_state', 'provider_name', 'provider_city', 'address_line_1',
       'address_line_2', 'phone_number', 'ownership_type', 'total_number_of_beds', 'measure_code', 'score', 'footnote',
       'start_date', 'end_date']]

    return ldf



        