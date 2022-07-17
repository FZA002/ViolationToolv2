import tkinter as tk
from tkinter import ttk
import gui, pickle


class OptionsPage(tk.Frame):
    ''' Shows users options for the dataset. '''
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



class FormatPage(tk.Frame):
    ''' Format excel sheets for home health. '''
    def __init__(self, parent, controller):
        gui.PageLayout.__init__(self, parent)
        self.controller: gui.tkinterApp = controller

        # Instructions
        self.instructions = ttk.Label(self, text="Choose which data to include", font=("Times", 15))
        self.instructions.grid(column=1, row=2, columnspan=3, pady=10)
        
        self.fm_width = 70
        self.fm = ttk.Labelframe(self, width=self.fm_width, border=0) # Frame to hold the buttons and list to access them directly
        self.fm.grid(column=2, row=4)
        self.options = {} # bools for options
        self.option_buttons = {} # Holds option buttons
        self.make_option_buttons() # Load option buttons

        # More Buttons
        self.all_btn = tk.Button(self, command=lambda:self.select_all(), text="Select All", font="Times", bg="#000099", fg="#00ace6", height=1, width=30)
        self.all_btn.grid(column=2, row=5, pady=15)
        self.all = False

        self.fin_btn = tk.Button(self, command=lambda:self.finish(), text="Finish", font="Times", bg="#000099", fg="#00ace6", height=1, width=30)
        self.fin_btn.grid(column=2, row=6, pady=5)

        # Sets all boxes to have no checkmark - need this so a user can click back in 
        for option in self.option_buttons:
            self.option_buttons[option].deselect()

    def finish(self):
        ''' Once user is done selecting options. '''
        self.controller.options["Home Health"] = self.options
        self.controller.resize_optionspage()
        self.controller.show_frame(OptionsPage)
        print(f"Chosen Home Health Options: {self.controller.options['Home Health']}")
        for option in self.option_buttons:
            self.option_buttons[option].destroy()
        self.fm.destroy()
        FormatPage.destroy(self)

    def add_option(self, opt: str):
        ''' # Add a chosen option to a list. '''
        self.options[opt] = not self.options[opt]

    def select_all(self):
        ''' Select all button functionality. '''
        if self.all:    
            self.options = {k: False for k, _ in self.options.items()}
            for option in self.option_buttons:
                self.option_buttons[option].deselect()   
            self.all = False
            self.all_btn.config(text="Select All")   
        else:         
            self.options = {k: True for k, _ in self.options.items()}
            for option in self.option_buttons:
                self.option_buttons[option].select()
            self.all = True
            self.all_btn.config(text="Unselect All")

    def make_option_buttons(self):
        ''' Create buttons that allow the user to exclude certain ownership types from the excel data. '''
        option = 'State Statistics'
        self.options[option] = False
        self.option_buttons[option] = tk.Checkbutton(self.fm, width=self.fm_width, text="Include State Statistics", anchor="w", command=lambda x=option: self.add_option(x), font=("Times", 12))
        self.option_buttons[option].grid()

        with open(self.controller.home_folder_path + "dataframes/hhc_df.pkl", 'rb') as inp:
            hhq = pickle.load(inp)
         
        ownership_types = list(hhq['type_of_ownership'].unique()) # List of the different ownership types organizations can have
        ownership_types.remove("-")
        ownership_types.append("Undefined") # This represents "-" ownership type

        # Make a button to exclude each type of ownership and add it to options
        for type in ownership_types:
            self.option_buttons[type] = tk.Checkbutton(self.fm, width=self.fm_width, text=f"Exclude {type} orgs", anchor="w", command=(lambda x=type: self.add_option(x)), font=("Times", 12))
            self.options[type] = False
            self.option_buttons[type].grid()

