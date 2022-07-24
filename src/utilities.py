'''
This file downloads data from https://data.cms.gov/provider-data.
It downloads raw data in the form of multiple CSV files from mutliple
pages, and turns them into pandas dataframes. Specifically, it grabs
the latest Penalties and Health Deficiencies CSV's. It also contains
various utility functions for back-end processes of gui.py.

'''
import pickle, sys, os, time, info, nursing_homes, home_health_care, long_term_care
import pandas as pd
from datetime import datetime
# Get imports from parent directory
sys.path.insert(1, os.path.join(sys.path[0], '..'))
import guis.gui as gui
import warnings
warnings.filterwarnings('ignore')

# This is where all the save data lies
abs_home = os.path.abspath(os.path.expanduser("~"))
home_folder_path = abs_home + "/ViolationToolv2/"

TESTING = False
TERRITORIES_LOADED = False # Turned False after certain data that is shared amongst make sheets is loaded for the first time
STATES_CONVERTED = False

def resource_path(relative_path):
    ''' Get absolute path to resource, works for dev and for PyInstaller '''
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def download(frame):
    ''' Downloads CSV's from cms.gov and saves them as pandas dataframes. Also saves the date that this method
        was executed so it can be displayed on the program's start page. '''

    # Make the dataframes and save them
    nursing_home_frames = nursing_homes.download_data()
    home_health_frames = home_health_care.download_data()
    ldf = long_term_care.download_data()
    hdf, tags = nursing_home_frames['hdf'], nursing_home_frames['tags']
    hhq, hhs, mdr = home_health_frames['hhq'], home_health_frames['hhs'], home_health_frames['mdr'] # Home Health Care
    
    # Save the new dataframes
    paths = ["assets/tag_hash.pkl", "dataframes/df.pkl", "dataframes/hhc_df.pkl",
            "dataframes/hhc_state_by_state_df.pkl", "dataframes/hhc_date_range_df.pkl", "dataframes/ltch_df.pkl"]
    dataframes = [tags, hdf, hhq, hhs, mdr, ldf]
    for idx, path in enumerate(paths):
        with open(f"{home_folder_path}{path}", 'wb') as outp:
            pickle.dump(dataframes[idx], outp, pickle.HIGHEST_PROTOCOL)
    
    # Save the date of this download
    today = datetime.now()
    today = str(today.month) + "/" + str(today.day) + "/" + str(today.year)
    with open(home_folder_path + "assets/lastupdate.pkl", 'wb') as outp:
        pickle.dump(today, outp, pickle.HIGHEST_PROTOCOL)

    # Update screen, show options page
    frame.show_options(True)


def make_sheets(frame: gui.SheetsPage, nursing_home_df, home_health_df, long_term_care_df, outpath):
    ''' Calls all functions that make sheets. '''

    # Make a folder for each dataset.
    datasets = ["NursingHomes", "HomeHealth", "LongTermCare"]
    for dataset in datasets:
        folder_path = f"{outpath}/{dataset}/"
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)

    make_nursing_home_sheets(frame, nursing_home_df, outpath)
    make_home_health_sheets(frame, home_health_df, outpath)
    make_home_long_term_care_sheets(frame, long_term_care_df, outpath)


def make_nursing_home_sheets(frame: gui.SheetsPage, df, outpath):
    ''' Makes the nursing home sheets based on options chosen by the user. Saves them to a folder chosen by the user. '''
    if TESTING:
        print("------- USING TEST VALUES FOR NURSING HOME -------")
    # Update the screen
    frame.instructions.config(text="Making Nursing Home sheets...")
    frame.instructions2.grid_forget()
    frame.sheet_btn.grid_forget()
    start_time = time.time()

    # Load in tag data 
    with open(home_folder_path + "assets/tag_hash.pkl", 'rb') as inp:
        tag_hash = pickle.load(inp)

    set_defaults(frame)
    dfs = {} # Holds optional dataframes that will be sheets
    years = list(range(frame.controller.startdate.year, frame.controller.enddate.year+1)) # Range of years from date filter

    # Check to see if tags were chosen and if not use all
    if len(frame.controller.tags) == 0:
        frame.controller.tags = list(tag_hash.keys())
        print("Used Default Tags")
    else:
        df = df.loc[df['deficiency_tag_number'].isin(frame.controller.tags)] 
        print("Filtered Tags, length: {}".format(len(df)))

    # Get dates in range for nursing home df
    df = get_inrange_nursing_homes(df, frame.controller.startdate, frame.controller.enddate)
    print("Filtered Dates")

    # Sort the dataframe by state and organization name 
    df = df.sort_values(by=["provider_state", "provider_name"])
    df = df[['provider_state', 'provider_name', 'provider_city', 
    'provider_address', 'federal_provider_number', 'survey_date', 'survey_type',
    'deficiency_prefix', 'deficiency_category', 'deficiency_tag_number',
    'deficiency_description', 'scope_severity_code', 'deficiency_corrected',
    'correction_date', 'fine_amount']]
    df = df.reset_index()
    df = df.drop(["index"], axis=1)
    
    # Convert fine column to numeric
    df['fine_amount'] = df['fine_amount'].apply(lambda x: 0 if x == "" else x)
    df['fine_amount'] = pd.to_numeric(df['fine_amount'], errors="coerce")

    # Make a dataframe for each territory (saved in a dict) and then only keep violations in date range
    t_dfs = sort_by_territories(df, frame.controller.territories)
    print("Made Territory Dataframes")

    # Sort through options
    if "Nursing Home" in frame.controller.options.keys():
        for option in frame.controller.options["Nursing Home"].keys():

    
            if option == "US Fines (Total, yearly)" and frame.controller.options["Nursing Home"][option]:
                start = time.time()

                if not "US" in dfs.keys():
                    dfs["US"] = pd.DataFrame(columns=(["Total"] + years))

                # Initialize indicies
                dfs["US"].loc["Fines"] = [0] * (len(dfs["US"].columns))
                
                # Conversion to date time objects for comparison
                oldcol = df['survey_date']
                df['survey_date'] =  pd.to_datetime(df['survey_date'], format='%Y-%m-%d')

                # Total sum -> after the df has been filtered on tags and date 
                sum = df['fine_amount'].sum()
            
                # Sum for each year
                for year in years:
                    # Make sure we are within the users date range  
                    yearstart, yearend = get_year_range(year, years, frame.controller.startdate, frame.controller.enddate)

                    # Get the year's sum and format it as currency
                    dfs["US"].at["Fines", year] = get_inrange_nursing_homes(df, yearstart, yearend)['fine_amount'].sum()

                # Change columns type back, add data to hash
                df['survey_date'] = oldcol
                dfs["US"].at["Fines", "Total"] = sum
                print(f"Made US Fines dataframe for Nursing Homes in {str(int(time.time() - start))} seconds")
                    
                        
            elif option == "US Violations (Total, yearly)" and frame.controller.options["Nursing Home"][option]:
                start = time.time()

                if not "US" in dfs.keys():
                    dfs["US"] = pd.DataFrame(columns=(["Total"] + years))

                # Initialize indicies
                dfs["US"].loc["Violations"] = [0] * (len(dfs["US"].columns))

                # Get total number of US violations within date range
                sum = count_violations_df(df)
            
                # Sum for each year
                for year in years:
                    # Make sure we are within the users date range  
                    yearstart, yearend = get_year_range(year, years, frame.controller.startdate, frame.controller.enddate)

                    # Get the year's sum
                    dfs["US"].at["Violations", year] = count_violations_df(get_inrange_nursing_homes(df, yearstart, yearend)) 

                # Add data to hash of dfs
                dfs["US"].at["Violations", "Total"] = sum
                print(f"Made US Violations dataframe for Nursing Homes in {str(int(time.time() - start))} seconds")


            elif option == "Top fined organizations (Total, yearly)" and frame.controller.options["Nursing Home"][option]:
                start = time.time()

                # dict[String, dict[String, List]]
                state_orgs = {}
                num = 3
                # For each state get the most fined overall
                state_orgs["Overall"] = {}
                for state in info.states_codes:
                    # Get subdf of a given state
                    subdf = df.loc[df['provider_state'] == state]
                    # Get a list of the most fined organizations across entire period
                    state_orgs["Overall"][state] = get_most_fined(subdf, num)
                    
                # Go through each year in range
                for year in years:
                    state_orgs[year] = {}
                    # Make sure we are within the users date range  
                    yearstart, yearend = get_year_range(year, years, frame.controller.startdate, frame.controller.enddate)

                    # Get top fined for each year
                    for state in info.states_codes:
                        # Get subdf of a given state
                        subdf = df.loc[df['provider_state'] == state]
                        subdf = get_inrange_nursing_homes(subdf, yearstart, yearend)
                        # Get a list of the most fined organizations across a year
                        state_orgs[year][state] = get_most_fined(subdf, num)

                # Make the multi-index columns
                cols = [(["Overall"] + years), ["Organization", "Fines"]]
                cols = pd.MultiIndex.from_product(cols, names=["Year", "Value"])
                dfs["Most Fined"] = pd.DataFrame(columns=cols)
                dfs["Most Fined"].insert(0, "State", "Not Set")

                # Populate the new df
                for state in info.states_codes:
                    for i in range(num):
                        row = [(state + str(i+1))]
                        for year in state_orgs.keys():
                            # Turn tuple with org and fine into list and add state to front
                            tups = state_orgs[year][state]
                            row += list(tups[i])

                        # Add row to dataframe
                        dfs["Most Fined"].loc[len(dfs["Most Fined"])] = row

                # Finally, make the state the vertical index and make fines currency
                dfs["Most Fined"] = dfs["Most Fined"].set_index(["State"])
                print(f"Made Top fined organizations per state dataframe for Nursing Homes in {str(int(time.time() - start))} seconds")
            

            elif option == "Most severe organizations (Total, yearly)" and frame.controller.options["Nursing Home"][option]:
                start = time.time()

                # dict[String, dict[String, List]]
                state_orgs = {}
                num = 3
                # For each state get the most severe overall
                state_orgs["Overall"] = {}
                for state in info.states_codes:
                    # Get subdf of a given state
                    subdf = df.loc[df['provider_state'] == state]
                    # Get a list of the most severe organizations across entire period
                    state_orgs["Overall"][state] = get_most_severe(subdf, num)
                    
                # Go through each year in range
                for year in years:
                    state_orgs[year] = {}
                    # Make sure we are within the users date range  
                    yearstart, yearend = get_year_range(year, years, frame.controller.startdate, frame.controller.enddate)

                    # Get most severe for each year
                    for state in info.states_codes:
                        # Get subdf of a given state
                        subdf = df.loc[df['provider_state'] == state]
                        subdf = get_inrange_nursing_homes(subdf, yearstart, yearend)
                        # Get a list of the most severe organizations across a year
                        state_orgs[year][state] = get_most_severe(subdf, num)

                # Make the multi-index columns
                cols = [(["Overall"] + years), ["Organization", "Severity Score"]]
                cols = pd.MultiIndex.from_product(cols, names=["Year", "Value"])
                dfs["Most Severe"] = pd.DataFrame(columns=cols)
                dfs["Most Severe"].insert(0, "State", "Not Set")

                # Populate the new df
                for state in info.states_codes:
                    for i in range(num):
                        row = [(state + str(i+1))]
                        for year in state_orgs.keys():
                            # Turn tuple with org and severity into list and add state to front
                            tups = state_orgs[year][state]
                            row += list(tups[i])

                        # Add row to dataframe
                        dfs["Most Severe"].loc[len(dfs["Most Severe"])] = row

                # Finally, make the state the vertical index and make fines currency
                dfs["Most Severe"] = dfs["Most Severe"].set_index(["State"])
                print(f"Made Most severe organizations per state sheet for Nursing Homes in {str(int(time.time() - start))} seconds")

            elif option == "Sum of fines per state (Total, yearly)" and frame.controller.options["Nursing Home"][option]:
                start = time.time()
                dfs["State Fines"] = pd.DataFrame(columns=(["Total"] + years))

                # Initialize indicies
                for state in info.states_codes:
                    # Get row for each state, add total for a state first
                    subdf = df.loc[df['provider_state'] == state]
                    row = [subdf['fine_amount'].sum()]

                    for year in years:
                        yearstart, yearend = get_year_range(year, years, frame.controller.startdate, frame.controller.enddate)
                        subdf2 = get_inrange_nursing_homes(subdf, yearstart, yearend)
                        row += [subdf2['fine_amount'].sum()]
                    
                    dfs["State Fines"].loc[state] = row
                print(f"Made sum of fines per state per year sheet for Nursing Homes in {str(int(time.time() - start))} seconds")
                

            elif option == "Sum of violations per state (Total, yearly)" and frame.controller.options["Nursing Home"][option]:
                start = time.time()
                dfs["State Violations"] = pd.DataFrame(columns=(["Total"] + years))

                # Initialize indicies
                for state in info.states_codes:
                    # Get row for each state, add total for a state first
                    subdf = df.loc[df['provider_state'] == state]
                    row = [count_violations_df(subdf)]

                    for year in years:
                        yearstart, yearend = get_year_range(year, years, frame.controller.startdate, frame.controller.enddate)
                        subdf2 = get_inrange_nursing_homes(subdf, yearstart, yearend)
                        row += [count_violations_df(subdf2)]
                    
                    dfs["State Violations"].loc[state] = row
                print(f"Made sum of violations per state per year sheet for Nursing Homes in {str(int(time.time() - start))} seconds")


            elif option == "Sum of fines per tag (Total, yearly)" and frame.controller.options["Nursing Home"][option]:
                start = time.time()
                dfs["Tag Fines"] = pd.DataFrame(columns=(["Total"] + years))

                # Initialize indicies
                for tag in sorted(frame.controller.tags):
                    # Get row for each state, add total for a state first
                    subdf = df.loc[df['deficiency_tag_number'] == tag]
                    row = [subdf['fine_amount'].sum()]

                    for year in years:
                        yearstart, yearend = get_year_range(year, years, frame.controller.startdate, frame.controller.enddate)
                        subdf2 = get_inrange_nursing_homes(subdf, yearstart, yearend)
                        row += [subdf2['fine_amount'].sum()]
                    
                    dfs["Tag Fines"].loc[tag] = row
                print(f"Made sum of fines per tag per year sheet for Nursing Homes in {str(int(time.time() - start))} seconds")
                

            elif option == "Sum of violations per tag (Total, yearly)" and frame.controller.options["Nursing Home"][option]:
                start = time.time()
                dfs["Tag Violations"] = pd.DataFrame(columns=(["Total"] + years))

                # Initialize indicies
                for tag in sorted(frame.controller.tags):
                    # Get row for each state, add total for a state first
                    subdf = df.loc[df['deficiency_tag_number'] == tag]
                    row = [count_violations_df(subdf)]

                    for year in years:
                        yearstart, yearend = get_year_range(year, years, frame.controller.startdate, frame.controller.enddate)
                        subdf2 = get_inrange_nursing_homes(subdf, yearstart, yearend)
                        row += [count_violations_df(subdf2)]
                    
                    dfs["Tag Violations"].loc[tag] = row
                print(f"Made sum of violations per state per year sheet for Nursing Homes in {str(int(time.time() - start))} seconds")
            

            elif option == "Create sheet with all territories combined" and frame.controller.options["Nursing Home"][option]:
                start = time.time()
                # Get a dict of dfs by territory
                tdfs = sort_by_territories(df, frame.controller.territories)
                combined = pd.DataFrame()
                for terr in tdfs.keys():
                    combined = pd.concat([combined, tdfs[terr]])

                # Set indicies properly
                dfs["All Territories"] = combined.reset_index()
                dfs["All Territories"] = dfs["All Territories"].drop(["index"], axis=1)
                print(f"Made all territories combined sheet for Nursing Homes in {str(int(time.time() - start))} seconds")


            elif option == "Create sheet for all violations without territories" and frame.controller.options["Nursing Home"][option]:
                start = time.time()
                dfs["All US States"] = df
                print(f"Made all violations sheet for Nursing Homes in {str(int(time.time() - start))} seconds")

   
    # Make and save sheets
    save_csvs(t_dfs, dfs, outpath, "NursingHomes")
    make_nursing_homes_optional_workbook(tag_hash, outpath) # Makes csvs that have descriptions of different metrcs
    instructions = f"Nursing Home Sheets made in {str(int(time.time() - start_time))} seconds"
    frame.instructions.config(text=instructions)
    print(instructions)
    time.sleep(3)


def make_nursing_homes_optional_workbook(tag_hash, outpath):
    ''' Creates the optional data's Description sheet for nursing homes. '''
    items1 = list(tag_hash.items())
    items2 = list(info.severities.items())
    df1 = pd.DataFrame(items1, columns=["Tag", "Description"])
    df1 = df1.sort_values(by="Tag")
    df1 = df1.reset_index().drop("index", axis=1)
    df2 = pd.DataFrame(items2, columns=["Rank", "Description"])        
    df1.to_csv(f"{outpath}/NursingHomes/TagDescription_NursingHomes.csv")
    df2.to_csv(f"{outpath}/NursingHomes/SeverityRanks_NursingHomes.csv")


def make_home_health_sheets(frame: gui.SheetsPage, df, outpath):
    ''' Makes the home health sheets based on options chosen by the user. Saves them to a folder chosen by the user. '''

    # Update the screen
    frame.instructions.config(text="Making Home Health sheets...")
    frame.instructions2.grid_forget()
    frame.sheet_btn.grid_forget()
    start_time = time.time()
              
    dfs = {} # Optional sheets
    set_defaults(frame)

    # Filter out unwanted ownership types before anything else, if the user chose to exclude any
    if "Home Health" in frame.controller.options:
        df = exclude_ownership_types_home_health(df, frame.controller.options["Home Health"])
        print("Filtered Home Health ownership types")

    # Filter on the users chosen star range
    if not None in {frame.controller.lower_stars, frame.controller.higher_stars}:
        df = df[(df['quality_of_patient_care_star_rating'] >= frame.controller.lower_stars) & (df['quality_of_patient_care_star_rating'] <= frame.controller.higher_stars)]
        print("Filtered Star Range using user's choices")
    else:
        print("No Star Range chosen by user")


    # Make a dataframe for each territory (saved in a hash) and then only keep violations in date range
    t_dfs = sort_by_territories(df, frame.controller.territories)
    
    # Sort through options
    if "Home Health" in frame.controller.options.keys():
        for option in frame.controller.options["Home Health"].keys():

    
            if option == "State Statistics" and frame.controller.options["Home Health"][option]:

                with open(home_folder_path + "dataframes/hhc_state_by_state_df.pkl", 'rb') as inp:
                    dfs[option] = pickle.load(inp)
                    print(f"Loaded Home Health {option} data")


            elif option == "Measure Averages per Organization" and frame.controller.options["Home Health"][option]:

                dfs[option] = get_organization_averages(df)
                print(f"Loaded Home Health {option} data")
                    
        
            elif option == "Sheet With All Territories Combined" and frame.controller.options["Home Health"][option]:
                # Get a dict of dfs by territory
                tdfs = sort_by_territories(df, frame.controller.territories)
                combined = pd.DataFrame()
                for terr in tdfs.keys():
                    combined = pd.concat([combined, tdfs[terr]])
                dfs["AllTerritories"] = combined.reset_index()

                # Set indicies properly
                dfs["AllTerritories"] = dfs["AllTerritories"].drop(["index"], axis=1)
                print("Made all territories combined sheet for Home Health")


            elif option == "Sheet For All Violations in the Dataset Without Territories" and frame.controller.options["Home Health"][option]:
                dfs["AllUSStates"] = df.sort_values(by=["provider_state", "provider_name"])
                dfs["AllUSStates"] = dfs["AllUSStates"].reset_index()
                dfs["AllUSStates"] = dfs["AllUSStates"].drop(["index"], axis=1)
                print("Made all violations sheet for Home Health")


    # Sheet for date ranges
    with open(home_folder_path + "dataframes/hhc_date_range_df.pkl", 'rb') as inp:
        dfs["MeasureDateRanges"] = pickle.load(inp)
        print("Loaded Home Health measure date range data")

    # Make and save sheets
    save_csvs(t_dfs, dfs, outpath, "HomeHealth")
    instructions = f"Home Health Sheets made in {str(int(time.time() - start_time))} seconds"
    frame.instructions.config(text=instructions)
    print(instructions)
    time.sleep(3)
    frame.finish()


def make_home_long_term_care_sheets(frame: gui.SheetsPage, df, outpath):
    ''' Makes the long term care sheets based on options chosen by the user. Saves them to a folder chosen by the user. '''

    # Update the screen
    frame.instructions.config(text="Making Long Term Care sheets...")
    frame.instructions2.grid_forget()
    frame.sheet_btn.grid_forget()
    start_time = time.time()

    dfs = {}     # Optional sheets
    set_defaults(frame)

    # Filter out unwanted ownership types before anything else, if the user chose to exclude any
    if "Long Term" in frame.controller.options:
        df = exclude_ownership_types_long_term_care(df, frame.controller.options["Long Term"])
        print("Filtered Long Term ownership types")

    df = get_inrange_long_term_care(df, frame.controller.startdate, frame.controller.enddate) # Get dates in range
    print("Filtered Dates")


    # Filter on the users chosen bed range
    if not None in {frame.controller.lower_beds, frame.controller.higher_beds}:
        df = df[(df['total_number_of_beds'] >= frame.controller.lower_beds) & (df['total_number_of_beds'] <= frame.controller.higher_beds)]
        print("Filtered Bed Range using user's choices")
    else:
        print("No Bed Range chosen by user")

    # Make a dataframe for each territory (saved in a dict) and then only keep violations in date range
    t_dfs = sort_by_territories(df, frame.controller.territories)
    
    # Sort through options
    if "Long Term" in frame.controller.options.keys():
        for option in frame.controller.options["Long Term"].keys():
                

            if option == "Sheet With All Territories Combined" and frame.controller.options["Long Term"][option]:
                # Get a dict of dfs by territory
                tdfs = sort_by_territories(df, frame.controller.territories)
                combined = pd.DataFrame()
                for terr in tdfs.keys():
                    combined = pd.concat([combined, tdfs[terr]])

                # Set indicies properly
                dfs["AllTerritories"] = combined.reset_index()
                dfs["AllTerritories"] = dfs["AllTerritories"].drop(["index"], axis=1)


            elif option == "Sheet For All Violations in the Dataset Without Territories" and frame.controller.options["Long Term"][option]:
                dfs["AllUSStates"] = df.sort_values(by=["provider_state", "provider_name"])
                dfs["AllUSStates"] = dfs["AllUSStates"].reset_index()
                dfs["AllUSStates"] = dfs["AllUSStates"].drop(["index"], axis=1)

                print("Made all violations sheet for Long Term")


    # Make and save sheets
    save_csvs(t_dfs, dfs, outpath, "LongTermCare")
    instructions = "Long Term Sheets made in " + str(int(time.time() - start_time)) + " seconds"
    frame.instructions.config(text=instructions)
    print(instructions)
    time.sleep(3)
    frame.finish()


def convert_states(territories):
    ''' Converts states from full name into their two letter code Dict[String, List[String]]) -> Dict[String, List[String]] '''
    
    # Get two letter state code hash
    codes = info.get_state_codes()
    keys = list(codes.keys())
    vals = list(codes.values())
    for territory in territories.keys():

        # Convert actual state name to it's two letter code
        states = []
        for state in territories[territory]:
            index = vals.index(state)
            code = keys[index]
            states.append(code)

        # Replace territory in original hash with the newly translated list of states
        territories[territory] = states
    
    return territories

def sort_by_territories(df, territories):
    ''' Sort violations by territories for when we make a sheet. Also want to update
        territory values as we go through the dataframe. '''
    tdict = {}
    territorynames = list(territories.keys())

    # Create a hash where key is territory name and value is dataframe of related rows
    for name in territorynames:
        # Get subframe, add territory column and reset indicies
        tdict[name] = df[df['provider_state'].isin(territories[name])]
        tdict[name].insert(0,"territory", 0)
        tdict[name] = tdict[name].reset_index(drop=True)

        # Set territory column
        tdict[name] = tdict[name].replace({"territory": 0}, name)

    return tdict

def get_inrange_nursing_homes(df, start, end):
    ''' Gets a subframe where only violations with dates in a certain range are included. '''
    # Conversion to date time objects for comparison
    oldcol = df['survey_date']
    df['survey_date'] =  pd.to_datetime(df['survey_date'], format='%Y-%m-%d')
    new = df.loc[(df['survey_date'] >= start) & (df['survey_date'] <= end)]

    # Then revert columns back to strings
    new['survey_date'] = new['survey_date'].dt.strftime('%Y-%m-%d')
    df['survey_date'] = oldcol

    return new

def get_inrange_long_term_care(df, start, end):
    ''' Gets a subframe where only violations with dates in a certain range are included. '''
    # Conversion to date time objects for comparison
    old_start = df['start_date']
    old_end = df['end_date']
    df['start_date'] =  pd.to_datetime(df['start_date'], format='%m/%d/%Y')
    df['end_date'] =  pd.to_datetime(df['end_date'], format='%m/%d/%Y')
    # So rows included where the start date is on or after the start date filter, same for end date filter
    new = df.loc[(df['start_date'] >= start) & (df['end_date'] <= end)] 

    # Then revert columns back to strings
    new['start_date'] = new['start_date'].dt.strftime('%m/%d/%Y')
    new['end_date'] = new['end_date'].dt.strftime('%m/%d/%Y')
    df['start_date'], df['end_date'] = old_start, old_end
    
    return new 

def count_violations_df(df):
    ''' Counts the number of violations in a dataframe by counting the rows. '''
    return len(df)

def get_most_fined(df, num):
    ''' Returns a sorted list of tuples where each tuple contains an organization and total fines for a period. '''
    sums = []
    # Get the facility names
    facilities = df['provider_name'].unique()
    for name in facilities:
        # Convert fine column to a number so we can sum
        sum = df.loc[df['provider_name'] == name, 'fine_amount'].sum()
        if sum != 0:
            sums.append((name, sum))

    # Sort the list of tuples by fine
    sums = sorted(sums, key=lambda item: item[1], reverse=True)

    # Add place holders if not enough data
    if len(sums) < num:
        sums += [("NA", 0)] * (num - len(sums))
    
    # Format the sums to currenices
    for i, sum in enumerate(sums):
        if sum[0] != "NA":
            temp = list(sum)
            temp[1] = temp[1]
            sums[i] = tuple(temp)

    return sums[:num]

def get_most_severe(df, num):
    ''' Returns a sorted list of tuples where each tuple contains an organization and total violations for a period. '''
    sums = []
    # Get the facility names
    facilities = df['provider_name'].unique()
    for name in facilities:
        curdf = df.loc[df['provider_name'] == name]
        # Convert the severity column to numeric and sum it
        sum = curdf['scope_severity_code'].apply(lambda x: info.severity_ranks[x]).sum()
        if sum != 0:
            sums.append((name, sum))

    # Sort the list of tuples by violations
    sums = sorted(sums, key=lambda item: item[1], reverse=True)
    # Add place holders if not enough data
    if len(sums) < num:
        sums += [("NA", 0)] * (num - len(sums))

    return sums[:num]

def get_year_range(year, years, startdate, enddate):
    ''' Get proper bounds for a date range. '''
    if year == years[0]:
        yearstart = startdate
        yearend = datetime.strptime(str(year)+"-12-31", "%Y-%m-%d")
    elif year == years[-1]:
        yearstart = datetime.strptime(str(year)+"-01-01", "%Y-%m-%d")
        yearend = enddate
    else:
        yearstart = datetime.strptime(str(year)+"-01-01", "%Y-%m-%d")
        yearend = datetime.strptime(str(year)+"-12-31", "%Y-%m-%d")

    return (yearstart, yearend)

def set_defaults(frame):
    ''' Sets the default values for the date and territory filters if necessary. Also converts 
        territory states to two letter codes if necessary. '''
    global STATES_CONVERTED, TERRITORIES_LOADED
    # Check to see if territories were chosen and use default if not
    if len(frame.controller.territories) == 0:
        if TESTING:
            frame.controller.territories = {"Test_Territory": ["Maryland", "California", "Florida", "Texas"]}
        else:
            if not TERRITORIES_LOADED:
                TERRITORIES_LOADED = True
                frame.controller.territories = info.territories
                print("Used Default Territories")
    
    # Convert states to their two letter code
    if not STATES_CONVERTED:
        STATES_CONVERTED = True
        frame.controller.territories = convert_states(frame.controller.territories)
        print("Converted States to Two-Letter Codes")

    # Set default date filters if necessary
    if None in {frame.controller.startdate, frame.controller.enddate}:

        if TESTING:
            frame.controller.startdate = datetime.strptime("01/10/2018", '%m/%d/%Y')
            frame.controller.enddate = datetime.strptime("01/10/2020", '%m/%d/%Y')
        else:

            with open(home_folder_path + "dataframes/df.pkl", 'rb') as inp:
                df = pickle.load(inp)

            # Conversion to date time objects for min and max
            oldcol = df['survey_date']
            df['survey_date'] =  pd.to_datetime(df['survey_date'], format='%Y-%m-%d')

            frame.controller.startdate = df['survey_date'].min()
            frame.controller.enddate = df['survey_date'].max()

            # Convert date column back to string 
            df['survey_date'] = oldcol
            print("Used Default Dates")

def exclude_ownership_types_home_health(df: pd.DataFrame, options):
    ''' Filters out ownership types for home health data that the user chose to exclude. '''
    ownership_types = list(df['type_of_ownership'].unique()) # List of the different ownership types organizations can have
    ownership_types.remove("-")
    ownership_types.append("Undefined") # This represents "-" ownership type

    for type in ownership_types:
        if options[type]: # If the types value is True, the user chose to exclude it
            if type == "Undefined":
                df = df.loc[df['type_of_ownership'] != "-"]
            else:
                df = df.loc[df['type_of_ownership'] != type]

    # Turn "-" to NA, will only take effect if the used didn't chose to exclude Undefined
    df['type_of_ownership'] = df['type_of_ownership'].replace('-', "NA")

    return df

def exclude_ownership_types_long_term_care(df: pd.DataFrame, options):
    ''' Filters out ownership types for long term care hospital data that the user chose to exclude. '''
    ownership_types = list(df['ownership_type'].unique()) # List of the different ownership types organizations can have
    ownership_types.append("Undefined") # Use this to remove nan's if chosen by user
    ownership_types = [type for type in ownership_types if not pd.isnull(type)]

    for type in ownership_types:
        if options[type]: # If the types value is True, the user chose to exclude it
            if type == "Undefined":
                df = df.dropna(subset=['ownership_type'])
            else:
                df = df.loc[df['ownership_type'] != type]

    return df

def get_organization_averages(df):
    ''' Returns a dataframe with averages for different measures for each home 
        health care organization in the dataset. '''
    
    columns = list(df.columns)[6:] # Get rid of columns not related to measures
    measures = []
    for column in columns:
        if column.find("footnote") == -1: # If "footnote" isn't in the column name, it's a measure
            measures.append(column)

    averages_df = df.groupby('provider_name')[measures].mean()
    return averages_df

def save_csvs(territory_dfs, dfs, outpath, dataset):
    ''' Save the csv files to the appropriate folder. '''
    
    outpath = f"{outpath}/{dataset}"
    for terr in territory_dfs.keys():
        start = time.time()
        # Makes the sheets more organized
        if not territory_dfs[terr].empty:
            # Sort alphabetically by provider name
            territory_dfs[terr] = territory_dfs[terr].sort_values(by=["provider_state", "provider_name", "provider_city"])
            # Set indicies properly
            territory_dfs[terr] = territory_dfs[terr].reset_index()
            territory_dfs[terr] = territory_dfs[terr].drop(["index"], axis=1)

        territory_dfs[terr].to_csv(f"{outpath}/{terr}_{dataset}.csv")
        print(f"Made {terr}_{dataset}.csv: Wrote {str(len(territory_dfs[terr]))} rows to csv in {str(int(time.time() - start))} seconds")

    # Sheet for each set of options
    for dfname in dfs.keys():
        start = time.time()
        dfs[dfname].to_csv(f"{outpath}/{dfname}_{dataset}.csv")
        print(f"Made {dfname}_{dataset}.csv: Wrote {str(len(dfs[dfname]))} rows to csv {str(int(time.time() - start))} seconds")

    



    
