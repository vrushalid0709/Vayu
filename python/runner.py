import time
import json
from fetch_data import fetch_aqi_data

print("Runner started")

last_timestamp = None

while True:
    print("Fetching data...")

    data = fetch_aqi_data()
    print("Data received:", data)

    if data and data.get("timestamp"):
        if data["timestamp"] != last_timestamp:
            print("New data:", data)

            with open("data/aqi_data.jsonl", "a") as f:
                f.write(json.dumps(data) + "\n")

            last_timestamp = data["timestamp"]
        else:
            print("No new update")

    else:
        print("Fetch failed or invalid data")

    print("Sleeping for 5 minutes...\n")
    time.sleep(300)