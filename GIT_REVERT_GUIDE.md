# Git Revert Guide - How to Go Back to a Previous Commit

## Quick Reference

### View All Commits
```bash
git log --oneline
```

### Revert to a Specific Commit (3 Methods)

---

## Method 1: Soft Reset (Keep Changes in Staging Area)
**Use when:** You want to keep your changes but undo the commits

```bash
git reset --soft <commit-hash>
```

**Example:**
```bash
git reset --soft 8c26570
```

**What happens:**
- ✅ Reverts to that commit
- ✅ Keeps all changes in staging area
- ✅ You can modify and recommit
- ✅ Safe - doesn't lose work

---

## Method 2: Mixed Reset (Keep Changes in Working Directory)
**Use when:** You want to keep changes but unstage them

```bash
git reset --mixed <commit-hash>
```

**Example:**
```bash
git reset --mixed 8c26570
```

**What happens:**
- ✅ Reverts to that commit
- ✅ Keeps all changes in working directory (unstaged)
- ✅ You can modify and recommit
- ✅ Safe - doesn't lose work

---

## Method 3: Hard Reset (Discard All Changes)
**Use when:** You want to completely discard all changes

```bash
git reset --hard <commit-hash>
```

**Example:**
```bash
git reset --hard 8c26570
```

**What happens:**
- ⚠️ Reverts to that commit
- ⚠️ Discards ALL changes after that commit
- ⚠️ Cannot be undone easily
- ⚠️ Use with caution!

---

## Method 4: Revert (Create New Commit)
**Use when:** You want to undo changes but keep history

```bash
git revert <commit-hash>
```

**Example:**
```bash
git revert 1793d18
```

**What happens:**
- ✅ Creates a NEW commit that undoes the changes
- ✅ Keeps all history intact
- ✅ Safe - doesn't lose anything
- ✅ Good for shared repositories

---

## Step-by-Step Examples

### Example 1: Revert to Commit Before Error Fix

**Step 1: View all commits**
```bash
git log --oneline
```

**Output:**
```
f9b4546 docs: add error fix summary for overview page
1793d18 fix: add error handling for get_gdp_growth calls in Overview page
5305209 docs: add quick streamlit cloud deployment guide
8c26570 docs: add comprehensive dual-mode geo career advisor documentation
191bc4a feat: restore dual-mode geo career advisor
...
```

**Step 2: Decide which commit to revert to**
- If you want to go back BEFORE the error fix: `8c26570`
- If you want to go back BEFORE the deployment guide: `5305209`

**Step 3: Revert using soft reset (safest)**
```bash
git reset --soft 8c26570
```

**Step 4: Check status**
```bash
git status
```

**Step 5: If happy, push to GitHub**
```bash
git push --force-with-lease origin main
```

---

## Comparison of Methods

| Method | Keeps Changes | Keeps History | Safe | Use Case |
|--------|---------------|---------------|------|----------|
| **Soft Reset** | ✅ Staging | ❌ No | ✅ Yes | Undo commits, keep work |
| **Mixed Reset** | ✅ Working Dir | ❌ No | ✅ Yes | Undo commits, unstage |
| **Hard Reset** | ❌ No | ❌ No | ⚠️ Risky | Complete discard |
| **Revert** | ✅ New Commit | ✅ Yes | ✅ Yes | Undo on shared repo |

---

## Common Scenarios

### Scenario 1: "I Made a Mistake, Keep My Work"
```bash
git reset --soft <commit-hash>
# Make changes
git add .
git commit -m "Fixed version"
git push --force-with-lease origin main
```

### Scenario 2: "I Want to Undo Last Commit"
```bash
git reset --soft HEAD~1
# HEAD~1 means "one commit before current"
```

### Scenario 3: "I Want to Undo Last 3 Commits"
```bash
git reset --soft HEAD~3
# HEAD~3 means "three commits before current"
```

### Scenario 4: "I Want to Completely Discard Changes"
```bash
git reset --hard <commit-hash>
# WARNING: This cannot be undone!
```

### Scenario 5: "I Want to Undo But Keep History"
```bash
git revert <commit-hash>
# Creates a new commit that undoes the changes
git push origin main
```

---

## Safety Tips

### ✅ Safe Operations
- `git reset --soft` - Always safe
- `git reset --mixed` - Always safe
- `git revert` - Always safe
- `git log` - Just viewing, no changes

### ⚠️ Risky Operations
- `git reset --hard` - Loses work!
- `git push --force` - Can overwrite others' work!

### 🛡️ Best Practices
1. Always check `git log --oneline` first
2. Use `--soft` or `--mixed` by default
3. Use `--hard` only if you're sure
4. Use `--force-with-lease` instead of `--force`
5. Backup important work before hard reset

---

## Undo a Reset (If You Made a Mistake)

If you accidentally did a hard reset and lost work:

```bash
git reflog
```

This shows ALL commits you've ever been on. Find your commit and:

```bash
git reset --hard <commit-hash>
```

---

## Your Current Commits

Here are your recent commits:

```
f9b4546 docs: add error fix summary for overview page
1793d18 fix: add error handling for get_gdp_growth calls in Overview page
5305209 docs: add quick streamlit cloud deployment guide
8c26570 docs: add comprehensive dual-mode geo career advisor documentation
191bc4a feat: restore dual-mode geo career advisor
506e7d8 docs: add comprehensive geo career advisor fix documentation
48401b4 fix: geo career advisor - input validation, skill filtering, remove model risk tab
526d6f2 fix: repair Overview page and update pricing to affordable rates
41c4966 docs: add GitHub upload completion summary
```

---

## Example: Revert to Before Error Fix

If you want to go back to before the error fix was applied:

```bash
# View commits
git log --oneline

# Revert to commit before error fix (soft reset - keeps work)
git reset --soft 8c26570

# Check what changed
git status

# If happy, push to GitHub
git push --force-with-lease origin main
```

---

## Pushing After Reset

### Option 1: Force with Lease (Safer)
```bash
git push --force-with-lease origin main
```
- Safer than `--force`
- Won't overwrite others' work
- Recommended for shared repos

### Option 2: Force (Use with Caution)
```bash
git push --force origin main
```
- Overwrites remote history
- Can cause issues if others are working
- Use only if you're sure

### Option 3: Create New Branch (Safest)
```bash
git checkout -b backup-branch
git push origin backup-branch
# Then reset on main
git checkout main
git reset --soft <commit-hash>
git push --force-with-lease origin main
```

---

## Troubleshooting

### "I Can't Push After Reset"
```bash
# Use force-with-lease instead of force
git push --force-with-lease origin main
```

### "I Lost My Work!"
```bash
# Check reflog to find your commit
git reflog

# Reset to that commit
git reset --hard <commit-hash>
```

### "I Want to See What Changed"
```bash
# Before resetting, see what will change
git diff <commit-hash> HEAD
```

---

## Summary

**To revert to a specific commit:**

1. **View commits:** `git log --oneline`
2. **Choose method:**
   - Keep work: `git reset --soft <hash>`
   - Discard work: `git reset --hard <hash>`
   - Keep history: `git revert <hash>`
3. **Push to GitHub:** `git push --force-with-lease origin main`

**Remember:** Soft reset is usually the safest option!

---

## Need Help?

If you're unsure:
1. Always use `--soft` first
2. Check `git status` before pushing
3. Use `--force-with-lease` not `--force`
4. Keep backups of important work

Good luck! 🚀
