import os
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional
from ..utils.logger import setup_logger
from ..utils.output_handler import OutputHandler
from ..utils.config import MOVING_AVERAGE_DAYS, START_DATE, TODAY

class BaseScanner:
    def __init__(self, strategy_name: str, symbols: List[str]):
        """
        Initialize the base scanner.
        
        Args:
            strategy_name (str): Name of the trading strategy
            symbols (List[str]): List of stock symbols to scan
        """
        self.strategy_name = strategy_name
        self.symbols = symbols
        self.logger = setup_logger(strategy_name)
        self.output_handler = OutputHandler(strategy_name)
        
    def calculate_moving_average(self, data: pd.DataFrame, days: int = MOVING_AVERAGE_DAYS) -> float:
        """
        Calculate the moving average for a given period.
        
        Args:
            data (pd.DataFrame): Price data
            days (int): Number of days for moving average
            
        Returns:
            float: Moving average value
        """
        return data['close'].rolling(window=days).mean().iloc[-1]
        
    def calculate_gap_percentage(self, current_price: float, previous_close: float) -> float:
        """
        Calculate the gap percentage between current price and previous close.
        
        Args:
            current_price (float): Current stock price
            previous_close (float): Previous closing price
            
        Returns:
            float: Gap percentage
        """
        return ((current_price - previous_close) / previous_close) * 100
        
    def save_results(self, results: List[Dict], save_json: bool = True, save_csv: bool = True) -> None:
        """
        Save scanning results to files.
        
        Args:
            results (List[Dict]): Scanning results
            save_json (bool): Whether to save as JSON
            save_csv (bool): Whether to save as CSV
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if save_json:
            json_file = self.output_handler.save_json(results)
            self.logger.info(f"Results saved to JSON: {json_file}")
            
        if save_csv:
            csv_file = self.output_handler.save_csv(results)
            self.logger.info(f"Results saved to CSV: {csv_file}")
            
    def scan(self) -> List[Dict]:
        """
        Base scanning method to be implemented by subclasses.
        
        Returns:
            List[Dict]: Scanning results
        """
        raise NotImplementedError("Subclasses must implement scan() method") 