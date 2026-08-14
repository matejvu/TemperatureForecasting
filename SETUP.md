# Setup Guide (Linux)

This guide walks you through getting this project from GitHub onto your
Linux machine, installing everything it needs, and the git workflow you
should use when making changes.

## 1. Prerequisites

You need `git`, `python3` (3.10+), `pip`, and the `venv` module. On
Ubuntu/Debian:

```bash
sudo apt update
sudo apt install -y git python3 python3-venv python3-pip
```

Confirm they're installed:

```bash
git --version
python3 --version
```

## 2. Clone the repository

```bash
git clone https://github.com/matejvu/TemperatureForecasting.git
cd TemperatureForecasting
```

## 3. Create and activate a virtual environment

A virtual environment keeps this project's Python packages separate from
the rest of your system.

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Your shell prompt should now start with `(.venv)`. You can confirm the
active Python is the venv's with:

```bash
which python
```

It should point inside `.venv/bin/python`, not `/usr/bin/python3`.

`.venv/` is already listed in `.gitignore`, so it never gets committed —
you (and your mentee) each create your own locally.

Whenever you open a new terminal to work on this project, re-activate it:

```bash
source .venv/bin/activate
```

To leave the virtual environment when you're done:

```bash
deactivate
```

## 4. Install dependencies

With the virtual environment active:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## 5. Verify the install

Run the data-fetching script as a smoke test:

```bash
python real_data/fetch_data.py
```

If everything is installed correctly, this fetches weather data from the
Open-Meteo API and creates `real_data/berlin_data.csv`,
`real_data/berlin_data.npz`, and a `.cache.sqlite` file (all gitignored).
If you get `ModuleNotFoundError`, double check the virtual environment is
active (step 3) and that `pip install -r requirements.txt` completed
without errors.

---

# Git Workflow

This project keeps things simple: everyone works directly on `main`.
There are no branches and no Pull Requests — you edit files, commit, and
push straight to `main`.

## One-time git setup

If you haven't used git on this machine before, set your identity (this
is what shows up as the author of your commits):

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

## The day-to-day workflow

### 1. Pull the latest changes before you start

Always start a work session by getting whatever changes are already on
GitHub, so you're not working on an outdated copy:

```bash
git pull
```

### 2. Make your changes

Edit files as needed. Check what you've changed at any point with:

```bash
git status
git diff
```

`git status` lists which files changed; `git diff` shows the actual
line-by-line changes.

### 3. Stage and commit your changes

Stage the specific files you want to include in the commit (avoid
`git add .` until you're comfortable — it's easy to accidentally include
files you didn't mean to commit):

```bash
git add real_data/plotting.py
git status
```

Run `git status` again before committing to confirm only the files you
intended are staged (shown in green). Then commit:

```bash
git commit -m "Add temperature and surface pressure plots vs. date"
```

Write commit messages in the imperative mood ("Add X", "Fix Y", not
"Added X" or "Fixes Y"), and keep them short but specific about *what*
changed.

You can make several commits like this as you work — you don't need to
squash everything into one.

### 4. Push to GitHub

```bash
git push
```

This uploads your commits to `main` on GitHub, where your mentor (and
anyone else on the project) can see them.

### If `git push` is rejected

This happens when someone else pushed changes to `main` after your last
`git pull` — your local copy is now behind. Fix it by pulling first,
then pushing again:

```bash
git pull
git push
```

`git pull` will try to automatically combine your changes with theirs.
If both of you edited the *same lines* in a file, git can't merge
automatically and will mark the conflict directly in the file:

```
<<<<<<< HEAD
your version of the code
=======
the version that was already on GitHub
>>>>>>> origin/main
```

Open the file, decide which version (or combination) is correct, delete
the `<<<<<<<`, `=======`, and `>>>>>>>` marker lines, save, then:

```bash
git add <the-file-you-fixed>
git commit
git push
```

## Quick reference

| Command | What it does |
|---|---|
| `git pull` | Get the latest changes from GitHub |
| `git status` | Show what's changed / staged |
| `git diff` | Show line-by-line changes |
| `git add <file>` | Stage a file for commit |
| `git commit -m "message"` | Commit staged changes |
| `git push` | Upload your commits to GitHub |

## Common issues

- **`ModuleNotFoundError` when running a script** — your virtual
  environment isn't active. Run `source .venv/bin/activate`.
- **`git push` rejected** — your local `main` is behind GitHub's. Run
  `git pull` first (resolve any conflicts as described above), then
  `git push` again.
- **Accidentally staged a file you didn't mean to** — unstage it with
  `git restore --staged <file>` (the file's edits are kept, just
  un-staged).
