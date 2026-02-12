> 酷丁编程的人做梦也不会想到，有人会使用OCR识别他们的登录验证码......


# AutoCBZ 酷丁自动化
一个用于酷丁评测系统的自动化工具，支持自动登录、验证码识别、代码提交和结果查询。
## ✨ 功能特性
- 🔐 **自动登录**：支持用户名密码登录，自动处理验证码
- 🖼️ **GUI 验证码显示**：验证码图片直接在 GUI 窗口中显示，无需手动打开文件
- 🔍 **OCR 自动识别（实验性功能）**：可能支持验证码自动识别（需安装 Tesseract）
- 💾 **Token 自动管理**：登录成功后自动保存 Token 和 Cookie，无需重复登录
- 🚀 **代码自动提交**：支持多种编程语言（C++、C、Python、Java）
- 📊 **结果轮询**：自动轮询评测结果，直到完成
- 📝 **灵活输入**：支持字符串输入或从文件读取输入
- 🔄 **验证码刷新**：GUI 中可一键刷新验证码

### 注意：我只测试了部分功能，不保证一定可以正常运行！

## 📋 环境要求（Python版本，exe版本不用）
- Python 3.7+
- 依赖库：
  - `requests` - HTTP 请求
  - `beautifulsoup4` - HTML 解析（可选）
  - `pillow` - 图像处理和 GUI 显示
  - `pytesseract` - OCR 识别（可选）
## 📦 安装 （Python版本，exe版本不用）
### 1. 安装 Python 依赖
```bash
# 基础依赖
pip install requests pillow
# 可选：用于 OCR 自动识别验证码
pip install pytesseract
```
### 2. 安装 Tesseract（OCR 模式需要）
**Windows:**
1. 下载安装包：https://github.com/UB-Mannheim/tesseract/wiki
2. 安装后添加到系统 PATH

**Linux:**
```bash
sudo apt-get install tesseract-ocr
```
**macOS:**
```bash
brew install tesseract
```
## 🚀 快速开始
### 1. 首次使用 - 登录
```bash
# 方式 1：GUI 手动输入验证码（推荐）
python AutoKuding.exe --login -u "你的用户名" -p "你的密码" -vcm hm
# 方式 2：OCR 自动识别验证码
python AutoKuding.exe --login -u "你的用户名" -p "你的密码" -vcm ocr
```
登录成功后，Token 和 Cookie 会自动保存到：
- `kd_token.txt` - Access Token
- `kd_cookies.txt` - Cookie 文件
### 2. 提交代码
```bash
# 默认提交 test.cpp，输入为 "test"
python AutoKuding.exe
# 提交 Python 代码，输入来自文件
python AutoKuding.exe -l py -i data.in
# 指定代码文件和输入字符串
python AutoKuding.exe solution.py -l cpp -i "1 2 3"
# 从文件读取输入
python AutoKuding.exe -c code.cpp -l cpp -i input.txt
# 只提交不轮询结果
python AutoKuding.exe --no-poll
```
## 📖 详细使用说明
### 登录模式
```bash
python AutoKuding.exe --login -u <用户名> -p <密码> [-vcm <验证码模式>]
```
**参数说明：**
- `--login`：启用登录模式
- `-u, --username`：用户名
- `-p, --password`：密码
- `-vcm, --vercode-mode`：验证码模式
  - `hm`：手动输入（GUI 窗口显示验证码）
  - `ocr`：自动 OCR 识别
**登录流程：**
1. 自动生成 CID 并请求验证码
2. 验证码保存为 `captcha_temp.png`
3. 显示 GUI 窗口（或使用 OCR 自动识别）
4. 用户输入验证码后提交登录
5. 登录成功后自动保存 Token 和 Cookie
### 提交代码模式
```bash
python AutoKuding.exe [代码文件] [-l <语言>] [-i <输入>] [其他选项]
```
**参数说明：**
| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| `code_file` | - | 代码文件路径（位置参数） | 根据语言自动选择 |
| `-l, --lang` | - | 编程语言 | cpp |
| `-i, --input` | - | 输入数据（字符串或文件路径） | "test" |
| `-c, --code` | - | 指定代码文件 | - |
| `--no-poll` | - | 只提交不轮询结果 | False |
| `--interval` | - | 轮询间隔（秒） | 1.0 |
| `--max-poll` | - | 最大轮询次数 | 30 |
| `--token-file` | - | Token 文件路径 | kd_token.txt |
**支持的语言：**
- `cpp` / `c++`：C++（默认文件：`test.cpp`）
- `c`：C（默认文件：`test.c`）
- `py` / `python`：Python（默认文件：`test.py`）
- `java`：Java（默认文件：`Main.java`）
## 🎯 使用示例
### 示例 1：首次登录
```bash
python AutoKuding.exe --login -u "student123" -p "password123" -vcm hm
```
执行后会弹出 GUI 窗口：
```
┌─────────────────────────────────────┐
│     请输入验证码                     │
├─────────────────────────────────────┤
│  ┌─────────────────────────────┐   │
│  │   [验证码图片显示区域]        │   │
│  │     4 7 X 2                 │   │
│  └─────────────────────────────┘   │
│                                     │
│  验证码: [输入框___________]        │
│                                     │
│  [提交] [刷新验证码] [取消]         │
└─────────────────────────────────────┘
```
### 示例 2：提交 C++ 代码
```bash
# 假设你有一个 solution.cpp 和 input.txt
python AutoKuding.exe solution.cpp -l cpp -i input.txt
```
输出：
```
✅ 已加载 Token: 4WT9Uis1L5lCN6BswVC9...
📄 读取代码文件: solution.cpp
   代码长度: 523 字符
📁 检测到文件输入: input.txt
   文件大小: 45 字符
============================================================
🚀 提交代码到评测系统
============================================================
  语言: cpp
  代码长度: 523 字符
  输入长度: 45 字符
============================================================
状态码: 200
响应: {"code":0,"msg":"","data":13785747,"t":false}
✅ 提交成功！评测 ID: 13785747
⏳ [轮询 1/30] 查询评测结果...
   📊 状态: 评测中...
⏳ [轮询 2/30] 查询评测结果...
============================================================
🎯 评测完成！
============================================================
  结果: Accepted
📤 输出:
It is the test result.
============================================================
```
### 示例 3：提交 Python 代码
```bash
python AutoKuding.exe -l py -i "5\n1 2 3 4 5"
```
### 示例 4：使用 OCR 自动识别验证码登录
```bash
python AutoKuding.exe --login -u "user" -p "pass" -vcm ocr
```
OCR 识别后会自动填入，但仍会显示 GUI 供你确认或修改。
## ⚙️ 配置文件
### Token 文件 (kd_token.txt)
存储 Access Token，格式：
```
4WT9Uis1L5lCN6BswVC9nsxPc0S83uWcg13N69FL3Sg282RDvdPs9xn54weQLRCg
```
### Cookie 文件 (kd_cookies.txt)
存储 Session Cookie，由 `requests` 自动管理。
### 验证码文件 (captcha_temp.png)
临时存储验证码图片，登录后可删除。
## ❓ 常见问题
### Q1: 登录失败，提示"验证码错误"
**A:** 验证码可能过期或识别错误。解决方案：
1. 使用 `-vcm hm` 模式手动输入
2. 在 GUI 中点击"刷新验证码"按钮
3. 确保网络连接正常
### Q2: 提示"GUI 不可用"
**A:** 需要安装 tkinter 和 pillow：
```bash
pip install pillow
```
Windows 通常自带 tkinter，Linux 可能需要：
```bash
sudo apt-get install python3-tk
```
### Q3: OCR 识别不准确
**A:** OCR 识别依赖验证码清晰度。建议：
1. 使用 `-vcm hm` 手动输入
2. 或在 GUI 中修改 OCR 识别结果
3. 调整 Tesseract 配置或使用第三方打码服务
### Q4: Token 过期怎么办？
**A:** 重新执行登录命令：
```bash
python AutoKuding.exe --login -u "用户名" -p "密码"
```
### Q5: 如何查看已保存的 Token？
**A:** Token 保存在 `kd_token.txt` 文件中，可直接查看：
```bash
cat kd_token.txt  # Linux/Mac
type kd_token.txt  # Windows
```
## 🔧 高级用法
### 自定义 Token 文件路径
```bash
python AutoKuding.exe --token-file /path/to/token.txt
```
### 调整轮询参数
```bash
# 每 0.5 秒查询一次，最多查询 50 次
python AutoKuding.exe --interval 0.5 --max-poll 50
```
### 只提交不轮询
```bash
python AutoKuding.exe --no-poll
# 后续手动查询
# 访问：https://courseadmin.kuding.cn/problem/judge/test/result?id=<评测ID>
```
## 📝 代码文件示例
### test.cpp
```cpp
#include <iostream>
using namespace std;
int main() {
    int n;
    cin >> n;
    cout << "Hello, n = " << n << endl;
    return 0;
}
```
### test.py
```python
n = int(input())
print(f"Hello, n = {n}")
```
## ⚠️ 注意事项
1. **安全性**：
   - 不要将 `kd_token.txt` 和 `kd_cookies.txt` 上传
2. **验证码有效期**：
   - 验证码通常有时效性，建议在 GUI 中尽快输入
   - 如果过期，点击"刷新验证码"重新获取
3. **网络连接**：
   - 确保能访问 `courseadmin.kuding.cn` 和 `ke.kuding.cn`
   - 如遇网络错误，检查代理设置
4. **Token 有效期**：
   - Token 可能会在一段时间后过期
   - 过期后重新登录即可
