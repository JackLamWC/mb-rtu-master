# GitHub Actions Workflow Guide

This guide explains how to use the automated build and release workflows for the Modbus RTU Simulator project.

## 🔄 Available Workflows

### 1. **Build Workflow** (`.github/workflows/build.yml`)
- **Triggers**: Push to main/master/develop, Pull Requests
- **Purpose**: Continuous Integration - builds executable on every code change
- **Outputs**: Build artifacts for testing

### 2. **Release Workflow** (`.github/workflows/release.yml`)
- **Triggers**: Version tags (v1.0.0), Manual trigger
- **Purpose**: Create official releases with downloadable executables
- **Outputs**: GitHub Release with zip file

## 🚀 How to Create a Release

### Method 1: Git Tags (Recommended)

```bash
# 1. Commit your changes
git add .
git commit -m "Release v1.0.0"

# 2. Create and push a version tag
git tag v1.0.0
git push origin v1.0.0
```

This automatically triggers the release workflow and creates:
- GitHub Release page
- `ModbusSimulator-v1.0.0-Windows.zip` download

### Method 2: Manual Trigger

1. Go to your GitHub repository
2. Click **Actions** tab
3. Select **Create Release** workflow
4. Click **Run workflow**
5. Enter version (e.g., `v1.0.0`)
6. Click **Run workflow**

## 📦 What Gets Built

Each workflow creates:

- **`ModbusSimulator.exe`** - Standalone executable (~15-20MB)
- **`ModbusSimulator-vX.X.X-Windows.zip`** - Complete package with:
  - ModbusSimulator.exe
  - README.md (if exists)
  - sample_config.json
  - QUICK_START.txt

## 🔍 Monitoring Builds

### Check Build Status
1. Go to **Actions** tab in your GitHub repo
2. Click on the latest workflow run
3. Monitor progress in real-time

### Download Build Artifacts
- **During development**: Download from Actions → Artifacts
- **For releases**: Download from Releases page

## 🛠️ Workflow Configuration

### Customizing Build Settings

Edit `.github/workflows/build.yml` to modify:

```yaml
# Change Python version
- name: Set up Python
  uses: actions/setup-python@v4
  with:
    python-version: '3.11'  # Change this

# Add build options
- name: Build executable
  run: |
    python build.py
    # Add custom build steps here
```

### Customizing Release Notes

Edit `.github/workflows/release.yml` to modify the release description:

```yaml
body: |
  ## Modbus RTU Simulator ${{ env.VERSION }}
  
  ### 🚀 New Features
  - Your new features here
  
  ### 🐛 Bug Fixes
  - Your bug fixes here
```

## 🔧 Troubleshooting

### Build Fails

1. **Check the logs**:
   - Go to Actions → Failed workflow → Click on failed step
   - Review error messages

2. **Common issues**:
   ```bash
   # Missing dependencies
   python -m uv add --dev missing-package
   
   # PyInstaller issues
   python -m uv run pyinstaller --log-level DEBUG modbus_simulator_gui.py
   ```

### Release Not Created

1. **Check permissions**: Ensure `GITHUB_TOKEN` has release permissions
2. **Verify tag format**: Use `v1.0.0` format (with 'v' prefix)
3. **Check workflow triggers**: Ensure tag matches pattern in workflow

### Large Artifact Size

```yaml
# Reduce retention days to save storage
retention-days: 7  # Instead of 30
```

## 📋 Workflow Triggers Summary

| Event | Build Workflow | Release Workflow |
|-------|----------------|------------------|
| Push to main | ✅ | ❌ |
| Pull Request | ✅ | ❌ |
| Version tag (v1.0.0) | ✅ | ✅ |
| Manual trigger | ✅ | ✅ |

## 🎯 Best Practices

### 1. **Semantic Versioning**
- `v1.0.0` - Major release
- `v1.1.0` - Minor update
- `v1.0.1` - Bug fix

### 2. **Pre-release Testing**
```bash
# Test locally before release
python build.py
./ModbusSimulator_Portable/ModbusSimulator.exe
```

### 3. **Release Checklist**
- [ ] All tests pass
- [ ] Code reviewed
- [ ] Documentation updated
- [ ] Version number updated
- [ ] Tag created and pushed

### 4. **Branch Protection**
- Protect main branch
- Require PR reviews
- Require status checks

## 🔐 Security

### Secrets Used
- `GITHUB_TOKEN` - Automatically provided by GitHub
- No additional secrets required

### Permissions
The workflows need:
- **Contents**: Read (checkout code)
- **Actions**: Write (upload artifacts)
- **Releases**: Write (create releases)

## 📊 Monitoring & Analytics

### Build Metrics
- Build time: ~5-10 minutes
- Artifact size: ~15-20MB
- Success rate: Monitor in Actions tab

### Storage Usage
- Artifacts: 7-day retention
- Releases: Permanent storage
- Clean up old artifacts regularly

## 🚀 Advanced Usage

### Multi-platform Builds
```yaml
strategy:
  matrix:
    os: [windows-latest, ubuntu-latest, macos-latest]
```

### Conditional Releases
```yaml
if: startsWith(github.ref, 'refs/tags/v')
```

### Custom Notifications
Add Slack/Discord notifications:
```yaml
- name: Notify on success
  uses: 8398a7/action-slack@v3
  with:
    status: success
```

## 🎯 Modbus Simulator Specific Notes

### Build Requirements
- Windows environment for Windows executable
- Python 3.11+ recommended
- All Modbus dependencies included automatically

### Testing Checklist
- [ ] Serial port detection works
- [ ] Modbus communication functions
- [ ] Register read/write operations
- [ ] Raw command functionality
- [ ] CRC calculation accuracy
- [ ] Export features work
- [ ] Error handling displays correctly

---

## 🎉 Quick Start

1. **Push your code** to GitHub
2. **Create a tag**: `git tag v1.0.0 && git push origin v1.0.0`
3. **Watch the magic**: Go to Actions tab and see the build
4. **Download**: Go to Releases and download your executable!

Your Modbus RTU Simulator is now fully automated for builds and releases! 🚀
