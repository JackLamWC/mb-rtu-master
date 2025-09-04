#!/usr/bin/env python3
"""
Build script for packaging the Modbus RTU Simulator into a standalone executable.
"""

import subprocess
import sys
import os
from pathlib import Path

def build_executable():
    """Build the executable using PyInstaller"""
    
    # PyInstaller command
    cmd = [
        "python", "-m", "uv", "run", "pyinstaller",
        "--onefile",                    # Create a single executable file
        "--windowed",                   # No console window (GUI only)
        "--name=ModbusSimulator",       # Name of the executable
        "--icon=icon.ico",              # Optional: add an icon (if you have one)
        "--add-data=README.md;.",       # Include README
        "--hidden-import=tkinter",      # Ensure tkinter is included
        "--hidden-import=pymodbus",     # Ensure pymodbus is included
        "--hidden-import=serial",       # Ensure pyserial is included
        "--hidden-import=serial.tools", # Ensure serial tools are included
        "modbus_simulator_gui.py"       # Main script
    ]
    
    # Remove icon option if no icon file exists
    if not Path("icon.ico").exists():
        cmd = [c for c in cmd if not c.startswith("--icon")]
    
    print("Building Modbus Simulator executable with PyInstaller...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Build successful!")
        print(f"Executable created at: dist/ModbusSimulator.exe")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def create_portable_package():
    """Create a portable package with the executable and documentation"""
    
    dist_dir = Path("dist")
    portable_dir = Path("ModbusSimulator_Portable")
    
    if not dist_dir.exists():
        print("No dist directory found. Run build first.")
        return False
    
    # Create portable directory
    portable_dir.mkdir(exist_ok=True)
    
    # Copy executable
    exe_file = dist_dir / "ModbusSimulator.exe"
    if exe_file.exists():
        import shutil
        shutil.copy2(exe_file, portable_dir / "ModbusSimulator.exe")
        
        # Copy README if it exists
        if Path("README.md").exists():
            shutil.copy2("README.md", portable_dir / "README.md")
        
        # Create a sample configuration file
        sample_config = portable_dir / "sample_config.json"
        with open(sample_config, 'w') as f:
            f.write("""{
  "port": "COM1",
  "baudrate": "115200",
  "slave_id": "1",
  "command_type": "Read Holding Registers",
  "address": "0",
  "count": "1"
}""")
        
        # Create a quick start guide
        quick_start = portable_dir / "QUICK_START.txt"
        with open(quick_start, 'w') as f:
            f.write("""Modbus RTU Simulator - Quick Start Guide

1. CONNECTION SETUP:
   - Connect your Modbus device via serial port
   - Select the correct COM port (e.g., COM1, COM2)
   - Set baud rate (default: 115200)
   - Set slave ID (default: 1)

2. BASIC OPERATIONS:
   - Read Holding Registers: Read data from device
   - Write Holding Registers: Write data to device
   - Write Single Register: Write one register
   - Read Input Registers: Read input data
   - Read/Write Coils: Control digital outputs

3. RAW COMMANDS:
   - Use the "Raw Modbus Command" section
   - Enter hex bytes like: 01 03 00 00 00 06
   - CRC will be calculated automatically
   - Do NOT include CRC in your input

4. TROUBLESHOOTING:
   - "No response" error: Check connection, baud rate, slave ID
   - Verify device is powered and connected
   - Try different baud rates (9600, 19200, 38400, 57600, 115200)
   - Check if device responds to correct slave ID

5. FEATURES:
   - Real-time register monitoring
   - Command history logging
   - Export to CSV/JSON
   - Frame analysis and CRC calculation
   - 0x prefix for hex values

For more help, check the log messages in the application.
""")
        
        print(f"Portable package created at: {portable_dir}")
        print("Contents:")
        for file in portable_dir.iterdir():
            print(f"  - {file.name}")
        return True
    else:
        print("Executable not found in dist directory")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "portable":
        create_portable_package()
    else:
        if build_executable():
            create_portable_package()
