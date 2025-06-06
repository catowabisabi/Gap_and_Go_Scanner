from typing import Dict, List
import pandas as pd
from datetime import datetime
from ..utils.logger import setup_logger

class PositionManager:
    def __init__(self, 
                 initial_capital: float,
                 max_position_size: float = 0.1,  # 最大單一倉位佔總資金比例
                 max_daily_loss: float = 0.02,    # 最大日虧損比例
                 max_total_positions: int = 5):   # 最大同時持倉數量
        
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.max_position_size = max_position_size
        self.max_daily_loss = max_daily_loss
        self.max_total_positions = max_total_positions
        
        self.positions: Dict[str, Dict] = {}  # 當前持倉
        self.daily_pnl = 0.0                  # 當日盈虧
        self.logger = setup_logger('position_manager')
        
    def can_open_position(self, symbol: str, price: float, quantity: int) -> bool:
        """
        檢查是否可以開新倉位
        """
        position_value = price * quantity
        
        # 檢查是否超過最大持倉數量
        if len(self.positions) >= self.max_total_positions:
            self.logger.warning(f"達到最大持倉數量限制: {self.max_total_positions}")
            return False
            
        # 檢查是否超過單一倉位限制
        if position_value > self.current_capital * self.max_position_size:
            self.logger.warning(f"倉位大小超過限制: {position_value} > {self.current_capital * self.max_position_size}")
            return False
            
        # 檢查是否已有相同股票的倉位
        if symbol in self.positions:
            self.logger.warning(f"已有 {symbol} 的倉位")
            return False
            
        return True
        
    def open_position(self, symbol: str, price: float, quantity: int, position_type: str = 'long') -> bool:
        """
        開倉
        """
        if not self.can_open_position(symbol, price, quantity):
            return False
            
        position_value = price * quantity
        self.positions[symbol] = {
            'quantity': quantity,
            'entry_price': price,
            'current_price': price,
            'type': position_type,
            'value': position_value,
            'entry_time': datetime.now()
        }
        
        self.logger.info(f"開倉 {symbol}: 數量={quantity}, 價格={price}, 類型={position_type}")
        return True
        
    def update_position(self, symbol: str, current_price: float) -> None:
        """
        更新倉位當前價格和價值
        """
        if symbol in self.positions:
            position = self.positions[symbol]
            old_value = position['value']
            new_value = current_price * position['quantity']
            
            position['current_price'] = current_price
            position['value'] = new_value
            
            # 更新當日盈虧
            self.daily_pnl += (new_value - old_value)
            
            # 檢查是否觸及止損
            if self.daily_pnl < -self.initial_capital * self.max_daily_loss:
                self.logger.warning(f"達到每日最大虧損限制: {self.daily_pnl}")
                
    def close_position(self, symbol: str, price: float) -> Dict:
        """
        平倉
        """
        if symbol not in self.positions:
            return {}
            
        position = self.positions.pop(symbol)
        pnl = (price - position['entry_price']) * position['quantity']
        if position['type'] == 'short':
            pnl = -pnl
            
        self.current_capital += pnl
        self.daily_pnl += pnl
        
        self.logger.info(f"平倉 {symbol}: 價格={price}, 盈虧={pnl}")
        
        return {
            'symbol': symbol,
            'entry_price': position['entry_price'],
            'exit_price': price,
            'quantity': position['quantity'],
            'pnl': pnl,
            'hold_time': datetime.now() - position['entry_time']
        }
        
    def get_position_summary(self) -> pd.DataFrame:
        """
        獲取當前倉位摘要
        """
        if not self.positions:
            return pd.DataFrame()
            
        summary = []
        for symbol, pos in self.positions.items():
            pnl = (pos['current_price'] - pos['entry_price']) * pos['quantity']
            if pos['type'] == 'short':
                pnl = -pnl
                
            summary.append({
                'symbol': symbol,
                'type': pos['type'],
                'quantity': pos['quantity'],
                'entry_price': pos['entry_price'],
                'current_price': pos['current_price'],
                'current_value': pos['value'],
                'unrealized_pnl': pnl,
                'hold_time': datetime.now() - pos['entry_time']
            })
            
        return pd.DataFrame(summary)
        
    def reset_daily_pnl(self) -> None:
        """
        重置每日盈虧
        """
        self.daily_pnl = 0.0 