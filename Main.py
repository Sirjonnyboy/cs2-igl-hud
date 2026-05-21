import sys
import os
import argparse

if getattr(sys, 'frozen', False):
    base_dir = os.path.dirname(sys.executable)
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))

src_path = os.path.join(base_dir, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from igl_hud.server import run_server
from scout.scout import ensure_gsi_cfg_exists


def main():
    # Ensure the user's CS2 GSI config exists so the host HUD can receive local game data
    try:
        ensure_gsi_cfg_exists()
    except Exception:
        # Don't block server start if GSI helper fails for any reason
        pass

    run_server()


if __name__ == '__main__':
    main()
