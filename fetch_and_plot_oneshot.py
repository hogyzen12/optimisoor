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

def fetch_token_prices(mints):
    mints_query = '&input='.join(mints)
    url = f"https://api.sanctum.so/v1/price?input={mints_query}"
    response = requests.get(url)
    return response.json()['prices']

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
        time.sleep(2)

    with open(f"{mint}_accounts.json", 'w') as f:
        json.dump(token_accounts, f, indent=2)

    return token_accounts

def generate_plot(data, token_id, metadata, price):
    # Correct the path to 'amount' in the data structure
    amounts = [int(account['info']['tokenAmount']['amount']) for account in data]
    readable_amounts = [amount / 10**metadata.get('decimals', 9) for amount in amounts]  # Adjust decimal places based on token metadata if available

    # Define min_amount and max_amount for the range of histogram
    min_amount = min(readable_amounts) if readable_amounts else 0
    max_amount = 1000  # Adjust as needed based on your data analysis

    # Calculate basic statistics
    mean_amount = np.mean(readable_amounts) if readable_amounts else 0
    median_amount = np.median(readable_amounts) if readable_amounts else 0

    # Percentiles
    percentiles = [99, 95, 90, 75, 50, 25]
    percentile_values = np.percentile(readable_amounts, percentiles) if readable_amounts else [0] * len(percentiles)

    # Create the histogram
    plt.figure(figsize=(10, 5))
    plt.hist(readable_amounts, bins=10, range=(min_amount, max_amount), color='blue', alpha=0.7)
    plt.title(f"{metadata['name']} ({metadata['symbol']}) Token Distribution")
    plt.xlabel(f"Token Amount ({metadata['symbol']})")
    plt.ylabel('Number of Accounts')
    plt.grid(True)

    # Add text box for statistics
    stats_text = (
        f"Mean: {mean_amount:.2f} {metadata['symbol']}\n"
        f"Median: {median_amount:.2f} {metadata['symbol']}\n"
        + '\n'.join(f"Top {p}%: ≥ {value:.2f} {metadata['symbol']}" for p, value in zip(percentiles, percentile_values))
    )
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    plt.annotate(stats_text, xy=(0.98, 0.98), xycoords='axes fraction', fontsize=10,
                 verticalalignment='top', horizontalalignment='right', bbox=props)

    plt.tight_layout()
    plt.savefig(f"{metadata['symbol']}_distribution.png")
    plt.close()


def generate_distri_plot(data, token_id, metadata, price):
    # Correct the path to 'amount' in the data structure and handle decimal places
    sorted_amounts = sorted([int(account['info']['tokenAmount']['amount']) for account in data], reverse=True)
    N = len(sorted_amounts)
    decimals = metadata.get('decimals', 9)  # Default to 9 decimals if not specified in metadata
    readable_amounts = np.array(sorted_amounts) / 10**decimals  # Adjust based on actual token decimals

    # Calculate the percentage of each token amount compared to the total
    percentages = 100 * readable_amounts / np.sum(readable_amounts)

    # Define the percentile bands
    percentiles = [25, 50, 75, 90, 95, 99, 100]
    percentile_values = [np.percentile(readable_amounts, p) for p in percentiles]
    percentile_ranges = [(percentile_values[i], percentile_values[i+1]) for i in range(len(percentiles)-1)]

    # Calculate the average of the values within each percentile band
    averages = []
    for lower, upper in percentile_ranges:
        band_values = readable_amounts[(readable_amounts >= lower) & (readable_amounts <= upper)]
        averages.append(np.mean(band_values) if band_values.size > 0 else 0)

    # Create the plot with a logarithmic y-axis
    plt.figure(figsize=(10, 5))
    bar_positions = np.arange(len(percentiles)-1)
    bar_heights = averages
    plt.bar(bar_positions, bar_heights, color='blue', alpha=0.7, log=True)
    plt.xticks(bar_positions, labels=[f"Top {p}%" for p in percentiles[:-1]], rotation=45)
    plt.title(f"{metadata['name']} ({metadata['symbol']}) Token Distribution")
    plt.xlabel("Percentile")
    plt.ylabel(f"Average Token Amount ({metadata['symbol']})")
    plt.grid(True, which="both", ls="--", linewidth=0.5)

    plt.tight_layout()
    plt.savefig(f"{metadata['symbol']}_percentile_distribution.png")
    plt.close()

    # Print the statistics to the console
    print(f"Total Supply: {np.sum(readable_amounts):.2f} {metadata['symbol']}")
    print(f"Total Accounts: {N}")


def main():
    tokens = [
        'he1iusmfkpAdwvxLNGV8Y1iSbj4rUy6yMhEA3fotn9A',
        'jucy5XJ76pHVvtPZb5TKRcGQExkwit2P5s4vY8UzmpC',
        '5oVNBeEEQvYi1cX3ir8Dx5n1P7pdxydbGF2X4TxVusJm',
        'BonK1YhkXEGLZzwtcvRTip3gAL9nCeQD7ppZBLXhtTs',
        'jupSoLaHXQiZZTSfEWMTRRgpnyFm8f6sZdosWBjx93v',
    ]

    prices = fetch_token_prices(tokens)

    for mint in tokens:
        metadata = fetch_token_metadata(mint)
        print(f"Processing {metadata['name']} ({metadata['symbol']})")
        #token_accounts = fetch_token_accounts(mint)
        token_accounts = fetch_token_accounts_from_solana_fm(mint)
        price = next((float(price['amount'])/1e9 for price in prices if price['mint'] == mint), 0)
        generate_plot(token_accounts, mint, metadata, price)
        generate_distri_plot(token_accounts, mint, metadata, price)
        print(f"Completed {metadata['name']} ({metadata['symbol']})")
        time.sleep(10)  # Sleep to manage API call frequency

if __name__ == "__main__":
    main()
