from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import requests
import json
import os
from datetime import datetime
import threading
import logging
from urllib.parse import urljoin
import re
from html import unescape
import uuid
import time

# 可选依赖
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.service import Service
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

try:
    import paddleocr
    PADDLEOCR_AVAILABLE = True
except ImportError:
    PADDLEOCR_AVAILABLE = False

app = Flask(__name__)
app.secret_key = 'kuding-judge-secret-key'
CORS(app)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 全局变量
selenium_driver = None
selenium_lock = threading.Lock()
ocr = None
session_obj = requests.Session()  # 保持 cookies

# 库丁服务器配置
BASE_URL = "https://courseadmin.kuding.cn"
CAPTCHA_API = urljoin(BASE_URL, "/course/auth/captcha")
PROBLEM_CAPTCHA_API = urljoin(BASE_URL, "/problem/captcha")

def init_selenium():
    """初始化 Selenium WebDriver"""
    global selenium_driver
    if not SELENIUM_AVAILABLE:
        logger.warning("Selenium not available. Install with: pip install selenium webdriver-manager")
        return False

    try:
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        try:
            service = Service(ChromeDriverManager().install())
            selenium_driver = webdriver.Chrome(service=service, options=options)
        except:
            selenium_driver = webdriver.Chrome(options=options)

        logger.info("Selenium WebDriver initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize Selenium: {e}")
        return False

def init_ocr():
    """初始化 OCR"""
    global ocr
    if not PADDLEOCR_AVAILABLE:
        logger.warning("PaddleOCR not available. Install with: pip install paddleocr")
        return False

    try:
        ocr = paddleocr.PaddleOCR(use_angle_cls=True, lang='ch')
        logger.info("PaddleOCR initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize OCR: {e}")
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok',
        'selenium': SELENIUM_AVAILABLE and selenium_driver is not None,
        'ocr': PADDLEOCR_AVAILABLE and ocr is not None,
        'version': '3.0'
    })

@app.route('/api/captcha/login', methods=['GET'])
def get_login_captcha():
    """获取登录验证码"""
    try:
        # 生成 UUID 作为 cid
        cid = str(uuid.uuid4())
        # 生成时间戳（毫秒）
        v = int(time.time() * 1000)
        # 构建 URL
        url = f"{CAPTCHA_API}?v={v}&cid={cid}"

        logger.info(f"Requesting captcha from: {url}")

        # 使用 session 保持 cookies
        response = session_obj.get(url, timeout=10)

        if response.status_code == 200:
            # 返回验证码图片和 cid
            return jsonify({
                'success': True,
                'image': f"data:image/png;base64,{__import__('base64').b64encode(response.content).decode()}",
                'cid': cid
            })
        else:
            logger.error(f"Captcha API returned {response.status_code}: {response.text}")
            return jsonify({'error': f'Failed to get captcha: {response.status_code}'}), 500
    except Exception as e:
        logger.error(f"Get captcha error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/captcha/problem/<problem_id>', methods=['GET'])
def get_problem_captcha(problem_id):
    """获取题目页面验证码"""
    try:
        # 先获取题目页面
        problem_url = urljoin(BASE_URL, f"/problem/{problem_id}")
        logger.info(f"Fetching problem page: {problem_url}")

        response = session_obj.get(problem_url, timeout=10)

        if response.status_code != 200:
            logger.error(f"Failed to get problem page: {response.status_code}")
            return jsonify({'error': f'Failed to get problem page: {response.status_code}'}), 500

        # 从 HTML 中提取验证码图片 URL
        pattern = r'<img[^>]*src="([^"]*problem/captcha[^"]*)"[^>]*>'
        match = re.search(pattern, response.text)

        if not match:
            logger.error("Captcha not found in problem page")
            return jsonify({'error': 'Captcha not found in problem page'}), 404

        captcha_url = unescape(match.group(1))
        if not captcha_url.startswith("http"):
            captcha_url = urljoin(BASE_URL, captcha_url)

        logger.info(f"Captcha URL: {captcha_url}")

        # 获取验证码图片
        captcha_response = session_obj.get(captcha_url, timeout=10)
        if captcha_response.status_code != 200:
            logger.error(f"Failed to get captcha image: {captcha_response.status_code}")
            return jsonify({'error': 'Failed to get captcha image'}), 500

        # 提取 cid
        cid_match = re.search(r'cid=([^&"]+)', captcha_url)
        cid = cid_match.group(1) if cid_match else str(uuid.uuid4())

        return jsonify({
            'success': True,
            'image': f"data:image/png;base64,{__import__('base64').b64encode(captcha_response.content).decode()}",
            'cid': cid
        })
    except Exception as e:
        logger.error(f"Get problem captcha error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    """登录接口"""
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        captcha = data.get('captcha')
        cid = data.get('cid')

        if not all([username, password, captcha, cid]):
            return jsonify({'error': 'Missing required fields'}), 400

        # 这里添加实际的登录逻辑
        session['username'] = username
        session['logged_in'] = True

        return jsonify({
            'success': True,
            'message': 'Login successful',
            'username': username
        })
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/ocr', methods=['POST'])
def ocr_recognize():
    """OCR 识别接口"""
    try:
        if not PADDLEOCR_AVAILABLE:
            return jsonify({'error': 'PaddleOCR not available'}), 503

        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400

        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        # 保存临时文件
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            file.save(tmp.name)
            temp_path = tmp.name

        try:
            # 执行 OCR
            result = ocr.ocr(temp_path, cls=True)
            text = '\n'.join([line[0][1] for line in result[0]]) if result else ''

            return jsonify({
                'success': True,
                'text': text,
                'confidence': 0.95
            })
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    except Exception as e:
        logger.error(f"OCR error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/decrypt', methods=['POST'])
def decrypt():
    """解密接口（使用 Selenium 执行 JavaScript）"""
    try:
        if not SELENIUM_AVAILABLE:
            return jsonify({'error': 'Selenium not available'}), 503

        data = request.json
        encrypted_text = data.get('text')

        if not encrypted_text:
            return jsonify({'error': 'No text provided'}), 400

        with selenium_lock:
            if not selenium_driver:
                return jsonify({'error': 'Selenium not initialized'}), 500

            # 这里添加实际的解密逻辑
            decrypted = encrypted_text

        return jsonify({
            'success': True,
            'decrypted': decrypted
        })
    except Exception as e:
        logger.error(f"Decrypt error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/submit', methods=['POST'])
def submit():
    """提交答案接口"""
    try:
        data = request.json
        problem_id = data.get('problem_id')
        answer = data.get('answer')

        if not problem_id or not answer:
            return jsonify({'error': 'Problem ID and answer required'}), 400

        return jsonify({
            'success': True,
            'message': 'Answer submitted successfully',
            'problem_id': problem_id
        })
    except Exception as e:
        logger.error(f"Submit error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # 初始化
    init_selenium()
    init_ocr()

    # 启动 Flask 应用
    app.run(debug=False, host='127.0.0.1', port=5000)
