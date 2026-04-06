# BBU UAT Dashboard — Deploy Guide

## What's in this folder

| File | Purpose |
|------|---------|
| `BBU_UAT_Dashboard.html` | The dashboard — this is what Netlify serves |
| `build.py` | Rebuild script — run this when you get a new data export |

---

## One-time setup (~20 minutes)

### Step 1 — Create a GitHub repository

1. Go to [github.com](https://github.com) and sign in (or create a free account)
2. Click **New repository**
3. Name it something like `bbu-uat-dashboard`
4. Set it to **Private**
5. Click **Create repository**
6. Upload both files (`BBU_UAT_Dashboard.html` and `build.py`) to the repo

### Step 2 — Connect Netlify to GitHub

1. Go to [netlify.com](https://netlify.com) and sign in
2. Click **Add new site → Import an existing project**
3. Choose **GitHub** and authorize Netlify
4. Select your `bbu-uat-dashboard` repository
5. Settings:
   - **Branch to deploy:** `main`
   - **Build command:** *(leave blank)*
   - **Publish directory:** *(leave blank — or type `.`)*
6. Click **Deploy site**

Netlify will deploy immediately. Every time you push a new file to GitHub, it redeploys automatically within 30–60 seconds.

---

## Ongoing workflow — updating the dashboard

Every time you get a new Smartsheet export from Jorge:

### On Mac or Linux

```bash
# 1. Go to your project folder
cd ~/path/to/bbu-uat-dashboard

# 2. Run the build script
python3 build.py ~/Downloads/o9_UAT_export.xlsx

# 3. Commit and push
git add BBU_UAT_Dashboard.html
git commit -m "Data refresh - $(date '+%B %d %Y')"
git push
```

Netlify picks it up automatically. Done.

### On Windows

```bash
# Same steps, just use backslashes for paths
python build.py C:\Users\YourName\Downloads\o9_UAT_export.xlsx
git add BBU_UAT_Dashboard.html
git commit -m "Data refresh"
git push
```

---

## First-time Git setup (if needed)

If you haven't used Git before, run these once:

```bash
# Install Git: https://git-scm.com/downloads
# Then clone your repo locally:
git clone https://github.com/YOUR_USERNAME/bbu-uat-dashboard.git
cd bbu-uat-dashboard
```

---

## Install Python dependencies (once)

```bash
pip install pandas openpyxl
```

---

## Adding Jorge as a collaborator (optional)

If Jorge should be able to push updates directly:

1. Go to your GitHub repo
2. **Settings → Collaborators → Add people**
3. Enter Jorge's GitHub username or email
4. He accepts the invitation

Jorge's workflow would then be identical — run `build.py`, commit, push.

---

## Troubleshooting

**"No module named pandas"**
Run: `pip install pandas openpyxl`

**"Template not found"**
Make sure `build.py` and `BBU_UAT_Dashboard.html` are in the same folder.

**Netlify not updating**
Check the Netlify dashboard for build errors. Most common cause: the file wasn't committed before pushing.

**New tester names not normalizing**
Add them to the `NAME_MAP` dict in `build.py` and re-run.
