# 完整安装指南

## 系统要求

- Python 3.7+
- Google Chrome 浏览器
- 2GB RAM
- 500MB 磁盘空间

## 第一步：安装 Python

### Windows
1. 下载 Python：https://www.python.org/downloads/
2. 运行安装程序
3. **重要**：勾选 "Add Python to PATH"
4. 点击 "Install Now"

### macOS
```bash
# 使用 Homebrew
brew install python3
```

### Linux
```bash
# Ubuntu/Debian
sudo apt-get install python3 python3-pip

# Fedora
sudo dnf install python3 python3-pip
```

## 第二步：安装 Google Chrome

### Windows
1. 下载：https://www.google.com/chrome/
2. 运行安装程序
3. 完成安装

### macOS
```bash
brew install --cask google-chrome
```

### Linux
```bash
# Ubuntu/Debian
sudo apt-get install google-chrome-stable

# Fedora
sudo dnf install google-chrome-stable
```

## 第三步：安装项目依赖

### Windows
```bash
# 进入项目目录
cd qt

# 安装依赖
pip install -r requirements.txt
```

### macOS/Linux
```bash
# 进入项目目录
cd qt

# 安装依赖
pip3 install -r requirements.txt
```

## 第四步：验证安装

### 验证 Python
```bash
python --version
# 或
python3 --version
```

### 验证 Selenium
```bash
python -c "from selenium import webdriver; print('OK')"
# 或
python3 -c "from selenium import webdriver; print('OK')"
```

### 验证 Chrome
```bash
# Windows
where chrome

# macOS/Linux
which google-chrome
```

## 第五步：启动后端

### Windows
双击 `start_backend.bat` 或运行：
```bash
python backend.py
```

### macOS/Linux
```bash
chmod +x start_backend.sh
./start_backend.sh
```

或直接运行：
```bash
python3 backend.py
```

## 验证后端

在浏览器中访问：
```
http://127.0.0.1:5000/api/health
```

应该看到：
```json
{
  "status": "ok",
  "selenium": "available",
  "ocr": "paddle"
}
```

## 常见问题

### Q: "python: command not found"
A:
- Windows：重新安装 Python，勾选 "Add Python to PATH"
- macOS/Linux：使用 `python3` 代替 `python`

### Q: "ModuleNotFoundError: No module named 'selenium'"
A:
```bash
pip install selenium webdriver-manager
```

### Q: "ChromeDriver not found"
A:
```bash
pip install webdriver-manager
```

### Q: "Chrome not found"
A:
- 确保已安装 Google Chrome
- 检查 Chrome 是否在 PATH 中

### Q: "Permission denied" (macOS/Linux)
A:
```bash
chmod +x start_backend.sh
```

### Q: 端口 5000 已被占用
A:
编辑 backend.py，修改最后一行：
```python
app.run(host='127.0.0.1', port=5001, debug=False, threaded=True)
```

## 高级配置

### 使用代理
编辑 backend.py：
```python
proxies = {
    'http': 'http://proxy.example.com:8080',
    'https': 'http://proxy.example.com:8080',
}
resp = self.session.get(url, proxies=proxies)
```

### 自定义 Chrome 路径
编辑 backend.py：
```python
chrome_options.binary_location = "/path/to/chrome"
```

### 增加超时时间
编辑 backend.py：
```python
resp = self.session.get(url, timeout=30)  # 30 秒
```

## 性能优化

### 1. 使用 SSD
将项目放在 SSD 上可以加快启动速度。

### 2. 增加内存
如果内存不足，可能导致 Selenium 崩溃。

### 3. 关闭不必要的浏览器扩展
编辑 backend.py：
```python
chrome_options.add_argument("--disable-extensions")
```

## 卸载

### Windows
```bash
pip uninstall -r requirements.txt
```

### macOS/Linux
```bash
pip3 uninstall -r requirements.txt
```

## 获取帮助

- 查看日志：后端启动时会输出详细日志
- 检查网络：确保能访问 https://courseadmin.kuding.cn
- 查看文档：README.md, SELENIUM_SETUP.md

## 下一步

1. 编译 Qt 前端
2. 运行应用
3. 登录并测试

详见 BUILD_INSTRUCTIONS.md
