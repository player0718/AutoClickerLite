# Auto Clicker

A simple and easy-to-use Windows desktop automatic mouse clicking tool.

## Features

- Set click interval (supports milliseconds and seconds)
- Choose click type: left click, right click, left double-click
- Choose click position: current mouse position or fixed coordinates
- Real-time display of click status and count
- Fail-safe: move mouse to top-left corner of screen to stop the program

## Technical Notes

### Why Tkinter?

- **Built-in library**: Comes with Python, no need to install additional GUI dependencies
- **Lightweight**: Small program size, fast startup
- **Cross-platform**: Although this tool is primarily for Windows, the code can run on other systems
- **Easy to package**: Fewer dependencies when packaging with PyInstaller

### Thread Safety

This program uses Tkinter's `after()` method to implement timed clicking instead of multi-threading. This approach:
- Executes in the main thread, avoiding thread safety issues
- Does not block the GUI
- Makes code simpler and easier to maintain

---

## Step 1: Environment Setup

### 1.1 Install Python

Ensure Python 3.7 or higher is installed. Check in Command Prompt:

```bash
python --version
```

### 1.2 Install Dependencies

Open Command Prompt (CMD) or PowerShell and run:

```bash
pip install pyautogui pyinstaller
```

Or use requirements.txt:

```bash
pip install -r requirements.txt
```

**Dependencies:**
- `pyautogui`: For controlling mouse clicks
- `pyinstaller`: For packaging into exe files
- `tkinter`: Built into Python, no installation needed

---

## Step 2: Running the Program

### 2.1 Run Python Script Directly

In the project directory, execute:

```bash
python auto_clicker.py
```

### 2.2 Usage Instructions

1. **Set click interval**: Enter a number and select the unit (milliseconds/seconds)
2. **Choose click type**: Left click, right click, or left double-click
3. **Set click position**:
   - Check "Use current mouse position": Uses real-time mouse position when clicking
   - Uncheck: Enter fixed X, Y coordinates
4. **Click "Start"**: Begin auto-clicking
5. **Click "Stop"**: Stop auto-clicking

**Safety tip**: Quickly move the mouse to the top-left corner of the screen to trigger fail-safe and automatically stop clicking.

---

## Step 3: Package as EXE File

### 3.1 Basic Packaging Command

```bash
pyinstaller --onefile --windowed --name "AutoClicker" auto_clicker.py
```

**Parameter descriptions:**
- `--onefile`: Package into a single exe file
- `--windowed`: Don't show console window when running
- `--name`: Specify the generated exe file name

### 3.2 Package with Icon (Optional)

If you have an .ico icon file:

```bash
pyinstaller --onefile --windowed --name "AutoClicker" --icon=icon.ico auto_clicker.py
```

### 3.3 Package Output

After packaging is complete, the exe file is located at:
```
dist/AutoClicker.exe
```

### 3.4 Clean Up Temporary Files (Optional)

```bash
rmdir /s /q build
del AutoClicker.spec
```

---

## Step 4: Distribution and Use

### 4.1 Distributing the exe File

Copy `dist/AutoClicker.exe` to any Windows computer to run it without installing Python.

### 4.2 System Requirements

- Windows 10 or higher
- No dependencies required

### 4.3 Important Notes

1. **Antivirus software**: Some antivirus software may flag false positives; you may need to add it to the trusted list
2. **Administrator privileges**: Some applications may require running the auto-clicker as administrator to click
3. **Screen scaling**: If using fixed coordinates, note that Windows display scaling settings may affect coordinates

---

## FAQ

### Q: Clicks not working?

1. Check if the target window requires administrator privileges
2. Try running the auto-clicker as administrator

### Q: Coordinates are inaccurate?

Check the scaling ratio in Windows Display Settings; it's recommended to set it to 100%.

### Q: How to emergency stop?

Quickly move the mouse to the top-left corner of the screen (near position 0,0) to trigger fail-safe.

---

## Project Structure

```
AutoClickerLite/
├── auto_clicker.py      # Main program source code
├── requirements.txt     # Python dependency list
└── README.md           # Documentation
```

---

## License

MIT License
