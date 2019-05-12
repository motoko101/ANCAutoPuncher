import sys
sys.path.append("/users/luszczkk/tools/py_modules")
sys.path.append("/users/luszczkk/tools/py_modules/AAP")
sys.path.append("/home/luszczkk/tools/py_modules")
sys.path.append("/home/luszczkk/tools/py_modules/AAP")

from frames_and_widgets import *
from data_management import *

class DataStorage():
    def __init__(self,parent):
        self.parent = parent

def main():
    root = tk.Tk()
    app = MainApplication(root)
    root.mainloop()

if __name__ == "__main__":
    main()
