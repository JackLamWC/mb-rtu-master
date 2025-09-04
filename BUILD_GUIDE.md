# Modbus RTU Simulator - Build Guide

This guide explains how to build the Modbus RTU Simulator into a standalone executable that can run on any Windows computer without requiring Python installation.

## Prerequisites

- Python 3.8 or higher
- `uv` package manager
- Windows operating system (for building Windows executables)

## Quick Start

### 1. Install Dependencies

```bash
# Install PyInstaller (build tool)
python -m uv add --dev pyinstaller

# Sync all dependencies
python -m uv sync
```

### 2. Build the Executable

```bash
# Run the build script
python build.py
```

This will create:
- `dist/ModbusSimulator.exe` - The standalone executable
- `ModbusSimulator_Portable/` - A portable package ready for distribution

## Detailed Build Process

### Manual Build (Alternative to build.py)

If you prefer to build manually or customize the build process:

```bash
# Build with PyInstaller directly
python -m uv run pyinstaller \
    --onefile \
    --windowed \
    --name=ModbusSimulator \
    --hidden-import=tkinter \
    --hidden-import=pymodbus \
    --hidden-import=serial \
    --hidden-import=serial.tools \
    modbus_simulator_gui.py
```

### Build Options Explained

- `--onefile`: Creates a single executable file instead of a folder
- `--windowed`: No console window (GUI only)
- `--name=ModbusSimulator`: Sets the executable name
- `--hidden-import=tkinter`: Ensures tkinter GUI library is included
- `--hidden-import=pymodbus`: Ensures PyModbus library is included
- `--hidden-import=serial`: Ensures PySerial library is included
- `--hidden-import=serial.tools`: Ensures serial tools are included

### Optional: Adding an Icon

1. Create or obtain an `.ico` file (e.g., `icon.ico`)
2. Modify the build command to include: `--icon=icon.ico`

## File Structure After Build

```
mb-master/
├── dist/
│   └── ModbusSimulator.exe          # Main executable (~15-20MB)
├── build/                           # Temporary build files
├── ModbusSimulator_Portable/        # Ready-to-distribute package
│   ├── ModbusSimulator.exe         # Executable
│   ├── README.md                   # Documentation (if exists)
│   ├── sample_config.json          # Sample configuration
│   └── QUICK_START.txt             # Quick start guide
├── ModbusSimulator.spec             # PyInstaller configuration
└── build.py                         # Build script
```

## Distribution

### Option 1: Single Executable
- Copy `dist/ModbusSimulator.exe` to target computer
- Double-click to run

### Option 2: Portable Package (Recommended)
- Zip the `ModbusSimulator_Portable` folder
- Extract on target computer
- Run `ModbusSimulator.exe`

## Troubleshooting

### Common Issues

1. **"Module not found" errors**
   ```bash
   # Add missing modules to build command
   --hidden-import=module_name
   ```

2. **Large executable size**
   - This is normal for PyInstaller (includes Python runtime)
   - Size: ~15-20MB is typical for GUI applications with PyModbus

3. **Antivirus false positives**
   - Some antivirus software may flag PyInstaller executables
   - This is a known issue with packaged Python applications
   - Add exception or sign the executable

4. **Serial port access issues**
   - Ensure the executable has proper permissions
   - Run as administrator if needed for COM port access

### Build on Different Platforms

- **Windows executable**: Build on Windows
- **Linux executable**: Build on Linux with `--onefile`
- **macOS executable**: Build on macOS with `--onefile`

## Advanced Configuration

### Custom PyInstaller Spec File

The build process creates a `ModbusSimulator.spec` file. You can customize it for advanced builds:

```python
# ModbusSimulator.spec
a = Analysis(['modbus_simulator_gui.py'],
             pathex=[],
             binaries=[],
             datas=[('README.md', '.')],
             hiddenimports=['tkinter', 'pymodbus', 'serial', 'serial.tools'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=None,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='ModbusSimulator',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,  # Set to True for debugging
          icon='icon.ico')  # Optional icon
```

Then build with:
```bash
python -m uv run pyinstaller ModbusSimulator.spec
```

## Testing the Executable

1. **Test on build machine**:
   ```bash
   # Run the executable
   ./dist/ModbusSimulator.exe
   
   # Or from portable package
   ./ModbusSimulator_Portable/ModbusSimulator.exe
   ```

2. **Test on clean machine**:
   - Copy to a computer without Python installed
   - Verify all features work correctly
   - Test with actual Modbus devices
   - Test serial port communication

## Build Script Usage

The included `build.py` script supports additional options:

```bash
# Build executable and create portable package
python build.py

# Only create portable package (if executable already exists)
python build.py portable
```

## Dependencies

The executable includes these dependencies automatically:
- Python runtime
- tkinter (GUI framework)
- pymodbus (Modbus communication)
- pyserial (Serial communication)
- datetime, threading, queue (standard library)

## Performance Notes

- **Startup time**: 3-5 seconds (normal for packaged Python apps with GUI)
- **Memory usage**: ~30-50MB (includes Python runtime and GUI)
- **File size**: ~15-20MB (all dependencies bundled)

## Deployment Checklist

- [ ] Build successful without errors
- [ ] Executable runs on build machine
- [ ] Test on machine without Python
- [ ] Verify all Modbus communication features work
- [ ] Test serial port detection and connection
- [ ] Check register read/write operations
- [ ] Verify raw command functionality
- [ ] Test CRC calculation
- [ ] Check export functionality
- [ ] Verify error handling and logging

## Automation

You can integrate the build process into CI/CD:

```yaml
# GitHub Actions example
- name: Build executable
  run: |
    python -m uv add --dev pyinstaller
    python build.py
    
- name: Upload artifacts
  uses: actions/upload-artifact@v3
  with:
    name: ModbusSimulator-Windows
    path: ModbusSimulator_Portable/
```

## Support

For build issues:
1. Check that all dependencies are installed: `python -m uv sync`
2. Verify Python version: `python --version` (3.8+ required)
3. Check PyInstaller version: `python -m uv run pyinstaller --version`
4. Review build logs for specific error messages
5. Ensure all required modules are included in hidden-imports

---

**Ready to distribute!** 🚀

Your Modbus RTU Simulator is now packaged as a standalone executable that can run on any Windows computer without requiring Python installation.
