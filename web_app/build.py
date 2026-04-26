#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kuding Judge Helper v3.0 - 打包脚本
自动安装依赖并生成 EXE 文件
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description=""):
    """运行命令"""
    if description:
        print(f"\n{description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"错误: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"错误: {e}")
        return False

def main():
    print("\n" + "=" * 50)
    print("  Kuding Judge Helper v3.0 - 打包脚本")
    print("=" * 50)

    # 检查 Python
    print("\n✓ Python 已安装")

    # 安装依赖
    print("\n正在安装依赖...")
    print("这可能需要几分钟...")

    dependencies = [
        "flask==2.3.0",
        "flask-cors==4.0.0",
        "requests==2.31.0",
        "pillow==10.0.0",
        "pywebview==5.0.0",
        "selenium==4.15.0",
        "webdriver-manager==4.0.1",
        "paddleocr==2.7.0.3",
        "pyinstaller",
    ]

    for dep in dependencies:
        print(f"  安装 {dep}...")
        if not run_command(f"pip install -q {dep}"):
            print(f"✗ 安装 {dep} 失败")
            return False

    print("\n✓ 所有依赖已安装")

    # 清理旧的构建
    print("\n正在清理旧的构建...")
    for path in ["build", "dist"]:
        if os.path.exists(path):
            import shutil
            shutil.rmtree(path)

    # 打包
    print("\n" + "=" * 50)
    print("  开始打包...")
    print("=" * 50)
    print("\n这可能需要 5-10 分钟，请耐心等待...\n")

    if not run_command("pyinstaller --onefile KudingJudgeHelper.spec"):
        print("\n✗ 打包失败！")
        return False

    # 检查输出
    exe_path = Path("dist") / "KudingJudgeHelper.exe"
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print("\n" + "=" * 50)
        print("  ✓ 打包完成！")
        print("=" * 50)
        print(f"\nEXE 文件位置: {exe_path}")
        print(f"文件大小: {size_mb:.1f} MB")
        print(f"\n现在可以运行: {exe_path}")
        return True
    else:
        print("\n✗ 打包失败：未找到 EXE 文件")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
