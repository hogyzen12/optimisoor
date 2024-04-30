import requests
import json
import time
import matplotlib.pyplot as plt
import numpy as np
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
            'pageSize': 1000  # You can adjust the pageSize if needed
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

        # Sleep for 1 second to avoid overwhelming the API
        time.sleep(1)

    with open(f"{mint}_accounts.json", 'w') as f:
        json.dump(token_accounts, f, indent=2)

    return token_accounts

def main():
    tokens = [
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
        'pWrSoLAhue6jUxUkbWgmEy5rD9VJzkFmvfTDV5KgNuu'
    ]

    for mint in tokens:
        metadata = fetch_token_metadata(mint)
        print(f"Processing {metadata['name']} ({metadata['symbol']})")
        token_accounts = fetch_token_accounts_from_solana_fm(mint)
        print(f"Completed {metadata['name']} ({metadata['symbol']})")
        time.sleep(10)  # Sleep to manage API call frequency

if __name__ == "__main__":
    main()

