# MJW Clock Control - Raspberry Pi Desktop Icon Setup

## Quick Setup (Recommended)

Install

Step 1: Install tkinter on Raspberry Pi
```
sudo apt update
sudo apt install python3-tk
```
Step 2: Transfer files and navigate to the project

```
# If files are already on the Pi at /home/pi/MJW_Clock/
cd "/home/pi/MJW_Clock/Ludo Test Script"
```

Step 3: Install CustomTkinter
```
pip3 install customtkinter
```

Step 4: Run the automatic setup script

```
python3 create_shortcut.py
```

Step 5: Test the GUI directly

```
python3 UserInterface.py
```

If you want to manually create the desktop shortcut:
```
# Make launch script executable
chmod +x "/home/pi/MJW_Clock/Ludo Test Script/launch_clock_ui.sh"

# Copy desktop file to desktop
cp "/home/pi/MJW_Clock/Ludo Test Script/MJW_Clock_Control.desktop" ~/Desktop/

# Make desktop entry executable
chmod +x ~/Desktop/MJW_Clock_Control.desktop
```


For GPIO functionality (if your clock uses GPIO pins):

```
sudo apt install python3-rpi.gpio
# or
pip3 install RPi.GPIO
```

The key difference for Raspberry Pi is that `python3-tk` should be available in the repositories, and you'll have GPIO access for the actual clock hardware control.

1. **Transfer files to your Raspberry Pi** in the folder `/home/pi/MJW_Clock/`

2. **Run the setup script:**
   ```bash
   cd "/home/pi/MJW_Clock/Ludo Test Script"
   python3 create_shortcut.py
   ```

3. **Done!** You should now see a "MJW Clock Control" icon on your desktop.

## Manual Setup (if needed)

If the automatic setup doesn't work, follow these steps:

1. **Make the launch script executable:**
   ```bash
   chmod +x "/home/pi/MJW_Clock/Ludo Test Script/launch_clock_ui.sh"
   ```

2. **Copy the desktop file to your desktop:**
   ```bash
   cp "/home/pi/MJW_Clock/Ludo Test Script/MJW_Clock_Control.desktop" ~/Desktop/
   ```

3. **Make the desktop entry executable:**
   ```bash
   chmod +x ~/Desktop/MJW_Clock_Control.desktop
   ```

## What You Get

- 🖥️ **Desktop Icon**: Double-click to launch the clock control interface
- 📱 **Applications Menu**: Find "MJW Clock Control" in your applications
- 🎯 **No Terminal Required**: Launch directly from the desktop environment

## Requirements

- Raspberry Pi OS (Raspbian)
- Python 3 (pre-installed)
- CustomTkinter (automatically installed by setup script)

## File Structure

```
/home/pi/MJW_Clock/
├── Functioning scripts/
│   ├── clock9.py              # Main clock control
│   ├── skiphour.py           # Skip one hour
│   └── skipmin.py            # Skip one minute
└── Ludo Test Script/
    ├── UserInterface.py       # GUI interface
    ├── launch_clock_ui.sh     # Launch script
    ├── create_shortcut.py     # Desktop setup script
    └── MJW_Clock_Control.desktop  # Desktop entry file
```

## Troubleshooting

- **Icon doesn't appear**: Try logging out and back in
- **Permission denied**: Make sure scripts are executable with `chmod +x`
- **CustomTkinter not found**: Run `pip3 install customtkinter`
- **GPIO errors**: Make sure you're running on a Raspberry Pi with proper GPIO setup

## Usage

1. Click the desktop icon
2. Use the three buttons to control your clock:
   - **🕐 Run Clock**: Start the main clock operation
   - **⏩ Skip 1 Hour**: Advance clock by one hour
   - **⏭️ Skip 1 Minute**: Advance clock by one minute
