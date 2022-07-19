import tkinter as tk
from tkinter import ttk
import gui, pickle, pandas as pd


class OptionsPage(tk.Frame):
    ''' Shows users options for the dataset. '''
    def __init__(self, parent, controller):
        gui.PageLayout.__init__(self, parent)
        self.controller: gui.tkinterApp = controller

        # Instructions, Buttons for options
        self.instructions = ttk.Label(self, text="Choose your options for Long Term Care Hospital Data", font=("Times", 15))
        self.instructions.grid(column=1, row=1, columnspan=3, pady=30)

        labels = ["Set Bed Range", "Format Excel Data", "Done"]
        pages = [BedRangePage, FormatPage, gui.MainOptionsPage]
        for idx, page in enumerate(pages):
            button = tk.Button(self, command=(lambda x=page: self.show_page(x)), text=labels[idx], font="Times", bg="#000099", fg="#00ace6", height=1, width=30)
            button.grid(column=2, row=idx+2, pady=30)
            

    def show_page(self, page):
        ''' Show the appropriate page after a button is pressed. '''
        self.controller.resize_optionspage()
        self.controller.add_frames([page])
        self.controller.show_frame(page)



class BedRangePage(tk.Frame):
    ''' Lets user set a range for the number of beds an organization must have to be included in the excel sheets. '''
    def __init__(self, parent, controller):
        gui.PageLayout.__init__(self, parent)
        self.controller: gui.tkinterApp = controller

    # Instructions
        self.instructions = ttk.Label(self, text="Choose a range for # of beds an organization must have to be included", font=("Times", 15))
        self.instructions.grid(column=1, row=1, columnspan=3, pady=10)

        self.instructions2 = ttk.Label(self, text="This range will be applied to the whole dataset!", font=("Times", 15))
        self.instructions2.grid(column=1, row=2, columnspan=3, pady=10) 

        self.instructions3 = ttk.Label(self, text="Lowest Number of Beds Acceptable", font=("Times", 15))
        self.instructions3.grid(column=1, row=3, columnspan=3, pady=10)

        self.instructions4 = ttk.Label(self, text="Highest Number of Beds Acceptable", font=("Times", 15))
        self.instructions4.grid(column=1, row=5, columnspan=3, pady=10)

        self.start = tk.Text(self, height=2, width=25)
        self.start.grid(column=2, row=4, pady=10)

        self.end = tk.Text(self, height=2, width=25)
        self.end.grid(column=2, row=6, pady=10)

        self.fin_btn = tk.Button(self, command=lambda:self.check_range(), text="Finish", font="Times", bg="#000099", fg="#00ace6", height=1, width=30)
        self.fin_btn.grid(column=2, row=7, pady=20)
       
        self.cancel_btn = tk.Button(self, command=lambda:self.cancel(), text="Cancel", font="Times", bg="#000099", fg="#00ace6", height=1, width=5)
        self.cancel_btn.grid(column=2, row=8, pady=3)

        
        def hide_cancel_button(_):
            ''' Hides the cancel button once user types anything into the boxes. '''
            self.cancel_btn.grid_forget()
        self.start.bind('<Key>', hide_cancel_button)
        self.end.bind('<Key>', hide_cancel_button)


    def cancel(self):
        ''' When cancel is pressed. '''
        self.controller.resize_optionspage()
        self.controller.show_frame(OptionsPage)

    def check_range(self):
        ''' Checks to see if beds are in correct format and within range. '''
        try:
            lower_beds = self.start.get("1.0","end-1c")
            higher_beds = self.end.get("1.0","end-1c")
            lower_beds = int(lower_beds)
            higher_beds = int(higher_beds)

            if lower_beds > higher_beds:
                self.instructions.config(text="Lower number of beds must be greater than or equal to higher number of beds!")
            elif lower_beds < 0:
                self.instructions.config(text="Lower number of beds cannot be less than 0!")
            else:
                self.controller.set_bed_range(lower_beds, higher_beds)
                self.controller.resize_optionspage()
                self.controller.show_frame(OptionsPage)
                print(f"Chosen Bed Range: {self.controller.lower_beds}-{self.controller.higher_beds}")
                BedRangePage.destroy()

        except:
            self.instructions.config(text="Make sure valid whole numbers have been used!")



class FormatPage(tk.Frame):
    ''' Format excel sheets. '''
    def __init__(self, parent, controller):
        gui.PageLayout.__init__(self, parent)
        self.controller: gui.tkinterApp = controller

        # Instructions
        self.instructions = ttk.Label(self, text="Choose excel formatting options", font=("Times", 15))
        self.instructions.grid(column=1, row=2, columnspan=3, pady=10)
        
        self.fm_width = 35
        self.fm = ttk.Labelframe(self, width=self.fm_width, border=0) # Frame to hold the buttons and list to access them directly
        self.fm.grid(column=2, row=4)
        self.options, self.option_buttons = {}, {} # bools for options, holds options buttons
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
        self.controller.options["Long Term"] = self.options
        self.controller.resize_optionspage()
        self.controller.show_frame(OptionsPage)
        for option in self.option_buttons:
            self.option_buttons[option].destroy()
        self.fm.destroy()
        FormatPage.destroy(self)

    def add_option(self, opt):
        ''' Add a chosen option to a list. '''
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
        options = []
        for option in options:
            self.options[option] = False
            self.option_buttons[option] = tk.Checkbutton(self.fm, width=self.fm_width, text=f"Include {option}", anchor="w", command=lambda x=option: self.add_option(x), font=("Times", 15))
            self.option_buttons[option].grid()

        with open(self.controller.home_folder_path + "dataframes/ltch_df.pkl", 'rb') as inp:
            ltc = pickle.load(inp)
         
        ownership_types = list(ltc['ownership_type'].unique()) # List of the different ownership types organizations can have
        ownership_types = [type for type in ownership_types if not pd.isnull(type)] # Remove nan from the list and replace with "Undefined"
        ownership_types.append('Undefined')
        ownership_types.append('Mobile') # Not an ownership type, but an option to exclude

        # Make a button to exclude each type of ownership and add it to options
        for type in ownership_types:
            self.option_buttons[type] = tk.Checkbutton(self.fm, width=self.fm_width, text=f"Exclude {type} organizations", anchor="w", command=(lambda x=type: self.add_option(x)), font=("Times", 15))
            self.options[type] = False
            self.option_buttons[type].grid()
