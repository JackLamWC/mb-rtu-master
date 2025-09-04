# Modbus RTU Simulator - Quick Build Reference

## 🚀 One-Command Build

```bash
# Install dependencies and build
python -m uv add --dev pyinstaller && python build.py
```

## 📋 Step-by-Step

1. **Setup**
   ```bash
   python -m uv add --dev pyinstaller
   python -m uv sync
   ```

2. **Build**
   ```bash
   python build.py
   ```

3. **Distribute**
   - Zip `ModbusSimulator_Portable/` folder
   - Share with users

## 📁 What You Get

- `dist/ModbusSimulator.exe` - Standalone executable (~15-20MB)
- `ModbusSimulator_Portable/` - Ready-to-ship package with:
  - ModbusSimulator.exe
  - README.md (if exists)
  - sample_config.json
  - QUICK_START.txt

## 🔧 Manual Build (Alternative)

```bash
python -m uv run pyinstaller --onefile --windowed --name=ModbusSimulator --hidden-import=tkinter --hidden-import=pymodbus --hidden-import=serial --hidden-import=serial.tools modbus_simulator_gui.py
```

## ✅ Testing

```bash
# Test locally
./ModbusSimulator_Portable/ModbusSimulator.exe

# Test on another computer (no Python required)
# Just copy ModbusSimulator_Portable folder and run ModbusSimulator.exe
```

## 🐛 Common Issues

- **Missing modules**: Add `--hidden-import=module_name`
- **Large size**: Normal (~15-20MB with Python runtime and GUI)
- **Antivirus warnings**: Add executable to exceptions
- **Serial port access**: Run as administrator if needed

## 📦 Distribution Options

1. **Single file**: Just `ModbusSimulator.exe`
2. **Portable package**: Whole `ModbusSimulator_Portable/` folder (recommended)
3. **Installer**: Use NSIS/Inno Setup for `.msi`/`.exe` installer

## 🔧 Required Hidden Imports

For Modbus Simulator, ensure these are included:
- `tkinter` - GUI framework
- `pymodbus` - Modbus communication
- `serial` - Serial communication
- `serial.tools` - Serial port detection

## 📊 Build Metrics

- **Build time**: ~2-5 minutes
- **Executable size**: ~15-20MB
- **Startup time**: ~3-5 seconds
- **Memory usage**: ~30-50MB

---

**That's it!** Your Modbus RTU Simulator is now ready for production use. 🎉
