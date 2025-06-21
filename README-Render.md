# 🚀 Deploy Internshala Scraper to Render

This guide will walk you through deploying your Internshala Scraper application to Render.

## 📋 Prerequisites

- A Render account (free tier available)
- Your code pushed to a Git repository (GitHub, GitLab, etc.)
- Python 3.8+ support

## 🎯 Quick Deployment Steps

### 1. Prepare Your Repository

Make sure your repository contains these files:
- `app.py` - Main Flask application
- `requirements.txt` - Python dependencies
- `render.yaml` - Render configuration
- `build.sh` - Build script
- `templates/index.html` - Web interface

### 2. Deploy to Render

#### Option A: Using render.yaml (Recommended)

1. **Connect your repository** to Render
2. **Create a new Web Service**
3. **Select your repository**
4. **Render will automatically detect the `render.yaml`** and configure everything
5. **Deploy!**

#### Option B: Manual Configuration

1. **Go to Render Dashboard**
2. **Click "New +" → "Web Service"**
3. **Connect your Git repository**
4. **Configure the service:**

   **Build Command:**
   ```bash
   chmod +x build.sh && ./build.sh
   ```

   **Start Command:**
   ```bash
   python app.py
   ```

   **Environment Variables:**
   ```
   FLASK_ENV=production
   FLASK_DEBUG=0
   PYTHONUNBUFFERED=1
   ```

## ⚙️ Configuration Details

### render.yaml Configuration

The `render.yaml` file automatically configures:

- **Environment**: Python
- **Plan**: Starter (free tier)
- **Build Command**: Installs dependencies and Playwright browsers
- **Start Command**: Runs the Flask application
- **Health Check**: `/` endpoint
- **Auto Deploy**: Enabled

### Environment Variables

| Variable | Value | Purpose |
|----------|-------|---------|
| `FLASK_ENV` | `production` | Production environment |
| `FLASK_DEBUG` | `0` | Disable debug mode |
| `PYTHONUNBUFFERED` | `1` | Unbuffered output |
| `PORT` | `8000` | Application port |

### Build Process

The build script (`build.sh`) performs:

1. **Install Python dependencies** from `requirements.txt`
2. **Install Playwright browsers** (Chromium)
3. **Install system dependencies** for Playwright

## 🔧 Customization

### Changing Plans

To use a different plan, update `render.yaml`:

```yaml
services:
  - type: web
    name: internshala-scraper
    env: python
    plan: starter  # Change to: starter, standard, pro, etc.
```

### Adding Environment Variables

Add to `render.yaml`:

```yaml
envVars:
  - key: CUSTOM_VAR
    value: custom_value
  - key: SECRET_VAR
    sync: false  # For secrets
```

### Custom Domain

1. **Go to your service settings**
2. **Click "Custom Domains"**
3. **Add your domain**
4. **Configure DNS** as instructed

## 📊 Monitoring & Logs

### View Logs

1. **Go to your service dashboard**
2. **Click "Logs" tab**
3. **View real-time logs**

### Health Checks

The application includes a health check endpoint:
- **URL**: `https://your-app.onrender.com/health`
- **Response**: `{"status": "healthy", "message": "Internshala Scraper is running"}`

### Performance Monitoring

Render provides:
- **Response times**
- **Error rates**
- **Request counts**
- **Resource usage**

## 🔍 Troubleshooting

### Common Issues

#### 1. Build Failures

**Problem**: Build fails during Playwright installation
**Solution**: 
- Check if `build.sh` is executable
- Ensure all dependencies are in `requirements.txt`
- Check Render logs for specific errors

#### 2. Runtime Errors

**Problem**: Application crashes after deployment
**Solution**:
- Check application logs
- Verify environment variables
- Ensure Playwright browsers are installed

#### 3. Timeout Issues

**Problem**: Requests timeout during scraping
**Solution**:
- Increase timeout in `app.py`
- Check if target website is accessible
- Monitor resource usage

#### 4. Memory Issues

**Problem**: Application runs out of memory
**Solution**:
- Upgrade to a higher plan
- Optimize scraping logic
- Reduce concurrent requests

### Debug Commands

```bash
# Check if Playwright is installed
playwright --version

# Test browser installation
playwright install --dry-run

# Check Python dependencies
pip list

# Test the application locally
python app.py
```

## 📈 Scaling

### Auto Scaling

Render automatically scales based on:
- **Traffic patterns**
- **Resource usage**
- **Plan limits**

### Manual Scaling

1. **Go to service settings**
2. **Click "Scaling"**
3. **Adjust instance count**

### Performance Optimization

- **Use caching** for repeated requests
- **Implement rate limiting**
- **Optimize database queries**
- **Use CDN** for static assets

## 🔒 Security

### Environment Variables

- **Never commit secrets** to your repository
- **Use Render's secret management** for sensitive data
- **Rotate secrets** regularly

### HTTPS

- **Render provides free SSL certificates**
- **HTTPS is enabled by default**
- **No additional configuration needed**

### Rate Limiting

Consider implementing rate limiting:
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
```

## 💰 Cost Optimization

### Free Tier Limits

- **750 hours/month** of runtime
- **512 MB RAM**
- **Shared CPU**
- **Sleep after 15 minutes** of inactivity

### Upgrading Plans

Consider upgrading if you need:
- **More memory** for complex scraping
- **Faster CPU** for better performance
- **Always-on** service (no sleep)
- **Custom domains**

## 🚀 Advanced Features

### Background Jobs

For long-running scraping tasks:
1. **Use Render's Background Workers**
2. **Implement job queues**
3. **Use external services** (Redis, PostgreSQL)

### Database Integration

To add a database:
1. **Create a PostgreSQL service** on Render
2. **Update environment variables**
3. **Modify application** to use database

### CI/CD Integration

Set up automatic deployments:
1. **Connect GitHub repository**
2. **Enable auto-deploy**
3. **Configure deployment hooks**

## 📞 Support

### Render Support

- **Documentation**: [render.com/docs](https://render.com/docs)
- **Community**: [community.render.com](https://community.render.com)
- **Email**: support@render.com

### Application Issues

1. **Check Render logs**
2. **Test locally** first
3. **Review error messages**
4. **Check dependencies**

## 🎉 Success Checklist

- [ ] Application deploys successfully
- [ ] Health check passes
- [ ] Web interface loads
- [ ] Scraping functionality works
- [ ] Logs show no errors
- [ ] Performance is acceptable
- [ ] SSL certificate is active
- [ ] Custom domain works (if configured)

---

**Note**: This deployment guide is optimized for Render's platform. The application is configured to work efficiently within Render's constraints while maintaining full functionality. 