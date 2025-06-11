# main.py

import tkinter as tk
from gui.dashboard import ResourceMonitorApp

if __name__ == "__main__":
    root = tk.Tk()
    app = ResourceMonitorApp(root)
    root.geometry("700x400")
    root.mainloop()
