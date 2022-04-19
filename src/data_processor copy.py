'''
This program downloads data from https://data.cms.gov/provider-data.
It downloads raw data in the form of multiple CSV files from mutliple
pages, and combines them into a pandas dataframe. Specifically, it grabs
the latest Penalties and Health Deficiencies CSV's.

'''
import requests, os, utilities
from bs4 import BeautifulSoup as bs

# This is where all the save data lies
abs_home = os.path.abspath(os.path.expanduser("~"))
home_folder_path = abs_home + "/ViolationTool2/"
utilities.setup_savedata()

url = "https://data.cms.gov/provider-data/search?theme=Nursing%20homes%20including%20rehab%20services"

import csv
import requests

CSV_URL = 'https://data.cms.gov/provider-data/api/1/datastore/query/r5ix-sfxw/0?limit=0&offset=0&count=true&results=true&schema=true&keys=true&format=json&rowIds=false'


