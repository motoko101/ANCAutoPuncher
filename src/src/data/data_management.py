# Module to manage data
from tkinter import StringVar

class data_storage():
    def __init__(self,parent):
        self.parent = parent
        self.aro_dep_file = StringVar()
        self.din_dep_file = StringVar()
        self.plant_id = StringVar()
        self.window = StringVar()
        self.job_id = StringVar()
        self.choice = StringVar()
        self.lead_bank = StringVar()
        self.percent_in = StringVar()
        self.punched_files = list()

# returns the analysis key
# if the key does not exists returns None
def select_analysis(*,choice):
    analyses = ["D-in Depletion",
                "Worst Stuck Rod",
                "Fdh at RIL", 
                "MTC - BOC", 
                "MTC - EOC", "Rod Misalignment", "Rod Ejection - HFP", "Rod Ejection - HZP"]
    analyses_ID = ["Din_depletion_punch",
                   "wsr",
                   "Fdh_RIL_punch",
                   "MTC_BOC_punch",
                   "MTC_EOC_punch",
                   "rma","re_hfp","re_hzp"]
    
    d = dict(zip(analyses,analyses_ID))
    try:
        choice = d[choice]
    except:
        choice = None
        
    return choice