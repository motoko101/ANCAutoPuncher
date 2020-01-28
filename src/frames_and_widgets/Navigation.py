import tkinter as tk

class Navigation(tk.Frame):
        def __init__(self,parent,controller, *args, **kwargs):
            tk.Frame.__init__(self,parent,*args,**kwargs)
            self.parent = parent
            self.grandpa = parent.grandpa

            self.grid_columnconfigure(0, weight = 1)
            self.label = tk.Label(self,text="Navigation:",bg="white")
            
            self.punch = tk.Button(self, text="Punch file", command = lambda: controller.show_page("PunchPage"))
            self.run   = tk.Button(self, text="Run jobs", command = lambda: controller.show_page("RunPage"))
            self.postp = tk.Button(self, text="Process", command = lambda: controller.show_page("ProcessPage"))
            
            self.label.grid(row=0,sticky="we",padx=(5,5))
            self.punch.grid(row=1,sticky="we",padx=(5,5))
            self.run.grid(row=2,sticky="we",padx=(5,5))
            self.postp.grid(row=3,sticky="we",padx=(5,5))
