#!/usr/bin/env python3
"""
Create Desktop Icon for MJW Clock Control Interface on Raspberry Pi
Run this script once to create a desktop icon
"""
import os
import shutil
import stat
import subprocess

def create_desktop_icon():
    """Create desktop icon for Raspberry Pi OS"""
    
    # Get current script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Paths
    desktop_path = os.path.expanduser("~/Desktop")
    desktop_entry_source = os.path.join(script_dir, "MJW_Clock_Control.desktop")
    desktop_entry_dest = os.path.join(desktop_path, "MJW_Clock_Control.desktop")
    launch_script = os.path.join(script_dir, "launch_clock_ui.sh")
    
    # Update the desktop entry with correct paths
    desktop_entry_content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=MJW Clock Control
Comment=Control interface for MJW mechanical clock
Exec={launch_script}
Icon=applications-engineering
Terminal=false
Categories=Utility;Engineering;
StartupNotify=true
Path={script_dir}
"""
    
    try:
        # Create desktop directory if it doesn't exist
        os.makedirs(desktop_path, exist_ok=True)
        
        # Write updated desktop entry
        with open(desktop_entry_source, 'w') as f:
            f.write(desktop_entry_content)
        
        # Make launch script executable
        os.chmod(launch_script, stat.S_IRWXU | stat.S_IRGRP | stat.S_IROTH)
        print(f"✓ Made launch script executable: {launch_script}")
        
        # Copy desktop entry to desktop
        shutil.copy2(desktop_entry_source, desktop_entry_dest)
        
        # Make desktop entry executable
        os.chmod(desktop_entry_dest, stat.S_IRWXU | stat.S_IRGRP | stat.S_IROTH)
        
        print(f"✓ Desktop icon created: {desktop_entry_dest}")
        print("✓ You should now see 'MJW Clock Control' icon on your desktop!")
        
        # Also install to applications menu
        applications_dir = os.path.expanduser("~/.local/share/applications")
        os.makedirs(applications_dir, exist_ok=True)
        applications_entry = os.path.join(applications_dir, "MJW_Clock_Control.desktop")
        shutil.copy2(desktop_entry_source, applications_entry)
        print(f"✓ Added to applications menu: {applications_entry}")
        
        # Update desktop database
        try:
            subprocess.run(["update-desktop-database", applications_dir], 
                         capture_output=True, timeout=10)
            print("✓ Updated desktop database")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print("→ Desktop database update skipped (not critical)")
            
    except Exception as e:
        print(f"✗ Error creating desktop icon: {e}")
        print("\n📋 Manual setup instructions:")
        print("1. Make launch script executable:")
        print(f"   chmod +x '{launch_script}'")
        print("2. Copy desktop file to desktop:")
        print(f"   cp '{desktop_entry_source}' '{desktop_entry_dest}'")
        print("3. Make desktop entry executable:")
        print(f"   chmod +x '{desktop_entry_dest}'")

def install_dependencies():
    """Install required Python packages for Raspberry Pi"""
    try:
        print("📦 Checking CustomTkinter installation...")
        import customtkinter
        print("✓ CustomTkinter already installed")
    except ImportError:
        print("📦 Installing CustomTkinter...")
        subprocess.run(["pip3", "install", "customtkinter"], check=True)
        print("✓ CustomTkinter installed successfully")

if __name__ == "__main__":
    print("🕐 MJW Clock Control - Desktop Icon Setup")
    print("=" * 50)
    
    # Install dependencies
    install_dependencies()
    
    # Create desktop icon
    create_desktop_icon()
    
    print("\n🎉 Setup complete!")
    print("💡 You can now:")
    print("   • Double-click the desktop icon to launch the clock control")
    print("   • Find 'MJW Clock Control' in your applications menu")
    print("   • Run the interface anytime without opening a terminal")
