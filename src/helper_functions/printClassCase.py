# RECORD OF REVISION
# 
# Date(DD/MM/YYY) Changes         Programmer 
# ==============  =======         ==========
# 30/10/2018      Original issue  K. Luszczek (Westinghouse Sweden)
#
#
# Print the class to file
# Takes class to be printed and a file name as an argument
#
from classes import *
#
def PrintClassCase(case,f):
	# TO DO: check if file is opened
	
	# append all classes to the lookup list
    classes = list()
    classes.append(Archive)
    classes.append(Read)
    classes.append(Depletion)
    classes.append(Control)
    classes.append(Weight_Corrector)
    classes.append(Core_State)
    classes.append(Axial_Offset_Search)
    classes.append(Solution_Control)
    classes.append(Convergence)
    classes.append(Iteration)
    classes.append(Control_Rod_Adjust)
    classes.append(Output)
    classes.append(Traces)
    classes.append(Axial)
    classes.append(Control_Rod)
    classes.append(Sequence)
    classes.append(Base_Case)
    classes.append(Step)
    classes.append(Coefficient)
    classes.append(Units)
    classes.append(Search_Parameter)
    classes.append(Model_Symmetry)
    classes.append(Rod_Worth)
    classes.append(Census)
    classes.append(Xe_Shape)
    classes.append(Core_Parameters)
    classes.append(Inlet_Temperature)
    classes.append(Breakpoint)
    classes.append(Write)
    classes.append(Repeat)
    classes.append(Feedback)
    classes.append(Groups)
    classes.append(Limits)
    classes.append(Region)
    classes.append(Fdh_Limits)
    classes.append(RodBowUncertainty)
    classes.append(BurnupRelation)
    classes.append(Uncertainty)
    classes.append(Limit_Slope)
	
    tab = -8
    Print(case,f,classes,tab)

#-----------------------------------------------------------------------------
# Function to print class attributes
# function is recursive : if another class encountered it calls itself
# tab variable controls the depth of indentation
# Case: 	instance of a class to be printed
# f: 		file to write to
# classes:	list of all legal classes
# tab:		number of columns the tab should be
def Print(case, f,classes,tab):
	
	# increase number of tab by 8 (default length of one tab)
	tab = tab + 8
	
	# open the class text block
	f.write(("\t"+case.class_name+":\n").expandtabs(tab))
	
	# read class attributes and check if any are of class type
	for att in sorted(vars(case).keys()):
		# flag to mark if attribute was passed on the Print
		flag = 0
		for cl in classes:
		
			if isinstance(vars(case)[att],cl):	
			# if attribute is on the list use Print function
			# get name from cl
				flag = 1
				Print(vars(case)[att],f,classes,tab)
		
		# ---------------------------------------------
		# if not passed to Print_Level_I and not empty print to file	
		if flag == 0:
			name = att	
			value = str(vars(case)[att])
			if not (value == "" or name == "level" or name=="class_name"):
				f.write(("\t"+name+"="+value+"\n").expandtabs(tab+8))	
	
	
	# close class block file
	f.write(("\t/"+case.class_name+"\n").expandtabs(tab))
