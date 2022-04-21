'''
This program downloads data from https://data.cms.gov/provider-data.
It downloads raw data in the form of multiple CSV files from mutliple
pages, and combines them into a pandas dataframe. Specifically, it grabs
the latest Penalties and Health Deficiencies CSV's.

'''
import requests, os, utilities
from bs4 import BeautifulSoup as bs
import pandas as pd

# This is where all the save data lies
save_data_path = os.path.abspath(os.path.expanduser("~")) + "/ViolationTool2/"
utilities.setup_savedata()

def download_csvs():

    import csv
    import requests

    CSV_URL = 'https://data.cms.gov/provider-data/api/1/datastore/query/r5ix-sfxw/0?limit=0&offset=0&count=true&results=true&schema=true&keys=true&format=json&rowIds=false'


    with requests.Session() as s:
        download = s.get(CSV_URL)

        decoded_content = download.content.decode('utf-8')

        cr = csv.reader(decoded_content.splitlines(), delimiter=',')
        my_list = list(cr)
        for row in my_list:
            print(row)
        print(len(my_list))


def csvs_to_pandas():

    # Url for Penalties and Health Deficiencies dataset queries
    p_urls = "https://data.cms.gov/provider-data/api/1/datastore/query/g6vv-u9sr/0/download?format=csv"
    hd_urls = "https://data.cms.gov/provider-data/api/1/datastore/query/r5ix-sfxw/0/download?format=csv"

    # Make the dataframes
    pdf = pd.read_csv(p_urls, encoding="iso_8859-1")
    hdf = pd.read_csv(hd_urls, encoding="iso_8859-1")

    
    

csvs_to_pandas("")