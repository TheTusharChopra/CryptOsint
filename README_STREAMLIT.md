# 🚨 CryptoSint - Streamlit Version

**CryptoSint** is a blockchain transaction analysis tool that helps trace suspicious cryptocurrency activity. This is the Streamlit version of the application.

## 🔍 Features

- 🧾 **Transaction Hash Lookup** – Search any cryptocurrency transaction by its hash
- 🧠 **Suspicious Wallet Detection** – Uses DBSCAN clustering to identify wallets with abnormal transaction behavior
- 💰 **Multi-Cryptocurrency Support** – Bitcoin, Ethereum, Litecoin, Bitcoin Cash, Dogecoin, Dash
- ⚡ **Unconfirmed Transaction Support** – Works with mempool transactions
- 🇮🇳 **Indian Currency Formatting** – Displays INR values with lakhs/crores formatting
- 📊 **Interactive UI** – Clean, modern Streamlit interface

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements_streamlit.txt
```

Or install individually:
```bash
pip install streamlit requests scikit-learn numpy
```

### 2. Run the Streamlit App

```bash
streamlit run streamlit_app.py
```

The app will automatically open in your browser at `http://localhost:8501`

## 📋 Usage

1. **Select Cryptocurrency**: Choose from the sidebar (default: Bitcoin)
2. **Enter Transaction Hash**: Paste the transaction hash you want to analyze
3. **Click "Analyze Transaction"**: Wait for the analysis to complete
4. **View Results**: 
   - Input wallets
   - End wallets
   - Suspicious wallet clusters
   - Summary statistics

## ⚙️ Configuration

### API Key (Optional but Recommended)

For better rate limits, add your BlockCypher API key to `crypto.py`:

```python
API_TOKEN = 'your-api-key-here'
```

Get a free API key at: https://www.blockcypher.com/dev/

### Currency Conversion Rates

Update conversion rates in `crypto.py` in the `CRYPTO_CONFIG` dictionary:

```python
'btc': {
    'conversion_rate': 5053094.57  # BTC to INR
}
```

## 🎨 Features Comparison

| Feature | Flask Version | Streamlit Version |
|---------|--------------|-------------------|
| Multi-crypto support | ✅ | ✅ |
| Unconfirmed transactions | ✅ | ✅ |
| Indian currency formatting | ✅ | ✅ |
| Suspicious wallet detection | ✅ | ✅ |
| Interactive UI | HTML/CSS | Streamlit native |
| Deployment | Flask server | Streamlit Cloud/Server |

## 🌐 Deployment

### Streamlit Cloud (Free)

1. Push your code to GitHub
2. Go to https://share.streamlit.io/
3. Connect your repository
4. Set main file to `streamlit_app.py`
5. Deploy!

### Local Server

```bash
streamlit run streamlit_app.py --server.port 8501
```

### Docker (Optional)

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements_streamlit.txt .
RUN pip install -r requirements_streamlit.txt

COPY . .

CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

## 📝 Notes

- The app uses BlockCypher API which has rate limits on the free tier
- For production use, consider adding your API key
- Unconfirmed transactions may take longer to process
- Large transaction chains may hit recursion depth limits

## 🐛 Troubleshooting

**"Transaction not found"**
- Verify the transaction hash is correct
- Check you've selected the right cryptocurrency
- Wait a moment if you hit rate limits
- Try again after a few seconds

**"No end wallets found"**
- The transaction chain might be very long
- All outputs might be spent (chain continues)
- API rate limiting might have interrupted tracing

**"No suspicious wallets detected"**
- Normal if wallets show similar patterns
- Need at least 2-3 wallets for clustering
- Clustering parameters might need adjustment

## 📄 License

See LICENSE file for details.

