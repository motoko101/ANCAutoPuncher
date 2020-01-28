from anc_out import *
import os
from classes import *
from printClassCase import *

#-----------------------------------------------------------------------------    
def MTC_EOC_punch(*,inputpath,punchpath):
# Punch MTC at EOC calculations
# Function takes the ANC9 base depletion output file as an argument
# Function punches the input file
# Function returns the input file name
    # In code:
    # =======
    # SE_General             : list to store an ANC edit of the same name
    # SM_Archive_Write        : list to store an ANC edit of the same name
    # model_file            : to store ANC9 model file
    # punch                : punch file to write to
    # punch_path            : punch file path    
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
        
    # Create a punch directory and open punch file
    if not os.path.exists(os.path.dirname(punch_path)):
        try:
            os.makedirs(os.path.dirname(punch_path))
        except OSError: # Guard against race condition
            if OSError.errno != errno.EEXIST:
                raise
    
    punch=open(punch_path,"w")    
    punch.write("run:\n")

    case = Case()
    case.title= SE_General[-1][1] + " MWD/MTU MTC"
    # write archive info
    
    # add Archive class
    # --------------------------------------------------
    case.archive=Archive()
    case.archive.model_file=    model_file
    # add Read class to Archive
    case.archive.read=Read()
    case.archive.read.name=        SE_General[-1][SE_length-2]

    # add Sequence class
    # --------------------------------------------------                
    case.sequence=Sequence()
    # add Base_Case class
    #--------------------
    case.sequence.base_case=Base_Case()
    
    # add Sequence class
    # --------------------------------------------------                
    case.sequence=Sequence()
    # add Base_Case class
    #--------------------
    case.sequence.base_case=Base_Case()
    # add step class
    case.sequence.base_case.step=Step()
    # add Core_State class
    case.sequence.base_case.step.core_state=Core_State()
    case.sequence.base_case.step.core_state.relative_power=    "1"
    case.sequence.base_case.step.core_state.boron_concentration = "0"
    # add Control Rod
    case.sequence.base_case.step.core_state.bankD=Control_Rod()
    case.sequence.base_case.step.core_state.bankD.name=    "ari"
            
    # add Depletion class
    case.sequence.base_case.step.depletion=Depletion()    
    case.sequence.base_case.step.depletion.delta_burnup=    "0"
    # add Control class
    case.sequence.base_case.step.depletion.control=Control()
    case.sequence.base_case.step.depletion.control.item=    "all"
    case.sequence.base_case.step.depletion.control.action=    "deplete"
    case.sequence.base_case.step.depletion.control2=Control()
    case.sequence.base_case.step.depletion.control2.item=    "xe"                
    case.sequence.base_case.step.depletion.control2.action= "equilibrium"
    
    
    #--------------------
    # add Coefficient class
    case.sequence.coefficient=Coefficient()
    case.sequence.coefficient.moderator=    "True"
    
    #add Units class
    # --------------------------------------------------
    case.units=Units()
    # add output class
    case.units.output=Output()
    case.units.output.overall=    "SI"
    
    # add Output class
    case.output=Output()
    case.output.edits=    "SM-General"
    
    # print the class to file
    PrintClassCase(case,punch)                            
    
    punch.write("/run\n")
    
    return str("\n\nPunched MTC EOC input file!"), punch_path 

#-----------------------------------------------------------------------------