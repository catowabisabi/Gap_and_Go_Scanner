import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Callable
from ..risk_management.position_manager import PositionManager
from ..utils.logger import setup_logger

class BacktestEngine:
    def __init__(self,
                 strategy: Callable,
                 symbols: List[str],
                 start_date: datetime,
                 end_date: datetime,
                 initial_capital: float = 100000,
                 position_size: float = 0.1,
                 commission: float = 0.001):
        """
        回測引擎初始化
        
        Args:
            strategy: 策略函數
            symbols: 股票代碼列表
            start_date: 開始日期
            end_date: 結束日期
            initial_capital: 初始資金
            position_size: 倉位大小比例
            commission: 手續費率
        """
        self.strategy = strategy
        self.symbols = symbols
        self.start_date = start_date
        self.end_date = end_date
        self.initial_capital = initial_capital
        self.position_size = position_size
        self.commission = commission
        
        self.position_manager = PositionManager(
            initial_capital=initial_capital,
            max_position_size=position_size
        )
        
        self.logger = setup_logger('backtest_engine')
        self.trades: List[Dict] = []
        self.daily_returns: List[float] = []
        
    def load_data(self) -> pd.DataFrame:
        """
        加載歷史數據
        """
        # 這裡需要實現數據加載邏輯
        # 可以從CSV文件或數據庫加載
        pass
        
    def calculate_metrics(self) -> Dict:
        """
        計算回測指標
        """
        if not self.daily_returns:
            return {}
            
        returns = np.array(self.daily_returns)
        
        # 計算年化收益率
        annual_return = np.mean(returns) * 252
        
        # 計算夏普比率
        risk_free_rate = 0.02  # 假設無風險利率為2%
        excess_returns = returns - risk_free_rate/252
        sharpe_ratio = np.sqrt(252) * np.mean(excess_returns) / np.std(returns)
        
        # 計算最大回撤
        cumulative_returns = (1 + returns).cumprod()
        rolling_max = np.maximum.accumulate(cumulative_returns)
        drawdowns = (cumulative_returns - rolling_max) / rolling_max
        max_drawdown = np.min(drawdowns)
        
        # 計算勝率
        profitable_trades = len([t for t in self.trades if t['pnl'] > 0])
        total_trades = len(self.trades)
        win_rate = profitable_trades / total_trades if total_trades > 0 else 0
        
        return {
            'total_return': (self.position_manager.current_capital - self.initial_capital) / self.initial_capital,
            'annual_return': annual_return,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'total_trades': total_trades,
            'profitable_trades': profitable_trades
        }
        
    def run(self) -> Dict:
        """
        執行回測
        """
        data = self.load_data()
        if data.empty:
            self.logger.error("無法加載數據")
            return {}
            
        current_date = self.start_date
        while current_date <= self.end_date:
            if current_date.weekday() < 5:  # 只在工作日交易
                # 獲取當日數據
                daily_data = data[data.index.date == current_date.date()]
                
                if not daily_data.empty:
                    # 執行策略
                    signals = self.strategy(daily_data)
                    
                    # 處理信號
                    for signal in signals:
                        symbol = signal['symbol']
                        action = signal['action']
                        price = signal['price']
                        
                        if action == 'buy':
                            quantity = int(self.position_manager.current_capital * self.position_size / price)
                            if quantity > 0:
                                success = self.position_manager.open_position(symbol, price, quantity)
                                if success:
                                    self.trades.append({
                                        'date': current_date,
                                        'symbol': symbol,
                                        'action': 'buy',
                                        'price': price,
                                        'quantity': quantity
                                    })
                        elif action == 'sell':
                            trade_result = self.position_manager.close_position(symbol, price)
                            if trade_result:
                                self.trades.append({
                                    'date': current_date,
                                    'symbol': symbol,
                                    'action': 'sell',
                                    'price': price,
                                    'quantity': trade_result['quantity'],
                                    'pnl': trade_result['pnl']
                                })
                    
                    # 計算當日收益率
                    daily_return = self.position_manager.daily_pnl / self.position_manager.current_capital
                    self.daily_returns.append(daily_return)
                    
                    # 重置當日盈虧
                    self.position_manager.reset_daily_pnl()
            
            current_date += timedelta(days=1)
        
        # 計算回測指標
        metrics = self.calculate_metrics()
        
        self.logger.info("回測完成")
        self.logger.info(f"回測指標: {metrics}")
        
        return metrics 