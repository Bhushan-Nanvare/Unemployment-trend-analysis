# Git Quick Reference - Revert Commands

## 🚀 Quick Commands

### View All Commits
```bash
git log --oneline
```

### Revert to a Specific Commit

#### Option 1: Soft Reset (Keep Changes - SAFEST)
```bash
git reset --soft <commit-hash>
git push --force-with-lease origin main
```

#### Option 2: Hard Reset (Discard Changes)
```bash
git reset --hard <commit-hash>
git push --force-with-lease origin main
```

#### Option 3: Revert (Keep History)
```bash
git revert <commit-hash>
git push origin main
```

---

## 📋 Your Recent Commits

```
a70b9fc docs: add comprehensive git revert guide
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

## 🎯 Common Use Cases

### "I want to go back to before the error fix"
```bash
git reset --soft 8c26570
git push --force-with-lease origin main
```

### "I want to undo the last commit"
```bash
git reset --soft HEAD~1
git push --force-with-lease origin main
```

### "I want to undo the last 3 commits"
```bash
git reset --soft HEAD~3
git push --force-with-lease origin main
```

### "I want to completely discard changes"
```bash
git reset --hard <commit-hash>
git push --force-with-lease origin main
```

---

## ⚠️ Important Notes

- **Soft Reset:** Keeps your work, safe to use
- **Hard Reset:** Loses work, use with caution
- **Force-with-lease:** Safer than force, use this
- **Reflog:** Can recover lost commits with `git reflog`

---

## 📚 Full Guide

See `GIT_REVERT_GUIDE.md` for detailed explanations and examples.

---

**Remember:** When in doubt, use `git reset --soft` - it's the safest option! 🛡️
