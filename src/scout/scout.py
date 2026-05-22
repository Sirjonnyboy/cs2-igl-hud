import os
import sys
import json
try:
    import requests
except ImportError:
    requests = None
import webbrowser
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

# ==========================================
# 1. SETUP & CONFIGURATION
# ==========================================


def get_app_base_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

CONFIG_FILE = os.path.join(get_app_base_dir(), "scout_config.json")
GSI_CFG_FILENAME = "gamestate_integration_python.cfg"
GSI_CFG_CONTENT = """\"Game State Integration\"
{
    "uri" "http://127.0.0.1:22222"
    "timeout" "5.0"
    "buffer"  "0.1"
    "throttle" "0.5"
    "heartbeat" "60.0"
    "data"
    {
        "provider"            "1"
        "map"                 "1"
        "round"               "1"
        "player_id"           "1"
        "player_state"        "1"
        "player_weapons"      "1"
        "player_match_stats"  "1"
    }
}"""

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
    if requests is None:
        print(" [!] Missing required package: requests")
        print(" [!] Install dependencies or rebuild the executable with requests available.")
        return False
    try:
        response = requests.get(f"{url}/data", timeout=timeout)
        return response.status_code == 200
    except:
        return False

def find_csgo_cfg_folder():
    # First try common Program Files locations
    for env_var in ("ProgramFiles(x86)", "ProgramFiles", "ProgramW6432"):
        root = os.environ.get(env_var)
        if not root:
            continue
        candidate = os.path.join(root, "Steam", "steamapps", "common", "Counter-Strike Global Offensive", "game", "csgo", "cfg")
        if os.path.isdir(candidate):
            return candidate

    # Try to detect which drive contains Steam (user may have Steam on D:, E:, etc.)
    def get_possible_steam_roots(drive):
        # Common Steam install roots on a given drive
        return [
            os.path.join(drive + ':', 'Program Files (x86)', 'Steam'),
            os.path.join(drive + ':', 'Program Files', 'Steam'),
            os.path.join(drive + ':', 'Steam'),
            os.path.join(drive + ':', 'Games', 'Steam'),
        ]

    def drive_has_steam(drive):
        for root in get_possible_steam_roots(drive):
            if os.path.isdir(os.path.join(root, 'steamapps')):
                return True
        return False

    # Check all local drive letters for Steam
    for letter in [chr(c) for c in range(ord('C'), ord('Z') + 1)]:
        try:
            if drive_has_steam(letter):
                candidate = os.path.join(letter + ':', 'Steam', 'steamapps', 'common', 'Counter-Strike Global Offensive', 'game', 'csgo', 'cfg')
                if os.path.isdir(candidate):
                    return candidate
        except Exception:
            continue

    return None


def prompt_for_cfg_folder():
    print(" [!] Could not locate the CS:GO cfg folder automatically.")
    print(" [!] If you know the CS:GO folder path, enter it below.")
    print(" [!] Example: C:\\Steam\\steamapps\\common\\Counter-Strike Global Offensive\\game\\csgo\\cfg")

    # Offer a quick drive-based lookup first
    def list_local_drives():
        drives = []
        for letter in [chr(c) for c in range(ord('C'), ord('Z') + 1)]:
            root = f"{letter}:\\"
            if os.path.isdir(root):
                drives.append(letter)
        return drives

    drives = list_local_drives()
    if drives:
        print(f" [*] Detected local drives: {' '.join(drives)}")
        drive_choice = input(" > If you know the drive letter where Steam is installed, enter it (e.g., D) or press Enter to skip: ").strip().upper()
        if drive_choice:
            if len(drive_choice) == 1 and drive_choice in drives:
                candidate = os.path.join(drive_choice + ':', 'Steam', 'steamapps', 'common', 'Counter-Strike Global Offensive', 'game', 'csgo', 'cfg')
                if os.path.isdir(candidate):
                    print(f" [*] Found CFG folder on drive {drive_choice}: {candidate}")
                    return candidate
                else:
                    print(f" [!] No CS2 cfg found on drive {drive_choice}. You can enter the full path below.")
            else:
                print(' [!] Invalid drive selection, falling back to manual path input.')

    folder = input(" > CS:GO cfg folder path (leave blank to skip): ").strip()
    if not folder:
        return None
    folder = os.path.normpath(folder)
    if os.path.isdir(folder):
        return folder
    print(f" [!] Folder does not exist: {folder}")
    return None


def ensure_gsi_cfg_exists(ask_if_missing=True):
    """Ensure the CS2 GSI cfg exists. If ask_if_missing is False, don't prompt the user."""
    if os.name != "nt":
        return None

    cfg_folder = find_csgo_cfg_folder()
    if not cfg_folder and ask_if_missing:
        cfg_folder = prompt_for_cfg_folder()
        if not cfg_folder:
            return None
    elif not cfg_folder:
        return None

    cfg_path = os.path.join(cfg_folder, GSI_CFG_FILENAME)
    if os.path.isfile(cfg_path):
        print(f" [*] Found existing GSI config: {cfg_path}")
        return cfg_path

    txt_path = os.path.join(cfg_folder, os.path.splitext(GSI_CFG_FILENAME)[0] + ".txt")
    if os.path.isfile(txt_path):
        print(" [!] Found a GSI config text file. Creating a proper .cfg file alongside it.")

    try:
        with open(cfg_path, "w", encoding="utf-8") as f:
            f.write(GSI_CFG_CONTENT)
        print(f" [+] Created GSI config: {cfg_path}")
        return cfg_path
    except Exception as e:
        print(f" [!] Could not create GSI config: {e}")
        return None


def setup_networking(master_ip=None, interactive=True):
    """Setup master server networking. If master_ip provided, use it. If interactive is False and master_ip is None, return False."""
    global MASTER_SERVER_URL

    if master_ip:
        target_ip = master_ip
        save_ip(target_ip)
    else:
        saved_ip = load_saved_ip()
        if saved_ip:
            if not interactive:
                target_ip = saved_ip
            else:
                print(f" > Saved IGL IP Address: {saved_ip}")
                choice = input(" > Is this IP still correct? (Y/N): ").strip().lower()
                if choice == 'y' or choice == '':
                    target_ip = saved_ip
                else:
                    saved_ip = ""
        if not master_ip and (not saved_ip or saved_ip == ""):
            if not interactive:
                return False
            while True:
                print(" [!] We need your Master Server IP Address.")
                new_ip = input(" > Enter IP (e.g., 100.10.20.30): ").strip()
                if new_ip:
                    new_ip = new_ip.replace("http://", "").replace("https://", "").replace(":22222", "").replace("/", "")
                    target_ip = new_ip
                    save_ip(target_ip)
                    print(f"\n [+] IP Successfully Saved: {target_ip}")
                    break
                else:
                    print(" [!] You cannot leave this blank. Please try again.")

    MASTER_SERVER_URL = f"http://{target_ip}:22222"

    if not interactive:
        return test_connection(MASTER_SERVER_URL)

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

        if requests is None:
            return

        try:
            requests.post(MASTER_SERVER_URL, json=payload, timeout=0.5)
        except requests.exceptions.RequestException:
            pass 

def run_scout(master_ip=None, interactive=True, open_browser=True):
    if requests is None:
        print(" [!] Cannot run Scout: missing dependency 'requests'.")
        print(" [!] Install requirements via 'pip install -r requirements.txt' or rebuild the executable with requests available.")
        return

    ensure_gsi_cfg_exists(ask_if_missing=interactive)
    if not setup_networking(master_ip=master_ip, interactive=interactive):
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

    # Auto-open the master server HUD webpage after a short delay (interactive only by default)
    if open_browser and interactive:
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