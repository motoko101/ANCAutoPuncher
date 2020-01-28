import tkinter as tk

from data_management import data_storage
from PunchPage       import PunchPage
from RunPage         import RunPage
from ProcessPage     import ProcessPage
from Navigation      import Navigation
from MessageBox      import MessageBox

class MainApplication(tk.Frame):
    """
    Main application frame.
    """
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self,parent,*args,**kwargs)
        self.parent = parent
        self.grandpa = self.parent
        self.parent.title("ANC AUTO PUNCHER")
        
        # The data dump is assigned to the root.
        # Root will be always referenced to as grandpa
        parent.ds = data_storage(self)
        
        # Determine the width and height of the main window
        self.w = self.parent.winfo_screenwidth() * 0.5
        self.h = self.parent.winfo_screenheight() * 0.5
        if (self.w < 750):
            self.w = 800
        # Set the window size
        self.parent.geometry(("%dx%d")%(self.w,self.h))
        
        self.parent.resizable(width=False, height=False)
        
        # Create a dictionary of main windows and populate
        self.main = {}
        for page in (PunchPage, RunPage, ProcessPage):
            self.main[page.__name__] = page(self,width = self.w/8*7, height = self.h/4*3)
            self.main[page.__name__].grid(row = 0, column = 1, sticky = "wens")
            self.main[page.__name__].grid_propagate(0)

        self.main["PunchPage"].tkraise()
        
        self.msgb = MessageBox(self,width = self.w, height = self.h/4, bg='lavender')
        self.navg = Navigation(self,controller=self,width = self.w/8, height = self.h/4*3, bg='white')

        # Layout all the main containers
        self.grid_rowconfigure(0, weight = 0)
        self.grid_rowconfigure(1, weight = 0)
        self.grid_columnconfigure(0, weight = 0)
        self.grid_columnconfigure(1, weight = 0)

        self.msgb.grid(row = 1, columnspan = 2, sticky = "wnse")
        self.navg.grid(row = 0, column = 0, sticky = "wnse")
         
        self.msgb.grid_propagate(0)
        self.navg.grid_propagate(0)

        self.msgb.insert_text("Welcome to ANC AUTO PUNCHER!")
        self.msgb.insert_text("\nSet inputs, choose an analysis from the drop down menu and get punching!")
        self.grid()

        self.grandpa.msgb = self.msgb
    
    # define a function to raise a selected main page
    def show_page(self, page_name):
        self.main[page_name].event_generate("<<ShowFrame>>")
        self.main[page_name].tkraise()