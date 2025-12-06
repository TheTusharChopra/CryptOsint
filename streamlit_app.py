import streamlit as st
from crypto import (
    trace_input_wallet, trace_transaction_chain, get_wallet_details,
    analyze_suspicious_wallets, summarize_funds, get_crypto_config,
    CRYPTO_CONFIG, get_transaction_details
)

# Page configuration
st.set_page_config(
    page_title="Cryptocurrency Transaction Analyzer",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 2px solid #ffc107;
        color: #856404;
    }
    .success-box {
        background-color: #d4edda;
        border: 2px solid #28a745;
        color: #155724;
    }
    .error-box {
        background-color: #ffebee;
        border: 2px solid #f44336;
        color: #c62828;
    }
    .wallet-card {
        background-color: #f1f8e9;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 4px solid #4caf50;
    }
    </style>
""", unsafe_allow_html=True)

def format_indian_currency(value):
    """
    Format number in Indian numbering system (lakhs, crores).
    Pattern: First 3 digits from right, then commas every 2 digits.
    Examples: 1,000 | 10,000 | 1,00,000 | 10,00,000 | 1,00,00,000
    """
    if value is None:
        return "0"
    
    try:
        # Convert to float then to int for whole numbers, or keep as float
        num = float(value)
        
        # Handle negative numbers
        is_negative = num < 0
        num = abs(num)
        
        # Split into integer and decimal parts
        if num == int(num):
            # Whole number
            num_str = str(int(num))
            decimal_part = ""
        else:
            # Decimal number
            num_str, decimal_str = f"{num:.2f}".split('.')
            decimal_part = f".{decimal_str}"
        
        # Apply Indian numbering system
        if len(num_str) <= 3:
            # No comma needed for numbers <= 999
            result = num_str
        else:
            # First 3 digits from right (no comma)
            result = num_str[-3:]
            remaining = num_str[:-3]
            
            # Then add commas every 2 digits
            while remaining:
                if len(remaining) <= 2:
                    result = remaining + ',' + result
                    break
                else:
                    result = remaining[-2:] + ',' + result
                    remaining = remaining[:-2]
        
        # Add decimal part if exists
        result += decimal_part
        
        # Add negative sign if needed
        if is_negative:
            result = '-' + result
            
        return result
    except (ValueError, TypeError):
        return str(value)

def display_wallet_info(wallet, config, label="Wallet"):
    """Display wallet information in a formatted card"""
    divisor = config['divisor']
    
    balance = wallet.get('balance', 0) / divisor
    total_received = wallet.get('total_received', 0) / divisor
    total_sent = wallet.get('total_sent', 0) / divisor
    
    with st.container():
        st.markdown(f'<div class="wallet-card">', unsafe_allow_html=True)
        st.markdown(f"**{label} Address:** `{wallet.get('address', 'N/A')}`")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Balance:** {balance:.8f} {config['symbol']}")
            if config['conversion_rate'] > 0:
                st.markdown(f"₹{format_indian_currency(balance * config['conversion_rate'])}")
        with col2:
            st.markdown(f"**Transactions:** {wallet.get('n_tx', 0)}")
        
        st.markdown(f"**Total Received:** {total_received:.8f} {config['symbol']}", unsafe_allow_html=True)
        if config['conversion_rate'] > 0:
            st.markdown(f"₹{format_indian_currency(total_received * config['conversion_rate'])}")
        
        st.markdown(f"**Total Sent:** {total_sent:.8f} {config['symbol']}")
        if config['conversion_rate'] > 0:
            st.markdown(f"₹{format_indian_currency(total_sent * config['conversion_rate'])}")
        
        if wallet.get('unconfirmed'):
            st.warning("⚠️ Unconfirmed Transaction")
        
        st.markdown('</div>', unsafe_allow_html=True)

def main():
    # Header
    st.markdown('<h1 class="main-header">🚨 Cryptocurrency Transaction Analyzer</h1>', unsafe_allow_html=True)
    
    # Sidebar for cryptocurrency selection
    with st.sidebar:
        st.header("⚙️ Settings")
        crypto = st.selectbox(
            "Select Cryptocurrency",
            options=list(CRYPTO_CONFIG.keys()),
            format_func=lambda x: f"{CRYPTO_CONFIG[x]['name']} ({CRYPTO_CONFIG[x]['symbol']})",
            index=0  # Default to BTC
        )
        
        st.markdown("---")
        st.markdown("### 📊 Features")
        st.markdown("""
        - Multi-cryptocurrency support
        - Unconfirmed transaction support
        - Indian currency formatting
        - Suspicious wallet detection
        - Transaction chain tracing
        """)
        
        st.markdown("---")
        st.markdown("### ℹ️ About")
        st.markdown("""
        This tool helps trace cryptocurrency transactions
        and identify suspicious wallet behavior using
        DBSCAN clustering analysis.
        """)
    
    # Main content area
    st.markdown("### Enter Transaction Hash")
    
    # Transaction hash input
    tx_hash = st.text_input(
        "Transaction Hash",
        placeholder="e.g., ed1b8647be6a514e589e9450255f7e85fee534c6b2536f8a04f64ed330087e7b",
        help="Enter the transaction hash you want to analyze"
    )
    
    # Analyze button
    if st.button("🔍 Analyze Transaction", type="primary", use_container_width=True):
        if not tx_hash:
            st.error("Please enter a transaction hash")
        else:
            with st.spinner("Analyzing transaction... This may take a moment."):
                try:
                    # Get crypto config
                    config = get_crypto_config(crypto)
                    config['divisor'] = 10 ** config['decimals']
                    
                    # Check if transaction is unconfirmed
                    tx_info = get_transaction_details(tx_hash, crypto, include_unconfirmed=True)
                    is_unconfirmed = False
                    confirmations = -1
                    
                    if tx_info:
                        is_unconfirmed = tx_info.get('unconfirmed', False) or tx_info.get('confirmations', -1) == 0
                        confirmations = tx_info.get('confirmations', -1)
                    
                    # Trace transaction
                    input_wallets = trace_input_wallet(tx_hash, crypto)
                    receivers = trace_transaction_chain(tx_hash, crypto)
                    
                    # Ensure we have valid lists
                    if input_wallets is None:
                        input_wallets = []
                    if receivers is None:
                        receivers = []
                    
                    # Check if we got any data
                    if not input_wallets and not receivers:
                        error_msg = f'Transaction {tx_hash} not found for {config["name"]}. '
                        if not tx_info:
                            error_msg += 'The transaction may not exist, may be unconfirmed and not yet in the mempool, or the API key may be invalid.'
                        else:
                            error_msg += 'Please verify the transaction hash and cryptocurrency selection.'
                        
                        st.error(error_msg)
                        st.info("""
                        **Possible reasons:**
                        - The transaction hash is incorrect
                        - The transaction doesn't exist on the selected network
                        - The API key is missing or invalid (check crypto.py)
                        - Network connectivity issues
                        - API rate limiting (wait a moment and try again)
                        """)
                    else:
                        # Display transaction status
                        st.markdown("---")
                        st.markdown(f"### Transaction Summary - {config['name']} ({config['symbol']})")
                        
                        if is_unconfirmed:
                            st.warning(f"⚠️ **Unconfirmed Transaction** - This transaction is in the mempool and has not been confirmed yet. Confirmations: {confirmations if confirmations >= 0 else 'Pending'}")
                        elif confirmations >= 0:
                            st.success(f"✅ **Confirmed Transaction** - {confirmations} confirmation{'s' if confirmations != 1 else ''}")
                        
                        # Get wallet details for suspicious wallet analysis
                        wallet_addresses = [wallet['address'] for wallet in receivers if wallet and 'address' in wallet]
                        wallet_details = [get_wallet_details(address, crypto) for address in wallet_addresses]
                        suspicious_wallets = analyze_suspicious_wallets(wallet_details)
                        fund_summary = summarize_funds(input_wallets, receivers, suspicious_wallets, crypto)
                        
                        # Display Input Wallets
                        st.markdown("---")
                        st.markdown("### 📥 Input Wallets")
                        if fund_summary['input_wallets']:
                            for wallet in fund_summary['input_wallets']:
                                display_wallet_info(wallet, config, "Input")
                        else:
                            st.info("No input wallets found.")
                        
                        # Display End Wallets
                        st.markdown("---")
                        st.markdown("### 📤 End Wallets")
                        if fund_summary['end_wallets']:
                            divisor = config['divisor']
                            for wallet in fund_summary['end_wallets']:
                                with st.container():
                                    st.markdown(f'<div class="wallet-card">', unsafe_allow_html=True)
                                    st.markdown(f"**Address:** `{wallet.get('address', 'N/A')}`")
                                    
                                    value = wallet.get('value', 0)
                                    st.markdown(f"**Value:** {value:.8f} {config['symbol']}")
                                    if config['conversion_rate'] > 0:
                                        st.markdown(f"₹{format_indian_currency(value * config['conversion_rate'])}")
                                    
                                    if wallet.get('unconfirmed'):
                                        st.warning("⚠️ Unconfirmed")
                                    st.markdown('</div>', unsafe_allow_html=True)
                        else:
                            st.warning("""
                            **No end wallets found.**
                            
                            This could mean:
                            - All transaction outputs have been spent (chain continues further)
                            - The transaction chain is very long and hit the depth limit
                            - API rate limiting prevented complete tracing
                            - The transaction outputs don't have addresses
                            """)
                        
                        # Display Suspicious Wallets
                        st.markdown("---")
                        st.markdown("### 🚨 Suspicious Wallets")
                        if fund_summary['suspicious_wallets']:
                            for cluster, wallets in fund_summary['suspicious_wallets'].items():
                                st.markdown(f"#### Cluster {cluster}")
                                for wallet in wallets:
                                    display_wallet_info(wallet, config, f"Cluster {cluster}")
                        else:
                            st.info("""
                            **No suspicious wallets detected.**
                            
                            This could mean:
                            - All wallets show similar transaction patterns (no anomalies)
                            - There are fewer than 3 wallets to analyze
                            - The wallets don't exhibit suspicious behavior patterns
                            - Wallet details couldn't be retrieved from the API
                            """)
                        
                        # Display Summary Statistics
                        st.markdown("---")
                        st.markdown("### 📊 Summary Statistics")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Total Spent", f"{fund_summary['total_spent']:.8f} {config['symbol']}")
                        with col2:
                            st.metric("Total Unspent", f"{fund_summary['total_unspent']:.8f} {config['symbol']}")
                        
                        # Transaction visualization (BTC only)
                        if crypto == 'btc':
                            st.markdown("---")
                            st.markdown("### 📈 Transaction Visualization")
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown(f"[View on txgraph.info](https://txgraph.info/tx/{tx_hash})")
                            with col2:
                                st.markdown(f"[View on fbbe.info](https://fbbe.info/t/{tx_hash})")
                
                except Exception as e:
                    st.error(f"Error processing the transaction: {e}")
                    import traceback
                    with st.expander("Error Details"):
                        st.code(traceback.format_exc())

if __name__ == "__main__":
    main()

