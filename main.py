import tkinter as tk
from tkinter import messagebox
import os
import webbrowser

# The NetbedLab class handles the window and the logic for the buttons
class NetbedLab:
    def __init__(self, window):
        # Setup the main window properties
        self.window = window
        self.window.title("NetbED")
        self.window.geometry("400x300")

        # 1. Creates the header
        self.title_label = tk.Label(window, text="NetbED Lab Deployer", font=("Arial", 14, "bold"))
        self.title_label.pack(pady=20)

        #Define a callback function
        def github_link():
            webbrowser.open_new_tab()

        # 2. Creates the start button which will run the command "Vagrant Up"
        self.start_btn = tk.Button(window, text="Start Lab", width=20, bg="green", fg="white", command=self.start_lab)
        self.start_btn.pack(pady=10)

        # 3. Creates the stop button which will run the command "Vagrant Halt"
        self.stop_btn = tk.Button(window, text="Stop Lab", width=20, command=self.stop_lab)
        self.stop_btn.pack(pady=10)

        # 4. Creates the delete button which will run "Vagrant destroy -f"
        self.destroy_btn = tk.Button(window, text="Delete Lab", width=20, bg="red", fg="white", command=self.delete_lab)
        self.destroy_btn.pack(pady=10)

    # Function to start the lab
    def start_lab(self):
        # os.system sends the command to the terminal as if you typed it in CLI
        os.system("vagrant up")
        messagebox.showinfo("Status", "Command 'vagrant up' has been sent.")

    # Function to stop the lab
    def stop_lab(self):
        os.system("vagrant halt")
        messagebox.showinfo("Status", "Command 'vagrant halt' has been sent.")

    # Function to delete the lab
    def delete_lab(self):
        # Message box pop up with Yes/No for user.
        if messagebox.askyesno("Warning", "Are you sure you want to delete all virtual machines?"):
            os.system("vagrant destroy -f")
            messagebox.showwarning("Status", "Lab has been destroyed.")
            
 
   


if __name__ == "__main__":
    root = tk.Tk()
    app = NetbedLab(root)
    root.mainloop()