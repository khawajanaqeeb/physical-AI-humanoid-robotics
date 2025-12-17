# Railway Deployment Guide

Complete guide for deploying the RAG Chatbot Backend to Railway and integrating with Vercel frontend.

## Prerequisites

- [x] Railway account created (https://railway.app)
- [x] GitHub repository connected
- [ ] Cohere API key (https://dashboard.cohere.com/api-keys)
- [ ] Qdrant Cloud cluster (https://cloud.qdrant.io/)

## Step 1: Deploy Backend to Railway

### 1.1 Create New Project

1. Go to https://railway.app
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Authorize Railway to access your GitHub account
5. Select repository: `khawajanaqeeb/physical-AI-humanoid-robotics`
6. Railway will detect the repository

### 1.2 Configure Root Directory

**IMPORTANT:** Railway needs to know your backend is in a subdirectory.

1. After selecting the repo, Railway will create a service
2. Click on the service (it will be named something like "physical-AI-humanoid-robotics")
3. Go to **Settings** tab
4. Find **"Root Directory"** setting
5. Set it to: `backend`
6. Click **"Save"**

### 1.3 Set Environment Variables

Go to **Variables** tab and add these environment variables:

#### Required Variables:

```bash
# Cohere API (Get from: https://dashboard.cohere.com/api-keys)
COHERE_API_KEY=your-cohere-api-key-here

# Qdrant Cloud (Get from: https://cloud.qdrant.io/)
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your-qdrant-api-key-here
QDRANT_COLLECTION_NAME=textbook_chunks

# Textbook Configuration
TEXTBOOK_SITEMAP_URL=https://physical-ai-humanoid-robotics-e3c7.vercel.app/sitemap.xml

# CORS Configuration (Your Vercel frontend URL)
CORS_ORIGINS=https://physical-ai-humanoid-robotics-e3c7.vercel.app,http://localhost:3000

# Optional: API Security (leave empty for now)
API_KEY=
```

#### How to Add Variables:

1. Click **"New Variable"**
2. Enter variable name (e.g., `COHERE_API_KEY`)
3. Enter variable value
4. Click **"Add"**
5. Repeat for all variables above

### 1.4 Deploy

1. Railway will automatically start deploying after you add variables
2. Wait for deployment to complete (usually 2-5 minutes)
3. Check the **Deployments** tab for progress
4. Look for "✓ SUCCESS" message

### 1.5 Get Your Backend URL

1. Go to **Settings** tab
2. Scroll to **"Networking"** section
3. Click **"Generate Domain"**
4. Railway will generate a URL like: `https://your-app.up.railway.app`
5. **COPY THIS URL** - you'll need it for Vercel

### 1.6 Test Your Backend

Test the health endpoint:

```bash
curl https://your-app.up.railway.app/health
```

You should see:
```json
{"status":"healthy","service":"rag-chatbot-api","version":"1.0.0"}
```

## Step 2: Configure Vercel Frontend

### 2.1 Add Backend URL to Vercel

1. Go to https://vercel.com/dashboard
2. Select your project: `physical-AI-humanoid-robotics`
3. Go to **Settings** → **Environment Variables**
4. Click **"Add New"**

Add this variable:
- **Name:** `BACKEND_URL`
- **Value:** `https://your-app.up.railway.app` (use your actual Railway URL)
- **Environment:** Check all: Production, Preview, Development
- Click **"Save"**

### 2.2 Redeploy Vercel

Two options:

**Option A: Trigger from Dashboard**
1. Go to **Deployments** tab
2. Click the three dots (•••) on the latest deployment
3. Click **"Redeploy"**
4. Wait for deployment to complete

**Option B: Push to GitHub**
```bash
# Make any small change and push
git commit --allow-empty -m "Trigger Vercel redeploy with Railway backend"
git push origin main
```

### 2.3 Verify Integration

1. Open your Vercel site: https://physical-ai-humanoid-robotics-e3c7.vercel.app/
2. Open the chatbot widget (bottom-right corner)
3. Ask a question: "What is physical AI?"
4. You should get a response with citations

## Step 3: Test Mobile Access

1. Open https://physical-ai-humanoid-robotics-e3c7.vercel.app/ on your mobile device
2. Open the chatbot widget
3. Ask a question
4. **The "fetch failed" error should be gone** ✓

## Troubleshooting

### Backend Issues

**Deployment Failed:**
- Check Railway logs: Click on deployment → View Logs
- Verify all environment variables are set correctly
- Ensure Root Directory is set to `backend`

**Health Check Fails:**
```bash
# Test your Railway backend
curl https://your-app.up.railway.app/health
```

**CORS Errors:**
- Verify `CORS_ORIGINS` includes your Vercel URL
- No trailing slash in URLs

### Frontend Issues

**Still Getting "fetch failed":**
- Clear browser cache (Ctrl+Shift+R / Cmd+Shift+R)
- Verify Vercel environment variable is set
- Check browser console for actual error
- Verify Railway backend is accessible

**Environment Variable Not Working:**
- Make sure you redeployed Vercel AFTER adding the variable
- Check Environment Variables are set for all environments
- Try a fresh deployment

### Check Backend Logs

Railway Logs:
1. Go to your Railway project
2. Click on your service
3. Click **"View Logs"** tab
4. Look for errors or issues

## File Reference

Railway uses these files:

- ✅ `Procfile` - Defines start command
- ✅ `requirements.txt` - Python dependencies
- ✅ `runtime.txt` - Python version (3.11)
- ✅ `railway.json` - Railway-specific config
- ✅ `.env.example` - Environment variable template

## API Endpoints

Once deployed, your backend will have these endpoints:

- `GET /health` - Health check
- `POST /api/v1/query` - Submit chatbot query
- `POST /api/v1/ingest` - Ingest content (protected by API_KEY)
- `GET /` - API information

## Next Steps

After successful deployment:

1. ✓ Test on desktop browser
2. ✓ Test on mobile device
3. ✓ Verify citations are working
4. Consider setting up monitoring (Railway provides built-in metrics)
5. Set up API_KEY for production security

## Cost Information

**Railway:**
- Free tier: $5 credit/month
- Pay-as-you-go after credits
- Typical usage: ~$5-10/month for this app

**Qdrant Cloud:**
- Free tier: 1GB storage
- Sufficient for this textbook

**Cohere:**
- Free tier available
- Pay-as-you-go for production

## Support

If you encounter issues:
1. Check Railway logs
2. Check Vercel logs
3. Review this guide
4. Contact support or create GitHub issue
