import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
from typing import List, Dict, Optional
import os

class ChartGenerator:
    def __init__(self, output_dir: str = 'output/charts'):
        """
        初始化圖表生成器
        
        Args:
            output_dir: 圖表輸出目錄
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
    def plot_price_and_signals(self,
                             data: pd.DataFrame,
                             signals: List[Dict],
                             title: str,
                             save_path: Optional[str] = None) -> None:
        """
        繪製價格和交易信號圖
        
        Args:
            data: 價格數據
            signals: 交易信號列表
            title: 圖表標題
            save_path: 保存路徑
        """
        fig = make_subplots(rows=2, cols=1,
                           shared_xaxes=True,
                           vertical_spacing=0.03,
                           subplot_titles=(title, 'Volume'),
                           row_heights=[0.7, 0.3])
        
        # 添加K線圖
        fig.add_trace(
            go.Candlestick(
                x=data.index,
                open=data['open'],
                high=data['high'],
                low=data['low'],
                close=data['close'],
                name='Price'
            ),
            row=1, col=1
        )
        
        # 添加成交量
        fig.add_trace(
            go.Bar(
                x=data.index,
                y=data['volume'],
                name='Volume'
            ),
            row=2, col=1
        )
        
        # 添加移動平均線
        if 'ma' in data.columns:
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data['ma'],
                    name='MA20',
                    line=dict(color='orange')
                ),
                row=1, col=1
            )
        
        # 添加交易信號
        buy_dates = []
        buy_prices = []
        sell_dates = []
        sell_prices = []
        
        for signal in signals:
            if signal['action'] == 'buy':
                buy_dates.append(signal['date'])
                buy_prices.append(signal['price'])
            elif signal['action'] == 'sell':
                sell_dates.append(signal['date'])
                sell_prices.append(signal['price'])
        
        # 買入點
        fig.add_trace(
            go.Scatter(
                x=buy_dates,
                y=buy_prices,
                mode='markers',
                name='Buy',
                marker=dict(
                    symbol='triangle-up',
                    size=12,
                    color='red'
                )
            ),
            row=1, col=1
        )
        
        # 賣出點
        fig.add_trace(
            go.Scatter(
                x=sell_dates,
                y=sell_prices,
                mode='markers',
                name='Sell',
                marker=dict(
                    symbol='triangle-down',
                    size=12,
                    color='green'
                )
            ),
            row=1, col=1
        )
        
        # 更新布局
        fig.update_layout(
            xaxis_rangeslider_visible=False,
            height=800
        )
        
        if save_path:
            fig.write_html(os.path.join(self.output_dir, save_path))
        
        fig.show()
        
    def plot_performance(self,
                        returns: pd.Series,
                        metrics: Dict,
                        title: str = 'Strategy Performance',
                        save_path: Optional[str] = None) -> None:
        """
        繪製策略績效圖
        
        Args:
            returns: 收益率序列
            metrics: 績效指標
            title: 圖表標題
            save_path: 保存路徑
        """
        fig = make_subplots(rows=2, cols=2,
                           subplot_titles=('Cumulative Returns',
                                         'Daily Returns',
                                         'Monthly Returns',
                                         'Drawdown'))
        
        # 累積收益
        cumulative_returns = (1 + returns).cumprod()
        fig.add_trace(
            go.Scatter(
                x=returns.index,
                y=cumulative_returns,
                name='Cumulative Returns'
            ),
            row=1, col=1
        )
        
        # 日收益分布
        fig.add_trace(
            go.Histogram(
                x=returns,
                name='Daily Returns'
            ),
            row=1, col=2
        )
        
        # 月收益
        monthly_returns = returns.resample('M').sum()
        fig.add_trace(
            go.Bar(
                x=monthly_returns.index,
                y=monthly_returns,
                name='Monthly Returns'
            ),
            row=2, col=1
        )
        
        # 回撤
        rolling_max = cumulative_returns.expanding().max()
        drawdowns = (cumulative_returns - rolling_max) / rolling_max
        fig.add_trace(
            go.Scatter(
                x=returns.index,
                y=drawdowns,
                name='Drawdown',
                fill='tozeroy'
            ),
            row=2, col=2
        )
        
        # 添加指標註解
        annotations = [
            f"Total Return: {metrics['total_return']:.2%}",
            f"Annual Return: {metrics['annual_return']:.2%}",
            f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}",
            f"Max Drawdown: {metrics['max_drawdown']:.2%}",
            f"Win Rate: {metrics['win_rate']:.2%}"
        ]
        
        for i, text in enumerate(annotations):
            fig.add_annotation(
                x=0.02,
                y=0.98 - i*0.05,
                xref='paper',
                yref='paper',
                text=text,
                showarrow=False,
                font=dict(size=10)
            )
        
        # 更新布局
        fig.update_layout(
            title=title,
            height=800,
            showlegend=True
        )
        
        if save_path:
            fig.write_html(os.path.join(self.output_dir, save_path))
        
        fig.show()
        
    def plot_position_summary(self,
                            position_data: pd.DataFrame,
                            title: str = 'Position Summary',
                            save_path: Optional[str] = None) -> None:
        """
        繪製持倉摘要圖
        
        Args:
            position_data: 持倉數據
            title: 圖表標題
            save_path: 保存路徑
        """
        fig = make_subplots(rows=2, cols=2,
                           subplot_titles=('Position Value Distribution',
                                         'Unrealized PnL',
                                         'Position Types',
                                         'Hold Time Distribution'))
        
        # 倉位價值分布
        fig.add_trace(
            go.Pie(
                labels=position_data['symbol'],
                values=position_data['current_value'],
                name='Position Value'
            ),
            row=1, col=1
        )
        
        # 未實現盈虧
        fig.add_trace(
            go.Bar(
                x=position_data['symbol'],
                y=position_data['unrealized_pnl'],
                name='Unrealized PnL'
            ),
            row=1, col=2
        )
        
        # 倉位類型分布
        position_types = position_data['type'].value_counts()
        fig.add_trace(
            go.Pie(
                labels=position_types.index,
                values=position_types.values,
                name='Position Types'
            ),
            row=2, col=1
        )
        
        # 持倉時間分布
        fig.add_trace(
            go.Histogram(
                x=position_data['hold_time'].dt.total_seconds() / 3600,
                name='Hold Time (hours)'
            ),
            row=2, col=2
        )
        
        # 更新布局
        fig.update_layout(
            title=title,
            height=800,
            showlegend=True
        )
        
        if save_path:
            fig.write_html(os.path.join(self.output_dir, save_path))
        
        fig.show() 