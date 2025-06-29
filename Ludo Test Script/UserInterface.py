import customtkinter 
import subprocess
import os

customtkinter.set_appearance_mode("light")  # Modes: "system" (default), "light", "dark"
customtkinter.set_default_color_theme("green")  # Themes: "blue" (default), "green", "dark-blue"

root = customtkinter.CTk()
root.geometry("400x300")
root.title("MJW Clock Control")

def run_clock():
    """Run the main clock9.py script"""
    try:
        script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Functioning scripts", "clock9.py")
        python_exe = "C:/Users/lbitt/AppData/Local/Microsoft/WindowsApps/python3.11.exe"
        print(f"Running clock script: {script_path}")
        subprocess.Popen([python_exe, script_path])
        print("Clock script started successfully")
    except Exception as e:
        print(f"Error running clock script: {e}")

def skip_hour():
    """Run the skiphour.py script"""
    try:
        script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Functioning scripts", "skiphour.py")
        python_exe = "C:/Users/lbitt/AppData/Local/Microsoft/WindowsApps/python3.11.exe"
        print(f"Running skip hour script: {script_path}")
        subprocess.run([python_exe, script_path])
        print("Skip hour completed")
    except Exception as e:
        print(f"Error running skip hour script: {e}")

def skip_minute():
    """Run the skipmin.py script"""
    try:
        script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Functioning scripts", "skipmin.py")
        python_exe = "C:/Users/lbitt/AppData/Local/Microsoft/WindowsApps/python3.11.exe"
        print(f"Running skip minute script: {script_path}")
        subprocess.run([python_exe, script_path])
        print("Skip minute completed")
    except Exception as e:
        print(f"Error running skip minute script: {e}")


frame = customtkinter.CTkFrame(master=root)
frame.pack(pady=20, padx=20, fill="both", expand=True)

# Title label
title_label = customtkinter.CTkLabel(master=frame, text="MJW Clock Control Panel", font=("Arial", 20, "bold"))
title_label.pack(pady=20, padx=10)

# Main clock control button
run_clock_button = customtkinter.CTkButton(
    master=frame, 
    text="🕐 Run Clock", 
    command=run_clock,
    width=200,
    height=50,
    font=("Arial", 16)
)
run_clock_button.pack(pady=15, padx=10)

# Skip hour button
skip_hour_button = customtkinter.CTkButton(
    master=frame, 
    text="⏩ Skip 1 Hour", 
    command=skip_hour,
    width=200,
    height=40,
    font=("Arial", 14)
)
skip_hour_button.pack(pady=10, padx=10)

# Skip minute button
skip_minute_button = customtkinter.CTkButton(
    master=frame, 
    text="⏭️ Skip 1 Minute", 
    command=skip_minute,
    width=200,
    height=40,
    font=("Arial", 14)
)
skip_minute_button.pack(pady=10, padx=10)

# Status label
status_label = customtkinter.CTkLabel(master=frame, text="Ready to control clock", font=("Arial", 12))
status_label.pack(pady=20, padx=10)

# Start the GUI event loop
root.mainloop()

