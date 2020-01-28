# Classes
# Class build basing on manual ANC9 rev.12
# These are sort of "dummies". When creating inputs to ANC9, attributes are added to each class.
# Then the class name and its attributes are printed into the input file by a recursive procedure in printClassCase.py
class Case:	
	class_name ="case"
	def __init__(self):
	       self.title      = ""
#	       self.archive=self.Archive()
#	       self.depletion=self.Depletion()
#	       self.core_state=self.CoreState()       
class Archive:
	class_name ="archive"
# Level 2
# Contains Read
	def __init__(self):
		self.model_file         = ""
#	self.read=self.Read()	       
class Read:
# Level 1
	class_name ="read"	
	def __inint__(self):
		self.name		= ""	#
		self.secondary_file	= ""
		self.shutdown_length	= ""
class Write:
	class_name="write"
	def __init__(self):
		self.dummy = ""			
class Depletion:
# Level 2
# Contains Control and Weight_Corrector
	class_name ="depletion"	
	def __init__(self):
		self.delta		 = ""	 #Units: MWD/Mtm (SI); MWD/Mtm (W)
		self.delta_burnup	 = ""	 #Units: MWD/Mtm (SI); MWD/Mtm (W)
		self.delta_time	 = ""		 #Units: hr (SI); hr (W)
		self.deplete_reference  = ""	 #Default: True
#		self.control=self.Control()
#		self.weight_corrector=self.Weight_Corrector() 	 
class Control:
# Level 1
	class_name ="control"	
	def __init__(self):
		self.action	= ""	#
		self.item	= ""	#
class Weight_Corrector:
# Level 1
	class_name ="weight_corrector"
	def __init__(self):
		self.fuel	= ""	#
		self.xe		= ""	#
class Core_State:
	class_name ="core_state"
	def __init__(self):
		self.axial_adjustment		= ""	#
		self.axial_offset		= ""	#Units: % (SI); % (W)
		self.b10_percentage		= ""	#Units: a/o (SI); a/o (W)
		self.boron_concentration	= ""	#Units: ppm (SI); ppm (W)
		self.buckling			= ""	#Units: 1/cm**2 (SI); 1/cm**2 (W)
		self.control_rod		= ""	#
		self.delta_axial_offset		= ""	#Units: % (SI); % (W)
		self.delta_eigenvalue		= ""	#
		self.eigenvalue			= ""	#
		self.inlet_temperature		= ""	#Units: C (SI); F (W)
		self.k_bias			= ""	#
		self.pressure			= ""	#
		self.relatvie_power		= ""	#
		self.relative_power		= ""	#
		self.axial_offset		= ""	#
class Control_Rod:
	class_name ="control_rod"
	def __init__(self):
		self.name	= ""
		self.position	= ""
class Axial_Offset_Search:
# Level 2
# Contains Control Rod
	class_name ="axial_offset_search"	
	def __init__(self):
		self.convergence	= "" #
		self.maximum_value	= "" #	
		self.measurement	= "" #
		self.minimum_value	= "" #
		self.parameter		= "" #
#		self.control_rod	= "" #
# 4.68
class Solution_Control:
# Level 2
# Contains Convergence, Iteration, Control_Rod_Adjust
	class_name ="solution_control"	
	def __init__(self):
		self.initialize_flux			= ""
		self.limits_margin_calculation		= ""
		self.perform_pin_calculation		= ""
		self.perform_solution			= ""
		self.perform_b10_depletion		= ""
		self.incore_detector_calculation	= "" # 4.68.8
		self.average_center_assembly		= "" # 4.68.9
		#self.control_rod_adjust			= "" # 4.68.10
		self.use_coef_crod_refl_model		= "" # 4.68.11		
# 4.68.6
class Convergence:
# Level 1
	class_name ="convergence"		
	def __init__(self):
		self.eigenvalue		= "" #
		self.flux		= "" #
		self.search		= "" #
		self.seatch_rod_position= "" #	
# 4.68.7
class Iteration:
# Level 1
	class_name ="iteration"	
	def __init__(self):
		self.maximum		= "" # 4.68.7.1 
		self.maximum_inner	= "" # 4.68.7.1
		self.outer_per_feedback	= "" # 4.68.7.3
# 4.68.10	
class Control_Rod_Adjust:
# Level 1
	class_name="control_rod_adjust"
	def __init__(self):
		self.gray	= "" # 4.68.10.1
		self.non_gray	= "" # 4.68.10.2
# 4.47
class Output:
# Level 3
# Contains Traces, Axial, Figures
	class_name="output"
	def __init__(self):
		pass
#4.47.8
class Traces:
# Level 2: contains Axial
	class_name="traces"
	def __init__(self):
		self.pin	= "" # 4.47.8.2		
#4.47.8.1		
class Axial:
# Level 1
	class_name="axial"
	def __init__(self):
		self.channel	= "" # 	4.47.8.1.1		
class Sequence:
	class_name="sequence"
	def __init__(self):
		self.base_case = ""	
class Base_Case:
	class_name="base_case"
	def __init__(self):
		self.dummy = ""		
class Step:
	class_name="step"
	def __init__(self):
		self.dummy = ""				
class Coefficient:
	class_name="coefficient"
	def __init__(self):
		self.dummy = ""	
class Units:
	class_name="units"
	def __init__(self):
		self.dummy = ""			
class Search_Parameter:
	class_name="search_parameter"
	def __init__(self):
		self.dummy = ""					
class Model_Symmetry:
	class_name="model_symmetry"
	def __init__(self):
		self.dummy = ""	
class Rod_Worth:
	class_name="rod_worth"
	def __init__(self):
		self.dummy = ""	
class Census:
	class_name="census"
	def __init__(self):
		self.dummy = ""	
class Xe_Shape:
	class_name="xe_shape"
	def __init__(self):
		self.dummy = ""	
class Core_Parameters:
	class_name="core_parameters"
	def __init__(self):
		self.dummy = ""	
class Inlet_Temperature:
	class_name="inlet_temperature"
	def __init__(self):
		self.dummy = ""	
class Breakpoint:
	class_name="breakpoint"
	def __init__(self):
		self.dummy = ""		

class Repeat:
	class_name="repeat"
	def __init__(self):
		self.dummy = ""
		
class Feedback:
	class_name="feedback"
	def __init__(self):
		self.dummy = ""		
        
class Groups:
    class_name="groups"
    def __init__(self):
        self.dummy = ""
        
class Limits:
    class_name="limits"
    def __init__(self):
        self.dummy = ""
        
class Region:
    class_name="region"
    def __init__(self):
        self.dummy = ""
        
class Limit_Slope:
    class_name="limit_slope"
    def __init__(self):
        self.dummy = ""
        
class Fdh_Limits:
    class_name="fdh_limit"
    def __init__(self):
        self.dummy = ""

class RodBowUncertainty:
    class_name="rod_bow_uncertainty"
    def __init__(self):
        self.dummy = ""
        
class BurnupRelation:
    class_name="burnup_relation"
    def __init__(self):
        self.dummy = ""
        
class Uncertainty:
    class_name="uncertainty"
    def __init__(self):
        self.dummy = ""