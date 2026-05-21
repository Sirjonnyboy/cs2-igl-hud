# CS2 Scout - Player Data Forwarder

CS2 Scout forwards CS2 GSI data from a player machine to the master IGL HUD server.

## Quick start

### Use the packaged executable

1. Run `dist\CS2Scout.exe`.
2. Enter the master server IP when prompted.
3. Keep the Scout window open while playing.

### Run from source

```powershell
pip install -r requirements.txt
python Scout.py
```

## Game State Integration config

Scout will automatically create `gamestate_integration_python.cfg` in the CS:GO cfg folder if it cannot find one.

Expected path:

`C:\Steam\steamapps\common\Counter-Strike Global Offensive\game\csgo\cfg`

## Build the executable

```powershell
scripts\build_scout.bat
```

This creates `dist\CS2Scout.exe`.

## Notes

- Only non-host teammates need to run Scout.
- The HUD server must be running on the host before Scout can connect.
- Scout stores the master server IP in `scout_config.json` next to the executable.

## More information

- User-facing project overview: `README.md`
- Developer and build documentation: `CONTRIBUTING.md`
