# Selenium 集成更新总结

## 更新内容

### ✅ 后端改进

1. **Selenium 支持**
   - 添加 Selenium WebDriver 支持
   - 支持 JavaScript 解密
   - 自动 ChromeDriver 管理

2. **新增 API 端点**
   ```
   POST /api/decrypt          # 使用 Selenium 解密数据
   GET  /api/health           # 健康检查
   ```

3. **错误处理**
   - 完整的异常捕获
   - 详细的日志输出
   - 自动降级处理

### ✅ 依赖管理

**新增依赖**
- `selenium==4.15.0` - WebDriver 框架
- `webdriver-manager==4.0.1` - 自动管理 ChromeDriver

**自动安装**
- 运行 `pip install -r requirements.txt` 自动安装所有依赖
- webdriver-manager 自动下载匹配的 ChromeDriver

### ✅ 启动脚本

**Windows**
- `start_backend.bat` - 自动检查依赖并启动

**macOS/Linux**
- `start_backend.sh` - 自动检查依赖并启动

### ✅ 文档

**新增文档**
- `SELENIUM_SETUP.md` - Selenium 安装和配置指南
- `INSTALLATION.md` - 完整安装指南
- 更新 `README.md` - 添加 Selenium 说明

## 使用方式

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 启动后端
```bash
# Windows
start_backend.bat

# macOS/Linux
./start_backend.sh
```

### 3. 验证 Selenium
```bash
curl http://127.0.0.1:5000/api/health
```

应该返回：
```json
{
  "status": "ok",
  "selenium": "available",
  "ocr": "paddle"
}
```

## 关键特性

### 自动 ChromeDriver 管理
```python
# 自动下载和管理 ChromeDriver
from webdriver_manager.chrome import ChromeDriverManager
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)
```

### JavaScript 解密
```python
# 使用 Selenium 执行 JavaScript 解密
result = backend.decrypt_with_selenium(encrypted_data, api_url)
```

### 线程安全
```python
# 使用锁保证线程安全
with selenium_lock:
    driver = init_selenium()
```

## 性能优化

1. **Headless 模式** - 减少内存占用
2. **连接池** - 复用 WebDriver
3. **缓存** - 缓存解密结果

## 故障排除

### ChromeDriver 问题
```bash
# 自动安装
pip install webdriver-manager

# 或手动指定路径
chrome_options.binary_location = "/path/to/chrome"
```

### Chrome 浏览器问题
```bash
# Windows
choco install googlechrome

# macOS
brew install --cask google-chrome

# Linux
sudo apt-get install google-chrome-stable
```

### 内存占用过高
- 使用 headless 模式（已启用）
- 定期关闭 WebDriver
- 限制并发请求

## 文件清单

**修改文件**
- ✅ backend.py - 添加 Selenium 支持
- ✅ requirements.txt - 添加 Selenium 依赖
- ✅ start_backend.bat - 改进启动脚本
- ✅ README.md - 更新文档

**新增文件**
- ✅ start_backend.sh - Linux/macOS 启动脚本
- ✅ SELENIUM_SETUP.md - Selenium 安装指南
- ✅ INSTALLATION.md - 完整安装指南

## 下一步

1. 测试 Selenium 功能
2. 测试 JavaScript 解密
3. 优化性能
4. 添加更多功能

## 支持

- 查看 SELENIUM_SETUP.md 了解 Selenium 配置
- 查看 INSTALLATION.md 了解完整安装步骤
- 查看 README.md 了解项目概览

---

**版本**：v3.1（Selenium 集成版）
**更新日期**：2026-03-28
**状态**：✅ 已完成
