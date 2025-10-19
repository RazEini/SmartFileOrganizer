# main.py
import tkinter as tk
from ui import SmartOrganizerApp

def main():
    root = tk.Tk()
    app = SmartOrganizerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
