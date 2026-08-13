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

This project uses a **feature branch + Pull Request** workflow: you never
commit directly to `main`. Every change goes through its own branch and a
Pull Request (PR) that gets reviewed before merging. This keeps `main`
always in a working state and gives you a record of what changed and why.

## One-time git setup

If you haven't used git on this machine before, set your identity (this
is what shows up as the author of your commits):

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

## The day-to-day workflow

### 1. Make sure `main` is up to date

Always start new work from the latest `main`:

```bash
git checkout main
git pull origin main
```

### 2. Create a branch for your task

Never work directly on `main`. Create a new branch with a short,
descriptive name:

```bash
git checkout -b feature/add-temperature-plot
```

Naming convention:
- `feature/...` — new functionality (e.g. `feature/add-temperature-plot`)
- `fix/...` — bug fixes (e.g. `fix/wrong-date-parsing`)
- `docs/...` — documentation-only changes (e.g. `docs/update-readme`)

### 3. Make your changes

Edit files as needed. Check what you've changed at any point with:

```bash
git status
git diff
```

`git status` lists which files changed; `git diff` shows the actual
line-by-line changes.

### 4. Stage and commit your changes

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

### 5. Push your branch to GitHub

The first time you push a new branch:

```bash
git push -u origin feature/add-temperature-plot
```

`-u` links your local branch to the remote one, so after this you can
just run `git push` for that branch.

### 6. Open a Pull Request

Go to the repository on GitHub — you'll see a banner suggesting
"Compare & pull request" for your recently pushed branch. Click it, add
a short description of what you changed and why, and open the PR.

If you have the [GitHub CLI](https://cli.github.com/) installed, you can
do this from the terminal instead:

```bash
gh pr create --fill
```

### 7. Respond to review feedback

If your mentor requests changes, make them on the same branch, then:

```bash
git add <changed-files>
git commit -m "Address review feedback: ..."
git push
```

The new commits automatically show up in the same PR — no need to open a
new one.

### 8. Merge

Once the PR is approved, merge it on GitHub (the "Merge pull request"
button). After merging, GitHub will offer to delete the branch — you can
click that, it's safe since the work is now in `main`.

### 9. Clean up locally after merging

Switch back to `main`, pull the merged changes, and delete your local
copy of the now-merged branch:

```bash
git checkout main
git pull origin main
git branch -d feature/add-temperature-plot
```

## Keeping a long-running branch up to date

If your PR sits open for a while and `main` moves forward, bring those
changes into your branch before merging:

```bash
git checkout feature/add-temperature-plot
git fetch origin
git merge origin/main
```

If git reports a conflict, it will mark the conflicting sections directly
in the affected files with markers like:

```
<<<<<<< HEAD
your version of the code
=======
the version from main
>>>>>>> origin/main
```

Edit the file to keep the correct combination of both, remove the
`<<<<<<<`/`=======`/`>>>>>>>` marker lines, then:

```bash
git add <the-file-you-fixed>
git commit
git push
```

## Quick reference

| Command | What it does |
|---|---|
| `git status` | Show what's changed / staged |
| `git diff` | Show line-by-line changes |
| `git checkout main && git pull` | Update your local `main` |
| `git checkout -b feature/x` | Create and switch to a new branch |
| `git add <file>` | Stage a file for commit |
| `git commit -m "message"` | Commit staged changes |
| `git push -u origin feature/x` | Push a new branch the first time |
| `git push` | Push subsequent commits on the same branch |
| `git branch -d feature/x` | Delete a local branch after it's merged |

## Common issues

- **`ModuleNotFoundError` when running a script** — your virtual
  environment isn't active. Run `source .venv/bin/activate`.
- **`git push` rejected** — someone else's changes landed on the branch
  or `main` first. Run `git pull` (or `git fetch && git merge origin/main`
  on a feature branch) to bring your branch up to date, then push again.
- **Accidentally staged a file you didn't mean to** — unstage it with
  `git restore --staged <file>` (the file's edits are kept, just
  un-staged).
