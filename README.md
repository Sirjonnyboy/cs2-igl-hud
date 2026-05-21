# IGL HUD

IGL HUD is a CS2 IGL dashboard that collects game data from teammates and yourself and displays it in a lightweight browser UI to help with ingame Economy managment. 

## Quick start

### Use the packaged executable

- `dist\IGLHUD.exe` - Single executable that can run as host, scout, or both.

### Run the app

1. Run `dist\IGLHUD.exe`.
2. Choose whether to run as the HUD host, a Scout forwarder, or both.
	- If you pick *Both*, the app will start the server and run the scout locally (teammates don't need to run a separate executable).

When running as the HUD host, the application will attempt to auto-create a `gamestate_integration_python.cfg` in your CS2 `cfg` folder if one is not already present, so the host does not need to run the scout separately.

If you prefer separate binaries, `scripts\build_scout.bat` can still build `CS2Scout.exe`.

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
