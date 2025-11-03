"""
Main application file for PDF Content Bookmark Generator
"""

import webbrowser
from http.server import HTTPServer
import threading
import time

from handlers.request_handler import RequestHandler


def run_server(port=8083):
    """
    Run the HTTP server for the PDF Bookmark Generator
    """
    server_address = ('', port)
    httpd = HTTPServer(server_address, RequestHandler)
    print(f"服务器启动，访问地址: http://localhost:{port}")

    # 在单独的线程中尝试打开浏览器
    def open_browser():
        time.sleep(1)  # 等待服务器启动
        try:
            webbrowser.open(f"http://localhost:{port}")
        except Exception as e:
            print(f"无法自动打开浏览器: {e}")

    # 启动浏览器打开线程
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n服务器正在关闭...")
        httpd.shutdown()
        print("服务器已关闭")


if __name__ == '__main__':
    run_server()