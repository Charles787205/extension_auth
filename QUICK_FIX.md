# Quick Fix Guide

## Problem 1: Local DNS Timeout (init_db.py failing)

Your local network/firewall is blocking DNS resolution for MongoDB Atlas. Here are solutions:

### Option A: Get Standard Connection String (Recommended)
1. Go to MongoDB Atlas: https://cloud.mongodb.com
2. Click "Connect" on your cluster
3. Choose "Connect your application"
4. Select "Driver: Python" version "3.12 or later"
5. **Look for a toggle that says "Use connection string (SRV)"** - turn it OFF
6. Copy the standard connection string (starts with `mongodb://` not `mongodb+srv://`)
7. Replace the MONGODB_URL in your `.env` file

### Option B: Skip Local Initialization
You can initialize the database directly in MongoDB Atlas:
1. Go to MongoDB Atlas
2. Click "Browse Collections"
3. Create database: `extension`
4. Create collection: `credentials`
5. Add document manually:
   ```json
   {
     "username": "admin",
     "password": "password"
   }
   ```
6. Create collection: `api_state`
7. Add document:
   ```json
   {
     "_id": "current_state",
     "status": "off",
     "message": "API is currently disabled"
   }
   ```

### Option C: Disable IPv6 (Windows)
Some networks have IPv6 issues. Try:
```powershell
netsh interface ipv6 set privacy state=disabled
```

## Problem 2: Vercel Deployment

### Critical Changes Made:
1. ✅ Created `api/index.py` - Vercel entry point
2. ✅ Updated `vercel.json` - Proper routing
3. ✅ Modified `database.py` - Better connection handling for serverless
4. ✅ Updated `main.py` - Serverless-compatible (no lifespan on Vercel)

### Deploy to Vercel:

1. **Push your code to GitHub**
   ```bash
   git add .
   git commit -m "Add MongoDB and Vercel support"
   git push
   ```

2. **In Vercel Dashboard:**
   - Go to your project settings
   - Navigate to "Environment Variables"
   - Add these variables:
     - Key: `MONGODB_URL`
     - Value: `mongodb+srv://joviancharles1210:Tn3T73SklEPMdG5h@extension.yldtxjz.mongodb.net/extension?retryWrites=true&w=majority`
     - Key: `DATABASE_NAME`
     - Value: `extension`
     - Key: `VERCEL`
     - Value: `1`

3. **Redeploy**
   - Vercel should auto-deploy on git push
   - Or manually redeploy from Vercel dashboard

### Check Vercel Logs:
If it still fails:
1. Go to your Vercel project
2. Click on the failed deployment
3. Click "View Function Logs"
4. Share the error message

## File Structure After Changes:
```
ext_auth/
├── api/
│   └── index.py          # NEW - Vercel entry point
├── main.py               # UPDATED - Serverless compatible
├── database.py           # UPDATED - Better error handling
├── vercel.json           # UPDATED - Correct routing
├── .vercelignore         # NEW - Exclude files from deployment
├── .env                  # Your MongoDB connection string
└── requirements.txt      # Dependencies
```

## Testing:

### Test Locally (after fixing .env):
```bash
python main.py
```

### Test Vercel Deployment:
After deploying, visit: `https://your-app.vercel.app`

## Common Issues:

### "Database not connected"
- Make sure MONGODB_URL is set in Vercel environment variables
- Check MongoDB Atlas network access allows 0.0.0.0/0

### "Static files not found"
- Make sure `templates/` folder is in your repository
- Vercel should include it automatically

### "Connection timeout"
- Check MongoDB Atlas cluster is running (not paused)
- Verify credentials in connection string
