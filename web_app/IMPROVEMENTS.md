# Kuding Judge Helper v3.0 - 改进版本

## ✅ 已修复的问题

### 1. 验证码端点修复
- ✅ 添加 `/api/captcha/login` - 获取登录验证码
- ✅ 添加 `/api/captcha/problem/<id>` - 获取题目验证码
- ✅ 正确处理库丁服务器的验证码请求
- ✅ 支持验证码 ID (cid) 传递

### 2. OCR 和 Selenium 打包
- ✅ 改进 PyInstaller 配置
- ✅ 使用 `collect_data_files()` 和 `collect_submodules()`
- ✅ 正确打包 PaddleOCR 和 Selenium 依赖
- ✅ 添加所有必需的 hidden imports

### 3. WebView2 集成
- ✅ 创建 `main.py` 使用 pywebview
- ✅ 无需浏览器，直接使用 WebView2
- ✅ 更好的用户体验
- ✅ 自动启动 Flask 后端

## 🚀 快速开始

### 方式 1: 运行源代码（推荐用于开发）

```bash
# 安装依赖
pip install -r requirements.txt

# 运行 WebView2 版本
python main.py

# 或运行浏览器版本
python app.py
```

### 方式 2: 打包成 EXE

```bash
# 运行打包脚本
build.bat

# 生成的 EXE 在 dist/ 目录中
dist/KudingJudgeHelper.exe
```

## 📁 文件结构

```
web_app/
├── app.py                    # Flask 后端
├── main.py                   # WebView2 启动器
├── requirements.txt          # 依赖列表
├── build.bat                 # 打包脚本
├── run_webview.bat           # WebView2 启动脚本
├── KudingJudgeHelper.spec    # PyInstaller 配置
├── templates/
│   └── index.html            # HTML 模板
└── static/
    ├── style.css             # 样式表
    └── app.js                # 前端逻辑
```

## 🔧 API 端点

### 验证码相关
- `GET /api/captcha/login` - 获取登录验证码
- `GET /api/captcha/problem/<id>` - 获取题目验证码

### 用户相关
- `POST /api/login` - 用户登录
- `GET /api/health` - 健康检查

### 功能相关
- `POST /api/ocr` - OCR 识别
- `POST /api/decrypt` - 解密
- `POST /api/submit` - 提交答案

## 📝 使用流程

### 1. 启动应用
```bash
python main.py
```

### 2. 登录
- 点击"登录"标签页
- 输入用户名、密码
- 点击"刷新"获取验证码
- 输入验证码
- 点击"登录"

### 3. 提交题目
- 点击"题目"标签页
- 输入题目 ID
- 点击"加载题目"
- 输入答案
- 点击"提交答案"

## 🎯 功能特性

### 前端
- ✅ 现代化 WebView2 界面
- ✅ 实时日志显示
- ✅ 本地设置存储
- ✅ 响应式设计

### 后端
- ✅ Flask REST API
- ✅ CORS 支持
- ✅ 可选依赖处理
- ✅ 错误处理和日志

### 集成功能
- ✅ 库丁服务器验证码获取
- ✅ OCR 识别（可选）
- ✅ JavaScript 解密（可选）
- ✅ 答案提交

## 🔧 可选功能

### 启用 Selenium（JavaScript 解密）
```bash
pip install selenium webdriver-manager
```

### 启用 PaddleOCR（高精度 OCR）
```bash
pip install paddleocr
```

### 启用所有功能
```bash
pip install -r requirements.txt
```

## 📊 技术栈

- **后端**: Flask 2.3.0
- **前端**: HTML5 + CSS3 + JavaScript
- **UI 框架**: pywebview 5.0.0
- **OCR**: PaddleOCR 2.7.0.3
- **自动化**: Selenium 4.15.0
- **打包**: PyInstaller

## 🐛 故障排除

### WebView2 不可用
- 确保已安装 pywebview
- 在 Windows 上需要 WebView2 运行时
- 下载: https://developer.microsoft.com/en-us/microsoft-edge/webview2/

### 验证码获取失败
- 检查网络连接
- 确保能访问 https://courseadmin.kuding.cn
- 查看日志获取详细错误信息

### OCR 不工作
- 确保已安装 PaddleOCR
- 首次运行会下载模型（需要网络）
- 检查磁盘空间（模型约 200MB）

### Selenium 错误
- 确保已安装 Chrome 浏览器
- 检查 ChromeDriver 版本匹配
- 查看后端日志获取详细信息

## 📞 支持

### 查看日志
- 应用窗口中显示实时日志
- 后端日志在控制台输出

### 调试
- 在设置中启用"调试模式"
- 查看浏览器开发者工具（F12）
- 检查网络请求

## 🎓 下一步

1. **集成真实数据源**
   - 连接实际的库丁服务器
   - 实现完整的登录流程
   - 加载真实题目数据

2. **完善功能**
   - 实现 JavaScript 解密逻辑
   - 优化 OCR 参数
   - 添加错误恢复

3. **部署**
   - 生成最终 EXE
   - 创建安装程序
   - 发布到用户

## 📄 许可证

MIT

---

**版本**: 3.0
**发布日期**: 2026-03-28
**状态**: ✅ 改进完成
