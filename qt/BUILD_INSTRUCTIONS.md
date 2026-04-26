# 构建说明

## 系统要求

### Windows
- Visual Studio 2019+ 或 MinGW
- Qt 5.15+ 或 Qt 6.0+
- Python 3.7+
- CMake 3.16+（可选）

### macOS
- Xcode 12+
- Qt 5.15+ 或 Qt 6.0+
- Python 3.7+
- CMake 3.16+（可选）

### Linux
- GCC 7+ 或 Clang 5+
- Qt 5.15+ 或 Qt 6.0+
- Python 3.7+
- CMake 3.16+（可选）

## 方法 1：使用 Qt Creator（推荐）

### 步骤 1：安装 Qt
1. 下载 Qt 在线安装程序：https://www.qt.io/download
2. 安装 Qt 5.15+ 或 Qt 6.0+
3. 选择合适的编译器（MSVC、MinGW 或 GCC）

### 步骤 2：打开项目
1. 启动 Qt Creator
2. 打开 `KudingJudge.pro`
3. 选择合适的 Kit

### 步骤 3：构建
1. 点击"构建"菜单 → "构建项目"
2. 或按 Ctrl+B

### 步骤 4：运行
1. 点击"构建"菜单 → "运行"
2. 或按 Ctrl+R

## 方法 2：使用 CMake

### 步骤 1：创建构建目录
```bash
mkdir build
cd build
```

### 步骤 2：配置
```bash
# Windows (MSVC)
cmake -G "Visual Studio 16 2019" ..

# Windows (MinGW)
cmake -G "MinGW Makefiles" ..

# macOS
cmake -G "Xcode" ..

# Linux
cmake -G "Unix Makefiles" ..
```

### 步骤 3：构建
```bash
# Windows
cmake --build . --config Release

# macOS/Linux
cmake --build . --config Release
```

### 步骤 4：运行
```bash
# Windows
.\bin\KudingJudge.exe

# macOS/Linux
./bin/KudingJudge
```

## 方法 3：使用 qmake

### 步骤 1：生成 Makefile
```bash
qmake KudingJudge.pro
```

### 步骤 2：构建
```bash
# Windows (MinGW)
mingw32-make

# Windows (MSVC)
nmake

# macOS/Linux
make
```

### 步骤 3：运行
```bash
# Windows
release\KudingJudge.exe

# macOS/Linux
./KudingJudge
```

## 后端设置

### 步骤 1：安装 Python 依赖
```bash
pip install -r requirements.txt
```

### 步骤 2：启动后端服务
```bash
python backend.py
```

后端将在 `http://127.0.0.1:5000` 启动

### 步骤 3：验证后端
在浏览器中访问：`http://127.0.0.1:5000/api/status`

应该返回：
```json
{
  "success": true,
  "logged_in": false,
  "ocr_engine": "paddle"
}
```

## 常见问题

### Q: Qt 找不到
A: 确保 Qt 在 PATH 中，或在 Qt Creator 中配置 Kit

### Q: 编译错误：找不到 QNetworkAccessManager
A: 确保 .pro 文件中包含 `QT += network`

### Q: 后端无法连接
A: 
1. 确保后端服务正在运行
2. 检查 5000 端口是否被占用
3. 检查防火墙设置

### Q: OCR 模型加载失败
A:
1. 确保 PaddleOCR 已安装
2. 检查网络连接（首次加载需要下载模型）
3. 尝试切换到其他 OCR 引擎

### Q: 编译时内存不足
A:
1. 关闭其他应用
2. 使用 `-j1` 限制并行编译
3. 增加虚拟内存

## 调试

### 启用调试模式
在 Settings 标签页中勾选"Debug Mode"

### 查看日志
所有日志输出在应用的日志面板中

### 后端调试
```bash
# 启用 Flask 调试模式
export FLASK_ENV=development
python backend.py
```

## 发布

### Windows
```bash
# 收集依赖
windeployqt.exe KudingJudge.exe

# 创建安装程序（可选）
# 使用 NSIS 或 WiX
```

### macOS
```bash
# 创建 .app 包
macdeployqt KudingJudge.app

# 创建 DMG（可选）
hdiutil create -volname KudingJudge -srcfolder . -ov -format UDZO KudingJudge.dmg
```

### Linux
```bash
# 创建 AppImage（可选）
# 使用 linuxdeployqt
```

## 性能优化

### 编译优化
```bash
# 启用优化
qmake CONFIG+=release KudingJudge.pro

# 或在 CMake 中
cmake -DCMAKE_BUILD_TYPE=Release ..
```

### 运行时优化
1. 预加载 OCR 模型
2. 使用连接池
3. 缓存验证码

## 支持

如有问题，请查看：
- README.md - 项目文档
- QUICKSTART.md - 快速开始
- PROJECT_SUMMARY.md - 项目总结
