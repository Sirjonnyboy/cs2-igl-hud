# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]
	- Launcher auto-detects Steam/CS2 cfg folder and can create `gamestate_integration_python.cfg` when missing.
	- CLI flags added: `--role`, `--master-ip`, `--steam-drive`, `--no-browser`, `--non-interactive`.
	- `scout` behavior is integrated; the separate `CS2Scout.exe` build is deprecated in favor of the unified exe.
	- Build script `scripts\build_main.bat` updated to include dependencies and `scout` module in the packaged executable.
## [0.2.0] - 2026-05-21

- Unified launcher: single `IGLHUD.exe` now supports `host` and `teammate` (scout) roles.
	- Launcher auto-detects Steam/CS2 cfg folder and can create `gamestate_integration_python.cfg` when missing.
	- CLI flags added: `--role`, `--master-ip`, `--steam-drive`, `--no-browser`, `--non-interactive`.
	- `scout` behavior is integrated; the separate `CS2Scout.exe` build is deprecated in favor of the unified exe.
	- Build script `scripts\build_main.bat` updated to include dependencies and `scout` module in the packaged executable.


## [0.1.0] - 2026-05-21
- Initial repository reorganization and packaging support.
