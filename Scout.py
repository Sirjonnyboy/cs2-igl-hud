import os
import json
import requests
import webbrowser
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

# ==========================================
# 1. SETUP & CONFIGURATION
# ==========================================
CONFIG_FILE = "scout_config.json"
MASTER_SERVER_URL = ""

def load_saved_ip():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                return data.get("master_ip", "")
        except:
            return ""
    return ""

def save_ip(ip):
    with open(CONFIG_FILE, "w") as f:
        json.dump({"master_ip": ip}, f)

def test_connection(url, timeout=2):
    """Test if the master server is reachable."""
    try:
        response = requests.get(f"{url}/data", timeout=timeout)
        return response.status_code == 200
    except:
        return False

def setup_networking():
    global MASTER_SERVER_URL
    os.system('cls' if os.name == 'nt' else 'clear')
    
    print("============================================================")
    print(" 🕵️ CS2 SCOUT INITIALIZATION ")
    print("============================================================")
    
    saved_ip = load_saved_ip()
    target_ip = ""
    
    if saved_ip:
        print(f" > Saved IGL IP Address: {saved_ip}")
        choice = input(" > Is this IP still correct? (Y/N): ").strip().lower()
        
        if choice == 'y' or choice == '':
            target_ip = saved_ip
        else:
            saved_ip = "" # Force them to type a new one
            print("------------------------------------------------------------")
            
    if not saved_ip:
        while True:
            print(" [!] We need your Master Server IP Address.")
            new_ip = input(" > Enter IP (e.g., 100.10.20.30): ").strip()
            
            if new_ip:
                # Foolproof cleanup: Just in case they copy/paste the "http://" or port by accident
                new_ip = new_ip.replace("http://", "").replace("https://", "").replace(":22222", "").replace("/", "")
                target_ip = new_ip
                save_ip(target_ip)
                print(f"\n [+] IP Successfully Saved: {target_ip}")
                break
            else:
                print(" [!] You cannot leave this blank. Please try again.")

    # Build the final URL that the script will use to send data
    MASTER_SERVER_URL = f"http://{target_ip}:22222"
    
    # Test connection to master server
    print("\n [*] Testing connection to master server...")
    if test_connection(MASTER_SERVER_URL):
        print(" [+] Successfully connected to master server!")
        return True
    else:
        print(" [!] ERROR: Could not connect to master server.")
        print(f" [!] Server IP is either wrong, or the master server has not started yet.")
        print(f" [!] Attempted to connect to: {MASTER_SERVER_URL}")
        input(" > Press Enter to exit and try again...")
        return False


# ==========================================
# 2. THE GSI FORWARDER
# ==========================================
class GSIForwarder(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass 

    def do_POST(self):
        length = int(self.headers['Content-Length'])
        body = self.rfile.read(length)
        payload = json.loads(body.decode('utf-8'))

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        try:
            requests.post(MASTER_SERVER_URL, json=payload, timeout=0.5)
        except requests.exceptions.RequestException:
            pass 

def run_scout():
    if not setup_networking():
        # Connection failed
        return
    
    server_address = ('127.0.0.1', 22222)
    httpd = HTTPServer(server_address, GSIForwarder)
    
    os.system('cls' if os.name == 'nt' else 'clear')
    print("============================================================")
    print(" 🕵️ CS2 SCOUT SCRIPT ACTIVE! ")
    print("============================================================")
    print(" Game data is being silently forwarded to your IGL.")
    print(f" Target Server : {MASTER_SERVER_URL}")
    print(" Status        : 🟢 ONLINE")
    print("------------------------------------------------------------")
    print(" DO NOT CLOSE THIS WINDOW WHILE PLAYING!")
    print("============================================================\n")
    
    # Auto-open the master server HUD webpage after a short delay
    try:
        print(" [*] Opening IGL HUD webpage in your browser...")
        time.sleep(1)
        webbrowser.open(MASTER_SERVER_URL)
        print(" [+] Webpage opened!")
    except Exception as e:
        print(f" [!] Could not open webpage automatically: {e}")
        print(f" [!] Please visit manually: {MASTER_SERVER_URL}")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()

if __name__ == '__main__':
    run_scout()