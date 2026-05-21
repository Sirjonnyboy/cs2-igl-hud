# IGL HUD Architecture and Developer Notes

## Overview

The IGL HUD repository contains two main components:

- `Main.py`: the IGL HUD server that collects CS2 match data and serves the HUD web UI.
- `Scout.py`: the player-side forwarder that reads CS2/CS:GSI data and posts it to the master IGL HUD server.

The package layout is:

- `src/igl_hud/`
  - `server.py`: HTTP server and UI endpoints.
  - `logger.py`: app logging and `rounds.db` persistence.
  - `economy.py`: enemy economy and team buy logic.
  - `index.html`, `analytics.html`: embedded web UI assets.
- `src/scout/`
  - `scout.py`: GSI forwarder logic and auto configuration.

## Packaging

This project supports standalone Windows executables using PyInstaller.

- `scripts/build_main.bat`: builds `IGLHUD.exe` from `Main.py`.
- `scripts/build_scout.bat`: builds `CS2Scout.exe` from `Scout.py`.

The executables are built with the Python runtime bundled and the web UI assets added as PyInstaller data files.

### Runtime file locations

- `rounds.db` is written next to the packaged HUD executable when running as a frozen bundle.
- `scout_config.json` is written next to the packaged Scout executable when frozen.
- `index.html` and `analytics.html` are loaded via a helper that resolves bundled data when the server is frozen.

## Running Locally

### Server host

1. Install Python dependencies:

```powershell
pip install -r requirements.txt
```

2. Run the HUD server:

```powershell
python Main.py
```

3. Visit `http://localhost:22222` in your browser.

### Non-host Scout

1. Install dependencies:

```powershell
pip install -r requirements.txt
```

2. Run Scout:

```powershell
python Scout.py
```

## Game State Integration (GSI)

The Scout forwarder automatically generates a GSI config file if it cannot find one.

The config must live in:

`C:\Steam\steamapps\common\Counter-Strike Global Offensive\game\csgo\cfg`

The file name is `gamestate_integration_python.cfg` and the contents are:

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

## Build and Test

- `scripts/build_main.bat` builds the HUD executable.
- `scripts/build_scout.bat` builds the Scout executable.
- Verify by running the built `.exe` and confirming the HUD loads in your browser or Scout connects to the master server.
