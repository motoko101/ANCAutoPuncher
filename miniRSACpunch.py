# RECORD OF REVISION
# 
# Date(DD/MM/YYY) Changes         Programmer 
# ==============  =======         ==========
# 30/10/2018      Original issue  K. Luszczek (Westinghouse Sweden)
#
#
from anc_out import *
import os
from classes import *
from printClassCase import *

#-----------------------------------------------------------------------------
def WSR_punch(model_file_name,step,window,inputpath):
# Punch WSR search for selected model file 
# Function takes the ANC9 base depletion output file and the desired model_file name as an argument
# Function punches the input file
# Function returns the input file name
    # In code:
    # =======
    # SE_General             : list to store an ANC edit of the same name
    # SM_Archive_Write        : list to store an ANC edit of the same name
    # model_file            : to store ANC9 model file
    # punch                : punch file to write to
    # punch_path            : punch file path    
    punch_path = "punch/"+window+"_WSR_"+model_file_name+".in"        
    
    # Get the SA-Placement edit
    edit = "SA-Placement"
    SA_Placement = ReadEditSingle(inputpath,edit)
    
    # Get the SM-Archive_Write edit
    edit = "SM-Archive_Write"
    SM_Archive_Write = ReadEditSingle(inputpath,edit)

    # Define the model file
    model_file = SM_Archive_Write[3][1]
    
    # Read all the control rods IDS
    # -----------------------------
    # Read SA-Placement until "Control Rod Placement is found", save the rest to the list
    # Truncate 6 first elements of that list
    # Read the list element by element. if the element length is 0 (empty line) break the loop
    # Otherwise read 2nd position to a CR name list
    
    # flag to start saving the lines
    CR_id =list()
    
    # read line by line until "Control" is found
    
    for idx, line in enumerate(SA_Placement):
        if line:
            if line[0] == "Control":
            # truncate SA_Placement and break
                del SA_Placement[:idx+6]
                break
            
    
    # read truncated SA_Placement and get CR IDs until empty line
    for line in SA_Placement:
        if not line:
            break
        CR_id.append(str(line[2]))
        
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
    
        
    case = Case()
    case.title= "WSR for " + model_file_name
    # write archive info
    
    # add Archive class
    # --------------------------------------------------
    case.archive=Archive()
    case.archive.model_file=    model_file
    # add Read class to Archive
    case.archive.read=Read()
    case.archive.read.name=        model_file_name
    
    # add Depletion class
    # --------------------------------------------------
    case.depletion=Depletion()
    case.depletion.delta_burnup=        "0"
    # add Control class
    case.depletion.control=Control()
    case.depletion.control.item=        "all"
    case.depletion.control.action=        "hold"
    
    # add SearchParameter class
    # --------------------------------------------------    
    case.search_parameter=Search_Parameter()
    case.search_parameter.name=        "eigenvalue"
    
    # add Output class
    # --------------------------------------------------    
    case.output=Output()
    case.output.edits=            "SM-General, CA-Cntrl_Rod, SI-Case"    
    
    # add CoreState class
    # --------------------------------------------------        
    case.core_state=Core_State()
    case.core_state.relative_power=        "0"
    # if step = EOC limit the boron concentration
    if (step == "EOC"):
        case.core_state.boron_concentration=    "0"

    PrintClassCase(case,punch)
    
    # --------------------------------------------------
    # --------------------------------------------------
    # print ARI case
    case = Case()
    case.title= "ARI"
    
    # add Core_State class
    # --------------------------------------------------    
    case.core_state=Core_State()
    
    # add Control Rod
    case.core_state.control_rod=Control_Rod()
    case.core_state.control_rod.name=    "ari"
    
    # add Model_Symmetry class
    # --------------------------------------------------
    case.model_symmetry=Model_Symmetry()
    case.model_symmetry.input=    "FULL"
    case.model_symmetry.solution=    "FULL"
    case.model_symmetry.output=    "FULL"

    PrintClassCase(case,punch)

    # --------------------------------------------------
    # --------------------------------------------------
    case = Case()
    case.title=    "WSR SEARCH"
    
    # add Sequence class
    # --------------------------------------------------
    case.sequence=Sequence()
    # add Rod Worth class
    case.sequence.rod_worth=Rod_Worth()
    case.sequence.rod_worth.calculation=    "worth"
    case.sequence.rod_worth.type=        "stuck"
    
    # create a list of control rods classes
    # for each control rod id that was read from ANC9 output do:
    # (this approach can be re-used in any other case where number of given classes is not known apriori)
    # add an instance of Control_Rod() to the case.sequence.rod_worth dictionary named after CD_id
    # add an attribute to the created Control_Rod() instnace 

        
    for RCCA in CR_id:
        case.sequence.rod_worth.__dict__[str(RCCA)]=Control_Rod()
        case.sequence.rod_worth.__dict__[str(RCCA)].name = RCCA


    
    PrintClassCase(case,punch)
    
    
    punch.write("/run")
    punch.close()        

    print ("Punched WSR     input file!\t\t" + punch_path)
    return punch_path

#-----------------------------------------------------------------------------
def WSR_punch2(step,identifier,inputpath):
# Punch WSR search for selected model file 
# Function takes the ANC9 base depletion output file and the desired model_file name as an argument
# Function punches the input file
# Function returns the input file name
    # In code:
    # =======
    # SE_General             : list to store an ANC edit of the same name
    # SM_Archive_Write        : list to store an ANC edit of the same name
    # model_file            : to store ANC9 model file
    # punch                : punch file to write to
    # punch_path            : punch file path    
    punch_path = "punch/"+ identifier + "_WSR" + step + ".in"
    # Determine the length of SE-General to set a right index for Archive (might be different depending on number of RCCA banks)
    # "Archive" will always be located at an index equal to this length - 2 position
    SE_length=int(SE_General_length(inputpath))
    
    
    # Determine the model file name (either BOC or EOC)
    # Get the SE-General
    SE_General = ReadEditSingle(inputpath,"SE-General")
    if (step == "BOC"):
        # use 150 MWD/MTU step
        model_file_name = SE_General[1][SE_length-2]
    elif (step == "EOC"):
        # use the last burnup step
        model_file_name = SE_General[-1][SE_length-2]
    
    
    # Get the SA-Placement edit
    edit = "SA-Placement"
    SA_Placement = ReadEditSingle(inputpath,edit)
    
    # Get the SM-Archive_Write edit
    edit = "SM-Archive_Write"
    SM_Archive_Write = ReadEditSingle(inputpath,edit)

    # Define the model file
    model_file = SM_Archive_Write[3][1]
    
    # Read all the control rods IDS
    # -----------------------------
    # Read SA-Placement until "Control Rod Placement is found", save the rest to the list
    # Truncate 6 first elements of that list
    # Read the list element by element. if the element length is 0 (empty line) break the loop
    # Otherwise read 2nd position to a CR name list
    
    # flag to start saving the lines
    CR_id =list()
    
    # read line by line until "Control" is found

    #edit = "SA-CR_Loc"
    #SA_CR_Loc = ReadEditSingle(inputpath,edit)
    #for line in SA_CR_Loc:
    #    CR_id.append(line[1])
    #
    #
    # It will not work if some other value in that edit is of length 4 as well
    edit = "CA-Cntrl_Rod"
    CA_Cntrl_Rod = ReadEditSingle(inputpath,edit)
    for line in CA_Cntrl_Rod:
        for x in line.split("|"):
            if len(x.strip()) == 4:
                CR_id.append(x.strip())

    # truncate the edit
    
    # for idx, line in enumerate(SA_Placement):
        # if line:
            # if line[0] == "Control":
            # # truncate SA_Placement and break
                # del SA_Placement[:idx+6]
                # break
            
    
    # # read truncated SA_Placement and get CR IDs until empty line
    # for line in SA_Placement:
        # if not line:
            # break
        # CR_id.append(str(line[2]))
        
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
    
        
    case = Case()
    case.title= "WSR for " + step
    # write archive info
    
    # add Archive class
    # --------------------------------------------------
    case.archive=Archive()
    case.archive.model_file=    model_file
    # add Read class to Archive
    case.archive.read=Read()
    case.archive.read.name=        model_file_name
    
    # add Depletion class
    # --------------------------------------------------
    case.depletion=Depletion()
    case.depletion.delta_burnup=        "0"
    # add Control class
    case.depletion.control=Control()
    case.depletion.control.item=        "all"
    case.depletion.control.action=        "hold"
    
    # add SearchParameter class
    # --------------------------------------------------    
    case.search_parameter=Search_Parameter()
    case.search_parameter.name=        "eigenvalue"
    
    # add Output class
    # --------------------------------------------------    
    case.output=Output()
    case.output.edits=            "SM-General, CA-Cntrl_Rod, SI-Case"    
    
    # add CoreState class
    # --------------------------------------------------        
    case.core_state=Core_State()
    case.core_state.relative_power=        "0"
    # if step = EOC limit the boron concentration
    if (step == "EOC"):
        case.core_state.boron_concentration=    "0"

    PrintClassCase(case,punch)
    
    # --------------------------------------------------
    # --------------------------------------------------
    # print ARI case
    case = Case()
    case.title= "ARI"
    
    # add Core_State class
    # --------------------------------------------------    
    case.core_state=Core_State()
    
    # add Control Rod
    case.core_state.control_rod=Control_Rod()
    case.core_state.control_rod.name=    "ari"
    
    # add Model_Symmetry class
    # --------------------------------------------------
    case.model_symmetry=Model_Symmetry()
    case.model_symmetry.input=    "FULL"
    case.model_symmetry.solution=    "FULL"
    case.model_symmetry.output=    "FULL"

    PrintClassCase(case,punch)

    # --------------------------------------------------
    # --------------------------------------------------
    case = Case()
    case.title=    "WSR SEARCH"
    
    # add Sequence class
    # --------------------------------------------------
    case.sequence=Sequence()
    # add Rod Worth class
    case.sequence.rod_worth=Rod_Worth()
    case.sequence.rod_worth.calculation=    "worth"
    case.sequence.rod_worth.type=        "stuck"
    
    # create a list of control rods classes
    # for each control rod id that was read from ANC9 output do:
    # (this approach can be re-used in any other case where number of given classes is not known a priori)
    # add an instance of Control_Rod() to the case.sequence.rod_worth dictionary named after CD_id
    # add an attribute to the created Control_Rod() instance 

        
    for RCCA in CR_id:
        case.sequence.rod_worth.__dict__[str(RCCA)]=Control_Rod()
        case.sequence.rod_worth.__dict__[str(RCCA)].name = RCCA


    
    PrintClassCase(case,punch)
    
    
    punch.write("/run")
    punch.close()        

    print ("Punched WSR     input file!\t\t" + punch_path)
    return punch_path    

#-----------------------------------------------------------------------------
def Fdh_RIL_punch(identifier,inputpath):
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
    punch_path = "punch/"+identifier+"_Fdh_RIL.in"
    
    
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
    
    print ("Punched FdH_RIL input file!\t\t" + punch_path)
    
    return punch_path

#-----------------------------------------------------------------------------    
def MTC_BOC_punch(identifier,inputpath):
# Punch MTC BOC calculations
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
    punch_path = "punch/"+ identifier + "_MTC_BOC" + ".in"
    
    # Get the SE-General edit
    edit = "SE-General"
    SE_General = ReadEditSingle(inputpath,edit)
    
    # Determine the length of SE-General to set a right index for Archive (might be different depending on number of RCCA banks)
    # "Archive" will always be located at an index equal to this length - 2 position
    SE_length=int(SE_General_length(inputpath))

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
    
    # Start writing to the file
    punch.write("run:\n")
    
    # Write all the cases
    # Loop over all elements in SE-General
    for idx, case in enumerate(SE_General):
         
        # Stop after burnup is longer than 6000 MWD|MTU
        if float(SE_General[idx][1]) >= 6000:
            break
        
        
        case = Case()
        case.title= SE_General[idx][1] + " MWD/MTU MTC"
        # write archive info
        
        # add Archive class
        # --------------------------------------------------
        case.archive=Archive()
        case.archive.model_file=    model_file
        # add Read class to Archive
        case.archive.read=Read()
        case.archive.read.name=        SE_General[idx][SE_length-2]

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
        case.sequence.base_case.step.core_state.relative_power=    "0"
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

    punch.write("/run")
        
    punch.close()
    
    print ("Punched MTC_BOC input file!\t\t" + punch_path)
    
    return punch_path    

#-----------------------------------------------------------------------------    
def MTC_EOC_punch(identifier,inputpath):
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
    punch_path = "punch/"+ identifier + "_MTC_EOC.in"

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
    
    # punch sequence info
    print ("Punched MTC_EOC input file!\t\t" + punch_path)
    
    return punch_path

#-----------------------------------------------------------------------------
def Census_punch(identifier,inputpath):
# Punch CENSUS calculations
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
    #
    # initalize variables if needed
    punch_path = "punch/"+identifier+"_census.in"

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

    
    # Start writing to the file
    punch.write("run:\n")
    
    # build cases and print them out
    # Loop over all elements in SE-General
    for idx, case in enumerate(SE_General):         
        
        case = Case()
        case.title= SE_General[idx][1] + " MWD/MTU census case"
        # write archive info
        
        # add Archive class
        # --------------------------------------------------
        case.archive=            Archive()
        case.archive.model_file=    model_file
        # add Read class to Archive
        case.archive.read=        Read()
        case.archive.read.name=        SE_General[idx][SE_length-2]
        
        # add Depletion class
        # --------------------------------------------------
        case.depletion=Depletion()
        case.depletion.delta_burnup=    "0"
        # add Control class
        case.depletion.control=        Control()
        case.depletion.control.item=    "all"
        case.depletion.control.action=    "hold"
        
        # add Census class
        # --------------------------------------------------                
        case.census=            Census()
        case.census.perform_calculation="True"
        case.census.fdh_limit=        "1.6"
        
        # print the class to file
        PrintClassCase(case,punch)
        
            
    
    punch.write("/run")
    
    punch.close()
    
    print ("Punched Census  input file!\t\t" + punch_path)
    
    return punch_path

#-----------------------------------------------------------------------------    
def SDM_punch(case_number, WSR_id, window, inputpath):

# Punch SDM search for selected model file 
# Function takes the ANC9 base depletion output file, case number and WSR id as arguments
# Function punches the input file
# Function returns the input file name
    #
    #
    # TO DO:
    # FIND WSR AUTOMARICALLY USING WSR SEARCH FUNCTION
    # FIND AVERAGE TEMPERATURE 4F DIFFERENCE AUTOMATICALLY
    # READ THE HZP TEMPERATURE
    # In code:
    # =======
    # SE_General             : list to store an ANC edit of the same name
    # SM_Archive_Write        : list to store an ANC edit of the same name
    # model_file            : to store ANC9 model file
    # punch                : punch file to write to
    # punch_path            : punch file path        
    
    # initialize some variables
    ARO = "228"
    ARI = "0"
    
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
    
    # Define Archive from SE-General (index is probably plant specific)
    # decrease case number as python starst indexing at zero
    case_number = case_number-1
    case_id = SE_General[case_number][SE_length-2]
    
    punch_path = "punch/"+window+"_SDM_"+case_id+".in"    

    AO = SE_General[case_number][14]
    AO = float(AO) + 5.5
        
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
    
    # --------------------------------------------------
    ####################################################
    case=Case()        
    case.title=            "K1 ARO BASE CASE"
    
    # add Archive class
    # --------------------------------------------------
    case.archive=            Archive()
    case.archive.model_file=    model_file
    # add Read class to Archive
    case.archive.read=        Read()
    case.archive.read.name=        case_id
    
    # add Depletion class
    # --------------------------------------------------    
    case.depletion=            Depletion()
    case.depletion.delta_burnup=    "0"
    # add Control class
    case.depletion.control=        Control()
    case.depletion.control.item=    "all"
    case.depletion.control.action=    "hold"
    
    # add Search Parameter Class
    # --------------------------------------------------
    case.search_parameter=        Search_Parameter()
    case.search_parameter.name=    "eigenvalue"
    
    # add Core_State Class    
    # --------------------------------------------------
    case.cs=            Core_State()
    case.cs.boron_concentration=    "0"
    case.cs.relative_power=        "1.0"
    
    # add Output class
    # --------------------------------------------------
    case.output=            Output()
    case.output.edits=        "SM-General, CA-Cntrl_Rod"
    
    # print the class to file
    PrintClassCase(case,punch)             

    # --------------------------------------------------
    ####################################################
    case=Case()
    case.title=            "K2 INSERT D TO RIL"
    
    # add Core_State class
    # --------------------------------------------------    
    case.cs=            Core_State()
    # add Control_Rod class
    case.cs.control_rod=        Control_Rod()
    case.cs.control_rod.name=    "D"
    case.cs.control_rod.position=    "174"
    
    # print the class to file
    PrintClassCase(case,punch)        

    # --------------------------------------------------
    ####################################################
    case=Case()
    case.title=            "K3 SKEW XENON AND ACCOUNT FOR THE HFP CORE AVERAGE TEMP UNCERTAINTY"
    
    # add Depletion class
    # --------------------------------------------------
    case.depletion=            Depletion()
    # add Control class
    case.depletion.control=        Control()
    case.depletion.control.item=    "all"
    case.depletion.control.action=    "hold"
    # add Control class
    case.depletion.control2=    Control()
    case.depletion.control2.item=    "xe"
    case.depletion.control2.action=    "reconstruct"
    
    # add Core_state class
    # --------------------------------------------------
    case.cs=            Core_State()
    case.cs.axial_offset=        AO
    # add Xe_Shape class
    case.cs.xe_shape=        Xe_Shape()
    case.cs.xe_shape.delta_xenon=    "-30"

    
    # add Axial_Offset_Search class
    # --------------------------------------------------
    case.aos=            Axial_Offset_Search()
    case.aos.parameter=        "xe_delta"
    case.aos.convergence=    "0.5"
    
    # add Core_Parameters class
    # --------------------------------------------------
    case.cp=            Core_Parameters()
    # add Inlet_Parameter class
    case.cp.it=            Inlet_Temperature()
    case.cp.it.option=        "breakpoint"
    # add Breapoint class
    case.cp.it.bp=            Breakpoint()
    case.cp.it.bp.relative_power=    "0.0"
    case.cp.it.bp.temperature=    "557.06"
    # add Breakpoint class
    case.cp.it.bp2=            Breakpoint()
    case.cp.it.bp2.relative_power=    "1.0"
    case.cp.it.bp2.temperature=    "552.73"

    # print the class to file
    PrintClassCase(case,punch)

    # --------------------------------------------------
    ####################################################
    case=Case()
    case.title=            "K4 TRIP TO HZP"
    
    # add Core_state class
    # --------------------------------------------------
    case.cs=            Core_State()
    case.cs.relative_power=        "0"
    
    # add Depletion class
    # --------------------------------------------------
    case.dp=            Depletion()
    # add Control class
    case.dp.control=        Control()
    case.dp.control.item=        "all"
    case.dp.control.action=        "hold"
    
    # add Axial_Offset_Search
    # --------------------------------------------------
    case.aos=            Axial_Offset_Search()
    case.aos.parameter=        "none"
    
    # print the class to file
    PrintClassCase(case,punch)                

    # --------------------------------------------------
    ####################################################
    case=Case()
    case.title=            "K5 HZP ARI FULL CORE"
    
    # add Core_State class
    # --------------------------------------------------
    case.cs=            Core_State()
    # add Control_Rod
    case.cs.bankD=            Control_Rod()
    case.cs.bankD.name=        "D"
    case.cs.bankD.position=        ARI
    # add Control_Rod
    case.cs.bankC=            Control_Rod()
    case.cs.bankC.name=        "C"
    case.cs.bankC.position=        ARI
    # add Control_Rod
    case.cs.bankB=            Control_Rod()
    case.cs.bankB.name=        "B"
    case.cs.bankB.position=        ARI    
    # add Control_Rod
    case.cs.bankA=            Control_Rod()
    case.cs.bankA.name=        "A"
    case.cs.bankA.position=        ARI
    # add Control_Rod
    case.cs.bankSA=            Control_Rod()
    case.cs.bankSA.name=        "SA"
    case.cs.bankSA.position=    ARI
    # add Control_Rod
    case.cs.bankSB=            Control_Rod()
    case.cs.bankSB.name=        "SB"
    case.cs.bankSB.position=    ARI
    
    # print the class to file
    PrintClassCase(case,punch)    
    
    # --------------------------------------------------
    ####################################################
    case=Case()
    case.title=            "K6 HZP ARI MINUS WSR"    
    
    # add Core_State class
    # --------------------------------------------------    
    case.cs=            Core_State()
    # add Control_Rod class
    case.cs.cr=            Control_Rod()
    case.cs.cr.name=        WSR_id
    case.cs.cr.position=        ARO

    # add Model_Symmetry class
    # --------------------------------------------------        
    case.model_symmetry=        Model_Symmetry()
    case.model_symmetry.input=    "FULL"
    case.model_symmetry.solution=    "FULL"
    case.model_symmetry.output=    "FULL"
    
    # print the class to file
    PrintClassCase(case,punch)
    
    punch.write("/run")
    
    punch.close()
    
    print ("Punched SDM EOC input file!\t\t" + punch_path)
    
    return punch_path

#-----------------------------------------------------------------------------    
def SDM_punch2(step, WSR_id, identifier, inputpath, inputpath_ARO):

# Punch SDM search for selected model file 
# Function takes the ANC9 base depletion output file, case number and WSR id as arguments
# Function punches the input file
# Function returns the input file name
    #
    #
    # TO DO:
    # FIND WSR AUTOMARICALLY USING WSR SEARCH FUNCTION
    # FIND AVERAGE TEMPERATURE 4F DIFFERENCE AUTOMATICALLY
    # READ THE HZP TEMPERATURE
    # In code:
    # =======
    # SE_General             : list to store an ANC edit of the same name
    # SM_Archive_Write        : list to store an ANC edit of the same name
    # model_file            : to store ANC9 model file
    # punch                : punch file to write to
    # punch_path            : punch file path        
    
    # initialize some variables
    ARO = "228"
    
    # Determine the length of SE-General to set a right index for Archive (might be different depending on number of RCCA banks)
    # "Archive" will always be located at an index equal to this length - 2 position
    SE_length=int(SE_General_length(inputpath))
    
    # ----------------------------------
    # Get the SE-General edit
    edit = "SE-General"
    SE_General = ReadEditSingle(inputpath_ARO,edit)
    #
    ARO_SE = [SE_General[0][15], SE_General[0][16], SE_General[0][17], SE_General[0][18], SE_General[0][19], SE_General[0][20]]
    Bank_id =['D','C','B','A','SA','SB']
    # Create a dictionary with bank_ARO
    Bank_ARO = dict(zip(Bank_id,ARO_SE))

    # ----------------------------------
    # Create a dictionary with control rod IDs and corresponding Bank IDs
    CR_id =list()
    Bank_id = list()
    # read line by line until "Control" is found
    # OBTAINABLE FROM ARO MODEL ONLY AT THAT MODEL. TO DO: Punch D-in so that this edit is printed in the output too
    edit = "CA-Cntrl_Rod"
    CA_Cntrl_Rod = ReadEditSingle(inputpath_ARO,edit)
    for line in CA_Cntrl_Rod:
        for x in line.split("|"):
            x = x.strip()
            if len(x) == 4:
                CR_id.append(x.strip())
            if ((len(x) <= 2) and x.isalpha()):
                Bank_id.append(x)
    # Create a dictionary
    Bank_ID = dict(zip(CR_id,Bank_id))
    # set the ARO
    ARO = Bank_ARO[Bank_ID[WSR_id]]
    
    edit = "SE-General"
    SE_General = ReadEditSingle(inputpath,edit)
    
    # ----------------------------------
    # Get the SM-Archive_Write edit
    edit = "SM-Archive_Write"
    SM_Archive_Write = ReadEditSingle(inputpath,edit)

    # Define the model file
    model_file = SM_Archive_Write[3][1]
    
    # Define Archive from SE-General, based on BOC or EOC passed as input
    if (step == "BOC"):
        case_id = SE_General[1][SE_length-2]
        AO = SE_General[1][14]
    elif (step == "EOC"):
        case_id = SE_General[-1][SE_length-2]
        AO = SE_General[-1][14]

    AO = float(AO) + 5.5
    
    
    
    # Read the SI-Core_Parameter to get the breakpoint temperature values
    # for now assumes only two input temperatures: at 0.000 and 1.000 relative power
    edit = "SI-Core_Parameter"
    SI_Core_Parameter = ReadEditSingle(inputpath,edit)
    
    # Check if the output from the depletion model is in Westinghouse or SI units
    edit = "SI-Case"
    SI_Case = ReadEditSingle(inputpath,edit)
    
    for line in SI_Case:
        if line: # check if line is not empty
            if (len(line) > 4):
                if (line[4] == "output:"):
                    units = line[5]
    
    for line in SI_Core_Parameter:
        if line: #check if line is not empty
            if (line[0] == "0.000"):
                if units == "Westinghouse":
                    temp_at_0 = line[1]
                else:
                    temp_at_0 = float(line[1]) * 9.0/5.0 + 32.0
            if (line[0] == "1.000"):
                if units == "Westinghouse":
                    temp_at_1 = line[1]
                    temp_at_1 = float(temp_at_1) + 5.0
                else:
                    temp_at_1 = float(line[1]) + 5.0
                    temp_at_1 = float(temp_at_1) * 9.0/5.0 + 32.0
                
                
    
        
    punch_path = "punch/"+identifier+"_SDM_"+case_id+".in"
        
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
    
    # --------------------------------------------------
    ####################################################
    case=Case()        
    case.title=            "K1 ARO BASE CASE"
    
    # add Archive class
    # --------------------------------------------------
    case.archive=            Archive()
    case.archive.model_file=    model_file
    # add Read class to Archive
    case.archive.read=        Read()
    case.archive.read.name=        case_id
    
    # add Depletion class
    # --------------------------------------------------    
    case.depletion=            Depletion()
    case.depletion.delta_burnup=    "0"
    # add Control class
    case.depletion.control=        Control()
    case.depletion.control.item=    "all"
    case.depletion.control.action=    "hold"
    
    # add Search Parameter Class
    # --------------------------------------------------
    case.search_parameter=        Search_Parameter()
    case.search_parameter.name=    "eigenvalue"
    
    # add Core_State Class    
    # --------------------------------------------------
    case.cs=            Core_State()
    case.cs.boron_concentration=    "0"
    case.cs.relative_power=        "1.0"
    
    # add Output class
    # --------------------------------------------------
    case.output=            Output()
    case.output.edits=        "SM-General, CA-Cntrl_Rod"
    
    # print the class to file
    PrintClassCase(case,punch)             

    # --------------------------------------------------
    ####################################################
    case=Case()
    case.title=            "K2 INSERT D TO RIL"
    
    # add Core_State class
    # --------------------------------------------------    
    case.cs=            Core_State()
    # add Control_Rod class
    case.cs.control_rod=        Control_Rod()
    case.cs.control_rod.ril = "true"         # set control rods to RIL
    
    # print the class to file
    PrintClassCase(case,punch)        

    # --------------------------------------------------
    ####################################################
    case=Case()
    case.title=            "K3 SKEW XENON AND ACCOUNT FOR THE HFP CORE AVERAGE TEMP UNCERTAINTY"
    
    # add Depletion class
    # --------------------------------------------------
    case.depletion=            Depletion()
    # add Control class
    case.depletion.control=        Control()
    case.depletion.control.item=    "all"
    case.depletion.control.action=    "hold"
    # add Control class
    case.depletion.control2=    Control()
    case.depletion.control2.item=    "xe"
    case.depletion.control2.action=    "reconstruct"
    
    # add Core_state class
    # --------------------------------------------------
    case.cs=            Core_State()
    case.cs.axial_offset=        AO
    # add Xe_Shape class
    case.cs.xe_shape=        Xe_Shape()
    case.cs.xe_shape.delta_xenon=    "-30"

    
    # add Axial_Offset_Search class
    # --------------------------------------------------
    case.aos=            Axial_Offset_Search()
    case.aos.parameter=        "xe_delta"
    case.aos.convergence=    "0.5"
    
    # add Core_Parameters class
    # --------------------------------------------------
    case.cp=            Core_Parameters()
    # add Inlet_Parameter class
    case.cp.it=            Inlet_Temperature()
    case.cp.it.option=        "breakpoint"
    # add Breakpoint class
    case.cp.it.bp=            Breakpoint()
    case.cp.it.bp.relative_power=    "0.0"
    case.cp.it.bp.temperature=    temp_at_0
    # add Breakpoint class
    case.cp.it.bp2=            Breakpoint()
    case.cp.it.bp2.relative_power=    "1.0"
    case.cp.it.bp2.temperature=    temp_at_1

    # print the class to file
    PrintClassCase(case,punch)

    # --------------------------------------------------
    ####################################################
    case=Case()
    case.title=            "K4 TRIP TO HZP"
    
    # add Core_state class
    # --------------------------------------------------
    case.cs=            Core_State()
    case.cs.relative_power=        "0"
    # add Control_Rod class
    case.cs.control_rod=        Control_Rod()
    case.cs.control_rod.ril = "false"        # switch off RILs to prevent unwanted insertion to due change of power    
    
    # add Depletion class
    # --------------------------------------------------
    case.dp=            Depletion()
    # add Control class
    case.dp.control=        Control()
    case.dp.control.item=        "all"
    case.dp.control.action=        "hold"
    
    # add Axial_Offset_Search
    # --------------------------------------------------
    case.aos=            Axial_Offset_Search()
    case.aos.parameter=        "none"
    
    # print the class to file
    PrintClassCase(case,punch)                

    # --------------------------------------------------
    ####################################################
    case=Case()
    case.title=            "K5 HZP ARI FULL CORE"
    
    # add Core_State class
    # --------------------------------------------------
    case.cs=            Core_State()
    # add Control_Rod
    case.cs.control_rod=            Control_Rod()
    case.cs.control_rod.name=        "ari"
    
    # print the class to file
    PrintClassCase(case,punch)    
    
    # --------------------------------------------------
    ####################################################
    case=Case()
    case.title=            "K6 HZP ARI MINUS WSR"    
    
    # add Core_State class
    # --------------------------------------------------    
    case.cs=            Core_State()
    # add Control_Rod class
    case.cs.cr=            Control_Rod()
    case.cs.cr.name=        WSR_id
    case.cs.cr.position=        ARO

    # add Model_Symmetry class
    # --------------------------------------------------        
    case.model_symmetry=        Model_Symmetry()
    case.model_symmetry.input=    "FULL"
    case.model_symmetry.solution=    "FULL"
    case.model_symmetry.output=    "FULL"
    
    # print the class to file
    PrintClassCase(case,punch)
    
    punch.write("/run")
    
    punch.close()
    
    print ("Punched SDM "+step+" input file!\t\t" + punch_path)
    
    return punch_path

#-----------------------------------------------------------------------------    
def SDM_punch_burnup(burnup, WSR_id, window, inputpath):

# Punch SDM search for selected model file 
# Function takes the ANC9 base depletion output file, case number and WSR id as arguments
# Function punches the input file
# Function returns the input file name
# Detemines the model file based on the burnup value
    #
    #
    # TO DO:
    # FIND WSR AUTOMARICALLY USING WSR SEARCH FUNCTION
    # FIND AVERAGE TEMPERATURE 4F DIFFERENCE AUTOMATICALLY
    # READ THE HZP TEMPERATURE
    # In code:
    # =======
    # SE_General             : list to store an ANC edit of the same name
    # SM_Archive_Write        : list to store an ANC edit of the same name
    # model_file            : to store ANC9 model file
    # punch                : punch file to write to
    # punch_path            : punch file path        
    
    # initialize some variables
    ARO = "228"
    
    # Determine the length of SE-General to set a right index for Archive (might be different depending on number of RCCA banks)
    # "Archive" will always be located at an index equal to this length - 2 position
    SE_length=int(SE_General_length(inputpath))
    
    # Get the SE-General edit
    edit = "SE-General"
    SE_General = ReadEditSingle(inputpath,edit)
    
    ARO = SE_General[0][16] # take ARO position from a differnet bank than lead. In case Din depletion is being read.
    
    # Get the SM-Archive_Write edit
    edit = "SM-Archive_Write"
    SM_Archive_Write = ReadEditSingle(inputpath,edit)

    # Define the model file
    model_file = SM_Archive_Write[3][1]
    
    # Define Archive from SE-General, based on BOC or EOC passed as input
    for case in SE_General:
        if (int(case[1]) == int(burnup)):
            case_id = case[SE_length-2]
            AO = case[14]

    AO = float(AO) + 5.5
    
    
    
    # Read the SI-Core_Parameter to get the breakpoint temperature values
    # for now assumes only two input temperatures: at 0.000 and 1.000 relative power
    edit = "SI-Core_Parameter"
    SI_Core_Parameter = ReadEditSingle(inputpath,edit)
    
    for line in SI_Core_Parameter:
        if line: #check if line is not empty
            if (line[0] == "0.000"):
                temp_at_0 = line[1]
            if (line[0] == "1.000"):
                temp_at_1 = line[1]
                temp_at_1 = float(temp_at_1) + 5.0
                

        
    punch_path = "punch/"+window+"_SDM_"+str(burnup)+".in"    
        
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
    
    # --------------------------------------------------
    ####################################################
    case=Case()        
    case.title=            "K1 ARO BASE CASE"
    
    # add Archive class
    # --------------------------------------------------
    case.archive=            Archive()
    case.archive.model_file=    model_file
    # add Read class to Archive
    case.archive.read=        Read()
    case.archive.read.name=        case_id
    
    # add Depletion class
    # --------------------------------------------------    
    case.depletion=            Depletion()
    case.depletion.delta_burnup=    "0"
    # add Control class
    case.depletion.control=        Control()
    case.depletion.control.item=    "all"
    case.depletion.control.action=    "hold"
    
    # add Search Parameter Class
    # --------------------------------------------------
    case.search_parameter=        Search_Parameter()
    case.search_parameter.name=    "eigenvalue"
    
    # add Core_State Class    
    # --------------------------------------------------
    case.cs=            Core_State()
    case.cs.boron_concentration=    "0"
    case.cs.relative_power=        "1.0"
    
    # add Output class
    # --------------------------------------------------
    case.output=            Output()
    case.output.edits=        "SM-General, CA-Cntrl_Rod"
    
    # print the class to file
    PrintClassCase(case,punch)             

    # --------------------------------------------------
    ####################################################
    case=Case()
    case.title=            "K2 INSERT D TO RIL"
    
    # add Core_State class
    # --------------------------------------------------    
    case.cs=            Core_State()
    # add Control_Rod class
    case.cs.control_rod=        Control_Rod()
    case.cs.control_rod.ril = "true"         # set control rods to RIL
    
    # print the class to file
    PrintClassCase(case,punch)        

    # --------------------------------------------------
    ####################################################
    case=Case()
    case.title=            "K3 SKEW XENON AND ACCOUNT FOR THE HFP CORE AVERAGE TEMP UNCERTAINTY"
    
    # add Depletion class
    # --------------------------------------------------
    case.depletion=            Depletion()
    # add Control class
    case.depletion.control=        Control()
    case.depletion.control.item=    "all"
    case.depletion.control.action=    "hold"
    # add Control class
    case.depletion.control2=    Control()
    case.depletion.control2.item=    "xe"
    case.depletion.control2.action=    "reconstruct"
    
    # add Core_state class
    # --------------------------------------------------
    case.cs=            Core_State()
    case.cs.axial_offset=        AO
    # add Xe_Shape class
    case.cs.xe_shape=        Xe_Shape()
    case.cs.xe_shape.delta_xenon=    "-30"

    
    # add Axial_Offset_Search class
    # --------------------------------------------------
    case.aos=            Axial_Offset_Search()
    case.aos.parameter=        "xe_delta"
    case.aos.convergence=    "0.5"
    
    # add Core_Parameters class
    # --------------------------------------------------
    case.cp=            Core_Parameters()
    # add Inlet_Parameter class
    case.cp.it=            Inlet_Temperature()
    case.cp.it.option=        "breakpoint"
    # add Breakpoint class
    case.cp.it.bp=            Breakpoint()
    case.cp.it.bp.relative_power=    "0.0"
    case.cp.it.bp.temperature=    temp_at_0
    # add Breakpoint class
    case.cp.it.bp2=            Breakpoint()
    case.cp.it.bp2.relative_power=    "1.0"
    case.cp.it.bp2.temperature=    temp_at_1

    # print the class to file
    PrintClassCase(case,punch)

    # --------------------------------------------------
    ####################################################
    case=Case()
    case.title=            "K4 TRIP TO HZP"
    
    # add Core_state class
    # --------------------------------------------------
    case.cs=            Core_State()
    case.cs.relative_power=        "0"
    # add Control_Rod class
    case.cs.control_rod=        Control_Rod()
    case.cs.control_rod.ril = "false"        # switch off RILs to prevent unwanted insertion to due change of power    
    
    # add Depletion class
    # --------------------------------------------------
    case.dp=            Depletion()
    # add Control class
    case.dp.control=        Control()
    case.dp.control.item=        "all"
    case.dp.control.action=        "hold"
    
    # add Axial_Offset_Search
    # --------------------------------------------------
    case.aos=            Axial_Offset_Search()
    case.aos.parameter=        "none"
    
    # print the class to file
    PrintClassCase(case,punch)                

    # --------------------------------------------------
    ####################################################
    case=Case()
    case.title=            "K5 HZP ARI FULL CORE"
    
    # add Core_State class
    # --------------------------------------------------
    case.cs=            Core_State()
    # add Control_Rod
    case.cs.control_rod=            Control_Rod()
    case.cs.control_rod.name=        "ari"
    
    # print the class to file
    PrintClassCase(case,punch)    
    
    # --------------------------------------------------
    ####################################################
    case=Case()
    case.title=            "K6 HZP ARI MINUS WSR"    
    
    # add Core_State class
    # --------------------------------------------------    
    case.cs=            Core_State()
    # add Control_Rod class
    case.cs.cr=            Control_Rod()
    case.cs.cr.name=        WSR_id
    case.cs.cr.position=        ARO

    # add Model_Symmetry class
    # --------------------------------------------------        
    case.model_symmetry=        Model_Symmetry()
    case.model_symmetry.input=    "FULL"
    case.model_symmetry.solution=    "FULL"
    case.model_symmetry.output=    "FULL"
    
    # print the class to file
    PrintClassCase(case,punch)
    
    punch.write("/run")
    
    punch.close()
    
    print ("Punched SDM"+str(burnup)+" MWD/MTU input file!\t\t" + punch_path)
    
    return punch_path        

#-----------------------------------------------------------------------------    
def Trip_Reactivity_Shape_k_aro(burnup, AO_target, window, inputpath):
# Punch file to get k_aro for TripShape 3D calculations METCOM 6.11
# Target AO should already be skewed to negative side
# 
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
    
    # Define Archive from SE-General based on burnup passed as input
    # and read the boron concnetration (to check if negetive: then set to 0)
    for case in SE_General:
        if (int(case[1]) == int(burnup)):
            case_id = case[SE_length-2]
            boron_con = float(case[5])
        
    punch_path = "punch/"+window+"_K_ARO_"+str(burnup)+".in"    
        
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
    
    # --------------------------------------------------
    ####################################################
    case=Case()        
    case.title=            "ARO base case"
    
    # add Archive class
    # --------------------------------------------------
    case.archive=            Archive()
    case.archive.model_file=    model_file
    # add Read class to Archive
    case.archive.read=        Read()
    case.archive.read.name=        case_id
    
    # add Depletion class
    # --------------------------------------------------    
    case.depletion=            Depletion()
    case.depletion.delta_burnup=    "0"
    # add Control class
    case.depletion.control=        Control()
    case.depletion.control.item=    "all"
    case.depletion.control.action=    "hold"
    
    # add Search Parameter Class
    # --------------------------------------------------
    case.search_parameter=        Search_Parameter()
    case.search_parameter.name=    "eigenvalue"
    
    # add Core_State Class    
    # --------------------------------------------------
    case.cs=            Core_State()
    if (boron_con < 0):
        case.cs.boron_concentration=    "0"
    case.cs.relative_power=        "1.0"
    # add Control_Rod class
    case.cs.cr = Control_Rod()
    case.cs.cr.name = "aro"
    
    
    # print the class to file
    PrintClassCase(case,punch)             

    # --------------------------------------------------
    ####################################################
    case=Case()
    case.title=            "CALCULATE K_ARO - SKEW AO NEGATIVE"
    
    # add Core_State class
    # --------------------------------------------------    
    case.cs=            Core_State()
    case.cs.axial_offset = AO_target
    
    # add Axial_Offset_Search Class\
    # --------------------------------------------------    
    case.aos = Axial_Offset_Search()
    case.aos.parameter = "xe_delta"
    case.aos.convergence = 0.5
    
    # print the class to file
    PrintClassCase(case,punch)        

    punch.write("/run")
    
    punch.close()
    
    print ("Punched K_ARO "+str(burnup)+" MWD/MTU file!\t\t" + punch_path)
    
    return punch_path            

#-----------------------------------------------------------------------------    
def Din_depletion_punch(lead_bank, percent_in, identifier,inputpath):
    # Punch the Din depletion input
    # Takes the following inputs:
    #
    #    lead_bank    Name of the lead RCCA bank
    #    percent_in   Din insertion as percentage
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
    punch_path = "punch/"+ identifier + "_DIN" + str(percent_in) + ".in"
    
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
    case.cs                = Core_State()
    case.cs.cr             = Control_Rod()
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
        
    print ("Punched Din_dep input file!\t\t" + punch_path)
    
    return punch_path

#-----------------------------------------------------------------------------    
def MDC_EOC_punch(window,delta_p,inputpath):
# Punch Most Positive MDC
# Pass RCS pressure and inlet temperature change (to account for unceratinty) as input
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

    punch_path = "punch/"+window+"_MDC_EOC.in"        

    # Determine the length of SE-General to set a right index for Archive (might be different depending on number of RCCA banks)
    # "Archive" will always be located at an index equal to this length - 2 position
    SE_length=int(SE_General_length(inputpath))
    
    # Get the SE-General edit
    edit = "SE-General"
    SE_General = ReadEditSingle(inputpath,edit)
    
    # Get the SM-Archive_Write edit
    edit = "SM-Archive_Write"
    SM_Archive_Write = ReadEditSingle(inputpath,edit)
    
    # Determine the RCS pressure from SI-Core_State
    # Get the SI-Core_Model edit -> HAS TO BE IN PSI!
    edit = "SI-Core_State"
    SI_Core_State = ReadEditSingle(inputpath,edit)
    
    pressure = SI_Core_State[16][1]    # get plant identifier
    pressure = float(pressure) + float(delta_p)   # increase the RCS pressure by the input value
    
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
    case.title= "CASE 1 - LW EOC ARO BASE CASE TO FIND AO" 
    # write archive info
    
    # add Archive class
    # --------------------------------------------------
    case.archive= Archive()
    case.archive.model_file=    model_file
    # add Read class to Archive
    case.archive.read=Read()
    case.archive.read.name=        SE_General[-1][SE_length-2]

    # add Depletion class Case
    # ------------------------
    case.dep = Depletion()
    case.dep.delta_burnup = 0
    # add Control Class to Case
    case.dep.control= Control()
    case.dep.control.item = "all"
    case.dep.control.action = "hold"
    
    # add SearchParameter class to Case
    # ---------------------------------
    case.sp = Search_Parameter()
    case.sp.name = "eigenvalue"
    
    # add CoreState class to Case
    # ----------------------------
    case.cs = Core_State()
    case.cs.boron_concentration = 0
    case.cs.relative_power = 1.0
    
    # print the class to file
    PrintClassCase(case,punch)        

    # ---------------------------------
    # --------------------------------- 
    case = Case()
    case.title = "CASE 2 - INCREASE RCS PRESSURE AND GO TO ARI"
    
    # add CoreState class to Class
    # ----------------------------
    case.cs =  Core_State()
    case.cs.pressure = pressure
    # add Control_Rod class to CoreState
    case.cs.cr=Control_Rod()
    case.cs.cr.name=    "ari"
    
    # print the class to file
    PrintClassCase(case,punch)    

    # ---------------------------------
    # ---------------------------------
    case = Case()
    case.title = "CASE 3 - LW EOC ARI SKEWED TO CASE 1 AO"
    
    # add Depletion class to case
    # ---------------------------
    case.dp= Depletion()
    case.dp.delta_burnup= 0
    # add Control class to depletion
    case.dp.c1 = Control()
    case.dp.c1.item = "all"
    case.dp.c1.action = "hold"
    # add Control class to depletion
    case.dp.c2= Control()
    case.dp.c2.item= "xe"
    case.dp.c2.action = "reconstruct"
    
    # add CoreState class to case_id
    case.cs = Core_State()
    # add Axial_Offset_Search to Case
    case.aos= Axial_Offset_Search()
    case.aos.parameter= "xe_delta"
    case.aos.convergence= "0.5"
    
    # print the class to file
    PrintClassCase(case,punch)    
    
    # ---------------------------------
    # ---------------------------------
    case = Case()
    case.title= "CASE 4 - LW BOC ARI MTC"
    
    # add Depletion case to Case
    # --------------------------
    case.dp= Depletion()
    case.dp.delta_burnup= 0
    # add Control to case to Depletion
    case.dp.co= Control()
    case.dp.co.item = "all"
    case.dp.co.action = "hold"
    # add Axial_Offset_Search Class to Case
    #--------------------------------------
    case.aos= Axial_Offset_Search()
    case.aos.parameter = "none"
    # add Sequence class to Case
    # --------------------------
    case.sq= Sequence()
    # add Coefficient class to Sequence
    case.sq.coe=Coefficient()
    case.sq.coe.moderator = "true"
    
    # print the class to file
    PrintClassCase(case,punch)        
    
    punch.write("/run\n")
    
    # punch sequence info
    print ("Punched MDC_EOC input file!\t\t" + punch_path)
    
    return punch_path

#-----------------------------------------------------------------------------
def Doppler_SW_punch(window,inputpath):
# Punch Doppler-only coefficient and defects calculations
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
    # initalize variables if needed
    punch_path = "punch/"+window+"_Doppler_SW.in"
    
    
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

    
    # Start writing to the file
    punch.write("run:\n")
    
    # build cases and print them out
    # Loop over all elements in SE-General
    for idx, case in enumerate(SE_General):
         
        # print a case for 0 MWD/MTU burnup
        if SE_General[idx][1] =="0":
            case = Case()
            case.title= SE_General[idx][1] + " MWD/MTU SW DTC"
            # add Archive class
            # --------------------------------------------------
            case.archive=Archive()
            case.archive.model_file=    model_file
            # add Read class to Archive
            case.archive.read=Read()
            case.archive.read.name=        SE_General[idx][SE_length-2]
            # add Output class to Case
            # ------------------------
            case.out= Output()
            case.out.edits = "SM-General"
            # add Search_Parameter Class to Case
            # ----------------------------------
            case.sp=Search_Parameter()
            case.sp.name = "eigenvalue"
            # add Repeat Class to Case
            # ------------------------
            case.rep= Repeat()
            case.rep.relative_powers = "0, 0.25, 0.50, 0.75, 1.0, 1.2"
            # add Sequence Class to Case
            # --------------------------
            case.seq= Sequence()
            # add Coefficient Class to Sequence
            # ----------------------------------
            case.seq.coe = Coefficient()
            case.seq.coe.doppler = "true"
            
            # print the class to file
            PrintClassCase(case,punch)

        # print a case for 150 MWD/MTU burnup
        elif SE_General[idx][1] == "150":
            case = Case()
            case.title= SE_General[idx][1] + " MWD/MTU SW DTC"
            # add Archive class
            # --------------------------------------------------
            case.archive=Archive()
            case.archive.model_file=    model_file
            # add Read class to Archive
            case.archive.read=Read()
            case.archive.read.name=        SE_General[idx][SE_length-2]
            # add Output class to Case
            # ------------------------
            case.out= Output()
            case.out.edits = "SM-General"
            # add Search_Parameter Class to Case
            # ----------------------------------
            case.sp=Search_Parameter()
            case.sp.name = "eigenvalue"
            # add Repeat Class to Case
            # ------------------------
            case.rep= Repeat()
            case.rep.relative_powers = "0, 0.25, 0.50, 0.75, 1.0, 1.2"
            # add Sequence Class to Case
            # --------------------------
            case.seq= Sequence()
            # add Coefficient Class to Sequence
            # ----------------------------------
            case.seq.coe = Coefficient()
            case.seq.coe.doppler = "true"
            
            # print the class to file
            PrintClassCase(case,punch)
        
        else:            
            continue
    
    punch.write("/run")
    
    punch.close()
    
    print ("Doppler_SW  input file!\t\t" + punch_path)
    
    return punch_path

#-----------------------------------------------------------------------------
def Doppler_LW_punch(window,inputpath):
# Punch Doppler-only coefficient and defects calculations
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
    # initalize variables if needed
    punch_path = "punch/"+window+"_Doppler_LW.in"
    
    
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

    
    # Start writing to the file
    punch.write("run:\n")
    
    # build cases and print them out
    # Loop over all elements in SE-General
    for idx, case in enumerate(SE_General):
         
        # print a case for 10000 MWD/MTU burnup
        if SE_General[idx][1] =="10000":
            case = Case()
            case.title= SE_General[idx][1] + " MWD/MTU SW DTC"
            # add Archive class
            # --------------------------------------------------
            case.archive=Archive()
            case.archive.model_file=    model_file
            # add Read class to Archive
            case.archive.read=Read()
            case.archive.read.name=        SE_General[idx][SE_length-2]
            # add Output class to Case
            # ------------------------
            case.out= Output()
            case.out.edits = "SM-General"
            # add Search_Parameter Class to Case
            # ----------------------------------
            case.sp=Search_Parameter()
            case.sp.name = "eigenvalue"
            # add Repeat Class to Case
            # ------------------------
            case.rep= Repeat()
            case.rep.relative_powers = "0, 0.25, 0.50, 0.75, 1.0, 1.2"
            # add Sequence Class to Case
            # --------------------------
            case.seq= Sequence()
            # add Coefficient Class to Sequence
            # ----------------------------------
            case.seq.coe = Coefficient()
            case.seq.coe.doppler = "true"
            
            # print the class to file
            PrintClassCase(case,punch)
        
        else:            
            continue
    
    # Punch the EOC case
    case = Case()
    case.title= SE_General[-1][1] + " MWD/MTU SW DTC"
    # add Archive class
    # --------------------------------------------------
    case.archive=Archive()
    case.archive.model_file=    model_file
    # add Read class to Archive
    case.archive.read=Read()
    case.archive.read.name=        SE_General[-1][SE_length-2]
    # add Output class to Case
    # ------------------------
    case.out= Output()
    case.out.edits = "SM-General"
    # add Search_Parameter Class to Case
    # ----------------------------------
    case.sp=Search_Parameter()
    case.sp.name = "eigenvalue"
    # add Repeat Class to Case
    # ------------------------
    case.rep= Repeat()
    case.rep.relative_powers = "0, 0.25, 0.50, 0.75, 1.0, 1.2"
    # add Sequence Class to Case
    # --------------------------
    case.seq= Sequence()
    # add Coefficient Class to Sequence
    # ----------------------------------
    case.seq.coe = Coefficient()
    case.seq.coe.doppler = "true"
        
    # print the class to file
    PrintClassCase(case,punch)    
    
    punch.write("/run")
    
    punch.close()
    
    print ("Doppler_LW  input file!\t\t" + punch_path)
    
    return punch_path

#-----------------------------------------------------------------------------
def Fdh_VS_Power_punch(window,job_number,inputpath,list_of_burnups):
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
    # initalize variables if needed
    AO_target =[]
    BU =[]
    punch_path = "punch/"+job_number+"_"+window+"_Fdh_vs_Power.in"
    
    
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
    # Extract burnups from SE-General into a separate 1D array
    for x in SE_General:
        temp1 = float(x[14])
        temp2 = float(x[1])
        AO_target.append(temp1)
        BU.append(temp2)
        
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
    
    # Define partial powers
    powers = [1.0, 0.75, 0.50, 0.25, 0.0]
    
    # build cases and print them out
    # Loop over all elements in SE-General
    for req_bu in list_of_burnups:
         
        # identify the burnup index
        idx = BU.index(req_bu)
        
        for power in powers:
            # -------------
            # ARO CASE
            # -------------
            case = Case()
            case.title = SE_General[idx][1] + " MWD/MTU " + str(power)+ "% ARO FDH"
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
        
            # add Core_State class to Case
            # ----------------------------
            case.corestate=Core_State()
            case.corestate.relative_power =    power
            
            # add Solution_Control class
            # --------------------------
            case.sc = Solution_Control()
            case.sc.limits_margin_calculation = "fdh"
            case.sc.iteration = Iteration()
            case.sc.iteration.maximum = "500"
            
            # add Output class
            # ----------------
            case.out = Output()
            case.out.edits = "standard, CA-Fdh_Margin, CA-Fdh_Pwr_Margin, SM-Fdh_limits, SR-Fdh_limits, SI-Fdh_Limits, SI-Fdh_Rod_Bow"
            
            # add limit class
            # ---------------
            case.limits = Limits()
            case.limits.fdh = Fdh_Limits()
            case.limits.fdh.region = Region()
            case.limits.fdh.region.name = "AJ"
            case.limits.fdh.region.hfp_limit = "1.62"
            case.limits.fdh.region.limit_slope1 = Limit_Slope()
            case.limits.fdh.region.limit_slope1.slope = "0.3"
            case.limits.fdh.region.limit_slope1.power = "1.0"
            case.limits.fdh.region.limit_slope2 = Limit_Slope()
            case.limits.fdh.region.limit_slope2.slope = "0.3"
            case.limits.fdh.region.limit_slope2.power = "0.0"
            #
            case.limits.fdh.region2 = Region()
            case.limits.fdh.region2.name = "AK"
            case.limits.fdh.region2.hfp_limit = "1.62"
            case.limits.fdh.region2.limit_slope1 = Limit_Slope()
            case.limits.fdh.region2.limit_slope1.slope = "0.3"
            case.limits.fdh.region2.limit_slope1.power = "1.0"
            case.limits.fdh.region2.limit_slope2 = Limit_Slope()
            case.limits.fdh.region2.limit_slope2.slope = "0.3"
            case.limits.fdh.region2.limit_slope2.power = "0.0"
            #
            case.limits.fdh.region3 = Region()
            case.limits.fdh.region3.name = "AL"
            case.limits.fdh.region3.hfp_limit = "1.62"
            case.limits.fdh.region3.limit_slope1 = Limit_Slope()
            case.limits.fdh.region3.limit_slope1.slope = "0.3"
            case.limits.fdh.region3.limit_slope1.power = "1.0"
            case.limits.fdh.region3.limit_slope2 = Limit_Slope()
            case.limits.fdh.region3.limit_slope2.slope = "0.3"
            case.limits.fdh.region3.limit_slope2.power = "0.0"
            #
            case.limits.fdh.uncertainty = Uncertainty()
            case.limits.fdh.uncertainty.calculation = "0.08"
            # check if HFP case
            if power == 1.0:
                case.limits.fdh.rbu = RodBowUncertainty()
                case.limits.fdh.rbu.locations = "all"
                case.limits.fdh.rbu.br1 = BurnupRelation()
                case.limits.fdh.rbu.br1.assembly_burnup = "0.00"
                case.limits.fdh.rbu.br1.multiplier = "1.0"
                case.limits.fdh.rbu.br2 = BurnupRelation()
                case.limits.fdh.rbu.br2.assembly_burnup = "23999"
                case.limits.fdh.rbu.br2.multiplier = "1.0"
                case.limits.fdh.rbu.br3 = BurnupRelation()
                case.limits.fdh.rbu.br3.assembly_burnup = "24000"
                case.limits.fdh.rbu.br3.multiplier = "1.03"
                case.limits.fdh.rbu.br4 = BurnupRelation()
                case.limits.fdh.rbu.br4.assembly_burnup = "33000"
                case.limits.fdh.rbu.br4.multiplier = "1.03"
                case.limits.fdh.rbu.br5 = BurnupRelation()
                case.limits.fdh.rbu.br5.assembly_burnup = "33001"
                case.limits.fdh.rbu.br5.multiplier = "1.0"
                case.limits.fdh.rbu.br6 = BurnupRelation()
                case.limits.fdh.rbu.br6.assembly_burnup = "80000"
                case.limits.fdh.rbu.br6.multiplier = "1.0"
            #
            # print the class to file
            PrintClassCase(case,punch)

            # -------------
            # RIL CASE
            # -------------
            case = Case()
            case.title= SE_General[idx][1] + " MWD/MTU "+ str(power) +"% RIL FDH"
        
            # add Archive class
            # --------------------------------------------------
            case.archive=Archive()
            case.archive.model_file=    model_file
            # add Read class to Archive
            case.archive.read=Read()
            case.archive.read.name=        SE_General[idx][SE_length-2]    
            
            # add Depletion class
            # --------------------------------------------------
            case.dep = Depletion()
            case.dep.delta_burnup = "0"
            case.dep.ctrl1 = Control()
            case.dep.ctrl1.item = "all"
            case.dep.ctrl1.action = "hold"
            case.dep.ctrl2 = Control()
            case.dep.ctrl2.item = "xe"
            case.dep.ctrl2.action = "reconstruct"
            
            # add Core_State class
            # --------------------------------------------------    
            case.cs=  Core_State()
            if float(power) > float(0.25):
                case.cs.axial_offset = AO_target[idx]+float(5.0/power)+float(0.5)
            else:
                case.cs.xe_shape = Xe_Shape()
                case.cs.xe_shape.delta_xenon = "-100"
            case.cs.relative_power = power
            case.cs.cr = Control_Rod()
            case.cs.cr.ril = "true"
            
            # add Axial_Offset_Search Class\
            # --------------------------------------------------    
            if float(power) > float(0.25):
                case.aos = Axial_Offset_Search()
                case.aos.parameter = "xe_delta"
                case.aos.convergence = 0.5
                
            # add Solution_Control class
            # --------------------------
            case.sc = Solution_Control()
            case.sc.limits_margin_calculation = "fdh"
            case.sc.iteration = Iteration()
            case.sc.iteration.maximum = "500"
            
            # add Output class
            # ----------------
            case.out = Output()
            case.out.edits = "standard, CA-Fdh_Margin, CA-Fdh_Pwr_Margin, SM-Fdh_limits, SR-Fdh_limits, SI-Fdh_Limits, SI-Fdh_Rod_Bow"
            
            # add limit class
            # ---------------
            case.limits = Limits()
            case.limits.fdh = Fdh_Limits()
            case.limits.fdh.region = Region()
            case.limits.fdh.region.name = "AJ"
            case.limits.fdh.region.hfp_limit = "1.62"
            case.limits.fdh.region.limit_slope1 = Limit_Slope()
            case.limits.fdh.region.limit_slope1.slope = "0.3"
            case.limits.fdh.region.limit_slope1.power = "1.0"
            case.limits.fdh.region.limit_slope2 = Limit_Slope()
            case.limits.fdh.region.limit_slope2.slope = "0.3"
            case.limits.fdh.region.limit_slope2.power = "0.0"
            #
            case.limits.fdh.region2 = Region()
            case.limits.fdh.region2.name = "AK"
            case.limits.fdh.region2.hfp_limit = "1.62"
            case.limits.fdh.region2.limit_slope1 = Limit_Slope()
            case.limits.fdh.region2.limit_slope1.slope = "0.3"
            case.limits.fdh.region2.limit_slope1.power = "1.0"
            case.limits.fdh.region2.limit_slope2 = Limit_Slope()
            case.limits.fdh.region2.limit_slope2.slope = "0.3"
            case.limits.fdh.region2.limit_slope2.power = "0.0"
            #
            case.limits.fdh.region3 = Region()
            case.limits.fdh.region3.name = "AL"
            case.limits.fdh.region3.hfp_limit = "1.62"
            case.limits.fdh.region3.limit_slope1 = Limit_Slope()
            case.limits.fdh.region3.limit_slope1.slope = "0.3"
            case.limits.fdh.region3.limit_slope1.power = "1.0"
            case.limits.fdh.region3.limit_slope2 = Limit_Slope()
            case.limits.fdh.region3.limit_slope2.slope = "0.3"
            case.limits.fdh.region3.limit_slope2.power = "0.0"
            #
            case.limits.fdh.uncertainty = Uncertainty()
            case.limits.fdh.uncertainty.calculation = "0.08"
            # check if HFP case
            if power == 1.0:
                case.limits.fdh.rbu = RodBowUncertainty()
                case.limits.fdh.rbu.locations = "all"
                case.limits.fdh.rbu.br1 = BurnupRelation()
                case.limits.fdh.rbu.br1.assembly_burnup = "0.00"
                case.limits.fdh.rbu.br1.multiplier = "1.0"
                case.limits.fdh.rbu.br2 = BurnupRelation()
                case.limits.fdh.rbu.br2.assembly_burnup = "23999"
                case.limits.fdh.rbu.br2.multiplier = "1.0"
                case.limits.fdh.rbu.br3 = BurnupRelation()
                case.limits.fdh.rbu.br3.assembly_burnup = "24000"
                case.limits.fdh.rbu.br3.multiplier = "1.03"
                case.limits.fdh.rbu.br4 = BurnupRelation()
                case.limits.fdh.rbu.br4.assembly_burnup = "33000"
                case.limits.fdh.rbu.br5 = BurnupRelation()
                case.limits.fdh.rbu.br4.multiplier = "1.03"
                case.limits.fdh.rbu.br5.assembly_burnup = "33001"
                case.limits.fdh.rbu.br5.multiplier = "1.0"
                case.limits.fdh.rbu.br6 = BurnupRelation()
                case.limits.fdh.rbu.br6.assembly_burnup = "80000"
                case.limits.fdh.rbu.br6.multiplier = "1.0"
                #
            #
            PrintClassCase(case,punch)
    
    punch.write("/run")
    
    punch.close()
    
    print ("Punched Fdh_vs_Power input file!\t\t" + punch_path)
    
    return punch_path

#-----------------------------------------------------------------------------
def MTC_HFP_punch(window,inputpath):
# Punch MTC at HFP (needed for Dropped Rod Analysis)
# (Will probably be only run at SW)
    #
    # initalize variables if needed
    punch_path = "punch/"+window+"_MTC_HFP.in"
    
    
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

    
    # Start writing to the file
    punch.write("run:\n")
    
    # build cases and print them out
    # Loop over all elements in SE-General
    for idx, case in enumerate(SE_General):
    
        case = Case()
        case.title= SE_General[idx][1] + " MWD/MTU MTC HFP"
        # write archive info
        
        # add Archive class
        # --------------------------------------------------
        case.archive=Archive()
        case.archive.model_file=    model_file
        # add Read class to Archive
        case.archive.read=Read()
        case.archive.read.name=        SE_General[idx][SE_length-2]
        
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
        # add Depletion class
        case.sequence.base_case.step.depletion=Depletion()    
        case.sequence.base_case.step.depletion.delta_burnup=    "0"
        # add Control class
        case.sequence.base_case.step.depletion.control=Control()
        case.sequence.base_case.step.depletion.control.item=    "all"
        case.sequence.base_case.step.depletion.control.action=    "hold"
        #--------------------
        # add Coefficient class
        case.sequence.coefficient=Coefficient()
        case.sequence.coefficient.moderator=    "True"
        
        #add Units class
        # --------------------------------------------------
        #case.units=Units()
        # add output class
        #case.units.output=Output()
        #case.units.output.overall=    "SI"
        
        # add Output class
        case.output=Output()
        case.output.edits=    "SM-General"

        # print the class to file
        PrintClassCase(case,punch)
        
            
    
    punch.write("/run")
    
    punch.close()
    
    print ("Punched MTC HFP input file!\t\t" + punch_path)
    
    return punch_path

#-----------------------------------------------------------------------------
def RIA_punch(window,AO_limit_plus,AO_limit_minus,inputpath):
# Punch RIA calculations.
# Full 3D calculation Procedure from METCOM Section 6.9.2.2 revision 82, 8/17
# Assumes CAOC band with +/- bounds passed on as arguments
    AO_plus =  []
    AO_minus = []
    punch_path = "punch/"+window+"_RIA.in"
        
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
        temp1 = float(x[14])+float(AO_limit_plus)+0.5  # skew AO to the positive CAOC limit + convergence criterion
        temp2 = float(x[14])-float(AO_limit_minus)-0.5 # skew AO to the negative CAOC limit - convergence criterion
        AO_plus.append(temp1)
        AO_minus.append(temp2)
        
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
    
        if SE_General[idx][1] == "0": # 0 MWD/MTU case needs to be skipped. It is not need and neither does it converge.
            continue    
            
        # --------------------------------------------------
        # ARO positively skewed AO case
        # --------------------------------------------------
        case = Case()
        case.title= SE_General[idx][1] + " AO plus" 
        
        # add Archive class
        # --------------------------------------------------
        case.archive=Archive()
        case.archive.model_file = model_file
        # add Read class to Archive
        case.archive.read=Read()
        case.archive.read.name = SE_General[idx][SE_length-2]
        
        # add Solution_Control Class to case
        case.sc = Solution_Control()
        # add Iteration
        case.sc.iteration= Iteration()
        case.sc.iteration.maximum = "500"
        
        # add Depletion class
        # --------------------------------------------------
        case.depletion=Depletion()
        case.depletion.delta_burnup=    "0"
        # add Control class
        case.depletion.control=Control()
        case.depletion.control.item=    "all"
        case.depletion.control.action=    "hold"    
        # add Control class
        case.depletion.control2=Control()
        case.depletion.control2.item = "xe"
        case.depletion.control2.action = "reconstruct"
        
        # add Core_Store class to Case
        # ----------------------------
        case.cs=Core_State()
        case.cs.axial_offset = AO_plus[idx]
        
        if (float(SE_General[idx][5]) < 0): # set boron con. to 0 if HFP CBC at this burnup step is negative
            case.cs.boron_concentration = 0
        
        # add Control_Rod class to Case
        case.cs.cr= Control_Rod()
        case.cs.cr.name = "aro"
        # add Xe_Shape
        case.cs.xes= Xe_Shape()
        case.cs.xes.delta_xenon = -30 # should be + for negative AO cases
        
        # add Axial_Offset_Search Class to Case
        case.aos = Axial_Offset_Search()
        case.aos.parameter = "xe_delta"
        case.aos.convergence = "0.5"
        
        # add Search_Parameter Class to Case
        case.sp =Search_Parameter()
        case.sp.name = "eigenvalue"
        
        # add Output class
        case.out = Output()
        case.out.disable_edits = "standard" # disable printing a lot of useless information
        
        # print the class to file
        PrintClassCase(case,punch)
        
        # --------------------------------------------------
        # RIA vs. POWERS (at RIL)
        # --------------------------------------------------        
        case = Case()
        case.title =  SE_General[idx][1] + " AO plus" 
        
        # add Depletion class to Case
        case.depletion = Depletion()
        # add Control class to Depletion
        case.depletion.c1= Control()
        case.depletion.c1.item = "all"
        case.depletion.c1.action = "hold"
        
        # add Axial_Offset_Search class to Case
        case.aos = Axial_Offset_Search()
        case.aos.parameter = "none"
        
        # add Core_State
        case.cs = Core_State()
        # add Control_Rod
        case.cs.cr = Control_Rod()
        case.cs.cr.ril = "true"
        
        # add Repeat Class
        case.rp = Repeat()
        case.rp.relative_powers = "1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0"

        # print the class to file
        PrintClassCase(case,punch)

        # --------------------------------------------------
        # ARO negatively skewed AO case
        # --------------------------------------------------
        case = Case()
        case.title= SE_General[idx][1] + " AO minus" 
        
        # add Archive class
        # --------------------------------------------------
        case.archive=Archive()
        case.archive.model_file = model_file
        # add Read class to Archive
        case.archive.read=Read()
        case.archive.read.name = SE_General[idx][SE_length-2]

        # add Solution_Control Class to case
        case.sc = Solution_Control()
        # add Iteration
        case.sc.iteration= Iteration()
        case.sc.iteration.maximum = "500"        

        # add Depletion class
        # --------------------------------------------------
        case.depletion=Depletion()
        case.depletion.delta_burnup=    "0"
        # add Control class
        case.depletion.control=Control()
        case.depletion.control.item=    "all"
        case.depletion.control.action=    "hold"    
        # add Control class
        case.depletion.control2=Control()
        case.depletion.control2.item = "xe"
        case.depletion.control2.action = "reconstruct"
        
        # add Core_Store class to Case
        # ----------------------------
        case.cs=Core_State()
        case.cs.axial_offset = AO_minus[idx]
        
        if (float(SE_General[idx][5]) < 0): # set boron con. to 0 if HFP CBC at this burnup step is negative
            case.cs.boron_concentration = 0
        
        # add Control_Rod class to Case
        case.cs.cr= Control_Rod()
        case.cs.cr.name = "aro"
        # add Xe_Shape
        case.cs.xes= Xe_Shape()
        case.cs.xes.delta_xenon = 30 # should be + for negative AO cases
        
        # add Axial_Offset_Search Class to Case
        case.aos = Axial_Offset_Search()
        case.aos.parameter = "xe_delta"
        case.aos.convergence = "0.5"
        
        # add Search_Parameter Class to Case
        case.sp =Search_Parameter()
        case.sp.name = "eigenvalue"
        
        # print the class to file
        PrintClassCase(case,punch)
        
        # --------------------------------------------------
        # RIA vs. POWERS (at RIL)
        # --------------------------------------------------        
        case = Case()
        case.title =  SE_General[idx][1] + " AO minus" 
        
        # add Depletion class to Case
        case.depletion = Depletion()
        # add Control class to Depletion
        case.depletion.c1= Control()
        case.depletion.c1.item = "all"
        case.depletion.c1.action = "hold"
        
        # add Axial_Offset_Search class to Case
        case.aos = Axial_Offset_Search()
        case.aos.parameter = "none"
        
        # add Core_State
        case.cs = Core_State()
        # add Control_Rod
        case.cs.cr = Control_Rod()
        case.cs.cr.ril = "true"
        
        # add Repeat Class
        case.rp = Repeat()
        case.rp.relative_powers = "1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0"

        # print the class to file
        PrintClassCase(case,punch)

        
    punch.write("/run")
    
    punch.close()
    
    print ("Punched RIA input file!\t\t" + punch_path)
    
    return punch_path

#-----------------------------------------------------------------------------    
def RodEjectionHfp_Punch(window,step,inputpath_aro,inputpath_din):
# Punch Rod Ejection Input
# "step" should be either "BOC" or "EOC"
#
# Din depletion edit does not have CA-CR_Loc edit. Thus ARO depletion output is 
# used instead.
#
    punch_path = "punch/"+window+"_RE_HFP_"+step+".in"
        
    # Determine the length of SE-General to set a right index for Archive (might be different depending on number of RCCA banks)
    # "Archive" will always be located at an index equal to this length - 2 position
    SE_length=int(SE_General_length(inputpath_aro))

    # Get the SE-General edit
    edit = "SE-General"
    SE_General_aro = ReadEditSingle(inputpath_aro,edit)
    SE_General_din = ReadEditSingle(inputpath_din,edit)

    # Get the SM-Archive_Write edit
    edit = "SM-Archive_Write"
    SM_Archive_Write_aro = ReadEditSingle(inputpath_aro,edit)
    SM_Archive_Write_din = ReadEditSingle(inputpath_din,edit)
    

    # Define the model file
    model_file_aro = SM_Archive_Write_aro[3][1]
    model_file_din = SM_Archive_Write_din[3][1]
    
    # ----------------------------------
    # Get the control rod IDs
    CR_id =list()
    # read line by line until "Control" is found
    # OBTAINABLE FROM ARO MODEL ONLY AT THAT MODEL. TO DO: Punch D-in so that this edit is printed in the output too
    edit = "CA-Cntrl_Rod"
    CA_Cntrl_Rod = ReadEditSingle(inputpath,edit)
    for line in CA_Cntrl_Rod:
        print(line.split("|"))
        for x in line.split("|"):
            if len(x.strip()) == 4:
                CR_id.append(x.strip())
    # ----------------------------------
    
    # Create a punch directory and open punch file
    if not os.path.exists(os.path.dirname(punch_path)):
        try:
            os.makedirs(os.path.dirname(punch_path))
        except OSError: # Guard against race condition
            if OSError.errno != errno.EEXIST:
                raise
    
    punch=open(punch_path,"w")
    
    if (step == "BOC"):
        idx = 1
        model_file = model_file_aro
        SE_General = SE_General_aro
    elif (step == "EOC"):
        idx = -1
        model_file = model_file_din
        SE_General = SE_General_din
    
    # Start writing to the file
    punch.write("run:\n")
        
    # build cases and print them out
    #
    # 
    #
    # Base case
    case = Case()
    
    case.title = "RE HFP "+step # this naming is needed for post-processing. Do not change
    
    # add Archive class
    # -----------------
    case.ar = Archive()
    case.ar.model_file = model_file
    # add Read class
    case.ar.r = Read()
    case.ar.r.name = SE_General[idx][SE_length-2]
    
    # add Depletion class
    # -------------------
    case.dp = Depletion()
    case.dp.delta_burnup = 0
    # add Control class -> hold all
    case.dp.cr = Control()
    case.dp.cr.item = "all"
    case.dp.cr.action = "hold"
    # add Control class -> set xenon to eq.
    case.dp.cr2 = Control()
    case.dp.cr2.item = "xe"
    case.dp.cr2.action = "equilibrium"
    
    # add Core_State class
    case.cs = Core_State()
    case.cs.relative_power = 1
    # add Control_Rod class to Core_State -> set RCCA to RIL
    case.cs.cr = Control_Rod()
    case.cs.cr.ril = "true"
    
    # print the class to file
    PrintClassCase(case,punch)    
    
    #
    # EJECT RCCAs
    #
    case = Case()
    case.title ="EJECT RCCAs"
    
    # add Sequence class
    # ------------------
    case.se = Sequence()
    case.se.rw = Rod_Worth()
    case.se.rw.calculation = "worth"
    case.se.rw.type = "ejected"
    
    # create a list of control rods classes
    # for each control rod id that was read from ANC9 output do:
    # (this approach can be re-used in any other case where number of given classes is not known a priori)
    # add an instance of Control_Rod() to the case.sequence.rod_worth dictionary named after CD_id
    # add an attribute to the created Control_Rod() instance
        
    for RCCA in CR_id:
        case.se.rw.__dict__[str(RCCA)]=Control_Rod()
        case.se.rw.__dict__[str(RCCA)].name = RCCA

    # print the class to file
    PrintClassCase(case,punch)

        
    punch.write("/run")
    
    punch.close()
    
    print ("Punched RE_HFP_%s input file!\t\t %s" %(step,punch_path))
    
    return punch_path

#-----------------------------------------------------------------------------
def RodEjectionHzp_Punch(window,step,inputpath_aro,ARO,inputpath_din):
# Punch Rod Ejection Input
# "step" should be either "BOC" or "EOC"
#
# Din depletion edit does not have CA-CR_Loc edit. Thus ARO depletion output is 
# used instead.
#
    punch_path = "punch/"+window+"_RE_HZP_"+step+".in"
        
    # Determine the length of SE-General to set a right index for Archive (might be different depending on number of RCCA banks)
    # "Archive" will always be located at an index equal to this length - 2 position
    SE_length=int(SE_General_length(inputpath_aro))

    # Get the SE-General edit
    edit = "SE-General"
    SE_General_aro = ReadEditSingle(inputpath_aro,edit)
    SE_General_din = ReadEditSingle(inputpath_din,edit)

    # Get the SM-Archive_Write edit
    edit = "SM-Archive_Write"
    SM_Archive_Write_aro = ReadEditSingle(inputpath_aro,edit)
    SM_Archive_Write_din = ReadEditSingle(inputpath_din,edit)
    

    # Define the model file
    model_file_aro = SM_Archive_Write_aro[3][1]
    model_file_din = SM_Archive_Write_din[3][1]
    
    # ----------------------------------
    # Get the control rod IDs
    CR_id =list()
    # read line by line until "Control" is found
    # OBTAINABLE FROM ARO MODEL ONLY AT THAT MODEL. TO DO: Punch D-in so that this edit is printed in the output too
    edit = "CA-Cntrl_Rod"
    CA_Cntrl_Rod = ReadEditSingle(inputpath,edit)
    for line in CA_Cntrl_Rod:
        print(line.split("|"))
        for x in line.split("|"):
            if len(x.strip()) == 4:
                CR_id.append(x.strip())
    # ----------------------------------
    
    # Create a punch directory and open punch file
    if not os.path.exists(os.path.dirname(punch_path)):
        try:
            os.makedirs(os.path.dirname(punch_path))
        except OSError: # Guard against race condition
            if OSError.errno != errno.EEXIST:
                raise
    
    punch=open(punch_path,"w")
    
    if (step == "BOC"):
        idx = 0
        model_file = model_file_aro
        SE_General = SE_General_aro
    elif (step == "EOC"):
        idx = -1
        model_file = model_file_din
        SE_General = SE_General_din
    
    # Start writing to the file
    punch.write("run:\n")
        
    # build cases and print them out
    #
    # 
    #
    # Base case: HZP at x BU SW ARO NOXE CRITICAL
    case = Case()
    
    case.title ="RE HZP "+ step # this naming is needed for post-processing. Do not change
    
    # add Archive class
    # -----------------
    case.ar = Archive()
    case.ar.model_file = model_file
    # add Read class
    case.ar.r = Read()
    case.ar.r.name = SE_General[idx][SE_length-2]
    
    # add Depletion class
    # -------------------
    case.dp = Depletion()
    case.dp.delta_burnup = 0
    # add Control class -> hold all
    case.dp.cr = Control()
    case.dp.cr.item = "all"
    case.dp.cr.action = "hold"
    # add Control class -> set xeonon to eq.
    case.dp.cr2 = Control()
    case.dp.cr2.item = "xe"
    case.dp.cr2.action = "equilibrium"
    
    # add Core_State class
    case.cs = Core_State()
    case.cs.relative_power = 0
    # add Control_Rod class to Core_State -> set RCCA to ARO
    case.cs.cr= Control_Rod()
    case.cs.cr.name = "aro"
    case.cs.eigenvalue = 1
    
    # add Search_Parameter Class
    case.sp = Search_Parameter()
    case.sp.name = "boron_concentration"
    
    # print the class to file
    PrintClassCase(case,punch)    
    
    #
    # INSERT RODS TO RIL
    # 
    case = Case()
    case.title = "INSERT RODS TO RIL"
    
    # add Core_State instance
    case.cs = Core_State()
    # add Control_Rod
    case.cs.cr = Control_Rod()
    case.cs.cr.ril = "true"    

    # print the class to file
    PrintClassCase(case,punch)    
    
    #
    # ITC CALCULATIONS
    #
    case = Case()
    case.title = "ITC CALCUALTIONS"
    
    # add Sequence instance
    case.se = Sequence()
    # add Coefficient instance
    case.se.coe = Coefficient()
    case.se.coe.isothermal = "true"
    
    # print the class to file
    PrintClassCase(case,punch)        
    
    #
    # EJECT RCCAs
    #
    case = Case()
    case.title ="EJECT RCCAs"
    
    # add Sequence class
    # ------------------
    case.se = Sequence()
    case.se.rw = Rod_Worth()
    case.se.rw.calculation = "worth"
    case.se.rw.type = "ejected"
    
    
    
    # create a list of control rods classes
    # for each control rod id that was read from ANC9 output do:
    # (this approach can be re-used in any other case where number of given classes is not known a priori)
    # add an instance of Control_Rod() to the case.sequence.rod_worth dictionary named after CD_id
    # add an attribute to the created Control_Rod() instance
        
    for RCCA in CR_id:
        case.se.rw.__dict__[str(RCCA)]=Control_Rod()
        case.se.rw.__dict__[str(RCCA)].name = RCCA

    # print the class to file
    PrintClassCase(case,punch)

        
    punch.write("/run")
    
    punch.close()
    
    print ("Punched RE_HZP_%s input file!\t\t %s" %(step,punch_path))
    
    return punch_path

#-----------------------------------------------------------------------------
def Trip_Reactivity_Shape_Punch(burnup, AO_target, WSR_id, k_aro, window, inputpath, ARO):
# Punch file to get k_aro for TripShape 3D calculations METCOM 6.11
# Target AO should already be skewed to negative side
# 
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

    # Get the SI-Rod_Relation
    edit = "SI-Rod_Relation"
    SI_Rod_Relation = ReadEditSingle(inputpath,edit)
    
    # Get the rod botoom position
    for line in SI_Rod_Relation:
        if len(line)== 0:
            continue
        elif line[0] == "Rod":
            if line[1] == "Bottom":
                rod_bottom = float(line[3])
                break
    # Get the rod step size
    for line in SI_Rod_Relation:
        if len(line) == 0:
            continue
        elif line[0] == "Step":
            if line [1] == "Size:":
                step_size = float(line[2])
                break
        
    # Get the SI-Core_Model
    edit = "SI-Core_Model"
    SI_Core_Model = ReadEditSingle(inputpath,edit)

    # Get hot active fuel height
    for line in SI_Core_Model:
        if len(line) == 0:
            continue
        elif line[0] == "Total":
            if line[1] == "Fuel":
                if line[2] == "Height":
                    if line[3] == "(hot):":
                        afl = float(line[4])
# Define Archive from SE-General based on burnup passed as input
# and read the boron concentration (to check if negative: then set to 0)
    for case in SE_General:
        if (int(case[1]) == int(burnup)):
            case_id = case[SE_length-2]
            boron_con = float(case[5])
            
    punch_path = "punch/"+window+"_TripShape_"+str(burnup)+".in"
    
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
    
    # --------------------------------------------------
    # ARO
    # --------------------------------------------------
    case=Case()        
    case.title=            "ARO base case"
    
    # add Archive class
    # --------------------------------------------------
    case.archive=            Archive()
    case.archive.model_file=    model_file
    # add Read class to Archive
    case.archive.read=        Read()
    case.archive.read.name=        case_id
    
    # add Depletion class
    # --------------------------------------------------    
    case.depletion=            Depletion()
    case.depletion.delta_burnup=    "0"
    # add Control class
    case.depletion.control=        Control()
    case.depletion.control.item=    "all"
    case.depletion.control.action=    "hold"
    
    # add Search Parameter Class
    # --------------------------------------------------
    case.search_parameter=        Search_Parameter()
    case.search_parameter.name=    "eigenvalue"
    
    # add Core_State Class    
    # --------------------------------------------------
    case.cs=            Core_State()
    if (boron_con < 0):
        case.cs.boron_concentration=    "0"
    case.cs.relative_power=        "1.0"
    # add Control_Rod class
    case.cs.cr2 = Control_Rod()
    case.cs.cr2.name = "aro"
    
    # add Groups class
    # ----------------
    case.groups = Groups()
    # add Control_Rod()
    case.groups.cr = Control_Rod()
    case.groups.cr.name = "WSR"
    case.groups.cr.members = WSR_id
    
    
    # print the class to file
    PrintClassCase(case,punch)             

    # --------------------------------------------------
    # CALCUALTE K-ARO - SKEW AO NEGATIVE
    # --------------------------------------------------
    case=Case()
    case.title=            "CALCULATE K_ARO - SKEW AO NEGATIVE"
    
    # add Core_State class
    # --------------------------------------------------    
    case.cs=            Core_State()
    case.cs.axial_offset = AO_target
    
    # add Axial_Offset_Search Class\
    # --------------------------------------------------    
    case.aos = Axial_Offset_Search()
    case.aos.parameter = "xe_delta"
    case.aos.convergence = 0.5
    
    # print the class to file
    PrintClassCase(case,punch)        
    
    # --------------------------------------------------
    # FREEZE FEEDBACK, ARI-1 RCCA STRENGTH TO TARGET TRIP WORTH
    # --------------------------------------------------
    case = Case()
    case.title = "FREEZE FEEDBACK, ARI-1 RCCA STRENGTH TO TARGET TRIP WORTH"
    
    # add Feedback class
    # ------------------
    case.fb = Feedback()
    case.fb.reference_case =  "false"
    # add Control class
    case.fb.c = Control()
    case.fb.c.item = "fuel_temperature"
    case.fb.c.action = "hold"
    # add Control class
    case.fb.cc = Control()
    case.fb.cc.item = "moderator"
    case.fb.cc.action = "hold"
    
    # add Core_Parameters class
    # -------------------------
    case.cp = Core_Parameters()
    case.cp.calculate_enthalpy_rise = "no"
    case.cp.enthalpy_rise = "10"
    
    # add Axial_Offset_Search class
    # -----------------------------
    case.aos = Axial_Offset_Search()
    case.aos.parameter = "none"
    
    # add Core_State class
    # --------------------
    case.cs =Core_State()
    # add Control_Rod class
    case.cs.crr = Control_Rod()
    case.cs.crr.name = "ari"
    # add Control_Rod class
    case.cs.cr = Control_Rod()
    case.cs.cr.name = "WSR"
    case.cs.cr.position = ARO
    case.cs.eigenvalue = k_aro
    
    # add Search_Parameter class
    # --------------------------
    case.sp = Search_Parameter()
    case.sp.name = "cr_abs_search_w_gray"
    
    # print the class to file
    PrintClassCase(case,punch)       
    
    # --------------------------------------------------
    # BACK TO ARO, SEARCH ON KEFF WITH SAVED RCCA STRENGTHS
    # --------------------------------------------------
    case = Case()
    case.title = "BACK TO ARO, SEARCH ON KEFF WITH SAVED RCCA STRENGTHS"    
    
    # add Core_State class
    # --------------------
    case.cs = Core_State()
    # add Control_Rod class
    case.cs.cr = Control_Rod()
    case.cs.cr.name = "aro"
    
    # add Search_Parameter()
    case.sp = Search_Parameter()
    case.sp.name = "eigenvalue"
    
     # print the class to file
    PrintClassCase(case,punch)          

    # --------------------------------------------------
    # N-1 FRAC INS
    # --------------------------------------------------    
    
    frac_ins = [0.03, 0.06, 0.10, 0.20, 0.30, 0.40, 0.60, 0.80, 0.90, 0.95, 1.00]
    
    for x in frac_ins:
    
        print (x)
        case = Case()
        case.title = "N-1 " + str(x) + " FRAC INS"
        
        position = round(float((afl - rod_bottom) * (1.0 - float(x))/step_size),0)
        
        # add Core_State()
        # ----------------
        case.cs = Core_State()
        # add Control_Rod
        case.cs.crr = Control_Rod()
        case.cs.crr.name = "ALL"
        case.cs.crr.position = position
        # add Control Rod
        case.cs.cr = Control_Rod()
        case.cs.cr.name = "WSR"
        case.cs.cr.position = ARO
        
        # print the class to file
        PrintClassCase(case,punch)             

    punch.write("/run")
    
    punch.close()
    
    print ("Punched TripShape "+str(burnup)+" MWD/MTU file!\t\t" + punch_path)
    
    return punch_path

#-----------------------------------------------------------------------------
def Rod_Misalignment(window,job_number,inputpath,list_of_burnups):
# Punch Rod Misalignment calculations
    
    AO_target =[]
    BU =[]
    punch_path = "punch/"+job_number+"_"+window+"_Rod_Misalignment.in"
    
    
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
    # Extract burnups from SE-General into a separate 1D array
    for x in SE_General:
        temp1 = float(x[14])
        temp2 = float(x[1])
        AO_target.append(temp1)
        BU.append(temp2)
    
    # ----------------------------------
    # Get the control rod IDs
    CR_id = GetRCCAs (inputpath)
    # ----------------------------------
        
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
    for req_bu in list_of_burnups:
         
        # identify the burnup index
        idx = BU.index(req_bu)
        
        # -------------
        # ARO CASE
        # -------------
        case = Case()
        case.title = window + " ARO BASE CASE"
        # write archive info    
        
        # add Archive class
        # --------------------------------------------------
        case.archive=Archive()
        case.archive.model_file= model_file
        # add Read class to Archive
        case.archive.read=Read()
        case.archive.read.name= SE_General[idx][SE_length-2]
        
        # add Depletion class
        # --------------------------------------------------
        case.depletion=Depletion()
        case.depletion.delta_burnup=    "0"
        # add Control class
        case.depletion.control=Control()
        case.depletion.control.item=    "all"
        case.depletion.control.action=    "hold"
        
        # add Output
        # --------------------------------------------------
        case.output = Output()
        case.output.edits = "SM-General, CA-Cntrl_Rod"
        
        # print the class to file
        PrintClassCase(case,punch)

        # -------------
        # SKEW XENON
        # -------------
        case = Case()
        case.title = "SKEW XENON"
        case.depletion = Depletion()
        case.depletion.control1 = Control()
        case.depletion.control1.item = "all"
        case.depletion.control1.action = "hold"
        case.depletion.control2 = Control()
        case.depletion.control2.item = "xe"
        case.depletion.control2.action = "reconstruct"
        case.cs = Core_State()
        case.cs.control_rod = Control_Rod()
        case.cs.control_rod.name = "aro"
        case.cs.xe_shape = Xe_Shape()
        case.cs.xe_shape.delta_xenon = "-30"
        case.cs.axial_offset = AO_target[idx]+float(5.0)+float(0.5)
        #
        case.axial_offset_search = Axial_Offset_Search()
        case.axial_offset_search.parameter = "xe_delta"
        case.axial_offset_search.convergence = "0.5"
        # print the class to file
        PrintClassCase(case,punch)
        # -------------
        # TURN OFF XE_DELTA SEARCH
        # -------------
        case = Case()
        case.title = "TURN OFF XE_DELTA SEARCH"
        case.axial_offset_search = Axial_Offset_Search()
        case.axial_offset_search.parameter = "none"
        # print the class to file
        PrintClassCase(case,punch)
        # -------------
        # FULLY MISALIGNED IN (DROPPED) ROD FROM ARO LW
        # -------------
        case = Case()
        case.title = "FULLY MISALIGNED IN (DROPPED) ROD FROM ARO" + window
        case.se = Sequence()
        case.se.rw = Rod_Worth()
        case.se.rw.calculation = "worth"
        case.se.rw.type = "dropped"
        
        # create a list of control rods classes
        # for each control rod id that was read from ANC9 output do:
        # (this approach can be re-used in any other case where number of given classes is not known a priori)
        # add an instance of Control_Rod() to the case.sequence.rod_worth dictionary named after CD_id
        # add an attribute to the created Control_Rod() instance
        
        for RCCA in CR_id:
            case.se.rw.__dict__[str(RCCA)]=Control_Rod()
            case.se.rw.__dict__[str(RCCA)].name = RCCA
        # print the class to file
        PrintClassCase(case,punch)
        #
        # -------------
        # RIL BASE CASE
        # -------------
        case = Case()
        case.title = window + "RIL BASE CASE"
        #
        case.depletion = Depletion()
        case.depletion.control1 = Control()
        case.depletion.control1.item = "all"
        case.depletion.control1.action = "hold"
        case.depletion.control2 = Control()
        case.depletion.control2.item = "xe"
        case.depletion.control2.action = "reconstruct"
        #
        case.cs = Core_State()
        case.cs.control_rod = Control_Rod()
        case.cs.control_rod.ril = "true"
        case.cs.xe_shape = Xe_Shape()
        case.cs.xe_shape.delta_xenon = "-30"
        case.cs.axial_offset = AO_target[idx]+float(5.0)+float(0.5)
        #
        case.axial_offset_search = Axial_Offset_Search()
        case.axial_offset_search.parameter = "xe_delta"
        case.axial_offset_search.convergence = "0.5"
        #
        # print the class to file
        PrintClassCase(case,punch)
        #
        # -------------
        # TURN OFF XE_DELTA SEARCH
        # -------------
        case = Case()
        case.title = "TURN OFF XE_DELTA SEARCH"
        case.axial_offset_search = Axial_Offset_Search()
        case.axial_offset_search.parameter = "none"
        # print the class to file
        PrintClassCase(case,punch)
        #
        # ------------
        # FULLY MISALIGNED IN (DROPPED) ROD FROM D
        # -------------
        case = Case()
        case.title = "FULLY MISALIGNED IN (DROPPED) ROD FROM D"
        
        # print the class to file
        PrintClassCase(case,punch)
        case.se = Sequence()
        case.se.rw = Rod_Worth()
        case.se.rw.calculation = "worth"
        case.se.rw.type = "dropped"
        
        # create a list of control rods classes
        # for each control rod id that was read from ANC9 output do:
        # (this approach can be re-used in any other case where number of given classes is not known a priori)
        # add an instance of Control_Rod() to the case.sequence.rod_worth dictionary named after CD_id
        # add an attribute to the created Control_Rod() instance
        
        for RCCA in CR_id:
            case.se.rw.__dict__[str(RCCA)]=Control_Rod()
            case.se.rw.__dict__[str(RCCA)].name = RCCA
        # print the class to file
        PrintClassCase(case,punch)
        # -------------
        # RIL BASE CASE
        # -------------
        case = Case()
        case.title = window + "RIL BASE CASE"
        #
        case.depletion = Depletion()
        case.depletion.control1 = Control()
        case.depletion.control1.item = "all"
        case.depletion.control1.action = "hold"
        case.depletion.control2 = Control()
        case.depletion.control2.item = "xe"
        case.depletion.control2.action = "reconstruct"
        #
        case.cs = Core_State()
        case.cs.control_rod = Control_Rod()
        case.cs.control_rod.ril = "true"
        case.cs.xe_shape = Xe_Shape()
        case.cs.xe_shape.delta_xenon = "-30"
        case.cs.axial_offset = AO_target[idx]+float(5.0)+float(0.5)
        #
        case.axial_offset_search = Axial_Offset_Search()
        case.axial_offset_search.parameter = "xe_delta"
        case.axial_offset_search.convergence = "0.5"
        #
        # print the class to file
        PrintClassCase(case,punch)
        #
        # -------------
        # TURN OFF XE_DELTA SEARCH
        # -------------
        case = Case()
        case.title = "TURN OFF XE_DELTA SEARCH"
        case.axial_offset_search = Axial_Offset_Search()
        case.axial_offset_search.parameter = "none"
        # print the class to file
        PrintClassCase(case,punch)
        #
        # ------------
        # FULLY MISALIGNED OUT (STUCK) ROD FROM D-IN
        # -------------
        case = Case()
        case.title = "FULLY MISALIGNED IN (DROPPED) ROD FROM D"
        #
        case.census = Census()
        case.census.perform_calculation = "true"
        # fdh_limit value is not used in the calculation
        # but a value must be provided if it does not exist on the archive
        case.census.fdh_limit = "1.62"
        #
        case.output = Output()
        case.output.edits = "standard, CA-Power, CA-Fdh, SM-General, CA-Fdh_Margin, CA-Fdh_Pwr_Margin, SM-Fdh_limits, SR-Fdh_limits, SI-Fdh_Limits"
        #
        case.limits = Limits()
        case.limits.fdh_limit = Fdh_Limits()
        case.limits.fdh_limit.unceratinty = Uncertainty()
        case.limits.fdh_limit.unceratinty.calculation = "0.08"
        #
        case.se = Sequence()
        case.se.rw = Rod_Worth()
        case.se.rw.calculation = "worth"
        case.se.rw.type = "stuck"
        # create a list of control rods classes
        # for each control rod id that was read from ANC9 output do:
        # (this approach can be re-used in any other case where number of given classes is not known a priori)
        # add an instance of Control_Rod() to the case.sequence.rod_worth dictionary named after CD_id
        # add an attribute to the created Control_Rod() instance
        for RCCA in CR_id:
            case.se.rw.__dict__[str(RCCA)]=Control_Rod()
            case.se.rw.__dict__[str(RCCA)].name = RCCA
        # print the class to file
        PrintClassCase(case,punch)
    punch.write("/run")
    punch.close()
    
    print ("Punched Rod Misalignment input file!\t\t" + punch_path)
    
    return punch_path

#-----------------------------------------------------------------------------
def Files_Prefix(window,inputpath):
    # Takes the ARO depletion output file and window 
    # Returns the prefix for punch files' names
    
    # Get the SM-Archive_Write edit
    #------------------------------
    edit = "SM-Archive_Write"
    SM_Archive_Write = ReadEditSingle(inputpath,edit)
    
    # Get the SI-Core_Model edit
    #------------------------------
    edit = "SI-Core_Model"
    SI_Core_Model = ReadEditSingle(inputpath,edit)
    
    plant_name = SI_Core_Model[4][1]                # get plant identifier
    
    if plant_name == 'Not':                            # check if plant name is identified
        plant_name = 'UNK'                           # if not set to the default name
    
    cycle_number = SI_Core_Model[9][1]                # get cycle number
    
    if cycle_number == 'Not':                        # check if cycle number is identified
        cycle_number == 'UNK'                        # if not set to the default name
    
    if plant_name == 'KOE':
        plant_name = 'KOE1'
    
    identifier = plant_name +'C'+ cycle_number + '_' + window
    
    return identifier