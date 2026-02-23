# 🐻 StatusForge 

**StatusForge** is a lightweight, self-hosted, Discord-less Rich Presence engine built for content creators and livestreamers. 

Tired of relying on Discord to broadcast what game you're playing? Built from the ground up with a "Right-to-Repair" philosophy, StatusForge is a 100% local engine that scans your active windows, fetches high-fidelity metadata, and pushes it directly to **OBS** and **Streamer.bot**. 

No cloud tethers. No bloated software. No data harvesting. You own your setup.

---

## ⚙️ How It Works (The Core Systems)

StatusForge operates using three main backend systems to keep your stream updated silently and automatically:

1. **The Universal Scout:** A cross-platform background scanner that monitors your active windows. It knows the difference between a background process and the game you are actually playing. It works natively on Windows, macOS, and Linux (including SteamOS for Steam Deck users).
2. **The Metadata Waterfall:** When the Scout detects a new game, the engine triggers a "waterfall" request to grab the highest quality cover art, release date, genre, and publisher. It checks **RAWG** first, falls back to **IGDB** and **SteamGridDB**, and finally checks **GOG** to ensure you always have art for your OBS widgets.
3. **The Master Vault:** The engine's memory. The Vault safely stores your customized game titles (e.g., changing "eldenring.exe" to "Elden Ring") and maintains your "Exile" list, ensuring nuisance apps like `chrome.exe` or `obs64.exe` are never tracked as games.

---

## 📁 File Structure Explained
Because we believe in transparent software, there are no hidden `.exe` installers or buried registry keys. Here is exactly what is inside the box:

* `presence.py`: The Master Engine. This Python script runs the Flask web server, the Scout, and the API requests. 
* `Config_Template.json`: The blank configuration file for your API keys and engine settings. 
* `Start_Engine.vbs` / `.sh`: Silent background launchers for Windows and Mac/Linux so you don't have to look at a terminal window while streaming.
* `Dashboard.html` & `Logic.js`: The frontend files that power your local control panel.
* `/layouts/`: This folder contains the raw HTML/CSS files for your OBS widgets (Vertical, Horizontal Left, Horizontal Right).
* `vault.json`: The cross-platform database that stores your Listed (tracked) and Delisted (ignored) apps.
* `Custom_Meta.json`: (Auto-generated) Stores any manual overrides you make to a game's cover art or release date.

---

## 🚀 Installation & Setup

### Step 1: Prepare the Environment
1. Clone or download this repository to your machine.
2. Open your terminal/command prompt inside the extracted `StatusForge` folder.
3. Create an isolated Virtual Environment so the engine doesn't clutter your PC's main Python installation:
   ```bash
   python -m venv venv