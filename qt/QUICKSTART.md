# 快速开始指南

## 第一步：安装依赖

### Windows

```bash
# 安装 Python 依赖
pip install -r requirements.txt

# 如果使用 PaddleOCR（推荐）
pip install paddleocr
```

### macOS/Linux

```bash
# 安装 Python 依赖
pip3 install -r requirements.txt

# 如果使用 PaddleOCR
pip3 install paddleocr
```

## 第二步：启动后端服务

### Windows
双击 `start_backend.bat` 或在命令行运行：
```bash
python backend.py
```

### macOS/Linux
```bash
python3 backend.py
```

后端将在 `http://127.0.0.1:5000` 启动

## 第三步：编译 Qt 前端

### 使用 Qt Creator
1. 打开 Qt Creator
2. 打开项目 `KudingJudge.pro`
3. 选择合适的 Kit
4. 点击"构建"（Ctrl+B）
5. 点击"运行"（Ctrl+R）

### 使用 CMake
```bash
mkdir build
cd build
cmake ..
cmake --build .
./bin/KudingJudge
```

## 第四步：使用应用

1. **登录**
   - 输入用户名和密码
   - 点击"Refresh"获取验证码
   - 勾选"Auto OCR"自动识别
   - 点击"Login"

2. **测试提交**
   - 选择编程语言
   - 选择代码文件
   - 输入测试数据
   - 点击"Submit Test"

3. **题目提交**
   - 输入题目编号
   - 获取验证码
   - 输入代码
   - 点击"Submit Problem"

## 常见问题

### 后端无法启动
- 检查 Python 版本（需要 3.7+）
- 检查依赖是否安装完整
- 检查 5000 端口是否被占用

### Qt 编译失败
- 确保 Qt 版本 5.15+
- 检查 C++ 编译器版本
- 清理构建目录重新编译

### OCR 识别不准
- 尝试"OCR Enhanced"选项
- 尝试"Super OCR"模式
- 在设置中切换 OCR 引擎

## 获取帮助

查看 README.md 了解更多信息
