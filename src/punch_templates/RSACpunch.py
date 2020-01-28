# RECORD OF REVISION
# 
# Date(DD/MM/YYY) Changes         Programmer 
# ==============  =======         ==========
# 30/10/2018      Original issue  K. Luszczek (Westinghouse Sweden)
#
#
import os
from DinDepletionPunch import Din_depletion_punch
from FdhRilPunch import Fdh_RIL_punch
from MtcBocPunch import MTC_BOC_punch
from MtcEocPunch import MTC_EOC_punch


def puncher(*,ds,analysis):
    # determine which punch function to call
    function_to_call = globals()[analysis]
    if (ds.aro_dep_file.get()==''):
        return("Missing input parameters!")

    if (analysis == "Din_depletion_punch"):
        if ((ds.lead_bank.get() == '') or 
            (ds.percent_in.get() == '') or
            (ds.aro_dep_file.get() == '')):
            return ("Missing input parameters!")
        else:
            punchpath = "punch/"+ str(ds.job_id.get())+"_"+str(ds.plant_id.get())+ "_DIN_" + str(ds.lead_bank.get())+str(ds.percent_in.get()) + ".in"
            return function_to_call(lead_bank = ds.lead_bank.get(),
                                    percent_in= int(ds.percent_in.get()),
                                    punchpath = punchpath,
                                    inputpath = ds.aro_dep_file.get() )
                                    
    elif (analysis == "Fdh_RIL_punch"):
        punchpath = "punch/"+ str(ds.job_id.get())+"_"+str(ds.plant_id.get())+"_Fdh_RIL.in"
        return function_to_call(inputpath = ds.aro_dep_file.get(),
                                punchpath = punchpath)
    elif(analysis == "MTC_BOC_punch"):
        punchpath = "punch/"+ str(ds.job_id.get())+"_"+str(ds.plant_id.get())+"_MTC_BOC.in"
        return function_to_call(inputpath = ds.aro_dep_file.get(),
                                punchpath = punchpath )

    elif(analysis == "MTC_EOC_punch"):
        punchpath = "punch/"+ str(ds.job_id.get())+"_"+str(ds.plant_id.get())+"_MTC_EOC.in"
        return function_to_call(inputpath = ds.aro_dep_file.get(),
                                punchpath = punchpath )
            
