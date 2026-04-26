# Kuding Judge Helper v3.0

现代化的酷丁评测系统 GUI 工具，采用 Qt C++ 前端 + Python 后端架构。

## 功能特性

- ✨ 美观的 Qt C++ 用户界面
- 🔐 支持登录和记住密码
- 📝 代码编辑器（带行号和语法高亮）
- 🧪 测试代码提交和结果查询
- 📋 题目代码提交
- 🤖 高精度 OCR 验证码识别（PaddleOCR/EasyOCR）
- 🌐 Selenium JavaScript 解密支持
- 🔧 灵活的设置面板
- 📊 实时日志输出

## 项目结构

```
qt/
├── KudingJudge.pro          # Qt 项目文件
├── backend.py               # Python 后端服务
├── src/
│   ├── main.cpp             # 主程序入口
│   ├── mainwindow.h/cpp     # 主窗口
│   ├── backend_client.h/cpp # 后端通信客户端
│   ├── code_editor.h/cpp    # 代码编辑器组件
│   ├── login_tab.h/cpp      # 登录标签页
│   ├── test_tab.h/cpp       # 测试提交标签页
│   ├── problem_tab.h/cpp    # 题目提交标签页
│   └── settings_tab.h/cpp   # 设置标签页
└── README.md
```

## 安装和运行

### 前置要求

#### Qt 开发环境
- Qt 5.15+ 或 Qt 6.0+
- Qt Creator（推荐）
- C++17 编译器

#### Python 后端
```bash
pip install -r requirements.txt
```

**重要**：需要以下组件
- Python 3.7+
- Google Chrome 浏览器
- Selenium WebDriver（自动安装）
- webdriver-manager（自动管理 ChromeDriver）

### 编译 Qt 前端

1. 使用 Qt Creator 打开 `KudingJudge.pro`
2. 选择合适的 Kit（MSVC 或 MinGW）
3. 点击"构建"或按 Ctrl+B

### 运行后端服务

```bash
# Windows
start_backend.bat

# macOS/Linux
./start_backend.sh
# 或
python3 backend.py
```

后端将在 `http://127.0.0.1:5000` 启动

**首次运行**：会自动下载 ChromeDriver 和 OCR 模型，请耐心等待

### 运行前端

编译完成后，运行生成的可执行文件

## 使用说明

### 登录
1. 点击"Login"标签页
2. 点击验证码图片或"Refresh"按钮获取验证码
3. 勾选"Auto OCR"自动识别验证码
4. 输入用户名、密码和验证码
5. 点击"Login"登录

### 测试提交
1. 点击"Test Submit"标签页
2. 选择编程语言
3. 选择代码文件或输入代码
4. 输入测试数据
5. 点击"Submit Test"提交

### 题目提交
1. 点击"Problem Submit"标签页
2. 输入题目编号
3. 获取验证码并输入
4. 在代码编辑器中输入代码
5. 点击"Submit Problem"提交

### 设置
1. 点击"Settings"标签页
2. 配置 API URL（如需使用远程服务）
3. 选择 OCR 引擎
4. 选择语言
5. 点击"Save"保存设置

## OCR 引擎对比

| 引擎 | 精度 | 速度 | 内存占用 | 推荐 |
|------|------|------|---------|------|
| PaddleOCR | 99%+ | 中等 | 中等 | ✅ |
| EasyOCR | 95%+ | 较慢 | 较大 | ✓ |
| Tesseract | 85%+ | 快 | 小 | - |

## 常见问题

### Q: 后端无法连接
A: 确保 Python 后端服务正在运行，检查 `http://127.0.0.1:5000` 是否可访问

### Q: ChromeDriver 找不到
A:
- 自动安装：`pip install webdriver-manager`
- 手动安装：下载 ChromeDriver 并添加到 PATH
- 详见 SELENIUM_SETUP.md

### Q: Chrome 浏览器找不到
A:
- 确保已安装 Google Chrome
- 检查 Chrome 是否在 PATH 中
- 详见 INSTALLATION.md

### Q: OCR 识别不准确
A:
- 尝试勾选"OCR Enhanced"选项
- 切换到"Super OCR"模式
- 在设置中选择不同的 OCR 引擎

### Q: 登录失败
A:
- 检查用户名和密码是否正确
- 确保验证码输入正确
- 尝试刷新验证码重新登录
- 检查网络连接

## 开发说明

### 添加新功能

1. 在 Python 后端 (`backend.py`) 中添加新的 API 端点
2. 在 `BackendClient` 中添加对应的请求方法
3. 在相应的标签页中调用新方法

### 修改 UI 样式

编辑各个标签页的 `setupUI()` 方法，使用 Qt 的样式表进行美化

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
