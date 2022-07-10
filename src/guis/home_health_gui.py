import tkinter as tk
from tkinter import Checkbutton, ttk
import gui, pickle

# Shows users options for the dataset
class OptionsPage(tk.Frame):
    def __init__(self, parent, controller):
        gui.PageLayout.__init__(self, parent)
        self.controller: gui.tkinterApp = controller

        # Instructions, Buttons for options
        option_count = 1
        self.instructions = ttk.Label(self, text="Choose your options for Home Health Care Data", font=("Times", 15))
        self.instructions.grid(column=1, row=option_count, columnspan=3, pady=15)
        option_count += 1 

        self.instructions2 = ttk.Label(self, text="", font=("Times", 15))
        self.instructions2.grid(column=1, row=option_count, columnspan=3)
        option_count += 1 

        self.excel_btn = tk.Button(self, command=lambda:self.show_format(), text="Format Excel Data", font="Times", bg="#000099", fg="#00ace6", height=1, width=30)
        self.excel_btn.grid(column=2, row=option_count, pady=30)
        option_count += 1

        self.done_btn = tk.Button(self, command=lambda:self.show_main_options(), text="Done", font="Times", bg="#000099", fg="#00ace6", height=1, width=30)
        self.done_btn.grid(column=2, row=option_count, pady=30)
        option_count += 1

    # Functions to show appropriate screens and disable buttons after press    
    def show_format(self):
        self.controller.resize_optionspage()
        self.controller.add_frames([FormatPage])
        self.controller.show_frame(FormatPage)

    def show_main_options(self):
        self.controller.resize_optionspage()
        self.controller.add_frames([gui.MainOptionsPage])
        self.controller.show_frame(gui.MainOptionsPage)


# Format excel sheets
class FormatPage(tk.Frame):
    def __init__(self, parent, controller):
        gui.PageLayout.__init__(self, parent)
        self.controller: gui.tkinterApp = controller

        # Instructions
        self.instructions = ttk.Label(self, text="Choose which data to include", font=("Times", 15))
        self.instructions.grid(column=1, row=2, columnspan=3, pady=10)
        
        # Holds buttons
        self.options = {"State Statistics":False}

        # Frame to hold the buttons and list to access them directly
        self.fm = ttk.Labelframe(self, width=50, border=0)
        self.fm.grid(column=2, row=4)
        self.boxes = {}
        
        # Buttons
        option = 'State Statistics'
        self.boxes[option] = tk.Checkbutton(self.fm, width=35, text="Include State Statistics", anchor="w", command=lambda x=option: self.add_option(x))
        self.boxes[option].grid()

        # Load ownership type buttons
        self.make_ownership_type_buttons()

        # Butttons
        self.all_btn = tk.Button(self, command=lambda:self.select_all(), text="Select All", font="Times", bg="#000099", fg="#00ace6", height=1, width=30)
        self.all_btn.grid(column=2, row=5, pady=15)
        self.all = False

        self.fin_btn = tk.Button(self, command=lambda:self.finish(), text="Finish", font="Times", bg="#000099", fg="#00ace6", height=1, width=30)
        self.fin_btn.grid(column=2, row=6, pady=5)

        # Sets all boxes to have no checkmark - need this so a user can click back in 
        for option in self.boxes:
            self.boxes[option].deselect()


    # Once user is done selecting options
    def finish(self):
        self.controller.options["Home Health"] = self.options
        self.controller.resize_optionspage()
        self.controller.show_frame(OptionsPage)
        print(f"Chosen Home Health Options: {self.controller.options['Home Health']}")
        for option in self.boxes:
            self.boxes[option].destroy()
        self.fm.destroy()
        FormatPage.destroy(self)

    # Add a chosen option to a list
    def add_option(self, opt):
        self.options[opt] = not self.options[opt]

    # Select all button functionality
    def select_all(self):
        if self.all:    
            self.options = {k: False for k, _ in self.options.items()}
            for option in self.boxes:
                self.boxes[option].deselect()   
            self.all = False
            self.all_btn.config(text="Select All")   
        else:         
            self.options = {k: True for k, _ in self.options.items()}
            for option in self.boxes:
                self.boxes[option].select()
            self.all = True
            self.all_btn.config(text="Unselect All")

    def make_ownership_type_buttons(self):
        ''' Create buttons that allow the user to exclude certain ownership types from the excel data. '''
        with open(self.controller.home_folder_path + "dataframes/hhc_df.pkl", 'rb') as inp:
            hhq = pickle.load(inp)
         
        ownership_types = list(hhq['type_of_ownership'].unique())
        ownership_types.remove("-")

        # Make a button to exclude each type of ownership and add it to options
        for type in ownership_types:
            self.boxes[type] = tk.Checkbutton(self.fm, width=35, text=f"Exclude {type} orgs", anchor="w", command=(lambda x=type: self.add_option(x)))
            self.options[type] = False 
            self.boxes[type].grid()

