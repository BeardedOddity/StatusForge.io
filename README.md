# ⚒️ The Forge Database (Community Metadata)

Welcome to the master data vault for **StatusForge.io**. This branch is strictly dedicated to storing the unified game metadata, custom cover art, and platform IDs that power the engine.

Because StatusForge is local-first, the engine relies on a `Forge_Database.json` file to identify obscure indie games, map compilation titles, and pull high-fidelity vertical cover art. 

## 🤝 How to Contribute your Games

If you play a game that the public APIs struggle to find, or if you found a much better vertical cover art URL, you can submit it here so the rest of the community can use it!

1. Open your local StatusForge app and navigate to **⚒️ The Forge**.
2. Lock your game, custom cover art, and IDs into your local database.
3. Click **📥 EXPORT DATABASE** to get your local `Forge_Database.json`.
4. Submit a **Pull Request (PR)** to this branch, uploading your updated `.json` file.

*Note: I (BearddOddity) manually reviews all Pull Requests. Please ensure your cover art URLs are direct image links (e.g., ending in `.jpg` or `.png`) and your Kick/Twitch IDs are numeric.*
