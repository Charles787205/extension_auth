# MongoDB Setup for Vercel Deployment

This guide will help you set up MongoDB Atlas (cloud MongoDB) for your FastAPI application deployed on Vercel.

## Step 1: Set Up MongoDB Atlas

1. **Create a MongoDB Atlas Account**
   - Go to https://www.mongodb.com/cloud/atlas/register
   - Sign up for a free account (no credit card required)

2. **Create a Cluster**
   - Click "Build a Database"
   - Select the FREE tier (M0)
   - Choose a cloud provider and region close to your users
   - Click "Create Cluster"

3. **Set Up Database Access**
   - Go to "Database Access" in the left sidebar
   - Click "Add New Database User"
   - Choose "Password" authentication
   - Create a username and strong password (save these!)
   - Set privileges to "Read and write to any database"
   - Click "Add User"

4. **Set Up Network Access**
   - Go to "Network Access" in the left sidebar
   - Click "Add IP Address"
   - Click "Allow Access from Anywhere" (0.0.0.0/0)
   - Click "Confirm"
   - Note: For production, you might want to restrict this to specific IPs

5. **Get Your Connection String**
   - Go to "Database" in the left sidebar
   - Click "Connect" on your cluster
   - Choose "Connect your application"
   - Select "Python" and version "3.12 or later"
   - Copy the connection string (looks like: `mongodb+srv://username:<password>@cluster.mongodb.net/...`)
   - Replace `<password>` with your actual database user password
   - Replace `<database>` with your database name (e.g., `ext_auth`)

## Step 2: Local Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create a `.env` File**
   ```bash
   cp .env.example .env
   ```

3. **Edit `.env` File**
   - Open `.env` and paste your MongoDB connection string
   - Example:
     ```
     MONGODB_URL=mongodb+srv://myuser:mypassword@cluster0.xxxxx.mongodb.net/ext_auth?retryWrites=true&w=majority
     DATABASE_NAME=ext_auth
     ```

4. **Initialize the Database**
   ```bash
   python init_db.py
   ```
   This will create the default admin user and set up initial data.

5. **Run Locally**
   ```bash
   python main.py
   ```
   Visit http://localhost:8000 and login with:
   - Username: `admin`
   - Password: `password`

## Step 3: Deploy to Vercel

1. **Create `vercel.json`** (if not exists)
   ```json
   {
     "builds": [
       {
         "src": "main.py",
         "use": "@vercel/python"
       }
     ],
     "routes": [
       {
         "src": "/(.*)",
         "dest": "main.py"
       }
     ]
   }
   ```

2. **Install Vercel CLI** (optional)
   ```bash
   npm install -g vercel
   ```

3. **Deploy via Vercel Dashboard**
   - Go to https://vercel.com
   - Import your Git repository
   - Go to "Settings" → "Environment Variables"
   - Add your environment variables:
     - `MONGODB_URL`: Your MongoDB connection string
     - `DATABASE_NAME`: `ext_auth`
   - Click "Deploy"

4. **Initialize Production Database**
   - After deployment, run the init script locally with production credentials
   - Or create the admin user directly in MongoDB Atlas UI

## Step 4: Security Considerations

1. **Change Default Password**
   - Login to your app and change the admin password
   - Or update it directly in MongoDB Atlas

2. **Use Strong Passwords**
   - For database users
   - For application users

3. **Environment Variables**
   - Never commit `.env` file to Git
   - Keep `.env.example` updated without sensitive data
   - Make sure `.env` is in `.gitignore`

4. **HTTPS Only**
   - Vercel provides HTTPS by default
   - Always use HTTPS in production

## Troubleshooting

### Connection Issues
- Check if your IP is whitelisted in MongoDB Atlas Network Access
- Verify connection string is correct
- Ensure password doesn't contain special characters that need URL encoding

### Database Not Initializing
- Run `python init_db.py` manually
- Check MongoDB Atlas logs for errors
- Verify DATABASE_NAME matches in your connection string and .env

### Vercel Deployment Issues
- Check Vercel logs for errors
- Ensure all environment variables are set
- Verify `vercel.json` is in the root directory

## File Structure

```
ext_auth/
├── main.py              # FastAPI application
├── database.py          # MongoDB connection handler
├── init_db.py          # Database initialization script
├── requirements.txt     # Python dependencies
├── .env                # Environment variables (NOT in Git)
├── .env.example        # Example environment variables
├── templates/
│   ├── login.html
│   └── main.html
└── README_MONGODB.md   # This file
```

## MongoDB Collections

### credentials
Stores user credentials
```json
{
  "username": "admin",
  "password": "hashed_password"
}
```

### api_state
Stores API state
```json
{
  "_id": "current_state",
  "status": "on",
  "message": "API is enabled"
}
```

## Next Steps

- Implement password hashing (use `passlib` or `bcrypt`)
- Add more user management features
- Store sessions in MongoDB instead of memory
- Add user registration functionality
- Implement role-based access control
