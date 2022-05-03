import tkinter as tk
from tkinter import ttk, scrolledtext
from tkinter.filedialog import askdirectory
from PIL import Image, ImageTk
import pickle, threading, datetime, os, shutil, info
import utilities as util

# Global variables
home_folder_path = ""
df = None
sdate = None
edate = None
options = None
territories = {}
chosen_tags = []


# Contains tags and their descriptions
with open(util.resource_path("assets/tag_hash.pkl"), 'rb') as inp:
    tag_hash = pickle.load(inp)

class TkWait:
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
     
    # __init__ function for class tkinterApp
    def __init__(self, *args, **kwargs):
         
        # __init__ function for class Tk
        tk.Tk.__init__(self, *args, **kwargs)
        self.title("NHI Scraper")
        self.iconbitmap(util.resource_path("images/icon.ico"))
    
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
  
        self.add_frames([StartPage, OptionsPage, FormatPage, ExcelPage, DonePage])

        self.show_frame(StartPage)
        
    # Shows frame that was passed in as a parameter
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()        

    # Add a frame to the dict of pages 
    def add_frames(self, frames):
        for F in frames:
            frame = F(self.container, self)
            self.frames[F] = frame
            frame.grid(row = 0, column = 0, sticky ="nsew")

    # Window size for options page
    def resize_optionspage(self):
        self.geometry("500x650")

    # Creates a folder for this program's data
    def setup_savedata(self):
        global home_folder_path
        abs_home = os.path.abspath(os.path.expanduser("~"))
        home_folder_path = abs_home + "/ViolationToolv2/"

        # Create all folders if they don't already exist
        if not os.path.exists(home_folder_path):
            os.mkdir(home_folder_path)
        
        # Make all necessary folders
        folders = ["assets", "rawdata", "dataframes"]
        for folder in folders:
            if not os.path.exists(home_folder_path + folder):
                os.mkdir(home_folder_path + folder)
        

# Default page layout
class PageLayout(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        # Logo
        logo = Image.open(util.resource_path("images/logo.png"))
        logo = ImageTk.PhotoImage(logo)
        logo_label = ttk.Label(self, image=logo)
        logo_label.image = logo
        logo_label.grid(column=1, row=0, columnspan=3)

# Start Page
class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        PageLayout.__init__(self, parent)
        self.controller = controller
        self.parent = parent
         
        # Instructions and Buttons
        self.instructions = ttk.Label(self, text="Welcome! Do you want to download the most recent data?", font=("Times", 15))
        self.instructions.grid(column=1, row=1, columnspan=3, pady=10)

        instructions2 = "Your save data is from: {}"
        global home_folder_path
        with open(home_folder_path + "assets/lastupdate.pkl", "rb") as inp:
            lastlocalupdate = pickle.load(inp)

        self.instructions2 =  ttk.Label(self, text=instructions2.format(lastlocalupdate), font=("Times", 15))
        self.instructions2.grid(column=1, row=2, columnspan=3, pady=10)
        
        self.yes_btn = tk.Button(self, text="Yes", command=lambda:self.download_data(), font="Times", bg="#000099", fg="#00ace6", height=2, width=15)
        self.yes_btn.grid(column=1, row=4, pady=10)

        self.no_btn = tk.Button(self, text="No", command=lambda:self.show_options(False), font="Times", bg="#000099", fg="#00ace6", height=2, width=15)
        self.no_btn.grid(column=3, row=4, pady=10)

    # If yes is selected 
    def download_data(thisframe):
        thisframe.instructions.config(text="Downloading data...")
        thisframe.instructions2.grid_forget()
        thisframe.yes_btn.grid_forget()
        thisframe.no_btn.grid_forget()

        # Create a custom thread class so that we can update the screen during download
        class thread(threading.Thread):
            def __init__(self, func):
                threading.Thread.__init__(self)
                self.func = func
        
            def run(self):
                self.func(thisframe)

        thread(util.download).start()

    # Advance page after download
    def show_options(self, downloaded):
        if downloaded:
            with TkWait(self.parent, 3000):
                self.instructions.config(text="Download finished")
        
        global df, home_folder_path
        with open(home_folder_path + "dataframes/df.pkl", 'rb') as inp:
            df = pickle.load(inp)

        self.controller.resize_optionspage()
        self.controller.show_frame(OptionsPage)


# Shows users options for the dataset
class OptionsPage(tk.Frame):
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

        self.tag_btn = tk.Button(self, command=lambda:self.show_tags(), text="Choose Tags to Include", font="Times", bg="#000099", fg="#00ace6", height=1, width=30)
        self.tag_btn.grid(column=2, row=option_count, pady=15)
        option_count += 1 

        self.excel_btn = tk.Button(self, command=lambda:self.show_format(), text="Format Excel Data", font="Times", bg="#000099", fg="#00ace6", height=1, width=30)
        self.excel_btn.grid(column=2, row=option_count, pady=15)
        option_count += 1 

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
    
    def show_tags(self):
        self.controller.add_frames([TagsPage])
        self.controller.geometry("500x520")
        self.controller.show_frame(TagsPage)

    def show_format(self):
        self.controller.resize_optionspage()
        self.controller.add_frames([FormatPage])
        self.controller.show_frame(FormatPage)

    def show_excel(self):
        self.controller.geometry("500x370")
        self.controller.show_frame(ExcelPage)


# Page where states in each territory is set
class TerritoriesPage(tk.Frame):
    def __init__(self, parent, controller):
        PageLayout.__init__(self, parent)
        self.controller = controller

        # Instructions, Territory box and Next button 
        self.instructions = ttk.Label(self, text="Enter territory names, each on their own line", font=("Times", 15))
        self.instructions.grid(column=1, row=1, columnspan=3, pady=10)

        self.instructions2 = ttk.Label(self, text="", font=("Times", 15))
        self.instructions2.grid(column=1, row=2, columnspan=3, pady=10)

        self.box = scrolledtext.ScrolledText(self, undo=True, width=40, height=10)
        self.box.grid(column=2, row=3, pady=10)

        self.nextbtn = tk.Button(self, command=lambda:self.set_terr(), text="Next", font="Times", bg="#000099", fg="#00ace6", height=1, width=30)
        self.nextbtn.grid(column=2, row=4, pady=30)

        self.cancel_btn = tk.Button(self, command=lambda:self.cancel(), text="Cancel", font="Times", bg="#000099", fg="#00ace6", height=1, width=5)
        self.cancel_btn.grid(column=2, row=5, pady=3)

        # Hides the cancel button once user types anything into the boxes
        def hide_cancel_button(_):
            self.cancel_btn.grid_forget()
        self.box.bind('<Key>', hide_cancel_button)

        # Used for populating territories
        self.count = 0 

    # When cancel is pressed
    def cancel(self):
        self.controller.show_frame(OptionsPage)

    # Lets the user add territories
    def set_terr(self):
        lines = self.box.get("1.0","end-1c").splitlines()
        lines = [x for x in lines if x != '']
        if len(lines) != 0:
            # Makes dict to hold territories and their states
            global territories; territories = {key: [] for key in lines}
            self.tlist = lines

            # Update screen
            self.add_states()
    
        else:
            self.instructions.config(text="Please enter at least one territory")

    # Lets the user add states
    def add_states(self):
        global territories
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
                territories[terr] = states
                # Update screen
                if self.count < len(self.tlist):
                    terr = self.tlist[self.count]
                    self.instructions.config(text="Enter states in {} territory, each on their own line".format(terr))
                # Updates the button
                if self.count == len(self.tlist) - 1:
                    self.nextbtn.config(text="Finish")
                # Last screen
                elif self.count == len(self.tlist):
                    print(territories)
                    last = True
                    self.controller.show_frame(OptionsPage)
                    TerritoriesPage.destroy(self)


        # Clear the box
        if not bad and not last:
            self.box.delete("1.0", "end")
            self.count += 1


# Page where date range for cases is set
class DateRangePage(tk.Frame):
    def __init__(self, parent, controller):
        PageLayout.__init__(self, parent)
        self.controller = controller   

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

        # Hides the cancel button once user types anything into the boxes
        def hide_cancel_button(_):
            self.cancel_btn.grid_forget()
        self.start.bind('<Key>', hide_cancel_button)
        self.end.bind('<Key>', hide_cancel_button)
       
    # When cancel is pressed
    def cancel(self):
        self.controller.resize_optionspage()
        self.controller.show_frame(OptionsPage)

    # Sets start and end dates to None, this will make sure that min and max dates used when excel sheets are made
    def all_dates(self):
        global sdate, edate
        sdate, edate = None, None
        self.controller.resize_optionspage()
        self.controller.show_frame(OptionsPage)

    # Checks to see if dates are in correct format and within range -> need to add earliest date
    def check_range(self):
            try:
                stext = self.start.get("1.0","end-1c")
                etext = self.end.get("1.0","end-1c")
                stime = datetime.datetime.strptime(stext, '%m/%d/%Y')
                etime = datetime.datetime.strptime(etext, '%m/%d/%Y')

                # If user gives start date later than end date
                if stime > etime:
                    self.instructions.config(text="Start date must be less than or equal to end date!")
                else:
                    global sdate; sdate = stime
                    global edate; edate = etime
                    self.controller.resize_optionspage()
                    self.controller.show_frame(OptionsPage)
                    DateRangePage.destroy()

            except:
                self.instructions.config(text="Check date formats and retry")


# Choose which tags to include
class TagsPage(tk.Frame):
    def __init__(self, parent, controller):
        PageLayout.__init__(self, parent)
        self.controller = controller
        self.parent = parent

        # Instructions, Tags box, buttons
        self.instructions = ttk.Label(self, text="Enter tags to include in excel sheets, each on their own line", font=("Times", 15))
        self.instructions.grid(column=1, row=1, columnspan=3, pady=10)

        self.instructions2 = ttk.Label(self, text="Only include last 3 numbers (ex: F757 -> 757)", font=("Times", 15))
        self.instructions2.grid(column=1, row=2, columnspan=3, pady=10)

        self.box = scrolledtext.ScrolledText(self, undo=True, width=40, height=10)
        self.box.grid(column=2, row=3, pady=10)
        
        self.all_btn = tk.Button(self, command=lambda:self.set_all_tags(), text="Include All Tags", font="Times", bg="#000099", fg="#00ace6", height=1, width=30)
        self.all_btn.grid(column=2, row=4, pady=15)

        self.fin_btn = tk.Button(self, command=lambda:self.set_tags(), text="Finish", font="Times", bg="#000099", fg="#00ace6", height=1, width=30)
        self.fin_btn.grid(column=2, row=5, pady=10)

        self.cancel_btn = tk.Button(self, command=lambda:self.cancel(), text="Cancel", font="Times", bg="#000099", fg="#00ace6", height=1, width=5)
        self.cancel_btn.grid(column=2, row=6, pady=3)

        # Hides the cancel button once user types anything into the box 
        def hide_cancel_button(_):
            self.cancel_btn.grid_forget()
            self.controller.resize_optionspage()
        self.box.bind('<Key>', hide_cancel_button)

        # For storing invalid tags
        self.rejected_tags = []

    # When cancel is pressed
    def cancel(self):
        self.controller.resize_optionspage()
        self.controller.show_frame(OptionsPage)

    # Lets the user add the tags
    def set_tags(self):
        notags = True
        lines = self.box.get("1.0","end-1c").splitlines()
        lines = [x.strip() for x in lines if x != '']
        
        if len(lines) != 0:
            # List to hold the tags
            global chosen_tags; chosen_tags = []
            for tag in lines:
                try:
                    tag = int(tag)
                    if tag in tag_hash.keys():
                        chosen_tags += [tag]
                        notags = False
                    else:
                        self.rejected_tags += [tag]
                except:        
                    self.rejected_tags += [tag]
                
        if notags:
            self.instructions.config(text="Please enter at least one valid tag")
            self.instructions2.grid_forget()
        else:
            self.show_tags()
    
    # For setting all tags
    def set_all_tags(self):
        global chosen_tags; chosen_tags = list(tag_hash.keys())
        self.show_tags()

    # Shows tags accepted and rejected
    def show_tags(self):
        # Hide elements
        self.all_btn.grid_forget()
        self.fin_btn.grid_forget()
        self.box.grid_forget()
        self.cancel_btn.grid_forget()
        self.instructions2.grid_forget()
        self.controller.geometry("500x600")

        # Make a string of accepted tags that will fit within the screen without stretching it
        valid_tags = ""
        invalid_tags = ""
        global chosen_tags
        for i in range(len(chosen_tags)):
            if i % 15 == 0:
                valid_tags += "\n"
            
            valid_tags += str(chosen_tags[i]) + " "

        for i in range(len(self.rejected_tags)):
            if i % 15 == 0:
                invalid_tags += "\n"
            
            invalid_tags += str(self.rejected_tags[i]) + " "

        # Makes the screen wait for 3 seconds going back to OptionsPage
        with TkWait(self.parent, 3000):
            self.instructions.config(text="Tags Accepted: ")
            self.instructions2.config(text=valid_tags)
            self.instructions2.grid(column=1, row=2, columnspan=3, pady=2)
            self.instructions3 = ttk.Label(self, text="Tags Rejected: ", font=("Times", 15))
            self.instructions3.grid(column=1, row=3, columnspan=3, pady=10)
            self.instructions4 = ttk.Label(self, text=invalid_tags, font=("Times", 15))
            self.instructions4.grid(column=1, row=4, columnspan=3, pady=10)

        self.controller.resize_optionspage()
        self.controller.show_frame(OptionsPage)
        TagsPage.destroy(self)


# Format excel sheets
class FormatPage(tk.Frame):
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
                            "Include only corrected violations":False, "Include only uncorrected violations":False,
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

        self.boxes.append(tk.Checkbutton(self.fm, text="Create sheet for only corrected violations", width=35, anchor="w", command=lambda:self.add_option("Include only corrected violations")))
        self.boxes[i].grid()
        i += 1

        self.boxes.append(tk.Checkbutton(self.fm, text="Create sheet for only uncorrected violations", width=35, anchor="w", command=lambda:self.add_option("Include only uncorrected violations")))
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


    # Once user is done selecting options
    def finish(self):
        global options; options = self.options
        self.controller.resize_optionspage()
        self.controller.show_frame(OptionsPage)
        for button in self.boxes:
            button.destroy()
        self.fm.destroy()
        FormatPage.destroy(self)

    # Add a chosen option to a list
    def add_option(self, opt):
        self.options[opt] = not self.options[opt]

    # Select all button functionality
    def select_all(self):
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


# Page where excel sheet is made
class ExcelPage(tk.Frame):
    def __init__(thisframe, parent, controller):
        PageLayout.__init__(thisframe, parent)
        thisframe.controller = controller

        # Instructions and Make sheets button
        thisframe.instructions = ttk.Label(thisframe, text="Press button to choose where to save excel sheets", font=("Times", 15))
        thisframe.instructions.grid(column=1, row=2, columnspan=3, pady=10)

        thisframe.instructions2 = ttk.Label(thisframe, text="Sheet creation will start", font=("Times", 15))
        thisframe.instructions2.grid(column=1, row=3, columnspan=3, pady=10)
    
        thisframe.sheet_btn = tk.Button(thisframe, command=lambda:thisframe.make_sheets(), text="Make Sheets", font="Times", bg="#000099", fg="#00ace6", height=1, width=30)
        thisframe.sheet_btn.grid(column=2, row=4, pady=40)

        thisframe.cancel_btn = tk.Button(thisframe, command=lambda:thisframe.cancel(), text="Go Back", font="Times", bg="#000099", fg="#00ace6", height=1, width=5)
        thisframe.cancel_btn.grid(column=2, row=5, pady=3)

    # Lets a user go back to OptionsPage
    def cancel(thisframe):
        thisframe.controller.resize_optionspage()
        thisframe.controller.show_frame(OptionsPage)

    # Uses threads to make excel sheets -> need to first break data up by territory
    def make_sheets(thisframe):

        outpath = askdirectory()
        with open(home_folder_path + "dataframes/df.pkl", 'rb') as inp:
            df = pickle.load(inp)  

        # Create a thread to run make_sheets() so we can update the screen
        class thread(threading.Thread):
            def __init__(self, func):
                threading.Thread.__init__(self)
                self.func = func
        
            def run(self):
                global options, sdate, edate, territories, chosen_tags
                self.func(thisframe, options, df, sdate, edate, territories, chosen_tags, outpath)

        thisframe.cancel_btn.grid_forget()
        thread(util.make_sheets).start()

    # Once sheets are made
    def finish(thisframe):
        thisframe.controller.show_frame(DonePage)


# After excel sheets are made
class DonePage(tk.Frame):
    def __init__(self, parent, controller):
        PageLayout.__init__(self, parent)
        self.controller = controller

        # Instructions
        self.instructions = ttk.Label(self, text="Program finished", font=("Times", 15))
        self.instructions.grid(column=1, row=2, columnspan=3, pady=10)

        self.sheet_btn = tk.Button(self, command=lambda:self.exit(), text="Exit Program", font="Times", bg="#000099", fg="#00ace6", height=1, width=30)
        self.sheet_btn.grid(column=2, row=3, pady=40)

    def exit(self):
        app.quit()
    

if __name__ == '__main__':
    # Driver Code
    app = tkinterApp()
    app.mainloop()
