# Running Instructions for Claw Personal Assistant

## Problem Description
When attempting to run the Claw Personal Assistant project on Windows, users may encounter the following error:

```
Command exited with code 1 —— 你这个错误几乎每次都会发生，每次都要重复来一遍，你要记住你修复的结果，不要每次犯同样的错误，记下来
[tools] exec failed: λ :1 ַ: 37 + cd "F:\AIP\claw-personal-assistant" && python claw_main.py + ~~ ǡ&&Ǵ˰汾еЧָ
```

This error occurs because Windows PowerShell has issues with the `&&` operator syntax when executing commands from OpenClaw.

## Solution

### Method 1: Using Batch File (Recommended)
Create a batch file to properly handle the directory change and Python execution:

```batch
@echo off
cd /d "F:\AIP\claw-personal-assistant"
call venv\Scripts\activate.bat
python claw_main.py
```

Then execute the batch file using:
```bash
cmd /c "F:\AIP\claw-personal-assistant\run_claw.bat"
```

### Method 2: Direct Command Execution
Alternatively, execute the Python script directly from the correct directory:

```bash
cd /d "F:\AIP\claw-personal-assistant" && cmd /c "call venv\\Scripts\\activate.bat && python claw_main.py"
```

### Method 3: Using Python Directly
If the virtual environment is already activated:

```bash
cd /d "F:\AIP\claw-personal-assistant" && python claw_main.py
```

## Key Points
1. Use `cd /d` to change both directory and drive in Windows
2. Activate the virtual environment with `call venv\Scripts\activate.bat`
3. Use `cmd /c` to ensure proper execution of chained commands
4. The batch file method is most reliable for recurring executions

## Troubleshooting
- If you get "python is not recognized", make sure the virtual environment is activated
- If you encounter encoding issues, ensure your console uses UTF-8
- For permission issues, run as administrator if necessary