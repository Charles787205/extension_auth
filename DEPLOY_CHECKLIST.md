# 🚀 Vercel Deployment Checklist

## ✅ Critical Fixes Applied

1. **Fixed api/index.py** - Added proper path handling and error logging
2. **Fixed database.py** - Only loads .env locally, not on Vercel
3. **Fixed main.py** - Absolute template paths for Vercel compatibility
4. **Database connection works** - Tested locally ✓

## 📋 Before You Deploy

### Step 1: Verify Environment Variables in Vercel

Go to your Vercel project → Settings → Environment Variables

**Required Variables:**

| Variable | Value | Notes |
|----------|-------|-------|
| `MONGODB_URL` | `mongodb://joviancharles1210:Tn3T73SklEPMdG5h@ac-fihi6e3-shard-00-00.yldtxjz.mongodb.net:27017,ac-fihi6e3-shard-00-01.yldtxjz.mongodb.net:27017,ac-fihi6e3-shard-00-02.yldtxjz.mongodb.net:27017/?replicaSet=atlas-5aecx1-shard-0&ssl=true&authSource=admin` | Use this exact connection string |
| `DATABASE_NAME` | `extension` | Your database name |
| `VERCEL` | `1` | Tells app it's running on Vercel |

⚠️ **IMPORTANT**: Copy the MONGODB_URL exactly as shown above. Any typo will cause connection failures.

### Step 2: Verify Database is Initialized

Your database already has:
- ✅ Admin user (username: admin, password: password)
- ✅ API state initialized

If you need to verify, go to MongoDB Atlas → Browse Collections

### Step 3: Push Code to GitHub

```bash
git add .
git commit -m "Fix Vercel serverless deployment issues"
git push
```

### Step 4: Deploy on Vercel

Vercel will auto-deploy when you push to GitHub.

Or manually:
1. Go to Vercel Dashboard
2. Select your project
3. Click "Redeploy"

### Step 5: Test the Deployment

After deployment:
1. Visit your Vercel URL: `https://extension-auth-p6ufzbkpz-jovian-charles-canedos-projects.vercel.app`
2. You should see the login page
3. Login with:
   - Username: `admin`
   - Password: `password`

## 🐛 If You Still Get Errors

The new error handler in `api/index.py` will now show detailed error messages. If you see a 500 error:

1. **Check the error response** - It will now show the actual error in the browser
2. **Check Vercel Function Logs** - Should show more details now
3. **Common issues:**
   - Missing environment variables
   - Typo in MONGODB_URL
   - MongoDB Atlas network access not allowing 0.0.0.0/0

## 📁 Key Files Changed

- ✅ `api/index.py` - Better error handling and path resolution
- ✅ `database.py` - Conditional .env loading
- ✅ `main.py` - Absolute paths for templates
- ✅ `.env` - Working MongoDB connection string

## 🔍 Testing Locally

To test locally before deploying:

```bash
# Activate virtual environment
.\Scripts\Activate.ps1

# Navigate to project
cd ext_auth

# Run the app
python main.py
```

Visit http://localhost:8000

## 📞 Support

If errors persist after deployment, the error handler will now show:
- The exact Python error
- Full traceback
- Line numbers

Share this information for faster debugging.

---

**Ready to deploy!** 🎉
