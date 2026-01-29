import os
import time
import random
import pandas as pd
from faker import Faker
from datetime import datetime


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "raw")
os.makedirs(OUTPUT_DIR, exist_ok=True)  

CSV_INTERVAL = 5             
EVENTS_PER_FILE = 10         
ACTIONS = ["view", "purchase"]  
PRODUCT_CATEGORIES = ["Electronics", "Books", "Clothing", "Home", "Toys", "Sports"]


fake = Faker()


def generate_event():
    return {
        "user_id": random.randint(1, 1000),
        "product_id": random.randint(1, 500),
        "action": random.choice(ACTIONS),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "price": round(random.uniform(5.0, 500.0), 2),
        "category": random.choice(PRODUCT_CATEGORIES)
    }


def generate_csv_loop():
    file_counter = 1
    print("Starting data generation... Press Ctrl+C to stop.")
    try:
        while True:
            events = [generate_event() for _ in range(EVENTS_PER_FILE)]
            df = pd.DataFrame(events)

           
            csv_file = os.path.join(OUTPUT_DIR, f"events_{file_counter}.csv")

           
            df.to_csv(csv_file, index=False)
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Generated {csv_file} with {EVENTS_PER_FILE} events.")

            file_counter += 1
            time.sleep(CSV_INTERVAL)

    except KeyboardInterrupt:
        print("Data generation stopped manually.")


if __name__ == "__main__":
    generate_csv_loop()
