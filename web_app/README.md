# Kuding Judge Helper v3.0 - Web 版本

现代化的 Web 应用，用于辅助库丁判官系统。

## 功能特性

- ✨ 美观的 Web UI（响应式设计）
- 🔐 用户登录和验证码识别
- 📝 题目和测试管理
- 🤖 高精度 OCR（PaddleOCR 99% 准确率）
- 🔓 JavaScript 解密支持（Selenium）
- ⚙️ 灵活的设置面板
- 📊 实时日志显示

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动应用

**Windows:**
```bash
run.bat
```

**macOS/Linux:**
```bash
bash run.sh
```

### 3. 打开浏览器

访问 `http://localhost:5000`

## 项目结构

```
web_app/
├── app.py                 # Flask 后端
├── requirements.txt       # Python 依赖
├── run.bat               # Windows 启动脚本
├── run.sh                # Linux/macOS 启动脚本
├── templates/
│   └── index.html        # HTML 模板
└── static/
    ├── style.css         # 样式表
    └── app.js            # 前端逻辑
```

## API 端点

- `GET /` - 主页
- `GET /api/health` - 健康检查
- `POST /api/login` - 用户登录
- `POST /api/ocr` - OCR 识别
- `POST /api/decrypt` - 解密
- `POST /api/submit` - 提交答案

## 配置

在设置标签页中可以配置：
- API 地址
- OCR 引擎（PaddleOCR/EasyOCR/Tesseract）
- 调试模式
- 语言（中文/English）

## 技术栈

- **后端**: Flask + Python
- **前端**: HTML5 + CSS3 + JavaScript
- **OCR**: PaddleOCR
- **自动化**: Selenium + webdriver-manager
- **浏览器兼容**: Chrome/Firefox/Safari/Edge

## 系统要求

- Python 3.7+
- Chrome/Chromium（用于 Selenium）
- 4GB+ RAM（用于 PaddleOCR）

## 故障排除

### 连接失败
- 确保后端正在运行
- 检查 API 地址设置
- 查看浏览器控制台错误

### OCR 不工作
- 确保已安装 PaddleOCR
- 检查图片格式（支持 PNG/JPG）
- 查看后端日志

### Selenium 错误
- 确保已安装 Chrome
- 检查 ChromeDriver 版本
- 查看后端日志

## 许可证

MIT
