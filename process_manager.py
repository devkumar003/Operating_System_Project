import psutil
import tkinter as tk
from tkinter import ttk

def get_processes_info():
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent', 'io_counters']):
        try:
            io_counters = proc.info['io_counters']
            read_write = (io_counters.read_bytes + io_counters.write_bytes) if io_counters else 0

            # Classify process type
            if proc.info['cpu_percent'] > 10 and read_write < 1_000_000:
                proc_type = 'CPU-bound'
            elif read_write >= 1_000_000:
                proc_type = 'I/O-bound'
            else:
                proc_type = 'Balanced'

            user_type = 'System' if proc.info['username'] in ['SYSTEM', 'root'] else 'User'

            processes.append({
                'pid': proc.info['pid'],
                'name': proc.info['name'],
                'user': proc.info['username'],
                'type': user_type,
                'cpu': proc.info['cpu_percent'],
                'memory': proc.info['memory_percent'],
                'io': read_write,
                'bound': proc_type
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return processes

def refresh_data():
    for row in tree.get_children():
        tree.delete(row)

    for proc in get_processes_info():
        tree.insert('', 'end', values=(
            proc['pid'],
            proc['name'],
            proc['user'],
            proc['type'],
            f"{proc['cpu']}%",
            f"{proc['memory']:.2f}%",
            f"{proc['io'] / 1024:.0f} KB",
            proc['bound']
        ))

# GUI setup
root = tk.Tk()
root.title("Process Manager")

columns = ("PID", "Name", "User", "Type", "CPU %", "Memory %", "I/O", "Bound Type")
tree = ttk.Treeview(root, columns=columns, show='headings')

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=100)

tree.pack(fill=tk.BOTH, expand=True)

refresh_btn = tk.Button(root, text="Refresh", command=refresh_data)
refresh_btn.pack(pady=5)

# Initial load
refresh_data()
root.mainloop()
