# 🚀 Quick Start Guide - Streamlit Version

## Installation & Run

### Step 1: Install Streamlit (if not already installed)
```bash
pip install streamlit
```

Or install all requirements:
```bash
pip install -r requirements_streamlit.txt
```

### Step 2: Run the Streamlit App
```bash
streamlit run streamlit_app.py
```

The app will automatically open in your browser at `http://localhost:8501`

## 🎯 How to Use

1. **Select Cryptocurrency** from the sidebar (default: Bitcoin)
2. **Enter Transaction Hash** in the main input field
3. **Click "Analyze Transaction"** button
4. **View Results**:
   - Input wallets with balances
   - End wallets (final recipients)
   - Suspicious wallet clusters (DBSCAN analysis)
   - Summary statistics

## 📝 Example Transaction Hash

Try this Bitcoin transaction:
```
ed1b8647be6a514e589e9450255f7e85fee534c6b2536f8a04f64ed330087e7b
```

Or this one:
```
c66f6ed957295218590fd854c910fd516d43d5efcf55b52d92fe6240cfe9c574
```

## 🌐 Deploy to Streamlit Cloud (Free)

1. Push your code to GitHub
2. Go to https://share.streamlit.io/
3. Sign in with GitHub
4. Click "New app"
5. Select your repository
6. Set main file: `streamlit_app.py`
7. Click "Deploy"

Your app will be live at: `https://your-app-name.streamlit.app`

## ⚙️ Configuration

### Add API Key (Optional but Recommended)

Edit `crypto.py` and replace:
```python
API_TOKEN = '<YOUR-API-KEY>'
```

With your BlockCypher API key from: https://www.blockcypher.com/dev/

This will give you higher rate limits and better reliability.

## 🆚 Flask vs Streamlit

Both versions work the same way! Choose based on your preference:

- **Flask**: More control, traditional web app, requires HTML/CSS knowledge
- **Streamlit**: Easier to use, modern UI, faster to deploy, great for data apps

## 🐛 Troubleshooting

**App won't start?**
- Make sure Streamlit is installed: `pip install streamlit`
- Check Python version: `python --version` (needs 3.8+)

**Transaction not found?**
- Verify the hash is correct
- Check you selected the right cryptocurrency
- Wait a moment if you hit rate limits

**Need help?**
- Check `README_STREAMLIT.md` for detailed documentation
- Review error messages in the Streamlit interface

