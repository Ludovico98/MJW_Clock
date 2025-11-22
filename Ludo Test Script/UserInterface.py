import customtkinter
import os
import subprocess
import sys
import threading

customtkinter.set_appearance_mode("light")  # Modes: "system" (default), "light", "dark"
customtkinter.set_default_color_theme("green")  # Themes: "blue" (default), "green", "dark-blue"

PYTHON_EXE = "python3"
FUNCTIONING_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Functioning scripts")
SCRIPT_DIR = os.path.dirname(__file__)

status_label = None
hour_entry = None
minute_entry = None

root = customtkinter.CTk()
root.geometry("420x420")
root.title("MJW Clock Control")


def update_status(message):
    print(message)
    if status_label is not None:
        status_label.configure(text=message)


def run_script_async(command, start_message, success_message):
    update_status(start_message)

    def worker():
        try:
            result = subprocess.run(command, capture_output=True, text=True)
            if result.stdout:
                print(result.stdout.strip())
            if result.stderr:
                print(result.stderr.strip(), file=sys.stderr)
            if result.returncode == 0:
                root.after(0, lambda: update_status(success_message))
            else:
                error_text = result.stderr.strip() or f"Command failed with code {result.returncode}"
                root.after(0, lambda: update_status(error_text))
        except Exception as exc:  # noqa: BLE001 - surface subprocess issues
            root.after(0, lambda: update_status(f"Error: {exc}"))

    threading.Thread(target=worker, daemon=True).start()


def run_clock():
    """Run the main clock9.py script"""
    try:
        script_path = os.path.join(FUNCTIONING_DIR, "clock9.py")
        print(f"Running clock script: {script_path}")
        process = subprocess.Popen([PYTHON_EXE, script_path])
        update_status(f"Clock started (PID {process.pid})")
    except Exception as exc:
        update_status(f"Error running clock script: {exc}")


def skip_hour():
    """Run the skiphour.py script"""
    script_path = os.path.join(FUNCTIONING_DIR, "skiphour.py")
    run_script_async([PYTHON_EXE, script_path], "Skipping hour...", "Skip hour completed")


def set_hour_from_input():
    if hour_entry is None or minute_entry is None:
        update_status("Hour controls not initialised")
        return

    hour_text = hour_entry.get().strip()
    minute_text = minute_entry.get().strip()

    if not hour_text:
        update_status("Enter an hour between 0 and 23.")
        return

    try:
        hour_value = int(hour_text)
    except ValueError:
        update_status("Hour must be a number between 0 and 23.")
        return

    if minute_text:
        try:
            minute_value = int(minute_text)
        except ValueError:
            update_status("Minute must be a number between 0 and 59.")
            return
    else:
        minute_value = 0

    if not 0 <= hour_value <= 23:
        update_status("Hour must be between 0 and 23.")
        return
    if not 0 <= minute_value <= 59:
        update_status("Minute must be between 0 and 59.")
        return

    display_hour = hour_value % 12 or 12
    script_path = os.path.join(SCRIPT_DIR, "sethour.py")
    command = [PYTHON_EXE, script_path, str(hour_value), "--minute", str(minute_value)]

    start_message = f"Setting hour hand to {display_hour:02d}:{minute_value:02d}..."
    success_message = f"Hour hand set to {display_hour:02d}:{minute_value:02d}"
    run_script_async(command, start_message, success_message)


def set_minute_from_input():
    if minute_entry is None:
        update_status("Minute controls not initialised")
        return

    minute_text = minute_entry.get().strip()
    if not minute_text:
        update_status("Enter a minute between 0 and 59.")
        return

    try:
        minute_value = int(minute_text)
    except ValueError:
        update_status("Minute must be a number between 0 and 59.")
        return

    if not 0 <= minute_value <= 59:
        update_status("Minute must be between 0 and 59.")
        return

    script_path = os.path.join(SCRIPT_DIR, "setmin.py")
    command = [PYTHON_EXE, script_path, str(minute_value)]

    start_message = f"Setting minute hand to {minute_value:02d}..."
    success_message = f"Minute hand set to {minute_value:02d}"
    run_script_async(command, start_message, success_message)


frame = customtkinter.CTkFrame(master=root)
frame.pack(pady=20, padx=20, fill="both", expand=True)

# Title label
title_label = customtkinter.CTkLabel(master=frame, text="MJW Clock Control Panel", font=("Arial", 20, "bold"))
title_label.pack(pady=20, padx=10)

inputs_frame = customtkinter.CTkFrame(master=frame)
inputs_frame.pack(pady=10, padx=10, fill="x")
inputs_frame.grid_columnconfigure((0, 1), weight=1)

hour_label = customtkinter.CTkLabel(master=inputs_frame, text="Hour (0-23)")
hour_label.grid(row=0, column=0, padx=5, pady=(10, 0), sticky="w")

minute_label = customtkinter.CTkLabel(master=inputs_frame, text="Minute (0-59)")
minute_label.grid(row=0, column=1, padx=5, pady=(10, 0), sticky="w")

hour_entry = customtkinter.CTkEntry(master=inputs_frame, placeholder_text="e.g. 10")
hour_entry.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

minute_entry = customtkinter.CTkEntry(master=inputs_frame, placeholder_text="e.g. 30")
minute_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

set_hour_button = customtkinter.CTkButton(
    master=inputs_frame,
    text="Set Hour",
    command=set_hour_from_input,
    height=36
)
set_hour_button.grid(row=2, column=0, padx=5, pady=(5, 10), sticky="ew")

set_minute_button = customtkinter.CTkButton(
    master=inputs_frame,
    text="Set Minute",
    command=set_minute_from_input,
    height=36
)
set_minute_button.grid(row=2, column=1, padx=5, pady=(5, 10), sticky="ew")

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

# Status label
status_label = customtkinter.CTkLabel(master=frame, text="Ready to control clock", font=("Arial", 12))
status_label.pack(pady=20, padx=10)

# Start the GUI event loop
root.mainloop()

