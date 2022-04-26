import pickle, pandas as pd, os
abs_home = os.path.abspath(os.path.expanduser("~"))
home_folder_path = abs_home + "/ViolationToolv2/"

with open(home_folder_path + "dataframes/df.pkl", 'rb') as inp:
    df = pickle.load(inp)