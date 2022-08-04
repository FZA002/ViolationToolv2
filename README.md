# **Violation Tool v2**
Welcome! The purpose of this tool is to allow a user to easily view and filter datasets related to Healthcare. This version includes data on Nursing Home, Home Health Care, and Long Term Care Hospital organizations. The data is pulled from [cms.gov](https://data.cms.gov/provider-data/?redirect=true), which is refreshed monthly. After a  user chooses filters for the datasets, the final products are organized CSV files. As of now, the program is built on a Mac, which is reflected in the code's design.

## How to run the program (As a user with an executable file)
Please follow these steps, as Apple makes it hard to run a random program downloaded from the Internet (as they should). These steps will give the program permission to run.
&nbsp;  
&nbsp;  

1. Download the file
2. Drag it onto your desktop
3. Open up your terminal (you can do this via command + space and then searching "Terminal")
4. In the terminal, type "cd ~/Desktop"
5. In the terminal, type "chmod +x ./ViolationTool". You can now close the terminal.
6. Now go to your desktop and click on the program. You should now get a pop up from Apple acting as the Warden between you and malicious actors. Just press "OK".
7. Click on the apple logo at the top left of your screen. Then System Preferences -> Security & Privacy -> General. You should see a message about how ViolationTool was blocked. Allow it to open. You can trust me :)
8. Be patient and the program will be at your service. A terminal will pop up and produce text on occasion. If the program doesn't work as expected, or at all, and text pops up in the terminal window, please copy it and send me it. You should be able to just click the program to run it from now on.
&nbsp;  
&nbsp;

The program will create a folder in your User folder where it will store all necessary data that it downloads and updates. The first time the program is run on your machine (or if the auto-created folder is moved or deleted), it will automatically download the lastest data. The very first screen of the program will tell you if this data is up to date. If the program is up to date, there is no need to click yes on the first screen.

&nbsp;  
&nbsp;  
&nbsp;  

# **Breakdowns of Options and Filters, by Dataset** 

## All Datasets
---

## Filter by Territories
A user is able to dynamically input territories of whatever name they choose. A territory is simply a group of states that the user gets to set. As mentioned above, a user will get one CSV per territory that they create. If a user skips this option, the default territories are East, West, and Central. The 52 states are divided amongst these.

## Filter by Date Range
A user is able to specify a range of dates for which they want to see data for. This date range is inclusive, meaning the start and end dates will be included. An important note on this date range: it will apply to other options. For example, one other option for Nursing Homes is to include data on the fines for the entire US. The total shown will only include data in a user's date range! This includes individual years. For example, consider if a user sets their date range as 01/10/2019-01/01/2021. The total produced for the US will include 01/10/2019-12/31/2019 (inclusive), all of 2020, and 01/01/2021. The total shown for 2019 and 2021 individually would abides by the same metrics. This date range only applies to Nursing Home and Long Term Care Hopsital data as of now. For Nursing Home data, the tool will use the "survey_date" column to filter dates. For Long Term Care Hospital data, it will use the "start_date" and "end_date" columns. If both the start_date and end_date are within the inclusive range provided by the user, the row of data will be included.


&nbsp;  
&nbsp;  
&nbsp;  

## Nursing Homes
---
The Nursing Homes dataset includes data on violations that Nursing Home organizations across the US have made. These violations each have an associated violation tag, date of the violation, fine amount, and other qualities associated with them.

## Filter by Tags
Each violation has a violation corresponding tag. A tag is simply a way of categorizing a violation based on its nature. For example, tag F757's description is "Drug Regimen is Free From Unnecessary Drugs". A CSV with tag numbers and descriptions is included with the CSV's made by the tool. Additionally, anything that you input that isn't a valid tag will not be used and will be displayed on the screen once you finish entering tags. This filter will be used on the entire Nursing Home dataset, meaning that similar to the above described date range, any other Nursing Home options will be affected by this filter!

### Options
1. **US Fines:**
    This will include a total for each year in a given date range, as well as a total for that range. As described above in the "Filter by Date Range" section, the total shown and individual years will only include dates and violation tags in the given range!

2. **US Violations:**
    This will include a total for each year in a given date range, as well as a total for that range. The same rules apply for dates and violation tags in range as described throughout this document.

3. **Top Fined Organizations:**
    This will include a sheet that will include the top 3 most fined organizations per state, per year, and overall. The same rules apply for dates and tags in range as described throughout this document.

4. **Most Severe Organizations:**
    This will include a sheet that will include the top 3 most severe organizations per state, per year, and overall. The same rules apply for dates and tags in range as described throughout this document. An organization's severity is ranked via severity scores associated with each violation. The scores are calculated as described at the end of the document.

5. **Sum of Fines and Violations per State:**
    These will include sheets that will include the total number of violations and fines for each state, for each year in range, and a total for the date range. The same rules apply for dates and tags in range as described throughout this document.

6. **Create Sheet with All Territories Combined**
    This will include a sheet of all of the territories chosen by the user (or the defaults) combined. The same rules apply for dates and tags in range as described throughout this document.

7. **Create Sheet for All Violations without Territories**
    This will create a sheet of all states, filtered by the given date range and tags. The states will not be grouped by territories.

&nbsp; 

## How Severity is Calculated for States and Organizations
The scores included in some of the optional sheets are based off of CMS's "Design for Care Compare Nursing Home Five-Star Quality Rating System: Technical Users’ Guide", available [here](https://www.cms.gov/Medicare/Provider-Enrollment-and-Certification/CertificationandComplianc/downloads/usersguide.pdf), and included in this repo in the "documents" folder. The specific numeric value associated with each scope severity code is included in one of the CSV files that are made each time any other sheets are made.

&nbsp;  
&nbsp;  
&nbsp;  

## Home Health Care
---
The Home Healthcare dataset includes different measures of quality for Home Healthcare organizations across the US. The different quality measures have associated date ranges for when these measures are relevant to, and are included in a CSV made by the tool each time it is ran.

&nbsp; 

## Filter by Star Range
Each Home Health care organization has an associated "quality_of_patient_care_star_rating". Filtering by star range allows a user to include only organizations within their chosen star range, which can be any decimal between 0 and 5. Similar to date and tag filters for the Nursing Home dataset, the star range filtered dataset will be used for the rest of the options!

## Exclude ownership types
Each Home Healthcare organization has an associated "type_of_ownership". On the "Format CSV Data" screen for Home Health, the user can choose to exclude organizations with certain types of ownership. "Undefined" organizations are organizations that have a blank value for "type_of_ownership" in the dataset. Similar to star range, the organization type filtered dataset will be used for the rest of the options!

### Options
1. **Include State Statistics:**
    This will include many of the same quality measures used for Home Healthcare organizations, but for each US state. The same rules apply for stars and ownership types that have been filtered as described throughout this document.

2. **Include Measure Averages per Organization:**
    This will include an average for each Home Healthcare organization's different quality measures, grouping together organzations with the same name, regardless of their location. The same rules apply for stars and ownership types that have been filtered as described throughout this document.

3. **Create Sheet with All Territories Combined**
    This will include a sheet of all of the territories chosen by the user (or the defaults) combined. The same rules apply for stars and ownership types that have been filtered as described throughout this document.

4. **Create Sheet for All Violations without Territories**
    This will create a sheet of all states, filtered by the given star range and ownership types. The states will not be grouped by territories.

&nbsp; 

## Additional Information about the Home Healthcare Dataset
More information about the dataset is included [here](https://data.cms.gov/provider-data/sites/default/files/data_dictionaries/home_health/HHS_Data_Dictionary.pdf), which is also included as a pdf named "HomeHealthcare_Data_Dictionary" in the "documents" folder of this repo.

&nbsp;  
&nbsp;  
&nbsp;  

## Long Term Care Hospitals
---
The Long Term Care Hospital dataset is made up of measure codes, which correspond to different quality measures for Long Term Care Hospitals. Each row of the dataset is made up of an organization, a measure code, and a score for that measure code, along with other attribute columns. The measure codes are described [here](https://data.cms.gov/provider-data/sites/default/files/data_dictionaries/long_term_care_hospital/LTCH-Data-Dictionary.pdf), as well as in the "LongTermCareHospital-Data-Dictionary" pdf in the "documents" folder of this repo.

&nbsp;  

## Filter by Bed Range
Each row has a corresponding "total_number_of_beds". Filtering by bed range allows a user to include only organizations within their chosen bed range, which can be any whole number greater than 0. Similar to date and tag filters for the Nursing Home dataset, the bed range filtered dataset will be used for the rest of the options!

## Exclude ownership types
Each Long Term Care Hospital organization has an associated "ownership_type". On the "Format CSV Data" screen for Long Term Care Hospital, the user can choose to exclude organizations with certain types of ownership. "Undefined" organizations are organizations that have a blank value for "ownership_type" in the dataset. Similar to bed range, the organization type filtered dataset will be used for the rest of the options!


### Options
1. **Create Sheet with All Territories Combined**
    This will include a sheet of all of the territories chosen by the user (or the defaults) combined. The same rules apply for beds and ownership types that have been filtered as described throughout this document.

2. **Create Sheet for All Violations without Territories**
    This will create a sheet of all states, filtered by the given bed range and ownership types. The states will not be grouped by territories.

&nbsp; 

## Additional Information about the Long Term Care Hospital Dataset
More information about the dataset is included [here](https://data.cms.gov/provider-data/sites/default/files/data_dictionaries/long_term_care_hospital/LTCH-Data-Dictionary.pdf), which is also included as a pdf named "LongTermCareHospital-Data-Dictionary" in the "documents" folder of this repo.

&nbsp;  
&nbsp;  
&nbsp; 
