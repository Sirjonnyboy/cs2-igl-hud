# IGL HUD

IGL HUD is a CS2 IGL dashboard that collects game data from teammates and yourself and displays it in a lightweight browser UI to help with ingame Economy managment. 

## Quick start

### Single packaged executable

- `dist\IGLHUD.exe` - Single unified executable. On startup it detects (or helps you find) the CS2 Steam folder, optionally creates the `gamestate_integration_python.cfg`, and asks whether you are the `host` or a `teammate`.

### Run the app (interactive)

1. Run `dist\IGLHUD.exe`.
2. Follow prompts to locate your Steam/CS2 `cfg` folder if needed.
3. Select role:
   - Host: runs the HUD server (creates GSI cfg if needed).
   - Teammate: runs the Scout forwarder (you'll be prompted for the host IP or can pass it with `--master-ip`).

### Non-interactive / CLI usage

You can run the launcher directly from source or pass flags to the exe:

From source (after installing requirements):
```powershell
pip install -r requirements.txt
python Main.py --role host
python Main.py --role teammate --master-ip 192.0.2.5
```

Common flags supported by the launcher:
- `--role host|teammate` : Choose role non-interactively.
- `--master-ip <IP>` : Master HUD IP for teammate mode.
- `--steam-drive <LETTER>` : Hint which drive Steam is installed on (e.g., `D`).
- `--no-browser` : Do not auto-open the HUD UI in a browser.
- `--non-interactive` : Run without prompting; useful for scripted installs.

When running as the HUD host, the application will attempt to auto-create a `gamestate_integration_python.cfg` in your CS2 `cfg` folder if one is not already present.

If you still need a separate scout-only binary, `scripts\build_scout.bat` remains available, but the recommended workflow is the single `IGLHUD.exe`.

## If you want to run from source

```powershell
pip install -r requirements.txt
python Main.py
python Scout.py
```

## Learn more

- Developer and architecture notes: `docs/ARCHITECTURE.md`
- Contribution and build conventions: `CONTRIBUTING.md`
- User-facing changelog: `CHANGELOG.md`

## Notes

- The HUD uses local data from CS2 GSI and serves the UI on port `22222`.
- `scripts/build_main.bat` builds `IGLHUD.exe`.
- `scripts/build_scout.bat` builds `CS2Scout.exe`.
