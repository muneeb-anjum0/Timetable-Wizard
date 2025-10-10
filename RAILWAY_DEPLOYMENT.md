# 🚀 Railway Deployment Guide - Timetable Wizard

## 📋 Prerequisites

1. **GitHub Repository**: Push your code to GitHub
2. **Railway Account**: Sign up at [railway.app](https://railway.app)
3. **Supabase Account**: Set up database at [supabase.com](https://supabase.com)
4. **Gmail API Credentials**: Set up Google Cloud Console project

## 🎯 A-Z Deployment Steps

### 1. Setup Supabase Database

1. **Create Supabase Project**:
   - Go to [supabase.com](https://supabase.com)
   - Create new project
   - Note down your Project URL and Service Role Key

2. **Create Required Tables**:
   ```sql
   -- Users table
   CREATE TABLE users (
     id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
     email TEXT UNIQUE NOT NULL,
     created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
   );

   -- Tokens table
   CREATE TABLE tokens (
     id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
     user_id UUID REFERENCES users(id) ON DELETE CASCADE,
     token_data JSONB NOT NULL,
     created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
   );

   -- Timetable cache table
   CREATE TABLE timetable_cache (
     id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
     user_id UUID REFERENCES users(id) ON DELETE CASCADE,
     cache_data JSONB NOT NULL,
     created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
   );

   -- User settings table
   CREATE TABLE user_settings (
     id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
     user_id UUID REFERENCES users(id) ON DELETE CASCADE,
     settings JSONB NOT NULL DEFAULT '{}',
     created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
     updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
   );
   ```

### 2. Setup Gmail API

1. **Google Cloud Console**:
   - Go to [console.cloud.google.com](https://console.cloud.google.com)
   - Create new project or select existing one
   - Enable Gmail API
   - Create OAuth 2.0 credentials
   - Download `client_secret.json`

2. **Upload credentials to Railway**:
   - We'll add this as environment variable in Railway

### 3. Deploy to Railway

#### Option A: Using Railway Dashboard (Recommended)

1. **Create Railway Project**:
   - Go to [railway.app](https://railway.app)
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Connect your GitHub account and select your repository

2. **Deploy Backend Service**:
   - Click "Add Service"
   - Select "GitHub Repo"
   - Choose your repository
   - Set **Root Directory**: `backend`
   - Railway will auto-detect Python and use our Dockerfile

3. **Deploy Frontend Service**:
   - Click "Add Service" again
   - Select "GitHub Repo" 
   - Choose the same repository
   - Set **Root Directory**: `frontend`
   - Railway will auto-detect Node.js and use our Dockerfile

#### Option B: Using Railway CLI

1. **Install Railway CLI**:
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway**:
   ```bash
   railway login
   ```

3. **Create and Deploy**:
   ```bash
   # Run our deployment script
   ./deploy-railway.sh  # Linux/Mac
   # OR
   deploy-railway.bat   # Windows
   ```

### 4. Configure Environment Variables

#### Backend Environment Variables (In Railway Dashboard):

| Variable Name | Value | Description |
|---------------|--------|-------------|
| `SUPABASE_URL` | `https://your-project.supabase.co` | Your Supabase project URL |
| `SUPABASE_SERVICE_KEY` | `eyJ...` | Your Supabase service role key |
| `TZ` | `Asia/Karachi` | Timezone (optional) |
| `CHECK_HOUR_LOCAL` | `20` | Schedule check hour (optional) |
| `CHECK_MINUTE_LOCAL` | `0` | Schedule check minute (optional) |
| `NEWER_THAN_DAYS` | `2` | Email search range (optional) |
| `FLASK_ENV` | `production` | Flask environment |
| `PYTHONPATH` | `/app` | Python path |

#### Frontend Environment Variables (In Railway Dashboard):

| Variable Name | Value | Description |
|---------------|--------|-------------|
| `REACT_APP_API_URL` | `https://your-backend-service.up.railway.app` | Backend service URL |

**Note**: Railway will automatically provide the backend URL once deployed.

### 5. Setup Service Communication

1. **Get Backend URL**:
   - In Railway dashboard, go to your backend service
   - Copy the generated domain (e.g., `https://backend-production-xxxx.up.railway.app`)

2. **Update Frontend Environment**:
   - Set `REACT_APP_API_URL` to your backend URL

### 6. Upload Gmail Credentials

Since we can't upload files directly to Railway, we'll handle credentials through environment variables:

1. **Convert client_secret.json to base64**:
   ```bash
   # Linux/Mac
   base64 -i client_secret.json
   
   # Windows (PowerShell)
   [Convert]::ToBase64String([IO.File]::ReadAllBytes("client_secret.json"))
   ```

2. **Add to Railway Environment Variables**:
   - Variable: `GOOGLE_CREDENTIALS_BASE64`
   - Value: The base64 string from step 1

3. **Update Backend Code** (if needed):
   - The app will automatically handle credentials

### 7. Verify Deployment

1. **Check Backend**:
   - Visit your backend URL + `/health` (e.g., `https://your-backend.up.railway.app/health`)
   - Should return service status

2. **Check Frontend**:
   - Visit your frontend URL
   - Should load the application

3. **Test API Connection**:
   - Try logging in with Gmail
   - Check if data loads properly

## 🔧 Troubleshooting

### Common Issues:

1. **Build Fails**:
   - Check Railway logs in dashboard
   - Ensure all dependencies are in requirements.txt/package.json

2. **Environment Variables Not Working**:
   - Double-check variable names (case-sensitive)
   - Restart services after adding variables

3. **CORS Issues**:
   - Ensure frontend `REACT_APP_API_URL` points to correct backend URL
   - Check backend CORS configuration

4. **Database Connection Issues**:
   - Verify Supabase credentials
   - Check if tables exist
   - Ensure service role key has proper permissions

### Useful Railway Commands:

```bash
# View logs
railway logs

# Connect to shell
railway shell

# View services
railway status

# Deploy specific service
railway up --service backend
railway up --service frontend
```

## 💰 Cost Management

### Railway Free Tier Limits:
- $5 worth of usage per month
- Includes compute, memory, and bandwidth
- Services sleep after inactivity

### Optimization Tips:
- Use lightweight Docker images
- Set reasonable resource limits
- Monitor usage in Railway dashboard
- Consider using hobby plan ($5/month) for better performance

## 🔄 Continuous Deployment

Railway automatically redeploys when you push to your connected GitHub repository:

1. **Auto-Deploy Setup**:
   - Link Railway services to GitHub branches
   - Push changes to trigger auto-deployment

2. **Manual Deploy**:
   - Use Railway dashboard "Deploy" button
   - Or use CLI: `railway up`

## 📊 Monitoring

1. **Railway Dashboard**:
   - View service metrics
   - Check logs and errors
   - Monitor resource usage

2. **Application Logs**:
   - Backend logs available in Railway dashboard
   - Frontend build logs show any issues

## 🎉 Success!

Your Timetable Wizard should now be fully deployed on Railway with:
- ✅ Backend API running on Railway
- ✅ Frontend app running on Railway  
- ✅ Supabase database connected
- ✅ Gmail API integration working
- ✅ Auto-deployment from GitHub
- ✅ Free tier hosting (within limits)

Access your app at the Railway-provided URLs and enjoy your deployed Timetable Wizard! 🚀