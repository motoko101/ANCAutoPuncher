from anc_out import *
import os
from classes import *
from printClassCase import *

#----------------------------------------------------------------------------
def Fdh_RIL_punch(*,inputpath,punchpath):
# Punch Fdh calculations
# Function takes the ANC9 base depletion output file as an argument
# Function punches the input file
# Function returns the input file name
    # In code:
    # =======
    # SE_General             : list to store an ANC edit of the same name
    # SM_Archive_Write        : list to store an ANC edit of the same name
    # model_file            : to store ANC9 model file
    # AO                : array to store Axial Offset from SE-General    
    # punch                : punch file to write to
    # punch_path            : punch file path
    #
    # initialize variables if needed
    AO =[]
    punch_path = punchpath
    
    
    # Determine the length of SE-General to set a right index for Archive (might be different depending on number of RCCA banks)
    # "Archive" will always be located at an index equal to this length - 2 position
    SE_length=int(SE_General_length(inputpath))

    # Get the SE-General edit
    edit = "SE-General"
    SE_General = ReadEditSingle(inputpath,edit)

    # Get the SM-Archive_Write edit
    edit = "SM-Archive_Write"
    SM_Archive_Write = ReadEditSingle(inputpath,edit)

    # Define the model file
    model_file = SM_Archive_Write[3][1]
    
    # Extract AO from SE-General into an array
    for x in SE_General:
        temp = float(x[14]) + 5.5
        AO.append(temp)
        
    # Create a punch directory and open punch file
    if not os.path.exists(os.path.dirname(punch_path)):
        try:
            os.makedirs(os.path.dirname(punch_path))
        except OSError: # Guard against race condition
            if OSError.errno != errno.EEXIST:
                raise
    
    punch=open(punch_path,"w")

    
    # Start writing to the file
    punch.write("run:\n")
    
    # build cases and print them out
    # Loop over all elements in SE-General
    for idx, case in enumerate(SE_General):
         
        # dont write a case for all burnup smaller or equal to 0    
        if SE_General[idx][1] =="0":
            continue
        
        case = Case()
        case.title= SE_General[idx][1] + " MWD/MTU RIL FDH"
        # write archive info
        
        # add Archive class
        # --------------------------------------------------
        case.archive=Archive()
        case.archive.model_file=    model_file
        # add Read class to Archive
        case.archive.read=Read()
        case.archive.read.name=        SE_General[idx][SE_length-2]
        
        # add Depletion class
        # --------------------------------------------------
        case.depletion=Depletion()
        case.depletion.delta_burnup=    "0"
        # add Control class
        case.depletion.control=Control()
        case.depletion.control.item=    "all"
        case.depletion.control.action=    "hold"
        case.depletion.control2=Control()
        case.depletion.control2.item=    "xe"
        case.depletion.control2.action=    "reconstruct"
        
        # add Core_State class
        # --------------------------------------------------                
        case.corestate=Core_State()
        case.corestate.relative_power =    "1"
        case.corestate.axial_offset=    ("%.2f" %AO[idx])
        # add control rod
        case.corestate.control_rod=        Control_Rod()
        case.corestate.control_rod.ril = "true"         # set control rods to RIL
        
        # add Axial_Offset_Search
        # --------------------------------------------------
        case.axial_offset_search=Axial_Offset_Search()
        case.axial_offset_search.parameter="xe_delta"
        case.axial_offset_search.convergence= "0.5"
        
        # add Solution Control
        # --------------------------------------------------
        case.solution_control=Solution_Control()
        # add iteration
        case.solution_control.iteration=Iteration()
        case.solution_control.iteration.maximum ="500"
        
        # add Output
        # --------------------------------------------------                    
        case.output=Output()
        case.output.edits="SM-General, CA-Cntrl_Rod, CA-Power, CA-Fdh"
        
        # print the class to file
        PrintClassCase(case,punch)
    
    punch.write("/run")
    
    punch.close()
    
    return str("\n\nPunched Fdh RIL input file!"), punch_path
#-----------------------------------------------------------------------------