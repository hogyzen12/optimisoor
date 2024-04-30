import requests
import json
import time
import pandas as pd
import os

def fetch_token_metadata(mint):
    url = f"https://api.sanctum.so/v1/metadata/{mint}"
    response = requests.get(url)
    return response.json()

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
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            print(f"Failed to fetch data: {response.status_code} - {response.text}")
            break

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

    with open(f"{mint}_accounts.json", 'w') as f:
        json.dump(token_accounts, f, indent=2)

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
        'he1iusmfkpAdwvxLNGV8Y1iSbj4rUy6yMhEA3fotn9A',
        'jucy5XJ76pHVvtPZb5TKRcGQExkwit2P5s4vY8UzmpC',
        '5oVNBeEEQvYi1cX3ir8Dx5n1P7pdxydbGF2X4TxVusJm',
        'BonK1YhkXEGLZzwtcvRTip3gAL9nCeQD7ppZBLXhtTs',
        'GRJQtWwdJmp5LLpy8JWjPgn5FnLyqSJGNhn5ZnCTFUwM',
        'Comp4ssDzXcLeu2MnLuGNNFC4cmLPMng8qWHPvzAMU1h',
        'HUBsveNpjo5pWqNkH57QzxjQASdTVXcSK7bVKTSZtcSX',
        'jupSoLaHXQiZZTSfEWMTRRgpnyFm8f6sZdosWBjx93v',
        'picobAEvs6w7QEknPce34wAE4gknZA9v5tTonnmHYdX'
    ]

    for mint in tokens:
        metadata = fetch_token_metadata(mint)
        print(f"Processing {metadata['name']} ({metadata['symbol']})")
        token_accounts = fetch_token_accounts_from_solana_fm(mint)
        print(f"Completed {metadata['name']} ({metadata['symbol']})")
        time.sleep(5)  # Sleep to manage API call frequency

    # After collecting all data, process it into a single JSON
    load_and_process_json_files(tokens)

if __name__ == "__main__":
    main()
