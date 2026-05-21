# IGL HUD

This repository contains two main components:

- `Main.py` - the IGL HUD server that collects CS2 match data and serves it to the browser.
- `Scout.py` - the player-side forwarder that reads GSI data and sends it to the HUD.

## Project structure

- `Main.py` - root entrypoint for the HUD server.
- `Scout.py` - root entrypoint for the scout forwarder.
- `requirements.txt` - Python dependencies.
- `scripts/build_scout.bat` - build script for packaging `Scout.py`.
 - `scripts/build_main.bat` - build script for packaging `Main.py`.
- `src/igl_hud/` - HUD backend package:
  - `server.py` - server logic and API handlers.
  - `logger.py` - logging and database persistence.
  - `economy.py` - enemy economy tracking.
  - `index.html`, `analytics.html` - HUD frontend pages.
- `src/scout/` - scout client package:
  - `scout.py` - GSI forwarder logic.

## Run locally

1. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

2. Start the HUD server (server host only):
   ```powershell
   python Main.py
   ```

3. Start the scout forwarder (all non-host teammates):
   ```powershell
   python Scout.py
   ```

## Build standalone Windows executables

This repository can be packaged into `.exe` files so end users do not need a Python installation.

1. Install packaging dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

2. Build the HUD server executable:
   ```powershell
   scripts\build_main.bat
   ```

3. Build the scout forwarder executable:
   ```powershell
   scripts\build_scout.bat
   ```

The created `.exe` files will be available in the `dist\` folder.

## Who runs what

- Only the server host needs to run `python Main.py`.
- If you are not the server owner, just run `python Scout.py` to forward your local CS:GO/CS2 game data.

## Game State Integration config

`Scout.py` checks for `gamestate_integration_python.cfg` in the CS:GO cfg folder and will create it automatically if it is missing. This file must be placed in:

`C:\Steam\steamapps\common\Counter-Strike Global Offensive\game\csgo\cfg`

The file contents are:

```text
"Game State Integration"
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
}
```

## Notes

- `rounds.db` is excluded from git and created automatically by the HUD.
- `scout_config.json` is stored next to `src/scout/scout.py` after first run.
 4cfba61 (Add server and scout modules for CS2 IGL dashboard)
