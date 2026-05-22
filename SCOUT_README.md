# CS2 Scout - Player Data Forwarder (Integrated)

The Scout forwarder is now integrated into the single unified launcher `IGLHUD.exe`. Non-host teammates can run the Scout behavior from the same executable or from source.

## Quick start (recommended)

1. Run `dist\IGLHUD.exe`.
2. Select `Teammate` when prompted and enter the master HUD IP (or pass `--master-ip` on the CLI).
3. Keep the Scout window open while playing.

## Run from source

```powershell
pip install -r requirements.txt
python Main.py --role teammate --master-ip 192.0.2.5
```

## Game State Integration config

The launcher can automatically create `gamestate_integration_python.cfg` in the detected CS2 `cfg` folder if none is present. The launcher tries common Program Files locations and scans available drives; if it cannot find the CFG folder it will prompt you (or accept `--steam-drive`).

Expected path (typical):

`C:\Steam\steamapps\common\Counter-Strike Global Offensive\game\csgo\cfg`

## Build the executable

Use the unified build script to create the single executable:

```powershell
scripts\build_main.bat
```

`scripts\build_scout.bat` still exists if you want a separate scout-only binary, but the unified `IGLHUD.exe` is recommended for simplicity.

## Notes

- Only non-host teammates need to run the Scout forwarder.
- The HUD server must be running on the host before Scout can connect (use `--master-ip` to point teammates at the host).
- Scout stores the master server IP in `scout_config.json` next to the executable.

## More information

- User-facing project overview: `README.md`
- Developer and build documentation: `CONTRIBUTING.md`
