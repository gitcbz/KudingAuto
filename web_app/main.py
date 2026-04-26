import sys
import os
import subprocess
import time
import threading
from pathlib import Path

try:
    import webview
    WEBVIEW_AVAILABLE = True
except ImportError:
    WEBVIEW_AVAILABLE = False

def start_flask_server():
    """在后台启动 Flask 服务器"""
    app_dir = Path(__file__).parent
    app_file = app_dir / 'app.py'

    subprocess.Popen(
        [sys.executable, str(app_file)],
        cwd=str(app_dir),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
    )

    # 等待服务器启动
    time.sleep(3)

def main():
    if not WEBVIEW_AVAILABLE:
        print("Error: pywebview is not installed")
        print("Install with: pip install pywebview")
        sys.exit(1)

    # 启动 Flask 服务器
    server_thread = threading.Thread(target=start_flask_server, daemon=True)
    server_thread.start()

    # 创建 WebView 窗口
    try:
        webview.create_window(
            title='Kuding Judge Helper v3.0',
            url='http://127.0.0.1:5000',
            width=1200,
            height=800,
            min_size=(800, 600),
            background_color='#ffffff'
        )
        webview.start(debug=False)
    except Exception as e:
        print(f"Error starting WebView: {e}")
        print("Trying with GTK backend...")
        try:
            webview.create_window(
                title='Kuding Judge Helper v3.0',
                url='http://127.0.0.1:5000',
                width=1200,
                height=800,
                min_size=(800, 600)
            )
            webview.start(debug=False, gui='gtk')
        except Exception as e2:
            print(f"Error: {e2}")
            sys.exit(1)

if __name__ == '__main__':
    main()
