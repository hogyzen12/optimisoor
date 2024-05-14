import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import asyncio
import numpy as np
import matplotlib.pyplot as plt
import io
import base64

app = FastAPI()
templates = Jinja2Templates(directory="templates")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Why u": "pinging me?"}

@app.get("/dashboard", response_class=HTMLResponse)
async def show_dashboard(request: Request):
    # Hardcoded image URLs
    overall_graphs = {
        "total tokens per owner distribution": "https://shdw-drive.genesysgo.net/7xLawi47mz65xag7NXvEvkMTqLtdG9dWoSh4sLhf56fc/total_tokens_per_owner_distribution.webp",
        "unique owners per token distribution": "https://shdw-drive.genesysgo.net/7xLawi47mz65xag7NXvEvkMTqLtdG9dWoSh4sLhf56fc/unique_owners_per_token_distribution.webp",
        "cumulative total tokens per owner distribution": "https://shdw-drive.genesysgo.net/7xLawi47mz65xag7NXvEvkMTqLtdG9dWoSh4sLhf56fc/cumulative_total_tokens_per_owner_distribution.webp",
        "token diversity per owner": "https://shdw-drive.genesysgo.net/7xLawi47mz65xag7NXvEvkMTqLtdG9dWoSh4sLhf56fc/token_diversity_per_owner.webp"
    }

    lst_graphs = {
        "Juicy SOL": {
            "pet": "https://shdw-drive.genesysgo.net/7xLawi47mz65xag7NXvEvkMTqLtdG9dWoSh4sLhf56fc/Juicy_SOL_pet_log_bins.webp",
            "log": "https://shdw-drive.genesysgo.net/7xLawi47mz65xag7NXvEvkMTqLtdG9dWoSh4sLhf56fc/Juicy_SOL_log_bins.webp"
        },
        "Infinity": {
            "pet": "https://shdw-drive.genesysgo.net/7xLawi47mz65xag7NXvEvkMTqLtdG9dWoSh4sLhf56fc/Infinity_pet_log_bins.webp",
            "log": "https://shdw-drive.genesysgo.net/7xLawi47mz65xag7NXvEvkMTqLtdG9dWoSh4sLhf56fc/Infinity_log_bins.webp"
        },
        "Jupiter Staked SOL": {
            "pet": "https://shdw-drive.genesysgo.net/7xLawi47mz65xag7NXvEvkMTqLtdG9dWoSh4sLhf56fc/Jupiter_Staked_SOL_pet_log_bins.webp",
            "log": "https://shdw-drive.genesysgo.net/7xLawi47mz65xag7NXvEvkMTqLtdG9dWoSh4sLhf56fc/Jupiter_Staked_SOL_log_bins.webp"
        },        
        "Helius Staked SOL": {
            "pet": "https://shdw-drive.genesysgo.net/7xLawi47mz65xag7NXvEvkMTqLtdG9dWoSh4sLhf56fc/Helius_Staked_SOL_pet_log_bins.webp",
            "log": "https://shdw-drive.genesysgo.net/7xLawi47mz65xag7NXvEvkMTqLtdG9dWoSh4sLhf56fc/Helius_Staked_SOL_log_bins.webp"
        },
        "Drift Staked SOL": {
            "pet": "https://shdw-drive.genesysgo.net/7xLawi47mz65xag7NXvEvkMTqLtdG9dWoSh4sLhf56fc/Drift_Staked_SOL_pet_log_bins.webp",
            "log": "https://shdw-drive.genesysgo.net/7xLawi47mz65xag7NXvEvkMTqLtdG9dWoSh4sLhf56fc/Drift_Staked_SOL_log_bins.webp"
        },
        "Power Staked SOL": {
            "pet": "https://shdw-drive.genesysgo.net/7xLawi47mz65xag7NXvEvkMTqLtdG9dWoSh4sLhf56fc/Power_Staked_SOL_pet_log_bins.webp",
            "log": "https://shdw-drive.genesysgo.net/7xLawi47mz65xag7NXvEvkMTqLtdG9dWoSh4sLhf56fc/Power_Staked_SOL_log_bins.webp"
        },        
        "Pumpkin's Staked SOL": {
            "pet": "https://shdw-drive.genesysgo.net/7xLawi47mz65xag7NXvEvkMTqLtdG9dWoSh4sLhf56fc/Pumpkin's_Staked_SOL_pet_log_bins.webp",
            "log": "https://shdw-drive.genesysgo.net/7xLawi47mz65xag7NXvEvkMTqLtdG9dWoSh4sLhf56fc/Pumpkin's_Staked_SOL_log_bins.webp"
        },
        "Lantern Staked SOL": {
            "pet": "https://shdw-drive.genesysgo.net/7xLawi47mz65xag7NXvEvkMTqLtdG9dWoSh4sLhf56fc/Lantern_Staked_SOL_pet_log_bins.webp",
            "log": "https://shdw-drive.genesysgo.net/7xLawi47mz65xag7NXvEvkMTqLtdG9dWoSh4sLhf56fc/Lantern_Staked_SOL_log_bins.webp"
        },
        "bonkSOL": {
            "pet": "https://shdw-drive.genesysgo.net/7xLawi47mz65xag7NXvEvkMTqLtdG9dWoSh4sLhf56fc/bonkSOL_pet_log_bins.webp",
            "log": "https://shdw-drive.genesysgo.net/7xLawi47mz65xag7NXvEvkMTqLtdG9dWoSh4sLhf56fc/bonkSOL_log_bins.webp"
        },
        "Overclock SOL": {
            "pet": "https://shdw-drive.genesysgo.net/7xLawi47mz65xag7NXvEvkMTqLtdG9dWoSh4sLhf56fc/Overclock_SOL_pet_log_bins.webp",
            "log": "https://shdw-drive.genesysgo.net/7xLawi47mz65xag7NXvEvkMTqLtdG9dWoSh4sLhf56fc/Overclock_SOL_log_bins.webp"
        },
        "SolanaHub staked SOL": {
            "pet": "https://shdw-drive.genesysgo.net/7xLawi47mz65xag7NXvEvkMTqLtdG9dWoSh4sLhf56fc/SolanaHub_staked_SOL_pet_log_bins.webp",
            "log": "https://shdw-drive.genesysgo.net/7xLawi47mz65xag7NXvEvkMTqLtdG9dWoSh4sLhf56fc/SolanaHub_staked_SOL_log_bins.webp"
        },
        "Solana Compass LST": {
            "pet": "https://shdw-drive.genesysgo.net/7xLawi47mz65xag7NXvEvkMTqLtdG9dWoSh4sLhf56fc/Solana_Compass_LST_pet_log_bins.webp",
            "log": "https://shdw-drive.genesysgo.net/7xLawi47mz65xag7NXvEvkMTqLtdG9dWoSh4sLhf56fc/Solana_Compass_LST_log_bins.webp"
        },
        "Phase Labs SOL": {
            "pet": "https://shdw-drive.genesysgo.net/7xLawi47mz65xag7NXvEvkMTqLtdG9dWoSh4sLhf56fc/Phase_Labs_SOL_pet_log_bins.webp",
            "log": "https://shdw-drive.genesysgo.net/7xLawi47mz65xag7NXvEvkMTqLtdG9dWoSh4sLhf56fc/Phase_Labs_SOL_log_bins.webp"
        },
        "picoSOL": {
            "pet": "https://shdw-drive.genesysgo.net/7xLawi47mz65xag7NXvEvkMTqLtdG9dWoSh4sLhf56fc/picoSOL_pet_log_bins.webp",
            "log": "https://shdw-drive.genesysgo.net/7xLawi47mz65xag7NXvEvkMTqLtdG9dWoSh4sLhf56fc/picoSOL_log_bins.webp"
        },
    }

    return templates.TemplateResponse("dashboard.html", {"request": request, "overall_graphs": overall_graphs, "lst_graphs": lst_graphs})



async def fetch_token_metadata(mint):
    url = f"https://api.sanctum.so/v1/metadata/{mint}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail="Failed to fetch metadata")

async def fetch_token_prices(mints):
    # Construct the query string by joining mints with the proper parameter format
    mints_query = '&'.join(f'input={mint}' for mint in mints)
    url = f"https://api.sanctum.so/v1/price?{mints_query}"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 200:
            price_data = response.json().get('prices', [])
            # Transform the price data into a dictionary, extracting the 'amount' for each 'mint'
            return {item['mint']: float(item['amount']) for item in price_data if 'mint' in item and 'amount' in item}
        else:
            raise HTTPException(status_code=response.status_code, detail="Failed to fetch prices")

async def fetch_token_data(url: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail="Failed to fetch data")
      
@app.get("/old-dashboard", response_class=HTMLResponse)
async def show_dashboard(request: Request):
    url = "https://shdw-drive.genesysgo.net/3UgjUKQ1CAeaecg5CWk88q9jGHg8LJg9MAybp4pevtFz/token_data.json"
    data = await fetch_token_data(url)
    tokens = list(data.keys())

    metadata_tasks = [fetch_token_metadata(token) for token in tokens]
    metadata_results = await asyncio.gather(*metadata_tasks)

    prices_dict = await fetch_token_prices(tokens)
    print(prices_dict)

    images = {}
    for token, metadata in zip(tokens, metadata_results):
        price = prices_dict.get(token, 0.0) / 1_000_000_000
        #image_base64 = await plot_logarithmic_bins(data, token, metadata, price)
        image_base64 = await plot_pet_logarithmic_bins(data, token, metadata, price)
        if image_base64:
            images[token] = image_base64

    return templates.TemplateResponse("dashboard.html", {"request": request, "images": images})


async def generate_percentile_scatter_plot(data, token_id, metadata):
    if token_id not in data:
        return None

    token_data = data[token_id]
    amounts = np.array([account['amount_normalized'] for account in token_data])
    sorted_amounts = np.sort(amounts)[::-1]  # Sort amounts in descending order

    # Generating x-values (percentiles) for each point
    n = len(sorted_amounts)
    percentiles = np.arange(1, n+1) / n * 100  # Calculate percentiles for each data point

    plt.figure(figsize=(10, 6))
    plt.scatter(percentiles, sorted_amounts, color='blue', alpha=0.7)

    # Setting logarithmic scale for y-axis
    plt.yscale('log')
    plt.ylim(np.min(sorted_amounts[sorted_amounts > 0]), np.max(sorted_amounts))  # Avoid log(0) error by excluding zeros

    # Plot aesthetics
    plt.title(f"{metadata['name']} ({metadata['symbol']}) Distribution - Log Scale")
    plt.xlabel("Percentile")
    plt.ylabel(f"Token Amount ({metadata['symbol']}) [Log Scale]")
    plt.grid(True, which="both", ls="--", linewidth=0.5)

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')

async def plot_pet_logarithmic_bins(data, token_id, metadata, price):
    token_data = data.get(token_id, [])
    if not token_data:
        return None

    amounts = np.array([account['amount_normalized'] for account in token_data if account['amount_normalized'] > 0])
    if amounts.size == 0:
        return None

    bins = [0.1, 0.3, 0.6, 0.9, 1.1, 2, 4, 6, np.inf]
    bin_labels = ['0.1-0.3','0.3-0.6', '0.6-0.9', '0.9-1.1', '1.1-2', '2-4', '4-6', '6+']
    counts, _ = np.histogram(amounts, bins=bins)
    percentages = (counts / counts.sum()) * 100 if counts.sum() > 0 else [0] * len(counts)

    plt.figure(figsize=(10, 6))
    plt.bar(bin_labels, percentages, color='green', alpha=0.7)
    plt.title(f"Distribution of {metadata['name']} ({metadata['symbol']}) - Current Price: {price:.4f} SOL")
    plt.xlabel("Token Holdings Range")
    plt.ylabel("Percentage of Holders")
    plt.grid(True, which="both", ls="--", linewidth=0.5)
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')

async def plot_logarithmic_bins(data, token_id, metadata, price):
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
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')
