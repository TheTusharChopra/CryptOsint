import requests
from sklearn.cluster import DBSCAN
import numpy as np
import csv
from requests.exceptions import RequestException

# BlockCypher API token
# Set to None or empty string to use public API (rate limited)
# Get your free API token at: https://www.blockcypher.com/dev/
API_TOKEN = '<YOUR-API-KEY>'

# Supported cryptocurrencies configuration
CRYPTO_CONFIG = {
    'btc': {
        'name': 'Bitcoin',
        'symbol': 'BTC',
        'base_url': 'https://api.blockcypher.com/v1/btc/main/',
        'decimals': 8,  # satoshis
        'conversion_rate': 5053094.57  # BTC to INR (can be updated)
    },
    'eth': {
        'name': 'Ethereum',
        'symbol': 'ETH',
        'base_url': 'https://api.blockcypher.com/v1/eth/main/',
        'decimals': 18,  # wei
        'conversion_rate': 0  # Set to 0 to disable conversion, or add ETH to INR rate
    },
    'ltc': {
        'name': 'Litecoin',
        'symbol': 'LTC',
        'base_url': 'https://api.blockcypher.com/v1/ltc/main/',
        'decimals': 8,
        'conversion_rate': 0
    },
    'bch': {
        'name': 'Bitcoin Cash',
        'symbol': 'BCH',
        'base_url': 'https://api.blockcypher.com/v1/bch/main/',
        'decimals': 8,
        'conversion_rate': 0
    },
    'doge': {
        'name': 'Dogecoin',
        'symbol': 'DOGE',
        'base_url': 'https://api.blockcypher.com/v1/doge/main/',
        'decimals': 8,
        'conversion_rate': 0
    },
    'dash': {
        'name': 'Dash',
        'symbol': 'DASH',
        'base_url': 'https://api.blockcypher.com/v1/dash/main/',
        'decimals': 8,
        'conversion_rate': 0
    }
}

def get_crypto_config(crypto='btc'):
    """Get configuration for a specific cryptocurrency."""
    crypto_lower = crypto.lower()
    if crypto_lower not in CRYPTO_CONFIG:
        # Default to BTC if unsupported crypto is provided
        crypto_lower = 'btc'
    return CRYPTO_CONFIG[crypto_lower]

def get_base_url(crypto='btc'):
    """Get the base URL for a specific cryptocurrency."""
    return get_crypto_config(crypto)['base_url']

def get_transaction_details(tx_hash, crypto='btc', include_unconfirmed=True, retries=3):
    """
    Retrieve details of a transaction using its hash.
    Supports both confirmed and unconfirmed (mempool) transactions.
    
    BlockCypher API automatically includes unconfirmed transactions from the mempool
    when querying by transaction hash, so we don't need a separate mempool endpoint.
    
    Args:
        tx_hash: Transaction hash
        crypto: Cryptocurrency code (btc, eth, ltc, etc.)
        include_unconfirmed: Whether to include unconfirmed transactions (always True for mempool support)
        retries: Number of retry attempts for rate-limited requests
    """
    base_url = get_base_url(crypto)
    # BlockCypher API includes mempool transactions automatically when querying by hash
    # Only add token if it's set and not the placeholder
    if API_TOKEN and API_TOKEN != '<YOUR-API-KEY>':
        url = f'{base_url}txs/{tx_hash}?token={API_TOKEN}'
    else:
        url = f'{base_url}txs/{tx_hash}'
    
    import time
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                tx_data = response.json()
                # Check if transaction is unconfirmed
                confirmations = tx_data.get('confirmations', -1)
                if confirmations == 0 or confirmations is None:
                    tx_data['unconfirmed'] = True
                # Also check block_height - if None or 0, it's unconfirmed
                if tx_data.get('block_height') is None:
                    tx_data['unconfirmed'] = True
                return tx_data
            elif response.status_code == 404:
                # Transaction not found - could be:
                # 1. Invalid hash
                # 2. Not yet in mempool (very new transaction)
                # 3. Dropped from mempool
                if attempt == retries - 1:  # Only print on last attempt
                    print(f"Transaction with hash {tx_hash} not found. It may be unconfirmed and not yet in the mempool, or the hash may be invalid.")
                return None
            elif response.status_code == 429:
                # Rate limit - wait and retry
                wait_time = (attempt + 1) * 2  # Exponential backoff: 2s, 4s, 6s
                if attempt < retries - 1:
                    print(f"Rate limit exceeded. Waiting {wait_time} seconds before retry {attempt + 2}/{retries}...")
                    time.sleep(wait_time)
                    continue
                else:
                    print("Rate limit exceeded. Please wait a moment and try again.")
                    return None
            else:
                if attempt == retries - 1:  # Only print on last attempt
                    print(f"Error retrieving transaction details: {response.status_code}")
                return None
        except requests.Timeout:
            if attempt < retries - 1:
                wait_time = (attempt + 1) * 1
                print(f"Request timeout. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                continue
            else:
                print(f"Request timeout while fetching transaction {tx_hash}. The transaction may be processing.")
                return None
        except RequestException as e:
            if attempt == retries - 1:  # Only print on last attempt
                print(f"Error contacting BlockCypher API: {e}")
            return None
    
    return None

def trace_transaction_chain(tx_hash, crypto='btc', visited=None, max_depth=100):
    """
    Recursively trace the transaction chain until reaching unspent outputs.
    Supports both confirmed and unconfirmed transactions.
    
    Args:
        tx_hash: Transaction hash
        crypto: Cryptocurrency code (btc, eth, ltc, etc.)
        visited: Set of visited transaction hashes to avoid cycles
        max_depth: Maximum recursion depth to prevent infinite loops
    """
    if visited is None:
        visited = set()
    
    if tx_hash in visited or max_depth <= 0:
        return []

    visited.add(tx_hash)

    transaction = get_transaction_details(tx_hash, crypto, include_unconfirmed=True)
    if not transaction:
        return []

    config = get_crypto_config(crypto)
    decimals = config['decimals']
    divisor = 10 ** decimals

    receivers = []
    is_unconfirmed = transaction.get('unconfirmed', False) or transaction.get('confirmations', -1) == 0

    outputs = transaction.get('outputs', [])
    for output in outputs:
        # Check if output has been spent
        spent_by = output.get('spent_by')
        has_address = output.get('addresses') and len(output.get('addresses', [])) > 0
        
        if spent_by:
            # Output has been spent - trace the next transaction
            next_tx_hash = spent_by
            # Trace further (limit depth for unconfirmed to avoid deep chains)
            if is_unconfirmed and max_depth < 3:
                # For unconfirmed, don't trace too deep
                pass
            else:
                receivers.extend(trace_transaction_chain(next_tx_hash, crypto, visited, max_depth - 1))
        elif has_address:
            # Output not spent yet - this is an end wallet
            address = output.get('addresses', [None])[0]
            if address:
                receivers.append({
                    'address': address,
                    'value': output['value'] / divisor,  # Convert to main unit
                    'unconfirmed': is_unconfirmed
                })

    return receivers

def get_wallet_details(address, crypto='btc'):
    """
    Retrieve details of a wallet using its address.
    
    Args:
        address: Wallet address
        crypto: Cryptocurrency code (btc, eth, ltc, etc.)
    """
    try:
        base_url = get_base_url(crypto)
        # Only add token if it's set and not the placeholder
        if API_TOKEN and API_TOKEN != '<YOUR-API-KEY>':
            url = f'{base_url}addrs/{address}?token={API_TOKEN}'
        else:
            url = f'{base_url}addrs/{address}'
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error retrieving wallet details: {response.status_code}")
            return {}
    except RequestException as e:
        print(f"Error contacting BlockCypher API: {e}")
        return {}

def analyze_suspicious_wallets(wallet_details):
    """
    Analyze the list of wallet details to find the most significant and potentially suspicious wallets using clustering analysis.
    """
    data = []
    valid_details = []
    for details in wallet_details:
        if details:
            # Normalize data for better clustering (log scale for large values)
            balance = details.get('balance', 0)
            n_tx = details.get('n_tx', 0)
            total_received = details.get('total_received', 0)
            
            # Use log scale for large values to prevent outliers from dominating
            balance_log = np.log1p(balance) if balance > 0 else 0
            total_received_log = np.log1p(total_received) if total_received > 0 else 0
            
            data.append([balance_log, n_tx, total_received_log])
            valid_details.append(details)
    
    if not data:
        print("No wallet data available for clustering.")
        return {}
    
    if len(data) < 2:
        # Not enough data for clustering, return all as a single group
        return {-1: valid_details}

    data = np.array(data)
    
    # Adjust clustering parameters based on data size
    min_samples = min(3, max(2, len(data) // 3))  # Adaptive min_samples
    eps = 1.0  # Increased eps for better clustering
    
    try:
        clustering = DBSCAN(eps=eps, min_samples=min_samples).fit(data)
        labels = clustering.labels_
    except Exception as e:
        print(f"Clustering error: {e}")
        # Fallback: return all wallets as a single group
        return {-1: valid_details}

    unique_labels = np.unique(labels)
    
    # Filter out noise (-1 label) and create clusters
    suspicious_wallets = {}
    for label, details in zip(labels, valid_details):
        if label not in suspicious_wallets:
            suspicious_wallets[label] = []
        suspicious_wallets[label].append(details)
    
    # Handle different clustering scenarios
    if len(unique_labels) == 1 and unique_labels[0] == -1:
        # All are noise (all different) - return all as a single suspicious group
        # This means wallets are all different from each other, which could be suspicious
        return {-1: valid_details}
    elif len(unique_labels) == 1:
        # Only one cluster (all similar) - wallets are normal, return empty
        # If all wallets are similar, they're likely not suspicious
        return {}
    elif len(unique_labels) == 2 and -1 in unique_labels:
        # One cluster + noise - return only the noise (outliers) as suspicious
        # The main cluster represents normal wallets, outliers are suspicious
        if -1 in suspicious_wallets:
            return {-1: suspicious_wallets[-1]}
        else:
            # Shouldn't happen, but handle it
            return suspicious_wallets
    
    # Multiple clusters found (3+) - return all clusters as potentially suspicious
    # Different clusters may represent different suspicious patterns
    # But filter out the largest cluster (likely normal wallets)
    if len(suspicious_wallets) > 1:
        # Find the largest cluster (probably normal wallets)
        largest_cluster = max(suspicious_wallets.items(), key=lambda x: len(x[1]))
        largest_label = largest_cluster[0]
        
        # If largest cluster is significantly bigger, it's probably normal wallets
        # Return only smaller clusters as suspicious
        if len(largest_cluster[1]) > len(valid_details) * 0.6:  # More than 60% of wallets
            # Remove the largest cluster, keep others as suspicious
            result = {k: v for k, v in suspicious_wallets.items() if k != largest_label}
            if result:
                return result
            # If removing largest leaves nothing, return all except largest
            return {k: v for k, v in suspicious_wallets.items() if k != largest_label or len(v) == 1}
    
    return suspicious_wallets

def print_summary(fund_summary, crypto='btc', conversion_rate=None):
    """
    Print the summary of funds including input wallets, end wallets, and suspicious wallets.
    
    Args:
        fund_summary: Dictionary containing fund summary data
        crypto: Cryptocurrency code (btc, eth, ltc, etc.)
        conversion_rate: Optional conversion rate to fiat currency (e.g., INR)
    """
    config = get_crypto_config(crypto)
    symbol = config['symbol']
    decimals = config['decimals']
    divisor = 10 ** decimals
    
    if conversion_rate is None:
        conversion_rate = config.get('conversion_rate', 0)
    
    print("Input Wallets:")
    for wallet in fund_summary['input_wallets']:
        balance = wallet.get('balance', 0) / divisor
        total_received = wallet.get('total_received', 0) / divisor
        total_sent = wallet.get('total_sent', 0) / divisor
        print(f"  Address: {wallet['address']}")
        print(f"    Balance: {balance} {symbol}", end="")
        if conversion_rate > 0:
            print(f" ({balance * conversion_rate:.2f} INR)", end="")
        print()
        print(f"    Total Received: {total_received} {symbol}", end="")
        if conversion_rate > 0:
            print(f" ({total_received * conversion_rate:.2f} INR)", end="")
        print()
        print(f"    Total Sent: {total_sent} {symbol}", end="")
        if conversion_rate > 0:
            print(f" ({total_sent * conversion_rate:.2f} INR)", end="")
        print()
        print(f"    Total Transactions: {wallet.get('n_tx', 0)}")

    print("\nEnd Wallets:")
    for wallet in fund_summary['end_wallets']:
        value = wallet.get('value', 0)
        print(f"  Address: {wallet['address']}")
        print(f"    Value: {value} {symbol}", end="")
        if conversion_rate > 0:
            print(f" ({value * conversion_rate:.2f} INR)", end="")
        print()

    print("\nSuspicious Wallets:")
    for cluster, wallets in fund_summary['suspicious_wallets'].items():
        print(f"\nCluster {cluster}:")
        for wallet in wallets:
            balance = wallet.get('balance', 0) / divisor
            total_received = wallet.get('total_received', 0) / divisor
            total_sent = wallet.get('total_sent', 0) / divisor
            print(f"  Address: {wallet['address']}")
            print(f"    Balance: {balance} {symbol}", end="")
            if conversion_rate > 0:
                print(f" ({balance * conversion_rate:.2f} INR)", end="")
            print()
            print(f"    Total Received: {total_received} {symbol}", end="")
            if conversion_rate > 0:
                print(f" ({total_received * conversion_rate:.2f} INR)", end="")
            print()
            print(f"    Total Sent: {total_sent} {symbol}", end="")
            if conversion_rate > 0:
                print(f" ({total_sent * conversion_rate:.2f} INR)", end="")
            print()
            print(f"    Total Transactions: {wallet.get('n_tx', 0)}")

def trace_input_wallet(tx_hash, crypto='btc'):
    """
    Trace the input wallet(s) of a transaction.
    Supports both confirmed and unconfirmed transactions.
    
    Args:
        tx_hash: Transaction hash
        crypto: Cryptocurrency code (btc, eth, ltc, etc.)
    """
    transaction = get_transaction_details(tx_hash, crypto, include_unconfirmed=True)
    if not transaction:
        return []  # Return empty list instead of None

    is_unconfirmed = transaction.get('unconfirmed', False) or transaction.get('confirmations', -1) == 0
    
    inputs = transaction.get('inputs', [])
    input_wallets = []
    for input_tx in inputs:
        if 'addresses' in input_tx and input_tx['addresses']:
            address = input_tx['addresses'][0]
            wallet_details = get_wallet_details(address, crypto)
            if wallet_details:
                input_wallets.append({
                    'address': address,
                    'balance': wallet_details.get('balance', 0),
                    'total_received': wallet_details.get('total_received', 0),
                    'total_sent': wallet_details.get('total_sent', 0),
                    'n_tx': wallet_details.get('n_tx', 0),
                    'unconfirmed': is_unconfirmed
                })
            else:
                # For unconfirmed transactions, we might not have wallet details yet
                # Still include the address
                input_wallets.append({
                    'address': address,
                    'balance': 0,
                    'total_received': 0,
                    'total_sent': 0,
                    'n_tx': 0,
                    'unconfirmed': True
                })
    
    return input_wallets

def summarize_funds(input_wallets, receivers, suspicious_wallets, crypto='btc'):
    """
    Summarize the flow of funds, including spent and unspent amounts.
    
    Args:
        input_wallets: List of input wallet details
        receivers: List of receiver wallet details
        suspicious_wallets: Dictionary of suspicious wallet clusters
        crypto: Cryptocurrency code (btc, eth, ltc, etc.)
    """
    # Ensure we have valid lists (not None)
    if input_wallets is None:
        input_wallets = []
    if receivers is None:
        receivers = []
    if suspicious_wallets is None:
        suspicious_wallets = {}
    
    config = get_crypto_config(crypto)
    decimals = config['decimals']
    divisor = 10 ** decimals
    
    total_spent = sum(receiver.get('value', 0) for receiver in receivers if receiver and 'value' in receiver)
    
    total_unspent = 0
    for cluster_wallets in suspicious_wallets.values():
        if cluster_wallets:
            for wallet in cluster_wallets:
                if wallet:
                    total_unspent += wallet.get('balance', 0) / divisor
    
    return {
        'input_wallets': input_wallets,
        'end_wallets': receivers,
        'suspicious_wallets': suspicious_wallets,
        'total_spent': total_spent,
        'total_unspent': total_unspent
    }

def load_csv_data(file_path):
    """
    Load wallet addresses and associated data from a CSV file.
    """
    csv_data = {}
    try:
        with open(file_path, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                address = row.get('address')
                if address:
                    csv_data[address] = row
    except Exception as e:
        print(f"Error loading CSV file: {e}")
    return csv_data

def match_wallets(wallet_details, csv_data):
    """
    Cross-reference wallet addresses with known entities from CSV data.
    """
    matched_wallets = []
    for wallet in wallet_details:
        address = wallet.get('address')
        if address in csv_data:
            matched_wallets.append({**wallet, **csv_data[address]})
    return matched_wallets

# Execution example (commented out for Flask app usage)
# TX_HASH = "ed1b8647be6a514e589e9450255f7e85fee534c6b2536f8a04f64ed330087e7b"
# CRYPTO = "btc"
# 
# try:
#     input_wallets = trace_input_wallet(TX_HASH, CRYPTO)
#     receivers = trace_transaction_chain(TX_HASH, CRYPTO)
#     wallet_addresses = [wallet['address'] for wallet in receivers]
#     wallet_details = [get_wallet_details(address, CRYPTO) for address in wallet_addresses]
#     suspicious_wallets = analyze_suspicious_wallets(wallet_details)
#     fund_summary = summarize_funds(input_wallets, receivers, suspicious_wallets, CRYPTO)
#     print_summary(fund_summary, CRYPTO)
# except Exception as e:
#     print(f"Error tracing funds: {e}")
