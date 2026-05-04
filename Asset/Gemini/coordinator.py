import subprocess
import time
import os

# Config
NUM_BATCHES = 1382
WORKER_RANGE = 100
MAX_CONCURRENT_WORKERS = 10 
DELAY_BETWEEN_WORKERS = 10 

# Ranges to EXCLUDE (User already did these manually)
EXCLUDE_RANGES = [(101, 200)]

def launch_worker(start_batch, end_batch):
    cmd = [
        "python", "Asset/Gemini/gemini_worker.py",
        "--start", str(start_batch),
        "--end", str(end_batch),
        "--delay", str(45)
    ]
    return subprocess.Popen(cmd)

def main():
    workers = []
    for i in range(1, NUM_BATCHES + 1, WORKER_RANGE):
        start = i
        end = min(i + WORKER_RANGE - 1, NUM_BATCHES)
        
        # Check if range is excluded
        if any(start >= r[0] and end <= r[1] for r in EXCLUDE_RANGES):
            print(f"Skipping excluded range {start}-{end}...")
            continue
            
        print(f"Launching worker for batches {start}-{end}...")
        p = launch_worker(start, end)
        workers.append(p)
        
        # Simple limit to avoid crashing the machine/API
        if len(workers) >= MAX_CONCURRENT_WORKERS:
            time.sleep(30)
            
        time.sleep(DELAY_BETWEEN_WORKERS)

    print(f"Deployment complete. {len(workers)} workers active.")
    print("Check Asset/Gemini/ for results and progress files.")

if __name__ == "__main__":
    main()
