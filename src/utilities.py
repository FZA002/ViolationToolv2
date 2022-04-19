'''

This file contains various utlities used throughout the tool. 

'''
import os, sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

 # Creates a folder for this program's data
def setup_savedata():
    abs_home = os.path.abspath(os.path.expanduser("~"))
    home_folder_path = abs_home + "/ViolationTool2/"

    # Create all folders if they don't already exist
    if not os.path.exists(home_folder_path):
        os.mkdir(home_folder_path)
    
    # Make all necessary folders
    folders = ["rawdata"]
    #folders = ["assets", "rawdata", "scraper_pages", "dataframes", "dataframes/saved", "dataframes/new"]
    for folder in folders:
        if not os.path.exists(home_folder_path + folder):
            os.mkdir(home_folder_path + folder)

            '''
            # The if statements ensure that if folders already exist, nothing is overwritten
            # In other words only use default program data if this is the first time the program has been run
            if folder == "dataframes/saved":
                dest = home_folder_path + "dataframes/saved/"
                src = nhi.resource_path("dataframes/saved/")
                for file in os.listdir(src):
                    source = src + file
                    destination = dest + file
                    shutil.copy(source, destination)
            
            elif folder == "assets":
                dest = home_folder_path + "assets/"
                src = nhi.resource_path("assets/")
                for file in os.listdir(src):
                    source = src + file
                    destination = dest + file
                    shutil.copy(source, destination)
            '''