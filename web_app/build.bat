@echo off
REM 打包脚本 - 生成单个 EXE 文件（包含所有依赖）

pause
echo.
echo ========================================
echo  Kuding Judge Helper v3.0 - 打包脚本
echo ========================================
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到 Python
    pause
    exit /b 1
)

echo ✓ Python 已安装
echo.

REM 安装所有依赖
echo 正在安装所有依赖...
echo 这可能需要几分钟...
echo.

pip install -q flask flask-cors requests pillow pywebview
pip install -q selenium webdriver-manager
pip install -q paddleocr

if errorlevel 1 (
    echo.
    echo 错误: 依赖安装失败
    pause
    exit /b 1
)

echo ✓ 所有依赖已安装
echo.

REM 检查 PyInstaller
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo 正在安装 PyInstaller...
    pip install -q pyinstaller
)

echo ✓ PyInstaller 已安装
echo.

REM 清理旧的构建
echo 正在清理旧的构建...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo.
echo ========================================
echo  开始打包...
echo ========================================
echo.
echo 这可能需要 5-10 分钟，请耐心等待...
echo.

REM 使用 spec 文件打包
pyinstaller --onefile KudingJudgeHelper.spec

if errorlevel 1 (
    echo.
    echo ========================================
    echo  ✗ 打包失败！
    echo ========================================
    echo.
    echo 请检查错误信息并重试
    pause
    exit /b 1
)

echo.
echo ========================================
echo  ✓ 打包完成！
echo ========================================
echo.
echo EXE 文件位置: dist\KudingJudgeHelper.exe
echo 文件大小:
for %%A in (dist\KudingJudgeHelper.exe) do echo %%~zA 字节
echo.
echo 现在可以运行: dist\KudingJudgeHelper.exe
echo.
pause
