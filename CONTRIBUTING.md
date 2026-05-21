# Contributing to IGL HUD

## Commit message style

This repository uses Conventional Commits.

Format:

```text
type(scope): short summary

optional body

optional footer
```

Accepted types:

- `feat` - new feature
- `fix` - bug fix
- `docs` - documentation only changes
- `style` - formatting, white-space, linting
- `refactor` - code change that neither fixes a bug nor adds a feature
- `perf` - performance improvement
- `test` - adding or fixing tests
- `build` - changes to build scripts or tooling
- `chore` - maintenance tasks

Examples:

- `feat(packaging): add Windows executable build script`
- `fix(entrypoint): load src path for frozen executables`
- `docs(readme): add standalone executable usage instructions`

## Staging and commits

Use staging to keep commits small and logical.

Example workflow:

```bash
git add Main.py
git commit -m "fix(entrypoint): load src path for frozen executables"

git add README.md
git commit -m "docs(readme): add standalone executable build instructions"
```

If multiple files are part of a single change, stage and commit them together.

## Running the project

### Local development

```powershell
pip install -r requirements.txt
python Main.py
python Scout.py
```

### Build Windows executables

- `scripts/build_main.bat`
- `scripts/build_scout.bat`

## How to contribute

1. Fork the repository.
2. Create a feature branch.
3. Make your changes.
4. Stage and commit with Conventional Commits.
5. Open a pull request with a short description.

## Changelog and releases

Use `CHANGELOG.md` for user-facing release notes.
Link release notes to GitHub Releases when publishing a new version.
