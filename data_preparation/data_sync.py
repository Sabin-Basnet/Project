import pandas as pd
import time
import os
from io import StringIO
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# --- CONFIG ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
METADATA_FILE = os.path.join(BASE_DIR, "metadata.csv")
DATA_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "stock_data"))
START_DATE = "2020-01-01" 

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# --- SELENIUM ---
options = Options()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 20)

# Load page ONCE at the start
driver.get("https://nepsealpha.com/nepse-data")

def sync_stock(symbol):
    try:
        print(f"🔄 Syncing: {symbol}")

        # 1. Clear and Select Symbol
        dropdown = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".select2-selection--single")))
        dropdown.click()
        
        search_field = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "select2-search__field")))
        search_field.clear() # Clear any previous search
        search_field.send_keys(symbol)
        time.sleep(1.5)
        search_field.send_keys(Keys.ENTER)
        
        # 2. Set the Date
        date_input = wait.until(EC.presence_of_element_located((By.NAME, "start_date")))
        date_input.click() # Click to focus
        date_input.send_keys(Keys.CONTROL + "a") # Select all existing text
        date_input.send_keys(Keys.BACKSPACE)
        date_input.send_keys(START_DATE)
        
        # 3. TRIGGER FILTER VIA KEYBOARD
        # Pressing ENTER on the date field is often more reliable than the button
        print(f"   Submitting filter...")
        date_input.send_keys(Keys.ENTER)
        
        # Wait for the AJAX table to refresh
        time.sleep(6) 

        # 4. Extract Table
        table = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table.table-bordered")))
        df_new = pd.read_html(StringIO(table.get_attribute('outerHTML')))[0]

        if not df_new.empty:
            file_path = os.path.join(DATA_DIR, f"{symbol}.csv")
            df_new.to_csv(file_path, index=False)
            print(f"   ✅ Success: {symbol}")
            return True
        return False

    except Exception as e:
        print(f"   ❌ Failed: {symbol}")
        return False

# --- MAIN LOOP ---
if os.path.exists(METADATA_FILE):
    symbols = pd.read_csv(METADATA_FILE)['Symbol'].tolist()
    for i, sym in enumerate(symbols):
        # If it fails, we try a quick refresh of the page and move to next
        success = sync_stock(sym)
        if not success:
            driver.get("https://nepsealpha.com/nepse-data")
            time.sleep(2)
        
        print(f"Progress: {i+1}/{len(symbols)}")
else:
    print("Metadata not found.")

driver.quit()