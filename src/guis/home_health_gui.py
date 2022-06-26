import tkinter as tk
from tkinter import ttk
import gui

# Shows users options for the dataset
class OptionsPage(tk.Frame):
    def __init__(self, parent, controller):
        gui.PageLayout.__init__(self, parent)
        self.controller = controller

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


    # Once user is done selecting options
    def finish(self):
        gui.options = self.options
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
