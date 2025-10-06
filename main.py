import tkinter as tk #Imports python library for GUIS

#The function to run when the button is clicked.
def deploy_lab():
    print("Button clicked. This will be replaced with the vagrant up command")

window = tk.Tk()
window.title("NetbED Lab Deployer")
window.geometry("400x200")  #Size of the window


#Text labels.
label = tk.Label(window, text="NetbED Lab Deployment Tool")
label.pack(pady=10, padx=10) 

#A button that will run the 'deploy_lab" function when clicked
deploy_button = tk.Button(window, text="Deploy Full lab", command=deploy_lab)
deploy_button.pack(pady=20)

window.mainloop()