import os
import time
from datetime import datetime
import subprocess
import shutil

def create_dated_directory():
    date = datetime.now().strftime("%Y%m%d")
    directory = f"data/{date}"
    os.makedirs(directory, exist_ok=True)
    print(f"Created directory: {directory}")
    return directory

def get_last_fetch_time(directory):
    json_files = [file for file in os.listdir(directory) if file.endswith(".json")]
    if json_files:
        last_fetch_time = max(os.path.getmtime(f"{directory}/{file}") for file in json_files)
        return datetime.fromtimestamp(last_fetch_time)
    return None

def should_fetch_data(directory):
    last_fetch_time = get_last_fetch_time(directory)
    if last_fetch_time:
        time_since_last_fetch = datetime.now() - last_fetch_time
        if time_since_last_fetch.total_seconds() > 6 * 3600:
            print("More than 6 hours have passed since the last fetch. Fetching new data.")
            return True
        else:
            print(f"Last fetch was less than 6 hours ago. Skipping data fetch.")
            return False
    print("No previous fetch exists for the current day. Fetching new data.")
    return True

def run_data_fetcher():
    print("Running data fetcher script...")
    subprocess.run(["python3", "data_fetcher.py"])
    print("Data fetcher script completed.")

def run_data_plotter():
    print("Running data plotter script...")
    subprocess.run(["python3", "data_plotter.py"])
    print("Data plotter script completed.")

def push_to_server(directory):
    base_url = "https://shdw-drive.genesysgo.net/7xLawi47mz65xag7NXvEvkMTqLtdG9dWoSh4sLhf56fc/"
    api_url = "https://damp-fabled-panorama.solana-mainnet.quiknode.pro/186133957d30cece76e7cd8b04bce0c5795c164e/"
    keypair_path = "/Users/hogyzen12/.config/solana/dshYBbhPkXeYjuHPq1XZGivpXdS4ibXp2jfaACs5ZrH.json"
    
    for filename in os.listdir(directory):
        if filename.endswith(".webp"):
            file_path = os.path.join(directory, filename)
            file_url = f"{base_url}{filename}"
            print(file_path)
            print(file_url)
            command = [
                "shdw-drive", "edit-file",
                "-r", api_url,
                "-kp", keypair_path,
                "-f", file_path,
                "-u", file_url
            ]
            subprocess.run(command)
    time.sleep(1)

def move_data_to_directory(directory):
    print(f"Moving JSON files to directory: {directory}")
    json_files = [file for file in os.listdir() if file.endswith(".json")]
    for file in json_files:
        new_file_name = file.replace(" ", "_")
        shutil.move(file, os.path.join(directory, new_file_name))
    print("JSON files moved to the directory with spaces replaced by underscores.")

def main():
    while True:
        print("\n--- Starting data fetch cycle ---")
        
        # Create a dated directory for each data fetch
        directory = create_dated_directory()

        # Check if data should be fetched based on the last fetch time
        if should_fetch_data(directory):
            # Run the data fetcher script
            run_data_fetcher()
            print("Data fetch cycle completed.")

            # Run the data plotter script
            run_data_plotter()

            # Move the data to the dated directory
            move_data_to_directory(directory)
            print("Data plotting completed.")

        # Push the data and images to the server
        push_to_server("figures")
        print("Pushing images.")
        
        
        
        # Sleep for a day (86400 seconds) before the next fetch
        print("Waiting for the next data fetch cycle...")
        time.sleep(86400)

if __name__ == "__main__":
    main()