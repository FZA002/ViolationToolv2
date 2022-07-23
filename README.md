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
5. In the terminal, type "chmod +x ./ViolationTool". 
6. Now go to your desktop and click on the program. You should now get a pop up from Apple acting as the Warden between you and malicious actors. Just press "OK".
7. Click on the apple logo at the top left of your screen. Then System Preferences -> Security & Privacy -> General. You should see a message about how ViolationTool was blocked. Allow it to open. You can trust me :)
8. Be patient and the program will be at your service. A terminal will pop up and produce text on occasion. If the program doesn't work as expected, or at all, and text pops up in the terminal window, please copy it and send me it. You should be able to just click the program to run it from now on.
&nbsp;  
&nbsp;

For your first time running, please choose to download data. The program will also create a folder in your User folder where it will store all necessary data that it downloads and updates. Do NOT move this folder or the program will not work! The very first screen of the program will tell you if this data is up to date with Nursing Home Inspect's data. If the program is up to date, there is no need to click yes on the first screen.

&nbsp;  
&nbsp;  
&nbsp;  

## **Breakdowns of Options and Filters, by Dataset** 
---

## Filter by Territories
A user is able to dynamically input territories of whatever name they choose. A territory is simply a group of states that the user gets to set. As mentioned above, a user will get one excel sheet per territory that they create. If a user skips this option, the default territories are East, West, and Central. The 52 states are divided amongst these.

## Filter by Date Range
A user is able to specify a range of dates for which they want to see data for. This date range is inclusive, meaning the start and end dates will be included. A user may choose to use the whole date range available, which, as mentioned above, is from 2015-2021. An important note on this date range: it will apply to other options. For example, one other option is to include data on the fines for the entire US. The total shown will only include data in a user's date range! This includes individual years. For example, consider if a user sets their date range as 01/10/2019-01/01/2021. The total produced for the US will include 01/10/2019-12/31/2019 (inclusive), all of 2020, and 01/01/2021. The total shown for 2019 and 2021 individually would abides by the same metrics

## Filter by Tags
Each violation recorded by Nursing Home Inspect has a corresponding tag. A tag is simply a way of categorizing a violation based on its nature. For example, tag F757's description is "Drug Regimen is Free From Unnecessary Drugs". A pdf of all F-Tags is included in this repo as "Ftags.pdf". All tags will also be listed in the "OptionalData" excel sheet that is made each time you run the program. Additionally, anything that you input that isn't a valid tag will not be used and will be displayed on the screen once you finish entering tags.

## Format Excel Sheet
This screen allows a user to pick what extra data they would like included in an excel file. This file will be separate from the individual files for each territory. Roughly each option gets its own sheet in a file titled "OptionalData.xlsx". All of the following options will be derived from the dataset AFTER it has been filtered by a user's chosen tags and date range! The options are described below.   


### Options
1. **US Fines:**
    This will include a total for each year in a given date range, as well as a total for that range. As described above in the "Filter by Date Range" section, the total shown and individual years will only include dates in the given range!

2. **US Violations:**
    This will include a total for each year in a given date range, as well as a total for that range. The same rules apply for dates in range as described throughout this document.

3. **Top Fined Organizations:**
    This will include a sheet that will include the top 3 most fined organizations per state, per year, and overall. The same rules apply for dates in range as described throughout this document.

4. **Most Severe Organizations:**
    This will include a sheet that will include the top 3 most severe organizations per state, per year, and overall. The same rules apply for dates in range as described throughout this document. An organization's severity is ranked via severity scores associated with each violation. The scores are calculated as described at the end of the document.

5. **Sum of Fines and Violations per State:**
    These will include sheets that will include the total number of violations and fines for each state, for each year in range, and a total for the date range. The same rules apply for dates in range as described throughout this document.

6. **Create Sheet with All Territories Combined**
    This will include a sheet of all of the territories chosen by the user (or the defaults) combined. 

7. **Create Sheet for All Violations without Territories**
    This will create a sheet of all states, filtered by the given date range and tags. **This can take a long time!** The less filters used, the longer it will take. It could take around 20 minutes in my experience, if you include the entire date and tag range.  

## Format of Data in the Excel Sheets
The main excel sheets, which are the ones for the individual territories, combined territories, and without territories, are formatted the same way. Violations are grouped by territory (if relevant), then by state, then by organzation, then by date. Multiple violations may have taken place on the same date! This will be represented by multiple tags separated by commas in the "Tag" column. The number of violations on a date directly correlates to the number of tags in that rows "Tag" column. Tags will be listed without the leading "F". For example, tag F757 will be shown as just 757 in the excel sheets. Each tag and severity also match up. For example, if on 07/10/2021 the tag column has the tags, "757, 796, 869" and the severity column has the severities "D, E, B", then the pairs would be 757 and D, 796 and E, and 869 and B. This would mean that on 07/10/2021 there were 3 violations, one with tag 757 and severity D, etc. The severities' descriptions are included in the "OptionalData" excel file by default. 

## How Severity is Calculated for States and Organizations
The scores are based off of CMS's "Design for Care Compare Nursing Home Five-Star Quality Rating System:
Technical Users’ Guide", available at https://www.cms.gov/Medicare/Provider-Enrollment-and-Certification/CertificationandComplianc/downloads/usersguide.pdf. The specific numeric value associated with each scope severity code
is included in the "OptionalData" excel file that is made each time any other excel sheets are made.

