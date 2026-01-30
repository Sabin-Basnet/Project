import pandas as pd
import numpy as np

class NepsePipeline:
    def __init__(self, file_path):
        self.file_path = file_path
        self.df = None

    def run(self):
        """Executes the full pipeline in order."""
        self.ingest_and_clean()
        self.add_moving_averages()
        self.add_rsi()
        self.add_macd()
        return self.df

    def ingest_and_clean(self):
        """Cleans the raw NEPSE Alpha format safely."""
        self.df = pd.read_csv(self.file_path)
    
        # Chronological sort (Oldest to Newest)
        self.df['Date'] = pd.to_datetime(self.df['Date'])
        self.df = self.df.sort_values(by='Date', ascending=True)
    
        # List of columns that should be numbers
        cols_to_fix = ['Volume', 'Turn Over', 'Percent Change', 'Open', 'High', 'Low', 'Close']
    
        for col in cols_to_fix:
            if col in self.df.columns:
                # 1. Remove commas and % signs if they exist
                if self.df[col].dtype == 'object':
                    self.df[col] = self.df[col].str.replace(',', '').str.replace('%', '')
            
                # 2. Convert to numeric - dashes will become NaN
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
            
                # 3. Optional: Replace NaN with 0 (if that makes sense for the column)
                # self.df[col] = self.df[col].fillna(0)
    
        self.df = self.df.reset_index(drop=True)

    def add_moving_averages(self):
        """Adds SMA and EMA features."""
        self.df['SMA_20'] = self.df['Close'].rolling(window=20).mean()
        self.df['EMA_12'] = self.df['Close'].ewm(span=12, adjust=False).mean()
        self.df['EMA_26'] = self.df['Close'].ewm(span=26, adjust=False).mean()

    def add_rsi(self, window=14):
        """Calculates Relative Strength Index."""
        delta = self.df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        self.df['RSI'] = 100 - (100 / (1 + rs))

    def add_macd(self):
        """Calculates MACD and Signal Line."""
        self.df['MACD'] = self.df['EMA_12'] - self.df['EMA_26']
        self.df['MACD_Signal'] = self.df['MACD'].ewm(span=9, adjust=False).mean()
        self.df['MACD_Hist'] = self.df['MACD'] - self.df['MACD_Signal']


# --- HOW TO RUN ---
lead_pipeline = NepsePipeline('nepse_data.csv')
final_data = lead_pipeline.run()
print(final_data.tail())