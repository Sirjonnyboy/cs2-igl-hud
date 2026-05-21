# IGL HUD

IGL HUD is a multiplayer CS2 IGL dashboard that collects game data from teammates and displays it in a lightweight browser UI.

## Quick start

### Use the packaged executables

- `dist\IGLHUD.exe` - HUD server executable for the match host.
- `dist\CS2Scout.exe` - Scout forwarder executable for teammates.

### Run the HUD

1. Start `IGLHUD.exe` on the host machine.
2. Open `http://localhost:22222` in your browser.

### Run the Scout

1. Start `CS2Scout.exe` on teammate machines.
2. Enter the host IP when prompted.
3. Scout will forward CS2 GSI data to the host HUD.

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
