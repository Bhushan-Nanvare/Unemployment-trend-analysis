# How to Revert Payment Implementation

If you want to revert back to the version before payment implementation was added, follow these steps:

## Option 1: Revert Specific Commit (Recommended)

This will undo ONLY the payment implementation commit while keeping all other changes:

```bash
# Revert the monetization commit
git revert 0df680b --no-edit

# Push to GitHub
git push origin main
```

**What this does:**
- Removes Pricing page (pages/10_Pricing.py)
- Removes For Business page (pages/11_For_Business.py)
- Removes upgrade banners from Job Risk Predictor
- Removes usage limit tracking
- Restores app.py to previous state
- Keeps all other improvements (Geo Career Advisor, Advanced Simulation, etc.)

**Result:** Clean revert with a new commit showing the revert

---

## Option 2: Hard Reset to Previous Commit

This will completely reset to the state BEFORE payment implementation:

```bash
# Reset to commit before monetization
git reset --hard 41c4966

# Force push to GitHub (WARNING: This rewrites history)
git push origin main --force
```

**What this does:**
- Completely removes all payment-related changes
- Removes Pricing page
- Removes For Business page
- Removes upgrade banners
- Removes usage limits
- Removes research paper and monetization docs

**WARNING:** This rewrites git history. Only use if you want to completely remove the payment implementation.

---

## Option 3: Selective Revert (Manual)

If you want to keep some payment features but remove problematic ones:

### Remove Pricing Page
```bash
git rm pages/10_Pricing.py
git commit -m "remove: pricing page"
git push
```

### Remove For Business Page
```bash
git rm pages/11_For_Business.py
git commit -m "remove: for business page"
git push
```

### Remove Upgrade Banners from Job Risk Predictor
Edit `pages/7_Job_Risk_Predictor.py` and remove:
- Lines 84-99 (usage limit banner)
- Lines 40-50 (upgrade banner in sidebar)
- Line 185 (usage counter increment)

Then commit:
```bash
git add pages/7_Job_Risk_Predictor.py
git commit -m "remove: upgrade banners from job risk predictor"
git push
```

---

## Commits to Revert

**Payment Implementation Commits:**
1. `0df680b` - feat: add monetization showcase and research paper
2. `526d6f2` - fix: repair Overview page and update pricing to affordable rates

**Related Commits:**
3. `41c4966` - docs: add GitHub upload completion summary (before payment)

---

## After Reverting

1. **Verify the revert:**
   ```bash
   git log --oneline -5
   ```

2. **Test the app:**
   ```bash
   streamlit run app.py
   ```

3. **Check that:**
   - Home page loads without errors
   - All 9 core pages are accessible
   - No Pricing or For Business pages
   - Job Risk Predictor works without upgrade banners

---

## If You Want to Keep Payment Features But Fix Errors

Instead of reverting, we can:

1. **Identify the specific error** (see DIAGNOSE_ERRORS.md)
2. **Fix just that issue** without removing payment features
3. **Test thoroughly** before pushing

This is the preferred approach if the errors are minor and fixable.

---

## Decision Matrix

| Situation | Recommended Action |
|-----------|-------------------|
| Payment pages have critical errors | Option 1: Revert specific commit |
| Want to remove all payment features | Option 2: Hard reset |
| Want to keep some payment features | Option 3: Selective revert |
| Want to fix errors without reverting | Identify error + fix directly |

---

## Need Help?

1. **Tell me the exact error message** you're seeing
2. **Tell me which page shows the error**
3. **Tell me when it appears** (on load, on button click, etc.)

Then I can either:
- Fix it directly (preferred)
- Revert it safely (if needed)

Let me know what you'd like to do!
