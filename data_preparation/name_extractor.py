import pandas as pd
import time
import os
from io import StringIO
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# --- SECTION 1 ---
options = Options()
options.add_argument("--disable-blink-features=AutomationControlled")
# to make it like a human is accessing the webpage
options.add_experimental_option("excludeSwitches", ["enable-automation"])
# to remove a prompy saying " this browser is controlled by selenium"
options.add_argument("--start-maximized")
# full screen

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
# open chrome and do the above settings

try:
    # --- SECTION 2: NAVIGATION ---
    print("Step 1: Opening the Traded Stocks page...")
    driver.get("https://nepsealpha.com/traded-stocks")
    
    wait = WebDriverWait(driver, 30)
    
    # Wait for the table to actually appear by looking for the "Symbol" header
    print("Waiting for table headers...")
    wait.until(EC.presence_of_element_located((By.XPATH, "//th[contains(text(),'Symbol')]")))
    # wait until excepted condition is met 
    time.sleep(2)

    # --- SECTION 3: EXPAND VIEW ---
    print("Step 2: Attempting to expand table to maximum entries...")
    try:
        dropdown = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "select[name*='length'], .dataTables_length select")))
        select = Select(dropdown)
        
        # Check all available options in the dropdown
        options_values = [opt.get_attribute("value") for opt in select.options]
        
        if '-1' in options_values:
            select.select_by_value('-1') # '-1' usually means 'Show All'
        else:
            # Select the last index (the largest number available, e.g., 100)
            select.select_by_index(len(select.options) - 1)
        
        print("Set table to maximum display capacity.")
        time.sleep(5) # Allow time for the large table to render
    except Exception as e:
        print(f"Note: Could not change dropdown (maybe only one page exists).")

    # --- SECTION 4: PAGINATION LOOP ---
    all_dfs = []
    page = 1

    while True:
        print(f"Scraping data from page {page}...")
        
        # Target the table that contains the Symbol header
        target_table = driver.find_element(By.XPATH, "//th[contains(text(),'Symbol')]/ancestor::table")
        table_html = target_table.get_attribute('outerHTML')
        
        # Convert HTML to DataFrame
        df_page = pd.read_html(StringIO(table_html))[0]
        all_dfs.append(df_page)

        # Look for the 'Next' button
        try:
            # We look for a link or button that contains the text 'Next'
            next_btn = driver.find_element(By.XPATH, "//a[contains(text(),'Next')] | //button[contains(text(),'Next')]")
            
            # Check if the button is disabled (common in DataTables)
            classes = next_btn.get_attribute("class")
            if "disabled" in classes or not next_btn.is_enabled():
                print("Reached the last page.")
                break
            
            # If not disabled, click it
            driver.execute_script("arguments[0].click();", next_btn)
            time.sleep(3)
            page += 1
        except:
            print("No 'Next' button found or only one page exists.")
            break

    # --- SECTION 5: COMBINE, CLEAN & SAVE ---
    final_df = pd.concat(all_dfs, ignore_index=True)
    final_df.columns = final_df.columns.str.strip()
    
    # Identify 'Symbol' and 'Name'
    if 'Symbol' in final_df.columns:
        name_col = [c for c in final_df.columns if 'Name' in c or 'Company' in c][0]
        
        metadata = final_df[['Symbol', name_col]].copy()
        metadata.columns = ['Symbol', 'Company_Name']
        
        # Clean up duplicates in case of overlap during pagination
        metadata = metadata.drop_duplicates(subset=['Symbol']).dropna()

        # Save to absolute path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, 'metadata.csv')
        
        metadata.to_csv(file_path, index=False)
        print(f"\n✅ TOTAL SUCCESS!")
        print(f"Captured {len(metadata)} unique stocks.")
        # print(f"File saved at: {file_path}")
    else:
        print("❌ Error: 'Symbol' column was not found in the scraped data.")

except Exception as e:
    print(f"❌ Error encountered: {e}")
    driver.save_screenshot("final_error_debug.png")

finally:
    driver.quit()