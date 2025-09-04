# Modbus RTU Simulator GUI

A comprehensive Python GUI application for testing Modbus RTU communication with timestamp logging and command history.

> 🤖 **AI-Assisted Development**: This project was developed with the assistance of AI to create a professional, feature-rich Modbus RTU testing tool with modern GUI design and comprehensive functionality.

## Features

### 🚀 Core Functionality
- **Serial Port Management**: Automatic detection and selection of available serial ports
- **Modbus RTU Client**: Full support for Modbus RTU protocol with PyModbus integration
- **Real-time Register Display**: 64-register grid with 0x hex prefix formatting
- **Raw Command Support**: Send custom Modbus commands with automatic CRC calculation

### 📋 Command Types
- **Read Operations**: Read Holding Registers, Input Registers, Coils
- **Write Operations**: Write Single/Multiple Registers, Write Single/Multiple Coils
- **Advanced Features**: Command validation, frame analysis, and response parsing

### 📊 Monitoring & Logging
- **Real-time Logging**: Timestamped command execution with response times
- **Command History**: Complete log of all operations with success/failure status
- **Export Functionality**: Export command history to CSV or JSON formats
- **Settings Management**: Save and load connection settings

### 🛠️ Professional Features
- **Error Handling**: Comprehensive error handling with detailed troubleshooting messages
- **Hex Value Display**: Professional 0x prefix formatting for all register values
- **Frame Analysis**: Detailed Modbus frame logging with CRC information
- **Standalone Executable**: Packaged as Windows executable for easy distribution

## Installation

### 🚀 Quick Start (Standalone Executable)

Download the latest release and run directly - no Python installation required!

1. **Download**: Get `ModbusSimulator-v1.0.0.exe` from [Releases](../../releases)
2. **Run**: Double-click to launch - works on any Windows computer

### 🛠️ Development Setup

#### Using uv (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd modbus-rtu-master

# Install dependencies
python -m uv sync

# Run the application
python modbus_simulator_gui.py
```

#### Using pip

```bash
# Install dependencies
pip install pymodbus pyserial

# Run the application
python modbus_simulator_gui.py
```

### 📦 Building from Source

```bash
# Install build dependencies
python -m uv add --dev pyinstaller

# Build executable
python build.py

# Run the built executable
./ModbusSimulator_Portable/ModbusSimulator.exe
```

## Usage

### 🔌 Connection Setup
1. **Select Serial Port**: Choose from detected COM ports
2. **Configure Settings**: Set baud rate (115200), slave ID (1), etc.
3. **Connect**: Click "Connect" to establish Modbus communication

### 📋 Command Execution
1. **Choose Command Type**: Select from Read/Write operations
2. **Set Parameters**: Enter start address and count/length
3. **Enter Values**: For write operations, use 0x hex format (e.g., 0x1234)
4. **Execute**: Click "Execute" to send command to device

### 🔍 Raw Command Support
1. **Enter Raw Bytes**: Type hex bytes like `01 03 00 00 00 06`
2. **Auto CRC**: CRC is calculated and added automatically
3. **Send**: Click "Send Raw" to transmit custom commands

### 📊 Monitoring & Analysis
- **Real-time Display**: 64-register grid shows current values with 0x prefix
- **Command Log**: Timestamped execution log with response times
- **Frame Analysis**: Detailed Modbus frame information with CRC
- **Export Options**: Save command history to CSV/JSON formats

## GUI Layout

### 🖥️ Interface Overview
- **Connection Panel**: Serial port selection, baud rate, slave ID, and connection status
- **Command Controls**: Command type selection, address/length parameters, and execution buttons
- **Register Display**: 64-register grid (8x8) with real-time hex value display
- **Raw Command Panel**: Custom Modbus command input with automatic CRC calculation
- **Results & Log**: Real-time command execution log with timestamps and response times
- **Export Options**: Save command history and connection settings

## Command Types

### 📖 Read Operations
- **Read Holding Registers (FC 03)**: Read 16-bit registers from slave device
- **Read Input Registers (FC 04)**: Read input-only registers
- **Read Coils (FC 01)**: Read single-bit coil states

### ✍️ Write Operations
- **Write Single Register (FC 06)**: Write single 16-bit register
- **Write Multiple Registers (FC 16)**: Write multiple 16-bit registers
- **Write Single Coil (FC 05)**: Write single coil state
- **Write Multiple Coils (FC 15)**: Write multiple coil states

### 🔧 Raw Commands
- **Custom Modbus Frames**: Send any valid Modbus RTU command
- **Automatic CRC**: CRC16 calculation and validation
- **Frame Analysis**: Detailed logging of sent and received frames

## Configuration

### ⚙️ Settings Management
- **Auto-save**: Settings automatically saved to `modbus_settings.json`
- **Manual Save/Load**: Use "Save Settings" button for custom configurations
- **Port Detection**: Automatic COM port detection and refresh

### 🔧 Advanced Configuration
- **Baud Rates**: 9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600
- **Slave IDs**: 1-255 range support
- **Register Range**: 0-63 register display (expandable)

## Requirements

### 🖥️ System Requirements
- **Windows**: Windows 7+ (for executable)
- **Python**: 3.8+ (for development)
- **Memory**: 50MB RAM minimum
- **Storage**: 20MB disk space

### 📦 Dependencies
- **pymodbus** >= 3.0.0 (Modbus communication)
- **pyserial** >= 3.5 (Serial communication)
- **tkinter** (GUI framework - included with Python)

## Troubleshooting

### 🔧 Common Issues

1. **"No response" Error**:
   - Check serial port connection
   - Verify baud rate matches device settings
   - Confirm correct slave ID
   - Try different baud rates (9600, 19200, 38400, 57600, 115200)

2. **Connection Issues**:
   - Ensure device is powered and connected
   - Check COM port selection
   - Verify cable connections
   - Try running as administrator

3. **Permission Errors**:
   - Run as administrator on Windows
   - Add user to dialout group on Linux/Mac

4. **Port Not Found**:
   - Click "Refresh" to update port list
   - Check Device Manager for COM port status
   - Reconnect USB-to-serial adapter

### 🐛 Debug Tips
- Check the log messages for detailed error information
- Use raw commands to test basic communication
- Verify CRC calculation with known good frames
- Test with different Modbus devices

## 🤖 AI Development Notes

This project was developed with AI assistance to demonstrate:
- **Modern Python GUI Development**: Using tkinter with professional design patterns
- **Modbus Protocol Implementation**: Complete RTU communication with PyModbus
- **Professional Packaging**: Automated build system with PyInstaller
- **CI/CD Integration**: GitHub Actions workflows for automated builds and releases
- **Comprehensive Documentation**: Detailed guides and troubleshooting information

The AI-assisted development process included:
- Code architecture and design patterns
- Feature implementation and testing
- Build system configuration
- Documentation and user guides
- Error handling and edge cases

## License

This project is open source and available under the MIT License.

---

**Perfect for Modbus device testing, debugging, and development!** 🚀
