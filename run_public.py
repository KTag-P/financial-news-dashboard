import subprocess
import time
import os
import sys
from pyngrok import ngrok

def run_streamlit():
    # Start streamlit in the background
    cmd = [sys.executable, "-m", "streamlit", "run", "app.py", "--server.headless", "true"]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return process

def start_ngrok():
    # Open a HTTP tunnel on the default port 8501
    # <NgrokTunnel: "http://<public_sub>.ngrok.io" -> "http://localhost:8501">
    try:
        public_url = ngrok.connect(8501).public_url
        return public_url
    except Exception as e:
        print(f"Error connecting ngrok: {e}")
        return None

if __name__ == "__main__":
    print("Starting Streamlit App...")
    streamlit_process = run_streamlit()
    
    print("Waiting for app to start...")
    time.sleep(5)
    
    print("Starting secure tunnel...")
    public_url = start_ngrok()
    
    if public_url:
        print("\n" + "="*50)
        print(f" SUCCESS! Your App is live on the internet:")
        print(f" {public_url}")
        print("="*50 + "\n")
        print("Share this URL to access from your phone.")
        print("Keep this window OPEN to keep the site running.")
        print("Press Ctrl+C to stop.")
    else:
        print("Failed to create tunnel. Ensure ngrok is authenticated if needed.")

    try:
        # Keep running
        streamlit_process.wait()
    except KeyboardInterrupt:
        print("Stopping...")
        ngrok.kill()
        streamlit_process.terminate()
