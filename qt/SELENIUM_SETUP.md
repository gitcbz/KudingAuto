# Selenium 安装和配置指南

## 快速安装

### 1. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

### 2. 安装 ChromeDriver

Selenium 需要 ChromeDriver 来控制 Chrome 浏览器。

#### Windows

**方法 1：自动安装（推荐）**
```bash
pip install webdriver-manager
```

然后在 backend.py 中修改：
```python
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

service = Service(ChromeDriverManager().install())
selenium_driver = webdriver.Chrome(service=service, options=chrome_options)
```

**方法 2：手动安装**
1. 下载 ChromeDriver：https://chromedriver.chromium.org/
2. 选择与你的 Chrome 版本匹配的版本
3. 解压到 `C:\chromedriver.exe`
4. 添加到 PATH 环境变量

#### macOS

```bash
# 使用 Homebrew
brew install chromedriver

# 或使用 webdriver-manager
pip install webdriver-manager
```

#### Linux

```bash
# Ubuntu/Debian
sudo apt-get install chromium-chromedriver

# 或使用 webdriver-manager
pip install webdriver-manager
```

## 验证安装

运行以下命令验证 Selenium 是否正确安装：

```bash
python -c "from selenium import webdriver; print('Selenium OK')"
```

## 后端启动

### Windows

```bash
# 方法 1：双击脚本
start_backend.bat

# 方法 2：命令行
python backend.py
```

### macOS/Linux

```bash
python backend.py
```

## 常见问题

### Q: ChromeDriver 找不到
A:
1. 确保 ChromeDriver 在 PATH 中
2. 或使用 webdriver-manager 自动管理
3. 检查 Chrome 版本是否匹配

### Q: Chrome 浏览器找不到
A:
1. 确保已安装 Google Chrome
2. 在 chrome_options 中指定路径：
```python
chrome_options.binary_location = "/path/to/chrome"
```

### Q: Selenium 超时
A:
1. 增加等待时间
2. 检查网络连接
3. 检查解密服务是否可用

### Q: 内存占用过高
A:
1. 定期关闭 WebDriver
2. 使用 headless 模式（已启用）
3. 限制并发请求

## 性能优化

### 1. 使用 Headless 模式
已在 backend.py 中启用，可以减少内存占用。

### 2. 连接池
```python
# 在 KuDingBackend.__init__ 中
self.driver_pool = []
```

### 3. 缓存解密结果
```python
# 添加缓存
self.decrypt_cache = {}
```

## 调试

### 启用详细日志
```bash
export FLASK_ENV=development
python backend.py
```

### 查看 Selenium 日志
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 部署

### Docker 部署

创建 Dockerfile：
```dockerfile
FROM python:3.9

RUN apt-get update && apt-get install -y chromium-browser chromium-chromedriver

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY backend.py .

CMD ["python", "backend.py"]
```

构建和运行：
```bash
docker build -t kuding-backend .
docker run -p 5000:5000 kuding-backend
```

## 支持

如有问题，请检查：
- Chrome 版本
- ChromeDriver 版本
- Python 版本
- 网络连接
