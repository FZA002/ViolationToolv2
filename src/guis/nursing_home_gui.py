import tkinter as tk
from tkinter import ttk, scrolledtext
import gui


class OptionsPage(tk.Frame):
    ''' Shows users options for the dataset. '''
    def __init__(self, parent, controller):
        gui.PageLayout.__init__(self, parent)
        self.controller = controller

        # Instructions, Buttons for options
        option_count = 1
        self.instructions = ttk.Label(self, text="Choose your options for Nursing Home Data", font=("Times", 15))
        self.instructions.grid(column=1, row=option_count, columnspan=3, pady=15)
        option_count += 1 

        self.instructions2 = ttk.Label(self, text="", font=("Times", 15))
        self.instructions2.grid(column=1, row=option_count, columnspan=3)
        option_count += 1 

        self.tag_btn = tk.Button(self, command=lambda:self.show_tags(), text="Choose Tags to Include", font="Times", bg="#000099", fg="#00ace6", height=1, width=30)
        self.tag_btn.grid(column=2, row=option_count, pady=30)
        option_count += 1

        self.excel_btn = tk.Button(self, command=lambda:self.show_format(), text="Format Excel Data", font="Times", bg="#000099", fg="#00ace6", height=1, width=30)
        self.excel_btn.grid(column=2, row=option_count, pady=30)
        option_count += 1

        self.done_btn = tk.Button(self, command=lambda:self.show_main_options(), text="Done", font="Times", bg="#000099", fg="#00ace6", height=1, width=30)
        self.done_btn.grid(column=2, row=option_count, pady=30)
        option_count += 1

    # Functions to show appropriate screens and disable buttons after press    
    def show_tags(self):
        self.controller.add_frames([TagsPage])
        self.controller.geometry("500x520")
        self.controller.show_frame(TagsPage)

    def show_format(self):
        self.controller.resize_optionspage()
        self.controller.add_frames([FormatPage])
        self.controller.show_frame(FormatPage)

    def show_main_options(self):
        self.controller.resize_optionspage()
        self.controller.add_frames([gui.MainOptionsPage])
        self.controller.show_frame(gui.MainOptionsPage)



class TagsPage(tk.Frame):
    ''' Choose which tags to include. '''
    def __init__(self, parent, controller):
        gui.PageLayout.__init__(self, parent)
        self.controller: gui.tkinterApp = controller
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

        
        def hide_cancel_button(_):
            ''' Hides the cancel button once user types anything into the box. '''
            self.cancel_btn.grid_forget()
            self.controller.resize_optionspage()
        self.box.bind('<Key>', hide_cancel_button)

        # For storing invalid tags
        self.rejected_tags = []


    def cancel(self):
        ''' When cancel is pressed. '''
        self.controller.resize_optionspage()
        self.controller.show_frame(OptionsPage)

    
    def set_tags(self):
        ''' Lets the user add the tags. '''
        notags = True
        lines = self.box.get("1.0","end-1c").splitlines()
        lines = [x.strip() for x in lines if x != '']
        print(f"User input: {lines}")
        
        if len(lines) != 0:
            # List to hold the tags
            chosen_tags = []
            for tag in lines:
                try:
                    tag = int(tag)
                    if tag in self.controller.tag_hash.keys():
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
            self.controller.add_tags(chosen_tags)
            self.show_tags()
    

    def set_all_tags(self):
        ''' For setting all tags. '''
        self.controller.add_tags(list(self.controller.tag_hash.keys()))
        self.show_tags()


    def show_tags(self):
        ''' Shows tags accepted and rejected. '''
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
        for i in range(len(self.controller.tags)):
            if i % 15 == 0:
                valid_tags += "\n"
            
            valid_tags += str(self.controller.tags[i]) + " "

        for i in range(len(self.rejected_tags)):
            if i % 15 == 0:
                invalid_tags += "\n"
            
            invalid_tags += str(self.rejected_tags[i]) + " "

        # Makes the screen wait for 3 seconds going back to OptionsPage
        with gui.TkWait(self.parent, 3000):
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



class FormatPage(tk.Frame):
    ''' Format excel sheets for nursing homes. '''
    def __init__(self, parent, controller):
        gui.PageLayout.__init__(self, parent)
        self.controller = controller

        # Instructions
        self.instructions = ttk.Label(self, text="Choose which data to include", font=("Times", 15))
        self.instructions.grid(column=1, row=2, columnspan=3, pady=10)
        
        self.instructions2 = ttk.Label(self, text="Will include dates and tag filters or defaults if none are selected", font=("Times", 15))
        self.instructions2.grid(column=1, row=3, columnspan=3, pady=10)

        # Frame to hold the buttons and list to access them directly
        self.fm = ttk.Labelframe(self, width=50, border=0)
        self.fm.grid(column=2, row=4)
        self.options = {} # bools for options
        self.option_buttons = {} # Holds option buttons
        self.make_option_buttons() # Load option buttons
        
        # Butttons
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
        self.controller.options["Nursing Home"] = self.options
        self.controller.resize_optionspage()
        self.controller.show_frame(OptionsPage)
        print(f"Chosen Nursing Home Options: {self.controller.options['Nursing Home']}")
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
        ''' Create buttons that allow the user to exclude include certain extra data. '''
        options = ["US Fines (Total, yearly)", "US Violations (Total, yearly)", "Top fined organizations (Total, yearly)", 
                    "Most severe organizations (Total, yearly)", "Sum of fines per state (Total, yearly)",
                    "Sum of violations per state (Total, yearly)", "Sum of fines per tag (Total, yearly)",
                    "Sum of violations per tag (Total, yearly)", "Create sheet with all territories combined",
                    "Create sheet for all violations without territories"]
        
        # Make a button for each option and add it to options
        for option in options:
            self.options[option] = False
            self.option_buttons[option] = tk.Checkbutton(self.fm, width=35, text=option, anchor="w", command=lambda x=option: self.add_option(x))
            self.option_buttons[option].grid()
