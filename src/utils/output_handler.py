import os
import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Union
from .config import OUTPUT_DIR, DEFAULT_JSON_OUTPUT, CSV_COLUMNS

class OutputHandler:
    def __init__(self, strategy_name: str):
        """
        Initialize the output handler for a specific trading strategy.
        
        Args:
            strategy_name (str): Name of the trading strategy (e.g., 'long_smallcaps', 'short_bigtech')
        """
        self.strategy_name = strategy_name
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.output_dir = os.path.join(OUTPUT_DIR, strategy_name)
        os.makedirs(self.output_dir, exist_ok=True)
        
    def save_json(self, data: Union[Dict, List[Dict]], filename: str = None) -> str:
        """
        Save trading data to a JSON file.
        
        Args:
            data: Trading data to save
            filename: Optional custom filename
            
        Returns:
            str: Path to the saved file
        """
        if filename is None:
            filename = f"{self.strategy_name}_{self.timestamp}.json"
            
        if not filename.endswith('.json'):
            filename += '.json'
            
        filepath = os.path.join(self.output_dir, filename)
        
        # Ensure data is in list format
        if isinstance(data, dict):
            data = [data]
            
        # Validate and fill missing fields
        validated_data = []
        for entry in data:
            validated_entry = DEFAULT_JSON_OUTPUT.copy()
            validated_entry.update(entry)
            validated_data.append(validated_entry)
            
        with open(filepath, 'w') as f:
            json.dump(validated_data, f, indent=4)
            
        return filepath
        
    def save_csv(self, data: Union[Dict, List[Dict]], filename: str = None) -> str:
        """
        Save trading data to a CSV file.
        
        Args:
            data: Trading data to save
            filename: Optional custom filename
            
        Returns:
            str: Path to the saved file
        """
        if filename is None:
            filename = f"{self.strategy_name}_{self.timestamp}.csv"
            
        if not filename.endswith('.csv'):
            filename += '.csv'
            
        filepath = os.path.join(self.output_dir, filename)
        
        # Convert to DataFrame
        if isinstance(data, dict):
            data = [data]
        
        df = pd.DataFrame(data)
        
        # Ensure all columns exist
        for col in CSV_COLUMNS:
            if col not in df.columns:
                df[col] = None
                
        # Reorder columns to match CSV_COLUMNS
        df = df.reindex(columns=CSV_COLUMNS)
        
        # Save to CSV
        df.to_csv(filepath, index=False)
        
        return filepath
        
    def load_json(self, filename: str) -> List[Dict]:
        """
        Load trading data from a JSON file.
        
        Args:
            filename: Name of the file to load
            
        Returns:
            List[Dict]: Loaded trading data
        """
        if not filename.endswith('.json'):
            filename += '.json'
            
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'r') as f:
            data = json.load(f)
            
        return data
        
    def load_csv(self, filename: str) -> pd.DataFrame:
        """
        Load trading data from a CSV file.
        
        Args:
            filename: Name of the file to load
            
        Returns:
            pd.DataFrame: Loaded trading data
        """
        if not filename.endswith('.csv'):
            filename += '.csv'
            
        filepath = os.path.join(self.output_dir, filename)
        
        return pd.read_csv(filepath) 