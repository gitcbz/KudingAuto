#!/bin/bash

# Kuding Judge Helper v3.0 - Web 版本启动脚本
# 这个脚本会自动安装依赖并启动应用

echo ""
echo "========================================"
echo " Kuding Judge Helper v3.0 - Web 版本"
echo "========================================"
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 Python 3"
    echo "请从 https://www.python.org 下载并安装 Python 3.7+"
    exit 1
fi

echo "✓ Python 已安装"
echo ""

# 安装依赖
echo "正在安装依赖..."
pip3 install -q flask flask-cors requests pillow

echo "✓ 基础依赖已安装"
echo ""

# 可选依赖
echo "可选: 安装高级功能依赖?"
echo "  1. 安装 Selenium + PaddleOCR (推荐)"
echo "  2. 仅安装 Selenium"
echo "  3. 仅安装 PaddleOCR"
echo "  4. 跳过 (仅使用基础功能)"
echo ""
read -p "请选择 (1-4): " choice

case $choice in
    1)
        echo "正在安装 Selenium 和 PaddleOCR..."
        pip3 install -q selenium webdriver-manager paddleocr
        echo "✓ 已安装"
        ;;
    2)
        echo "正在安装 Selenium..."
        pip3 install -q selenium webdriver-manager
        echo "✓ 已安装"
        ;;
    3)
        echo "正在安装 PaddleOCR..."
        pip3 install -q paddleocr
        echo "✓ 已安装"
        ;;
esac

echo ""
echo "========================================"
echo " 启动应用..."
echo "========================================"
echo ""
echo "打开浏览器访问: http://localhost:5000"
echo "按 Ctrl+C 停止应用"
echo ""

python3 app.py
