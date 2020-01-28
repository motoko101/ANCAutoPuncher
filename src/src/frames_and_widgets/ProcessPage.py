import tkinter as tk

class ProcessPage(tk.Frame):
        def __init__(self,parent, *args, **kwargs):
            tk.Frame.__init__(self,parent,*args,**kwargs)
            self.parent = parent
            self.grandpa = parent.grandpa