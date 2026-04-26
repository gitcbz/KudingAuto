# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules, collect_data_files
import sys

# 收集所有必需的数据文件和子模块
datas = [
    ('templates', 'templates'),
    ('static', 'static'),
]

# 添加 webview 数据文件
try:
    datas += collect_data_files('webview')
except:
    pass

# 添加 paddleocr 数据文件
try:
    datas += collect_data_files('paddleocr')
except:
    pass

# 添加 selenium 数据文件
try:
    datas += collect_data_files('selenium')
except:
    pass

# 收集所有隐藏导入
hiddenimports = [
    'flask',
    'flask_cors',
    'requests',
    'PIL',
    'webview',
    'selenium',
    'webdriver_manager',
    'paddleocr',
    'cv2',
    'numpy',
    'urllib3',
]

# 添加 paddleocr 的子模块
try:
    hiddenimports += collect_submodules('paddleocr')
except:
    pass

# 添加 selenium 的子模块
try:
    hiddenimports += collect_submodules('selenium')
except:
    pass

# 添加 webview 的子模块
try:
    hiddenimports += collect_submodules('webview')
except:
    pass

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludedimports=['PyQt5', 'PySide6'],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='KudingJudgeHelper',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
