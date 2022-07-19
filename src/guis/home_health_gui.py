import tkinter as tk
from tkinter import ttk
import gui, pickle


class OptionsPage(tk.Frame):
    ''' Shows users options for the dataset. '''
    def __init__(self, parent, controller):
        gui.PageLayout.__init__(self, parent)
        self.controller: gui.tkinterApp = controller

        # Instructions, Buttons for options
        self.instructions = ttk.Label(self, text="Choose your options for Home Health Care Data", font=("Times", 15))
        self.instructions.grid(column=1, row=1, columnspan=3, pady=30)

        buttons = ["Choose Star Range", "Format Excel Data", "Done"]
        pages = [StarRangePage, FormatPage, gui.MainOptionsPage]
        for idx, page in enumerate(pages):
            button = tk.Button(self, command=(lambda x=page: self.show_page(x)), text=buttons[idx], font="Times", bg="#000099", fg="#00ace6", height=1, width=30)
            button.grid(column=2, row=idx+2, pady=30)


    def show_page(self, page):
        ''' Show the appropriate page after a button is pressed. '''
        self.controller.resize_optionspage()
        self.controller.add_frames([page])
        self.controller.show_frame(page)



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
        options = ['State Statistics', 'Measure Averages per Organization', 'Sheet With All Territories Combined', 'Sheet For All Violations in the Dataset Without Territories']
        for option in options:
            self.options[option] = False
            self.option_buttons[option] = tk.Checkbutton(self.fm, width=self.fm_width, text=f"Include {option}", anchor="w", command=lambda x=option: self.add_option(x), font=("Times", 12))
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



class StarRangePage(tk.Frame):
    ''' Define a range for quality_of_patient_care_star_rating to be shown in the end excel sheets.
        Will apply to the whole Home Health dataset. '''
    def __init__(self, parent, controller):
        gui.PageLayout.__init__(self, parent)
        self.controller: gui.tkinterApp = controller

        # Instructions
        self.instructions = ttk.Label(self, text="Choose a range (0-5) for the \"quality_of_patient_care_star_rating\"", font=("Times", 15))
        self.instructions.grid(column=1, row=1, columnspan=3, pady=10)

        self.instructions2 = ttk.Label(self, text="This range will be applied to the whole dataset!", font=("Times", 15))
        self.instructions2.grid(column=1, row=2, columnspan=3, pady=10) 

        self.instructions3 = ttk.Label(self, text="Lowest Star Rating Acceptable", font=("Times", 15))
        self.instructions3.grid(column=1, row=3, columnspan=3, pady=10)

        self.instructions4 = ttk.Label(self, text="Highest Star Rating Acceptable", font=("Times", 15))
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
        ''' Checks to see if stars are in correct format and within range. '''
        try:
            lower_stars = self.start.get("1.0","end-1c")
            higher_stars = self.end.get("1.0","end-1c")
            lower_stars = float(lower_stars)
            higher_stars = float(higher_stars)

            # If user gives start date later than end date
            if lower_stars > higher_stars:
                self.instructions.config(text="Lower stars must be greater than or equal to higher stars!")
            elif lower_stars < 0 or higher_stars > 5:
                self.instructions.config(text="Range must be with 0 to 5 stars!")
            else:
                self.controller.set_star_range(lower_stars, higher_stars)
                self.controller.resize_optionspage()
                self.controller.show_frame(OptionsPage)
                print(f"Chosen Star Range: {self.controller.lower_stars}-{self.controller.higher_stars}")
                StarRangePage.destroy()

        except:
            self.instructions.config(text="Make sure valid decimals have been used!")
        