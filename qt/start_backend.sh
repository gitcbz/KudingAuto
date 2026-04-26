#!/bin/bash

# Kuding Judge Helper - 启动脚本（macOS/Linux）

echo "========================================"
echo "Kuding Judge Helper Backend Launcher"
echo "========================================"
echo ""

# 检查 Python 是否安装
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    echo "Please install Python 3.7+ from https://www.python.org/"
    exit 1
fi

echo "[OK] Python found"
python3 --version
echo ""

# 检查并安装依赖
echo "Checking and installing dependencies..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies"
    exit 1
fi

echo "[OK] Dependencies installed"
echo ""

# 检查 Selenium
echo "Checking Selenium..."
python3 -c "from selenium import webdriver; print('[OK] Selenium available')" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Warning: Selenium not available, installing..."
    pip3 install selenium webdriver-manager
fi

echo ""
echo "========================================"
echo "Starting Backend Server"
echo "========================================"
echo ""
echo "Backend will run on: http://127.0.0.1:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# 启动后端
python3 backend.py
