import tkinter as tk
from tkinter import ttk, scrolledtext
from tkinter.filedialog import askdirectory
from typing import List
from PIL import Image, ImageTk
import pickle, threading, datetime, os, sys
import nursing_home_gui, home_health_gui, long_term_care_gui
# Get imports from parent directory
sys.path.insert(1, os.path.join(sys.path[0], '..'))
import info, utilities as util


# Global variables

df = None
territories = {}
chosen_tags = []

class TkWait:
    ''' Used to let program wait while also updating the UI. '''
    def __init__(self, master, milliseconds):
        self.duration = milliseconds
        self.master = master
        
    def __enter__(self):
        self.resume = tk.BooleanVar(value=False)
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.master.after(self.duration, self.resume.set, True)
        self.master.wait_variable(self.resume)
  
class tkinterApp(tk.Tk):
    ''' The main program class. '''
     
    # __init__ function for class tkinterApp
    def __init__(self, *args, **kwargs):

        self.home_folder_path = ""
        # Contains tags and their descriptions
        with open(util.resource_path("../assets/tag_hash.pkl"), 'rb') as inp:
            self.tag_hash = pickle.load(inp)
         
        # __init__ function for class Tk
        tk.Tk.__init__(self, *args, **kwargs)
        self.title("NHI Scraper")
        self.iconbitmap(util.resource_path("../images/icon.ico"))
    
        # Prevents user from stretching screen
        self.resizable(width=False, height=False)
        self.geometry("500x320")
         
        # creating a container
        self.container = tk.Frame(self) 
        self.container.pack(side = "top", fill = "both", expand = True)
  
        self.container.grid_rowconfigure(0, weight = 1)
        self.container.grid_columnconfigure(0, weight = 1)
  
        # Initializing frames to an empty dict so that we can access pages by their name
        self.frames = {}

         # Will create a folder at the User's home folder for this programs data
        self.setup_savedata()
        self.add_frames([StartPage, MainOptionsPage, FormatPage])
        self.show_frame(StartPage)

        self.startdate: datetime = None
        self.enddate: datetime = None
        self.tags: List[str] = []
        self.territories: dict[str, list[str]] = {}
        self.options = {} # Excel formatting options for the different data categories
        

    def show_frame(self, cont):
        ''' Shows frame that was passed in as a parameter. '''
        frame = self.frames[cont]
        frame.tkraise()        

    
    def add_frames(self, frames):
        ''' Add a frame to the dict of pages. '''
        for F in frames:
            frame = F(self.container, self)
            self.frames[F] = frame
            frame.grid(row = 0, column = 0, sticky ="nsew")


    def resize_optionspage(self):
        ''' Window size for options page. '''
        self.geometry("500x650")

    
    def setup_savedata(self):
        ''' Creates a folder for this program's data. '''
        #global home_folder_path
        abs_home = os.path.abspath(os.path.expanduser("~"))
        self.home_folder_path = abs_home + "/ViolationToolv2/"
        # print("First: " + self.home_folder_path)

        # Create all folders if they don't already exist
        if not os.path.exists(self.home_folder_path):
            os.mkdir(self.home_folder_path)
        
        # Make all necessary folders
        folders = ["assets", "rawdata", "dataframes"]
        for folder in folders:
            if not os.path.exists(self.home_folder_path + folder):
                os.mkdir(self.home_folder_path + folder)

    def add_tags(self, tags: List[str]):
        ''' Save tags that are chosen by the user for nursing homes. '''
        self.tags = tags
    
    def add_dates(self, startdate: datetime, enddate: datetime):
        ''' Save filter dates that are chosen by the user. '''
        self.startdate = startdate
        self.enddate = enddate

    def set_territories(self, territories: dict[str, list[str]]):
        ''' Save territories that are defined by the user. '''
        self.territories = territories



class PageLayout(tk.Frame):
    ''' Default page layout. '''
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        # Logo
        logo = Image.open(util.resource_path("../images/logo.png"))
        logo = ImageTk.PhotoImage(logo)
        logo_label = ttk.Label(self, image=logo)
        logo_label.image = logo
        logo_label.grid(column=1, row=0, columnspan=3)


class StartPage(tk.Frame):
    ''' The first page that a user sees. Asks if they want to download fresh data. '''
    def __init__(thisframe, parent, controller):
        PageLayout.__init__(thisframe, parent)
        thisframe.controller = controller
        thisframe.parent = parent
         
        # Instructions and Buttons
        thisframe.instructions = ttk.Label(thisframe, text="Welcome! Do you want to download the most recent data?", font=("Times", 15))
        thisframe.instructions.grid(column=1, row=1, columnspan=3, pady=10)

        instructions2 = "Your save data is from: {}"
        with open(controller.home_folder_path + "assets/lastupdate.pkl", "rb") as inp:
            lastlocalupdate = pickle.load(inp)

        thisframe.instructions2 =  ttk.Label(thisframe, text=instructions2.format(lastlocalupdate), font=("Times", 15))
        thisframe.instructions2.grid(column=1, row=2, columnspan=3, pady=10)
        
        thisframe.yes_btn = tk.Button(thisframe, text="Yes", command=lambda:thisframe.download_data(), font="Times", bg="#000099", fg="#00ace6", height=2, width=15)
        thisframe.yes_btn.grid(column=1, row=4, pady=10)

        thisframe.no_btn = tk.Button(thisframe, text="No", command=lambda:thisframe.show_options(False), font="Times", bg="#000099", fg="#00ace6", height=2, width=15)
        thisframe.no_btn.grid(column=3, row=4, pady=10)


    def download_data(thisframe):
        ''' Creates a thread that calls util.download, so that UI can be updated while fresh data is downloaded. '''
        thisframe.instructions.config(text="Downloading data...")
        thisframe.instructions2.grid_forget()
        thisframe.yes_btn.grid_forget()
        thisframe.no_btn.grid_forget()

        class thread(threading.Thread):
            ''' Create a custom thread class so that we can update the screen during download. '''
            def __init__(self, func):
                threading.Thread.__init__(self)
                self.func = func
        
            def run(self):
                self.func(thisframe)

        thread(util.download).start()

    def show_options(thisframe, downloaded):
        ''' Advance page after download. '''
        if downloaded:
            with TkWait(thisframe.parent, 3000):
                thisframe.instructions.config(text="Download finished")
        
        global df
        with open(thisframe.controller.home_folder_path + "dataframes/df.pkl", 'rb') as inp:
            df = pickle.load(inp)

        thisframe.controller.resize_optionspage()
        thisframe.controller.show_frame(MainOptionsPage)


class MainOptionsPage(tk.Frame):
    ''' Shows users options for the datasets. '''
    def __init__(self, parent, controller):
        PageLayout.__init__(self, parent)
        self.controller = controller

        # Instructions, Buttons for options
        option_count = 1
        self.instructions = ttk.Label(self, text="Choose your options", font=("Times", 15))
        self.instructions.grid(column=1, row=option_count, columnspan=3, pady=15)
        option_count += 1 

        self.instructions2 = ttk.Label(self, text="", font=("Times", 15))
        self.instructions2.grid(column=1, row=option_count, columnspan=3)
        option_count += 1 

        self.terr_btn = tk.Button(self, command=lambda:self.show_territories(), text="Set Territories", font="Times", bg="#000099", fg="#00ace6", height=1, width=30)
        self.terr_btn.grid(column=2, row=option_count, pady=15)
        option_count += 1 

        self.date_btn = tk.Button(self, command=lambda:self.show_daterange(), text="Set Date Range", font="Times", bg="#000099", fg="#00ace6", height=1, width=30)
        self.date_btn.grid(column=2, row=option_count, pady=15)
        option_count += 1

        # self.tag_btn = tk.Button(self, command=lambda:self.show_tags(), text="Choose Tags to Include", font="Times", bg="#000099", fg="#00ace6", height=1, width=30)
        # self.tag_btn.grid(column=2, row=option_count, pady=15)
        # option_count += 1

        self.tag_btn = tk.Button(self, command=lambda:self.show_nursing_home_data(), text="Format Nursing Home Data", font="Times", bg="#000099", fg="#00ace6", height=1, width=30)
        self.tag_btn.grid(column=2, row=option_count, pady=15)
        option_count += 1

        self.tag_btn = tk.Button(self, command=lambda:self.show_home_health_data(), text="Format Home Health Data", font="Times", bg="#000099", fg="#00ace6", height=1, width=30)
        self.tag_btn.grid(column=2, row=option_count, pady=15)
        option_count += 1
         
        self.tag_btn = tk.Button(self, command=lambda:self.show_long_term_care_data(), text="Format Long Term Care Hospital Data", font="Times", bg="#000099", fg="#00ace6", height=1, width=30)
        self.tag_btn.grid(column=2, row=option_count, pady=15)
        option_count += 1

        # self.excel_btn = tk.Button(self, command=lambda:self.show_format(), text="Format Excel Data", font="Times", bg="#000099", fg="#00ace6", height=1, width=30)
        # self.excel_btn.grid(column=2, row=option_count, pady=15)
        # option_count += 1 

        self.make_btn = tk.Button(self, command=lambda:self.show_excel(), text="Make Excel Files", font="Times", bg="#000099", fg="#00ace6", height=1, width=30)
        self.make_btn.grid(column=2, row=option_count, pady=15)
        option_count += 1 

    # Functions to show appropriate screens and disable buttons after press
    def show_territories(self):
        self.controller.add_frames([TerritoriesPage]) 
        self.controller.show_frame(TerritoriesPage)

    def show_daterange(self):    
        self.controller.add_frames([DateRangePage]) 
        self.controller.geometry("500x600")
        self.controller.show_frame(DateRangePage)
    
    def show_nursing_home_data(self):
        self.controller.add_frames([nursing_home_gui.OptionsPage])
        self.controller.geometry("500x520")
        self.controller.show_frame(nursing_home_gui.OptionsPage)

    def show_home_health_data(self):
        self.controller.resize_optionspage()
        self.controller.add_frames([home_health_gui.OptionsPage])
        self.controller.show_frame(home_health_gui.OptionsPage)

    def show_long_term_care_data(self):
        self.controller.resize_optionspage()
        self.controller.add_frames([long_term_care_gui.OptionsPage])
        self.controller.show_frame(long_term_care_gui.OptionsPage)

    def show_excel(self):
        self.controller.geometry("500x370")
        self.controller.add_frames([ExcelPage])
        self.controller.show_frame(ExcelPage)



class TerritoriesPage(tk.Frame):
    ''' Page where states in each territory are set. '''
    def __init__(self, parent, controller):
        PageLayout.__init__(self, parent)
        self.controller: tkinterApp = controller

        # Instructions, Territory box and Next button 
        self.instructions = ttk.Label(self, text="Enter territory names, each on their own line", font=("Times", 15))
        self.instructions.grid(column=1, row=1, columnspan=3, pady=10)

        self.instructions2 = ttk.Label(self, text="", font=("Times", 15))
        self.instructions2.grid(column=1, row=2, columnspan=3, pady=10)

        self.box = scrolledtext.ScrolledText(self, undo=True, width=40, height=10)
        self.box.grid(column=2, row=3, pady=10)

        self.nextbtn = tk.Button(self, command=lambda:self.set_terr(), text="Next", font="Times", bg="#000099", fg="#00ace6", height=1, width=30)
        self.nextbtn.grid(column=2, row=4, pady=30)

        self.allbtn = tk.Button(self, command=lambda:self.use_all(), text="Use Default Territories", font="Times", bg="#000099", fg="#00ace6", height=1, width=30)
        self.allbtn.grid(column=2, row=5, pady=3)

        self.cancel_btn = tk.Button(self, command=lambda:self.cancel(), text="Cancel", font="Times", bg="#000099", fg="#00ace6", height=1, width=5)
        self.cancel_btn.grid(column=2, row=6, pady=3)

        def hide_cancel_button(_):
            ''' Hides the cancel button once user types anything into the boxes. '''
            self.cancel_btn.grid_forget()
        self.box.bind('<Key>', hide_cancel_button)

        # Used for populating territories
        self.count = 0 


    def use_all(self):
        ''' When use default is pressed. '''
        self.controller.set_territories(info.territories)
        self.controller.show_frame(MainOptionsPage)


    def cancel(self):
        ''' When cancel is pressed. '''
        self.controller.show_frame(MainOptionsPage)

    
    def set_terr(self):
        ''' Lets the user add territories. '''
        lines = self.box.get("1.0","end-1c").splitlines()
        lines = [x for x in lines if x != '']
        if len(lines) != 0:
            # Makes dict to hold territories and their states
            self.controller.set_territories({key: [] for key in lines})
            self.tlist = lines

            # Update screen
            self.add_states()
    
        else:
            self.instructions.config(text="Please enter at least one territory")


    def add_states(self):
        ''' Lets the user add states. '''
        bad, last = False, False
        self.instructions2.config(text="Use full state names, with first letter capitalized".format(self.tlist[0]))
        # First territory
        if self.count == 0:
            self.instructions.config(text="Enter states in {} territory, each on their own line".format(self.tlist[0]))
            self.nextbtn.config(command=lambda:self.add_states())

            # If there's only one territory
            if len(self.tlist) == 1:
                self.nextbtn.config(text="Finish")

        elif self.count > 0:
            # Grab states from box
            states = self.box.get("1.0","end-1c").splitlines()
            states = [x.strip() for x in states if x != '']

            # Make sure valid states were given
            if len(states) != 0:
                for state in states:
                    if state not in info.all_states:
                        self.instructions.config(text="Please make sure states are spelled correctly and valid")
                        bad = True
            else:
                # If there isn't at least one valid state
                self.instructions.config(text="Please enter at least one valid state")
                bad = True

            # Only continue if valid input was given
            if not bad:
                # Update territory hash
                terr = self.tlist[self.count-1]
                self.controller.territories[terr] = states
                # Update screen
                if self.count < len(self.tlist):
                    terr = self.tlist[self.count]
                    self.instructions.config(text="Enter states in {} territory, each on their own line".format(terr))
                # Updates the button
                if self.count == len(self.tlist) - 1:
                    self.nextbtn.config(text="Finish")
                # Last screen
                elif self.count == len(self.tlist):
                    print(f"Chosen Territories: {self.controller.territories}")
                    last = True
                    self.controller.show_frame(MainOptionsPage)
                    TerritoriesPage.destroy(self)


        # Clear the box
        if not bad and not last:
            self.box.delete("1.0", "end")
            self.count += 1



class DateRangePage(tk.Frame):
    ''' Page where date range for cases is set. '''
    def __init__(self, parent, controller):
        PageLayout.__init__(self, parent)
        self.controller: tkinterApp = controller   

        # Instructions, Dates, Buttons
        self.instructions = ttk.Label(self, text="Choose range of dates to include in excel file", font=("Times", 15))
        self.instructions.grid(column=1, row=2, columnspan=3, pady=10)

        self.instructions2 = ttk.Label(self, text="Start date (MM/DD/YYYY)", font=("Times", 15))
        self.instructions2.grid(column=1, row=3, columnspan=3, pady=10)

        self.instructions3 = ttk.Label(self, text="End date (MM/DD/YYYY)", font=("Times", 15))
        self.instructions3.grid(column=1, row=5, columnspan=3, pady=10)

        self.start = tk.Text(self, height=2, width=25)
        self.start.grid(column=2, row=4, pady=10)

        self.end = tk.Text(self, height=2, width=25)
        self.end.grid(column=2, row=6, pady=10)

        self.fin_btn = tk.Button(self, command=lambda:self.check_range(), text="Finish", font="Times", bg="#000099", fg="#00ace6", height=1, width=30)
        self.fin_btn.grid(column=2, row=7, pady=20)
       
        self.instructions4 = ttk.Label(self, text=".. or use all dates in the dataset", font=("Times", 15))
        self.instructions4.grid(column=1, row=8, columnspan=3, pady=10)

        self.rec_btn = tk.Button(self, command=lambda:self.all_dates(), text="All Dates", font="Times", bg="#000099", fg="#00ace6", height=1, width=30)
        self.rec_btn.grid(column=2, row=9, pady=20)

        self.cancel_btn = tk.Button(self, command=lambda:self.cancel(), text="Cancel", font="Times", bg="#000099", fg="#00ace6", height=1, width=5)
        self.cancel_btn.grid(column=2, row=10, pady=3)

        
        def hide_cancel_button(_):
            ''' Hides the cancel button once user types anything into the boxes. '''
            self.cancel_btn.grid_forget()
        self.start.bind('<Key>', hide_cancel_button)
        self.end.bind('<Key>', hide_cancel_button)
       

    def cancel(self):
        ''' When cancel is pressed. '''
        self.controller.resize_optionspage()
        self.controller.show_frame(MainOptionsPage)


    def all_dates(self):
        ''' Sets start and end dates to None, this will make sure that min and max dates used when excel sheets are made. '''
        self.controller.add_dates(None, None)
        self.controller.resize_optionspage()
        self.controller.show_frame(MainOptionsPage)

    
    def check_range(self):
        ''' Checks to see if dates are in correct format and within range -> need to add earliest date. '''
        try:
            stext = self.start.get("1.0","end-1c")
            etext = self.end.get("1.0","end-1c")
            stime = datetime.datetime.strptime(stext, '%m/%d/%Y')
            etime = datetime.datetime.strptime(etext, '%m/%d/%Y')
            today = datetime.datetime.today()

            # If user gives start date later than end date
            if stime > etime:
                self.instructions.config(text="Start date must be less than or equal to end date!")
            elif stime > today or etime > today:
                self.instructions.config(text="Dates cannot be in the future!")
            else:
                self.controller.add_dates(stime, etime)
                self.controller.resize_optionspage()
                self.controller.show_frame(MainOptionsPage)
                DateRangePage.destroy()

        except:
            self.instructions.config(text="Check date formats and retry")


class FormatPage(tk.Frame):
    ''' Format excel sheets. '''
    def __init__(self, parent, controller):
        PageLayout.__init__(self, parent)
        self.controller = controller

        # Instructions
        self.instructions = ttk.Label(self, text="Choose which data to include", font=("Times", 15))
        self.instructions.grid(column=1, row=2, columnspan=3, pady=10)\
        
        self.instructions2 = ttk.Label(self, text="Will include dates and tags chosen or defaults if none are selected", font=("Times", 15))
        self.instructions2.grid(column=1, row=3, columnspan=3, pady=10)

        # Holds buttons
        self.options = {"US Fines":False, "US Violations":False,
                            "Top fined organizations per state":False, "Most severe organizations per state":False,
                            "Sum of fines per state per year":False, "Sum of violations per state per year":False,
                            "Sum of fines per tag per year":False, "Sum of violations per tag per year":False,
                            "Create sheet with all territories combined":False, "All Violations":False}

        # Frame to hold the buttons and list to access them directly
        self.fm = ttk.Labelframe(self, width=50, border=0)
        self.fm.grid(column=2, row=4)
        self.boxes = []
        i = 0
        
        # Buttons
        self.boxes.append(tk.Checkbutton(self.fm, width=35, text="US Fines (Total, yearly)", anchor="w", command=lambda:self.add_option("US Fines")))
        self.boxes[i].grid()
        i += 1

        self.boxes.append(tk.Checkbutton(self.fm, width=35, text="US Violations (Total, yearly)", anchor="w", command=lambda:self.add_option("US Violations")))
        self.boxes[i].grid()
        i += 1

        self.boxes.append(tk.Checkbutton(self.fm, text="Top fined organizations (Total, yearly)", width=35, anchor="w", command=lambda:self.add_option("Top fined organizations per state")))
        self.boxes[i].grid()
        i += 1

        self.boxes.append(tk.Checkbutton(self.fm, text="Most severe organizations (Total, yearly)", width=35, anchor="w", command=lambda:self.add_option("Most severe organizations per state")))
        self.boxes[i].grid()
        i += 1

        self.boxes.append(tk.Checkbutton(self.fm, text="Sum of fines per state (Total, yearly)", width=35, anchor="w", command=lambda:self.add_option("Sum of fines per state per year")))
        self.boxes[i].grid()
        i += 1

        self.boxes.append(tk.Checkbutton(self.fm, text="Sum of violations per state (Total, yearly)", width=35, anchor="w", command=lambda:self.add_option("Sum of violations per state per year")))
        self.boxes[i].grid()
        i += 1

        self.boxes.append(tk.Checkbutton(self.fm, text="Sum of fines per tag (Total, yearly)", width=35, anchor="w", command=lambda:self.add_option("Sum of fines per tag per year")))
        self.boxes[i].grid()
        i += 1

        self.boxes.append(tk.Checkbutton(self.fm, text="Sum of violations per tag (Total, yearly)", width=35, anchor="w", command=lambda:self.add_option("Sum of violations per tag per year")))
        self.boxes[i].grid()
        i += 1

        self.boxes.append(tk.Checkbutton(self.fm, text="Create sheet with all territories combined", width=35, anchor="w", command=lambda:self.add_option("Create sheet with all territories combined")))
        self.boxes[i].grid()
        i += 1

        self.boxes.append(tk.Checkbutton(self.fm, text="Create sheet for all violations without territories", width=35, anchor="w", command=lambda:self.add_option("All Violations")))
        self.boxes[i].grid()
        i += 1

        # Butttons
        self.all_btn = tk.Button(self, command=lambda:self.select_all(), text="Select All", font="Times", bg="#000099", fg="#00ace6", height=1, width=30)
        self.all_btn.grid(column=2, row=5, pady=15)
        self.all = False

        self.fin_btn = tk.Button(self, command=lambda:self.finish(), text="Finish", font="Times", bg="#000099", fg="#00ace6", height=1, width=30)
        self.fin_btn.grid(column=2, row=6, pady=5)

        # Sets all boxes to have no checkmark - need this so a user can click back in 
        for box in self.boxes:
            box.deselect()


    def finish(self):
        ''' Once user is done selecting options. '''
        global options; options = self.options
        self.controller.resize_optionspage()
        self.controller.show_frame(MainOptionsPage)
        for button in self.boxes:
            button.destroy()
        self.fm.destroy()
        FormatPage.destroy(self)


    def add_option(self, opt):
        ''' Add a chosen option to a list. '''
        self.options[opt] = not self.options[opt]


    def select_all(self):
        ''' Select all button functionality. '''
        if self.all:    
            self.options = {k: False for k, _ in self.options.items()}
            for box in self.boxes:
                box.deselect()   
            self.all = False
            self.all_btn.config(text="Select All")   
        else:         
            self.options = {k: True for k, _ in self.options.items()}
            for box in self.boxes:
                box.select()
            self.all = True
            self.all_btn.config(text="Unselect All")   



class ExcelPage(tk.Frame):
    ''' Page where excel sheet is made. '''
    def __init__(thisframe, parent, controller):
        PageLayout.__init__(thisframe, parent)
        thisframe.controller: tkinterApp = controller

        # Instructions and Make sheets button
        thisframe.instructions = ttk.Label(thisframe, text="Press button to choose where to save excel sheets", font=("Times", 15))
        thisframe.instructions.grid(column=1, row=2, columnspan=3, pady=10)

        thisframe.instructions2 = ttk.Label(thisframe, text="Sheet creation will start", font=("Times", 15))
        thisframe.instructions2.grid(column=1, row=3, columnspan=3, pady=10)
    
        thisframe.sheet_btn = tk.Button(thisframe, command=lambda:thisframe.make_sheets(controller), text="Make Sheets", font="Times", bg="#000099", fg="#00ace6", height=1, width=30)
        thisframe.sheet_btn.grid(column=2, row=4, pady=40)

        thisframe.cancel_btn = tk.Button(thisframe, command=lambda:thisframe.cancel(), text="Go Back", font="Times", bg="#000099", fg="#00ace6", height=1, width=5)
        thisframe.cancel_btn.grid(column=2, row=5, pady=3)


    def cancel(thisframe):
        ''' Lets a user go back to OptionsPage. '''
        thisframe.controller.resize_optionspage()
        thisframe.controller.show_frame(MainOptionsPage)


    def make_sheets(thisframe, controller):
        ''' Uses threads to make excel sheets -> need to first break data up by territory. '''
        outpath = askdirectory()
        if outpath == "":
            print(f"No save location chosen: saving to {controller.home_folder_path}")
            outpath = controller.home_folder_path
        else:
            print(f"Save path chosen: {outpath}")

        # Make a folder for the sheets
        outpath = outpath + "/ViolationToolExcelData/"
        if not os.path.exists(outpath):
            os.mkdir(outpath)

        print(f"Home folder path: {controller.home_folder_path}")
        with open(controller.home_folder_path + "dataframes/df.pkl", 'rb') as inp:
            nursing_home_df = pickle.load(inp)
        with open(controller.home_folder_path + "dataframes/hhc_df.pkl", 'rb') as inp:
            home_health_df = pickle.load(inp)  
        with open(controller.home_folder_path + "dataframes/ltch_df.pkl", 'rb') as inp:
            long_term_care_df = pickle.load(inp)    

        # Create a thread to run make_sheets() so we can update the screen
        class thread(threading.Thread):
            def __init__(self, func):
                threading.Thread.__init__(self)
                self.func = func
        
            def run(self):
                global options
                self.func(thisframe, nursing_home_df, home_health_df, long_term_care_df, outpath)

        thisframe.cancel_btn.grid_forget()
        thread(util.make_sheets).start()

    
    def finish(thisframe):
        ''' Once sheets are made. '''
        thisframe.controller.add_frames([DonePage]) # Not sure why I have to re-add this...
        thisframe.controller.show_frame(DonePage)



class DonePage(tk.Frame):
    ''' After excel sheets are made. '''
    def __init__(self, parent, controller):
        PageLayout.__init__(self, parent)
        self.controller = controller

        # Instructions
        self.instructions = ttk.Label(self, text="Program finished", font=("Times", 15))
        self.instructions.grid(column=1, row=2, columnspan=3, pady=10)

        self.sheet_btn = tk.Button(self, command=lambda:self.exit(), text="Exit Program", font="Times", bg="#000099", fg="#00ace6", height=1, width=30)
        self.sheet_btn.grid(column=2, row=3, pady=40)

    def exit(self):
        ''' Quit the app. '''
        self.controller.quit()
    

if __name__ == '__main__':
    # Driver Code
    app = tkinterApp()
    app.mainloop()
