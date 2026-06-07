# Mini Blog

A small Flask-based mini blog used for testing image uploads and basic CRUD.

## Setup (Windows)

1. Create and activate virtual environment

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

2. Install dependencies

```powershell
pip install -r requirements.txt
```

3. Run the app

```powershell
python app.py
```

Open http://127.0.0.1:5000 in your browser.

## Notes
- Uploaded images are stored in `static/uploads/` (this folder is excluded from git via `.gitignore`).
- Database file `blog.db` is stored in the project root; add it to `.gitignore` if you don't want it tracked.

## Publishing to GitHub

Create a new repository on GitHub (e.g. `mini_blog`) and then run these commands locally in the project folder:

```powershell
# initialize
git init
git add .
git commit -m "Initial commit"
# set branch to main
git branch -M main
# add remote (HTTPS)
git remote add origin https://github.com/YOUR_USERNAME/mini_blog.git
# push
git push -u origin main
```

Or with SSH (after adding your SSH key to GitHub):

```powershell
git remote add origin git@github.com:YOUR_USERNAME/mini_blog.git
git push -u origin main
```

Or using GitHub CLI:

```powershell
gh repo create YOUR_USERNAME/mini_blog --public --source=. --push
```

