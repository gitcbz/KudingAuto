#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
酷丁评测系统 GUI 版本 - v2.0
修复内容：
1. 动态布局适配小窗口
2. 测试提交显示完整输出结果
3. 题号提交支持验证码爬取和OCR
4. 使用requests获取结果页面
5. 记住密码功能
"""

import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import json
#from kuding_decrypt import decrypt_api_result, set_log_callback, set_local_api_url, get_local_api_url, set_debug_mode

# ========== 多语言支持 ==========
LANGUAGES = {
    "en": {
        # 标签页
        "tab_login": "Login",
        "tab_test": "Test Submit",
        "tab_problem": "Problem Submit",
        "tab_settings": "Settings",
        # 登录
        "username": "Username:",
        "password": "Password:",
        "login_btn": "Login",
        "logout_btn": "Logout",
        "remember_pwd": "Remember Password",
        # 测试提交
        "test_code": "Test Code:",
        "language": "Language:",
        "get_captcha": "Get Captcha",
        "refresh": "Refresh",
        "enter_captcha": "Enter captcha:",
        "auto_ocr": "Auto OCR",
        "submit_test": "Submit Test",
        # 题目提交
        "problem_id": "Problem ID:",
        "submit_mode": "Submit Mode:",
        "mode_editor": "Editor",
        "mode_file": "File",
        "code_file": "Code file:",
        "browse": "Browse...",
        "submit_problem": "Submit Problem",
        # 设置
        "settings_title": "Settings",
        "decrypt_settings": "Decryption Settings",
        "api_url": "Local API URL:",
        "save": "Save",
        "debug_mode": "Debug Mode (verbose logging)",
        "language": "Language:",
        # 日志
        "log": "Log",
        "clear": "Clear",
        # 结果
        "result": "Result",
        "score": "Score",
        "status": "Status",
        "time": "Time",
        "memory": "Memory",
    },
    "zh": {
        # 标签页
        "tab_login": "登录",
        "tab_test": "测试提交",
        "tab_problem": "题目提交",
        "tab_settings": "设置",
        # 登录
        "username": "用户名:",
        "password": "密码:",
        "login_btn": "登录",
        "logout_btn": "退出登录",
        "remember_pwd": "记住密码",
        # 测试提交
        "test_code": "测试代码:",
        "language": "语言:",
        "get_captcha": "获取验证码",
        "refresh": "刷新",
        "enter_captcha": "输入验证码:",
        "auto_ocr": "自动识别",
        "submit_test": "提交测试",
        # 题目提交
        "problem_id": "题目编号:",
        "submit_mode": "提交方式:",
        "mode_editor": "编辑器",
        "mode_file": "文件",
        "code_file": "代码文件:",
        "browse": "浏览...",
        "submit_problem": "提交题目",
        # 设置
        "settings_title": "设置",
        "decrypt_settings": "解密设置",
        "api_url": "本地 API 地址:",
        "save": "保存",
        "debug_mode": "调试模式 (详细日志)",
        "language": "语言:",
        # 日志
        "log": "日志",
        "clear": "清空",
        # 结果
        "result": "结果",
        "score": "得分",
        "status": "状态",
        "time": "时间",
        "memory": "内存",
    }
}

_current_language = "zh"


def set_language(lang: str):
    """设置当前语言"""
    global _current_language
    _current_language = lang


def get_language() -> str:
    """获取当前语言"""
    return _current_language


def t(key: str) -> str:
    """翻译函数"""
    return LANGUAGES.get(_current_language, LANGUAGES["en"]).get(key, key)
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

# 尝试导入 PIL
try:
    from PIL import ImageTk, Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("Warning: PIL not installed, please run: pip install pillow")

# 尝试导入 OCR
try:
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("Warning: pytesseract not installed, please run: pip install pytesseract")

# 尝试导入 CTkCodeBox
try:
    from CTkCodeBox import *
    CODEBOX_AVAILABLE = True
except ImportError:
    CODEBOX_AVAILABLE = False
    print("Tip: CTkCodeBox not installed, will use normal textbox")

# ========= 配置区域 =========
BASE_URL = "https://courseadmin.kuding.cn"
LOGIN_URL = urljoin(BASE_URL, "/course/auth/login_")
CAPTCHA_API = urljoin(BASE_URL, "/course/auth/captcha")
PROBLEM_CAPTCHA_API = urljoin(BASE_URL, "/problem/captcha")

JUDGE_TEST_URL = urljoin(BASE_URL, "/problem/judge/test")
JUDGE_PROBLEM_URL = urljoin(BASE_URL, "/problem/judge")
RESULT_TEST_URL = urljoin(BASE_URL, "/problem/judge/test/result")
RESULT_INFO_URL = urljoin(BASE_URL, "/problem/judge/resultInfo")

PROBLEM_SUBMIT_URL = "https://ke.kuding.cn/#/problem/problemSub"

TOKEN_FILE = "kd_token.txt"
COOKIE_FILE = "kd_cookies.txt"
CAPTCHA_FILE = "captcha_temp.png"
PROBLEM_CAPTCHA_FILE = "problem_captcha_temp.png"
LOGIN_DATA_FILE = "kd_login_data.json"  # 保存账号密码

DEFAULT_CODE_FILE = {
    "cpp": "test.cpp",
    "c": "test.c",
    "py": "test.py",
    "java": "Main.java",
}
# ===========================


class KuDingSubmitter:
    """后台逻辑处理类"""

    def __init__(self, log_callback):
        self.log = log_callback
        self.session = self._build_session()
        self.token = None
        self.cid = None
        self.problem_cid = None
        self.image_code = None
        self.problem_image_code = None

    def _build_session(self) -> requests.Session:
        session = requests.Session()
        if os.path.exists(COOKIE_FILE):
            self.log(f"Loading Cookie: {COOKIE_FILE}")
            session.cookies = LWPCookieJar(COOKIE_FILE)
            try:
                session.cookies.load(ignore_discard=True, ignore_expires=True)
            except Exception as e:
                self.log(f"Cookie load failed: {e}")
        return session

    def save_token(self, token: str):
        self.token = token
        with open(TOKEN_FILE, "w", encoding="utf-8") as f:
            f.write(token)
        self.log("Token saved")

    def load_token(self) -> Optional[str]:
        if not os.path.exists(TOKEN_FILE):
            return None
        with open(TOKEN_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()

    def save_cookies(self):
        if not isinstance(self.session.cookies, LWPCookieJar):
            self.session.cookies = LWPCookieJar(COOKIE_FILE)
        try:
            self.session.cookies.save(ignore_discard=True, ignore_expires=True)
            self.log("Cookie saved")
        except Exception as e:
            self.log(f"Cookie save failed: {e}")

    def _build_headers(self, with_content_type: bool = False, with_auth: bool = False) -> Dict[str, str]:
        headers = {
            "accept": "application/json, text/plain, */*",
            "origin": "https://ke.kuding.cn",
            "referer": "https://ke.kuding.cn/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
        }
        if with_content_type:
            headers["content-type"] = "application/json"
        if with_auth and self.token:
            headers["authorization"] = f"Token {self.token}"
        return headers

    def fetch_captcha(self) -> Tuple[Optional[str], Optional[bytes]]:
        try:
            self.log("Fetching login captcha...")
            self.cid = str(uuid.uuid4())
            v = int(time.time() * 1000)
            url = f"{CAPTCHA_API}?v={v}&cid={self.cid}"
            resp = self.session.get(url)
            resp.raise_for_status()
            image_data = resp.content
            with open(CAPTCHA_FILE, "wb") as f:
                f.write(image_data)
            self.log(f"Captcha updated (CID: {self.cid[:8]}...)")
            return self.cid, image_data
        except Exception as e:
            self.log(f"Fetch captcha failed: {e}")
            return None, None

    def fetch_problem_page_captcha(self, problem_id: str) -> Tuple[Optional[str], Optional[bytes]]:
        """爬取题目页面获取验证码，返回 (cid, image_data)"""
        try:
            self.log(f"Fetching problem {problem_id} captcha...")
            # 访问题目提交页面
            url = f"{PROBLEM_SUBMIT_URL}?id={problem_id}"
            resp = self.session.get(url, headers=self._build_headers())
            resp.raise_for_status()
            html = resp.text

            # 从HTML中提取验证码图片URL
            # 匹配格式: <img ... src="https://courseadmin.kuding.cn/problem/captcha?v=xxx&cid=xxx" ...>
            pattern = r'<img[^>]*src="([^"]*problem/captcha[^"]*)"[^>]*>'
            match = re.search(pattern, html)
            if not match:
                self.log("Captcha image not found in page")
                return None, None

            # 提取URL并解码HTML实体（如 &amp; -> &）
            captcha_url = html_unescape(match.group(1))
            # 确保是绝对URL
            if not captcha_url.startswith("http"):
                captcha_url = urljoin(BASE_URL, captcha_url)

            self.log(f"Captcha URL: {captcha_url}")

            # 从URL中提取cid参数
            cid_match = re.search(r'cid=([^&"\']+)', captcha_url)
            if cid_match:
                self.problem_cid = cid_match.group(1)
            else:
                self.problem_cid = str(uuid.uuid4())

            # 获取验证码图片
            img_resp = self.session.get(captcha_url, headers=self._build_headers())
            img_resp.raise_for_status()
            image_data = img_resp.content

            # 保存到临时文件
            with open(PROBLEM_CAPTCHA_FILE, "wb") as f:
                f.write(image_data)

            self.log(f"Problem captcha fetched (CID: {self.problem_cid[:8]}...)")
            return self.problem_cid, image_data

        except Exception as e:
            self.log(f"Fetch problem captcha failed: {e}")
            return None, None

    def fetch_problem_captcha_direct(self) -> Tuple[Optional[str], Optional[bytes]]:
        try:
            self.log("Fetching problem captcha...")
            self.problem_cid = str(uuid.uuid4())
            v = int(time.time() * 1000)
            url = f"{PROBLEM_CAPTCHA_API}?v={v}&cid={self.problem_cid}"
            resp = self.session.get(url)
            resp.raise_for_status()
            image_data = resp.content
            with open(PROBLEM_CAPTCHA_FILE, "wb") as f:
                f.write(image_data)
            self.log(f"Problem captcha updated (CID: {self.problem_cid[:8]}...)")
            return self.problem_cid, image_data
        except Exception as e:
            self.log(f"Fetch problem captcha failed: {e}")
            return None, None

    def ocr_captcha(self, image_data: bytes) -> str:
        if not OCR_AVAILABLE:
            return ""
        try:
            image = Image.open(BytesIO(image_data))
            image = image.convert('L')
            text = pytesseract.image_to_string(image, config='--psm 7')
            return text.strip()
        except Exception as e:
            self.log(f"OCR error: {e}")
            return ""

    def login(self, username: str, password: str, code: str) -> bool:
        if not self.cid:
            self.log("Please fetch captcha first")
            return False

        payload = {
            "username": username,
            "password": password,
            "cid": self.cid,
            "imageCode": code,
        }

        self.log(f"Logging in user: {username}...")
        try:
            resp = self.session.post(LOGIN_URL, headers=self._build_headers(True), data=json.dumps(payload))
            result = resp.json()

            if result.get("code") != 0:
                self.log(f"Login failed: {result.get('msg')}")
                return False

            token = result.get("data", {}).get("access_token")
            if token:
                self.save_token(token)
                self.save_cookies()
                user = result.get("data", {}).get("user", {})
                self.log(f"Login success! User: {user.get('name')}, Coin: {user.get('coin')}")
                return True
            else:
                self.log("No token in response")
                return False
        except Exception as e:
            self.log(f"Login error: {e}")
            return False

    def submit_code_test(self, code: str, input_data: str, language: str) -> Optional[int]:
        if not self.token:
            self.load_token()
        if not self.token:
            self.log("Not logged in")
            return None

        payload = {"code": code, "input": input_data, "language": language}
        self.log(f"Submitting code ({language})...")

        try:
            resp = self.session.post(JUDGE_TEST_URL, headers=self._build_headers(True, True), data=json.dumps(payload))
            result = resp.json()

            if result.get("code") == 0:
                jid = result.get("data")
                self.log(f"Submit success! ID: {jid}")
                return jid
            else:
                self.log(f"Submit failed: {result.get('msg')}")
                return None
        except Exception as e:
            self.log(f"Submit error: {e}")
            return None

    def submit_problem_code(self, problem_id: str, code: str, language: str,
                            is_file_input: bool = False) -> Optional[int]:
        if not self.token:
            self.load_token()
        if not self.token:
            self.log("Not logged in")
            return None

        payload = {
            "language": language,
            "cid": self.problem_cid or str(uuid.uuid4()),
            "code": code,
            "exam_id": 0,
            "id": problem_id,
            "imageCode": self.problem_image_code or "",
            "is_file_input": "1" if is_file_input else "0",
            "xml": ""
        }

        self.log(f"Submitting problem {problem_id} ({language})...")

        try:
            resp = self.session.post(
                JUDGE_PROBLEM_URL,
                headers=self._build_headers(True, True),
                data=json.dumps(payload)
            )
            result = resp.json()

            if result.get("code") == 0:
                jid = result.get("data")
                self.log(f"Submit success! ID: {jid}")
                return jid
            else:
                self.log(f"Submit failed: {result.get('msg')}")
                return None
        except Exception as e:
            self.log(f"Submit error: {e}")
            return None

    def poll_result(self, judge_id: int, callback_result=None):
        """轮询测试提交结果 - 显示完整输出"""
        self.log(f"Polling result (ID: {judge_id})...")
        for i in range(1, 61):  # 增加到60秒
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

                # 记录原始响应用于调试
                if i <= 2:
                    self.log(f"Debug: response code={result.get('code')}, has_data={bool(data)}")

                # 检查是否有结果
                if data.get("result"):
                    res = data.get("result")
                    out = data.get("output", "")
                    err = data.get("compile_err", "")
                    run_err = data.get("runtime_err", "")

                    self.log(f"Judge complete: {res}")

                    # 显示完整输出
                    if out:
                        self.log(f"Program output:\n{out}")

                    if err:
                        self.log(f"Compile error:\n{err}")

                    if run_err:
                        self.log(f"Runtime error:\n{run_err}")

                    if callback_result:
                        callback_result(res, out, err)
                    return
                else:
                    if i % 5 == 0:
                        self.log(f"Waiting... ({i}s)")

            except requests.exceptions.Timeout:
                self.log(f"Request timeout ({i}s)")
            except Exception as e:
                self.log(f"Poll error: {e}")

        self.log("Poll timeout - result may still be processing")


class KudingGUI:
    """主界面类 - 使用 customtkinter + 动态布局"""

    def __init__(self, root):
        self.root = root
        self.root.title("Kuding Judge Helper v2.4")
        self.root.geometry("900x750")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.root.minsize(700, 600)

        self.submitter = None
        self.captcha_image_data = None
        self.problem_captcha_image_data = None
        self.ocr_enhanced_var = ctk.BooleanVar(value=False)  # OCR增强选项
        self.ocr_super_var = ctk.BooleanVar(value=False)  # 超级增强OCR选项（登录）
        self.problem_ocr_super_var = ctk.BooleanVar(value=False)  # 超级增强OCR选项（问题）

        # 设置解密模块的日志回调
        set_log_callback(self.log)

        self.create_widgets()
        self.submitter = KuDingSubmitter(self.log)
        self.root.after(100, self.init_app)

    def create_widgets(self):
        main_container = ctk.CTkFrame(self.root, fg_color="#2b2b2b")
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        title_label = ctk.CTkLabel(main_container, text="Kuding Judge Helper v2.3", font=("Arial", 20, "bold"))
        title_label.pack(pady=8)

        self.notebook = ctk.CTkTabview(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5)

        tab_login = self.notebook.add("Login")
        tab_test = self.notebook.add("Test Submit")
        tab_problem = self.notebook.add("Problem Submit")
        tab_settings = self.notebook.add("Settings")

        self.create_login_tab(tab_login)
        self.create_test_tab(tab_test)
        self.create_problem_tab(tab_problem)
        self.create_settings_tab(tab_settings)

        log_frame = ctk.CTkFrame(main_container, fg_color="#3a3a3a")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(8, 0))

        log_header = ctk.CTkFrame(log_frame, fg_color="transparent")
        log_header.pack(fill=tk.X, padx=5, pady=(5, 0))

        ctk.CTkLabel(log_header, text="Log", font=("Arial", 11)).pack(side=tk.LEFT)

        self.btn_clear_log = ctk.CTkButton(log_header, text="Clear", command=self.clear_log,
                                          fg_color="#f44336", width=80, height=24)
        self.btn_clear_log.pack(side=tk.RIGHT)

        self.log_text = ctk.CTkTextbox(log_frame, height=120)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def create_login_tab(self, parent):
        scroll_frame = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        content_frame = ctk.CTkFrame(scroll_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)

        split_container = ctk.CTkFrame(content_frame, fg_color="transparent")
        for i in range(2):
            split_container.grid_columnconfigure(i, weight=1)

        left_frame = ctk.CTkFrame(split_container, fg_color="#3a3a3a")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=5)

        ctk.CTkLabel(left_frame, text="Username:", font=("Arial", 11)).pack(anchor=tk.W, padx=10, pady=(10, 3))
        self.entry_user = ctk.CTkEntry(left_frame, placeholder_text="Enter username", height=32)
        self.entry_user.pack(fill=tk.X, padx=10, pady=(0, 10))

        ctk.CTkLabel(left_frame, text="Password:", font=("Arial", 11)).pack(anchor=tk.W, padx=10, pady=(0, 3))
        self.entry_pass = ctk.CTkEntry(left_frame, show="*", placeholder_text="Enter password", height=32)
        self.entry_pass.pack(fill=tk.X, padx=10, pady=(0, 10))

        # 记住密码选项
        self.remember_var = ctk.BooleanVar(value=False)
        self.remember_check = ctk.CTkCheckBox(left_frame, text="Remember password", variable=self.remember_var,
                                              font=("Arial", 10))
        self.remember_check.pack(anchor=tk.W, padx=10, pady=(0, 5))

        ctk.CTkLabel(left_frame, text="Captcha:", font=("Arial", 11)).pack(anchor=tk.W, padx=10, pady=(0, 3))
        self.entry_code = ctk.CTkEntry(left_frame, placeholder_text="Enter captcha", height=32)
        self.entry_code.pack(fill=tk.X, padx=10, pady=(0, 10))
        self.entry_code.bind("<Return>", lambda e: self.do_login())

        self.btn_login = ctk.CTkButton(left_frame, text="Login", command=self.do_login,
                                      fg_color="#1f77b4", height=36)
        self.btn_login.pack(fill=tk.X, padx=10, pady=(5, 15))

        right_frame = ctk.CTkFrame(split_container, fg_color="#3a3a3a")
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=5)

        ctk.CTkLabel(right_frame, text="Captcha (click to refresh)", font=("Arial", 11)).pack(pady=(10, 5))

        self.lbl_captcha = ctk.CTkLabel(right_frame, text="Loading...", cursor="hand2",
                                       text_color="#ffffff", width=150, height=80)
        self.lbl_captcha.bind("<Button-1>", lambda e: self.refresh_captcha())
        self.lbl_captcha.pack(pady=5)

        ctk.CTkButton(right_frame, text="Refresh", command=self.refresh_captcha,
                     fg_color="#4CAF50", height=32).pack(pady=5, padx=15, fill=tk.X)

        self.ocr_var = ctk.BooleanVar(value=False)
        self.ocr_check_login = ctk.CTkCheckBox(right_frame, text="Auto OCR", variable=self.ocr_var,
                                                command=self.on_ocr_toggle, font=("Arial", 11))
        self.ocr_check_login.pack(pady=5)

        self.ocr_enhanced_var = ctk.BooleanVar(value=False)  # OCR增强选项
        self.ocr_enhanced_check_login = ctk.CTkCheckBox(right_frame, text="OCR增强", variable=self.ocr_enhanced_var,
                                                      font=("Arial", 10))
        self.ocr_enhanced_check_login.pack(pady=2)

        self.ocr_super_var = ctk.BooleanVar(value=False)  # 超级增强选项
        self.ocr_super_check_login = ctk.CTkCheckBox(right_frame, text="超级增强OCR(约99%准确率)", variable=self.ocr_super_var,
                                                    command=self.on_super_ocr_toggle_login, font=("Arial", 10))
        self.ocr_super_check_login.pack(pady=2)

        if not OCR_AVAILABLE:
            self.ocr_check_login.configure(state="disabled", text="OCR N/A")
            ctk.CTkLabel(right_frame, text="Need Tesseract-OCR", text_color="gray", font=("Arial", 9)).pack()

        split_container.pack(fill=tk.BOTH, expand=True)

    def create_test_tab(self, parent):
        scroll_frame = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        top_frame = ctk.CTkFrame(scroll_frame, fg_color="#3a3a3a")
        top_frame.pack(fill=tk.X, pady=(0, 8))

        lang_row = ctk.CTkFrame(top_frame, fg_color="transparent")
        lang_row.pack(fill=tk.X, padx=10, pady=8)

        ctk.CTkLabel(lang_row, text="Language:", font=("Arial", 11)).pack(side=tk.LEFT)
        self.combo_lang_test = ctk.CTkComboBox(lang_row, values=["cpp", "py", "c", "java"],
                                              state="readonly", width=100)
        self.combo_lang_test.set("cpp")
        self.combo_lang_test.pack(side=tk.LEFT, padx=8)

        file_row = ctk.CTkFrame(top_frame, fg_color="transparent")
        file_row.pack(fill=tk.X, padx=10, pady=(0, 8))

        ctk.CTkLabel(file_row, text="Code file:", font=("Arial", 11)).pack(side=tk.LEFT)
        self.entry_code_file_test = ctk.CTkEntry(file_row, placeholder_text="Select code file")
        self.entry_code_file_test.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8)
        self.entry_code_file_test.insert(0, DEFAULT_CODE_FILE["cpp"])

        ctk.CTkButton(file_row, text="Browse...", command=self.browse_code_test,
                     fg_color="#1f77b4", width=70).pack(side=tk.LEFT)
        self.combo_lang_test.bind("<<ComboboxSelected>>", self.on_lang_change_test)

        input_frame = ctk.CTkFrame(scroll_frame, fg_color="#3a3a3a")
        input_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

        ctk.CTkLabel(input_frame, text="Input data:", font=("Arial", 11)).pack(anchor=tk.W, padx=10, pady=(8, 5))

        input_btn_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        input_btn_frame.pack(fill=tk.X, padx=10)

        self.input_type_test = tk.StringVar(value="manual")
        ctk.CTkRadioButton(input_btn_frame, text="Manual", variable=self.input_type_test,
                         value="manual", font=("Arial", 11)).pack(side=tk.LEFT)
        ctk.CTkRadioButton(input_btn_frame, text="From file", variable=self.input_type_test,
                         value="file", font=("Arial", 11)).pack(side=tk.LEFT, padx=10)
        ctk.CTkButton(input_btn_frame, text="Load", command=self.load_input_file_test,
                     fg_color="#1f77b4", width=80).pack(side=tk.RIGHT)

        self.text_input_test = ctk.CTkTextbox(input_frame, height=100)
        self.text_input_test.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        self.text_input_test.insert(tk.END, "test")

        self.btn_submit_test = ctk.CTkButton(scroll_frame, text="Submit",
                                            command=self.do_submit_test,
                                            fg_color="#1f77b4", font=("Arial", 13), height=40)
        self.btn_submit_test.pack(fill=tk.X, pady=(0, 5))

    def create_problem_tab(self, parent):
        scroll_frame = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        top_frame = ctk.CTkFrame(scroll_frame, fg_color="#3a3a3a")
        top_frame.pack(fill=tk.X, pady=(0, 8))

        row1 = ctk.CTkFrame(top_frame, fg_color="transparent")
        row1.pack(fill=tk.X, padx=10, pady=8)

        ctk.CTkLabel(row1, text="Problem ID:", font=("Arial", 11)).pack(side=tk.LEFT)
        self.entry_problem_id = ctk.CTkEntry(row1, placeholder_text="e.g. 1000", width=100)
        self.entry_problem_id.pack(side=tk.LEFT, padx=5)

        ctk.CTkLabel(row1, text="Language:", font=("Arial", 11)).pack(side=tk.LEFT, padx=(15, 0))
        self.combo_lang_problem = ctk.CTkComboBox(row1, values=["cpp", "c", "py", "java"],
                                                  state="readonly", width=100)
        self.combo_lang_problem.set("cpp")
        self.combo_lang_problem.pack(side=tk.LEFT, padx=5)

        self.btn_get_captcha = ctk.CTkButton(row1, text="Get Captcha", command=self.fetch_problem_captcha,
                                           fg_color="#4CAF50", width=100)
        self.btn_get_captcha.pack(side=tk.LEFT, padx=(20, 0))

        row2 = ctk.CTkFrame(top_frame, fg_color="transparent")
        row2.pack(fill=tk.X, padx=10, pady=(0, 8))

        self.submit_mode_var = tk.StringVar(value="editor")
        ctk.CTkRadioButton(row2, text="Editor", variable=self.submit_mode_var, value="editor",
                         command=self.on_submit_mode_change, font=("Arial", 11)).pack(side=tk.LEFT)
        ctk.CTkRadioButton(row2, text="File", variable=self.submit_mode_var, value="file",
                         command=self.on_submit_mode_change, font=("Arial", 11)).pack(side=tk.LEFT, padx=15)

        captcha_frame = ctk.CTkFrame(scroll_frame, fg_color="#3a3a3a")
        captcha_frame.pack(fill=tk.X, pady=(0, 8))

        captcha_row = ctk.CTkFrame(captcha_frame, fg_color="transparent")
        captcha_row.pack(fill=tk.X, padx=10, pady=8)

        captcha_left = ctk.CTkFrame(captcha_row, fg_color="transparent")
        captcha_left.pack(side=tk.LEFT)

        ctk.CTkLabel(captcha_left, text="Captcha:", font=("Arial", 11)).pack(anchor=tk.W)
        self.lbl_problem_captcha = ctk.CTkLabel(captcha_left, text="Click 'Get Captcha'",
                                               cursor="hand2", text_color="#ffffff",
                                               width=120, height=60)
        self.lbl_problem_captcha.bind("<Button-1>", lambda e: self.refresh_problem_captcha())
        self.lbl_problem_captcha.pack(pady=5)

        ctk.CTkButton(captcha_left, text="Refresh", command=self.refresh_problem_captcha,
                     fg_color="#4CAF50", width=80, height=28).pack()

        captcha_right = ctk.CTkFrame(captcha_row, fg_color="transparent")
        captcha_right.pack(side=tk.LEFT, padx=(20, 0), fill=tk.X, expand=True)

        ctk.CTkLabel(captcha_right, text="Enter captcha:", font=("Arial", 11)).pack(anchor=tk.W)
        self.entry_problem_code = ctk.CTkEntry(captcha_right, placeholder_text="Enter captcha", height=32)
        self.entry_problem_code.pack(fill=tk.X, pady=5)

        self.problem_ocr_var = ctk.BooleanVar(value=False)
        self.ocr_check_problem = ctk.CTkCheckBox(captcha_right, text="Auto OCR",
                                                  variable=self.problem_ocr_var,
                                                  command=self.on_problem_ocr_toggle, font=("Arial", 11))
        self.ocr_check_problem.pack(anchor=tk.W)

        self.ocr_enhanced_check_problem = ctk.CTkCheckBox(captcha_right, text="OCR增强", variable=self.ocr_enhanced_var,
                                                        font=("Arial", 10))
        self.ocr_enhanced_check_problem.pack(anchor=tk.W, pady=2)

        self.ocr_super_check_problem = ctk.CTkCheckBox(captcha_right, text="超级增强OCR(约99%准确率)", variable=self.problem_ocr_super_var,
                                                          command=self.on_super_ocr_toggle_problem, font=("Arial", 10))
        self.ocr_super_check_problem.pack(anchor=tk.W, pady=2)

        if not OCR_AVAILABLE:
            self.ocr_check_problem.configure(state="disabled", text="OCR N/A")

        if CODEBOX_AVAILABLE:
            editor_frame = ctk.CTkFrame(scroll_frame, fg_color="#2b2b2b")
            editor_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

            ctk.CTkLabel(editor_frame, text="Code Editor", font=("Arial", 11)).pack(anchor=tk.W, padx=5, pady=(5, 3))

            self.code_editor = CTkCodeBox(
                editor_frame,
                language="cpp",
                theme="monokai",
                line_numbering=True,
                height=180
            )
            self.code_editor.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
        else:
            editor_frame = ctk.CTkFrame(scroll_frame, fg_color="#2b2b2b")
            editor_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

            ctk.CTkLabel(editor_frame, text="Code Editor", font=("Arial", 11)).pack(anchor=tk.W, padx=5, pady=(5, 3))

            self.code_editor = ctk.CTkTextbox(editor_frame, height=180)
            self.code_editor.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
            self.code_editor.insert(tk.END, "#include <iostream>\nusing namespace std;\nint main() {\n    // your code\n    return 0;\n}")

        file_frame = ctk.CTkFrame(scroll_frame, fg_color="#3a3a3a")
        file_frame.pack(fill=tk.X)

        file_row = ctk.CTkFrame(file_frame, fg_color="transparent")
        file_row.pack(fill=tk.X, padx=10, pady=8)

        ctk.CTkLabel(file_row, text="Code file:", font=("Arial", 11)).pack(side=tk.LEFT)
        self.entry_code_file_problem = ctk.CTkEntry(file_row, placeholder_text="Select code file")
        self.entry_code_file_problem.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8)
        self.entry_code_file_problem.insert(0, DEFAULT_CODE_FILE["cpp"])
        self.entry_code_file_problem.configure(state="disabled")

        self.btn_browse_code_problem = ctk.CTkButton(file_row, text="Browse...",
                                                     command=self.browse_code_problem,
                                                     fg_color="#1f77b4", width=70)
        self.btn_browse_code_problem.pack(side=tk.LEFT)
        self.btn_browse_code_problem.configure(state="disabled")

        self.btn_submit_problem = ctk.CTkButton(scroll_frame, text="Submit Problem",
                                              command=self.do_submit_problem,
                                              fg_color="#1f77b4", font=("Arial", 13), height=40)
        self.btn_submit_problem.pack(fill=tk.X, pady=(0, 5))

    def create_settings_tab(self, parent):
        """创建设置标签页"""
        scroll_frame = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 解密设置部分
        decrypt_frame = ctk.CTkFrame(scroll_frame, fg_color="#3a3a3a")
        decrypt_frame.pack(fill=tk.X, pady=(0, 10))

        ctk.CTkLabel(decrypt_frame, text="Decryption Settings",
                    font=("Arial", 14, "bold")).pack(anchor=tk.W, padx=10, pady=(10, 5))

        # 本地 API URL 设置
        url_row = ctk.CTkFrame(decrypt_frame, fg_color="transparent")
        url_row.pack(fill=tk.X, padx=10, pady=5)

        ctk.CTkLabel(url_row, text="Local API URL:", font=("Arial", 11)).pack(side=tk.LEFT)
        self.entry_local_api_url = ctk.CTkEntry(url_row, placeholder_text="https://kddecode.api.cbzstudio.qzz.io", width=280)
        self.entry_local_api_url.pack(side=tk.LEFT, padx=8)

        # 加载当前设置
        current_url = get_local_api_url()
        self.entry_local_api_url.insert(0, current_url)

        self.btn_save_api_url = ctk.CTkButton(url_row, text="Save", command=self.save_local_api_url,
                                             fg_color="#4CAF50", width=70)
        self.btn_save_api_url.pack(side=tk.LEFT)

        # Debug 模式选项
        debug_row = ctk.CTkFrame(decrypt_frame, fg_color="transparent")
        debug_row.pack(fill=tk.X, padx=10, pady=5)

        self.debug_mode_var = tk.BooleanVar(value=False)
        self.debug_check = ctk.CTkCheckBox(debug_row, text="Debug Mode (verbose logging)",
                                           variable=self.debug_mode_var,
                                           command=self.toggle_debug_mode,
                                           font=("Arial", 11))
        self.debug_check.pack(side=tk.LEFT)

        # 语言选项
        lang_row = ctk.CTkFrame(decrypt_frame, fg_color="transparent")
        lang_row.pack(fill=tk.X, padx=10, pady=5)

        ctk.CTkLabel(lang_row, text="Language:", font=("Arial", 11)).pack(side=tk.LEFT)
        self.language_var = tk.StringVar(value=get_language())
        self.combo_language = ctk.CTkComboBox(
            lang_row,
            values=["en", "zh"],
            variable=self.language_var,
            state="readonly",
            width=100,
            command=self.change_language
        )
        self.combo_language.pack(side=tk.LEFT, padx=8)
        # 显示当前语言名称
        self.lbl_current_lang = ctk.CTkLabel(lang_row,
                                              text="中文" if get_language() == "zh" else "English",
                                              font=("Arial", 11))
        self.lbl_current_lang.pack(side=tk.LEFT)

        # 说明文字
        info_frame = ctk.CTkFrame(scroll_frame, fg_color="#2b2b2b")
        info_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=5)

        info_text = """Decryption Settings:

The application uses Selenium to access the API URL for
decryption. This is the default and recommended method.

API URL: The address of your decryption server.
- Default: https://kddecode.api.cbzstudio.qzz.io
- The server should accept 'data' parameter via GET request
- The server should return decrypted JSON data

Your API server needs to handle the encrypted data and
return the decrypted result (similar to test_decrypt.py).

If the Selenium method fails, the system will automatically
fallback to remote service or local Node.js service."""

        ctk.CTkLabel(info_frame, text=info_text, font=("Arial", 10),
                    justify=tk.LEFT, anchor=tk.NW).pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def save_local_api_url(self):
        """保存本地 API URL 设置"""
        new_url = self.entry_local_api_url.get().strip()
        if not new_url:
            new_url = "http://127.0.0.1"
        set_local_api_url(new_url)
        self.log(f"Local API URL saved: {new_url}")
        messagebox.showinfo("Settings Saved", f"Local API URL has been set to:\n{new_url}")

    def toggle_debug_mode(self):
        """切换 Debug 模式"""
        enabled = self.debug_mode_var.get()
        set_debug_mode(enabled)
        status = "enabled" if enabled else "disabled"
        self.log(f"Debug mode {status}")

    def change_language(self, choice=None):
        """切换语言"""
        lang = self.language_var.get()
        set_language(lang)
        lang_name = "中文" if lang == "zh" else "English"
        self.lbl_current_lang.configure(text=lang_name)
        self.log(f"Language changed to: {lang_name}")
        messagebox.showinfo("Language Changed", f"Language has been set to {lang_name}\n\nPlease restart the application for full effect.")

    def log(self, message):
        def _append():
            if not self.root.winfo_exists(): return
            self.log_text.configure(state='normal')
            self.log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {message}\n")
            self.log_text.see(tk.END)
            self.log_text.configure(state='disabled')

        if threading.current_thread() != threading.main_thread():
            self.root.after(0, _append)
        else:
            _append()

    def clear_log(self):
        self.log_text.configure(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.configure(state='disabled')

    def set_ui_state(self, enabled: bool):
        state = "normal" if enabled else "disabled"
        self.btn_login.configure(state=state)
        self.btn_submit_test.configure(state=state)
        self.btn_submit_problem.configure(state=state)

    def init_app(self):
        if not self.submitter: return
        token = self.submitter.load_token()
        if token:
            self.log("Found saved login info")
        else:
            self.log("Please login first")

        # 加载保存的登录数据
        self.load_login_data()
        self.refresh_captcha()

    def on_ocr_toggle(self):
        if self.ocr_var.get():
            self.log("Login OCR enabled")
            if hasattr(self, 'captcha_image_data') and self.captcha_image_data:
                self.perform_ocr(self.captcha_image_data, is_login=True)
        else:
            self.log("Login OCR disabled")

    def on_super_ocr_toggle_login(self):
        """超级增强OCR登录切换"""
        if self.ocr_super_var.get():
            self.log("Login Super OCR enabled")
            if hasattr(self, 'captcha_image_data') and self.captcha_image_data:
                self.perform_super_ocr(self.captcha_image_data, is_login=True)
        else:
            self.log("Login Super OCR disabled")

    def on_problem_ocr_toggle(self):
        if self.problem_ocr_var.get():
            self.log("Problem OCR enabled")
            if hasattr(self, 'problem_captcha_image_data') and self.problem_captcha_image_data:
                self.perform_ocr(self.problem_captcha_image_data, is_login=False)
        else:
            self.log("Problem OCR disabled")

    def on_super_ocr_toggle_problem(self):
        """超级增强OCR问题提交切换"""
        if self.problem_ocr_super_var.get():
            self.log("Problem Super OCR enabled")
            if hasattr(self, 'problem_captcha_image_data') and self.problem_captcha_image_data:
                self.perform_super_ocr(self.problem_captcha_image_data, is_login=False)
        else:
            self.log("Problem Super OCR disabled")

    def refresh_captcha(self):
        """同步刷新验证码 - 不使用线程"""
        if not self.submitter: return

        self.log("Refreshing login captcha...")
        cid, data = self.submitter.fetch_captcha()
        if data:
            self.captcha_image_data = data
            self.log(f"Captcha fetched, CID: {cid}")
            self.update_captcha_image(data, self.lbl_captcha)
            if self.ocr_var.get():
                self.perform_ocr(data, is_login=True)
        else:
            self.log("Failed to fetch captcha")

    def fetch_problem_captcha(self):
        """同步刷新问题验证码 - 不使用线程"""
        if not self.submitter: return

        problem_id = self.entry_problem_id.get().strip() or "1000"
        self.log(f"Fetching problem {problem_id} captcha...")
        cid, data = self.submitter.fetch_problem_page_captcha(problem_id)
        if data:
            self.problem_captcha_image_data = data
            self.log(f"Problem captcha fetched, CID: {cid}")
            self.update_captcha_image(data, self.lbl_problem_captcha)
            if self.problem_ocr_var.get():
                self.perform_ocr(data, is_login=False)
        else:
            self.log("Failed to fetch problem captcha")

    def refresh_problem_captcha(self):
        """同步刷新问题验证码 - 不使用线程"""
        if not self.submitter: return

        self.log("Refreshing problem captcha...")
        cid, data = self.submitter.fetch_problem_captcha_direct()
        if data:
            self.problem_captcha_image_data = data
            self.log(f"Problem captcha refreshed, CID: {cid}")
            self.update_captcha_image(data, self.lbl_problem_captcha)
            if self.problem_ocr_var.get():
                self.perform_ocr(data, is_login=False)
        else:
            self.log("Failed to refresh problem captcha")

    def perform_ocr(self, image_data, is_login=True):
        if not OCR_AVAILABLE or not self.submitter: return

        ocr_result = self.submitter.ocr_captcha(image_data)

        if ocr_result:
            if is_login:
                self.root.after(0, lambda: self.update_ocr_result(ocr_result, self.entry_code))
            else:
                self.root.after(0, lambda: self.update_ocr_result(ocr_result, self.entry_problem_code))


    def update_ocr_result(self, text, entry_widget):
        # OCR增强：去除空格、符号，只保留字母和数字
        if self.ocr_enhanced_var.get():
            original = text
            text = re.sub(r'[^A-Za-z0-9]', '', text)  # 只保留字母和数字
            self.log(f"OCR enhanced: '{original}' -> '{text}'")

        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, text)
        self.log(f"OCR result: {text}")
        if entry_widget == self.entry_problem_code:
            self.submitter.problem_image_code = text
        else:
            self.submitter.image_code = text

    def perform_super_ocr(self, image_data, is_login=True):
        """超级增强OCR - 判断结果是否为4个字符，不是则刷新验证码"""
        if not OCR_AVAILABLE or not self.submitter: return

        # 检查是否勾选了Auto OCR
        ocr_var = self.ocr_var if is_login else self.problem_ocr_var
        if not ocr_var.get():
            self.log("Please enable Auto OCR first")
            return

        ocr_result = self.submitter.ocr_captcha(image_data)

        if ocr_result:
            # OCR增强处理
            if self.ocr_enhanced_var.get():
                ocr_result = re.sub(r'[^A-Za-z0-9]', '', ocr_result)

            # 检查是否为4个字符
            if len(ocr_result) == 4:
                if is_login:
                    self.root.after(0, lambda: self.update_ocr_result(ocr_result, self.entry_code))
                else:
                    self.root.after(0, lambda: self.update_ocr_result(ocr_result, self.entry_problem_code))
            else:
                # 不是4个字符，刷新验证码
                self.log(f"OCR result not 4 chars ({len(ocr_result)}: {ocr_result}), refreshing captcha...")
                if is_login:
                    self.refresh_captcha()
                else:
                    self.refresh_problem_captcha()
    def update_captcha_image(self, image_data, label_widget):
        if not PIL_AVAILABLE or not image_data:
            label_widget.configure(text="Image load failed\n(PIL not installed)")
            return

        try:
            image = Image.open(BytesIO(image_data))
            w, h = image.size
            if w < 150: image = image.resize((w*2, h*2), Image.Resampling.LANCZOS)

            photo = ImageTk.PhotoImage(image)
            label_widget.configure(image=photo, text="")
            label_widget.image = photo
        except Exception as e:
            self.log(f"Image display error: {e}")

    def do_login(self):
        if not self.submitter: return

        user = self.entry_user.get().strip()
        pwd = self.entry_pass.get().strip()
        code = self.entry_code.get().strip()

        if not user or not pwd or not code:
            messagebox.showwarning("Warning", "Please fill all login fields")
            return

        self.set_ui_state(False)
        self.log("---------- Starting login ----------")

        def _task():
            success = self.submitter.login(user, pwd, code)
            self.root.after(0, lambda: self.set_ui_state(True))
            if success:
                # 如果勾选了记住密码，保存登录数据
                if self.remember_var.get():
                    self.save_login_data(user, pwd)
                else:
                    # 清除保存的登录数据
                    self.clear_login_data()
                self.root.after(0, lambda: messagebox.showinfo("Success", "Login successful!"))

        threading.Thread(target=_task, daemon=True).start()

    def save_login_data(self, username: str, password: str):
        """保存登录数据到文件"""
        try:
            data = {"username": username, "password": password}
            with open(LOGIN_DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            self.log(f"Login data saved to {LOGIN_DATA_FILE}")
        except Exception as e:
            self.log(f"Failed to save login data: {e}")

    def load_login_data(self):
        """从文件加载登录数据"""
        if not os.path.exists(LOGIN_DATA_FILE):
            return

        try:
            with open(LOGIN_DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)

            username = data.get("username", "")
            password = data.get("password", "")

            if username:
                self.entry_user.delete(0, tk.END)
                self.entry_user.insert(0, username)
            if password:
                self.entry_pass.delete(0, tk.END)
                self.entry_pass.insert(0, password)

            self.remember_var.set(True)  # 自动勾选记住密码
            self.log(f"Login data loaded from {LOGIN_DATA_FILE}")
        except Exception as e:
            self.log(f"Failed to load login data: {e}")

    def clear_login_data(self):
        """清除保存的登录数据"""
        try:
            if os.path.exists(LOGIN_DATA_FILE):
                os.remove(LOGIN_DATA_FILE)
                self.log("Saved login data cleared")
        except Exception as e:
            self.log(f"Failed to clear login data: {e}")

    def on_lang_change_test(self, event):
        lang = self.combo_lang_test.get()
        current = self.entry_code_file_test.get()
        is_default = any(current == v for v in DEFAULT_CODE_FILE.values())
        if is_default or not current:
            self.entry_code_file_test.delete(0, tk.END)
            self.entry_code_file_test.insert(0, DEFAULT_CODE_FILE.get(lang, "test.cpp"))

    def browse_code_test(self):
        file = filedialog.askopenfilename(filetypes=[("Code Files", "*.cpp *.c *.py *.java"), ("All Files", "*.*")])
        if file:
            self.entry_code_file_test.delete(0, tk.END)
            self.entry_code_file_test.insert(0, file)

    def load_input_file_test(self):
        file = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt *.in"), ("All Files", "*.*")])
        if file:
            try:
                content = Path(file).read_text(encoding="utf-8")
                self.text_input_test.delete(1.0, tk.END)
                self.text_input_test.insert(tk.END, content)
                self.log(f"Loaded input file: {Path(file).name}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read file: {e}")

    def do_submit_test(self):
        if not self.submitter: return

        code_path = self.entry_code_file_test.get().strip()
        lang = self.combo_lang_test.get()
        input_data = self.text_input_test.get(1.0, tk.END).strip()

        if not code_path:
            messagebox.showwarning("Warning", "Please select code file")
            return

        if not Path(code_path).exists():
            messagebox.showerror("Error", f"File not found: {code_path}")
            return

        try:
            code = Path(code_path).read_text(encoding="utf-8")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read code: {e}")
            return

        self.set_ui_state(False)
        self.log("---------- Starting test submit ----------")

        def _task():
            jid = self.submitter.submit_code_test(code, input_data, lang)
            if jid:
                self.submitter.poll_result(jid, callback_result=self.show_result_popup)

            self.root.after(0, lambda: self.set_ui_state(True))

        threading.Thread(target=_task, daemon=True).start()

    def on_submit_mode_change(self):
        mode = self.submit_mode_var.get()
        if mode == "editor":
            self.entry_code_file_problem.configure(state="disabled")
            self.btn_browse_code_problem.configure(state="disabled")
            self.log("Switched to editor mode")
        else:
            self.entry_code_file_problem.configure(state="normal")
            self.btn_browse_code_problem.configure(state="normal")
            self.log("Switched to file mode")

    def browse_code_problem(self):
        file = filedialog.askopenfilename(filetypes=[("Code Files", "*.cpp *.c *.py *.java"), ("All Files", "*.*")])
        if file:
            self.entry_code_file_problem.delete(0, tk.END)
            self.entry_code_file_problem.insert(0, file)

    def do_submit_problem(self):
        if not self.submitter: return

        problem_id = self.entry_problem_id.get().strip()
        if not problem_id:
            messagebox.showwarning("Warning", "Please enter problem ID")
            return

        problem_code = self.entry_problem_code.get().strip()
        self.submitter.problem_image_code = problem_code

        lang = self.combo_lang_problem.get()
        mode = self.submit_mode_var.get()

        if mode == "editor":
            if CODEBOX_AVAILABLE:
                code = self.code_editor.get("1.0", tk.END).strip()
            else:
                code = self.code_editor.get("1.0", tk.END).strip()
            is_file_input = False
        else:
            code_path = self.entry_code_file_problem.get().strip()
            if not code_path:
                messagebox.showwarning("Warning", "Please select code file")
                return
            if not Path(code_path).exists():
                messagebox.showerror("Error", f"File not found: {code_path}")
                return
            try:
                code = Path(code_path).read_text(encoding="utf-8")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read code: {e}")
                return
            is_file_input = True

        if not code:
            messagebox.showwarning("Warning", "Please enter or select code")
            return

        self.set_ui_state(False)
        self.log(f"---------- Starting problem {problem_id} submit ----------")

        def _task():
            jid = self.submitter.submit_problem_code(
                problem_id=problem_id,
                code=code,
                language=lang,
                is_file_input=is_file_input
            )
            if jid:
                self.parse_and_show_result(jid)

            self.root.after(0, lambda: self.set_ui_state(True))

        threading.Thread(target=_task, daemon=True).start()

    def parse_and_show_result(self, judge_id: int):
        """爬取评测结果 - 从HTML页面解析结果"""
        if not self.submitter:
            return

        # 爬取结果页面
        result_url = f"https://ke.kuding.cn/#/problems/submitInfo?id={judge_id}"
        self.log(f"Fetching result page (ID: {judge_id})...")

        def _poll_task():
            # 轮询爬取结果页面，减少次数避免长时间等待
            api_401_count = 0  # 记录 API 401 错误次数

            for attempt in range(1, 31):  # 最多30次，每次等待2秒（总共60秒）
                try:
                    # 直接爬取HTML页面
                    html_result = self._fetch_result_from_html(judge_id)
                    if html_result:
                        return html_result

                    # 如果返回None且是API 401错误，不再重试
                    if getattr(self, '_last_api_401', False):
                        api_401_count += 1
                        if api_401_count >= 2:
                            self.log("API返回401，认证失败。请检查Cookie和Token是否有效。")
                            self.log(f"Check manually: {result_url}")
                            return None

                    # 还没结果，等待后重试
                    if attempt < 30:
                        time.sleep(2)
                        if attempt % 5 == 1:  # 每5次显示一次
                            self.log(f"Waiting for result... (attempt {attempt})")

                except Exception as e:
                    self.log(f"Poll error (attempt {attempt}): {e}")
                    time.sleep(2)

            self.log(f"Poll timeout - Result may still be processing")
            self.log(f"Check manually: {result_url}")
            return None

        def _on_complete(result_data):
            if result_data:
                self._display_judge_result(result_data)

        threading.Thread(target=lambda: _on_complete(_poll_task()), daemon=True).start()

    def _fetch_result_from_html(self, judge_id: int):
        """通过 API 轮询获取评测结果"""
        try:
            # 只调用 API（使用 Selenium 解密）
            result = self._fetch_with_requests(judge_id)
            if result:
                return result
            return None

        except Exception as e:
            self.log(f"Fetch error: {e}")
            return None

    def _save_debug_html(self, judge_id: int):
        """保存HTML到文件供调试"""
        try:
            if not self.submitter:
                return

            url = f"https://ke.kuding.cn/#/problems/submitInfo?id={judge_id}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Referer': 'https://ke.kuding.cn/',
            }

            response = self.submitter.session.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                filename = f"result_html_{judge_id}.html"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                self.log(f"HTML saved to: {filename} ({len(response.text)} chars)")
            else:
                self.log(f"Failed to save HTML: HTTP {response.status_code}")
        except Exception as e:
            self.log(f"Failed to save HTML: {e}")

    def _fetch_with_requests(self, judge_id: int):
        """使用 requests 直接获取 API 结果（不获取 HTML）"""
        try:
            if not self.submitter:
                self.log("No submitter available")
                return None

            # 只调用 API 端点
            api_url = f"https://courseadmin.kuding.cn/problem/judge/result?id={judge_id}"
            self.log(f"Fetching API: {api_url}")

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Referer': 'https://ke.kuding.cn/',
                'Origin': 'https://ke.kuding.cn',
            }

            # 添加 Token 认证（API 必需）
            if self.submitter.token:
                headers['authorization'] = f"Token {self.submitter.token}"
                self.log(f"Using Token: {self.submitter.token[:20]}...")
            else:
                self.log("Warning: No token available")

            response = self.submitter.session.get(api_url, headers=headers, timeout=10)
            self.log(f"API Response status: {response.status_code}")

            # 标记 API 401 错误
            if response.status_code == 401:
                self._last_api_401 = True
                self.log("API认证失败 (401) - 可能需要重新登录")
                return None

            if response.status_code == 200:
                try:
                    data = response.json()
                    # 只打印关键信息，避免日志过长
                    if isinstance(data, dict):
                        data_field = data.get('data', '')
                        if isinstance(data_field, str) and len(data_field) > 50:
                            self.log(f"API Response: code={data.get('code')}, data={data_field[:50]}...")
                        else:
                            self.log(f"API Response: {data}")
                    else:
                        self.log(f"API Response: {data}")

                    # 解析API返回的结果
                    if isinstance(data, dict):
                        result = self._parse_api_result(data, judge_id)
                        if result:
                            # 检查评测是否完成
                            if not result.get('done', True):
                                self.log("评测尚未完成，继续轮询...")
                                return None  # 返回 None 让轮询继续
                            return result
                except Exception as json_err:
                    self.log(f"API JSON parse error: {json_err}")

            return None

        except Exception as e:
            self.log(f"API fetch error: {e}")
            return None

    def _parse_api_result(self, data: dict, judge_id: int):
        """解析API返回的加密结果数据"""
        return decrypt_api_result(data)

    def _parse_result_html(self, html: str, judge_id: int):
        """解析结果页面的HTML"""
        self.log(f"Parsing HTML, length: {len(html)} chars")

        # 首先尝试直接匹配酷丁网站的结果格式
        # 用户提供的HTML: <span class="problemResultShow" style="background: rgb(103, 194, 58);">Accepted：100分</span>
        kuding_patterns = [
            r'<span[^>]*class="[^"]*problemResultShow[^"]*"[^>]*>\s*([^<]+?)\s*</span>',
            r'<div[^>]*class="[^"]*problemResultShow[^"]*"[^>]*>\s*([^<]+?)\s*</div>',
        ]

        for pattern in kuding_patterns:
            matches = re.findall(pattern, html, re.IGNORECASE | re.DOTALL)
            if matches:
                for match in matches:
                    match = match.strip()
                    # 清理多余的空白字符
                    match = re.sub(r'\s+', ' ', match)
                    self.log(f"Found Kuding result: '{match}'")
                    parsed = self._parse_kuding_result(match)
                    if parsed:
                        result_data = {"status": parsed, "score": self._extract_score(match), "source": "kuding_html"}
                        self.log(f"Parsed Kuding result: {parsed}")
                        return result_data

        # 尝试查找可能包含结果的JSON数据
        json_patterns = [
            (r'window\.__NUXT__\s*=\s*({.+?});\s*<\/script>', 'NUXT'),
            (r'window\.__INITIAL_STATE__\s*=\s*({.+?});', 'INITIAL_STATE'),
            (r'window\.state\s*=\s*({.+?});', 'state'),
            (r'__INITIAL_STATE__\s*=\s*({.+?});', 'INITIAL_STATE'),
            (r'<script\s+id\s*=\s*"__NEXT_DATA__"[^>]*>(.+?)</script>', 'NEXT_DATA'),
            (r'__INITIAL_STATE__\s*=\s*({.+?});\s*window', 'INITIAL_STATE'),
        ]

        for pattern, name in json_patterns:
            matches = re.findall(pattern, html, re.DOTALL)
            for match in matches:
                try:
                    json_str = match.strip()
                    json_str = re.sub(r'/\*.*?\*/', '', json_str, flags=re.DOTALL)
                    decoded = html_unescape(json_str)
                    data = json.loads(decoded)
                    self.log(f"Found {name} data in HTML")
                    result = self._extract_result_from_json(data, judge_id)
                    if result:
                        self.log("Extracted result from HTML JSON")
                        return result
                except Exception as parse_err:
                    self.log(f"Parse {name} failed: {parse_err}")

        # 尝试直接从HTML解析结果状态 - 更广泛的模式
        status_patterns = [
            # 匹配包含评测状态的span/div
            r'<(?:span|div)[^>]*class="[^"]*problemResultShow[^"]*"[^>]*>\s*([^<]*?(?:Accepted|Wrong Answer|Time Limit|Memory Limit|Compilation Error|Runtime Error|AC|WA|TLE|MLE|CE|RE)[^<]*?)\s*</(?:span|div)>',
            r'<(?:span|div)[^>]*>([^<]*?(?:Accepted|Wrong Answer|Time Limit Exceeded|Memory Limit Exceeded|Compilation Error|Runtime Error)[^<]*?(?:：|:)\s*\d+\s*分?[^<]*?)</(?:span|div)>',
            r'<span[^>]*class="[^"]*status[^"]*"[^>]*>\s*([^<]+?)\s*</span>',
            r'<div[^>]*class="[^"]*status[^"]*"[^>]*>\s*([^<]+?)\s*</div>',
            r'<span[^>]*class="[^"]*result[^"]*"[^>]*>\s*([^<]+?)\s*</span>',
            r'<div[^>]*class="[^"]*result[^"]*"[^>]*>\s*([^<]+?)\s*</div>',
            # 最后尝试直接搜索文本
            r'(Accepted[：:]\s*\d+\s*分?|Wrong Answer[：:]\s*\d+\s*分?|Time Limit Exceeded[：:]\s*\d+\s*分?|Memory Limit Exceeded[：:]\s*\d+\s*分?|Compilation Error[：:]\s*\d+\s*分?|Runtime Error[：:]\s*\d+\s*分?)',
            r'(Accepted|Wrong Answer|Time Limit Exceeded|Memory Limit Exceeded|Compilation Error|Runtime Error|Judging|Pending)'
        ]

        combined_results = {}
        for pattern in status_patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[-1] if match[-1] else match[0]
                match = match.strip()
                match = html_unescape(match)
                match = re.sub(r'\s+', ' ', match)  # 清理多余空白
                if match and match not in ['&nbsp;', '', '\n', '\t']:
                    parsed = self._parse_kuding_result(match)
                    if parsed:
                        match = parsed
                    if match not in combined_results:
                        combined_results[match] = 0
                    combined_results[match] += 1

        if combined_results:
            status = max(combined_results.keys(), key=lambda k: combined_results[k])
            result_data = {"status": status, "source": "browser_parse", "all_found": list(combined_results.keys())}
            self.log(f"Found status in HTML: {status}, all: {combined_results}")
            return result_data

        self.log("No judge result found in HTML page")
        return None

    def _extract_score(self, text: str) -> int:
        """从结果文本中提取分数"""
        score_match = re.search(r'(\d+)\s*分', text)
        if score_match:
            return int(score_match.group(1))
        return 0

    def _parse_kuding_result(self, text: str) -> str:
        """解析酷丁网站的结果格式，如 'Accepted：100分' -> 'Accepted (100分)'"""
        if not text:
            return text

        # 匹配 "状态：分数分" 或 "状态：分数" 格式
        # 例如: "Accepted：100分" 或 "Wrong Answer：0分"
        patterns = [
            r'(Accepted|Wrong Answer|Time Limit Exceeded|Memory Limit Exceeded|Compilation Error|Runtime Error|AC|WA|TLE|MLE|CE|RE)[：:]\s*(\d+)\s*分?',
            r'(Accepted|Wrong Answer|Time Limit Exceeded|Memory Limit Exceeded|Compilation Error|Runtime Error|AC|WA|TLE|MLE|CE|RE)[：:]\s*([^：]+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                status = match.group(1)
                if match.lastindex >= 2:
                    extra = match.group(2)
                    # 如果extra是数字，添加"分"后缀
                    if extra.isdigit():
                        return f"{status} ({extra}分)"
                    else:
                        return f"{status}: {extra}"
                return status

        return text

    def _extract_result_from_json(self, data, judge_id: int):
        """从JSON数据中递归提取评测结果"""
        if isinstance(data, dict):
            # 检查是否包含评测结果的关键字段
            if any(k in data for k in ["status", "result", "score", "cases", "test_cases", "compile_err", "runtime_err"]):
                # 验证这个数据是相关的
                if "status" in data or "result" in data:
                    return data

            # 递归查找
            for v in data.values():
                result = self._extract_result_from_json(v, judge_id)
                if result:
                    return result

        elif isinstance(data, list):
            for item in data:
                result = self._extract_result_from_json(item, judge_id)
                if result:
                    return result

        return None

    def _display_judge_result(self, data: dict):
        """显示评测结果数据"""
        # 总体状态
        status = data.get("status", "Unknown")
        status_map = {
            "AC": "Accepted",
            "WA": "Wrong Answer",
            "TLE": "Time Limit Exceeded",
            "MLE": "Memory Limit Exceeded",
            "CE": "Compilation Error",
            "RE": "Runtime Error"
        }
        status_text = status_map.get(status, status)
        self.log(f"Overall result: {status_text}")

        # 编译错误
        compile_err = data.get("compile_err", "")
        if compile_err:
            self.log(f"Compilation Error:\n{compile_err}")

        # 运行错误
        runtime_err = data.get("runtime_err", "")
        if runtime_err:
            self.log(f"Runtime Error:\n{runtime_err}")

        # 测试点列表
        test_cases = data.get("cases", [])
        if test_cases:
            self.log(f"Test cases ({len(test_cases)}):")
            for idx, case in enumerate(test_cases[:10], start=1):
                case_status = case.get("status", "Unknown")
                case_time = case.get("time", "N/A")
                case_memory = case.get("memory", "N/A")
                case_output = case.get("output", "")

                self.log(f"  Case {idx}: {case_status}, time={case_time}ms, memory={case_memory}KB")
                if case_output and case_status not in ["AC", "Accepted"]:
                    self.log(f"    Output: {case_output[:100]}")
        else:
            # 如果没有cases，尝试解析详细输出
            output = data.get("output", "")
            if output:
                self.log(f"Program Output:\n{output}")

    def show_result_popup(self, res, out, err):
        msg = f"Judge result: {res}"
        if res == "Accepted":
            messagebox.showinfo("Complete", f"{msg}\n\nFull output shown in log")
        else:
            detail = ""
            if err: detail += f"\n\nCompile error:\n{err[:200]}"
            messagebox.showwarning("Complete", msg + detail + "\n\nFull output shown in log")


def main():
    root = ctk.CTk()
    app = KudingGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
