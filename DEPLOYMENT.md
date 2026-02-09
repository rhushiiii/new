# PowerGuard Deployment Guide

## Overview

PowerGuard is a full-stack application requiring separate deployments:
- **Frontend** → Vercel (React + Vite)
- **Backend** → Render (FastAPI + PostgreSQL)

---

## Step 1: Deploy Backend to Render

### 1.1 Create a GitHub Repository

```bash
cd c:\Rhushi\New folder (2)\project4
git init
git add .
git commit -m "Initial commit - PowerGuard"
git remote add origin https://github.com/YOUR_USERNAME/powerguard.git
git push -u origin main
```

### 1.2 Create PostgreSQL Database on Render

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **New** → **PostgreSQL**
3. Fill in:
   - Name: `powerguard-db`
   - Region: Choose closest to you
   - Plan: Free
4. Click **Create Database**
5. Copy the **Internal Database URL** for later

### 1.3 Create Web Service on Render

1. Click **New** → **Web Service**
2. Connect your GitHub repository
3. Configure:
   - Name: `powerguard-api`
   - Root Directory: `backend`
   - Runtime: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

4. Add Environment Variables:
   ```
   DATABASE_URL = [paste Internal Database URL from step 1.2]
   USE_SQLITE = false
   CORS_ORIGINS = https://powerguard.vercel.app
   ```

5. Click **Create Web Service**
6. Wait for deployment (5-10 minutes)
7. Copy your backend URL (e.g., `https://powerguard-api.onrender.com`)

---

## Step 2: Deploy Frontend to Vercel

### 2.1 Install Vercel CLI (Optional)

```bash
npm install -g vercel
```

### 2.2 Update Environment Variable

Edit `frontend/.env.production`:
```
VITE_API_URL=https://powerguard-api.onrender.com
```

### 2.3 Deploy via Vercel Dashboard

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click **Add New** → **Project**
3. Import your GitHub repository
4. Configure:
   - Framework Preset: Vite
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `dist`

5. Add Environment Variable:
   ```
   VITE_API_URL = https://powerguard-api.onrender.com
   ```

6. Click **Deploy**

### 2.4 Deploy via CLI (Alternative)

```bash
cd frontend
vercel --prod
```

When prompted:
- Set up and deploy: Yes
- Link to existing project: No
- Project name: powerguard
- Directory: ./
- Override settings: No

---

## Step 3: Update CORS on Backend

After getting your Vercel URL, update the backend:

1. Go to Render Dashboard → powerguard-api → Environment
2. Update `CORS_ORIGINS`:
   ```
   CORS_ORIGINS = https://powerguard.vercel.app,https://your-custom-domain.com
   ```
3. Click **Save Changes** (auto-redeploys)

---

## Verification

1. Visit your Vercel URL (e.g., `https://powerguard.vercel.app`)
2. Go to Upload page and upload the mock data CSV
3. Run anomaly detection
4. Verify Dashboard shows statistics

---

## Troubleshooting

### CORS Errors
- Ensure `CORS_ORIGINS` on Render includes your Vercel domain
- Check browser console for specific error messages

### API Connection Failed
- Verify `VITE_API_URL` is correct in Vercel environment variables
- Check Render logs for backend errors

### Slow First Load
- Render free tier sleeps after 15 min of inactivity
- First request may take 30-60 seconds to wake up

---

## Custom Domain (Optional)

### Vercel
1. Go to Project Settings → Domains
2. Add your domain
3. Follow DNS configuration instructions

### Render
1. Go to Service Settings → Custom Domains
2. Add your domain
3. Update DNS records as instructed

---

## Environment Variables Summary

### Backend (Render)
| Variable | Value |
|----------|-------|
| `DATABASE_URL` | PostgreSQL connection string |
| `USE_SQLITE` | `false` |
| `CORS_ORIGINS` | Your Vercel domain(s) |

### Frontend (Vercel)
| Variable | Value |
|----------|-------|
| `VITE_API_URL` | Your Render backend URL |
