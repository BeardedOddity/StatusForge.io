 ***StatusForge.io***

 
is a lightweight, self-hosted, Discord-less Rich Presence engine built for content creators and streamers.

StatusForge is a 100% local engine that scans your active windows, fetches high-fidelity metadata, and pushes it directly to OBS and Streamer.bot.

No cloud tethers. No bloated software. No data harvesting. Your status belongs to you.

**Security, Privacy & Anti-Cheat Safety**
I know gamers are cautious about what runs on their PCs. StatusForge is built to be the "Glass House" of gaming software: transparent and safe.

**Anti-Cheat Safe (Vanguard, EAC, BattlEye)**
StatusForge uses Passive Process Scanning. It functions exactly like the Windows Task Manager.

No Injection: It does NOT inject code into game processes.

No Hooking: It does NOT read game memory or modify game files.

Visibility: It is 100% safe for competitive titles like Valorant, Apex Legends, and Call of Duty.

**The "Sandbox" Guarantee**
Unlike standard .exe installers, StatusForge never asks for Administrator privileges.

It creates a Virtual Environment (venv)—a localized "sandbox" folder.

All dependencies live inside that folder.

Zero Trace: To uninstall, simply delete the folder. No registry bloat, no hidden background services left behind.

**Total Privacy**
Zero Telemetry: I don't track your playtime, your hardware, or your habits.

No "Phoning Home": There is no central StatusForge server. Your data stays on your machine.

Open Source: Every line of code is readable. Audit presence.py yourself to see exactly how your data is handled.

**Core Systems**
The Universal Scout: A cross-platform background scanner (Windows, macOS, Linux/Steam Deck) that monitors your active windows to detect what you're playing.

The Metadata Waterfall: A smart fetching system that grabs high-res cover art, genres, and release dates from RAWG, IGDB, SteamGridDB, and GOG.

The Master Vault: A local database that lets you manually rename games or "Exile" apps (like chrome.exe) so they are never tracked.

**One-Click Installation**
StatusForge features a Self-Healing Auto-Installer. You don't need to know how to code to use it.

Download & Extract the StatusForge folder.

Rename Config_Template.json to Config.json and add your API keys (found in the setup guide below).

Launch the Engine:

Windows: Double-click Launch StatusForge.vbs.

Linux/macOS: Run ./Start_Engine.sh.

What happens next? The launcher will detect if you are missing necessary files, automatically forge a virtual environment, install all dependencies, and then boot the engine silently in the background.

**The Dashboard**

Monitor the Scout: See real-time detection and playtime.

Generate OBS Widgets: Copy-paste secure URLs for Vertical or Horizontal overlays.

Edit the Vault: Click "Lock Into Vault" to override game art or titles manually.

Streamer.bot Sync: Enable auto_push in your config to have StatusForge update your Twitch/Kick category automatically.

**File Structure**
presence.py: The heart of the engine (Flask server & Scout).

Launch StatusForge.vbs: The silent, auto-installing launcher for Windows.

layouts/: Contains the HTML/CSS for your OBS Browser Sources.

Engine/vault.json: Your personal database of tracked and ignored games.

requirements.txt: A list of the Python libraries the engine needs to run.

Forged by the community, for the community. Stay Odd.
