# Troubleshooting Render Deployment

## Common Issues and Solutions

### 1. Pandas Compilation Error

**Error**: `standard attributes in middle of decl-specifiers`

**Solution**: 
- Use Python 3.11 instead of 3.13
- Use older pandas version (2.0.3)
- Or use the alternative version without pandas

**Steps**:
1. Update `runtime.txt` to specify Python 3.11
2. Use the updated `requirements.txt` with pandas 2.0.3
3. If still failing, use `requirements_alternative.txt` and `app_alternative.py`

### 2. Playwright Installation Issues

**Error**: `playwright: command not found`

**Solution**: Use `python -m playwright` instead of direct command

**Updated build command**:
```bash
python -m playwright install chromium
python -m playwright install-deps chromium
```

### 3. Module Not Found Errors

**Error**: `ModuleNotFoundError: No module named 'playwright'`

**Solution**: Ensure proper installation order in build script

### 4. Build Timeout

**Error**: Build takes longer than 10 minutes

**Solution**: 
- Use pre-compiled wheels when possible
- Consider upgrading to paid plan
- Optimize build process

## Alternative Deployment Approach

If the main deployment continues to fail, use the alternative approach:

### Step 1: Use Alternative Files

1. **Rename files**:
   ```bash
   mv requirements.txt requirements_backup.txt
   mv requirements_alternative.txt requirements.txt
   mv app.py app_backup.py
   mv app_alternative.py app.py
   ```

2. **Update render.yaml**:
   ```yaml
   services:
     - type: web
       name: internshala-scraper
       env: python
       pythonVersion: "3.11"
       buildCommand: |
         pip install --upgrade pip setuptools wheel
         pip install -r requirements.txt
         python -m playwright install chromium
         python -m playwright install-deps chromium
       startCommand: python app.py
       envVars:
         - key: FLASK_ENV
           value: production
         - key: PORT
           value: 8000
       healthCheckPath: /health
   ```

### Step 2: Deploy Alternative Version

The alternative version:
- Uses CSV instead of Excel (no pandas dependency)
- Still includes all core functionality
- More lightweight and faster to build

## Manual Deployment Steps

If automatic deployment fails:

### 1. Clean Build
```bash
# In Render dashboard, delete the service
# Recreate with manual configuration
```

### 2. Manual Configuration
- **Environment**: Python
- **Python Version**: 3.11
- **Build Command**: 
  ```bash
  pip install --upgrade pip setuptools wheel && pip install -r requirements.txt && python -m playwright install chromium && python -m playwright install-deps chromium
  ```
- **Start Command**: `python app.py`
- **Health Check Path**: `/health`

### 3. Environment Variables
- `FLASK_ENV`: `production`
- `PORT`: `8000`
- `PYTHONUNBUFFERED`: `1`

## Performance Optimization

### For Free Tier:
1. **Reduce memory usage**:
   - Use single worker
   - Limit concurrent requests
   - Optimize Playwright usage

2. **Handle sleep mode**:
   - First request after sleep will be slow
   - Consider upgrading to paid plan

### For Paid Plans:
1. **Starter Plan ($7/month)**:
   - 1GB RAM
   - No sleep mode
   - Better for Playwright

2. **Standard Plan ($25/month)**:
   - 2GB RAM
   - Better performance
   - More suitable for web scraping

## Monitoring and Debugging

### 1. Check Build Logs
- Monitor real-time build logs in Render dashboard
- Look for specific error messages
- Check memory usage during build

### 2. Check Runtime Logs
- Monitor application logs after deployment
- Check for Playwright initialization issues
- Verify health check endpoint

### 3. Test Locally First
```bash
# Test build locally
docker build -t test-build .
docker run -it test-build python -c "import playwright; print('OK')"
```

## Fallback Options

If all else fails:

### 1. Use Different Platform
- **Railway**: Often more lenient with build times
- **Heroku**: Good Python support
- **DigitalOcean App Platform**: Reliable deployment

### 2. Simplify Application
- Remove Playwright dependency
- Use simpler web scraping (requests + BeautifulSoup)
- Focus on core functionality

### 3. Use External Services
- Deploy Playwright separately
- Use headless browser services
- API-based approach

## Contact Support

If issues persist:
1. Check Render documentation
2. Contact Render support with build logs
3. Consider community forums for specific errors

## Success Checklist

Before deploying, ensure:
- [ ] Python 3.11 specified
- [ ] Compatible pandas version
- [ ] Proper Playwright installation
- [ ] Health check endpoint working
- [ ] All dependencies listed in requirements.txt
- [ ] Build script executable
- [ ] Environment variables set correctly

# Troubleshooting Guide for Render Deployment

## Issue: Playwright Authentication Failure

### Problem
```
🔧 Installing Playwright system dependencies...
Installing dependencies...
Switching to root user to install dependencies...
Password: su: Authentication failure
Failed to install browser dependencies
Error: Installation process exited with code: 1
```

### Root Cause
Render's build environment doesn't allow switching to root user with `su`, which Playwright's `install-deps` command requires.

### Solutions

#### Solution 1: Use Modified Build Script (Recommended)
The `build.sh` file has been updated to use the `--with-deps` flag instead of separate `install-deps` command:

```bash
# Instead of:
python -m playwright install-deps chromium

# Use:
python -m playwright install chromium --with-deps
```

#### Solution 2: Use Selenium Alternative
If Playwright continues to cause issues, use the Selenium-based alternative:

1. **Files to use:**
   - `app_alternative.py` (Selenium-based app)
   - `requirements_alternative.txt` (Selenium dependencies)
   - `build_alternative.sh` (Selenium build script)
   - `render_alternative.yaml` (Alternative render config)

2. **Deploy with alternative configuration:**
   ```bash
   # Use the alternative render configuration
   render deploy --config render_alternative.yaml
   ```

#### Solution 3: Use Docker Deployment
If web service deployment fails, use Docker:

1. **Use the existing Dockerfile** which properly handles Playwright installation
2. **Deploy as a Docker service** on Render

### Alternative Dependencies

#### Playwright Dependencies (Original)
```
flask
requests
beautifulsoup4
numpy
pandas
openpyxl
lxml
playwright
gunicorn
```

#### Selenium Dependencies (Alternative)
```
flask
requests
beautifulsoup4
numpy
pandas
openpyxl
lxml
selenium
webdriver-manager
gunicorn
```

### Build Scripts Comparison

#### Original Build Script (build.sh)
```bash
#!/bin/bash
set -e
echo "🚀 Starting build process..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
python -c "import playwright; print('Playwright imported successfully')"
python -m playwright install chromium
python -m playwright install chromium --with-deps  # Modified line
echo "✅ Build completed successfully!"
```

#### Alternative Build Script (build_alternative.sh)
```bash
#!/bin/bash
set -e
echo "🚀 Starting alternative build process with Selenium..."
pip install --upgrade pip setuptools wheel
pip install -r requirements_alternative.txt
python -c "import selenium; print('Selenium imported successfully')"
# Install Chrome dependencies directly
apt-get update && apt-get install -y [chrome-dependencies]
echo "✅ Alternative build completed successfully!"
```

### Render Configuration Files

#### Original (render.yaml)
```yaml
services:
  - type: web
    name: internshala-scraper
    env: python
    pythonVersion: "3.11"
    buildCommand: chmod +x build.sh && ./build.sh
    startCommand: python app.py
    # ... other config
```

#### Alternative (render_alternative.yaml)
```yaml
services:
  - type: web
    name: internshala-scraper-alternative
    env: python
    pythonVersion: "3.11"
    buildCommand: chmod +x build_alternative.sh && ./build_alternative.sh
    startCommand: python app_alternative.py
    # ... other config
```

### Testing Locally

#### Test Playwright Version
```bash
pip install -r requirements.txt
python -m playwright install chromium --with-deps
python app.py
```

#### Test Selenium Version
```bash
pip install -r requirements_alternative.txt
python app_alternative.py
```

### Common Issues and Fixes

1. **Permission Denied Errors**
   - Use the modified build script with `--with-deps`
   - Or switch to Selenium alternative

2. **Browser Installation Failures**
   - Ensure all system dependencies are installed
   - Use headless mode for production

3. **Memory Issues**
   - Reduce number of concurrent browser instances
   - Implement proper cleanup in the code

4. **Timeout Issues**
   - Increase timeout values in render.yaml
   - Implement proper error handling

### Performance Considerations

#### Playwright Advantages
- Better performance for complex web scraping
- Built-in waiting mechanisms
- Better handling of modern web applications

#### Selenium Advantages
- More stable on Render
- Better compatibility with older systems
- Easier to debug

### Recommended Approach

1. **First try:** Use the modified `build.sh` with `--with-deps` flag
2. **If that fails:** Switch to Selenium alternative
3. **For production:** Consider Docker deployment for better control

### Support

If you continue to experience issues:
1. Check Render's build logs for specific error messages
2. Verify all dependencies are correctly specified
3. Test the application locally before deploying
4. Consider using Render's Docker service instead of web service 