import pandas as pd
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

def download_data():
    ''' Downloads data related to Nursing Home organizations and returns the dataframes to be saved
        by the main download method in utilities.py as a dictionary. '''
    
    # Url for Penalties and Health Deficiencies dataset queries
    p_urls = "https://data.cms.gov/provider-data/api/1/datastore/query/g6vv-u9sr/0/download?format=csv"
    hd_urls = "https://data.cms.gov/provider-data/api/1/datastore/query/r5ix-sfxw/0/download?format=csv"

    pdf = pd.read_csv(p_urls, encoding="iso_8859-1") # Penalites
    hdf = pd.read_csv(hd_urls, encoding="iso_8859-1") # Health Deficiencies

    # Combine the nursing home dataframes
    hdf['fine_amount'] = ""
    hdf.update(pdf)
    hdf = hdf[['federal_provider_number', 'provider_name', 'provider_state',
        'provider_city', 'provider_address', 'survey_date', 'survey_type', 'deficiency_prefix', 'deficiency_category',
        'deficiency_tag_number', 'deficiency_description', 'scope_severity_code', 'deficiency_corrected', 
        'correction_date','fine_amount']]

    # Get tags and their descriptions and save it into a dictionary
    tags = hdf[['deficiency_tag_number', 'deficiency_description']].drop_duplicates()
    tags = dict(zip(tags['deficiency_tag_number'], tags['deficiency_description']))

    return {"hdf":hdf, "tags":tags}