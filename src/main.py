import uvicorn
import webbrowser
import threading
import time

def open_browser():
    time.sleep(3)  # Give the server a second to start
    webbrowser.open("http://127.0.0.1:8000")

if __name__ == "__main__":
    threading.Thread(target=open_browser).start()
    uvicorn.run("simulator:app", host="127.0.0.1", port=8000)