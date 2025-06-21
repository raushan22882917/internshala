# Deploying Internshala Scraper on Render

This guide will walk you through deploying your Internshala Scraper application on Render.

## Prerequisites

1. **GitHub Account**: Your code should be in a GitHub repository
2. **Render Account**: Sign up at [render.com](https://render.com)
3. **Code Repository**: Your project should be pushed to GitHub

## Step-by-Step Deployment Guide

### Step 1: Prepare Your Repository

1. **Push your code to GitHub** (if not already done):
   ```bash
   git add .
   git commit -m "Add Render deployment configuration"
   git push origin main
   ```

2. **Ensure these files are in your repository**:
   - `app.py`
   - `requirements.txt`
   - `render.yaml` (created above)
   - `templates/index.html`
   - All other project files

### Step 2: Create Render Account

1. Go to [render.com](https://render.com)
2. Sign up using your GitHub account (recommended)
3. Verify your email address

### Step 3: Deploy on Render

#### Option A: Using render.yaml (Recommended)

1. **Connect your GitHub repository**:
   - In Render dashboard, click "New +"
   - Select "Blueprint" (if you have render.yaml)
   - Connect your GitHub account
   - Select your repository

2. **Deploy automatically**:
   - Render will automatically detect the `render.yaml` file
   - Click "Apply" to start deployment
   - Render will build and deploy your application

#### Option B: Manual Setup

1. **Create a new Web Service**:
   - In Render dashboard, click "New +"
   - Select "Web Service"
   - Connect your GitHub repository

2. **Configure the service**:
   - **Name**: `internshala-scraper`
   - **Environment**: `Python`
   - **Build Command**: 
     ```bash
     pip install -r requirements.txt && playwright install chromium && playwright install-deps chromium
     ```
   - **Start Command**: `python app.py`
   - **Health Check Path**: `/health`

3. **Set Environment Variables**:
   - `FLASK_ENV`: `production`
   - `PORT`: `8000`

4. **Deploy**:
   - Click "Create Web Service"
   - Render will start building and deploying your application

### Step 4: Monitor Deployment

1. **Watch the build logs**:
   - The build process will take 5-10 minutes
   - You can see real-time logs in the Render dashboard
   - Monitor for any errors during the build

2. **Check deployment status**:
   - Once deployed, you'll get a URL like: `https://your-app-name.onrender.com`
   - Test the health endpoint: `https://your-app-name.onrender.com/health`

### Step 5: Verify Deployment

1. **Test the application**:
   - Visit your Render URL
   - Test the search functionality
   - Check if downloads work

2. **Monitor logs**:
   - Go to your service dashboard
   - Check "Logs" tab for any errors
   - Monitor "Metrics" for performance

## Important Notes for Render Deployment

### 1. Free Tier Limitations
- **Sleep after inactivity**: Free services sleep after 15 minutes of inactivity
- **Build time**: Limited to 10 minutes
- **Request timeout**: 30 seconds maximum
- **Memory**: 512MB RAM limit

### 2. Playwright Considerations
- **Browser installation**: Takes time during build
- **Memory usage**: Chromium requires significant memory
- **Headless mode**: Always runs in headless mode on Render

### 3. File System Limitations
- **Ephemeral storage**: Files are not persistent between deployments
- **Downloads**: Excel files will be lost when the service restarts
- **Consider using external storage** for file persistence

## Troubleshooting Common Issues

### Build Fails
1. **Check requirements.txt**: Ensure all dependencies are listed
2. **Memory issues**: Free tier has 512MB limit
3. **Timeout**: Build might timeout on free tier

### Application Won't Start
1. **Check start command**: Ensure `python app.py` is correct
2. **Port configuration**: Render sets PORT environment variable
3. **Health check**: Ensure `/health` endpoint works

### Playwright Issues
1. **Browser installation**: Check build logs for browser installation
2. **Memory**: Free tier might not have enough memory for Chromium
3. **Timeout**: Web scraping might timeout on free tier

## Upgrading to Paid Plan

For better performance, consider upgrading to a paid plan:

1. **Starter Plan ($7/month)**:
   - 1GB RAM
   - No sleep mode
   - Faster builds
   - Better for Playwright

2. **Standard Plan ($25/month)**:
   - 2GB RAM
   - Better performance
   - More suitable for web scraping

## Environment Variables

You can set these in Render dashboard:

| Variable | Value | Description |
|----------|-------|-------------|
| `FLASK_ENV` | `production` | Production environment |
| `PORT` | `8000` | Application port |
| `PYTHONUNBUFFERED` | `1` | Unbuffered Python output |

## Custom Domain (Optional)

1. **Add custom domain**:
   - Go to your service settings
   - Click "Custom Domains"
   - Add your domain
   - Configure DNS records

2. **SSL certificate**:
   - Render provides free SSL certificates
   - Automatically configured for custom domains

## Monitoring and Maintenance

1. **Set up alerts**:
   - Configure email notifications for deployment status
   - Monitor service health

2. **Regular updates**:
   - Keep dependencies updated
   - Monitor for security patches

3. **Backup strategy**:
   - Consider external storage for downloads
   - Regular code backups to GitHub

## Support

If you encounter issues:
1. Check Render documentation: [docs.render.com](https://docs.render.com)
2. Review build and runtime logs
3. Contact Render support if needed

Your application should now be successfully deployed on Render! 🎉 