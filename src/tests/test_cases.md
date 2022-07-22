Test Cases - Doing with everything integrated:

Nursing Homes: 
    ~~Filter Dates - 01/10/2019-10/10/2022~~
        Result: Filtered as expected
        Time: Nursing Home Sheets made in 4 seconds.
    ~~Select all dates~~
        Result: Filtered as expected
        Time: Nursing Home Sheets made in 6 seconds.
    ~~Filter Dates with optional sheets - 01/10/2019-10/10/2022~~
        Result: Filtered as expected
        Time: Nursing Home Sheets made in 108 seconds.
    ~~Filter territories - T1: MD, PA, T2: Michigan, DE~~
        Result: Filtered as expected
        Time: Nursing Home Sheets made in 3 seconds.
    ~~Filter territories with optional sheets - T1: MD, PA, T2: Michigan, DE~~
        Result: Filtered as expected
        Time: Nursing Home Sheets made in 188 seconds.
    ~~Filter tags - 757~~
        Result: Filtered as expected
        Time: Nursing Home Sheets made in 0 seconds.
    ~~Select all tags~~
        Result: Filtered as expected
        Time: Nursing Home Sheets made in 6 seconds.

Home Health Care: 
    ~~Filter Star Range - invalid numbers AND 2 to 4 AND 1 to 5~~
        Result: Filtered as expected
        Time: Home Health Sheets made in 0 seconds.
    ~~Include all optional sheets without exclusions~~
        Result: Filtered as expected
        Time: Home Health Sheets made in 0 seconds.
    ~~Include all exclusions~~
        Result: Filtered as expected
        Time: Home Health Sheets made in 0 seconds.
    ~~Include all exclusions except undefined~~
        Result: Filtered as expected
        Time: Home Health Sheets made in 0 seconds.
    ~~Exclude Undefined~~
        Result: Filtered as expected
        Time: Home Health Sheets made in 0 seconds.

Long Term Care Hospital: 
    ~~Filter Bed Range: Invalid numbers AND 1 to 10 AND 5 to 30~~
        Result: Filtered as expected
        Time: Long Term Care Sheets made in 0 seconds.
    ~~Include all optional sheets without exclusions~~
        Result: Filtered as expected
        Time: Long Term Care Sheets made in 0 seconds.
    ~~Include all exclusions~~
        Result: Filtered as expected
        Time: Long Term Care Sheets made in 0 seconds.
    ~~Include all exclusions except undefined~~
        Result: Filtered as expected
        Time: Long Term Care Sheets made in 0 seconds.
    ~~Include all exclusions except mobile~~
        Result: Filtered as expected
        Time: Long Term Care Sheets made in 0 seconds.
    ~~Exclude Undefined~~
        Result: Filtered as expected
        Time: Long Term Care Sheets made in 0 seconds.

All: Passed!
    Chosen Territories: {'T1': ['Maryland', 'Pennsylvania', 'Delaware', 'New Jersey'], 'T2': ['Montana', 'Washington', 'Guam', 'Hawaii'], 'T3': ['Florida', 'California', 'Arizona', 'Arkansas']}

    User input: ['757', '756', '800', '750']

    Chosen Date Range: 01/10/2018-11/11/2021

    Chosen Nursing Home Options: {'US Fines (Total, yearly)': True, 'US Violations (Total, yearly)': True, 'Top fined organizations (Total, yearly)': True, 'Most severe organizations (Total, yearly)': True, 'Sum of fines per state (Total, yearly)': True, 'Sum of violations per state (Total, yearly)': True, 'Sum of fines per tag (Total, yearly)': True, 'Sum of violations per tag (Total, yearly)': True, 'Create sheet with all territories combined': True, 'Create sheet for all violations without territories': True}

    Chosen Star Range: 1.0-3.0

    Chosen Home Health Options: {'State Statistics': True, 'Measure Averages per Organization': True, 'Sheet With All Territories Combined': True, 'Sheet For All Violations in the Dataset Without Territories': True, 'VOLUNTARY NON PROFIT - RELIGIOUS AFFILIATION': True, 'VOLUNTARY NON-PROFIT - OTHER': True, 'PROPRIETARY': True, 'GOVERNMENT - STATE/COUNTY': False, 'VOLUNTARY NON-PROFIT - PRIVATE': False, 'GOVERNMENT - COMBINATION GOVT & VOLUNTARY': False, 'GOVERNMENT - LOCAL': False, 'Undefined': False}

    Chosen Bed Range: 10-30

    Chosen Long Term Options: {'Sheet With All Territories Combined': True, 'Sheet For All Violations in the Dataset Without Territories': True, 'Non-profit': False, 'Government': False, 'For profit': True, 'Tribal': True, 'Physician': True, 'Undefined': False}


