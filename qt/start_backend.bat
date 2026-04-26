@echo off
REM Kuding Judge Helper - 启动脚本（带依赖检查）

echo ========================================
echo Kuding Judge Helper Backend Launcher
echo ========================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://www.python.org/
    pause
    exit /b 1
)

echo [OK] Python found
python --version
echo.

REM 检查并安装依赖
echo Checking and installing dependencies...
pip install -r requirements.txt

if errorlevel 1 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)

echo [OK] Dependencies installed
echo.

REM 检查 Selenium
echo Checking Selenium...
python -c "from selenium import webdriver; print('[OK] Selenium available')" 2>nul
if errorlevel 1 (
    echo Warning: Selenium not available, installing...
    pip install selenium webdriver-manager
)

echo.
echo ========================================
echo Starting Backend Server
echo ========================================
echo.
echo Backend will run on: http://127.0.0.1:5000
echo.
echo Press Ctrl+C to stop the server
echo.

REM 启动后端
python backend.py

pause
