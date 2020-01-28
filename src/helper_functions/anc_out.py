# RECORD OF REVISION
# 
# Date(DD/MM/YYY) Changes         Programmer 
# ==============  =======         ==========
# 30/10/2018      Original issue  K. Luszczek (Westinghouse Sweden)
import math as m

#-----------------------------------------------------------------------------
class ANC9_Output_File:
    # Call when instance is created
    def __init__(self, anc_output_file):
        self.anc_output = anc_output_file
        
    # Get a single selected edit
    def GetSingle(self,edit):
        self.edit = ReadEditSingle(self.anc_output,edit)
        return self.edit
        
    # Get a multiple selected edit:
    def GetMultiple(self,edit):
        self.edit = ReadEditMutliple(self.anc_output,edit)
        return self.edit
        
    # Get model_file
    def ModelFile(self):
        # Get the SM-Archive_Write edit
        edit_to_get = "SM-Archive_Write"
        SM_Archive_Write = ReadEditSingle(self.anc_output,edit_to_get)
        # Define the model file
        return SM_Archive_Write[3][1]
        
    # Get CASE names
    def CaseNames(self):
        edit_to_get = "SE-General"
        SE_General = ReadEditSingle(self.anc_output,edit_to_get)
        SE_length=int(SE_General_length(self.anc_output))
        case_names = list()
        for x in SE_General:
            case_names.append(x[SE_length-2])
        return case_names

#-----------------------------------------------------------------------------
def ReadEditSingle(filename, edit, NOTRUNCATE="false"):
# Function to read the selected edit.
# Use for edits that appear only once.
# Takes and edit and ANC output filepath as input.
# Skip split and truncation if NOTRUNCATE is different than false.
#
	# Variable dictionarty
	# ========================================================
	# Input:
	# =======
	# filename, f	: input file
	# edit			: name of an ANC9 edit
	#s
	# In code:
	# =======
	# flag 			: flag to start reading from file
	#
	# Output: 
	# =======
	# output 		: an output arrays of string
	# 
	
	# iniitalize variables
	flag = 0
	output = list()
	edit_end = "End-Edit"
	
	# ========================================================
	# open ANC9 output file
	try:
		f = open(filename, "r")
	except IOError:
		print("Could not open file")
		f.close()
		return 0
	
	# ========================================================	
	# read line by line
	for line in f:
		#check if the line begins with ANC edit
		if line.startswith(edit):
			flag = 1
			
		if flag==1:
			output.append(line)
			
			if line.startswith(edit_end):
				break
	
	if (NOTRUNCATE == "false"):
		# truncate and split the edit as needed
		output=TruncateEdit(output,edit)
	else:
		output=output
		
	return output

#-----------------------------------------------------------------------------
def SE_General_length(filename):
# Function used for determining the SE_General length.
# It returns the number of elements in the title row of SE-General.
# This value is needed in when trying to locate other data in the SE-General edit (e.g. Archive name index)
# This length differs depending on the number of RCCA groups in the model.

	flag = 0
	output = list()
	edit = "SE-General"
	edit_end = "End-Edit"
	
	# ========================================================
	# open ANC9 output file
	try:
		f = open(filename, "r")
	except IOError:
		print("Could not open file")
		return 0
	
	
	# read line by line
	for line in f:
		#check if the line begins with ANC edit
		if line.startswith(edit):
			flag = 1
			
		if flag==1:
			output.append(line)
			
			if line.startswith(edit_end):
				break
	
	# truncate and split the edit as needed
	del output[0:4]
	del output[-1]
	del output[-1]		
	
	output=SplitBlank(output)	
	
	output = len(output[0])
	
	return output

#-----------------------------------------------------------------------------
def ReadEditMultiple(filename, edit):
# Function to read the selected edit.
# Use for edits that appear multiple times in the output file.
# It saves each edit as a subsequent list element.
# Takes an edit and ANC output filepath as input.
# Each edit is a itself a list of elements split on the blank character.
#
	# Variable dictionary
	# ========================================================
	# Input:
	# =======
	# filename, f		: input file
	# edit			: name of an ANC9 edit
	#s
	# In code:
	# =======
	# flag 			: flag to start reading from file
	#
	# Output: 
	# =======
	# output 		: an output arrays of string
	#
	# ========================================================	
	
	# initialize some variables
	flag = 0
	output = list()
	edit_output = list()
	edit_end = "End-Edit"
	
	# ========================================================
	# open ANC9 output file
	try:
		f = open(filename, "r")
	except IOError:
		print("Could not open file")
		f.close()
		return 0
	
	# index to track case numbers that were read
	# read line by line
	for line in f:
		#check if the line begins with ANC edit
		if line.startswith(edit):
			flag = 1
			
			# clean the edit_output list
			edit_output=list()
			
		if flag==1:
		
			edit_output.append(line)
			
			if line.startswith(edit_end):
				# append entire block to the output
				# reset writing flag
				output.append(edit_output)
				flag = 0
	
	# truncate and split the edit as needed
	output=TruncateEditMultiple(output,edit)
	
	return output
    
#-----------------------------------------------------------------------------
def ReadEditMultipleANC8(filename, edit):
# Function to read the selected edit.
# Use for edits that appear multiple times in the output file.
# It saves each edit as a subsequent list element.
# Takes an edit and ANC output filepath as input.
# Each edit is a itself a list of elements split on the blank character.
#
	# Variable dictionary
	# ========================================================
	# Input:
	# =======
	# filename, f		: input file
	# edit			: name of an ANC8 edit
	#s
	# In code:
	# =======
	# flag 			: flag to start reading from file
	#
	# Output: 
	# =======
	# output 		: an output arrays of string
	#
	# ========================================================	
	
	# initialize some variables
	flag = 0
	output = list()
	edit_output = list()
	edit_end = " E-END"
	
	# ========================================================
	# open ANC9 output file
	try:
		f = open(filename, "r")
	except IOError:
		print("Could not open file")
		f.close()
		return 0
	
	# index to track case numbers that were read
	# read line by line
	for line in f:
		#check if the line begins with ANC edit
		if line.startswith(edit):
			flag = 1
			
			# clean the edit_output list
			edit_output=list()
			
		if flag==1:
		
			edit_output.append(line)
			
			if line.startswith(edit_end):
				# append entire block to the output
				# reset writing flag
				output.append(edit_output)
				flag = 0
	
	# truncate and split the edit as needed
	output=TruncateEditMultiple(output,edit)
	
	return output
#-----------------------------------------------------------------------------
def ReadEditSingleANC8(filename, edit, NOTRUNCATE="false"):
# Function to read the selected edit.
# Use for edits that appear only once.
# Takes and edit and ANC output filepath as input.
# Skip split and truncation if NOTRUNCATE is different than false.
#
	# Variable dictionarty
	# ========================================================
	# Input:
	# =======
	# filename, f	: input file
	# edit			: name of an ANC9 edit
	#s
	# In code:
	# =======
	# flag 			: flag to start reading from file
	#
	# Output: 
	# =======
	# output 		: an output arrays of string
	# 
	
	# iniitalize variables
	flag = 0
	output = list()
	edit_end = " E-END"
	
	# ========================================================
	# open ANC9 output file
	try:
		f = open(filename, "r")
	except IOError:
		print("Could not open file")
		f.close()
		return 0
	
	# ========================================================	
	# read line by line
	for line in f:
		#check if the line begins with ANC edit
		if line.startswith(edit):
			flag = 1
			
		if flag==1:
			output.append(line)
			
			if line.startswith(edit_end):
				break
	
	if (NOTRUNCATE == "false"):
		# truncate and split the edit as needed
		output=TruncateEdit(output,edit)
	else:
		output=output
		
	return output
#-----------------------------------------------------------------------------
def TruncateEdit(output,edit):
# Function to truncate edit read by ReadEdit function. (Single edit)
# Takes untruncated list and edit as in input.
# Truncation rules are specified based on the edit passed to the function.
# Some edits do not require truncations thus are no lines are removed in such cases.
# 
# All edits are additionally split on the blank character.
#
# Returns truncated and split list.

	if edit=="SE-General":
		# do truncation
		del output[0:5]
		del output[-1]
		del output[-1]	
		
		# split elements of and edits using blanks as separator
		output=SplitBlank(output)
	elif edit == "SM-Census " or edit == "CA-Cntrl_Rod":
		output = output
	elif edit == "SA-CR_Loc":
		del output[0:5]
		del output[-1]
		del output[-1]
		output=SplitBlank(output)
	else:
	#edit =="SM-Archive_Write" or edit =="SA-Placement" or  edit == "SI-Core_Model" or edit == "SS-Stuck"
		output=SplitBlank(output)	
		
	return output

#-----------------------------------------------------------------------------
def TruncateEditMultiple(output,edit):
# Function to truncate edit read by ReadEdit function. Version for edits saved at several burnup steps.
# Takes untruncated list and edit as in input.
# Truncation rules are specified based on the edit passed to the function.
# Some edits do not require truncations thus are no lines are removed in such cases.
# 
# All edits are additionally split on the blank character.
#
# Returns truncated and split list.

	if edit=="SM-Census ":
	
		output_processed=list()
		
		for case in output:
			#print case
			# do truncation
			del case[0:7]
			del case[-1]
			del case[-1]
			
		# split elements of and edits using blanks as separator
			case2=()
			case2=SplitBlank(case)
			#print case2
			output_processed.append(case2)
	
	else:
		output_processed=list()
		
		for case in output:
			case2=()
			case2=SplitBlank(case)
			
			output_processed.append(case2)
		
	return output_processed

#-----------------------------------------------------------------------------
def SplitBlank(output):
# Function to split each element of the list into separate lists using blanks as separators.

	output2 =list()
	
	for x in output:
		output2.append(x)
		output2[-1]=output2[-1].split()
	
	return output2

#-----------------------------------------------------------------------------
def GetRCCAs(inputpath):
# Function returns a list of RCCAs from the outputfile.
    CR_id =list()
    edit = "CA-Cntrl_Rod"
    CA_Cntrl_Rod = ReadEditSingle(inputpath,edit)
    for line in CA_Cntrl_Rod:
        #print(line.split("|"))
        for x in line.split("|"):
            if len(x.strip()) == 4:
                CR_id.append(x.strip())
    return CR_id

#-----------------------------------------------------------------------------
def CensusOut(filename,summary):
# Function to process CENSUS process for the miniRSAC script.
# Gathers census data from output
# Writes (appends) to the summary file of choice. 
# The powers of 0% and 30% are chosen for Krsko. 
# TO DO: modify so that powers are passed on as a list 
#        and data is gathered for all the powers on the list.

	power1= "0.000"
	power2= "30.000"
	census = list()
	census_power1 = list()
	census_power2 = list()
	edit = "SM-Census "
	
	census =ReadEditMultiple(filename,edit)
	
	edit = "SI-Archive_Read"
	SM_Archive_Read = ReadEditSingle(filename,edit)
	
	# put together census for power 1 and power 2
	for case in census:
		for power_line in case:
			if power_line[0] == power1:
				census_power1.append(power_line[1])
			elif power_line[0] == power2:
				census_power2.append(power_line[1])
	
	
	try:
		w = open(summary, "a")
	except IOError:
		print("Could not open file")
		w.close()	
	
	w.write("**************************************************************************************************************************************\n")
	w.write("ROD CENSUS SUMMARY\n")
	w.write("-------\n")
	w.write("Read CS file: %s\n"  % SM_Archive_Read[3][1])
	w.write("MD5 Hash:      %s\n" % SM_Archive_Read[6][2])
	w.write("-------\n")
	w.write("Burnup:\tCensus at power:\n" )
	w.write("MWD/MTU\t%s\t%s\n" %(power1, power2))
	w.write("======\t=====\t=====\n")
	
	edit = "SE-General"
	SE_General = ReadEditSingle(filename,edit)
	
	for idx, case in enumerate(census_power1):
		w.write("%s\t%s\t%s\n" % (SE_General[idx][1].ljust(6), census_power1[idx], census_power2[idx]))

	edit = "SE-Warning"
	SE_Warning = ReadEditSingle(filename,edit,"true")
	w.write("-------\n")
	w.write("\nWarnings from the output file:\n")
	if (len(SE_Warning) == 0):
		w.write("None\n")
	else:
		for x in SE_Warning:
			w.write("%s" %x)

	w.close()

#-----------------------------------------------------------------------------
def WSR_lookup(WSR_output):
# Function that returns the ID of the RCCA with the highest worth. 
# Works only is SS-Stuck edit is present in the output file.

	SS_stuck = ReadEditSingle(WSR_output,"SS-Stuck")
	
	for line in SS_stuck:

		if line:						# check if list is empty
			if (line[0] == "Highest"):
				WSR = line[4]
	
	return WSR

#-----------------------------------------------------------------------------
def DinDeplOut(outputfile, summary):
# Gathers Din Depletion summary from the file for purposes of the "miniRSAC" script.
# Writes (appends) to the summary file of choice. 

	try:
		w = open(summary, "a")
	except IOError:
		print("Could not open file")
		w.close()
	
	edit = "SM-Archive_Write"
	SM_Archive_W     = ReadEditMultiple(outputfile, edit)
	SM_Archive_Write = SM_Archive_W[-1]
	
	edit = "SI-Archive_Read"
	SM_Archive_Read = ReadEditSingle(outputfile,edit)

	edit = "SE-General"
	SE_General = ReadEditSingle(outputfile,edit,"true")
	
	edit = "SE-Warning"
	SE_Warning = ReadEditSingle(outputfile,edit,"true")
	w.write("**************************************************************************************************************************************\n")
	w.write("D-IN DEPLETION SUMMARY\n")
	w.write("Output file: %s\n" % outputfile)
	w.write("-------\n")
	w.write("Read CS file: %s\n"  % SM_Archive_Read[3][1])
	w.write("MD5 Hash:      %s\n" % SM_Archive_Read[6][2])
	w.write("-------\n")
	w.write("Write CS file: %s\n" % SM_Archive_Write[3][1])
	w.write("MD5 Hash:      %s\n" % SM_Archive_Write[6][2])
	w.write("-------\n")
	w.write("Depletion summary:\n")
	
	for x in SE_General:
		w.write("%s" %x)
	w.write("-------\n")
	w.write("Warnings from the output file:\n")
	
	if (len(SE_Warning) == 0):
		w.write("None\n")
	else:
		for x in SE_Warning:
			w.write("%s" %x)
	
	w.close()

#-----------------------------------------------------------------------------
def WSROut(WSR,outputfile,summary):
# Gathers Worst Stuck Rod search summary from the file for purposes of the "miniRSAC" script.
# Writes (appends) to the summary file of choice. 

	try:
		w = open(summary, "a")
	except IOError:
		print("Could not open file")
		w.close()	
		
	edit = "SE-Warning"
	SE_Warning = ReadEditSingle(outputfile,edit,"true")
	
	edit = "SI-Archive_Read"
	SM_Archive_Read = ReadEditSingle(outputfile,edit)
	
	w.write("\n**************************************************************************************************************************************\n")
	w.write("WSR SUMMARY\n")
	w.write("Output file: %s\n" % outputfile)
	w.write("-------\n")
	w.write("Read CS file: %s\n"  % SM_Archive_Read[3][1])
	w.write("MD5 Hash:      %s\n" % SM_Archive_Read[6][2])
	w.write("-------\n")
	w.write("WSR is: %s\n" % WSR)
	w.write("-------\n")
	w.write("Warnings from the output file:\n")
	
	if (len(SE_Warning) == 0):
		w.write("None")
	else:
		for x in SE_Warning:
			w.write("%s" %x)
		
	w.close()

#-----------------------------------------------------------------------------
def SDMOut(outputfile,summary):
# Gathers Shutdown Margin summary from the file for for purposes of the "miniRSAC" script.
# Writes (appends) to the summary file of choice. 

	
	try:
		w = open(summary, "a")
	except IOError:
		print("Could not open file")
		w.close()
		
	w.write("**************************************************************************************************************************************\n")
	edit = "SE-General"
	SE_General = ReadEditSingle(outputfile,edit)
	
	edit = "SE-Warning"
	SE_Warning = ReadEditSingle(outputfile,edit,"true")	
	
	edit = "SI-Archive_Read"
	SM_Archive_Read = ReadEditSingle(outputfile,edit)
	
	w.write("SDM SUMMARY\n")
	w.write("\nOutput file: %s\n" % outputfile)
	w.write("-------\n")
	w.write("Read CS file: %s\n"  % SM_Archive_Read[3][1])
	w.write("MD5 Hash:      %s\n" % SM_Archive_Read[6][2])
	w.write("-------\n")
	w.write("\nSDM Eigenvalue Rackup:\n")
	
	for idx, case in enumerate(SE_General):
		text = "k"+str(idx+1)+" = " + str(case[3])
		w.write("%s\n" %text)
	w.write("-------\n")
	w.write("\nSDM Rackup:\n")
	
	value1 = round(m.log(float(SE_General[2][3])/float(SE_General[5][3]))*10**5)
	w.write("Calculated SDM   : %s\n" % value1)
	
	value2 = round(0.10*m.log(float(SE_General[3][3])/float(SE_General[5][3]))*10**5)
	w.write("Rod worth uncert.: %s\n" % value2)
	w.write("Void             : 50\n")
	
	value3 = value1 - value2 - 50
	w.write("True SDM         : %s\n" % value3)	
	w.write("-------\n")
	w.write("\nWarnings from the output file:\n")
	if (len(SE_Warning) == 0):
		w.write("None\n")
	else:
		for x in SE_Warning:
			w.write("%s" %x)
		
	w.close()

#-----------------------------------------------------------------------------
def MTCOut(outputfile,summary):
# Gathers Moderator Temperature Coefficient from the file for purposes of the "miniRSAC" script.
# Writes (appends) to the summary file of choice. 
	
	try:
		w = open(summary, "a")
	except IOError:
		print("Could not open file")
		w.close()

	edit = "SE-Warning"
	SE_Warning = ReadEditSingle(outputfile,edit,"true")	
	
	edit = "SI-Archive_Read"
	SM_Archive_Read = ReadEditSingle(outputfile,edit)
	
	edit = "SE-Coefficient"
	SE_Coefficient = ReadEditSingle(outputfile,edit, "true")
	
	w.write("**************************************************************************************************************************************\n")
	w.write("MTC SUMMARY\n")
	w.write("-------\n")
	w.write("Read CS file: %s\n"  % SM_Archive_Read[3][1])
	w.write("MD5 Hash:      %s\n" % SM_Archive_Read[6][2])
	w.write("-------\n")
	
	for x in SE_Coefficient:
		w.write("%s" %x)
	
	SE_Coefficient = ReadEditSingle(outputfile,edit)
	
	# Truncate SE_Coefficient
	del SE_Coefficient[0:6]
	del SE_Coefficient[-1]
	del SE_Coefficient[-1]
	w.write("-------\n")
	w.write("\nBOC MTC           : %s at %s MWD/MTU\n" %(SE_Coefficient[0][-2], SE_Coefficient[0][3]))
	
	maxMTC = int(0) #row index
	maxCBC = int(0) #row index
	# Look for the least negative MTC and max CBC
	for idx, case in enumerate(SE_Coefficient):
		if (float(SE_Coefficient[idx][-2]) > float(SE_Coefficient[maxMTC][-2])):
			maxMTC = idx
		if (float(SE_Coefficient[idx][5])  > float(SE_Coefficient[maxCBC][5])):
			maxCBC = idx

	w.write("Least negative MTC: %s at %s MWD/MTU\n" %(SE_Coefficient[maxMTC][-2], SE_Coefficient[maxMTC][3]))
	w.write("Maximum HZP CBC   : %s at %s MWD/MTU\n" %(SE_Coefficient[maxCBC][5],  SE_Coefficient[maxCBC][3]))
	
	
	w.write("-------\n")
	w.write("\nWarnings from the output file:\n")
	if (len(SE_Warning) == 0):
		w.write("None\n")
	else:
		for x in SE_Warning:
			w.write("%s" %x)
		
	w.close()	

#-----------------------------------------------------------------------------
def FdhRILOut(outputfile,summary):
# Gathers Fdh at RIL data from the  output file for purposes of the "miniRSAC" script.
# Writes (appends) to the summary file of choice. 

	try:
		w = open(summary, "a")
	except IOError:
		print("Could not open file")
		w.close()
		
	w.write("**************************************************************************************************************************************\n")
	w.write("FDH RIL SUMMARY\n")
	
	edit = "SE-Warning"
	SE_Warning = ReadEditSingle(outputfile,edit,"true")	
	
	edit = "SE-General"
	SE_General = ReadEditSingle(outputfile,edit)
	
	edit = "SI-Archive_Read"
	SM_Archive_Read = ReadEditSingle(outputfile,edit)
	
	maxFdh = int(0) #row index
	
	w.write("-------\n")
	w.write("Read CS file: %s\n"  % SM_Archive_Read[3][1])
	w.write("MD5 Hash:      %s\n" % SM_Archive_Read[6][2])
	w.write("-------\n")
	
	for idx, case in enumerate(SE_General):
		if (float(SE_General[idx][12]) > float(SE_General[maxFdh][12])):
			maxFdh = idx

	w.write("\nMaximum Fdh: %s at %s MWD/MTU\n" % (float(SE_General[maxFdh][12]), SE_General[maxFdh][1]))
	w.write("-------\n")
	w.write("\nWarnings from the output file:\n")
	if (len(SE_Warning) == 0):
		w.write("None\n")
	else:
		for x in SE_Warning:
			w.write("%s" %x)
		
	w.close()			

#-----------------------------------------------------------------------------
def CaEditsMax(outputfile,edit):
# get the maximum value from the bottom of CA-* edit for each burn-up step.
# There are several CA-* with only one value of interest given at the bottom on that edit.
# Returns a list comprised of data from all instances of a given edit found in the output file.

	CA_Edit = ReadEditMultiple(outputfile,edit)
	
	max_at_each_step = list()
	
	for x in CA_Edit:
		max_at_each_step.append(x[-3][0])

	return max_at_each_step

#-----------------------------------------------------------------------------
def PhaOut(outputfile):
# Calculates Pha = CA-Power_max * CA-Fdh_max at the burnup step with maximum Fdh.
# Returns calculated Pha.

	
	edit = "CA-Power"
	max_CA_power = CaEditsMax(outputfile,edit)
	
	edit = "CA-Fdh"
	max_CA_fdh = CaEditsMax(outputfile,edit)
	
	Pha = 0
	max_Fdh = 0

	# Look for the maximum Fdh and update Pha
	for idx, x in enumerate(max_CA_fdh):
		if (float(x) > float(max_Fdh)):
			max_Fdh = x
			Pha = float(x)/float(max_CA_power[idx])
			
	return Pha

#-----------------------------------------------------------------------------
def RIAOut(outputfile):
# The RIA is obtained as the maximum over all power levels, of the reactivity difference
# between the HFP, ARO eigenvalue and the eigenvalue with the rods at the RIL,
# considering the results from both the jobs described above.
#
# RIA = RodWorth_RIL - PD_1.0->P
#
# Reactivity difference between points checks out because we insert rods (RodWorth) and decrease power (PD) at the same time.
# 
	edit = "SE-General"
	SE_General = ReadEditSingle(outputfile,edit)

	reactivity_overall = list()
	positive_AO = list()
	negative_AO = list()
	burnup_step = list()
	reactivity_BUstep = list()
	current_bu = SE_General[0][-3]
	# Break SE_General Edit into lists for each reactivity point
	for idx, x in enumerate(SE_General):

		if (x[-3] == current_bu): # if the entry is for the current burn-up, add the reactivity to a proper list
			if(x[-1] == "plus"):  # check if the entry was calculated for positively or negatively skewed AO
				positive_AO.append(x[3])
				burnup_step.append(x[1])
			else:
				negative_AO.append(x[3])
				burnup_step.append(x[1])
		else:					  # if the entry differs (it means that the new burn-up step is being read) do the following:
			current_bu = x[-3]    # change the current BU
			reactivity_BUstep.append(burnup_step) # add the "burnup_step" list as an element to the reactivity_BUstep list
			reactivity_BUstep.append(positive_AO) # add the "positive_AO" list as an element to the reactivity_BUstep list 
			reactivity_BUstep.append(negative_AO) # add the "positive_AO" list as an element to the reactivity_BUstep list
			
			reactivity_overall.append(reactivity_BUstep) # add the "reactvitiy_BUstep" list as an element to the reactivity burn-up
			
			burnup_step = list() # reset the supporting lists
			positive_AO = list()
			negative_AO = list()
			reactivity_BUstep = list()
			
			if(x[-1] == "plus"):  # check if the entry was calculated for positively or negatively skewed AO
				positive_AO.append(x[3])
				burnup_step.append(x[1])
			else:
				negative_AO.append(x[3])
				burnup_step.append(x[1])		

	# add the last step values
	reactivity_BUstep.append(burnup_step) # add the "burnup_step" list as an element to the reactivity_BUstep list
	reactivity_BUstep.append(positive_AO) # add the "positive_AO" list as an element to the reactivity_BUstep list 
	reactivity_BUstep.append(negative_AO) # add the "positive_AO" list as an element to the reactivity_BUstep list
	reactivity_overall.append(reactivity_BUstep) # add the "reactvitiy_BUstep" list as an element to the reactivity burn-up

	# The "reactivity_overall" list should have the following structure
	# Level 1: Lists of k_inf for each burnup step: reactivity_overall[1]
	# Level 2: Lists of k_inf for either AO+ or AO-: reactivity_overall[1][2]
	# Level 3 Index 0:   Element (burnup step) for each case sequentially read from SE-General (can be used for navigation in later processing): reactivity_overall[1][2][0] 
	# 		  Index 1-2: Element (k_inf value) at given burn-up point and AO in order it was read from SE-General: reactivity_overall[1][2][3]
	# 
	# First element is k_inf for HFP ARO with skewed Xenon. K_inf at RIL from 1.0 to 0.0 relative power follow afterwards.
	
	RIA = list()


	for idx, x in enumerate(reactivity_overall):
			
			# x comprises of: x[0] list of burnup values
			#                 x[1] kinf for positivly skewed AO
			#                 x[2] kinf for negatively skewed AO
			#if (idx == 0): #skip the burnup values
			#	continue 
			#else:
			max_RIA = float(0)
			
				
			for idy, y in enumerate(x): 
				
				if (idy == 0):
					burnup = int(y[idy])
					continue
					
				kinf_ARO = float(y[0])
				
				RIA_HFP=round(m.log(kinf_ARO/float(y[1]))*100000)
				
				#print("%5d %f"%(burnup,RIA_HFP))
				
				
				for idz, z in enumerate(y):
					if (idz == 0):
						continue
					else:

						current_RIA = m.log(kinf_ARO/float(z))
						
						print_RIA =current_RIA *100000
						print("%.0f"%print_RIA)
						
						
						if (current_RIA > max_RIA):
							max_RIA = current_RIA
							
				print("%5d %.0f  %.0f"%(burnup,RIA_HFP,max_RIA*100000)) 
				
			add_to_RIA = list()
			add_to_RIA.append(x[0][idy])
			add_to_RIA.append(round(max_RIA*100000))
				
			RIA.append(add_to_RIA)	

	
	return RIA

#-----------------------------------------------------------------------------
def ReOut(outputfile,summary):
# Gathers Rod Ejection analysis summary
# Writes (appends) to the summary file of choice. 

	try:
		w = open(summary, "a")
	except IOError:
		print("Could not open file")
		w.close()
	
	output = list()

	
	edit = "SE-Warning"
	SE_Warning = ReadEditSingle(outputfile,edit,"true")	
	
	edit = "SS-Ejected"
	SS_Ejected = ReadEditSingle(outputfile,edit)
	
	edit = "SE-General"
	SS_General = ReadEditSingle(outputfile,edit)
	
	step  = SS_General[0][-1] # follows the naming convention used for the first case in "RodEjectionHzp_Punch" and "RodEjectionHfp_Punch"
	power = SS_General[0][-2] # follows the naming convention used for the first case in "RodEjectionHzp_Punch" and "RodEjectionHfp_Punch"
	
	w.write("**************************************************************************************************************************************\n")
	w.write("%s %s Rod Ejection Summary\n"%(step,power))
	

		
	maxFq    = int(0)
	maxFqBu  = int(0)
	maxWorth = int(0)
	
	for idx, case in enumerate(SS_Ejected):
		if len(case) != 0:
			if case[0].isdigit():
				if (float(case[6]) >= maxFq):
					maxFq = float(case[6])
					if(float(case[8]) > maxFqBu):
						maxFqBu = float(case[8])
				if (float(case[2]) > maxWorth):
					maxWorth = float(case[2])

	edit = "SS-Ejected"
	SS_Ejected = ReadEditSingle(outputfile,edit,"true") # dont split SS_Ejected into single words. Keep lines as they are				
					
	for x in SS_Ejected:
		w.write("%s" %x)
					
	# add uncertainties depending on whether HFP or HZP
	if (power == "HFP"):
		maxWorth = maxWorth * 1.10
		maxFq = maxFq * 1.13
		w.write("\nRod Worth uncertainty: 10%\n")
		w.write("Rod Worth uncertainty: 13%\n")
	elif (power == "HZP"):
		maxWorth = maxWorth * 1.12
		maxFq = maxFq * 1.23
		w.write("\nRod Worth uncertainty: 12%\n")
		w.write("Rod Worth uncertainty: 23%\n")
	
	w.write("Max rod worth with uncertainty: %.1f\n" %(maxWorth))
	w.write("Max Fq        with uncertainty: %.2f\n" %(maxFq))
	w.write("Hot spot burn-up:               %.0f\n" %(maxFqBu))
	
	output.append(power)
	output.append(step)
	output.append(maxWorth)
	output.append(maxFq)
	output.append(maxFqBu)
	
	
	w.write("\nWarnings from the output file:\n")
	if (len(SE_Warning) == 0):
		w.write("None\n")
	else:
		for x in SE_Warning:
			w.write("%s" %x)
	
	w.close()
	
	return output

#-----------------------------------------------------------------------------
def FindMaxSingleRowList(list, initial_value):
# Finds and returns a maximum numerical value in a single row list.
# All characters in the list must be numerical.

	
	max = float(initial_value)
	
	for x in list:
		if (float(x) > max):
			max = float(x)

	return max

#-----------------------------------------------------------------------------
def N_1_worth_RIA_from_SDM(outputfile):
# Determines HZP ( N-1 worth - RIA ) from the SDM calculations 
		
	edit = "SE-General"
	SE_General = ReadEditSingle(outputfile,edit)

	for idx, case in enumerate(SE_General):
		text = "k"+str(idx+1)+" = " + str(case[3])
		
	value2 = round(m.log(float(SE_General[3][3])/float(SE_General[5][3]))*10**5)
	
	return value2
