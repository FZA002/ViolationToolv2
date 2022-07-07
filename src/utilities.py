'''
This file downloads data from https://data.cms.gov/provider-data.
It downloads raw data in the form of multiple CSV files from mutliple
pages, and turns them into pandas dataframes. Specifically, it grabs
the latest Penalties and Health Deficiencies CSV's. It also contains
various utility functions for back-end processes of gui.py.

'''
import pickle, sys, os, time, info, home_health_care, long_term_care, guis.gui as gui
import pandas as pd
from datetime import datetime

# This is where all the save data lies
abs_home = os.path.abspath(os.path.expanduser("~"))
home_folder_path = abs_home + "/ViolationToolv2/"

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

    # Url for Penalties and Health Deficiencies dataset queries
    p_urls = "https://data.cms.gov/provider-data/api/1/datastore/query/g6vv-u9sr/0/download?format=csv"
    hd_urls = "https://data.cms.gov/provider-data/api/1/datastore/query/r5ix-sfxw/0/download?format=csv"

    # Make the dataframes and save them
    pdf = pd.read_csv(p_urls, encoding="iso_8859-1") # Penalites
    hdf = pd.read_csv(hd_urls, encoding="iso_8859-1") # Health Deficiencies
    frames = home_health_care.download_data()
    hhq, hhs, mdr = frames['hhq'], frames['hhs'], frames['mdr'] # Home Health Care
    ldf = long_term_care.download_data()

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

    # Save the new dataframes
    with open(home_folder_path + "assets/tag_hash.pkl", 'wb') as outp:
        pickle.dump(tags, outp, pickle.HIGHEST_PROTOCOL)
    with open(home_folder_path + "dataframes/df.pkl", 'wb') as outp:
        pickle.dump(hdf, outp, pickle.HIGHEST_PROTOCOL)
    with open(home_folder_path + "dataframes/hhc_df.pkl", 'wb') as outp:
        pickle.dump(hhq, outp, pickle.HIGHEST_PROTOCOL)
    with open(home_folder_path + "dataframes/hhc_state_by_state_df.pkl", 'wb') as outp:
        pickle.dump(hhs, outp, pickle.HIGHEST_PROTOCOL)
    with open(home_folder_path + "dataframes/hhc_date_range_df.pkl", 'wb') as outp:
        pickle.dump(mdr, outp, pickle.HIGHEST_PROTOCOL)
    with open(home_folder_path + "dataframes/ltch_df.pkl", 'wb') as outp:
        pickle.dump(ldf, outp, pickle.HIGHEST_PROTOCOL)
    
    
    # Save the date of this download
    today = datetime.now()
    today = str(today.month) + "/" + str(today.day) + "/" + str(today.year)
    with open(home_folder_path + "assets/lastupdate.pkl", 'wb') as outp:
        pickle.dump(today, outp, pickle.HIGHEST_PROTOCOL)

    # Update screen, show options page
    frame.show_options(True)
    

def make_nursing_home_sheets(frame: gui.ExcelPage, options, df, outpath):
    ''' Makes the excel sheets based on options chosen by the user. Saves them to a folder chosen by the user. '''

    # Update the screen
    frame.instructions.config(text="Making sheets...")
    frame.instructions2.grid_forget()
    frame.sheet_btn.grid_forget()
    start_time = time.time()

    # Load in tag data 
    with open(home_folder_path + "assets/tag_hash.pkl", 'rb') as inp:
        tag_hash = pickle.load(inp)

    # Setting defaults for missing user choices

    # Get years in range that user chose, or set a default range
    if None in {frame.controller.startdate, frame.controller.enddate}:

        # Conversion to date time objects for min and max
        oldcol = df['survey_date']
        df['survey_date'] =  pd.to_datetime(df['survey_date'], format='%Y-%m-%d')

        frame.controller.startdate = df['survey_date'].min()
        frame.controller.enddate = df['survey_date'].max()

        # Convert date column back to string 
        df['survey_date'] = oldcol
        print("Used Default Dates")

    # Check to see if territories were chosen and use default if not
    if len(frame.controller.territories) == 0:
        frame.controller.territories = info.territories
        print("Used Default Territories")
    # Convert states to their two letter code
    frame.controller.territories = convert_states(frame.controller.territories)
    print("Converted States to Two-Letter Codes")

    # Check to see if tags were chosen and if not use all
    if len(frame.controller.tags) == 0:
        frame.controller.tags = list(tag_hash.keys())
        print("Used Default Tags")
    else:
        df = df.loc[df['deficiency_tag_number'].isin(frame.controller.tags)] 
        print("Filtered Tags, length: {}".format(len(df)))

    # Get dates in range for state df
    df = get_inrange(df, frame.controller.startdate, frame.controller.enddate)
    print("Filtered Dates")

    # Optional sheets
    dfs = {}
    years = list(range(frame.controller.startdate.year, frame.controller.enddate.year+1))
    dfs["US"] = pd.DataFrame(columns=(["Total"] + years))
    dfs["Most Fined"] = pd.DataFrame()
    dfs["Most Severe"] = pd.DataFrame()
    dfs["State Fines"] = pd.DataFrame(columns=(["Total"] + years))
    dfs["State Violations"] = pd.DataFrame(columns=(["Total"] + years))
    dfs["Tag Fines"] = pd.DataFrame(columns=(["Total"] + years))
    dfs["Tag Violations"] = pd.DataFrame(columns=(["Total"] + years))
    dfs["All Territories"] = pd.DataFrame()
    dfs["All US States"] = pd.DataFrame()

    # Make a dataframe for each territory (saved in a hash) and then only keep violations in date range
    t_dfs = sort_by_territories(df, frame.controller.territories)
    for terr in t_dfs.keys():
        # Convert fine column to currency
        t_dfs[terr]['fine_amount'] = t_dfs[terr]['fine_amount'].apply(lambda x: 0 if x == "" else x)
        t_dfs[terr]['fine_amount'] = pd.to_numeric(t_dfs[terr]['fine_amount'], errors="coerce")
    
    # Convert fine column to numeric
    df['fine_amount'] = df['fine_amount'].apply(lambda x: 0 if x == "" else x)
    df['fine_amount'] = pd.to_numeric(df['fine_amount'], errors="coerce")
    print("Made Territory Dataframes")

    # Sort through options
    if options != None:
        for option in options.keys():

    
            if option == "US Fines" and options[option]:

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
                    dfs["US"].at["Fines", year] = get_inrange(df, yearstart, yearend)['fine_amount'].sum()

                # Change columns type back, add data to hash
                df['survey_date'] = oldcol
                dfs["US"].at["Fines", "Total"] = sum
                print("Made US Fines sheet for Nursing Homes")
                    
                        
            elif option == "US Violations" and options[option]:

                 # Initialize indicies
                dfs["US"].loc["Violations"] = [0] * (len(dfs["US"].columns))

                # Get total number of US violations within date range
                sum = count_violations_df(df)
            
                # Sum for each year
                for year in years:
                    # Make sure we are within the users date range  
                    yearstart, yearend = get_year_range(year, years, frame.controller.startdate, frame.controller.enddate)

                    # Get the year's sum
                    dfs["US"].at["Violations", year] = count_violations_df(get_inrange(df, yearstart, yearend)) 

                # Add data to hash of dfs
                dfs["US"].at["Violations", "Total"] = sum
                print("Made US Violations sheet for Nursing Homes")


            elif option == "Top fined organizations per state" and options[option]:

                # Dict[String, Dict[String, List]]
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
                        subdf = get_inrange(subdf, yearstart, yearend)
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
                print("Made Top fined organizations per state sheet for Nursing Homes")
            

            elif option == "Most severe organizations per state" and options[option]:

                # Dict[String, Dict[String, List]]
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
                        subdf = get_inrange(subdf, yearstart, yearend)
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
                print("Made Most severe organizations per state sheet for Nursing Homes")

            elif option == "Sum of fines per state per year" and options[option]:

                # Initialize indicies
                for state in info.states_codes:
                    # Get row for each state, add total for a state first
                    subdf = df.loc[df['provider_state'] == state]
                    row = [subdf['fine_amount'].sum()]
                    #'${:,.2f}'.format(
                    for year in years:
                        yearstart, yearend = get_year_range(year, years, frame.controller.startdate, frame.controller.enddate)
                        subdf2 = get_inrange(subdf, yearstart, yearend)
                        row += [subdf2['fine_amount'].sum()]
                        #'${:,.2f}'.format(
                    
                    dfs["State Fines"].loc[state] = row
                    print("Made sum of fines per state per year sheet for Nursing Homes")
                

            elif option == "Sum of violations per state per year" and options[option]:

                # Initialize indicies
                for state in info.states_codes:
                    # Get row for each state, add total for a state first
                    subdf = df.loc[df['provider_state'] == state]
                    row = [count_violations_df(subdf)]
                    for year in years:
                        yearstart, yearend = get_year_range(year, years, frame.controller.startdate, frame.controller.enddate)
                        subdf2 = get_inrange(subdf, yearstart, yearend)
                        row += [count_violations_df(subdf2)]
                    
                    dfs["State Violations"].loc[state] = row
                    print("Made sum of violations per state per year sheet for Nursing Homes")


            elif option == "Sum of fines per tag per year" and options[option]:

                # Initialize indicies
                for tag in sorted(frame.controller.tags):
                    # Get row for each state, add total for a state first
                    subdf = df.loc[df['deficiency_tag_number'] == tag]
                    row = [subdf['fine_amount'].sum()]
                    #'${:,.2f}'.format(
                    for year in years:
                        yearstart, yearend = get_year_range(year, years, frame.controller.startdate, frame.controller.enddate)
                        subdf2 = get_inrange(subdf, yearstart, yearend)
                        row += [subdf2['fine_amount'].sum()]
                        #'${:,.2f}'.format(
                    
                    dfs["Tag Fines"].loc[tag] = row
                    print("Made sum of fines per tag per year sheet for Nursing Homes")
                

            elif option == "Sum of violations per tag per year" and options[option]:

                # Initialize indicies
                for tag in sorted(frame.controller.tags):
                    # Get row for each state, add total for a state first
                    subdf = df.loc[df['deficiency_tag_number'] == tag]
                    row = [count_violations_df(subdf)]
                    for year in years:
                        yearstart, yearend = get_year_range(year, years, frame.controller.startdate, frame.controller.enddate)
                        subdf2 = get_inrange(subdf, yearstart, yearend)
                        row += [count_violations_df(subdf2)]
                    
                    dfs["Tag Violations"].loc[tag] = row
                    print("Made sum of violations per state per year sheet for Nursing Homes")
            

            elif option == "Create sheet with all territories combined" and options[option]:
                # Get a dict of dfs by territory
                tdfs = sort_by_territories(df, frame.controller.territories)
                combined = pd.DataFrame()
                for terr in tdfs.keys():
                    combined = pd.concat([combined, tdfs[terr]])
                dfs["All Territories"] = combined.reset_index()

                # Set indicies properly
                dfs["All Territories"] = dfs["All Territories"].drop(["index"], axis=1)
                dfs["All Territories"] = dfs["All Territories"].set_index(["territory", 'provider_state','provider_name', 'federal_provider_number', 
                'provider_city', 'provider_address', 'survey_date', 'survey_type'])

                # Set fine column as currency
                dfs["All Territories"]['fine_amount'] = dfs["All Territories"]['fine_amount'].apply(lambda x: 0 if x == "" else x)
                dfs["All Territories"]['fine_amount'] = pd.to_numeric(dfs["All Territories"]['fine_amount'], errors="coerce")
                dfs["All Territories"]['fine_amount'] =  dfs["All Territories"]['fine_amount'].apply(lambda x: float(x))
                print("Made all territories combined sheet for Nursing Homes")


            elif option == "All Violations" and options[option]:
                dfs["All US States"] = df.sort_values(by=["provider_state", "provider_name", "survey_date"])
                dfs["All US States"] = dfs["All US States"].set_index(['provider_state','provider_name', 'federal_provider_number', 
                'provider_city', 'provider_address', 'survey_date', 'survey_type'])

                # Set fine column as currency
                dfs["All US States"]['fine_amount'] = dfs["All US States"]['fine_amount'].apply(lambda x: 0 if x == "No Fine" else x)
                dfs["All US States"]['fine_amount'] = dfs["All US States"]['fine_amount'].apply(lambda x: float(x))
                print("Made all violations sheet for Nursing Homes")


    # --- Write to excel --- #

    # Excel workbook for each territory
    for terr in t_dfs.keys():
        # Makes the sheets more organized
        if not t_dfs[terr].empty:
            # Sort alphabetically by provider name
            t_dfs[terr] = t_dfs[terr].sort_values(by=["provider_state", "provider_name", "survey_date"])
            # This will group things together in the excel sheets
            t_dfs[terr] = t_dfs[terr].set_index(["territory", 'provider_state','provider_name', 'federal_provider_number', 
       'provider_city', 'provider_address', 'survey_date', 'survey_type'])


        t_dfs[terr].to_excel(outpath + "/" + terr + ".xlsx", sheet_name=terr+"_NursingHomes")
        print(f"Made {terr}_NursingHomes.xlsx")

    start_row = 1
    with pd.ExcelWriter(outpath + '/OptionalData_NursingHomes.xlsx') as writer:

        # Excel sheet for each set of options
        for dfname in dfs.keys():
            if not dfs[dfname].empty:
                dfs[dfname].to_excel(writer, sheet_name=dfname)
                start_row += len(dfs[dfname])
                print(f"Made {dfname} Excel Workbook")

        # Makes Excel Sheet in OptionalData_NursingHomes.xlsx that has descriptions of different metrcs
        make_nursing_homes_optional_workbook(tag_hash, writer)

        writer.save()
        frame.instructions.config(text="Sheets made in " + str(int(time.time() - start_time)) + " seconds")
        print("Sheets made in " + str(int(time.time() - start_time)) + " seconds")
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


def sort_by_territories(state_df, territories):
    ''' Sort violations by territories for when we make an excel sheet. Also want to update
        territory values as we go through the dataframe. '''
    tdict = {}
    territorynames = list(territories.keys())

    # Create a hash where key is territory name and value is dataframe of related rows
    for name in territorynames:
        # Get subframe, add territory column and reset indicies
        tdict[name] = state_df[state_df['provider_state'].isin(territories[name])]
        tdict[name].insert(0,"territory", 0)
        tdict[name] = tdict[name].reset_index(drop=True)

        # Set territory column
        tdict[name] = tdict[name].replace({"territory": 0}, name)

    return tdict


def get_inrange(df, start, end):
    ''' Gets a subframe where only violations with dates in a certain range are included. '''
    # Conversion to date time objects for comparison
    oldcol = df['survey_date']
    df['survey_date'] =  pd.to_datetime(df['survey_date'], format='%Y-%m-%d')
    new = df.loc[(df['survey_date'] >= start) & (df['survey_date'] <= end)]

    # Then revert columns back to strings
    new['survey_date'] = new['survey_date'].dt.strftime('%Y-%m-%d')
    df['survey_date'] = oldcol

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
            #'${:,.2f}'.format(
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

def make_nursing_homes_optional_workbook(tag_hash, writer):
    ''' Creates the optional data's Description sheet for nursing homes. '''
    items1 = list(tag_hash.items())
    items2 = list(info.severities.items())
    df1 = pd.DataFrame(items1, columns=["Tag", "Description"])
    df1 = df1.sort_values(by="Tag")
    df1 = df1.reset_index().drop("index", axis=1)
    df2 = pd.DataFrame(items2, columns=["Rank", "Description"])        
    df1.to_excel(writer, sheet_name="Descriptions", startrow=1, startcol=0)
    df2.to_excel(writer, sheet_name="Descriptions", startrow=len(df1.index)+5, startcol=0)