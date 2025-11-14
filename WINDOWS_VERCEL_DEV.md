# Windows + Vercel Dev Known Issues

## ⚠️ `vercel dev` doesn't work on Windows

The error you're seeing:
```
AttributeError: module 'socket' has no attribute 'AF_UNIX'
```

This is a **known limitation** of `vercel dev` on Windows. Unix sockets (`AF_UNIX`) are not supported on Windows.

## ✅ Solutions

### Option 1: Test Locally with Python (Recommended)
```bash
# Activate virtual environment
.\Scripts\Activate.ps1

# Run the app directly
python index.py
```

Visit: http://localhost:8000

This works perfectly and is faster than Vercel dev anyway! ✓

### Option 2: Use WSL2 (Windows Subsystem for Linux)
If you need `vercel dev`:
1. Install WSL2
2. Install Node.js in WSL
3. Run `vercel dev` from WSL terminal

### Option 3: Just Deploy to Vercel
The production deployment will work fine! The Windows limitation only affects local development with `vercel dev`.

## 🚀 Your Setup is Ready

All files are now configured correctly:

| File | Status |
|------|--------|
| ✅ `index.py` | Root-level FastAPI app (Vercel auto-detects) |
| ✅ `database.py` | Works both locally and on Vercel |
| ✅ `vercel.json` | Simplified (Vercel auto-detects Python) |
| ✅ `main.py` | Keep for reference, but `index.py` is the entry point |

## 📤 Deploy to Production

Since `vercel dev` doesn't work on Windows, just deploy directly:

```bash
git add .
git commit -m "Use index.py for Vercel auto-detection"
git push
```

Vercel will automatically:
1. Detect `index.py` 
2. Find the `app` instance
3. Deploy as a serverless function
4. Use environment variables from Vercel dashboard

## ✅ Testing Strategy

1. **Local Development**: Use `python index.py` (works great!)
2. **Production**: Deploy to Vercel and test live
3. **Preview Deployments**: Every push creates a preview URL

No need for `vercel dev` on Windows! 🎉

---

**Current Status:** 
- ✅ App runs locally on http://localhost:8000
- ✅ MongoDB connection works
- ✅ Ready to deploy to Vercel production
