import tkinter as tk
from tkinter   import filedialog
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
