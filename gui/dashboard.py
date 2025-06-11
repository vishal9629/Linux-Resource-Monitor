# gui/dashboard.py

import tkinter as tk
from tkinter import ttk, messagebox
from monitor.process_monitor import get_process_list
from monitor.process_actions import kill_process, renice_process, suspend_process
import matplotlib.pyplot as pyplot
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class ResourceMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Linux Resource Monitor")

        self.tree = ttk.Treeview(root, columns=("PID", "Name", "CPU", "Memory", "Suggestion"), show='headings')
        for col in ("PID", "Name", "CPU", "Memory", "Suggestion"):
            self.tree.heading(col, text=col)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Buttons
        button_frame = tk.Frame(root)
        button_frame.pack(pady=5)

        tk.Button(button_frame, text="Refresh", command=self.refresh_processes).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Kill", command=self.kill_selected_process).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Renice", command=self.renice_selected_process).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Suspend", command=self.suspend_selected_process).pack(side=tk.LEFT, padx=5)

        self.refresh_processes()
        
        # Setup graph
        self.cpu_history = []
        self.mem_history = []
        self.time_history = []

        self.figure, self.ax = plt.subplots(figsize=(6, 2))
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.root)
        self.canvas.get_tk_widget().pack(pady=10)

        self.update_graph()

    def refresh_processes(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        processes = get_process_list()
        for proc in processes:
            suggestion = ""
            if proc["cpu_percent"] > 80:
                suggestion = "High CPU"
            elif proc["memory_percent"] > 70:
                suggestion = "High Memory"
            self.tree.insert("", "end", values=(
                proc["pid"], proc["name"], proc["cpu_percent"], proc["memory_percent"], suggestion
            ))

    def get_selected_pid(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a process first.")
            return None
        pid = self.tree.item(selected[0])["values"][0]
        return pid

    def kill_selected_process(self):
        pid = self.get_selected_pid()
        if pid:
            result = kill_process(pid)
            self._handle_result(result)

    def renice_selected_process(self):
        pid = self.get_selected_pid()
        if pid:
            result = renice_process(pid, nice_value=10)
            self._handle_result(result)

    def suspend_selected_process(self):
        pid = self.get_selected_pid()
        if pid:
            result = suspend_process(pid)
            self._handle_result(result)

    def _handle_result(self, result):
        if result is True:
            messagebox.showinfo("Success", "Action completed successfully.")
            self.refresh_processes()
        else:
            messagebox.showerror("Error", str(result))

    def update_graph(self):
        self.cpu_history.append(psutil.cpu_percent())
        self.mem_history.append(psutil.virtual_memory().percent)
        self.time_history.append(time.strftime('%H:%M:%S'))

        # Keep only last 20 data points
        if len(self.cpu_history) > 20:
            self.cpu_history = self.cpu_history[-20:]
            self.mem_history = self.mem_history[-20:]
            self.time_history = self.time_history[-20:]

        self.ax.clear()
        self.ax.plot(self.time_history, self.cpu_history, label='CPU %', color='blue')
        self.ax.plot(self.time_history, self.mem_history, label='Memory %', color='green')
        self.ax.set_ylim(0, 100)
        self.ax.set_title("System Resource Usage")
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Usage %")
        self.ax.legend(loc='upper left')
        self.ax.grid(True)

        self.canvas.draw()
        self.root.after(3000, self.update_graph)  # update every 3 seconds

