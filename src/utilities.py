'''
This file downloads data from https://data.cms.gov/provider-data.
It downloads raw data in the form of multiple CSV files from mutliple
pages, and turns them into pandas dataframes. Specifically, it grabs
the latest Penalties and Health Deficiencies CSV's. It also contains
various utility functions for back-end processes of gui.py.

'''
from tkinter import Label
from tkinter.ttk import Progressbar
from typing import Dict, List
import pickle, sys, os, time, random, info
import pandas as pd
from datetime import datetime

# This is where all the save data lies
abs_home = os.path.abspath(os.path.expanduser("~"))
home_folder_path = abs_home + "/ViolationToolv2/"

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Download csvs if user says yes
def download(frame):

    # Url for Penalties and Health Deficiencies dataset queries
    p_urls = "https://data.cms.gov/provider-data/api/1/datastore/query/g6vv-u9sr/0/download?format=csv"
    hd_urls = "https://data.cms.gov/provider-data/api/1/datastore/query/r5ix-sfxw/0/download?format=csv"

    # Make the dataframes and save them
    pdf = pd.read_csv(p_urls, encoding="iso_8859-1")
    hdf = pd.read_csv(hd_urls, encoding="iso_8859-1")

    # Combine the dataframes
    hdf['fine_amount'] = ""
    hdf.update(pdf)
    hdf = hdf[['federal_provider_number', 'provider_name', 'provider_state',
       'provider_city', 'provider_address', 'survey_date', 'survey_type', 'deficiency_prefix', 'deficiency_category',
       'deficiency_tag_number', 'deficiency_description', 'scope_severity_code', 'deficiency_corrected', 
       'correction_date','fine_amount']]

    # Get tags and their descriptions and save it into a dictionary
    tags = hdf[['deficiency_tag_number', 'deficiency_description']].drop_duplicates()
    tags = dict(zip(tags['deficiency_tag_number'], tags['deficiency_description']))
    with open(home_folder_path + "assets/tag_hash.pkl", 'wb') as outp:
        pickle.dump(tags, outp, pickle.HIGHEST_PROTOCOL)

    with open(home_folder_path + "dataframes/df.pkl", 'wb') as outp:
        pickle.dump(hdf, outp, pickle.HIGHEST_PROTOCOL)

    # Save the date of this download
    today = datetime.now()
    today = str(today.month) + "/" + str(today.day) + "/" + str(today.year)
    with open(home_folder_path + "assets/lastupdate.pkl", 'wb') as outp:
        pickle.dump(today, outp, pickle.HIGHEST_PROTOCOL)

    # Update screen
    frame.show_options(True)
    

# Makes the excel sheets based on options chosen by the user 
def make_sheets(frame, options, df, startdate, enddate, territories, tags, outpath):

    # Update the screen
    frame.instructions.config(text="Making sheets...")
    frame.instructions2.grid_forget()
    frame.sheet_btn.grid_forget()
    start_time = time.time()

    # Load in tag data 
    with open(resource_path("assets/tag_hash.pkl"), 'rb') as inp:
        tag_hash = pickle.load(inp)

    # Setting defaults for missing user choices

    # Get years in range that user chose, or set a default range
    if None in {startdate, enddate}:

        # Conversion to date time objects for min and max
        oldcol = state_df['Date']
        state_df['Date'] =  pd.to_datetime(state_df['Date'], format='%m/%d/%Y')

        startdate = state_df['Date'].min()
        enddate = state_df['Date'].max()

        # Convert date column back to string 
        state_df['Date'] = oldcol
        print("Used Default Dates")

    # Check to see if territories were chosen and use default if not
    if len(territories) == 0:
        territories = info.territories
        print("Used Default Territories")
    # Convert states to their two letter code
    territories = convert_states(territories)
    print("Converted States to Two-Letter Codes")

    # Check to see if tags were chosen and if not use all
    if len(tags) == 0:
        tags = list(tag_hash.keys())
        print("Used Default Tags")
    else:
        state_df = state_df.loc[state_df["Tag"].isin(tags)] 
        print("Filtered Tags")

    # Get dates in range for state df
    state_df = get_inrange(state_df, startdate, enddate)
    print("Filtered Dates")

    # Merge rows where state, date, and organization are the same
    hdf = hdf.set_index(['federal_provider_number', 'provider_name', 'provider_state',
       'provider_city', 'provider_address', 'survey_date', 'survey_type'])

    # Optional sheets
    dfs = {}
    years = list(range(startdate.year, enddate.year+1))
    dfs["US"] = pd.DataFrame(columns=(["Total"] + years))
    dfs["Most Fined"] = pd.DataFrame()
    dfs["Most Severe"] = pd.DataFrame()
    dfs["State Fines"] = pd.DataFrame(columns=(["Total"] + years))
    dfs["State Violations"] = pd.DataFrame(columns=(["Total"] + years))
    dfs["All Territories"] = pd.DataFrame()
    dfs["All"] = pd.DataFrame()

    # Make a dataframe for each territory (saved in a hash) and then only keep violations in date range
    t_dfs = sort_by_territories(state_df, territories)
    for terr in t_dfs.keys():
        # Convert fine column to currency
        t_dfs[terr]["Fine"] = t_dfs[terr]["Fine"].apply(lambda x: 0 if x == "No Fine" else x)
        t_dfs[terr]["Fine"] = pd.to_numeric(t_dfs[terr]["Fine"], errors="coerce")
        t_dfs[terr]["Fine"] =  t_dfs[terr]["Fine"].apply(lambda x: '${:,.2f}'.format(float(x)))

    
    # Convert fine column to numeric
    state_df["Fine"] = state_df["Fine"].apply(lambda x: 0 if x == "No Fine" else x)
    state_df["Fine"] = pd.to_numeric(state_df["Fine"], errors="coerce")

    # Sort through options
    if options != None:
        for option in options.keys():

    
            if option == "US Fines" and options[option]:

                # Initialize indicies
                dfs["US"].loc["Fines"] = [0] * (len(dfs["US"].columns))
                
                # Conversion to date time objects for comparison
                oldcol = state_df["Date"]
                state_df['Date'] =  pd.to_datetime(state_df['Date'], format='%m/%d/%Y')

                # Total sum -> after the df has been filtered on tags and date 
                sum = state_df["Fine"].sum()
            
                # Sum for each year
                for year in years:
                    # Make sure we are within the users date range  
                    yearstart, yearend = get_year_range(year, years, startdate, enddate)

                    # Get the year's sum and format it as currency
                    dfs["US"].at["Fines", year] = '${:,.2f}'.format(get_inrange(state_df, yearstart, yearend)["Fine"].sum())

                # Change columns type back, add data to hash
                state_df['Date'] = oldcol
                dfs["US"].at["Fines", "Total"] = '${:,.2f}'.format(sum)
                    
                        
            elif option == "US Violations" and options[option]:

                 # Initialize indicies
                dfs["US"].loc["Violations"] = [0] * (len(dfs["US"].columns))

                # Get total number of US violations within date range
                sum = count_violations_df(state_df)
            
                # Sum for each year
                for year in years:
                    # Make sure we are within the users date range  
                    yearstart, yearend = get_year_range(year, years, startdate, enddate)

                    # Get the year's sum
                    dfs["US"].at["Violations", year] = count_violations_df(get_inrange(state_df, yearstart, yearend)) 

                # Add data to hash of dfs
                dfs["US"].at["Violations", "Total"] = sum


            elif option == "Top fined organizations per state" and options[option]:

                # Dict[String, Dict[String, List]]
                state_orgs = {}
                num = 3
                # For each state get the most fined overall
                state_orgs["Overall"] = {}
                for state in info.states_codes:
                    # Get subdf of a given state
                    subdf = state_df.loc[state_df["State"] == state]
                    # Get a list of the most fined organizations across entire period
                    state_orgs["Overall"][state] = get_most_fined(subdf, num)
                    
                # Go through each year in range
                for year in years:
                    state_orgs[year] = {}
                    # Make sure we are within the users date range  
                    yearstart, yearend = get_year_range(year, years, startdate, enddate)

                    # Get top fined for each year
                    for state in info.states_codes:
                        # Get subdf of a given state
                        subdf = state_df.loc[state_df["State"] == state]
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
            

            elif option == "Most severe organizations per state" and options[option]:

                # Dict[String, Dict[String, List]]
                state_orgs = {}
                num = 3
                # For each state get the most severe overall
                state_orgs["Overall"] = {}
                for state in info.states_codes:
                    # Get subdf of a given state
                    subdf = state_df.loc[state_df["State"] == state]
                    # Get a list of the most severe organizations across entire period
                    state_orgs["Overall"][state] = get_most_severe(subdf, num)
                    
                # Go through each year in range
                for year in years:
                    state_orgs[year] = {}
                    # Make sure we are within the users date range  
                    yearstart, yearend = get_year_range(year, years, startdate, enddate)

                    # Get most severe for each year
                    for state in info.states_codes:
                        # Get subdf of a given state
                        subdf = state_df.loc[state_df["State"] == state]
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


            elif option == "Sum of fines per state per year" and options[option]:

                # Initialize indicies
                for state in info.states_codes:
                    # Get row for each state, add total for a state first
                    subdf = state_df.loc[state_df["State"] == state]
                    row = ['${:,.2f}'.format(subdf["Fine"].sum())]
                    for year in years:
                        yearstart, yearend = get_year_range(year, years, startdate, enddate)
                        df = get_inrange(subdf, yearstart, yearend)
                        row += ['${:,.2f}'.format(df["Fine"].sum())]
                    
                    dfs["State Fines"].loc[state] = row
                

            elif option == "Sum of violations per state per year" and options[option]:

                # Initialize indicies
                for state in info.states_codes:
                    # Get row for each state, add total for a state first
                    subdf = state_df.loc[state_df["State"] == state]
                    row = [count_violations_df(subdf)]
                    for year in years:
                        yearstart, yearend = get_year_range(year, years, startdate, enddate)
                        df = get_inrange(subdf, yearstart, yearend)
                        row += [count_violations_df(df)]
                    
                    dfs["State Violations"].loc[state] = row


            elif option == "Create sheet with all territories combined" and options[option]:
                # Get a dict of dfs by territory
                tdfs = sort_by_territories(state_df, territories)
                combined = pd.DataFrame()
                for terr in tdfs.keys():
                    combined = pd.concat([combined, tdfs[terr]])
                dfs["All Territories"] = combined.reset_index()

                # Set indicies properly
                dfs["All Territories"] = dfs["All Territories"].drop(["index"], axis=1)
                dfs["All Territories"] = dfs["All Territories"].set_index(["Territory", "State", "Organization", "Date"])

                # Set fine column as currency
                dfs["All Territories"]["Fine"] = dfs["All Territories"]["Fine"].apply(lambda x: 0 if x == "No Fine" else x)
                dfs["All Territories"]["Fine"] = pd.to_numeric(dfs["All Territories"]["Fine"], errors="coerce")
                dfs["All Territories"]["Fine"] =  dfs["All Territories"]["Fine"].apply(lambda x: '${:,.2f}'.format(float(x)))


            elif option == "All Violations" and options[option]:
                dfs["All"] = state_df.set_index(["State", "Organization", "Date"])

                # Set fine column as currency
                dfs["All"]["Fine"] = dfs["All"]["Fine"].apply(lambda x: 0 if x == "No Fine" else x)
                dfs["All"]["Fine"] =   dfs["All"]["Fine"].apply(lambda x: '${:,.2f}'.format(float(x)))


    # --- Write to an excel --- #

    # Excel workbook for each territory
    for terr in t_dfs.keys():
        # Makes the sheets more organized
        if not t_dfs[terr].empty:
            t_dfs[terr] = t_dfs[terr].set_index(["Territory", "State", "Organization", "Date"])

        t_dfs[terr].to_excel(outpath + "/" + terr + ".xlsx", sheet_name=terr)

    start_row = 1
    with pd.ExcelWriter(outpath + '/OptionalData.xlsx') as writer:

        # Excel sheet for each set of options
        for dfname in dfs.keys():
            if not dfs[dfname].empty:
                dfs[dfname].to_excel(writer, sheet_name=dfname)
                start_row += len(dfs[dfname])
                print(dfname)

        # Excel sheet for description of tags and severities
        items1 = list(tag_hash.items())
        items2 = list(info.severities.items())
        df1 = pd.DataFrame(items1, columns=["Tag", "Description"])
        df2 = pd.DataFrame(items2, columns=["Rank", "Description"])        
        df1.to_excel(writer, sheet_name="Descriptions", startrow=1, startcol=0)
        df2.to_excel(writer, sheet_name="Descriptions", startrow=len(df1.index)+5, startcol=0)

        writer.save()
        
        frame.instructions.config(text="Sheets made in " + str(int(time.time() - start_time)) + " seconds")
        time.sleep(3)
        frame.finish()

# Match up incidents with corresponding fines
def match_violations(state_df, fine_df):

    # Combine rows where state, org and date are the same but make a list of the tags and severities in order
    state_df = state_df.groupby(['State', 'Organization', 'Date']).agg({'Tag':lambda x: ','.join(x.astype(str)),\
        'Severity':lambda x: ','.join(x.astype(str)), 'Fine':'first', 'Url':'first'})
    
    # Format the fine_df, get rid of dupes, use it to update the state_df
    fine_df = fine_df.set_index(['State', 'Organization', 'Date'])
    fine_df = fine_df[~fine_df.index.duplicated()]
    state_df.update(fine_df)
    
    return state_df
    
    
# Converts states from full name into their two letter code Dict[String, List[String]]) -> Dict[String, List[String]]
def convert_states(territories):
    
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

# Sort violations by territories for when we make an excel sheet
# Also want to update territory values as we go through the dataframe
def sort_by_territories(state_df, territories):
    tdict = {}
    territorynames = list(territories.keys())

    # Create a hash where key is territory name and value is dataframe of related rows
    for name in territorynames:
        # Get subframe, add territory column and reset indicies
        tdict[name] = state_df[state_df["State"].isin(territories[name])]
        tdict[name].insert(0,"Territory", 0)
        tdict[name] = tdict[name].reset_index(drop=True)

        # Set territory column
        tdict[name] = tdict[name].replace({"Territory": 0}, name)

    return tdict

# Gets a subframe where only violations with dates in a certain range are included
def get_inrange(df, start, end):
    # Conversion to date time objects for comparison
    oldcol = df["Date"]
    df["Date"] =  pd.to_datetime(df["Date"], format='%m/%d/%Y')
    new = df.loc[(df["Date"] >= start) & (df["Date"] <= end)]

    # Then revert columns back to strings
    new["Date"] = new["Date"].dt.strftime('%m/%d/%Y')
    df["Date"] = oldcol

    return new 

# Counts the number of violations in a dataframe by checking number of tags
def count_violations_df(df):
    # Turn the tag column into a pandas series of lists
    vios = 0
    col = df["Tag"].apply(lambda x: x.strip('][').replace("'", "").split(",")) 
    for lst in col:
        vios += len(lst)

    return vios

# Returns a sorted list of tuples where each tuple contains an organization and total fines for a period    
def get_most_fined(df, num):
    sums = []
    # Get the facility names
    facilities = df["Organization"].unique()
    for name in facilities:
        # Convert fine column to a number so we can sum
        sum = df.loc[df["Organization"] == name, "Fine"].sum()
        if sum != 0:
            sums.append((name, sum))

    # Sort the list of tuples by fine
    sums = sorted(sums, key=lambda item: item[1], reverse=True)

    # Add place holders if not enough data
    if len(sums) < num:
        sums += [("NA", "$0")] * (num - len(sums))
    
    # Format the sums to currenices
    for i, sum in enumerate(sums):
        if sum[0] != "NA":
            temp = list(sum)
            temp[1] = '${:,.2f}'.format(temp[1])
            sums[i] = tuple(temp)

    return sums[:num]

# Returns a sorted list of tuples where each tuple contains an organization and total violations for a period    
def get_most_severe(df, num):
    sums = []
    # Get the facility names
    facilities = df["Organization"].unique()
    for name in facilities:
        curdf = df.loc[df["Organization"] == name]
        # Convert the severity column to numeric and sum it
        def convert(x):
            sum = 0
            lst = x.strip('][').replace("'", "").split(",") 
            for severity in lst:
                sum += info.severity_ranks[severity]

            return sum

        sum = curdf["Severity"].apply(lambda x: convert(x)).sum()
        if sum != 0:
            sums.append((name, sum))

    # Sort the list of tuples by violations
    sums = sorted(sums, key=lambda item: item[1], reverse=True)
    # Add place holders if not enough data
    if len(sums) < num:
        sums += [("NA", 0)] * (num - len(sums))

    return sums[:num]

# Get proper bounds for a date range
def get_year_range(year, years, startdate, enddate):
    if year == years[0]:
        yearstart = startdate
        yearend = datetime.strptime("12/31/"+str(year), "%m/%d/%Y")
    elif year == years[-1]:
        yearstart = datetime.strptime("01/01/"+str(year), "%m/%d/%Y")
        yearend = enddate
    else:
        yearstart = datetime.strptime("01/01/"+str(year), "%m/%d/%Y")
        yearend = datetime.strptime("12/31/"+str(year), "%m/%d/%Y")

    return (yearstart, yearend)


# Get violations that include chosen tags
def get_tag_range(df, tags):
    newdf = df
    newdf["Tag"] = df["Tag"].apply(lambda x: x.strip('][').replace("'", "").split(","))
    newdf["Severity"] = df["Severity"].apply(lambda x: x.strip('][').replace("'", "").split(","))
    newdf = newdf.reset_index()

    for i, row in newdf.iterrows():
        # Map each tag to its severity so that we know which severities to keep
        pairs = list(map(lambda x,y: (x,y), row["Tag"], row["Severity"]))
        
        # If there are no tags in a row that are ones chosen by the user, drop the row
        matches = [pair for pair in pairs if pair[0] in tags]
        if len(matches) == 0:
            newdf = newdf.drop(index=i)
        else:
            # Update the dataframe to only keep the correct tags and matches
            newdf.at[i, "Tag"] = str([pair[0] for pair in matches])
            newdf.at[i, "Severity"] = str([pair[1] for pair in matches])

    return newdf



