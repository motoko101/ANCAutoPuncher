import tkinter as tk
from PIL             import ImageTk, Image
from data_management import select_analysis
from RSACpunch       import puncher
from Functions       import browse_func, punch
from os              import path
from anc_out         import ReadEditSingle

try:
    from tkinter import messagebox
except:
    import tkMessageBox as messagebox

class PunchPage(tk.Frame):
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

class ButtonFrame(tk.Frame):
        def __init__(self,parent, *args, **kwargs):
            tk.Frame.__init__(self,parent,*args,**kwargs)
            self.parent = parent
            self.grandpa = parent.grandpa
            
            self.grid_rowconfigure(0, weight = 0)
            self.grid_columnconfigure(0, weight = 0)
            
            self.b = PunchButton(self)
            self.b.grid(row = 0, column = 0,sticky="nw",padx=(5,10))
	    	   
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
            
            self.op1 = tk.OptionMenu(self, self.grandpa.ds.choice,*analyses,command = self.setup_message) # options menu to select analysis
            
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
                self.win.b1 = tk.Button(self.win, text="Accept",command =self.close_top).grid(row=4,sticky="w",padx=(10,10))

            if analysis == "wsr":
                # Check if the ARO output was defined not defined show a warning
                if not self.grandpa.ds.aro_dep_file.get():
                    messagebox.showwarning("Warning","Define the ARO depletion output file.")
                elif not path.exists(self.grandpa.ds.aro_dep_file.get()):
                     messagebox.showwarning("Warning","ARO depletion output file does not exist.")                   
                else:
                    # Read the SE-General to get burnups and case IDs
                    edit = 'SE-General'
                    SE_General = ReadEditSingle(self.grandpa.ds.aro_dep_file.get(),edit)
                    bu = []
                    case_id = []
                    bu_case_dict = {}

                    self.win = tk.Toplevel(self.grandpa)
                    self.win.resizable(True,True)
                    self.win.geometry("+%d+%d" % (  self.grandpa.winfo_rootx(),
                                                    self.grandpa.winfo_rooty()) )
                    self.win.wm_title("Worst Stuck Rod specific input")
                    self.win.case_labels = {}
                    self.win.bu_labels   = {}
                    self.win.checkbox    = {}

                    for idx,x in enumerate(SE_General):

                        self.win.case_labels[idx] = tk.Label(self.win,text=x[21]).grid(row=idx+1,column=1,sticky="w")
                        self.win.bu_labels[idx]   = tk.Label(self.win,text=x[1]).grid(row=idx+1,column=2,sticky="w")
                        bu_case_dict[x[21]] = tk.IntVar()
                        self.win.checkbox[idx]    = tk.Checkbutton(self.win,variable=bu_case_dict[x[21]]).grid(row=idx+1,column=3,sticky="W")
       
        def close_top(self):
            """
            Updates the setup message after closing the specific inputs window.
            """
            self.setup_message(self)
            self.win.destroy()        

        def setup_message(self,event):

            analysis = select_analysis(choice=self.grandpa.ds.choice.get())
            self.grandpa.msgb.clear()

            if analysis == "Din_depletion_punch":
                text = str("Required input for: Din Depletion")
                self.grandpa.msgb.insert_text(text)

                self.i = 0
                text = str("\n{:d}. ANC9 out file                 Current value: {}".format(self.i,(lambda x: 'None' if (x == '') else x)(self.grandpa.ds.aro_dep_file.get().split('/')[-1])))
                self.grandpa.msgb.insert_text(text)

                self.i = self.i + 1
                text = str("\n{:d}. Lead bank         (via \'Set\') Current value: {}".format(self.i,(lambda x: 'None' if (x == '') else x)(self.grandpa.ds.lead_bank.get())))
                self.grandpa.msgb.insert_text(text)

                self.i = self.i + 1
                text = str("\n{:d}. Percent insertion (via \'Set\') Current value: {}".format(self.i,(lambda x: 'None' if (x == '') else x)(self.grandpa.ds.percent_in.get())))
                self.grandpa.msgb.insert_text(text)

                text = str("\n\nDISCLAIMER: AAP DOESN'T CHECK THE VALIDITY OF YOUR INPUT!\nTread lightly!")
                self.grandpa.msgb.insert_text(text)

            elif analysis == "Fdh_RIL_punch":
                text = str("Required input for: Fdh at RIL")
                self.grandpa.msgb.insert_text(text)

                self.i = 0
                text = str("\n{:d}. ANC9 out file                 Current value: {}".format(self.i,(lambda x: 'None' if (x == '') else x)(self.grandpa.ds.aro_dep_file.get().split('/')[-1])))
                self.grandpa.msgb.insert_text(text)

                text = str("\n\nDISCLAIMER: AAP DOESN'T CHECK THE VALIDITY OF YOUR INPUT!\nTread lightly!")
                self.grandpa.msgb.insert_text(text)                
		
class PunchButton(tk.Button):
        def __init__(self,parent,*args,**kwargs):
            self.parent = parent
            self.grandpa = parent.grandpa
            
            punch_image = Image.open("assets/W_logo.png")
	    #punch_image = Image.open("assets/W_logo.png")
	    
            # Adjust the size of the image
            basewidth = int(self.grandpa.children['!mainapplication'].w/8*2.5)
            wpercent = (basewidth/float(punch_image.size[0]))
            hsize = int((float(punch_image.size[1])*float(wpercent)))
            #basewidth = 300
            #hsize = 300
            punch_image = punch_image.resize((basewidth,hsize), Image.ANTIALIAS)
            #punch_image.save('welcome.jpg') 

            logo = ImageTk.PhotoImage(punch_image)
            
            tk.Button.__init__(self,parent,image = logo,command = lambda: punch(self))
            # Save the reference to image. Python garbage cleaner may blank it out.
            self.image = logo

def punch(self):
    # define what happens when the punch button is pressed
    # 1. Collect data from entries (stored in ds which is an instance of data_storage
    # 2. Check validity
    # 3. Ask for more data if needed depending on analysis of choice
    
    # Echo input in the message box
    text = "\n********************\n The following input parameters were set:"
    self.grandpa.msgb.insert_text(text)
    
    text = str("\nARO file: "+self.grandpa.ds.aro_dep_file.get())
    self.grandpa.msgb.insert_text(text)
    
    text = str("\nDin file: "+self.grandpa.ds.din_dep_file.get())
    self.grandpa.msgb.insert_text(text)
    
    text = str("\nPlant ID: "+self.grandpa.ds.plant_id.get())
    self.grandpa.msgb.insert_text(text)
    
    text = str("\nBurnup window: "+self.grandpa.ds.window.get())
    self.grandpa.msgb.insert_text(text)
    
    text = str("\nJob ID: "+self.grandpa.ds.job_id.get())
    self.grandpa.msgb.insert_text(text)
    
    text = str("\nAnalysis: "+self.grandpa.ds.choice.get())
    self.grandpa.msgb.insert_text(text)
    
    # Match the analysis of choice with the keys
    # Call the selector function
    self.anal = select_analysis(choice=self.grandpa.ds.choice.get())
    
    
    if self.anal == None:
        text = str("\n ********************\n No analysis was selected!")
        self.parent.grandpa.msgb.insert_text(text)
    else:
        puncher(ds=self.grandpa.ds,analysis=self.anal)
        text, self.punchpath = puncher(ds=self.grandpa.ds,analysis=self.anal)
        self.grandpa.msgb.insert_text(text)
        self.grandpa.ds.punched_files.append(self.punchpath)
