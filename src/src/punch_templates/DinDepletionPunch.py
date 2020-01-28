from anc_out import *
import os
from classes import *
from printClassCase import *

#-----------------------------------------------------------------------------    
def Din_depletion_punch(*,lead_bank: str, percent_in: int, punchpath: str,inputpath: str):
    # Punch the Din depletion input
    # Takes the following inputs:
    #
    #    lead_bank    Name of the lead RCCA bank
    #    percent_in   Din insertion as percentage
    #    punchpath    Punch file path
    #    inputpath    ARO depletion output file
    
    # Determine the length of SE-General to set a right index for Archive (might be different depending on number of RCCA banks)
    # "Archive" will always be located at an index equal to this length - 2 position
    SE_length=int(SE_General_length(inputpath))
    
    
    # Get the SM-Archive_Write edit
    #------------------------------
    edit = "SM-Archive_Write"
    SM_Archive_Write = ReadEditSingle(inputpath,edit)
    
    # Define the model file
    model_file_read = SM_Archive_Write[3][1]
    
    # Distill the model file name (get rid of directory and .h5 extension)
    model_file_write = model_file_read.split("/")[-1]
    model_file_write = model_file_write.split(".")[0]
    cwd = os.getcwd()
    model_file_write = cwd + "/DB/" + model_file_write + "_Din_"+ str(percent_in) + ".h5"
    #------------------------------
    
    # Get the SI-Core_Model edit
    #------------------------------
    edit = "SI-Core_Model"
    SI_Core_Model = ReadEditSingle(inputpath,edit)
    
    plant_name = SI_Core_Model[4][1]           # get plant identifier
    
    if plant_name == "Not":                    # check if plant name is identified
        plant_name = UNK                       # if not set to the default name
    
    cycle_number = SI_Core_Model[9][1]         # get cycle number
    
    if cycle_number == "Not":                  # check if cycle number is identified
        cycle_number == UNK                    # if not set to the default name
    #------------------------------
        
    # Get the SE-General edit
    #------------------------------    
    edit = "SE-General"
    SE_General = ReadEditSingle(inputpath,edit)
    #------------------------------
    
    # Determine the steps_in position
    #------------------------------    
    aro = SE_General[0][15]                            # assume that ARO is the first D bank position is HFP ARO depletion file
    steps_in = int (m.floor( (int(aro) * float(100 - percent_in) / 100.)))
                                                    
    #------------------------------        
    
    # Set punch path
    #------------------------------    
    #punch_path = "punch/"+ identifier + "_DIN" + str(percent_in) + ".in"
    punch_path = punchpath
    
    # Create a punch directory and open punch file
    if not os.path.exists(os.path.dirname(punch_path)):
        try:
            os.makedirs(os.path.dirname(punch_path))
        except OSError: # Guard against race condition
            if OSError.errno != errno.EEXIST:
                raise
    #------------------------------
    
    punch=open(punch_path,"w")
    # Start writing to the file
    punch.write("run:\n")    
    
    case = Case()                                    # create and build the case
       
    # First case: read from HFP ARO model and set the bank positions to percent_in
    case.title =  SE_General[0][1] + " MWD/MTU Din depletion"
    
    # add Archive class
    # ------------------
    case.archive= Archive()    
    # add Read class to Archive
    case.archive.read                 = Read()
    case.archive.read.secondary_file = model_file_read
    case.archive.read.name             = SE_General[0][SE_length-2]        
    # add Write class to Archive
    case.archive.model_file    = model_file_write
    case.archive.write= Write()
    name = plant_name + cycle_number + "DIN" + "01"
    case.archive.write.name = name
        
    # add Depletion class
    # -------------------
    case.depletion=Depletion()
    case.depletion.delta_burnup = "0"
    
    # add Core State class
    # -------------------
    case.cs             = Core_State()
    case.cs.cr          = Control_Rod()
    case.cs.cr.name     = lead_bank
    case.cs.cr.position = steps_in

    # print the Case class to file
    PrintClassCase(case,punch)
    
    # Loop over all remaining cases from the HFP ARO 
    
    for idx, case in enumerate(SE_General):
         
        # don't write a case for all burnup smaller or equal to 0 (bascially just skip the 0 MWD/MTU case which was punched out above already)    
        if SE_General[idx][1] =="0":
            continue        
            
        # determine the burnup differences between the current and the previous step
        burnup = int(SE_General[idx][1]) - int(SE_General[idx-1][1])
        
        case = Case()
        case.title = SE_General[idx][1] + " MWD/MTU Din depletion"
        
        # add Archive class
        # -----------------
        case.a= Archive ()
        # add Write class to Archive
        case.a.w = Write()
        if ( int(idx+1) > 9 ): 
            case.a.w.name = plant_name + cycle_number + "DIN" + str(idx+1)
        else:
            case.a.w.name = plant_name + cycle_number + "DIN0" + str(idx+1)
        
        # add Depletion class
        # -------------------
        case.dep = Depletion()
        case.dep.delta_burnup = burnup
        # # add Control class to Depletion
        case.dep.c = Control()
        case.dep.c.item = "all"
        case.dep.c.action = "deplete"
        case.dep.c2 = Control()
        case.dep.c2.item = "xe"
        case.dep.c2.action = "equilibrium"
        
        # print the Case class to file
        PrintClassCase(case,punch)    

    punch.write("/run")
    
    punch.close()
    
    return str("\n\nPunched Din_dep input file!"), punch_path
#---------------------------------------------------------------------------