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
import warnings
warnings.filterwarnings('ignore')

# Set up paths for either local testing or a production executable
PRODUCTION = True
OPTIONS_PAGE_SIZE = "500x320"
if PRODUCTION:
    TAG_HASH_PATH = "assets/tag_hash.pkl"
    ICON_PATH = "images/icon.ico"
    LOGO_PATH  = "images/logo.png"
else:
    TAG_HASH_PATH = "../assets/tag_hash.pkl"
    ICON_PATH = "../images/icon.ico"
    LOGO_PATH  = "../images/logo.png"


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
        global ICON_PATH, TAG_HASH_PATH
        # Contains tags and their descriptions
        with open(util.resource_path(TAG_HASH_PATH), 'rb') as inp:
            self.tag_hash = pickle.load(inp)
         
        # __init__ function for class Tk
        tk.Tk.__init__(self, *args, **kwargs)
        self.title("Violation Tool")
        self.iconbitmap(util.resource_path(ICON_PATH))
    
        # Prevents user from stretching screen
        global OPTIONS_PAGE_SIZE
        self.resizable(width=False, height=False)
        self.geometry(OPTIONS_PAGE_SIZE)

        # Will create a folder at the User's home folder for this programs data
        self.download = self.setup_savedata()
         
        # creating a container
        self.container = tk.Frame(self) 
        self.container.pack(side = "top", fill = "both", expand = True)
        self.container.grid_rowconfigure(0, weight = 1)
        self.container.grid_columnconfigure(0, weight = 1)
  
        # Initializing frames to an empty dict so that we can access pages by their name
        self.frames = {}
        self.add_frames([StartPage, MainOptionsPage])
        self.show_frame(StartPage)

        self.startdate: datetime = None
        self.enddate: datetime = None
        self.lower_stars: float = None
        self.higher_stars:float = None
        self.lower_beds: int = None
        self.higher_beds: int = None
        self.tags: List[str] = []
        self.territories: dict[str, list[str]] = {}
        self.options = {} # Formatting options for the different data categories

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
        ''' Creates a folder for this program's data. Will return True if data needs to be downloaded,
            False if data is already present. '''
        abs_home = os.path.abspath(os.path.expanduser("~"))
        self.home_folder_path = abs_home + "/ViolationToolv2/"

        # Create all folders if they don't already exist
        if not os.path.exists(self.home_folder_path):
            os.mkdir(self.home_folder_path)
        
        # Make all necessary folders
        folders = ["assets", "rawdata", "dataframes"]
        for folder in folders:
            if not os.path.exists(self.home_folder_path + folder):
                os.mkdir(self.home_folder_path + folder)

        # Force a download of data for first time
        if not os.path.exists(self.home_folder_path + "assets/lastupdate.pkl"):
            with open(self.home_folder_path + "assets/lastupdate.pkl", 'wb') as outp:
                pickle.dump("NA", outp, pickle.HIGHEST_PROTOCOL)
            return True
        return False
    
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

    def set_star_range(self, lower_stars, higher_stars):
        ''' Save star range for home health care quality_of_patient_care_star_rating measure. '''
        self.lower_stars = lower_stars
        self.higher_stars = higher_stars

    def set_bed_range(self, lower_beds, higher_beds):
        ''' Save bed range for long term care hospital number of beds. '''
        self.lower_beds = lower_beds
        self.higher_beds = higher_beds



class PageLayout(tk.Frame):
    ''' Default page layout. '''
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        # Logo
        global LOGO_PATH
        logo = Image.open(util.resource_path(LOGO_PATH))
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

        if thisframe.controller.download: # If no data has been saved yet, force a download
            thisframe.download_data()


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
        
        thisframe.controller.resize_optionspage()
        thisframe.controller.show_frame(MainOptionsPage)



class MainOptionsPage(tk.Frame):
    ''' Shows users options for the datasets. '''
    def __init__(self, parent, controller):
        PageLayout.__init__(self, parent)
        self.controller = controller

        # Instructions, Buttons for options
        self.instructions = ttk.Label(self, text="Choose your options", font=("Times", 15))
        self.instructions.grid(column=1, row=1, columnspan=3, pady=30)

        labels = ["Set Territories", "Set Date Range", "Format Nursing Home Data", "Format Home Health Data",
        "Format Long Term Care Hospital Data", "Make Sheets"]
        pages = [TerritoriesPage, DateRangePage, nursing_home_gui.OptionsPage, home_health_gui.OptionsPage,
        long_term_care_gui.OptionsPage, SheetsPage]
        for idx, page in enumerate(pages):
            button = tk.Button(self, command=(lambda x=page: self.show_page(x)), text=labels[idx], font="Times", bg="#000099", fg="#00ace6", height=1, width=30)
            button.grid(column=2, row=idx+2, pady=15)


    def show_page(self, page):
        ''' Show the appropriate page after a button is pressed. '''
        self.controller.add_frames([page])
        self.controller.show_frame(page)



class TerritoriesPage(tk.Frame):
    ''' Page where states in each territory are set. '''
    def __init__(self, parent, controller):
        PageLayout.__init__(self, parent)
        self.controller: tkinterApp = controller

        # Instructions, Territory box and Next button 
        self.instructions = ttk.Label(self, text="Enter territory names, each on their own line", font=("Times", 15))
        self.instructions.grid(column=1, row=1, columnspan=3, pady=20)

        self.instructions2 = ttk.Label(self, text="", font=("Times", 15))
        self.instructions2.grid(column=1, row=2, columnspan=3, pady=20)

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
        self.instructions = ttk.Label(self, text="Choose range of dates to include in sheets", font=("Times", 15))
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
        ''' Sets start and end dates to None, this will make sure that min and max dates used when sheets are made. '''
        self.controller.add_dates(None, None)
        print("All Dates in dataset chosen by user")
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
                print(f"Chosen Date Range: {stext}-{etext}")
                self.controller.resize_optionspage()
                self.controller.show_frame(MainOptionsPage)
                DateRangePage.destroy()

        except:
            self.instructions.config(text="Check date formats and retry")



class SheetsPage(tk.Frame):
    ''' Page where sheets are made. '''
    def __init__(thisframe, parent, controller):
        PageLayout.__init__(thisframe, parent)
        thisframe.controller: tkinterApp = controller

        # Instructions and Make sheets button
        thisframe.instructions = ttk.Label(thisframe, text="Press button to choose where to save sheets", font=("Times", 15))
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
        ''' Uses threads to make sheets for each dataset. Passes main dataframe for each dataset
            to respective make_sheets function. '''
        outpath = askdirectory()
        if outpath == "":
            print(f"No save location chosen: saving to {controller.home_folder_path}")
            outpath = controller.home_folder_path
        else:
            print(f"Save path chosen: {outpath}")

        # Make a folder for the sheets
        outpath = outpath + "/ViolationToolSheets/"
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
    ''' After sheets are made. '''
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
