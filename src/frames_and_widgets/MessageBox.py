import tkinter as tk
from tkinter.scrolledtext import ScrolledText

class MessageBox(tk.Frame):
    """
    Box for displaying messages.
    """
    def __init__(self,parent, *args, **kwargs):
            tk.Frame.__init__(self,parent,*args,**kwargs)
            self.parent = parent
            self.grandpa = parent.grandpa
            # there is something wrong with that height
            
            self.tbox = ScrolledText(self,width=int(parent.w),height=int(parent.h/4) )
            
            #When using grid, any extra space in the parent is allocated proportionate to the "weight" of a row and/or a column 
            #(ie: a column with a weight of 2 gets twice as much of the space as one with a weight of 1). By default, rows and columns have a weight of 0 (zero),
            #meaning no extra space is given to them.
            #
            #You need to give the column that the widget is in a non-zero weight, 
            # so that any extra space when the window grows is allocated to that column
            #
            # You'll also need to specify a weight for the row, and a sticky value of N+S+E+W if you want it to grow in all directions
            self.grid_rowconfigure(0, weight = 1)
            self.grid_columnconfigure(0, weight = 1)
            self.tbox.grid(row = 0)
    
    def insert_text(self,text):
        self.tbox.insert(tk.END,text)
        self.tbox.see(tk.END)

    def clear(self):
        self.tbox.delete(1.0,tk.END) 
