import sys
import os

if getattr(sys, 'frozen', False):
    base_dir = os.path.dirname(sys.executable)
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))

src_path = os.path.join(base_dir, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from scout.scout import run_scout

if __name__ == '__main__':
    run_scout()
