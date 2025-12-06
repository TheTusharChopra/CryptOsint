from flask import Flask, render_template, request
from crypto import trace_input_wallet, trace_transaction_chain, get_wallet_details, analyze_suspicious_wallets, summarize_funds, get_crypto_config, CRYPTO_CONFIG, get_transaction_details

app = Flask(__name__)

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

# Register the filter with Jinja2
app.jinja_env.filters['indian_currency'] = format_indian_currency

@app.route('/')
def home():
    return render_template('index.html', supported_cryptos=CRYPTO_CONFIG)

@app.route('/tx/<tx_hash>')
def transaction_details(tx_hash):
    try:
        # Get cryptocurrency from query parameter, default to 'btc'
        crypto = request.args.get('crypto', 'btc').lower()
        
        # Validate cryptocurrency
        if crypto not in CRYPTO_CONFIG:
            crypto = 'btc'
        
        config = get_crypto_config(crypto)
        # Calculate divisor for template (10^decimals)
        config['divisor'] = 10 ** config['decimals']
        
        # Check if transaction is unconfirmed
        tx_info = get_transaction_details(tx_hash, crypto, include_unconfirmed=True)
        is_unconfirmed = False
        confirmations = -1
        if tx_info:
            is_unconfirmed = tx_info.get('unconfirmed', False) or tx_info.get('confirmations', -1) == 0
            confirmations = tx_info.get('confirmations', -1)
        
        input_wallets = trace_input_wallet(tx_hash, crypto)
        receivers = trace_transaction_chain(tx_hash, crypto)
        
        # Ensure we have valid lists (not None)
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
            
            return render_template('result.html', 
                                 fund_summary={
                                     'input_wallets': [],
                                     'end_wallets': [],
                                     'suspicious_wallets': {},
                                     'total_spent': 0,
                                     'total_unspent': 0,
                                     'error': error_msg
                                 }, 
                                 crypto_config=config,
                                 tx_hash=tx_hash,
                                 crypto=crypto,
                                 is_unconfirmed=False,
                                 confirmations=-1)
        
        wallet_addresses = [wallet['address'] for wallet in receivers if wallet and 'address' in wallet]
        wallet_details = [get_wallet_details(address, crypto) for address in wallet_addresses]
        suspicious_wallets = analyze_suspicious_wallets(wallet_details)
        fund_summary = summarize_funds(input_wallets, receivers, suspicious_wallets, crypto)

        return render_template('result.html', 
                             fund_summary=fund_summary, 
                             crypto_config=config,
                             tx_hash=tx_hash,
                             crypto=crypto,
                             is_unconfirmed=is_unconfirmed,
                             confirmations=confirmations)
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return f"Error processing the transaction: {e}<br><br><pre>{error_details}</pre>"

if __name__ == '__main__':
    app.run(debug=True, port=8080)
