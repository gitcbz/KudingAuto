#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kuding Judge Backend Server
提供 REST API 供 Qt 前端调用
支持 Selenium 处理 JavaScript 解密
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import time
import requests
import os
import uuid
from pathlib import Path
from http.cookiejar import LWPCookieJar
from urllib.parse import urljoin
from io import BytesIO
from typing import Optional, Dict, Tuple
import re
from html import unescape as html_unescape
import threading
import logging
import base64

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 尝试导入 PIL
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logger.warning("PIL not installed")

# 尝试导入 Selenium - 必须可用
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service

    # 尝试导入 webdriver-manager 自动管理 ChromeDriver
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        WEBDRIVER_MANAGER_AVAILABLE = True
        logger.info("webdriver-manager available")
    except ImportError:
        WEBDRIVER_MANAGER_AVAILABLE = False
        logger.warning("webdriver-manager not available, will use system ChromeDriver")

    SELENIUM_AVAILABLE = True
    logger.info("Selenium available")
except ImportError as e:
    SELENIUM_AVAILABLE = False
    logger.error(f"Selenium not available: {e}")

# 尝试导入高精度 OCR
try:
    from paddleocr import PaddleOCR
    OCR_ENGINE = "paddle"
    ocr = PaddleOCR(use_angle_cls=True, lang='en')
    logger.info("Using PaddleOCR")
except ImportError:
    try:
        import easyocr
        OCR_ENGINE = "easyocr"
        reader = easyocr.Reader(['en'])
        logger.info("Using EasyOCR")
    except ImportError:
        try:
            import pytesseract
            OCR_ENGINE = "tesseract"
            logger.info("Using Tesseract OCR")
        except ImportError:
            OCR_ENGINE = None
            logger.warning("No OCR engine available")

# ========= 配置区域 =========
BASE_URL = "https://courseadmin.kuding.cn"
LOGIN_URL = urljoin(BASE_URL, "/course/auth/login_")
CAPTCHA_API = urljoin(BASE_URL, "/course/auth/captcha")
PROBLEM_CAPTCHA_API = urljoin(BASE_URL, "/problem/captcha")

JUDGE_TEST_URL = urljoin(BASE_URL, "/problem/judge/test")
JUDGE_PROBLEM_URL = urljoin(BASE_URL, "/problem/judge")
RESULT_TEST_URL = urljoin(BASE_URL, "/problem/judge/test/result")
RESULT_INFO_URL = urljoin(BASE_URL, "/problem/judge/resultInfo")

TOKEN_FILE = "kd_token.txt"
COOKIE_FILE = "kd_cookies.txt"
CAPTCHA_FILE = "captcha_temp.png"
PROBLEM_CAPTCHA_FILE = "problem_captcha_temp.png"

# ===========================

app = Flask(__name__)
CORS(app)

# 全局 Selenium WebDriver
selenium_driver = None
selenium_lock = threading.Lock()


def init_selenium():
    """初始化 Selenium WebDriver"""
    global selenium_driver

    if selenium_driver is not None:
        return selenium_driver

    if not SELENIUM_AVAILABLE:
        logger.error("Selenium not available")
        return None

    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

        # 使用 webdriver-manager 自动管理 ChromeDriver
        if WEBDRIVER_MANAGER_AVAILABLE:
            try:
                service = Service(ChromeDriverManager().install())
                selenium_driver = webdriver.Chrome(service=service, options=chrome_options)
                logger.info("Selenium WebDriver initialized with webdriver-manager")
                return selenium_driver
            except Exception as e:
                logger.warning(f"Failed to use webdriver-manager: {e}, trying system ChromeDriver")

        # 尝试使用系统 ChromeDriver
        try:
            selenium_driver = webdriver.Chrome(options=chrome_options)
            logger.info("Selenium WebDriver initialized with system ChromeDriver")
            return selenium_driver
        except Exception as e:
            logger.error(f"Failed to initialize with system ChromeDriver: {e}")
            return None

    except Exception as e:
        logger.error(f"Failed to initialize Selenium: {e}")
        return None


def close_selenium():
    """关闭 Selenium WebDriver"""
    global selenium_driver
    if selenium_driver:
        try:
            selenium_driver.quit()
            selenium_driver = None
            logger.info("Selenium WebDriver closed")
        except Exception as e:
            logger.error(f"Error closing Selenium: {e}")


class KuDingBackend:
    """后台逻辑处理类"""

    def __init__(self):
        self.session = self._build_session()
        self.token = None
        self.cid = None
        self.problem_cid = None
        self.image_code = None
        self.problem_image_code = None
        self.load_token()

    def _build_session(self) -> requests.Session:
        session = requests.Session()
        if os.path.exists(COOKIE_FILE):
            session.cookies = LWPCookieJar(COOKIE_FILE)
            try:
                session.cookies.load(ignore_discard=True, ignore_expires=True)
                logger.info("Cookies loaded")
            except Exception as e:
                logger.error(f"Cookie load failed: {e}")
        return session

    def save_token(self, token: str):
        self.token = token
        with open(TOKEN_FILE, "w", encoding="utf-8") as f:
            f.write(token)
        logger.info("Token saved")

    def load_token(self) -> Optional[str]:
        if not os.path.exists(TOKEN_FILE):
            return None
        with open(TOKEN_FILE, "r", encoding="utf-8") as f:
            self.token = f.read().strip()
            return self.token

    def save_cookies(self):
        if not isinstance(self.session.cookies, LWPCookieJar):
            self.session.cookies = LWPCookieJar(COOKIE_FILE)
        try:
            self.session.cookies.save(ignore_discard=True, ignore_expires=True)
            logger.info("Cookies saved")
        except Exception as e:
            logger.error(f"Cookie save failed: {e}")

    def _build_headers(self, with_content_type: bool = False, with_auth: bool = False) -> Dict[str, str]:
        headers = {
            "accept": "application/json, text/plain, */*",
            "origin": "https://ke.kuding.cn",
            "referer": "https://ke.kuding.cn/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        }
        if with_content_type:
            headers["content-type"] = "application/json"
        if with_auth and self.token:
            headers["authorization"] = f"Token {self.token}"
        return headers

    def fetch_captcha(self) -> Tuple[Optional[str], Optional[bytes]]:
        try:
            logger.info("Fetching login captcha...")
            self.cid = str(uuid.uuid4())
            v = int(time.time() * 1000)
            url = f"{CAPTCHA_API}?v={v}&cid={self.cid}"
            resp = self.session.get(url, timeout=10)
            resp.raise_for_status()
            image_data = resp.content
            with open(CAPTCHA_FILE, "wb") as f:
                f.write(image_data)
            logger.info(f"Captcha fetched (CID: {self.cid[:8]}...)")
            return self.cid, image_data
        except Exception as e:
            logger.error(f"Fetch captcha failed: {e}")
            return None, None

    def fetch_problem_captcha(self) -> Tuple[Optional[str], Optional[bytes]]:
        try:
            logger.info("Fetching problem captcha...")
            self.problem_cid = str(uuid.uuid4())
            v = int(time.time() * 1000)
            url = f"{PROBLEM_CAPTCHA_API}?v={v}&cid={self.problem_cid}"
            resp = self.session.get(url, timeout=10)
            resp.raise_for_status()
            image_data = resp.content
            with open(PROBLEM_CAPTCHA_FILE, "wb") as f:
                f.write(image_data)
            logger.info(f"Problem captcha fetched (CID: {self.problem_cid[:8]}...)")
            return self.problem_cid, image_data
        except Exception as e:
            logger.error(f"Fetch problem captcha failed: {e}")
            return None, None

    def ocr_captcha(self, image_data: bytes, ocr_mode: str = "normal") -> str:
        """
        OCR 识别验证码
        ocr_mode: "normal" 或 "enhanced"
        """
        if not OCR_ENGINE:
            return ""

        try:
            image = Image.open(BytesIO(image_data))

            if OCR_ENGINE == "paddle":
                result = ocr.ocr(image, cls=True)
                text = "".join([line[0][1] for line in result[0]]) if result else ""
            elif OCR_ENGINE == "easyocr":
                result = reader.readtext(image)
                text = "".join([item[1] for item in result])
            else:  # tesseract
                import pytesseract
                image = image.convert('L')
                text = pytesseract.image_to_string(image, config='--psm 7')

            text = text.strip()

            # 增强模式：只保留字母和数字
            if ocr_mode == "enhanced":
                text = re.sub(r'[^A-Za-z0-9]', '', text)

            logger.info(f"OCR result: {text}")
            return text
        except Exception as e:
            logger.error(f"OCR error: {e}")
            return ""

    def decrypt_with_selenium(self, encrypted_data: str, api_url: str = "https://kddecode.api.cbzstudio.qzz.io") -> Optional[str]:
        """
        使用 Selenium 执行 JavaScript 解密
        """
        if not SELENIUM_AVAILABLE:
            logger.error("Selenium not available for decryption")
            return None

        with selenium_lock:
            try:
                driver = init_selenium()
                if not driver:
                    return None

                logger.info(f"Decrypting with Selenium using API: {api_url}")

                # 构建解密 URL
                decrypt_url = f"{api_url}?data={encrypted_data}"

                # 访问解密服务
                driver.get(decrypt_url)

                # 等待 JavaScript 执行完成
                time.sleep(2)

                # 获取页面内容
                page_source = driver.page_source

                # 尝试从页面中提取解密结果
                # 通常解密服务会返回 JSON 或在页面中显示结果
                try:
                    # 尝试解析 JSON
                    result = json.loads(page_source)
                    logger.info("Decryption successful (JSON)")
                    return json.dumps(result)
                except:
                    # 尝试从 HTML 中提取
                    if "data" in page_source or "result" in page_source:
                        logger.info("Decryption successful (HTML)")
                        return page_source

                    logger.warning("Could not extract decryption result")
                    return None

            except Exception as e:
                logger.error(f"Selenium decryption error: {e}")
                return None

    def login(self, username: str, password: str, code: str) -> bool:
        if not self.cid:
            logger.error("Please fetch captcha first")
            return False

        payload = {
            "username": username,
            "password": password,
            "cid": self.cid,
            "imageCode": code,
        }

        logger.info(f"Logging in user: {username}...")
        try:
            resp = self.session.post(LOGIN_URL, headers=self._build_headers(True), json=payload, timeout=10)
            result = resp.json()

            if result.get("code") != 0:
                logger.error(f"Login failed: {result.get('msg')}")
                return False

            token = result.get("data", {}).get("access_token")
            if token:
                self.save_token(token)
                self.save_cookies()
                user = result.get("data", {}).get("user", {})
                logger.info(f"Login success! User: {user.get('name')}")
                return True
            else:
                logger.error("No token in response")
                return False
        except Exception as e:
            logger.error(f"Login error: {e}")
            return False

    def submit_code_test(self, code: str, input_data: str, language: str) -> Optional[int]:
        if not self.token:
            self.load_token()
        if not self.token:
            logger.error("Not logged in")
            return None

        payload = {"code": code, "input": input_data, "language": language}
        logger.info(f"Submitting code ({language})...")

        try:
            resp = self.session.post(JUDGE_TEST_URL, headers=self._build_headers(True, True), json=payload, timeout=10)
            result = resp.json()

            if result.get("code") == 0:
                jid = result.get("data")
                logger.info(f"Submit success! ID: {jid}")
                return jid
            else:
                logger.error(f"Submit failed: {result.get('msg')}")
                return None
        except Exception as e:
            logger.error(f"Submit error: {e}")
            return None

    def poll_result(self, judge_id: int) -> Optional[Dict]:
        """轮询测试提交结果"""
        logger.info(f"Polling result (ID: {judge_id})...")
        for i in range(1, 61):
            time.sleep(1)
            try:
                resp = self.session.get(
                    RESULT_TEST_URL,
                    params={"id": judge_id},
                    headers=self._build_headers(with_auth=True),
                    timeout=10
                )
                result = resp.json()
                data = result.get("data", {})

                if data.get("result"):
                    res = data.get("result")
                    out = data.get("output", "")
                    err = data.get("compile_err", "")
                    run_err = data.get("runtime_err", "")

                    logger.info(f"Judge complete: {res}")
                    return {
                        "result": res,
                        "output": out,
                        "compile_error": err,
                        "runtime_error": run_err
                    }
                else:
                    if i % 5 == 0:
                        logger.info(f"Waiting... ({i}s)")

            except Exception as e:
                logger.error(f"Poll error: {e}")

        logger.warning("Poll timeout")
        return None


# 全局后端实例
backend = KuDingBackend()


# ========== API 端点 ==========

@app.route('/api/captcha/login', methods=['GET'])
def get_login_captcha():
    """获取登录验证码"""
    cid, image_data = backend.fetch_captcha()
    if image_data:
        return jsonify({
            "success": True,
            "cid": cid,
            "image": base64.b64encode(image_data).decode()
        })
    return jsonify({"success": False, "error": "Failed to fetch captcha"}), 400


@app.route('/api/captcha/problem', methods=['GET'])
def get_problem_captcha():
    """获取题目验证码"""
    cid, image_data = backend.fetch_problem_captcha()
    if image_data:
        return jsonify({
            "success": True,
            "cid": cid,
            "image": base64.b64encode(image_data).decode()
        })
    return jsonify({"success": False, "error": "Failed to fetch captcha"}), 400


@app.route('/api/ocr', methods=['POST'])
def perform_ocr():
    """OCR 识别验证码"""
    data = request.json
    image_b64 = data.get('image')
    ocr_mode = data.get('mode', 'normal')

    if not image_b64:
        return jsonify({"success": False, "error": "No image provided"}), 400

    try:
        image_data = base64.b64decode(image_b64)
        text = backend.ocr_captcha(image_data, ocr_mode)
        return jsonify({"success": True, "text": text})
    except Exception as e:
        logger.error(f"OCR error: {e}")
        return jsonify({"success": False, "error": str(e)}), 400


@app.route('/api/decrypt', methods=['POST'])
def decrypt_data():
    """使用 Selenium 解密数据"""
    data = request.json
    encrypted_data = data.get('data')
    api_url = data.get('api_url', 'https://kddecode.api.cbzstudio.qzz.io')

    if not encrypted_data:
        return jsonify({"success": False, "error": "No encrypted data provided"}), 400

    try:
        result = backend.decrypt_with_selenium(encrypted_data, api_url)
        if result:
            return jsonify({"success": True, "data": result})
        else:
            return jsonify({"success": False, "error": "Decryption failed"}), 400
    except Exception as e:
        logger.error(f"Decrypt error: {e}")
        return jsonify({"success": False, "error": str(e)}), 400


@app.route('/api/login', methods=['POST'])
def login():
    """登录"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    code = data.get('code')

    if not all([username, password, code]):
        return jsonify({"success": False, "error": "Missing credentials"}), 400

    success = backend.login(username, password, code)
    return jsonify({"success": success})


@app.route('/api/submit/test', methods=['POST'])
def submit_test():
    """提交测试代码"""
    data = request.json
    code = data.get('code')
    input_data = data.get('input', '')
    language = data.get('language', 'cpp')

    if not code:
        return jsonify({"success": False, "error": "No code provided"}), 400

    jid = backend.submit_code_test(code, input_data, language)
    if jid:
        return jsonify({"success": True, "judge_id": jid})
    return jsonify({"success": False, "error": "Submit failed"}), 400


@app.route('/api/result/test/<int:judge_id>', methods=['GET'])
def get_test_result(judge_id):
    """获取测试结果"""
    result = backend.poll_result(judge_id)
    if result:
        return jsonify({"success": True, "data": result})
    return jsonify({"success": False, "error": "Result not ready"}), 400


@app.route('/api/status', methods=['GET'])
def get_status():
    """获取后端状态"""
    return jsonify({
        "success": True,
        "logged_in": backend.token is not None,
        "ocr_engine": OCR_ENGINE,
        "selenium_available": SELENIUM_AVAILABLE
    })


@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        "status": "ok",
        "selenium": "available" if SELENIUM_AVAILABLE else "unavailable",
        "ocr": OCR_ENGINE or "unavailable"
    })


@app.teardown_appcontext
def shutdown_session(exception=None):
    """应用关闭时清理资源"""
    close_selenium()


if __name__ == '__main__':
    try:
        # 初始化 Selenium
        init_selenium()

        # 启动 Flask 应用
        app.run(host='127.0.0.1', port=5000, debug=False, threaded=True)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        close_selenium()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        close_selenium()
