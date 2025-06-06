import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
import os
from ..utils.logger import setup_logger

class PerformanceMonitor:
    def __init__(self, output_dir: str = 'output/monitoring'):
        """
        績效監控系統
        
        Args:
            output_dir: 輸出目錄
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.logger = setup_logger('performance_monitor')
        
    def calculate_daily_metrics(self, trades: List[Dict]) -> pd.DataFrame:
        """
        計算每日交易指標
        
        Args:
            trades: 交易記錄列表
        """
        if not trades:
            return pd.DataFrame()
            
        # 轉換為DataFrame
        df = pd.DataFrame(trades)
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date')
        
        # 計算每日指標
        daily_metrics = pd.DataFrame()
        
        # 交易次數
        daily_metrics['trade_count'] = df.resample('D').size()
        
        # 盈虧
        daily_metrics['pnl'] = df.resample('D')['pnl'].sum()
        
        # 勝率
        def win_rate(x):
            if len(x) == 0:
                return 0
            return len(x[x['pnl'] > 0]) / len(x)
            
        daily_metrics['win_rate'] = df.resample('D').apply(win_rate)
        
        # 平均盈虧比
        def profit_loss_ratio(x):
            wins = x[x['pnl'] > 0]['pnl']
            losses = x[x['pnl'] < 0]['pnl']
            if len(losses) == 0 or abs(losses.mean()) == 0:
                return 0
            return wins.mean() / abs(losses.mean()) if len(wins) > 0 else 0
            
        daily_metrics['profit_loss_ratio'] = df.resample('D').apply(profit_loss_ratio)
        
        return daily_metrics
        
    def calculate_strategy_metrics(self, daily_metrics: pd.DataFrame) -> Dict:
        """
        計算策略整體指標
        
        Args:
            daily_metrics: 每日指標數據
        """
        if daily_metrics.empty:
            return {}
            
        total_days = len(daily_metrics)
        trading_days = len(daily_metrics[daily_metrics['trade_count'] > 0])
        
        metrics = {
            'total_pnl': daily_metrics['pnl'].sum(),
            'average_daily_pnl': daily_metrics['pnl'].mean(),
            'pnl_std': daily_metrics['pnl'].std(),
            'total_trades': daily_metrics['trade_count'].sum(),
            'average_trades_per_day': daily_metrics['trade_count'].mean(),
            'average_win_rate': daily_metrics['win_rate'].mean(),
            'best_day_pnl': daily_metrics['pnl'].max(),
            'worst_day_pnl': daily_metrics['pnl'].min(),
            'average_profit_loss_ratio': daily_metrics['profit_loss_ratio'].mean(),
            'trading_days_ratio': trading_days / total_days if total_days > 0 else 0
        }
        
        # 計算夏普比率
        daily_returns = daily_metrics['pnl'].pct_change()
        metrics['sharpe_ratio'] = np.sqrt(252) * daily_returns.mean() / daily_returns.std()
        
        # 計算最大回撤
        cumulative_pnl = daily_metrics['pnl'].cumsum()
        rolling_max = cumulative_pnl.expanding().max()
        drawdowns = (cumulative_pnl - rolling_max) / rolling_max
        metrics['max_drawdown'] = drawdowns.min()
        
        return metrics
        
    def monitor_risk_limits(self,
                          daily_metrics: pd.DataFrame,
                          max_daily_loss: float = -10000,
                          max_drawdown: float = -0.2) -> List[Dict]:
        """
        監控風險限制
        
        Args:
            daily_metrics: 每日指標數據
            max_daily_loss: 最大日虧損限制
            max_drawdown: 最大回撤限制
        """
        alerts = []
        
        # 檢查日虧損
        daily_losses = daily_metrics[daily_metrics['pnl'] < max_daily_loss]
        for date, row in daily_losses.iterrows():
            alerts.append({
                'date': date,
                'type': 'daily_loss_limit',
                'message': f"日虧損 ({row['pnl']:.2f}) 超過限制 ({max_daily_loss})",
                'severity': 'high'
            })
            
        # 檢查回撤
        cumulative_pnl = daily_metrics['pnl'].cumsum()
        rolling_max = cumulative_pnl.expanding().max()
        drawdowns = (cumulative_pnl - rolling_max) / rolling_max
        
        if drawdowns.min() < max_drawdown:
            alerts.append({
                'date': drawdowns.idxmin(),
                'type': 'max_drawdown',
                'message': f"回撤 ({drawdowns.min():.2%}) 超過限制 ({max_drawdown:.2%})",
                'severity': 'high'
            })
            
        return alerts
        
    def save_report(self,
                   daily_metrics: pd.DataFrame,
                   strategy_metrics: Dict,
                   alerts: List[Dict],
                   report_date: Optional[datetime] = None) -> str:
        """
        保存監控報告
        
        Args:
            daily_metrics: 每日指標數據
            strategy_metrics: 策略指標
            alerts: 風險提醒
            report_date: 報告日期
        """
        if report_date is None:
            report_date = datetime.now()
            
        report = {
            'date': report_date.strftime('%Y-%m-%d'),
            'daily_metrics': daily_metrics.to_dict(),
            'strategy_metrics': strategy_metrics,
            'alerts': alerts
        }
        
        # 保存報告
        filename = f"performance_report_{report_date.strftime('%Y%m%d')}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
            
        self.logger.info(f"績效報告已保存至: {filepath}")
        
        return filepath
        
    def load_report(self, report_date: datetime) -> Dict:
        """
        加載監控報告
        
        Args:
            report_date: 報告日期
        """
        filename = f"performance_report_{report_date.strftime('%Y%m%d')}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"找不到報告文件: {filepath}")
            
        with open(filepath, 'r', encoding='utf-8') as f:
            report = json.load(f)
            
        return report 