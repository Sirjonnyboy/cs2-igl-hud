import sys
import os
import argparse
import sys
import os

if getattr(sys, 'frozen', False):
    base_dir = os.path.dirname(sys.executable)
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))

src_path = os.path.join(base_dir, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from igl_hud.server import run_server
from scout.scout import (
    find_csgo_cfg_folder,
    prompt_for_cfg_folder,
    ensure_gsi_cfg_exists,
    run_scout,
)


def detect_or_ask_cfg_folder(interactive=True):
    cfg = find_csgo_cfg_folder()
    if cfg:
        print(f" [*] Detected CS2 cfg folder: {cfg}")
        return cfg

    if not interactive:
        return None

    print(" [*] Could not auto-detect CS2 cfg folder.")
    return prompt_for_cfg_folder()


def main():
    parser = argparse.ArgumentParser(description='IGL HUD unified launcher')
    parser.add_argument('--role', choices=['host', 'teammate'], help='Role to run as')
    parser.add_argument('--master-ip', help='Master HUD IP (for teammate mode)')
    parser.add_argument('--steam-drive', help='Drive letter where Steam is installed (e.g., D)')
    parser.add_argument('--no-browser', action='store_true', help='Do not open browser automatically')
    parser.add_argument('--non-interactive', action='store_true', help='Run without interactive prompts')
    args = parser.parse_args()

    interactive = not args.non_interactive

    # Preflight: detect cfg folder / steam drive
    cfg_folder = detect_or_ask_cfg_folder(interactive=interactive)
    if cfg_folder:
        print(f" [*] Using cfg folder: {cfg_folder}")

    role = args.role
    if not role and interactive:
        print('Select role:')
        print('  1) Host (run HUD server)')
        print('  2) Teammate (run Scout forwarder)')
        choice = input('Enter 1/2: ').strip()
        role = {'1': 'host', '2': 'teammate'}.get(choice, 'host')

    if role == 'host':
        # Ensure GSI config exists and then start server
        try:
            ensure_gsi_cfg_exists(ask_if_missing=interactive)
        except Exception:
            pass
        run_server()

    elif role == 'teammate':
        # Run scout / forwarder
        master_ip = args.master_ip
        run_scout(master_ip=master_ip, interactive=interactive, open_browser=(not args.no_browser))


if __name__ == '__main__':
    main()
