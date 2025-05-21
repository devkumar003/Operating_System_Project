import psutil
import tkinter as tk
from tkinter import ttk

def get_processes_info():
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent', 'io_counters']):
        try:
            io_counters = proc.info['io_counters']
            read_write = (io_counters.read_bytes + io_counters.write_bytes) if io_counters else 0

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
        tag = ''
        if proc['bound'] == 'CPU-bound':
            tag = 'cpu'
        elif proc['bound'] == 'I/O-bound':
            tag = 'io'
        elif proc['bound'] == 'Balanced':
            tag = 'balanced'

        tree.insert('', 'end', values=(
            proc['pid'],
            proc['name'],
            proc['user'],
            proc['type'],
            f"{proc['cpu']}%",
            f"{proc['memory']:.2f}%",
            f"{proc['io'] / 1024:.0f} KB",
            proc['bound']
        ), tags=(tag,))

# GUI setup
root = tk.Tk()
root.title("Process Manager")
root.geometry("900x500")
root.configure(bg="#2e2e2e")

style = ttk.Style()
style.theme_use("clam")

# Treeview styling
style.configure("Treeview",
                background="#1e1e1e",
                foreground="white",
                fieldbackground="#1e1e1e",
                rowheight=25,
                font=('Segoe UI', 10))
style.configure("Treeview.Heading",
                font=('Segoe UI', 10, 'bold'),
                background="#333333",
                foreground="white")

style.map("Treeview", background=[('selected', '#6666ff')])

columns = ("PID", "Name", "User", "Type", "CPU %", "Memory %", "I/O", "Bound Type")
tree = ttk.Treeview(root, columns=columns, show='headings')

# Add tag styles
tree.tag_configure('cpu', background='#ff6666')
tree.tag_configure('io', background="#b300ff")
tree.tag_configure('balanced', background="#000000")

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=110, anchor='center')

tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Refresh Button
refresh_btn = tk.Button(root,
                        text="Refresh",
                        command=refresh_data,
                        bg="#444",
                        fg="white",
                        font=('Segoe UI', 10),
                        relief='flat',
                        padx=10, pady=5)
refresh_btn.pack(pady=5)

# Initial load
refresh_data()
root.mainloop()
