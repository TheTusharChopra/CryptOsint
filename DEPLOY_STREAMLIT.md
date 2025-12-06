# 🚀 How to Deploy to Streamlit Cloud

## Step-by-Step Guide

### Option 1: Deploy via Streamlit Cloud (Recommended - Free!)

#### Step 1: Push Your Code to GitHub

1. **Create a GitHub account** (if you don't have one): https://github.com
2. **Create a new repository**:
   - Click the "+" icon → "New repository"
   - Name it (e.g., `cryptosint`)
   - Make it **Public** (required for free Streamlit Cloud)
   - Don't initialize with README (you already have files)
   - Click "Create repository"

3. **Push your code to GitHub**:

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: CryptoSint transaction analyzer"

# Add your GitHub repository as remote
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**Or use GitHub Desktop/GitHub CLI** if you prefer a GUI.

#### Step 2: Deploy to Streamlit Cloud

1. **Go to Streamlit Cloud**: https://share.streamlit.io/
2. **Sign in** with your GitHub account
3. **Click "New app"**
4. **Fill in the details**:
   - **Repository**: Select your repository from the dropdown
   - **Branch**: `main` (or `master`)
   - **Main file path**: `streamlit_app.py`
   - **App URL** (optional): Choose a custom subdomain
5. **Click "Deploy"**
6. **Wait 2-3 minutes** for deployment
7. **Your app is live!** 🎉

Your app will be available at: `https://YOUR-APP-NAME.streamlit.app`

---

### Option 2: Deploy via Streamlit Community Cloud (New)

1. Go to: https://streamlit.io/cloud
2. Sign in with GitHub
3. Click "New app"
4. Select your repository
5. Set main file: `streamlit_app.py`
6. Deploy!

---

## 📋 Pre-Deployment Checklist

Before deploying, make sure:

- ✅ All files are committed to GitHub
- ✅ `streamlit_app.py` is in the root directory
- ✅ `requirements_streamlit.txt` exists with all dependencies
- ✅ `crypto.py` is included
- ✅ No sensitive data (API keys) are hardcoded (use environment variables)

---

## 🔐 Adding API Key (Optional but Recommended)

### Method 1: Environment Variables in Streamlit Cloud

1. In Streamlit Cloud, go to your app settings
2. Click "Secrets" tab
3. Add your API key:

```toml
API_TOKEN = "your-blockcypher-api-key-here"
```

4. Update `crypto.py` to read from secrets:

```python
import streamlit as st

# Try to get from Streamlit secrets, fallback to hardcoded
try:
    API_TOKEN = st.secrets.get("API_TOKEN", "<YOUR-API-KEY>")
except:
    API_TOKEN = "<YOUR-API-KEY>"
```

### Method 2: Keep it in code (not recommended for production)

Just update `crypto.py` directly (but don't commit sensitive keys to public repos).

---

## 🐛 Troubleshooting

### App won't deploy?

**Error: "Module not found"**
- Check `requirements_streamlit.txt` includes all dependencies
- Make sure all imports are available

**Error: "File not found"**
- Ensure `streamlit_app.py` is in the root directory
- Check the main file path in Streamlit Cloud settings

**Error: "App crashed"**
- Check the logs in Streamlit Cloud dashboard
- Look for error messages
- Verify all file paths are correct

### App is slow?

- BlockCypher API has rate limits
- Consider adding your API key for higher limits
- Add delays between API calls if needed

---

## 📝 Quick Commands

```bash
# Check if everything is ready
ls -la streamlit_app.py crypto.py requirements_streamlit.txt

# Test locally before deploying
streamlit run streamlit_app.py

# If using git for the first time
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

---

## 🎯 After Deployment

1. **Share your app URL** with others
2. **Monitor usage** in Streamlit Cloud dashboard
3. **Update code** by pushing to GitHub (auto-deploys)
4. **Check logs** if something goes wrong

---

## 📚 Additional Resources

- Streamlit Cloud Docs: https://docs.streamlit.io/streamlit-community-cloud
- GitHub Guide: https://guides.github.com/
- Streamlit Documentation: https://docs.streamlit.io/

---

## ✅ Success Checklist

- [ ] Code pushed to GitHub
- [ ] Repository is public (for free tier)
- [ ] `streamlit_app.py` exists in root
- [ ] `requirements_streamlit.txt` has all dependencies
- [ ] App deployed on Streamlit Cloud
- [ ] App URL is working
- [ ] Tested with a real transaction hash

---

**Need help?** Check Streamlit Cloud logs or GitHub issues!

