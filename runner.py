# RECORD OF REVISION
# 
# Date(DD/MM/YYY) Changes         Programmer 
# ==============  =======         ==========
# 30/10/2018      Original issue  K. Luszczek (Westinghouse Sweden)
#
import os
import time
import subprocess
import glob
from miniRSACpunch import Din_depletion_punch

#-----------------------------------------------------------------------------
# Function to submit, wait for jobs to complete and move jobs to output folder
# Takes a list of punch files as an argument

def Runner(inputs):
    
    # submit all input and wait for completion
    WaitForJobs(Submitter(inputs))
    
    #move all outputs and logs to an output folder
    MoveOutputs(inputs)
    
    return 0

#-----------------------------------------------------------------------------
# Function to submit jobs to the cluster
# Waits for spawned jobs to complete
# Takes a list of input files as arguments
# Returns a list of spawned jobids
def Submitter(inputs):
    # collect jobids into jobid list
    jobid = list()

    # define ANC version
    anc_ver = "980"
    for name in inputs:
        
        #construct the bsub command
        #sub = "bsub -J "+name+" run_anc -ver "+anc_ver+" -i "+name
        sub = "bsub -J "+name+" run_anc -i "+name # run with defualt ANC9 version
        #os.system(sub)
        
        sub = subprocess.Popen(sub, shell=True, stdout=subprocess.PIPE, universal_newlines = True, stderr=subprocess.STDOUT)
        # In Python 3 Popen will return bytes because of \n. Use universal_newlines to get rid of \n and for popen to return string
        sub = sub.stdout.readline().strip()
        
        # printout a message about a job being submitted
        print (sub)
        sub = SearchForDigitsInString(sub)
        
        jobid.append(sub)
        
        #print(jobid)
    return jobid
            
#-----------------------------------------------------------------------------        
# Function waits for all jobids to finish on the cluster
# Takes jobids as an argument (use Runner to start jobs and get job ids)        
                
def WaitForJobs(jobids):
    
    # set flag to 1    
    flag = 1
    while True:
        
        flag = 0
        # loop over all jobids
        for job in jobids:
            command = "bjobs "+job
            status = subprocess.Popen(command, shell=True,stdout=subprocess.PIPE, universal_newlines = True, stderr=subprocess.STDOUT)
            status = status.stdout.readlines()
            
            # if more than two lines in response the job still exists
            # if any of the jobs still exists change flag to 1 and proceed to waiting
            lines_in_response = len(status)
            
            # if only one line the job doesnt exist 
            # check if two lines in bjobs response
            # if yes: check the status of the job
            # if different than EXIT aor DONE add 1 to the flag to keep the loop running
            if lines_in_response >= 2:
                # get the second line and break it at a blanks
                line = status[1]
                line = line.split()

                if not (line[2] == "DONE" or line[2] == "EXIT"):
                    flag = flag +1 
                
        
        # check if flag is 0 to exit
        # loop is broken only if all the jobs return DONE or EXIT 
        # TO DO! check other statuses in bjobs that should break the loop
        if flag == 0:
            print("Jobs completed")
            break
        else:
            print("Waiting for jobs to complete ...")
            time.sleep(20)
            
    return 0


#-----------------------------------------------------------------------------
# Function to extract a series of digits from a string 
#(works if only one integer is present in the string)

def SearchForDigitsInString(String):
    index_list = []
    del index_list[:]
    
    for i, x in enumerate(String):
        if type(x) is str:
            if x.isdigit() == True:
                index_list.append(i)
        if type(x) is int:
            index_list.append(i)
        
    start = index_list[0]
    end = index_list[-1] + 1
    number = String[start:end]
    return  number    
    
#----------------------------------------------------------------------------- 
# Function that moves all output and log files into an "output" folder
 
def MoveOutputs(inputs):
    # inputs are always in the form punch/name.in
    # remove "punch/" from the beginning and ".in" form the end
    # match all files containing job's "name" to output folder
    
    # Create an output folder if it doesn't exist yet
    output = "output/"
    if not os.path.exists(os.path.dirname(output)):
        try:
            os.makedirs(os.path.dirname(output))
        except OSError:
                raise
                
    # Loop over all input files from the list
    for input_file in inputs:
        # extract lemma
        # remove first 6 characters and last 3
        lemma = input_file
        lemma = lemma[6:-3]
        # list all files with that lemma in a directory
        files = glob.glob('*%s*' %lemma)
        
        # loop over all files to move
        for x in files:
            destination = output+x            
            os.rename(x,destination)
    
      
    return 0

# Function to run  D-in depletion
def Run_Din(bank,percent_in, window, inputpath):

    punch_files = list ()
    punch_files.append(Din_depletion_punch(bank,percent_in,window,inputpath))
    D_in_output = punch_files[-1].split("/")[-1].split(".")[0]

    Runner(punch_files)    
    
    D_in_output = glob.glob('output/*%s*out' %D_in_output)

    return D_in_output