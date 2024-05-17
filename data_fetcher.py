import requests
import json
import time
import pandas as pd
import os

def fetch_token_metadata(mint):
    url = f"https://api.sanctum.so/v1/metadata/{mint}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch metadata for {mint}: {e}")
        return None

def fetch_token_accounts_from_solana_fm(mint):
    url = f"https://api.solana.fm/v1/tokens/{mint}/holders"
    headers = {"accept": "application/json"}
    token_accounts = []
    page = 1
    total_items_collected = 0
    total_items_available = float('inf')  # Initial assumption

    while total_items_collected < total_items_available:
        params = {
            'page': page,
            'pageSize': 1000  # Adjust the pageSize if needed
        }
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()

            data = response.json()
            if 'tokenAccounts' in data and data['tokenAccounts']:
                token_accounts.extend(data['tokenAccounts'])
                total_items_collected += len(data['tokenAccounts'])
            else:
                break

            total_items_available = data.get('totalItemCount', 0)
            print(f"Page {page}: Retrieved {len(data['tokenAccounts'])} accounts, Total collected: {total_items_collected}")
            page += 1
            time.sleep(1)
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch token accounts for {mint} on page {page}: {e}")
            break

    if token_accounts:
        with open(f"{mint}_accounts.json", 'w') as f:
            json.dump(token_accounts, f, indent=2)
    else:
        print(f"No token accounts retrieved for {mint}")

    return token_accounts

def load_and_process_json_files(tokens):
    data_dict = {mint: [] for mint in tokens}  # Dictionary to hold data for each token

    for mint in tokens:
        filename = f"{mint}_accounts.json"
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                accounts = json.load(f)
                for account in accounts:
                    info = account['info']
                    amount_normalized = float(info['tokenAmount']['amount']) / (10 ** info['tokenAmount']['decimals'])
                    # Add a conditional check to only append non-zero amounts
                    if amount_normalized > 0.01:
                        data_dict[mint].append({'owner': info['owner'], 'amount_normalized': amount_normalized})

    # Save the dictionary to a JSON file if it contains non-zero entries
    with open("token_data.json", 'w') as json_file:
        json.dump(data_dict, json_file, indent=2)
    print("Data has been written to token_data.json")

def main():
    tokens = [
        'LAinEtNLgpmCP9Rvsf5Hn8W6EhNiKLZQti1xfWMLy6X',
        'J1toso1uCk3RLmjorhTtrVwY9HJ7X8V9yYac6Y7kGCPn',
        'fpSoL8EJ7UA5yJxFKWk1MFiWi35w8CbH36G5B9d7DsV',
        'pathdXw4He1Xk3eX84pDdDZnGKEme3GivBamGCVPZ5a',
        'iceSdwqztAQFuH6En49HWwMxwthKMnGzLFQcMN3Bqhj',
        'jucy5XJ76pHVvtPZb5TKRcGQExkwit2P5s4vY8UzmpC',
        '5oVNBeEEQvYi1cX3ir8Dx5n1P7pdxydbGF2X4TxVusJm',
        'jupSoLaHXQiZZTSfEWMTRRgpnyFm8f6sZdosWBjx93v',
        'he1iusmfkpAdwvxLNGV8Y1iSbj4rUy6yMhEA3fotn9A',        
        'BonK1YhkXEGLZzwtcvRTip3gAL9nCeQD7ppZBLXhtTs',
        'GRJQtWwdJmp5LLpy8JWjPgn5FnLyqSJGNhn5ZnCTFUwM',
        'Comp4ssDzXcLeu2MnLuGNNFC4cmLPMng8qWHPvzAMU1h',
        'HUBsveNpjo5pWqNkH57QzxjQASdTVXcSK7bVKTSZtcSX',        
        'picobAEvs6w7QEknPce34wAE4gknZA9v5tTonnmHYdX',
        'Dso1bDeDjCQxTrWHqUUi63oBvV7Mdm6WaobLbQ7gnPQ',
        'LnTRntk2kTfWEY6cVB8K9649pgJbt6dJLS1Ns1GZCWg',
        'phaseZSfPxTDBpiVb96H4XFSD8xHeHxZre5HerehBJG',
        'pumpkinsEq8xENVZE6QgTS93EN4r9iKvNxNALS1ooyp',
        'pWrSoLAhue6jUxUkbWgmEy5rD9VJzkFmvfTDV5KgNuu',
        'CgnTSoL3DgY9SFHxcLj6CgCgKKoTBr6tp4CPAEWy25DE'        
    ]

    for mint in tokens:
        metadata = fetch_token_metadata(mint)
        if metadata:
            print(f"Processing {metadata['name']} ({metadata['symbol']})")
            fetch_token_accounts_from_solana_fm(mint)
            print(f"Completed {metadata['name']} ({metadata['symbol']})")
        time.sleep(5)  # Sleep to manage API call frequency

    # After collecting all data, process it into a single JSON
    load_and_process_json_files(tokens)

if __name__ == "__main__":
    main()
