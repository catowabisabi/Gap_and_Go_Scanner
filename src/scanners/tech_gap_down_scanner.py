import datetime
from typing import List, Dict
import pandas as pd
from ..utils.config import (
    API_KEY, SECRET_KEY, BASE_URL,
    QQQ_SYMBOLS, MOVING_AVERAGE_DAYS,
    START_DATE, YESTERDAY, ORDER_DOLLAR_SIZE
)
from ..utils.logger import setup_logger
from ..risk_management.position_manager import PositionManager
from alpaca_trade_api.rest import REST, TimeFrame

class TechGapDownScanner:
    def __init__(self,
                 gap_percent: float = 3.0,
                 initial_capital: float = 100000):
        """
        大型科技股跌幅掃描器
        
        Args:
            gap_percent: 跌幅百分比閾值
            initial_capital: 初始資金
        """
        self.gap_percent = gap_percent
        self.api = REST(key_id=API_KEY,
                       secret_key=SECRET_KEY,
                       base_url=BASE_URL)
        
        self.logger = setup_logger('tech_gap_down_scanner')
        self.position_manager = PositionManager(initial_capital)
        
    def get_market_data(self) -> pd.DataFrame:
        """
        獲取市場數據
        """
        bars = self.api.get_bars(
            QQQ_SYMBOLS,
            TimeFrame.Day,
            START_DATE,
            YESTERDAY
        ).df
        
        # 計算前一日收盤價和移動平均線
        bars['previous_close'] = bars['close'].shift(1)
        bars['ma'] = bars['close'].rolling(MOVING_AVERAGE_DAYS).mean()
        
        return bars
        
    def scan_for_signals(self, bars: pd.DataFrame) -> List[Dict]:
        """
        掃描交易信號
        """
        # 過濾最新的數據
        filtered = bars[bars.index.strftime('%Y-%m-%d') == YESTERDAY.isoformat()].copy()
        filtered['percent'] = ((filtered['open'] - filtered['previous_close']) / filtered['previous_close']) * 100
        
        # 找出跌幅超過閾值的股票
        downgaps = filtered[filtered['percent'] < -abs(self.gap_percent)]
        
        # 進一步過濾：開盤價低於移動平均線
        downgaps_below_ma = downgaps[downgaps['open'] < downgaps['ma']]
        
        signals = []
        for _, row in downgaps_below_ma.iterrows():
            # 計算可買入數量
            quantity = int(ORDER_DOLLAR_SIZE // row['open'])
            if quantity > 0:
                signals.append({
                    'symbol': row.name[1],  # MultiIndex中的symbol
                    'action': 'sell',       # 做空信號
                    'price': row['open'],
                    'quantity': quantity,
                    'gap_percent': row['percent'],
                    'ma': row['ma']
                })
        
        return signals
        
    def execute_trades(self, signals: List[Dict]) -> None:
        """
        執行交易
        """
        for signal in signals:
            try:
                # 檢查是否可以開倉
                if self.position_manager.can_open_position(
                    signal['symbol'],
                    signal['price'],
                    signal['quantity']
                ):
                    # 提交訂單
                    order = self.api.submit_order(
                        symbol=signal['symbol'],
                        qty=signal['quantity'],
                        side='sell',
                        type='market'
                    )
                    
                    # 記錄交易
                    self.logger.info(
                        f"提交賣出訂單: {signal['symbol']}, "
                        f"數量={signal['quantity']}, "
                        f"價格={signal['price']}, "
                        f"ORDER ID={order.id}"
                    )
                    
                    # 更新倉位管理器
                    self.position_manager.open_position(
                        signal['symbol'],
                        signal['price'],
                        signal['quantity'],
                        'short'
                    )
                    
            except Exception as e:
                self.logger.error(f"執行交易時出錯: {str(e)}")
                
    def run(self) -> List[Dict]:
        """
        運行掃描器
        """
        self.logger.info("開始掃描大型科技股跌幅機會...")
        
        # 獲取市場數據
        bars = self.get_market_data()
        
        # 掃描信號
        signals = self.scan_for_signals(bars)
        
        if signals:
            self.logger.info(f"找到 {len(signals)} 個交易信號")
            # 執行交易
            self.execute_trades(signals)
        else:
            self.logger.info("未找到符合條件的交易信號")
            
        return signals
        
if __name__ == '__main__':
    scanner = TechGapDownScanner()
    scanner.run() 