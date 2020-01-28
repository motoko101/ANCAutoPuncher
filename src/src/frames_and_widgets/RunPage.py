import tkinter  as tk
try:
    from tkinter import messagebox
except:
    import tkMessageBox as messagebox

import subprocess
import glob
from PIL        import ImageTk, Image
from os         import remove, chdir, getcwd, path, mkdir
from anc_out    import ReadEditSingle

class RunPage(tk.Frame):
        def __init__(self,parent, *args, **kwargs):
            tk.Frame.__init__(self,parent,*args,**kwargs)
            self.parent = parent
            self.grandpa = parent.grandpa
            #
            self._width = parent.w/8*2.75
            self._height = (parent.h/4*3)/4*3
            #
            #
            #  TO DO: FIGURE OUT HOW TO MAKE A SCROLLABLE CANVAS WITH FRAME AND BOUNDARIES
            # Canvas will hold a scrollbar and a frame
            #self.canvas = tk.Canvas(self).grid(row=0,column=0)
            self.grid_columnconfigure(0,weight =1)
            self.grid_rowconfigure(0, weight = 1)

            self.canvas = tk.Canvas(self,width=self._width, height=self._height)
            self.canvas.grid(row=0,column=0, sticky="nwes")

            self.yscrollbar = tk.Scrollbar(self,orient=tk.VERTICAL)
            self.yscrollbar.grid(row=0,column=1,sticky="ns")

            self.canvas.configure(yscrollcommand=self.yscrollbar.set)
            self.canvas.grandpa = self.grandpa
            self.yscrollbar.config(command=self.canvas.yview)

            self.__init__build_rows_with_inputs()

            self.canvas.bind('<Configure>', self._on_canvas_configure)
            self.canvas.bind("<<UpdateFrame>>",self.on_show_frame)
            #
            self.bind("<<ShowFrame>>",self.on_show_frame)
            #
            #
        def __init__build_rows_with_inputs(self):
            self.innerframe = InnerFrame(self.canvas)
            self.innerframe.grid()
            self.canvas.create_window(0,0,window=self.innerframe,anchor="nw")

        def update_rows_with_inputs(self):
            self.innerframe.destroy()
            self.__init__build_rows_with_inputs()

        def on_show_frame(self,event):
            self.update_rows_with_inputs()

        def width(self):
            return self.canvas.winfo_width()

        @property
        def width(self):
            return self.canvas.winfo_width()

        @width.setter
        def width(self, width):
            self.canvas.configure(width= width)

        @property
        def height(self):
            return self.canvas.winfo_height()
        
        @height.setter
        def height(self, height):
                self.canvas.configure(height = height)
        
        def set_size(self, width, height):
            self.canvas.configure(width=width, height = height)

        def _on_canvas_configure(self, event):
            width = max(self.innerframe.winfo_reqwidth(), event.width)
            height = max(self.innerframe.winfo_reqheight(), event.height)

            self.canvas.configure(scrollregion="0 0 %s %s" % (width, height))
            self.canvas.itemconfigure("inner_frame", width=width, height=height)  

class InnerFrame(tk.Frame):
        def __init__(self,parent,*args,**kwargs):
            tk.Frame.__init__(self,parent)  
            self.__init__build_rows_with_inputs()
            self.parent = parent
            self.grandpa = self.parent.grandpa
            self.bind("<<DelButtonPress>>",self.send_signal_to_canvas)
            # This somehow gets called twice when the program is run. Probably becasue of being initiated and then reconstructed when the page is raised.
        def send_signal_to_canvas(self,event):
            self.parent.event_generate("<<UpdateFrame>>")

        def __init__build_rows_with_inputs(self):
            # Collect punch files names
            self.punched_files = glob.glob('punch/*in')

            # Collect output file names information and job status (if they exist)
            self.output_files = {}
            self.output_files_text = {}
            self.job_status = {}

            for punch_f in self.punched_files:
                name = punch_f.split('/')[-1]
                job_name = name.split('.')[0]  
                #print(print(path.join('output/',job_name,'_*.out'))
                globbed_files =  glob.glob(path.join('output',job_name+'_*.out'))
                if len(globbed_files) > 1:
                    text = "Multpile output files."
                elif len(globbed_files) == 0:
                    text = "No output file."
                else: 
                    text = globbed_files[0].split('/')[-1]
                self.output_files[punch_f] = globbed_files
                self.output_files_text[punch_f] = text

            # Collect running job statuses
            sub = subprocess.Popen('qstat', shell=True, stdout=subprocess.PIPE, universal_newlines = True, stderr=subprocess.STDOUT)
            # In Python 3 Popen will return bytes because of \n. Use universal_newlines to get rid of \n and for popen to return string
            
            for line in sub.stdout.readlines():
                # Get name of the job and the status
                if len(line) > 0:
                    line = line.split()
                    if len(line) == 6:
                        name = 'punch/'+line[-5]+'.in'
                        status = line[-2]
                        self.job_status[name] = status


            self.row = {}
            self.run_buttons = {}
            self.del_inp_buttons = {}
            self.output_label = {}
            self.output_delete_buttons = {}
            self.job_status_label = {}
            self.lookup_button = {}

            # First row of the inner frame with descriptions
            self.first_row = tk.Label(self,text = "Input file name:").grid(row=0,sticky="W",columnspan = 3)
            self.first_row = tk.Label(self,text = "Job Status:").grid(row=0,column = 6, sticky="W")
            self.first_row = tk.Label(self,text = "Output file:").grid(row=0,column =7,sticky="W", columnspan =3)

            for idx, pfile in enumerate(self.punched_files):
                #print(pfile)
                self.grid_rowconfigure(idx+1, minsize = 25)
                pfile_text = pfile.split('/')[-1]
                self.row[idx] = tk.Label(self, text=pfile_text).grid(row = idx+1,column = 0,sticky="W", columnspan = 3)
                self.del_inp_buttons[idx] = DelButton(self,pfile).grid(row = idx+1,column = 3)
                self.lookup_button[idx] = LookUpButton(self,pfile).grid(row = idx+1,column = 4)
                self.run_buttons[idx] = RunButton(self,pfile).grid(row = idx+1,column = 5)
                
                # Status of the job. Add some additional conditions. E.g. if not in Queue but file exist etc.
                status_text, bg_color = self.define_job_status(pfile)
                
                self.job_status_label[idx] = tk.Label(self, text=status_text,fg=bg_color).grid(row = idx+1,column = 6,sticky="W",padx=1)

                self.output_label[idx]  = tk.Label(self,text=self.output_files_text[pfile]).grid(row=idx+1,column=7,sticky = "NSWE")
                self.output_delete_buttons[idx] = DelButton(self,self.output_files[pfile]).grid(row = idx+1,column = 8)
                self.lookup_button[idx] = LookUpButton(self,self.output_files[pfile]).grid(row = idx+1,column = 9)

        def define_job_status(self,pfile):
                if pfile in self.job_status:
                    #print("job in qstat")
                    status = self.job_status[pfile]
                    if status == "Q":
                        return "In queue", 'SkyBlue3'
                    elif status == "R":
                        return "Running", 'SkyBlue1'
                    elif status == "C":
                        # Check for output file. Assume the latest as the correct one
                        if self.output_files[pfile]:
                            out_f = self.output_files[pfile][-1]
                            # Check if the job has errors
                            edit = 'SE-Error'
                            try:
                                SE_Error = ReadEditSingle(out_f, edit)
                            except:
                                SE_Error = ""
                        
                            if len(SE_Error) > 0:
                                return "Error when running.", 'red2'
                            # Check if the job has SE-General (means it completed)
                            edit = 'SE-General'
                            try:
                                SE_General = ReadEditSingle(out_f, edit)
                            except:
                                SE_General = ""
                        
                            if len(SE_General) > 0:
                                return "Completed.", 'green2'
                else:
                    # Check for output file. Assume the latest as the correct one
                    #print("job not in qstat")
                    if self.output_files[pfile]:
                        out_f = self.output_files[pfile][-1]
                        # Check if the job has errors
                        edit = 'SE-Error'
                        try:
                            SE_Error = ReadEditSingle(out_f, edit)
                        except:
                            SE_Error = ""
                        
                        if len(SE_Error) > 0:
                            return "Error when running.", 'red2'
                        # Check if the job has SE-General (means it completed)
                        edit = 'SE-General'
                        try:
                            SE_General = ReadEditSingle(out_f, edit)
                        except:
                            SE_General = ""
                        
                        if len(SE_General) > 0:
                            return "Completed.", 'green2'
                    else:
                        return "Job not in MOAB.",'grey1'

class RunButton(tk.Button):
        def __init__(self,parent,inputfile,*args,**kwargs):
            
            image = Image.open("assets/run_button.png")

            # Adjust the image size
            hsize = 25
            basewidth = int(52/42*25)
            image = image.resize((basewidth,hsize), Image.ANTIALIAS)

            logo = ImageTk.PhotoImage(image)
            
            tk.Button.__init__(self,parent,text = "Run",image = logo,compound = tk.LEFT,pady=0,command = lambda: self.run_job(parent,inputfile))
            # Save the reference to image. Python garbage cleaner may blank it out.
            self.image = logo

        def run_job(self,parent,inputfile):

            name = inputfile.split('/')[-1]
            job_name = name.split('.')[0]
            #construct the bsub command
            #sub = "bsub -J "+name+" run_anc -ver "+anc_ver+" -i "+name
            sub = "bsub -J "+job_name+" run_anc -i ../"+inputfile # run with defualt ANC9 version
            #print(sub)
            # Change the working directory to /output and submit the job
            if path.exists('output'):
                pass
            else:
                mkdir('output/')
            
            chdir('output')

            sub = subprocess.Popen(sub, shell=True, stdout=subprocess.PIPE, universal_newlines = True, stderr=subprocess.STDOUT)
            # In Python 3 Popen will return bytes because of \n. Use universal_newlines to get rid of \n and for popen to return string
            sub = sub.stdout.readline().strip()
            #print("sub"+sub)
            chdir('../')

            text = str(("Submitted job: %s with jobID number: %s" %(inputfile,sub)))
            parent.grandpa.msgb.insert_text("\n")
            parent.grandpa.msgb.insert_text(text)

class DelButton(tk.Button):
        def __init__(self,parent,inputfile,*args,**kwargs):
            image = Image.open("assets/del_button.png")
            self.parent = parent
            self.inputfile = inputfile
            # Adjust the image size
            hsize = 25
            basewidth = 25
            image = image.resize((basewidth,hsize), Image.ANTIALIAS)

            logo = ImageTk.PhotoImage(image)
            
            tk.Button.__init__(self,parent,image = logo,command = lambda: self.delete_file(parent))
            # Save the reference to image. Python garbage cleaner may blank it out.
            self.image = logo
        
        def delete_file(self,parent):
            if (type(self.inputfile) == list):
                for inp_file in self.inputfile:                    
                    decision = messagebox.askquestion("DELETE FILE","Are you sure you want to delete this file?",icon='warning')
                    if decision == 'yes':
                        text = str(("Deleted file: %s" %(inp_file)))
                        self.parent.grandpa.msgb.insert_text("\n")
                        self.parent.grandpa.msgb.insert_text(text)
                        remove(inp_file)
                        remove(inp_file.split('.')[0]+'.log')
                    else:
                        pass
            else:
                decision = messagebox.askquestion("DELETE FILE","Are you sure you want to delete this file?",icon='warning')
                if decision == 'yes':
                    text = str(("Deleted file: %s" %(self.inputfile)))
                    self.parent.grandpa.msgb.insert_text("\n")
                    self.parent.grandpa.msgb.insert_text(text)
                    remove(self.inputfile)
                else:
                    pass

            parent.event_generate("<<DelButtonPress>>")

class LookUpButton(tk.Button):
        def __init__(self,parent,inputfile,*args,**kwargs):
            image = Image.open("assets/read_button.png")
            self.parent = parent
            self.inputfile = inputfile
            # Adjust the image size
            hsize = 25
            basewidth = 25
            image = image.resize((basewidth,hsize), Image.ANTIALIAS)

            logo = ImageTk.PhotoImage(image)
            
            tk.Button.__init__(self,parent,image = logo,command = lambda: self.lookup_file(parent))
            # Save the reference to image. Python garbage cleaner may blank it out.
            self.image = logo
        
        def lookup_file(self,parent):
            if (type(self.inputfile) == list):
                for inp_file in self.inputfile:
                    text = str(("Showing file: %s" %(inp_file)))
                    self.parent.grandpa.msgb.insert_text("\n")
                    self.parent.grandpa.msgb.insert_text(text)
                    sub = subprocess.Popen('nedit '+inp_file, shell=True, stdout=subprocess.PIPE, universal_newlines = True, stderr=subprocess.STDOUT)
            elif len(self.inputfile) == 0:
                pass
            else:
                text = str(("Showing file: %s" %(self.inputfile)))
                self.parent.grandpa.msgb.insert_text("\n")
                self.parent.grandpa.msgb.insert_text(text)
                sub = subprocess.Popen('nedit '+self.inputfile, shell=True, stdout=subprocess.PIPE, universal_newlines = True, stderr=subprocess.STDOUT)
