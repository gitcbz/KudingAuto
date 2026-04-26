@echo off
REM Kuding Judge Helper v3.0 - Web 版本启动脚本
REM 这个脚本会自动安装依赖并启动应用

echo.
echo ========================================
echo  Kuding Judge Helper v3.0 - Web 版本
echo ========================================
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到 Python
    echo 请从 https://www.python.org 下载并安装 Python 3.7+
    pause
    exit /b 1
)

echo ✓ Python 已安装
echo.

REM 安装依赖
echo 正在安装依赖...
pip install -q flask flask-cors requests pillow

echo ✓ 基础依赖已安装
echo.

REM 可选依赖
echo 可选: 安装高级功能依赖?
echo   1. 安装 Selenium + PaddleOCR (推荐)
echo   2. 仅安装 Selenium
echo   3. 仅安装 PaddleOCR
echo   4. 跳过 (仅使用基础功能)
echo.
set /p choice="请选择 (1-4): "

if "%choice%"=="1" (
    echo 正在安装 Selenium 和 PaddleOCR...
    pip install -q selenium webdriver-manager paddleocr
    echo ✓ 已安装
) else if "%choice%"=="2" (
    echo 正在安装 Selenium...
    pip install -q selenium webdriver-manager
    echo ✓ 已安装
) else if "%choice%"=="3" (
    echo 正在安装 PaddleOCR...
    pip install -q paddleocr
    echo ✓ 已安装
)

echo.
echo ========================================
echo  启动应用...
echo ========================================
echo.
echo 打开浏览器访问: http://localhost:5000
echo 按 Ctrl+C 停止应用
echo.

python app.py
