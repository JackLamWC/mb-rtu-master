#!/usr/bin/env python3
"""
Modbus RTU Simulator GUI
A comprehensive GUI application for testing Modbus RTU communication
with timestamp logging and command history.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import serial
import serial.tools.list_ports
from pymodbus.client import ModbusSerialClient
from pymodbus.exceptions import ModbusException
import threading
import time
import json
import csv
from datetime import datetime
from typing import Optional, List, Dict, Any
import queue
import os



class ModbusSimulatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Modbus RTU Simulator")
        self.root.geometry("1000x700")
        self.root.resizable(False, False)  # Fixed window size
        
        # Modbus client
        self.client = None
        self.is_connected = False
        
        # Command history and logging
        self.command_history: List[Dict[str, Any]] = []
        self.log_queue = queue.Queue()
        
        # Create GUI
        self.create_widgets()
        self.setup_layout()
        
        # Start log processing thread
        self.start_log_processor()
        
        # Load saved settings
        self.load_settings()
    
    def create_widgets(self):
        """Create all GUI widgets"""
        # Connection frame
        self.conn_frame = ttk.LabelFrame(self.root, text="Connection Settings", padding=15)
        
        # Create a container frame to center the controls
        controls_container = ttk.Frame(self.conn_frame)
        controls_container.grid(row=0, column=0, sticky="")
        
        # Port selection
        ttk.Label(controls_container, text="Serial Port:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(controls_container, textvariable=self.port_var, width=15, state="readonly")
        self.port_combo.grid(row=0, column=1, padx=(0, 10))
        
        # Refresh ports button
        ttk.Button(controls_container, text="Refresh", command=self.refresh_ports).grid(row=0, column=2, padx=(0, 10))
        
        # Baud rate
        ttk.Label(controls_container, text="Baud Rate:").grid(row=0, column=3, sticky="w", padx=(0, 5))
        self.baud_var = tk.StringVar(value="115200")
        baud_combo = ttk.Combobox(controls_container, textvariable=self.baud_var, 
                                 values=["9600", "19200", "38400", "57600", "115200", "230400", "460800", "921600"], width=10, state="readonly")
        baud_combo.grid(row=0, column=4, padx=(0, 10))
        
        # Slave ID
        ttk.Label(controls_container, text="Slave ID:").grid(row=0, column=5, sticky="w", padx=(0, 5))
        self.slave_id_var = tk.StringVar(value="1")
        slave_id_values = [str(i) for i in range(1, 256)]  # 1 to 255
        slave_id_combo = ttk.Combobox(controls_container, textvariable=self.slave_id_var, 
                                     values=slave_id_values, width=5, state="readonly")
        slave_id_combo.grid(row=0, column=6, padx=(0, 10))
        
        # Connect button
        self.connect_btn = ttk.Button(controls_container, text="Connect", command=self.connect)
        self.connect_btn.grid(row=0, column=7, padx=(0, 5))
        
        # Disconnect button
        self.disconnect_btn = ttk.Button(controls_container, text="Disconnect", command=self.disconnect, state="disabled")
        self.disconnect_btn.grid(row=0, column=8, padx=(5, 0))
        
        # Status label - centered
        self.status_var = tk.StringVar(value="Disconnected")
        self.status_label = ttk.Label(self.conn_frame, textvariable=self.status_var, foreground="red")
        self.status_label.grid(row=1, column=0, pady=(10, 0))
        
        # Center the controls container horizontally
        self.conn_frame.grid_columnconfigure(0, weight=1)
        self.conn_frame.grid_rowconfigure(0, weight=1)
        self.conn_frame.grid_rowconfigure(1, weight=1)
        

        
        # Register display frame
        self.register_frame = ttk.LabelFrame(self.root, text="Register Monitor", padding=10)
        
        # Create register display area
        self.create_register_display()
        
        # Results frame
        self.results_frame = ttk.LabelFrame(self.root, text="Results & Log", padding=10)
        
        # Log text area (minimized)
        self.log_text = scrolledtext.ScrolledText(self.results_frame, height=8, width=80)
        self.log_text.grid(row=0, column=0, columnspan=2, sticky="nsew", pady=(0, 10))
        
        # Export buttons
        export_frame = ttk.Frame(self.results_frame)
        export_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
        
        ttk.Button(export_frame, text="Export to CSV", command=self.export_csv).pack(side="left", padx=(0, 10))
        ttk.Button(export_frame, text="Export to JSON", command=self.export_json).pack(side="left", padx=(0, 10))
        ttk.Button(export_frame, text="Save Settings", command=self.save_settings).pack(side="left")
        
        # Configure grid weights
        self.results_frame.columnconfigure(0, weight=1)
        self.results_frame.rowconfigure(0, weight=1)
    
    def create_register_display(self):
        """Create register display with individual boxes for each register"""
        # Control frame for command selection and parameters
        control_frame = ttk.Frame(self.register_frame)
        control_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        # Command type selection
        ttk.Label(control_frame, text="Command:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        self.cmd_type_var = tk.StringVar(value="Read Holding Registers")
        cmd_type_combo = ttk.Combobox(control_frame, textvariable=self.cmd_type_var, width=25,
                                     values=["Read Holding Registers", "Write Holding Registers", 
                                            "Write Single Register", "Read Input Registers", 
                                            "Read Coils", "Write Coils"], state="readonly")
        cmd_type_combo.grid(row=0, column=1, padx=(0, 10))
        cmd_type_combo.bind("<<ComboboxSelected>>", self.on_cmd_type_change)
        
        # Start register index
        ttk.Label(control_frame, text="Start Index:").grid(row=0, column=2, sticky="w", padx=(0, 5))
        self.start_idx_var = tk.StringVar(value="0")
        start_idx_values = [str(i) for i in range(0, 64)]  # 0 to 63
        start_idx_combo = ttk.Combobox(control_frame, textvariable=self.start_idx_var, 
                                      values=start_idx_values, width=8, state="readonly")
        start_idx_combo.grid(row=0, column=3, padx=(0, 10))
        
        # Length
        ttk.Label(control_frame, text="Length:").grid(row=0, column=4, sticky="w", padx=(0, 5))
        self.length_var = tk.StringVar(value="1")
        length_values = [str(i) for i in range(1, 65)]  # 1 to 64
        length_combo = ttk.Combobox(control_frame, textvariable=self.length_var, 
                                   values=length_values, width=8, state="readonly")
        length_combo.grid(row=0, column=5, padx=(0, 10))
        
        # Action buttons
        ttk.Button(control_frame, text="Execute", command=self.execute_register_command).grid(row=0, column=6, padx=(0, 5))
        ttk.Button(control_frame, text="Clear", command=self.clear_all_registers).grid(row=0, column=7)
        
        # Raw command frame
        raw_frame = ttk.LabelFrame(self.register_frame, text="Raw Modbus Command", padding=5)
        raw_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        
        # Raw command input
        ttk.Label(raw_frame, text="Raw Bytes:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        self.raw_bytes_var = tk.StringVar()
        self.raw_bytes_entry = ttk.Entry(raw_frame, textvariable=self.raw_bytes_var, width=40, font=("Courier", 9))
        self.raw_bytes_entry.grid(row=0, column=1, padx=(0, 10))
        self.raw_bytes_entry.bind('<KeyRelease>', self.validate_raw_input)
        
        # Send raw button
        ttk.Button(raw_frame, text="Send Raw", command=self.send_raw_command).grid(row=0, column=2, padx=(0, 5))
        
        # Help label
        help_label = ttk.Label(raw_frame, text="Format: 01 03 00 00 00 06 (CRC will be added automatically - do not include CRC)", 
                              font=("Arial", 8), foreground="gray")
        help_label.grid(row=1, column=0, columnspan=3, pady=(5, 0), sticky="w")
        
        # Create a fixed frame for all registers (no scrolling)
        registers_frame = ttk.Frame(self.register_frame)
        registers_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # Store references for updating
        self.register_vars = {}
        self.register_entries = {}
        
        # Create register boxes (0-63 for expanded range) in fixed 8x8 grid
        for i in range(64):
            row = i // 8
            col = i % 8
            
            # Register frame with increased width
            reg_frame = ttk.Frame(registers_frame, relief="solid", borderwidth=1)
            reg_frame.grid(row=row, column=col, padx=1, pady=1, sticky="nsew")
            reg_frame.configure(width=150)  # Increased width for 0x prefix
            
            # Register index label (left side)
            idx_label = ttk.Label(reg_frame, text=f"{i:02d}", font=("Arial", 8, "bold"))
            idx_label.pack(side="left", padx=3, pady=2)
            
            # Value display/input (right side) - wider entry field (read-only)
            self.register_vars[i] = tk.StringVar(value="0x0000")
            entry = ttk.Entry(reg_frame, textvariable=self.register_vars[i], width=10, justify="center", font=("Arial", 8), state="readonly")
            entry.pack(side="right", padx=3, pady=2)
            self.register_entries[i] = entry
            
            # Bind hex validation for write operations
            entry.bind('<KeyRelease>', lambda e, reg=i: self.validate_hex_input(reg))
            entry.bind('<FocusOut>', lambda e, reg=i: self.pad_hex_input(reg))
        
        # Configure grid weights for equal distribution in fixed frame
        for i in range(8):
            registers_frame.columnconfigure(i, weight=1)
        for i in range(8):  # 8 rows for 64 registers
            registers_frame.rowconfigure(i, weight=1)
        
        # Configure register frame to expand properly
        self.register_frame.grid_rowconfigure(1, weight=1)
        self.register_frame.grid_columnconfigure(0, weight=1)
    
    def setup_layout(self):
        """Setup the main layout"""
        # Use pack layout for fixed window
        self.conn_frame.pack(fill="x", padx=10, pady=5)
        self.register_frame.pack(fill="both", expand=True, padx=10, pady=5)
        self.results_frame.pack(fill="x", padx=10, pady=5)
        
        # Initial refresh of ports
        self.refresh_ports()
    
    def refresh_ports(self):
        """Refresh available serial ports"""
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.port_combo['values'] = ports
        if ports and not self.port_var.get():
            self.port_var.set(ports[0])
    
    def toggle_connection(self):
        """Toggle Modbus connection (legacy method)"""
        if not self.is_connected:
            self.connect()
        else:
            self.disconnect()
    
    def connect(self):
        """Connect to Modbus device using mbpoll or fallback to PyModbus"""
        try:
            port = self.port_var.get()
            baudrate = int(self.baud_var.get())
            slave_id = int(self.slave_id_var.get())
            
            if not port:
                messagebox.showerror("Error", "Please select a serial port")
                return
            
            # Use PyModbus directly
            self.log_message("Connecting using PyModbus", "INFO")
            self.client = ModbusSerialClient(
                port=port,
                baudrate=baudrate,
                bytesize=8,
                parity='N',
                stopbits=1,
                timeout=5,
                retries=3
            )
    
            
            if self.client.connect():
                self.is_connected = True
                self.connect_btn.config(state="disabled")
                self.disconnect_btn.config(state="normal")
                self.status_var.set("Connected")
                self.status_label.config(foreground="green")
                self.log_message("Connected to Modbus device", "INFO")
            else:
                messagebox.showerror("Error", "Failed to connect to Modbus device")
                
        except Exception as e:
            messagebox.showerror("Error", f"Connection error: {str(e)}")
    
    def disconnect(self):
        """Disconnect from Modbus device"""
        if self.client:
            self.client.close()
            self.client = None
        
        self.is_connected = False
        self.connect_btn.config(state="normal")
        self.disconnect_btn.config(state="disabled")
        self.status_var.set("Disconnected")
        self.status_label.config(foreground="red")
        self.log_message("Disconnected from Modbus device", "INFO")
    
    def on_cmd_type_change(self, event=None):
        """Handle command type change"""
        cmd_type = self.cmd_type_var.get()
        self.update_register_entry_states(cmd_type)
    
    def update_register_entry_states(self, cmd_type):
        """Update register entry states based on command type"""
        if "Write" in cmd_type:
            # Enable editing for write operations
            for entry in self.register_entries.values():
                entry.config(state="normal")
        else:
            # Disable editing for read operations
            for entry in self.register_entries.values():
                entry.config(state="readonly")
    
    def validate_hex_input(self, reg_index):
        """Validate hex input while typing (don't add 0x prefix yet)"""
        if reg_index not in self.register_vars:
            return
        
        current_value = self.register_vars[reg_index].get().upper()
        
        # Remove 0x prefix if present and non-hex characters
        if current_value.startswith('0X'):
            current_value = current_value[2:]
        hex_chars = ''.join(c for c in current_value if c in '0123456789ABCDEF')
        
        # Limit to 4 characters (16-bit register)
        if len(hex_chars) > 4:
            hex_chars = hex_chars[:4]
        
        # Don't add 0x prefix while typing - just validate the hex characters
        # Only update if the hex part changed (not the 0x prefix)
        if hex_chars != current_value and hex_chars != "":
            self.register_vars[reg_index].set(hex_chars)
    
    def pad_hex_input(self, reg_index):
        """Add 0x prefix and pad with leading zeros when user finishes editing (focus out)"""
        if reg_index not in self.register_vars:
            return
        
        current_value = self.register_vars[reg_index].get().upper()
        
        # Remove 0x prefix if present and non-hex characters
        if current_value.startswith('0X'):
            current_value = current_value[2:]
        hex_chars = ''.join(c for c in current_value if c in '0123456789ABCDEF')
        
        # When user finishes editing, add 0x prefix and pad to 4 digits
        if len(hex_chars) == 0:
            # Empty field becomes 0x0000
            self.register_vars[reg_index].set("0x0000")
        elif len(hex_chars) <= 4:
            # Pad with leading zeros and add 0x prefix
            hex_chars = "0x" + hex_chars.zfill(4)
            self.register_vars[reg_index].set(hex_chars)
        else:
            # More than 4 characters, truncate and add 0x prefix
            hex_chars = "0x" + hex_chars[:4]
            self.register_vars[reg_index].set(hex_chars)
    
    def modbus_crc16(self, data):
        """Calculate Modbus CRC16 for the given data bytes"""
        crc = 0xFFFF
        for byte in data:
            crc ^= byte
            for i in range(8):
                if crc & 0x01:
                    crc = (crc >> 1) ^ 0xA001
                else:
                    crc = crc >> 1
        # Return CRC with byte order swapped (LSB first, MSB second)
        return (crc >> 8) | (crc << 8)
    
    def log_modbus_frame(self, cmd_type, start_idx, length, slave_id, values=None):
        """Log the Modbus frame bytes that would be sent"""
        try:
            if cmd_type == "Read Holding Registers":
                # Function code 0x03
                frame_bytes = [
                    slave_id,           # Slave ID
                    0x03,               # Function code (Read Holding Registers)
                    (start_idx >> 8) & 0xFF,  # Start address high byte
                    start_idx & 0xFF,   # Start address low byte
                    (length >> 8) & 0xFF,     # Quantity high byte
                    length & 0xFF       # Quantity low byte
                ]
                
            elif cmd_type == "Write Holding Registers":
                # Function code 0x10
                byte_count = length * 2  # 2 bytes per register
                frame_bytes = [
                    slave_id,           # Slave ID
                    0x10,               # Function code (Write Multiple Registers)
                    (start_idx >> 8) & 0xFF,  # Start address high byte
                    start_idx & 0xFF,   # Start address low byte
                    (length >> 8) & 0xFF,     # Quantity high byte
                    length & 0xFF,      # Quantity low byte
                    byte_count          # Byte count
                ]
                # Add register values (high byte, low byte for each)
                for value in values:
                    frame_bytes.append((value >> 8) & 0xFF)  # High byte
                    frame_bytes.append(value & 0xFF)         # Low byte
                    
            elif cmd_type == "Write Single Register":
                # Function code 0x06
                frame_bytes = [
                    slave_id,           # Slave ID
                    0x06,               # Function code (Write Single Register)
                    (start_idx >> 8) & 0xFF,  # Start address high byte
                    start_idx & 0xFF,   # Start address low byte
                    (values[0] >> 8) & 0xFF,  # Value high byte
                    values[0] & 0xFF    # Value low byte
                ]
                    
            elif cmd_type == "Read Input Registers":
                # Function code 0x04
                frame_bytes = [
                    slave_id,           # Slave ID
                    0x04,               # Function code (Read Input Registers)
                    (start_idx >> 8) & 0xFF,  # Start address high byte
                    start_idx & 0xFF,   # Start address low byte
                    (length >> 8) & 0xFF,     # Quantity high byte
                    length & 0xFF       # Quantity low byte
                ]
                
            elif cmd_type == "Read Coils":
                # Function code 0x01
                frame_bytes = [
                    slave_id,           # Slave ID
                    0x01,               # Function code (Read Coils)
                    (start_idx >> 8) & 0xFF,  # Start address high byte
                    start_idx & 0xFF,   # Start address low byte
                    (length >> 8) & 0xFF,     # Quantity high byte
                    length & 0xFF       # Quantity low byte
                ]
                
            elif cmd_type == "Write Coils":
                # Function code 0x0F
                byte_count = (length + 7) // 8  # Calculate bytes needed for coils
                frame_bytes = [
                    slave_id,           # Slave ID
                    0x0F,               # Function code (Write Multiple Coils)
                    (start_idx >> 8) & 0xFF,  # Start address high byte
                    start_idx & 0xFF,   # Start address low byte
                    (length >> 8) & 0xFF,     # Quantity high byte
                    length & 0xFF,      # Quantity low byte
                    byte_count          # Byte count
                ]
                # Pack coils into bytes
                coil_bytes = []
                for i in range(0, length, 8):
                    byte_val = 0
                    for j in range(8):
                        if i + j < length and values[i + j]:
                            byte_val |= (1 << j)
                    coil_bytes.append(byte_val)
                frame_bytes.extend(coil_bytes)
            
            # Calculate CRC16 for the frame
            crc = self.modbus_crc16(frame_bytes)
            crc_high = crc & 0xFF
            crc_low = (crc >> 8) & 0xFF
            
            # Add CRC bytes to frame (LSB first, MSB second)
            complete_frame = frame_bytes + [crc_low, crc_high]
            
            # Display the complete frame with CRC
            hex_frame = ' '.join([f"{b:02X}" for b in complete_frame])
            self.log_message(f"Modbus Frame: {hex_frame} (CRC: {crc_low:02X} {crc_high:02X})", "INFO")
            
        except Exception as e:
            self.log_message(f"Error generating frame display: {str(e)}", "ERROR")
    

    
    def execute_register_command(self):
        """Execute the selected Modbus command with the specified range"""
        if not self.is_connected:
            messagebox.showerror("Error", "Not connected to Modbus device")
            return
        
        try:
            slave_id = int(self.slave_id_var.get())
            start_idx = int(self.start_idx_var.get())
            length = int(self.length_var.get())
            cmd_type = self.cmd_type_var.get()
            
            if start_idx < 0 or start_idx > 63:
                messagebox.showerror("Error", "Start index must be between 0 and 63")
                return
            
            if length < 1 or length > 64 or (start_idx + length) > 64:
                messagebox.showerror("Error", "Invalid length or range exceeds register limit")
                return
            
            timestamp = datetime.now()
            start_time = time.time()
            
            # Execute command based on type
            if cmd_type == "Read Holding Registers":
                # Log the request details and frame
                self.log_message(f"Sending Read Holding Registers: Start={start_idx}, Count={length}, Device ID={slave_id}", "INFO")
                self.log_modbus_frame(cmd_type, start_idx, length, slave_id)
                
                # Use PyModbus client
                result = self.client.read_holding_registers(start_idx, count=length, device_id=slave_id)
                self.handle_register_result(result, cmd_type, start_idx, length, timestamp, start_time, is_read=True)
                
            elif cmd_type == "Write Holding Registers":
                # For write operations, collect hex values from register entries
                values = []
                for i in range(length):
                    reg_addr = start_idx + i
                    if reg_addr in self.register_vars:
                        try:
                            hex_value = self.register_vars[reg_addr].get().strip()
                            # Remove 0x prefix if present
                            if hex_value.startswith('0x') or hex_value.startswith('0X'):
                                hex_value = hex_value[2:]
                            # Validate hex format (4 digits for 16-bit register)
                            if len(hex_value) != 4:
                                messagebox.showerror("Error", f"Register {reg_addr}: Please enter 4-digit hex value (e.g., 0x1234, 0xABCD)")
                                return
                            # Convert hex string to integer
                            value = int(hex_value, 16)
                            values.append(value)
                        except ValueError:
                            messagebox.showerror("Error", f"Register {reg_addr}: Invalid hex value. Please enter 4-digit hex values (0000-FFFF).")
                            return
                
                # Log the request details with values and frame
                hex_values = [f"{v:04X}" for v in values]
                self.log_message(f"Sending Write Holding Registers: Start={start_idx}, Values={hex_values}, Device ID={slave_id}", "INFO")
                self.log_modbus_frame(cmd_type, start_idx, length, slave_id, values)
                
                # Use PyModbus client
                result = self.client.write_registers(start_idx, values, device_id=slave_id)
                self.handle_register_result(result, cmd_type, start_idx, length, timestamp, start_time, is_read=False, values=values)
                
            elif cmd_type == "Write Single Register":
                # For single register write, only use the first register value
                if start_idx not in self.register_vars:
                    messagebox.showerror("Error", f"Register {start_idx} not found")
                    return
                
                try:
                    hex_value = self.register_vars[start_idx].get().strip()
                    # Remove 0x prefix if present
                    if hex_value.startswith('0x') or hex_value.startswith('0X'):
                        hex_value = hex_value[2:]
                    # Validate hex format (4 digits for 16-bit register)
                    if len(hex_value) != 4:
                        messagebox.showerror("Error", f"Register {start_idx}: Please enter 4-digit hex value (e.g., 0x1234, 0xABCD)")
                        return
                    # Convert hex string to integer
                    value = int(hex_value, 16)
                except ValueError:
                    messagebox.showerror("Error", f"Register {start_idx}: Invalid hex value. Please enter 4-digit hex values (0000-FFFF).")
                    return
                
                # Log the request details with value and frame
                self.log_message(f"Sending Write Single Register: Address={start_idx}, Value={value:04X}, Device ID={slave_id}", "INFO")
                self.log_modbus_frame(cmd_type, start_idx, 1, slave_id, [value])
                
                # Use PyModbus client - use write_register for single register
                result = self.client.write_register(start_idx, value, device_id=slave_id)
                self.handle_register_result(result, cmd_type, start_idx, 1, timestamp, start_time, is_read=False, values=[value])
                
            elif cmd_type == "Read Input Registers":
                self.log_message(f"Sending Read Input Registers: Start={start_idx}, Count={length}, Device ID={slave_id}", "INFO")
                self.log_modbus_frame(cmd_type, start_idx, length, slave_id)
                
                # Use PyModbus client
                result = self.client.read_input_registers(start_idx, count=length, device_id=slave_id)
                self.handle_register_result(result, cmd_type, start_idx, length, timestamp, start_time, is_read=True)
                
            elif cmd_type == "Read Coils":
                self.log_message(f"Sending Read Coils: Start={start_idx}, Count={length}, Device ID={slave_id}", "INFO")
                self.log_modbus_frame(cmd_type, start_idx, length, slave_id)
                
                # Use PyModbus client
                result = self.client.read_coils(start_idx, count=length, device_id=slave_id)
                self.handle_register_result(result, cmd_type, start_idx, length, timestamp, start_time, is_read=True)
                
            elif cmd_type == "Write Coils":
                # Collect values from the register display (0 or 1)
                values = []
                for i in range(length):
                    reg_addr = start_idx + i
                    if reg_addr in self.register_vars:
                        try:
                            value = int(self.register_vars[reg_addr].get())
                            if value not in [0, 1]:
                                messagebox.showerror("Error", f"Coil value in register {reg_addr} must be 0 or 1.")
                                return
                            values.append(bool(value))
                        except ValueError:
                            messagebox.showerror("Error", f"Invalid value in register {reg_addr}. Please use Execute with proper values.")
                            return
                
                # Log the request details with values and frame
                coil_values = [str(int(v)) for v in values]
                self.log_message(f"Sending Write Coils: Start={start_idx}, Values={coil_values}, Device ID={slave_id}", "INFO")
                self.log_modbus_frame(cmd_type, start_idx, length, slave_id, values)
                
                # Use PyModbus client
                result = self.client.write_coils(start_idx, values, device_id=slave_id)
                self.handle_register_result(result, cmd_type, start_idx, length, timestamp, start_time, is_read=False, values=values)
                
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for start index and length")
        except Exception as e:
            self.log_message(f"Error executing command: {str(e)}", "ERROR")
    
    def handle_register_result(self, result, cmd_type, start_idx, length, timestamp, start_time, is_read=True, values=None):
        """Handle the result of register operations"""
        response_time = (time.time() - start_time) * 1000
        
        if result.isError():
            error_msg = str(result)
            self.log_message(f"Error executing {cmd_type}: {error_msg}", "ERROR")
            
            # Try to get more detailed error information
            if hasattr(result, 'exception'):
                self.log_message(f"Exception details: {result.exception}", "ERROR")
            
            # Log that we're expecting a response but didn't get one
            self.log_message("Expected Response: Device should echo back the same frame", "INFO")
            self.log_message("Actual Response: No response received (timeout or communication error)", "ERROR")
        else:
            if is_read:
                # Handle read operations
                if "Register" in cmd_type:
                    read_values = result.registers
                    # Update register display (display as hex)
                    for i, value in enumerate(read_values):
                        reg_addr = start_idx + i
                        if reg_addr in self.register_vars:
                            # Display as 4-digit hex (16-bit register)
                            hex_value = f"0x{value:04X}"
                            self.register_vars[reg_addr].set(hex_value)
                else:  # Coils
                    read_values = result.bits
                    # Update register display (display as hex)
                    for i, value in enumerate(read_values):
                        reg_addr = start_idx + i
                        if reg_addr in self.register_vars:
                            # Display as 4-digit hex (16-bit register)
                            hex_value = f"0x{int(value):04X}"
                            self.register_vars[reg_addr].set(hex_value)
                
                self.log_message(f"{cmd_type} {start_idx}-{start_idx+length-1}: {read_values}, Response Time: {response_time:.2f}ms", "SUCCESS")
                
                # Log raw response bytes (if available from PyModbus)
                # Note: PyModbus doesn't expose raw response bytes, so we show processed data
                if "Register" in cmd_type:
                    self.log_message(f"Response Data: {read_values} (PyModbus processed response)", "INFO")
                else:  # Coils
                    self.log_message(f"Response Data: {read_values} (PyModbus processed response)", "INFO")
                
                # Store in history
                self.command_history.append({
                    'timestamp': timestamp.isoformat(),
                    'command': f"{cmd_type} {start_idx}-{start_idx+length-1}",
                    'address': start_idx,
                    'count': length,
                    'values': read_values,
                    'response_time_ms': response_time,
                    'success': True
                })
            else:
                # Handle write operations
                self.log_message(f"{cmd_type} {start_idx}-{start_idx+length-1}: {values}, Response Time: {response_time:.2f}ms", "SUCCESS")
                
                # Log write response (echo back the written values)
                if values:
                    self.log_message(f"Write Response: Echo back values {values} (Write operation confirmed)", "INFO")
                
                # Store in history
                self.command_history.append({
                    'timestamp': timestamp.isoformat(),
                    'command': f"{cmd_type} {start_idx}-{start_idx+length-1}",
                    'address': start_idx,
                    'count': length,
                    'values': values,
                    'response_time_ms': response_time,
                    'success': True
                })
    
    def clear_all_registers(self):
        """Clear all register values in the display"""
        for var in self.register_vars.values():
            var.set("0x0000")
        self.log_message("All register values cleared", "INFO")
    
    def validate_raw_input(self, event=None):
        """Validate raw hex input format"""
        current_value = self.raw_bytes_var.get().upper()
        
        # Remove non-hex and non-space characters
        cleaned = ''.join(c for c in current_value if c in '0123456789ABCDEF ')
        
        # Ensure proper spacing between bytes
        hex_chars = cleaned.replace(' ', '')
        if len(hex_chars) > 0:
            # Add spaces every 2 characters
            spaced = ' '.join([hex_chars[i:i+2] for i in range(0, len(hex_chars), 2)])
            if spaced != current_value:
                self.raw_bytes_var.set(spaced)
    
    def send_raw_command(self):
        """Send raw Modbus command"""
        if not self.is_connected:
            messagebox.showerror("Error", "Not connected to Modbus device")
            return
        
        raw_input = self.raw_bytes_var.get().strip()
        if not raw_input:
            messagebox.showerror("Error", "Please enter raw bytes")
            return
        
        try:
            # Parse hex bytes
            hex_parts = raw_input.split()
            if len(hex_parts) < 2:
                messagebox.showerror("Error", "Command too short. Minimum 2 bytes required (slave_id + function_code)")
                return
            
            # Validate hex format
            frame_bytes = []
            for part in hex_parts:
                if len(part) != 2:
                    messagebox.showerror("Error", f"Invalid hex byte: {part}. Each byte must be 2 hex digits (e.g., 01, FF)")
                    return
                try:
                    byte_val = int(part, 16)
                    frame_bytes.append(byte_val)
                except ValueError:
                    messagebox.showerror("Error", f"Invalid hex value: {part}")
                    return
            
            # Validate basic Modbus format
            slave_id = frame_bytes[0]
            function_code = frame_bytes[1]
            
            if slave_id < 1 or slave_id > 247:
                messagebox.showerror("Error", f"Invalid slave ID: {slave_id}. Must be 1-247")
                return
            
            if function_code < 1 or function_code > 127:
                messagebox.showerror("Error", f"Invalid function code: {function_code}. Must be 1-127")
                return
            
            # Calculate CRC and add to frame
            crc = self.modbus_crc16(frame_bytes)
            crc_low = crc & 0xFF
            crc_high = (crc >> 8) & 0xFF
            complete_frame = frame_bytes + [crc_high, crc_low]
            
            # Log the complete frame
            hex_frame = ' '.join([f"{b:02X}" for b in complete_frame])
            self.log_message(f"Sending Raw Command: {hex_frame} (CRC: {crc_low:02X} {crc_high:02X})", "INFO")
            
            # Send the raw command using PyModbus
            timestamp = datetime.now()
            start_time = time.time()
            
            # Send raw bytes directly through the serial connection
            if hasattr(self.client, 'socket') and self.client.socket:
                # Send the raw frame
                self.client.socket.write(bytes(complete_frame))
                
                # Read response (this is a simplified approach)
                # In a real implementation, you'd need to parse the response properly
                response_time = (time.time() - start_time) * 1000
                
                self.log_message(f"Raw Command Sent: {hex_frame}, Response Time: {response_time:.2f}ms", "SUCCESS")
                self.log_message("Note: Raw command sent successfully. Response parsing not implemented for raw commands.", "INFO")
                
                # Store in history
                self.command_history.append({
                    'timestamp': timestamp.isoformat(),
                    'command': f"Raw Command: {hex_frame}",
                    'raw_bytes': hex_frame,
                    'response_time_ms': response_time,
                    'success': True
                })
            else:
                self.log_message("Raw Command Error: No active serial connection", "ERROR")
            
        except Exception as e:
            self.log_message(f"Raw Command Error: {str(e)}", "ERROR")

    
    def log_message(self, message, level="INFO"):
        """Add message to log queue"""
        self.log_queue.put({
            'timestamp': datetime.now(),
            'message': message,
            'level': level
        })
    
    def start_log_processor(self):
        """Start the log processing thread"""
        def process_logs():
            while True:
                try:
                    log_entry = self.log_queue.get(timeout=0.1)
                    self.display_log_entry(log_entry)
                except queue.Empty:
                    continue
                except Exception as e:
                    print(f"Log processing error: {e}")
        
        log_thread = threading.Thread(target=process_logs, daemon=True)
        log_thread.start()
    
    def display_log_entry(self, log_entry):
        """Display log entry in the GUI"""
        timestamp = log_entry['timestamp'].strftime("%H:%M:%S.%f")[:-3]
        level = log_entry['level']
        message = log_entry['message']
        
        # Color coding
        colors = {
            'INFO': 'black',
            'SUCCESS': 'green',
            'ERROR': 'red',
            'WARNING': 'orange'
        }
        
        color = colors.get(level, 'black')
        
        # Insert with color
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        
        # Apply color to the last line
        start_line = self.log_text.index(tk.END + "-2l")
        end_line = self.log_text.index(tk.END + "-1l")
        self.log_text.tag_add(level, start_line, end_line)
        self.log_text.tag_config(level, foreground=color)
        
        # Auto-scroll to bottom
        self.log_text.see(tk.END)
    
    def clear_log(self):
        """Clear the log display"""
        self.log_text.delete(1.0, tk.END)
        self.command_history.clear()
    
    def export_csv(self):
        """Export command history to CSV"""
        if not self.command_history:
            messagebox.showwarning("Warning", "No command history to export")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', newline='') as csvfile:
                    if self.command_history:
                        fieldnames = self.command_history[0].keys()
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerows(self.command_history)
                
                self.log_message(f"Command history exported to {filename}", "SUCCESS")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export CSV: {str(e)}")
    
    def export_json(self):
        """Export command history to JSON"""
        if not self.command_history:
            messagebox.showwarning("Warning", "No command history to export")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w') as jsonfile:
                    json.dump(self.command_history, jsonfile, indent=2)
                
                self.log_message(f"Command history exported to {filename}", "SUCCESS")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export JSON: {str(e)}")
    
    def save_settings(self):
        """Save current settings"""
        settings = {
            'port': self.port_var.get(),
            'baudrate': self.baud_var.get(),
            'slave_id': self.slave_id_var.get(),
            'command_type': self.cmd_type_var.get(),
            'address': self.address_var.get(),
            'count': self.count_var.get()
        }
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w') as jsonfile:
                    json.dump(settings, jsonfile, indent=2)
                
                self.log_message(f"Settings saved to {filename}", "SUCCESS")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save settings: {str(e)}")
    
    def load_settings(self):
        """Load settings from file"""
        try:
            with open('modbus_settings.json', 'r') as jsonfile:
                settings = json.load(jsonfile)
                
                self.port_var.set(settings.get('port', ''))
                self.baud_var.set(settings.get('baudrate', '115200'))
                self.slave_id_var.set(settings.get('slave_id', '1'))
                self.cmd_type_var.set(settings.get('command_type', 'Read Holding Registers'))
                self.address_var.set(settings.get('address', '0'))
                self.count_var.set(settings.get('count', '1'))
                
        except FileNotFoundError:
            pass  # No settings file, use defaults
        except Exception as e:
            self.log_message(f"Failed to load settings: {str(e)}", "WARNING")


def main():
    """Main application entry point"""
    root = tk.Tk()
    app = ModbusSimulatorGUI(root)
    
    # Handle window closing
    def on_closing():
        if app.is_connected:
            app.disconnect()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
