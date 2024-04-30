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
      
@app.get("/dashboard", response_class=HTMLResponse)
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
        image_base64 = await plot_logarithmic_bins(data, token, metadata, price)
        if image_base64:
            images[token] = image_base64

    return templates.TemplateResponse("dashboard.html", {"request": request, "images": images})
