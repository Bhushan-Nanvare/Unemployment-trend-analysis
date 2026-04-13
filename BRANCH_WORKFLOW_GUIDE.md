# Git Branch Workflow Guide

## ✅ Current Setup

You now have two branches:
- **`main`** - Stable production version (your current deployed app)
- **`development`** - New branch for making changes (currently active)

---

## 🔄 Workflow for Making Changes

### **Step 1: Make Your Changes**
You're currently on the `development` branch. Make any changes you want:
```bash
# You're already on development branch
# Edit files, add features, fix bugs, etc.
```

### **Step 2: Commit Your Changes**
```bash
git add .
git commit -m "Description of your changes"
```

### **Step 3: Push to Development Branch**
```bash
git push origin development
```

### **Step 4: Test Your Changes**
- Changes are now on GitHub in the `development` branch
- You can deploy this branch to test it

---

## 🚀 Deploying the Development Branch

### **Option A: Streamlit Cloud (Recommended)**

1. **Go to Streamlit Cloud Dashboard**
   - Visit: https://share.streamlit.io/
   - Sign in with your GitHub account

2. **Update Your App Settings**
   - Click on your app (Unemployment-trend-analysis)
   - Click the ⚙️ **Settings** button
   - Go to **"General"** tab

3. **Change the Branch**
   - Find **"Branch"** setting
   - Change from `main` to `development`
   - Click **"Save"**

4. **Reboot the App**
   - Click **"Reboot app"** button
   - Your app will now run from the `development` branch

**Screenshot locations:**
```
Settings → General → Branch: [main ▼] → Select "development" → Save
```

### **Option B: Render**

If you're using Render:

1. **Go to Render Dashboard**
   - Visit: https://dashboard.render.com/

2. **Select Your Service**
   - Click on your Streamlit app service

3. **Update Branch**
   - Go to **Settings**
   - Find **"Branch"** under **"Build & Deploy"**
   - Change to `development`
   - Click **"Save Changes"**

4. **Manual Deploy (if needed)**
   - Click **"Manual Deploy"** → **"Deploy latest commit"**

---

## 🔙 How to Revert Back to Main

### **If You Want to Undo Changes Locally:**

```bash
# Switch back to main branch
git checkout main

# Your local files will revert to main branch state
```

### **If You Want to Revert Deployment:**

**On Streamlit Cloud:**
1. Go to Settings → General
2. Change Branch from `development` back to `main`
3. Click Save and Reboot

**On Render:**
1. Go to Settings → Build & Deploy
2. Change Branch to `main`
3. Save and redeploy

### **If You Want to Delete Development Branch:**

```bash
# Switch to main first
git checkout main

# Delete local development branch
git branch -d development

# Delete remote development branch
git push origin --delete development
```

---

## 🔀 Merging Development into Main (When Ready)

When you're happy with your changes and want to make them permanent:

### **Option 1: Via GitHub Pull Request (Recommended)**

1. **Go to GitHub Repository**
   - Visit: https://github.com/Bhushan-Nanvare/Unemployment-trend-analysis

2. **Create Pull Request**
   - Click **"Pull requests"** tab
   - Click **"New pull request"**
   - Base: `main` ← Compare: `development`
   - Click **"Create pull request"**

3. **Review and Merge**
   - Review your changes
   - Click **"Merge pull request"**
   - Click **"Confirm merge"**

4. **Update Deployment**
   - Change Streamlit Cloud branch back to `main`
   - Your changes are now in production!

### **Option 2: Via Command Line**

```bash
# Switch to main branch
git checkout main

# Merge development into main
git merge development

# Push to GitHub
git push origin main

# Update deployment to use main branch
```

---

## 📋 Quick Reference Commands

### **Check Current Branch**
```bash
git branch
# * development  ← asterisk shows current branch
#   main
```

### **Switch Between Branches**
```bash
# Switch to main
git checkout main

# Switch to development
git checkout development
```

### **See All Branches (Local + Remote)**
```bash
git branch -a
```

### **Create New Branch**
```bash
git checkout -b feature-name
```

### **Push Current Branch**
```bash
git push origin development
```

### **Pull Latest Changes**
```bash
git pull origin development
```

---

## 🎯 Recommended Workflow

### **For Experimental Changes:**
```
1. Work on development branch
2. Commit and push frequently
3. Deploy development branch to test
4. If good → Merge to main
5. If bad → Stay on main, delete development
```

### **For Multiple Features:**
```
main (stable)
  ├── development (general changes)
  ├── feature-career-paths (specific feature)
  ├── bugfix-data-quality (specific fix)
  └── experiment-new-model (risky changes)
```

Create separate branches for each major feature:
```bash
git checkout -b feature-name
# Make changes
git push origin feature-name
# Test separately
# Merge when ready
```

---

## ⚠️ Important Notes

### **Before Making Changes:**
```bash
# Always check which branch you're on
git branch

# Make sure you're on development
git checkout development

# Pull latest changes
git pull origin development
```

### **Before Committing:**
```bash
# Check what files changed
git status

# Review your changes
git diff

# Add files
git add .

# Commit with clear message
git commit -m "Clear description of what changed"
```

### **If You Make a Mistake:**
```bash
# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes)
git reset --hard HEAD~1

# Discard all local changes
git checkout .
```

---

## 🚀 Current Status

✅ **You are now on:** `development` branch
✅ **Main branch:** Safe and unchanged
✅ **Remote branches:** Both pushed to GitHub

**Next Steps:**
1. Make your changes on `development` branch
2. Commit and push: `git push origin development`
3. Update Streamlit Cloud to use `development` branch
4. Test your changes
5. If good → Merge to main
6. If bad → Switch back to main

---

## 📞 Quick Help

**"I want to make changes but keep main safe"**
→ You're already set up! Just make changes and commit.

**"I want to test my changes"**
→ Push to development, update Streamlit Cloud branch to development

**"I want to go back to the old version"**
→ `git checkout main` and update Streamlit Cloud to main

**"I want to make my changes permanent"**
→ Merge development into main via Pull Request

**"I messed up and want to start over"**
→ `git checkout main` then `git branch -D development` then create new development branch

---

## 🎓 Learning Resources

- **Git Branching**: https://git-scm.com/book/en/v2/Git-Branching-Basic-Branching-and-Merging
- **GitHub Flow**: https://guides.github.com/introduction/flow/
- **Streamlit Deployment**: https://docs.streamlit.io/streamlit-community-cloud/get-started

---

**Created:** 2026-04-13  
**Current Branch:** `development`  
**Status:** ✅ Ready for changes
