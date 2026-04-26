# 快速启动指南

## 方式 1: 直接运行（推荐）

### Windows
```bash
cd "c:\Users\陈炳灼\Desktop\杂物\api test\web_app"
python app.py
```

### macOS/Linux
```bash
cd ~/Desktop/杂物/api\ test/web_app
python app.py
```

然后打开浏览器访问: **http://localhost:5000**

## 方式 2: 使用启动脚本

### Windows
双击 `run.bat` 文件

### macOS/Linux
```bash
bash run.sh
```

## 首次使用

1. **安装依赖**（如果还没安装）
   ```bash
   pip install -r requirements.txt
   ```

2. **启动应用**
   ```bash
   python app.py
   ```

3. **打开浏览器**
   访问 http://localhost:5000

4. **使用应用**
   - 在"登录"标签页输入用户名和密码
   - 在"题目"标签页加载和提交题目
   - 在"测试"标签页进行测试
   - 在"设置"标签页配置选项

## 常见问题

### 端口被占用
如果 5000 端口被占用，修改 `app.py` 中的端口号：
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # 改为 5001
```

### 依赖安装失败
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 无法连接到后端
- 确保应用正在运行
- 检查防火墙设置
- 在设置中验证 API 地址

## 功能说明

### 登录
- 输入用户名、密码和验证码
- 点击"登录"按钮

### 题目管理
- 输入题目 ID 加载题目
- 在代码区域查看题目内容
- 在答案区域输入答案
- 点击"提交答案"提交

### 测试
- 类似题目管理流程
- 用于测试代码

### 设置
- 配置 API 地址
- 选择 OCR 引擎
- 启用调试模式
- 选择语言

### 日志
- 实时显示应用日志
- 帮助调试问题

## 下一步

- 配置实际的登录服务器地址
- 集成真实的题目数据源
- 自定义 OCR 和解密逻辑
- 部署到生产环境

## 支持

如有问题，请查看浏览器控制台（F12）和后端日志。
