'''
This file contains various dictionaries and lists that contain
information relative to the data being processed by the Violation Tool.
'''
import pickle, utilities as util

PRODUCTION = True
if PRODUCTION:
    STATE_CODES_PATH = "assets/state_codes_table.pkl"
else:
    STATE_CODES_PATH = "../assets/state_codes_table.pkl"

severities = {
    "A - 0" : "Isolated - No actual harm with potential for minimal harm",
    "B - 0" : "Pattern - No actual harm with potential for minimal harm",
    "C - 0" : "Widespread - No actual harm with potential for minimal harm",
    "D - 4" : "Isolated - No actual harm with potential for more than minimal harm that is not immediate jeopardy",
    "E - 8" : "Pattern - No actual harm with potential for more than minimal harm that is not immediate jeopardy",
    "F - 16" : "Widespread - No actual harm with potential for more than minimal harm that is not immediate jeopardy",
    "G - 20" : "Isolated - Actual harm that is not immediate",
    "H - 35" : "Pattern - Actual harm that is not immediate",
    "I - 45" : "Widespread - Actual harm that is not immediate",
    "J - 50" : "Isolated - Immediate jeopardy to resident health or safety",
    "K - 100" : "Pattern - Immediate jeopardy to resident health or safety",
    "L - 150" : "Widespread - Immediate jeopardy to resident health or safety"
}

severity_ranks = {
    "A" : 0,
    "B" : 0,
    "C" : 0,
    "D" : 4,
    "E" : 8,
    "F" : 16,
    "G" : 20,
    "H" : 35,
    "I" : 45,
    "J" : 50,
    "K" : 100,
    "L" : 150
}

territories = {
    "West" : ["California", "Oregon", "Washington", "Nevada", "Idaho", "Utah", "Arizona", "Montana", "Alaska", "Hawaii"],

    "Central" : ["Wyoming", "Colorado", "New Mexico", "North Dakota", "South Dakota", "Nebraska", "Kansas", "Oklahoma",
                "Texas", "Minnesota", "Iowa", "Missouri", "Arkansas", "Louisiana", "Wisconsin", "Illinois", "Mississippi"],

    "East" : ["Michigan", "Indiana", "Kentucky", "Tennessee", "Alabama", "Ohio", "Georgia", "Florida", "South Carolina", "North Carolina",
             "Virginia", "West Virginia", "Delaware", "Maryland", "New Jersey", "Pennsylvania", "New York", "Connecticut", "Rhode Island",
             "Massachusetts", "Vermont", "New Hampshire", "Maine", "District of Columbia", "Guam"]
}

all_states = ["California", "Oregon", "Washington", "Nevada", "Idaho", "Utah", "Arizona", "Montana", "Alaska", "Hawaii", "Wyoming",
                "Colorado", "New Mexico", "North Dakota", "South Dakota", "Nebraska", "Kansas", "Oklahoma", "Texas", "Minnesota", "Iowa",
                "Missouri", "Arkansas", "Louisiana", "Wisconsin", "Illinois", "Mississippi", "Michigan", "Indiana", "Kentucky", "Tennessee", 
                "Alabama", "Ohio", "Georgia", "Florida", "South Carolina", "North Carolina", "Virginia", "West Virginia", "Delaware", "Maryland",
                "New Jersey", "Pennsylvania", "New York", "Connecticut", "Rhode Island", "Massachusetts", "Vermont", "New Hampshire", "Maine", "District of Columbia",
                "Guam"]
all_states = sorted(all_states)

states_codes = [ 'AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'GA',
           'GU', 'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD', 'ME',
           'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM',
           'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX',
           'UT', 'VA', 'VT', 'WA', 'WI', 'WV', 'WY']

# Creates hash map where key is two letter state code and value is full state
def get_state_codes() -> dict:
    state_codes = {}
    with open(util.resource_path("assets/state_codes_table.pkl"), 'rb') as inp:
        table = pickle.load(inp)
        
    rows = table.values.tolist()
    for row in rows:
        state_codes[row[1]] = row[0]
        state_codes[row[3]] = row[2]
        state_codes[row[5]] = row[4]
    
    return state_codes

     


