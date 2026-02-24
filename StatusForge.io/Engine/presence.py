import psutil, time, threading, json, logging, os, re, secrets, ctypes, webbrowser, platform, subprocess, sys
import urllib.request, urllib.parse
from logging.handlers import RotatingFileHandler
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LAYOUTS_DIR = os.path.join(BASE_DIR, 'layouts') 
CURRENT_OS = platform.system()

# --- LOGGING ---
LOG_PATH = os.path.join(BASE_DIR, 'debug.log')
log_handler = RotatingFileHandler(LOG_PATH, maxBytes=1024 * 1024, backupCount=1)
logging.basicConfig(handlers=[log_handler], level=logging.INFO, format='%(asctime)s | %(message)s', datefmt='%H:%M:%S')

app = Flask(__name__)
CORS(app)

class NoSpamFilter(logging.Filter):
    def filter(self, record):
        msg = record.getMessage()
        if ('GET /status' in msg or 'GET /logs' in msg) and ' 200 ' in msg: return False
        return True
logging.getLogger('werkzeug').addFilter(NoSpamFilter())
logging.getLogger('werkzeug').setLevel(logging.ERROR)

# --- CONFIG & STATE ---
status_data = {"is_playing": False, "game_title": "System Initializing...", "process_name": "", "start_time": 0, "cover_url": "", "release_date": "", "genre": "", "publisher": ""}
VAULT_PATH = os.path.join(BASE_DIR, "vault.json")
CUSTOM_META_PATH = os.path.join(BASE_DIR, "Custom_Meta.json")
TOKEN_PATH = os.path.join(BASE_DIR, "Widget_Token.txt")
# Config is expected in the parent directory (Root), above Engine folder
CONFIG_PATH = os.path.join(os.path.dirname(BASE_DIR), "Config.json")

if not os.path.exists(TOKEN_PATH):
    with open(TOKEN_PATH, 'w') as f: f.write(secrets.token_urlsafe(16))
with open(TOKEN_PATH, 'r') as f: WIDGET_TOKEN = f.read().strip()

def load_json(path, default):
    if not os.path.exists(path):
        with open(path, 'w') as f: json.dump(default, f, indent=4)
    with open(path, 'r') as f: return json.load(f)

def save_json(path, data):
    with open(path, 'w') as f: json.dump(data, f, indent=4)

# Initialize Universal Vault if empty
DEFAULT_VAULT = {"listed_apps": {}, "delisted_apps": ["chrome.exe", "obs64.exe", "pythonw.exe", "finder", "explorer.exe"]}
load_json(VAULT_PATH, DEFAULT_VAULT)

# Default Config Structure (Updated with widget_fade_timer)
DEFAULT_CONFIG = {
    "api_keys": {"rawg": "", "steamgrid": "", "igdb_client": "", "igdb_secret": "", "igdb_token": ""},
    "engine_settings": {"idle_category": "Just Chatting", "sb_port": 8080, "scan_interval": 5, "widget_poll_rate": 3, "safe_mode": False, "auto_push": False, "widget_fade_timer": 15}
}
load_json(CONFIG_PATH, DEFAULT_CONFIG)

# --- HELPER: CROSS-PLATFORM SCOUT ---
def get_active_window_info():
    try:
        if CURRENT_OS == "Windows":
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            if not hwnd: return None, None
            length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
            buff = ctypes.create_unicode_buffer(length + 1)
            ctypes.windll.user32.GetWindowTextW(hwnd, buff, length + 1)
            window_title = buff.value.strip()
            pid = ctypes.c_ulong()
            ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            if pid.value > 0: return window_title, psutil.Process(pid.value).name()
        elif CURRENT_OS == "Darwin":
            script = 'tell application "System Events" to get name of first application process whose frontmost is true'
            proc_name = subprocess.check_output(['osascript', '-e', script]).decode().strip()
            return proc_name, proc_name
        elif CURRENT_OS == "Linux":
            wid = subprocess.check_output(['xdotool', 'getactivewindow']).decode().strip()
            title = subprocess.check_output(['xdotool', 'getwindowname', wid]).decode().strip()
            pid = subprocess.check_output(['xdotool', 'getwindowpid', wid]).decode().strip()
            return title, psutil.Process(int(pid)).name()
    except: return None, None
    return None, None

# --- API ROUTES ---
@app.route('/')
@app.route('/dashboard')
@app.route('/forge-dashboard') 
def serve_dashboard(): return send_from_directory(BASE_DIR, 'Dashboard.html')

@app.route('/layouts/<path:filename>')
def serve_layout(filename): return send_from_directory(LAYOUTS_DIR, filename)

@app.route('/Logic.js')
def serve_logic(): return send_from_directory(BASE_DIR, 'Logic.js')

@app.route('/forge-widget/<token>/<path:filename>')
def serve_secure_widget(token, filename):
    if token != WIDGET_TOKEN: return "Unauthorized Token", 401
    return send_from_directory(BASE_DIR, filename)
    
@app.route('/status')
def get_status():
    missing_deps = []
    if CURRENT_OS == "Linux" and subprocess.run(["which", "xdotool"], capture_output=True).returncode != 0: missing_deps.append("xdotool")
    
    # Load config to grab the live widget fade timer
    config = load_json(CONFIG_PATH, DEFAULT_CONFIG)
    fade_time = config.get("engine_settings", {}).get("widget_fade_timer", 15)
    
    payload = status_data.copy()
    payload["system_info"] = {"os": CURRENT_OS, "active_path": BASE_DIR.replace("\\", "/"), "missing_deps": missing_deps}
    payload["fade_timer"] = fade_time # Pass to the widget!
    
    return jsonify(payload)

@app.route('/get-token')
def get_token(): return jsonify({"token": WIDGET_TOKEN})

@app.route('/list', methods=['POST'])
def list_app():
    data = request.json
    title = data['title']
    vault = load_json(VAULT_PATH, DEFAULT_VAULT)
    
    if data.get('process'):
        vault["listed_apps"][data['process'].lower()] = title
        save_json(VAULT_PATH, vault)
        
    vault_key = title.lower().strip()
    if any([data.get('custom_url'), data.get('custom_release'), data.get('custom_genre'), data.get('custom_publisher')]):
        meta_vault = load_json(CUSTOM_META_PATH, {})
        if vault_key not in meta_vault: meta_vault[vault_key] = {}
        if data.get('custom_url'): meta_vault[vault_key]['url'] = data['custom_url']
        if data.get('custom_release'): meta_vault[vault_key]['release'] = data['custom_release']
        if data.get('custom_genre'): meta_vault[vault_key]['genre'] = data['custom_genre']
        if data.get('custom_publisher'): meta_vault[vault_key]['publisher'] = data['custom_publisher']
        save_json(CUSTOM_META_PATH, meta_vault)
        
    if status_data.get("game_title", "").lower().strip() == vault_key:
        threading.Thread(target=fetch_metadata, args=(status_data["game_title"],), daemon=True).start()
    return jsonify({"status": "success"})

@app.route('/delist', methods=['POST'])
def delist_app():
    proc_name = request.json.get('process')
    if proc_name:
        vault = load_json(VAULT_PATH, DEFAULT_VAULT)
        clean_proc = proc_name.lower().strip()
        if clean_proc not in vault["delisted_apps"]:
            vault["delisted_apps"].append(clean_proc)
            save_json(VAULT_PATH, vault)
            logging.info(f"[EXILE] Process banished: {clean_proc}")
    return jsonify({"status": "success"})

@app.route('/logs')
def get_logs():
    try:
        with open(LOG_PATH, 'r') as f: return jsonify({"logs": f.readlines()[-20:]})
    except: return jsonify({"logs": []})

@app.route('/clear-logs', methods=['POST'])
def clear_logs():
    with open(LOG_PATH, 'w') as f: f.write("System logs purged.\n")
    return jsonify({"status": "success"})

@app.route('/settings', methods=['GET', 'POST'])
def manage_settings():
    current_config = load_json(CONFIG_PATH, DEFAULT_CONFIG)
    if request.method == 'POST':
        data = request.json
        current_config["engine_settings"]["auto_push"] = data.get("auto_push", False)
        current_config["engine_settings"]["safe_mode"] = data.get("safe_mode", False)
        current_config["engine_settings"]["idle_category"] = data.get("idle_category", "Just Chatting")
        current_config["engine_settings"]["sb_port"] = data.get("sb_port", 8080)
        current_config["engine_settings"]["widget_poll_rate"] = data.get("widget_poll_rate", 3)
        current_config["engine_settings"]["widget_fade_timer"] = data.get("widget_fade_timer", 15) # Saves the new timer!
        
        current_config["api_keys"]["rawg"] = data.get("rawg_key", "")
        current_config["api_keys"]["steamgrid"] = data.get("sgdb_key", "")
        current_config["api_keys"]["igdb_client"] = data.get("igdb_client", "")
        current_config["api_keys"]["igdb_secret"] = data.get("igdb_secret", "")
        save_json(CONFIG_PATH, current_config)
        return jsonify({"status": "success"})
    
    # Flatten structure for dashboard compatibility
    flat_data = {**current_config["engine_settings"]}
    flat_data["rawg_key"] = current_config["api_keys"].get("rawg", "")
    flat_data["sgdb_key"] = current_config["api_keys"].get("steamgrid", "")
    flat_data["igdb_client"] = current_config["api_keys"].get("igdb_client", "")
    flat_data["igdb_secret"] = current_config["api_keys"].get("igdb_secret", "")
    return jsonify(flat_data)

@app.route('/push-stream', methods=['POST'])
def push_stream():
    data = request.json
    config = load_json(CONFIG_PATH, DEFAULT_CONFIG)
    settings = config.get("engine_settings", {})
    category = data.get('category') or status_data.get('game_title', settings.get("idle_category", "Just Chatting"))
    sb_port = settings.get("sb_port", 8080)
    
    if settings.get("safe_mode", False): return jsonify({"status": "success", "note": "Safe mode active"})
    payload = { "action": { "name": "UpdateCategory" }, "args": { "category": category } }
    try:
        req = urllib.request.Request(f'http://127.0.0.1:{sb_port}/DoAction', data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'}, method='POST')
        urllib.request.urlopen(req, timeout=2)
        return jsonify({"status": "success"})
    except: return jsonify({"error": "unreachable"}), 500

@app.route('/shutdown', methods=['POST'])
def shutdown_engine():
    threading.Timer(1.0, lambda: os._exit(0)).start()
    return jsonify({"status": "success"})

@app.route('/repair-engine', methods=['POST'])
def repair_engine():
    def run_repair():
        logging.info(f"[MAINTENANCE] Repairing {CURRENT_OS} dependencies...")
        py_deps = [sys.executable, "-m", "pip", "install", "flask", "flask-cors", "requests", "pillow", "psutil", "pyyaml"]
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
            subprocess.check_call(py_deps)
            if CURRENT_OS == "Windows": subprocess.check_call([sys.executable, "-m", "pip", "install", "pywin32"])
            elif CURRENT_OS == "Linux": 
                subprocess.check_call(["sudo", "apt", "update"])
                subprocess.check_call(["sudo", "apt", "install", "-y", "xdotool"])
            elif CURRENT_OS == "Darwin" and subprocess.run(["which", "brew"], capture_output=True).returncode == 0:
                subprocess.check_call(["brew", "install", "terminal-notifier"])
            logging.info(f"🏁 System Core Repaired for {CURRENT_OS}.")
        except Exception as e: logging.error(f"❌ Repair failed: {e}")
    threading.Thread(target=run_repair, daemon=True).start()
    return jsonify({"status": "Repair initiated"})

# --- METADATA WATERFALL ---
def fetch_metadata(title):
    global status_data
    config = load_json(CONFIG_PATH, DEFAULT_CONFIG)
    keys = config.get("api_keys", {})
    rawg, sgdb = keys.get("rawg", ""), keys.get("steamgrid", "")
    igdb_c, igdb_s, igdb_t = keys.get("igdb_client", ""), keys.get("igdb_secret", ""), keys.get("igdb_token", "")
    
    status_data.update({"cover_url": "", "release_date": "", "genre": "", "publisher": ""})
    vault_key = title.lower().strip()
    meta_vault = load_json(CUSTOM_META_PATH, {})
    
    if vault_key in meta_vault:
        v = meta_vault[vault_key]
        for field in ['url', 'release', 'genre', 'publisher']:
            if v.get(field): status_data[field if field != 'url' else 'cover_url'] = v[field]
    
    safe_title = urllib.parse.quote(title)
    if rawg and not status_data["cover_url"]:
        try:
            req = urllib.request.Request(f"https://api.rawg.io/api/games?key={rawg}&search={safe_title}&page_size=1")
            with urllib.request.urlopen(req, timeout=3) as res:
                game = json.loads(res.read().decode())["results"][0]
                status_data["cover_url"] = game.get("background_image")
                status_data["release_date"] = game.get("released", "").split('-')[0]
                status_data["genre"] = game["genres"][0]["name"].upper()
        except: pass

    # IGDB LOGIC
    if igdb_c and igdb_s and (not status_data.get("cover_url") or not status_data.get("release_date")):
        def do_igdb_fetch(token):
            body = f'search "{title}"; fields cover.url,first_release_date,genres.name,involved_companies.company.name; limit 1;'.encode('utf-8')
            req = urllib.request.Request("https://api.igdb.com/v4/games", data=body, headers={'Client-ID': igdb_c, 'Authorization': f'Bearer {token}', 'Accept': 'application/json'}, method='POST')
            with urllib.request.urlopen(req, timeout=3) as res:
                data = json.loads(res.read().decode())
                if data:
                    game = data[0]
                    if not status_data.get("cover_url") and game.get("cover"): status_data["cover_url"] = f"https:{game['cover']['url'].replace('t_thumb', 't_1080p')}"
                    if not status_data.get("release_date") and game.get("first_release_date"): status_data["release_date"] = time.strftime('%Y', time.gmtime(game["first_release_date"]))
                    if not status_data.get("genre") and game.get("genres"): status_data["genre"] = game["genres"][0]["name"].upper()
                    if not status_data.get("publisher") and game.get("involved_companies"): status_data["publisher"] = game["involved_companies"][0]["company"]["name"].upper()

        try:
            if not igdb_t: raise ValueError("No token exists.")
            do_igdb_fetch(igdb_t)
        except Exception as e:
            if isinstance(e, ValueError) or (hasattr(e, 'code') and e.code in [401, 403]):
                logging.info("[WATERFALL] IGDB Token missing or expired. Forging a new one...")
                try:
                    tok_url = "https://id.twitch.tv/oauth2/token"
                    tok_data = urllib.parse.urlencode({'client_id': igdb_c, 'client_secret': igdb_s, 'grant_type': 'client_credentials'}).encode('utf-8')
                    tok_req = urllib.request.Request(tok_url, data=tok_data, method='POST')
                    with urllib.request.urlopen(tok_req, timeout=3) as tok_res:
                        new_token = json.loads(tok_res.read().decode()).get('access_token')
                        if new_token:
                            config["api_keys"]["igdb_token"] = new_token
                            save_json(CONFIG_PATH, config) 
                            do_igdb_fetch(new_token) 
                except Exception as ex: logging.warning(f"[WATERFALL] IGDB Auto-Forge failed: {ex}")

    # SGDB LOGIC
    if sgdb and not status_data.get("cover_url"):
        try:
            req = urllib.request.Request(f"https://www.steamgriddb.com/api/v2/search/autocomplete/{safe_title}", headers={'Authorization': f'Bearer {sgdb}'})
            with urllib.request.urlopen(req, timeout=3) as res:
                data = json.loads(res.read().decode())
                if data.get("data"):
                    game_id = data["data"][0]["id"]
                    req2 = urllib.request.Request(f"https://www.steamgriddb.com/api/v2/grids/game/{game_id}?dimensions=600x900", headers={'Authorization': f'Bearer {sgdb}'})
                    with urllib.request.urlopen(req2, timeout=3) as res2:
                        data2 = json.loads(res2.read().decode())
                        if data2.get("data"): status_data["cover_url"] = data2["data"][0]["url"]
        except: pass

    # GOG LOGIC
    if not status_data.get("cover_url") or not status_data.get("publisher"):
        try:
            req = urllib.request.Request(f"https://embed.gog.com/games/ajax/filtered?mediaType=game&search={safe_title}")
            with urllib.request.urlopen(req, timeout=3) as res:
                data = json.loads(res.read().decode())
                if data.get("products"):
                    game = data["products"][0]
                    if not status_data.get("cover_url") and game.get("image"): status_data["cover_url"] = f"https:{game['image']}_glx_600.jpg"
                    if not status_data.get("publisher") and game.get("publisher"): status_data["publisher"] = game["publisher"].upper()
                    if not status_data.get("genre") and game.get("category"): status_data["genre"] = game["category"].upper()
        except: pass

    if not status_data.get("cover_url"): status_data["cover_url"] = ""
    if not status_data.get("release_date"): status_data["release_date"] = "UNKNOWN"
    if not status_data.get("genre"): status_data["genre"] = "GAMING"
    if not status_data.get("publisher"): status_data["publisher"] = "INDIE"
    logging.info(f"[WATERFALL] Metadata locked: {title}")

# --- SCANNER ---
def monitor_games():
    global status_data
    config = load_json(CONFIG_PATH, DEFAULT_CONFIG)
    settings = config.get("engine_settings", {})
    idle_cat = settings.get("idle_category", "Just Chatting")
    sb_port = settings.get("sb_port", 8080)
    
    status_data.update({"game_title": idle_cat, "is_playing": False})
    missed_scans = 0 
    
    while True:
        # Load from Universal Vault
        vault = load_json(VAULT_PATH, DEFAULT_VAULT)
        listed_lower_map = vault.get("listed_apps", {})
        delisted = vault.get("delisted_apps", [])
        
        # SCOUTING
        window_title, active_exe = get_active_window_info()
        if window_title and active_exe:
            active_lower = active_exe.lower()
            core_ignores = ['explorer.exe', 'cmd.exe', 'terminal', 'iterm2', 'finder', 'dock', 'systemsettings', 'taskmgr.exe']
            if active_lower not in delisted and active_lower not in core_ignores and active_lower not in listed_lower_map:
                vault["listed_apps"][active_lower] = window_title
                save_json(VAULT_PATH, vault)
                listed_lower_map[active_lower] = window_title # update local map immediately
                logging.info(f"[AUTO-FORGE] {CURRENT_OS} Scout: {window_title} ({active_exe})")

        # PROCESS SCANNER
        found = False
        for proc in psutil.process_iter(['name']):
            try:
                name_lower = proc.info['name'].lower()
                if name_lower in delisted: continue
                if name_lower in listed_lower_map:
                    found = True
                    missed_scans = 0
                    if not status_data["is_playing"] or status_data["process_name"] != proc.info['name']:
                        game_title = listed_lower_map[name_lower]
                        status_data.update({"is_playing": True, "game_title": game_title, "process_name": proc.info['name'], "start_time": time.time()})
                        logging.info(f"[SCANNER] Found: {game_title}")
                        threading.Thread(target=fetch_metadata, args=(game_title,), daemon=True).start()
                        
                        # Re-load config in case safe mode changed
                        current_settings = load_json(CONFIG_PATH, DEFAULT_CONFIG).get("engine_settings", {})
                        if current_settings.get("auto_push", False) and not current_settings.get("safe_mode", False):
                            try:
                                payload = { "action": { "name": "UpdateCategory" }, "args": { "category": game_title } }
                                req = urllib.request.Request(f'http://127.0.0.1:{current_settings.get("sb_port", 8080)}/DoAction', data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'}, method='POST')
                                urllib.request.urlopen(req, timeout=2)
                            except: pass
                    break
            except: continue
        
        if not found and status_data["is_playing"]:
            missed_scans += 1
            if missed_scans >= 8:
                status_data.update({"is_playing": False, "game_title": idle_cat, "process_name": "", "start_time": 0})
                logging.info(f"[SCANNER] Reverting: {idle_cat}")
                
                current_settings = load_json(CONFIG_PATH, DEFAULT_CONFIG).get("engine_settings", {})
                if current_settings.get("auto_push", False) and not current_settings.get("safe_mode", False):
                    try:
                        payload = { "action": { "name": "UpdateCategory" }, "args": { "category": idle_cat } }
                        req = urllib.request.Request(f'http://127.0.0.1:{current_settings.get("sb_port", 8080)}/DoAction', data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'}, method='POST')
                        urllib.request.urlopen(req, timeout=2)
                    except: pass
        
        time.sleep(load_json(CONFIG_PATH, DEFAULT_CONFIG).get("engine_settings", {}).get("scan_interval", 5))

if __name__ == '__main__':
    threading.Thread(target=monitor_games, daemon=True).start()
    threading.Timer(1.5, lambda: webbrowser.open("http://localhost:5050/dashboard")).start()
    app.run(host='0.0.0.0', port=5050)
