import requests
import numpy as np
import matplotlib.pyplot as plt
import os
import json

def fetch_token_data(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def load_token_data(filepath):
    with open(filepath, 'r') as file:
        return json.load(file)

def fetch_token_metadata(mint):
    url = f"https://api.sanctum.so/v1/metadata/{mint}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

def fetch_token_prices(mints):
    mints_query = '&'.join(f'input={mint}' for mint in mints)
    url = f"https://api.sanctum.so/v1/price?{mints_query}"
    response = requests.get(url)
    if response.status_code == 200:
        price_data = response.json().get('prices', [])
        return {item['mint']: float(item['amount']) for item in price_data if 'mint' in item and 'amount' in item}
    else:
        response.raise_for_status()

def save_plot(directory, filename, format='webp'):
    if not os.path.exists(directory):
        os.makedirs(directory)
    # Ensure the filename is URL-friendly
    filename = filename.replace(" ", "_")
    filepath = os.path.join(directory, filename)
    plt.savefig(filepath, format=format)
    plt.close()

def plot_logarithmic_bins(data, token_id, metadata, price, directory="figures"):
    token_data = data.get(token_id, [])
    if not token_data:
        return None

    amounts = np.array([account['amount_normalized'] for account in token_data if account['amount_normalized'] > 0])
    if amounts.size == 0:
        return None

    bins = [0.1, 1, 10, 100, 1000, np.inf]
    bin_labels = ['0.1-1', '1-10', '10-100', '100-1000', '1000+']
    counts, _ = np.histogram(amounts, bins=bins)
    percentages = (counts / counts.sum()) * 100 if counts.sum() > 0 else [0] * len(counts)

    plt.figure(figsize=(10, 6))
    plt.bar(bin_labels, percentages, color='green', alpha=0.7)
    plt.title(f"Distribution of {metadata['name']} ({metadata['symbol']}) - Current Price: {price:.4f} SOL")
    plt.xlabel("Token Holdings Range")
    plt.ylabel("Percentage of Holders")
    plt.grid(True, which="both", ls="--", linewidth=0.5)

    filename = f"{metadata['name']}_log_bins.webp".replace(" ", "_")
    save_plot(directory, filename)

def plot_pet_logarithmic_bins(data, token_id, metadata, price, directory="figures"):
    token_data = data.get(token_id, [])
    if not token_data:
        return None

    amounts = np.array([account['amount_normalized'] for account in token_data if account['amount_normalized'] > 0])
    if amounts.size == 0:
        return None

    bins = [0.1, 0.3, 0.5, 0.7, 0.9, 1.0, 1.1, 2, 4, 6, 8, 10, np.inf]
    bin_labels = ['0.1-0.3','0.3-0.5', '0.5-0.7', '0.7-0.9', '0.9-1.0','1.0-1.1', '1.1-2', '2-4', '4-6', '6-8', '8-10', '10+']
    counts, _ = np.histogram(amounts, bins=bins)
    percentages = (counts / counts.sum()) * 100 if counts.sum() > 0 else [0] * len(counts)

    # Compute statistics
    statistics = compute_statistics(amounts)

    plt.figure(figsize=(10, 6))
    plt.bar(bin_labels, percentages, color='green', alpha=0.7)
    plt.title(f"Distribution of {metadata['name']} ({metadata['symbol']}) - Current Price: {price:.4f} SOL")
    plt.xlabel("Token Holdings Range")
    plt.ylabel("Percentage of Holders")
    plt.grid(True, which="both", ls="--", linewidth=0.5)

    # Annotating with statistics
    stats_text = "\n".join([f"{key}: {val:.2f}" for key, val in statistics.items()])
    plt.annotate(stats_text, xy=(0.75, 0.95), xycoords='axes fraction', verticalalignment='top', bbox=dict(boxstyle="round,pad=0.5", fc="yellow", alpha=0.5))

    
    filename = f"{metadata['name']}_pet_log_bins.webp".replace(" ", "_")
    save_plot(directory, filename)

def compute_statistics(amounts):
    statistics = {
        'mean': np.mean(amounts),
        'median': np.median(amounts),
        'sum': np.sum(amounts),
        'count': len(amounts),
        'std_dev': np.std(amounts),
        'min': np.min(amounts),
        'max': np.max(amounts)
    }
    return statistics

def aggregate_owner_data(data):
    owner_details = {}

    for token_id, accounts in data.items():
        for account in accounts:
            owner = account['owner']
            amount = account['amount_normalized']

            if owner not in owner_details:
                owner_details[owner] = {}
            
            # Adding each token with its amount to the owner's record
            owner_details[owner][token_id] = amount

    return owner_details


def plot_total_tokens_per_owner(owner_details, directory="figures"):
    # Calculate the total number of tokens owned by each owner
    total_tokens = {owner: sum(tokens.values()) for owner, tokens in owner_details.items()}
    values = list(total_tokens.values())

    # Define bins and labels for the histogram
    bins = [0.1, 0.3, 0.5, 0.7, 0.9, 1.0, 1.1, 2, 4, 6, 8, 10, np.inf]
    bin_labels = ['0.1-0.3', '0.3-0.5', '0.5-0.7', '0.7-0.9', '0.9-1.0', '1.0-1.1', '1.1-2', '2-4', '4-6', '6-8', '8-10', '10+']

    # Histogram and calculate percentages
    counts, _ = np.histogram(values, bins=bins)
    percentages = (counts / counts.sum()) * 100 if counts.sum() > 0 else [0] * len(counts)

    # Plotting
    plt.figure(figsize=(10, 6))
    plt.bar(bin_labels, percentages, color='green', alpha=0.7)
    plt.title("Distribution of Total Tokens Owned per Owner")
    plt.xlabel("Total Tokens Owned")
    plt.ylabel("Percentage of Owners (%)")
    plt.grid(True, which="both", ls="--", linewidth=0.5)

    # Saving the plot
    filename = "total_tokens_per_owner_distribution.webp".replace(" ", "_")
    save_plot(directory, filename)

def plot_token_diversity_per_owner(owner_details, directory="figures"):
    diversity = {owner: len(tokens) for owner, tokens in owner_details.items()}
    counts = list(diversity.values())

    plt.figure(figsize=(10, 6))
    plt.hist(counts, bins=range(1, max(counts) + 2), alpha=0.7, edgecolor='black', log=True)
    plt.title("Distribution of Token Diversity per Owner")
    plt.xlabel("Number of Different Tokens Owned")
    plt.ylabel("Number of Owners")
    plt.grid(True, which="both", ls="--", linewidth=0.5)

    filename = "token_diversity_per_owner.webp".replace(" ", "_")
    save_plot(directory, filename)

def plot_total_tokens_per_owner_cumulative(owner_details, directory="figures"):
    # Calculate the total number of tokens owned by each owner
    total_tokens = {owner: sum(tokens.values()) for owner, tokens in owner_details.items()}
    values = list(total_tokens.values())

    # Define bins and labels for the histogram
    bins = [0.1, 0.3, 0.5, 0.7, 0.9, 1.0, 1.1, 2, 4, 6, 8, 10, np.inf]
    bin_labels = ['0.1-0.3', '0.3-0.5', '0.5-0.7', '0.7-0.9', '0.9-1.0', '1.0-1.1', '1.1-2', '2-4', '4-6', '6-8', '8-10', '10+']

    # Histogram and calculate percentages for cumulative distribution
    counts, bin_edges = np.histogram(values, bins=bins)
    cumulative_counts = np.cumsum(counts)
    percentages = (cumulative_counts / counts.sum()) * 100 if counts.sum() > 0 else [0] * len(cumulative_counts)

    # Plotting
    plt.figure(figsize=(10, 6))
    previous_cumulative = [0] + list(percentages[:-1])  # Start with 0 for the first bar's base

    # Plot the base of each bar (previous cumulative percentages)
    base_bars = plt.bar(bin_labels, previous_cumulative, color='blue', alpha=0.7)

    # Calculate delta percentages for each bin
    delta_percentages = [percentages[i] - previous_cumulative[i] for i in range(len(percentages))]
    
    # Plot the delta percentages on top of the previous bars
    delta_bars = plt.bar(bin_labels, delta_percentages, bottom=previous_cumulative, color='green', alpha=0.7)

    # Annotating each bar with the delta
    for bar, delta, total in zip(delta_bars, counts, cumulative_counts):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + bar.get_y(),
                 f'+{int(delta)} ({(delta / counts.sum() * 100):.2f}%)',
                 ha='center', va='bottom', color='black', fontsize=8)

    plt.title("Cumulative Distribution of Total Tokens Owned per Owner")
    plt.xlabel("Total Tokens Owned")
    plt.ylabel("Cumulative Percentage of Owners (%)")
    plt.grid(True, which="both", ls="--", linewidth=0.5)

    # Save the plot
    filename = "cumulative_total_tokens_per_owner_distribution.webp".replace(" ", "_")
    save_plot(directory, filename)

def plot_unique_owners_per_token(data, metadata_results, directory="figures"):
    # Aggregate data to count unique owners per token
    token_owners = {}
    token_names = {}
    for token_id, accounts in data.items():
        unique_owners = set(account['owner'] for account in accounts)
        token_owners[token_id] = len(unique_owners)
        # Assuming metadata_results is a dictionary where keys are token IDs and values contain token names
        token_names[token_id] = metadata_results[token_id]['name'] if token_id in metadata_results and 'name' in metadata_results[token_id] else token_id

    # Prepare data for plotting
    tokens = [token_names[tid] for tid in token_owners]  # Using token names instead of IDs
    owner_counts = list(token_owners.values())

    # Plotting
    plt.figure(figsize=(12, 6))
    bars = plt.bar(tokens, owner_counts, color='blue', alpha=0.7)
    plt.yscale('log')  # Set logarithmic scale on y-axis
    plt.xlabel('Token Name')
    plt.ylabel('Number of Unique Owners (Log Scale)')
    plt.title('Number of Unique Owners per Token')
    plt.xticks(rotation=90)  # Rotate token labels to avoid overlap
    plt.grid(True, which="both", ls="--", linewidth=0.5)

    # Adding text on top of each bar
    for bar, count in zip(bars, owner_counts):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f'{count}',
                 ha='center', va='bottom', color='black', fontsize=8)

    # Save the plot
    filename = "unique_owners_per_token_distribution.webp".replace(" ", "_")
    save_plot(directory, filename)

def main():
    #url = "https://shdw-drive.genesysgo.net/3UgjUKQ1CAeaecg5CWk88q9jGHg8LJg9MAybp4pevtFz/token_data.json"
    #data = fetch_token_data(url)
    filepath = "token_data.json"
    data = load_token_data(filepath)
    tokens = list(data.keys())
    metadata_results = {token: fetch_token_metadata(token) for token in tokens}
    prices_dict = fetch_token_prices(tokens)
    # Aggregating detailed owner data from tokens
    owner_details = aggregate_owner_data(data)
    
    plot_unique_owners_per_token(data,metadata_results)
    # Plotting distributions based on new owner details
    plot_total_tokens_per_owner(owner_details)
    plot_total_tokens_per_owner_cumulative(owner_details)
    plot_token_diversity_per_owner(owner_details)    

    for token, metadata in metadata_results.items():
        price = prices_dict.get(token, 0.0) / 1_000_000_000
        plot_logarithmic_bins(data, token, metadata, price)
        plot_pet_logarithmic_bins(data, token, metadata, price)

if __name__ == '__main__':
    main()
