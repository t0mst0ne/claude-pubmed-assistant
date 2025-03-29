#!/usr/bin/env python3
"""
Claude PubMed 助手啟動腳本
"""

import os
import sys
import subprocess
import webbrowser
import time
import platform
from dotenv import load_dotenv

# 加載環境變量
load_dotenv()

# 配置
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))
DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "t")

def check_dependencies():
    """檢查必要的依賴是否已安裝"""
    required = ["flask", "httpx", "python-dotenv"]
    missing = []
    
    # 直接嘗試導入模塊
    for package in required:
        try:
            module_name = package.replace('-', '_')
            if module_name == "python_dotenv":
                module_name = "dotenv"
            __import__(module_name)
        except ImportError:
            missing.append(package)
    
    if missing:
        print("缺少以下依賴項：")
        for package in missing:
            print(f"  - {package}")
        print("\n請安裝這些依賴項：")
        print(f"pip install {' '.join(missing)}")
        print("\n安裝後，請再次運行此腳本。")
        return False
    
    return True

def start_server():
    """啟動PubMed服務器"""
    try:
        # 啟動服務器
        print(f"\n啟動 Claude PubMed 助手服務器...")
        print(f"服務器地址: http://{HOST}:{PORT}")
        
        # 打印調用命令
        cmd = [sys.executable, "pubmed_server.py"]
        print(f"執行命令: {' '.join(cmd)}")
        
        # 在Windows上，使用不同的方法啟動進程
        proc = None
        if platform.system() == "Windows":
            try:
                from subprocess import CREATE_NEW_CONSOLE
                proc = subprocess.Popen(cmd, creationflags=CREATE_NEW_CONSOLE)
                print("在新的終端視窗開啟伺服器")
            except Exception as e:
                print(f"創建獨立窗口出錯，使用標準模式: {e}")
                proc = subprocess.Popen(cmd)
        else:
            # 創建一個永不結束的進程
            proc = subprocess.Popen(cmd)
        
        # 等待服務器啟動
        print("等待服務器啟動...")
        max_retries = 5
        retry_count = 0
        
        while retry_count < max_retries:
            time.sleep(1)
            try:
                # 檢查服務器是否已啟動
                import urllib.request
                urllib.request.urlopen(f"http://{HOST}:{PORT}")
                break  # 成功連接，跳出循環
            except Exception:
                retry_count += 1
                print(f"檢查服務器狀態... (第{retry_count}次嘗試)")
        
        # 自動打開瀏覽器
        print("自動開啟瀏覽器...")
        webbrowser.open(f"http://{HOST}:{PORT}")
        
        print("\n服務器已啟動！按 Ctrl+C 停止服務器")
        print("---------------------------------------")
        
        return proc
        
    except Exception as e:
        print(f"啟動服務器時出錯: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """主函數"""
    print("=" * 50)
    print("  Claude PubMed 助手啟動器")
    print("=" * 50)
    
    # 檢查依賴
    print("\n檢查依賴項...")
    if not check_dependencies():
        return
    
    # 啟動服務器
    proc = start_server()
    if proc:
        # 保持腳本運行，直到用戶按Ctrl+C
        try:
            while True:
                time.sleep(1)
                # 檢查子進程是否仍在運行
                if proc.poll() is not None:
                    print("\n伺服器進程已終止。返回代碼:", proc.returncode)
                    break
        except KeyboardInterrupt:
            print("\n用戶終止服務器...")
            # 嘗試終止子進程
            try:
                proc.terminate()
                proc.wait(timeout=5)
                print("服務器已停止")
            except Exception as e:
                print(f"停止服務器時出錯: {e}")

if __name__ == "__main__":
    main()
