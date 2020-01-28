import sys
sys.path.append('src/frames_and_widgets')
sys.path.append('src/helper_functions')
sys.path.append('src/data')
sys.path.append('src/punch_templates')

from MainApplication import *

def main():
    root = tk.Tk()
    app = MainApplication(root)
    root.mainloop()

if __name__ == "__main__":
    main()