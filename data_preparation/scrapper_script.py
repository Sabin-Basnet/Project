import pandas as pd
from datetime import datetime
import os

# Create a 'data' folder if it doesn't exist
if not os.path.exists('data'):
    os.makedirs('data')

# 1. Simulate fetching data (We will add the real scraper logic here later)
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
new_data = {
    'Timestamp': [now],
    'Market_Status': ['Open' if 11 <= datetime.now().hour <= 15 else 'Closed'],
    'Dummy_Price': [1250.50]
}

df = pd.DataFrame(new_data)

# 2. Save/Append to CSV
file_path = 'data/nepse_data.csv'

if os.path.exists(file_path):
    # Append without header if file exists
    df.to_csv(file_path, mode='a', header=False, index=False)
else:
    # Create new file with header
    df.to_csv(file_path, index=False)

print(f"Update successful at {now}")