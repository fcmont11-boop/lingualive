import subprocess
import threading
import time
import webbrowser
import os
import sys

if __name__ == "__main__":
    # Guard against re-launching
    if os.environ.get("TRANSLATOR_RUNNING"):
        sys.exit(0)
    os.environ["TRANSLATOR_RUNNING"] = "1"
    
    def open_browser():
        time.sleep(4)
        webbrowser.open("http://localhost:5001")

    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()

    os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
    subprocess.run([sys.executable, "server.py"])
