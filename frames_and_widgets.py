import tkinter as tk
from tkinter import filedialog
from tkinter.scrolledtext import ScrolledText
from PIL import ImageTk, Image
from data_management import *
from RSACpunch import puncher

def browse_func(x):
    filename = filedialog.askopenfilename()
    x.delete(0,tk.END)
    x.insert(0,filename)

def punch(self):
    # define what happens when the punch button is pressed
    # 1. Collect data from entries (stored in ds which is an instance of data_storage
    # 2. Check validity
    # 3. Ask for more data if needed depending on analysis of choice
    
    # Echo input in the message box
    text = "\n********************\n The following input parameters were set:"
    self.parent.parent.parent.msgb.insert_text(text)
    
    text = str("\nARO file: "+self.grandpa.ds.aro_dep_file.get())
    self.parent.parent.parent.msgb.insert_text(text)
    
    text = str("\nDin file: "+self.grandpa.ds.din_dep_file.get())
    self.parent.parent.parent.msgb.insert_text(text)
    
    text = str("\nPlant ID: "+self.grandpa.ds.plant_id.get())
    self.parent.parent.parent.msgb.insert_text(text)
    
    text = str("\nBurnup window: "+self.grandpa.ds.window.get())
    self.parent.parent.parent.msgb.insert_text(text)
    
    text = str("\nJob ID: "+self.grandpa.ds.job_id.get())
    self.parent.parent.parent.msgb.insert_text(text)
    
    text = str("\nAnalysis: "+self.grandpa.ds.choice.get())
    self.parent.parent.parent.msgb.insert_text(text)
    
    # Match the analysis of choice with the keys
    # Call the selector function
    self.anal = select_analysis(choice=self.grandpa.ds.choice.get())
    
    
    if self.anal == None:
        text = str("\n ********************\n No analysis was selected!")
        self.parent.parent.parent.msgb.insert_text(text)
    else:
        puncher(ds=self.grandpa.ds,analysis=self.anal)
        text, self.punchpath = puncher(ds=self.grandpa.ds,analysis=self.anal)
        self.parent.parent.parent.msgb.insert_text(text)
        self.grandpa.ds.punched_files.append(self.punchpath)
    
    
class PunchButtton(tk.Button):
        def __init__(self,parent,*args,**kwargs):
            self.parent = parent
            self.grandpa = parent.grandpa
            
            punch_image = Image.open("welcome.jpg")


            # Adjust the size of the image
            basewidth = int(parent.parent.parent.w/8*2.5)
            wpercent = (basewidth/float(punch_image.size[0]))
            hsize = int((float(punch_image.size[1])*float(wpercent)))
            punch_image = punch_image.resize((basewidth,hsize), Image.ANTIALIAS)
            punch_image.save('welcome.jpg') 

            logo = ImageTk.PhotoImage(punch_image)
            
            tk.Button.__init__(self,parent,image = logo,command = lambda: punch(self))
            # Save the reference to image. Python garbage cleaner may blank it out.
            self.image = logo
            

class ButtonFrame(tk.Frame):
        def __init__(self,parent, *args, **kwargs):
            tk.Frame.__init__(self,parent,*args,**kwargs)
            self.parent = parent
            self.grandpa = parent.grandpa
            
            self.grid_rowconfigure(0, weight = 0)
            self.grid_columnconfigure(0, weight = 0)
            
            self.b = PunchButtton(self)
            self.b.grid(row = 0, column = 0,sticky="nw",padx=(5,10))

class BaseSettings(tk.Frame):
        def __init__(self,parent, *args, **kwargs):
            tk.Frame.__init__(self,parent,*args,**kwargs)
            self.parent = parent
            self.grandpa = parent.grandpa
            
            # TO-DO: UPDATE THIS AT THE END! 
            #        0 column                1 column
            # 0 Row: Label: "ANC9 ARO depletion output file:" 
            # 1 Row: Input box               "Select" button that will open the file search box and put the selected name in the input box to the left
            # 2 Row: Label: "Plant name:"
            # 3 Row: Input box with the plant ID from the outputfile
            # 4 Row: Label: "Burnup Window:"
            # 5 Row: Dropdown menu to select: SW, NW, LW
            # 6 Row: Label: "Job Number (optional)":
            # 7 Row: Input box: by defualt start at 1 and increment each time PunchButton is pressed
            
            self.grid_rowconfigure(0, weight = 0)
            self.grid_rowconfigure(1, weight = 0)
            self.grid_rowconfigure(2, weight = 0)
            self.grid_rowconfigure(3, weight = 0)
            self.grid_columnconfigure(0, weight = 0)
            self.grid_columnconfigure(1, weight = 0)
            self.grid_columnconfigure(2, weight = 0)
            self.grid_columnconfigure(3, weight = 0)
            
            self.l1 = tk.Label(self,text="ANC9 ARO depletion output file:").grid(row=0,sticky="w")
            self.l5 = tk.Label(self,text="ANC9 Din depletion output file:").grid(row=2,sticky="w")
            self.l2 = tk.Label(self,text="Plant ID:").grid(row=4, column=0, sticky="w")
            self.l3 = tk.Label(self,text="Burnup window(SW/NW/LW):").grid(row=4, column=1, sticky="w")
            self.l4 = tk.Label(self,text ="Job number (optional):").grid(row=6, sticky="w")
            
            self.e1 = tk.Entry(self,textvariable=self.grandpa.ds.aro_dep_file)
            self.e1.grid(row=1,column=0,columnspan=2,sticky="we",pady=(0,5)) # entry for the ANC9 ARO output file
            self.e5 = tk.Entry(self,textvariable=self.grandpa.ds.din_dep_file)
            self.e5.grid(row=3,column=0,columnspan=2,sticky="we",pady=(0,5))
            self.e2 = tk.Entry(self,textvariable=self.grandpa.ds.plant_id)
            self.e2.grid(row=5,column = 0, sticky = "we",pady=(0,5)) # entry for plant ID
            self.e3 = tk.Entry(self,textvariable=self.grandpa.ds.window)
            self.e3.grid(row=5,column = 1, sticky = "we",pady=(0,5)) # entry for burnup window
            self.e4 = tk.Entry(self,textvariable=self.grandpa.ds.job_id)
            self.e4.grid(row=7,column = 0, sticky = "we",pady=(0,5)) # entry for job number 

            self.b1 = tk.Button(self,text = "Set",command = lambda: browse_func(self.e1)).grid(row=1,column=2,padx=(3,3),pady=(0,5))
            self.b2 = tk.Button(self,text = "Set",command = lambda: browse_func(self.e5)).grid(row=3,column=2,padx=(3,3),pady=(0,5))
            
class AnalysisOfChoice(tk.Frame):
        def __init__(self,parent, *args, **kwargs):
            tk.Frame.__init__(self,parent,*args,**kwargs)
            self.parent = parent
            self.grandpa = parent.grandpa
            
            self.grid_columnconfigure(0, weight = 0)
            self.grid_columnconfigure(1, weight = 0)
            
            self.grid_rowconfigure(0, weight = 0)
            self.grid_rowconfigure(1, weight = 0)

            self.l1 = tk.Label(self, text = "Choose the analysis to punch:")
            self.l2 = tk.Label(self, text = "Set analysis specific input:")
            
            self.b1 = tk.Button(self, text = "Set",command=self.create_input_window)
            
            analyses = ["D-in Depletion","Worst Stuck Rod", "Fdh at RIL", "MTC - BOC", "MTC - EOC", "Rod Misalignment", 
                        "Rod Ejection - HFP", "Rod Ejection - HZP"]
            analyses.sort()
            
            self.grandpa.ds.choice.set("Click for a drop-down menu")
            
            self.op1 = tk.OptionMenu(self, self.grandpa.ds.choice,*analyses) # options menu to select analysis
            
            self.l1.grid(row=0,column=0,sticky="w")
            self.l2.grid(row=0,column=1,sticky="w")
            
            self.op1.grid(row=1,column=0,sticky="we")
            self.op1.configure(width=20)
            self.b1.grid(row=1,column=1,sticky="w")
            
        def create_input_window(self):
            analysis = select_analysis(choice=self.grandpa.ds.choice.get())
            
            if analysis == "Din_depletion_punch":
                self.win = tk.Toplevel(self.grandpa)
                self.win.resizable(True,True)
                self.win.geometry("+%d+%d" % (  self.grandpa.winfo_rootx(),
                                                self.grandpa.winfo_rooty()) )
                
                self.win.wm_title("D-in depletion specific input")
                self.win.l1 = tk.Label(self.win, text="Lead bank:").grid(row=0,sticky="w",padx=(10,10))
                self.win.e1 = tk.Entry(self.win,textvariable=self.grandpa.ds.lead_bank).grid(row=1,sticky="w",pady=(0,5),padx=(10,10))
                self.win.l2 = tk.Label(self.win, text="Percent in:").grid(row=2,sticky="w",padx=(10,10))
                self.win.e2 = tk.Entry(self.win,textvariable=self.grandpa.ds.percent_in).grid(row=3,sticky="w",pady=(0,5),padx=(10,10))
            
class Main(tk.Frame):
        def __init__(self,parent, *args, **kwargs):
            tk.Frame.__init__(self,parent,*args,**kwargs)
            self.parent = parent
            self.grandpa = parent.grandpa
            
            self.grid_rowconfigure(0, weight = 0)
            self.grid_rowconfigure(1, weight = 0)
            self.grid_columnconfigure(0, weight = 0)
            self.grid_columnconfigure(1, weight = 0)
            
            self.btn_frame = ButtonFrame(self,width = (parent.w/8*2.75), height = (parent.h/4*3)/4*3)
            self.basesets_frame = BaseSettings(self,width = (parent.w/8*4.25), height = (parent.h/4*3)/4*3)
            self.choice_frame = AnalysisOfChoice(self,width = (parent.w/8*7), height = (parent.h/4*3)/4)
            
            self.btn_frame.grid_propagate(0)
            self.basesets_frame.grid_propagate(0)
            self.btn_frame.grid_propagate(0)
            
            self.basesets_frame.grid(row = 0, column = 0,sticky = "wens")
            self.btn_frame.grid(row = 0, column = 1,sticky = "e")
            self.choice_frame.grid(row = 1, columnspan = 2,sticky = "wes")

class MessageBox(tk.Frame):
        def __init__(self,parent, *args, **kwargs):
            tk.Frame.__init__(self,parent,*args,**kwargs)
            self.parent = parent
            self.grandpa = parent.grandpa
            # there is something wrong with that height
            
            self.tbox = ScrolledText(self,width=int(parent.w),height=int(parent.h/4) )
            
            #When using grid, any extra space in the parent is allocated proportionate to the "weight" of a row and/or a column 
            #(ie: a column with a weight of 2 gets twice as much of the space as one with a weight of 1). By default, rows and columns have a weight of 0 (zero),
            #meaning no extra space is given to them.
            #
            #You need to give the column that the widget is in a non-zero weight, 
            # so that any extra space when the window grows is allocated to that column
            #
            # You'll also need to specify a weight for the row, and a sticky value of N+S+E+W if you want it to grow in all directions
            self.grid_rowconfigure(0, weight = 1)
            self.grid_columnconfigure(0, weight = 1)
            self.tbox.grid(row = 0)
            
        def insert_text(self,text):
            self.tbox.insert(tk.END,text)
            self.tbox.see(tk.END)
            
class Navigation(tk.Frame):
        def __init__(self,parent, *args, **kwargs):
            tk.Frame.__init__(self,parent,*args,**kwargs)
            self.parent = parent
            self.grandpa = parent.grandpa
            
            self.grid_columnconfigure(0, weight = 1)
            self.label = tk.Label(self,text="Navigation:",bg="white")
            
            self.punch = tk.Button(self, text="Punch file")
            self.run   = tk.Button(self, text="Run jobs")
            self.postp = tk.Button(self, text="Process")
            
            self.label.grid(row=0,sticky="we",padx=(5,5))
            self.punch.grid(row=1,sticky="we",padx=(5,5))
            self.run.grid(row=2,sticky="we",padx=(5,5))
            self.postp.grid(row=3,sticky="we",padx=(5,5))

class MainApplication(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self,parent,*args,**kwargs)
        self.parent = parent
        self.grandpa = self.parent
        self.parent.title("ANC AUTO PUNCHER")
        
        # The data dump is assigned to the root.
        # Root will be always referenced to as grandpa
        parent.ds= data_storage(self)
        
        # Determine the width and height of the main window
        self.w = self.parent.winfo_screenwidth() * 0.5
        self.h = self.parent.winfo_screenheight() * 0.5
        if (self.w < 750):
            self.w = 800
        # Set the window size
        self.parent.geometry(("%dx%d")%(self.w,self.h))
        
        self.parent.resizable(width=False, height=False)
        
        self.main = Main(self,width = self.w/8*7, height = self.h/4*3)
        self.msgb = MessageBox(self,width = self.w, height = self.h/4, bg='lavender')
        self.navg = Navigation(self,width = self.w/8, height = self.h/4*3, bg='white')

        # Layout all the main containers
        self.grid_rowconfigure(0, weight = 0)
        self.grid_rowconfigure(1, weight = 0)
        self.grid_columnconfigure(0, weight = 0)
        self.grid_columnconfigure(1, weight = 0)

        self.main.grid(row = 0, column = 1, sticky = "wens")
        self.msgb.grid(row = 1, columnspan = 2, sticky = "wnse")
        self.navg.grid(row = 0, column = 0, sticky = "wnse")
        
        self.main.grid_propagate(0)
        self.msgb.grid_propagate(0)
        self.navg.grid_propagate(0)

        self.msgb.insert_text("Welcome to ANC AUTO PUNCHER!")
        self.msgb.insert_text("\nSet inputs, choose an analysis from the drop down menu and get punching!")
        self.grid()