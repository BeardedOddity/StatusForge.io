StatusForge (Discord-Less Rich Presence)
**A lightweight, cross-platform, self-hosted engine that tracks your active games and pushes them directly to Streamer.bot and OBS, completely bypassing Discord.**

Built with a "Right-to-Repair" philosophy: No bloated libraries, no cloud-tethering, and full local control.

Features
* **Universal Scout:** Automatically detects active windows on Windows, macOS, and Linux.
* **Metadata Waterfall:** Fetches high-res cover art and game info from RAWG, IGDB, SteamGrid, and GOG.
* **The Vault:** Manually override game titles, release dates, or banish unwanted apps (like `chrome.exe`) from ever being tracked.
* **Streamer.bot Integration:** Auto-pushes your detected game category to Twitch/Kick via Streamer.bot.
* **OBS Native:** Generates local, secure HTML URLs for vertical and horizontal OBS widgets.

Installation & Setup
1. **Clone the Repo** and navigate to the folder.
2. **Create a Virtual Environment:** `python -m venv venv`
3. **Install Dependencies:** * Windows: Run `Start_Engine.vbs` to auto-boot, or click "Run System Repair" in the Dashboard.
   * Mac/Linux: `source venv/bin/activate` then `pip install -r requirements.txt`. (Linux requires `sudo apt install xdotool`).
4. **Setup Config:** Rename `Config_Template.json` to `Config.json` and enter your API keys.

How to Use
1. Launch the Engine via `Start_Engine.vbs` (Windows) or `Start_Engine.sh` (Mac/Linux).
2. Open your browser or tablet to `http://localhost:5050/forge-dashboard` (replace `localhost` with your PC's local IP if using a tablet).
3. Generate an OBS layout link and add it as a Browser Source in OBS!
