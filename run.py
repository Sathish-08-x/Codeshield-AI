import uvicorn
import webbrowser
import threading
import time

def open_browser():
    time.sleep(1.2)
    webbrowser.open("http://127.0.0.1:8000")

if __name__ == "__main__":
    print("=" * 60)
    print("  🛡️  CODESHIELD AI - AI Code Detector & Humanizer v2.0")
    print("  🌐  Web Server: http://127.0.0.1:8000")
    print("  💾  Database: SQLite (code_detector.db)")
    print("=" * 60)
    
    threading.Thread(target=open_browser, daemon=True).start()
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
