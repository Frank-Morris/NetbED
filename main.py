import tkinter as tk
from tkinter import messagebox, Toplevel, scrolledtext, simpledialog
import subprocess
import threading

class NetbedLab:
    def __init__(self, window):
        self.window = window
        self.window.title("NetbED - Automated Lab Provisioner")
        # Expanded window to fit the console
        self.window.geometry("800x450") 

        # Modular Node Configuration
        self.nodes = {
            "pfsense": tk.BooleanVar(value=True),
            "attacker": tk.BooleanVar(value=False),
            "web-server": tk.BooleanVar(value=False),
            "domain-controller": tk.BooleanVar(value=False),
            "client": tk.BooleanVar(value=False)
        }

        # GUI Layout
        # Title
        self.title_label = tk.Label(window, text="NetbED Control Panel", font=("Arial", 16, "bold"))
        self.title_label.grid(row=0, column=0, columnspan=2, pady=10)

        # Left Frame: Controls
        self.control_frame = tk.Frame(window)
        self.control_frame.grid(row=1, column=0, padx=20, sticky="n")

        self.config_btn = tk.Button(self.control_frame, text="Configure Nodes", width=20, bg="blue", fg="white", command=self.open_config)
        self.config_btn.pack(pady=5)

        self.start_btn = tk.Button(self.control_frame, text="Start Lab", width=20, bg="green", fg="white", command=self.start_lab)
        self.start_btn.pack(pady=10)

        self.suspend_btn = tk.Button(self.control_frame, text="Suspend Lab", width=20, fg="red", command=self.suspend_lab)
        self.suspend_btn.pack(pady=10)

        self.resume_btn = tk.Button(self.control_frame, text="Resume Lab", width=20, fg="green", command=self.resume_lab)
        self.resume_btn.pack(pady=10)

        self.destroy_btn = tk.Button(self.control_frame, text="Delete Lab", width=20, bg="red", fg="white", command=self.delete_lab)
        self.destroy_btn.pack(pady=10)

        # Snapshot Section
        tk.Label(self.control_frame, text="--- Snapshots ---").pack(pady=(10, 0))
        
        tk.Label(self.control_frame, text="Snapshot lists").pack(pady=(5,0))
        self.snap_list = tk.Listbox(self.control_frame, height=5)
        self.snap_list.pack(pady=5)

        tk.Button(self.control_frame, text="Create Snapshot", command=self.snap_save).pack(pady=2)
        tk.Button(self.control_frame, text="Restore Snapshot", command=self.snap_load).pack(pady=2)


        # Right Frame: Log Console
        self.console_frame = tk.Frame(window)
        self.console_frame.grid(row=1, column=1, padx=10, sticky="nsew")
        
        tk.Label(self.console_frame, text="Live Execution Logs:", font=("Arial", 10, "bold")).pack(anchor="w")
        
        # ScrolledText acts as our terminal window
        self.console = scrolledtext.ScrolledText(self.console_frame, width=70, height=20, bg="black", fg="white", font=("Consolas", 9))
        self.console.pack()
        self.log_to_console("System Initialized. Ready for deployment.\n")

    # Modular Logic
    def open_config(self):
        # Opens a pop-up to select specific nodes. 
        config_win = Toplevel(self.window)
        config_win.title("Node Selection")
        config_win.geometry("250x250")

        tk.Label(config_win, text="Select Target Nodes:", font=("Arial", 10, "bold")).pack(pady=10)

    

        for node_name, var in self.nodes.items():
            tk.Checkbutton(config_win, text=node_name.capitalize(), variable=var).pack(anchor="w", padx=30)

        tk.Button(config_win, text="Save & Close", command=config_win.destroy).pack(pady=15)

    def get_selected_nodes(self):
        # Returns a string of selected node names. 
        selected = [name for name, var in self.nodes.items() if var.get()]
        return " ".join(selected)

    #  Console Logging Logic 
    def log_to_console(self, text):
         # Safely inserts text into the console and scrolls to the bottom. 
        self.console.insert(tk.END, text)
        self.console.see(tk.END)

    def run_subprocess(self, command):
        # Executes the CLI command in a separate thread to prevent GUI freezing.
        def execute():
            # Disable the buttons 
            self.window.after(0, self.set_gui_state, tk.DISABLED)
            self.log_to_console(f"\n>> EXECUTING: {command}\n")
            # Starts the background process and pipes the output
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            
            # Reads the output line by line as it generates
            for line in process.stdout:
                self.window.after(0, self.log_to_console, line)
            
            process.wait()
            self.window.after(0, self.log_to_console, f">> COMMAND FINISHED with exit code {process.returncode}\n")
            # Re-enable the buttons 
            self.window.after(0, self.set_gui_state, tk.NORMAL)

        # Start the thread
        threading.Thread(target=execute, daemon=True).start()

    # Button Commands 
    def start_lab(self):
        selected = self.get_selected_nodes()
        if not selected:
            messagebox.showwarning("Error", "No nodes selected! Check 'Configure Nodes'.")
            return
        
        command = f"vagrant up {selected}"
        self.run_subprocess(command)

    def suspend_lab(self):
        selected = self.get_selected_nodes()
        command = f"vagrant suspend {selected}"
        self.run_subprocess(command)

    def resume_lab(self):
        selected = self.get_selected_nodes()
        command = f"vagrant resume {selected } --no-provision"
        self.run_subprocess(command)

    def delete_lab(self):
        if messagebox.askyesno("Warning", "Are you sure you want to delete the selected virtual machines?"):
            selected = self.get_selected_nodes()
            command = f"vagrant destroy -f {selected}"
            self.run_subprocess(command)

    def set_gui_state(self, state):
        # Dynamically enables or disables the controls to prevent concurrent Vagrant locks.
        self.start_btn.config(state=state)
        self.suspend_btn.config(state=state)
        self.resume_btn.config(state=state)
        self.destroy_btn.config(state=state)
        self.config_btn.config(state=state)

    def snap_save(self):
        # System prompts user for a name and adds to list
        name = simpledialog.askstring("Snapshot", "Enter snapshot name:")
        selected = self.get_selected_nodes()
        if name and selected:
            self.snap_list.insert(tk.END, name)
            self.run_subprocess(f'vagrant snapshot save {selected} "{name}"')
        else:
            self.snap_list.insert(tk.END, name)
            self.run_subprocess(f'vagrant snapshot save "{name}"')

    def snap_load(self):
        #Get the name from the list
        name = self.snap_list.get(tk.ACTIVE)
        selected = self.get_selected_nodes()
        
        if name:
            # restores the whole environment back to that state.
            self.run_subprocess(f'vagrant snapshot restore {selected} "{name}" --no-start')






if __name__ == "__main__":
    root = tk.Tk()
    app = NetbedLab(root)
    root.mainloop()