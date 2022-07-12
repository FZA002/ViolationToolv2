import pickle, pandas as pd, os
abs_home = os.path.abspath(os.path.expanduser("~"))
home_folder_path = abs_home + "/ViolationToolv2/"

# with open(home_folder_path + "dataframes/df.pkl", 'rb') as inp:
#     df = pickle.load(inp)

with open(home_folder_path + "dataframes/hhc_df.pkl", 'rb') as inp:
    hhq = pickle.load(inp)

ownership_types = list(df['type_of_ownership'].unique()) # List of the different ownership types organizations can have
ownership_types.remove("-")

excluded_types = []
options = 
for type in ownership_types:
    if options[type]: # If the types value is True, the user chose to exclude it
        excluded_types += [type]
