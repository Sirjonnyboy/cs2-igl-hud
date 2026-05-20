# CS2 Scout - Player Data Forwarder

Scout is a lightweight Python application that runs on each player's machine and forwards CS2 GSI (Game State Integration) data to the master IGL HUD server.

## Features

- **Automatic Server Detection**: Remembers the master server IP and verifies connection before starting.
- **Guided Setup**: Minimal user input required on first run.
- **Auto-Open HUD**: Automatically opens the IGL HUD webpage once connected.
- **Graceful Error Handling**: Clear error messages if the server is unreachable.
- **Standalone EXE**: Can be bundled as a standalone executable for distribution.

## Installation

### For Development (Running as Python Script)

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run Scout:
   ```
   python Scout.py
   ```

> Note: Only the server host needs to run `Main.py`. If you are not the server owner, just run `Scout.py`.

### Game State Integration config

Scout checks for `gamestate_integration_python.cfg` in the CS:GO cfg folder and will create it if missing. This file should live in:

`C:\Steam\steamapps\common\Counter-Strike Global Offensive\game\csgo\cfg`

The file contents should be:

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

### For Distribution (Building as EXE)

1. Install PyInstaller:
   ```
   pip install pyinstaller
   ```

2. Run the build script:
   ```
   build_scout.bat
   ```

3. The executable will be created in the `dist\` folder as `CS2Scout.exe`.

## Usage

1. **First Run**: Scout will ask you to enter the master server IP address (e.g., `100.10.20.30`).
2. **Subsequent Runs**: Scout will ask if the saved IP is still correct. Press `Y` to confirm or `N` to enter a new one.
3. **Connection Verification**: Scout tests the connection before starting. If the master server is unreachable, you'll see a clear error message.
4. **Auto-Open HUD**: Once connected, your web browser will automatically open the IGL HUD.
5. **Keep Running**: Leave Scout running while playing. It silently forwards all game data to the master server.

## Error Messages

- **"Server IP is either wrong, or the master server has not started yet"**
  - Check that the IP address is correct.
  - Ensure the master server (Main.py) is running.
  - Check your network connection.

## Configuration

Scout stores the master server IP in `scout_config.json` in the same directory as the executable. You can delete this file to reset the saved IP.

## For Teammates

Simply download and run `CS2Scout.exe`. No additional setup required!

---

**Important**: Keep the Scout window open during gameplay. Closing it will stop data forwarding to the IGL HUD.
