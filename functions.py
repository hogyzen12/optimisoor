async def plot_cumulative_logarithmic_bins(data, token_id, metadata):
    if token_id not in data:
        return None

    token_data = data[token_id]
    amounts = np.array([account['amount_normalized'] for account in token_data if account['amount_normalized'] > 0])
    bins = [1, 10, 100, 1000, np.inf]  # Define bins
    bin_labels = ['1+', '10+', '100+', '1000+']

    # Use histogram to count the number of values in each bin
    counts, _ = np.histogram(amounts, bins=bins)

    # Calculate cumulative percentages
    total = counts.sum()
    cumulative_counts = np.cumsum(counts)
    cumulative_percentages = (cumulative_counts / total) * 100 if total > 0 else [0]*len(counts)

    plt.figure(figsize=(10, 6))
    plt.bar(bin_labels, cumulative_percentages, color='blue', alpha=0.7)

    # Plot aesthetics
    plt.title(f"Cumulative Distribution of {metadata['name']} ({metadata['symbol']}) Across Logarithmic Bins")
    plt.xlabel("Minimum Value Bins")
    plt.ylabel("Cumulative Percentage of Total Values")
    plt.grid(True, which="both", ls="--", linewidth=0.5)

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')

async def print_dataset_statistics(data, token_id, metadata):
    if token_id not in data:
        return "Token ID not found in the data."

    token_data = data[token_id]
    amounts = np.array([account['amount_normalized'] for account in token_data])
    total_sum = np.sum(amounts)
    average = np.mean(amounts)
    median = np.median(amounts)
    num_entries = len(amounts)

    # Define bins and calculate histogram
    bins = [0.1, 1, 10, 100, 1000, np.inf]
    counts, _ = np.histogram(amounts, bins=bins)
    bin_labels = ['0.1-1', '1-10', '10-100', '100-1000', '1000+']

    # Outputting statistics
    stats_text = f"Statistics for {metadata['name']} ({metadata['symbol']}):\n"
    stats_text += f"Total Sum: {total_sum:.2f} {metadata['symbol']}\n"
    stats_text += f"Average: {average:.2f} {metadata['symbol']}\n"
    stats_text += f"Median: {median:.2f} {metadata['symbol']}\n"
    stats_text += f"Number of Entries: {num_entries}\n"

    # Append bin counts to the statistics text
    for label, count in zip(bin_labels, counts):
        stats_text += f"Entries in {label} bin: {count}\n"

    return stats_text




# async def generate_percentile_plot(data, token_id, metadata):
#     if token_id not in data:
#         return None

#     token_data = data[token_id]
#     amounts = np.array([account['amount_normalized'] for account in token_data])
#     sorted_amounts = np.sort(amounts)[::-1]
  
#     # Percentile calculation
#     percentiles = [25, 50, 75, 90, 95, 99, 100]
#     percentile_values = np.percentile(sorted_amounts, percentiles)
#     percentile_ranges = [(percentile_values[i], percentile_values[i+1]) for i in range(len(percentiles)-1)]

#     # Calculate the average of the values within each percentile band
#     averages = []
#     for lower, upper in percentile_ranges:
#         band_values = sorted_amounts[(sorted_amounts >= lower) & (sorted_amounts <= upper)]
#         averages.append(np.mean(band_values) if band_values.size > 0 else 0)

#     # Basic statistics
#     mean_amount = np.mean(sorted_amounts) if sorted_amounts.size > 0 else 0
#     median_amount = np.median(sorted_amounts) if sorted_amounts.size > 0 else 0

#     # Define statistics text
#     stats_text = (
#         f"Mean: {mean_amount:.2f} {metadata['symbol']}\n"
#         f"Median: {median_amount:.2f} {metadata['symbol']}\n"
#         + '\n'.join(f"Top {100-p}%: ≥ {value:.2f} {metadata['symbol']}" for p, value in zip(percentiles[:-1], percentile_values[:-1]))
#     )
#     props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)

#     plt.figure(figsize=(10, 6))   
#     bar_positions = np.arange(len(percentiles)-1)
#     bar_heights = averages
#     plt.bar(bar_positions, bar_heights, color='blue', alpha=0.7, log=True)
#     plt.xticks(bar_positions, labels=[f"Top {p}%" for p in percentiles[:-1]], rotation=45)
#     plt.title(f"{metadata['name']} ({metadata['symbol']}) Token Distribution")
#     plt.xlabel("Percentile")
#     plt.ylabel(f"Average Token Amount ({metadata['symbol']})")
#     plt.grid(True, which="both", ls="--", linewidth=0.5)
#     plt.annotate(stats_text, xy=(0.48, 0.98), xycoords='axes fraction', fontsize=10,
#                  verticalalignment='top', horizontalalignment='right', bbox=props)

#     buf = io.BytesIO()
#     plt.savefig(buf, format='png')
#     plt.close()
#     buf.seek(0)
#     return base64.b64encode(buf.read()).decode('utf-8')
