import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
from typing import Dict, List, Optional
import os
import json
from jinja2 import Template
from ..visualization.chart_generator import ChartGenerator
from ..monitoring.performance_monitor import PerformanceMonitor

class ReportGenerator:
    def __init__(self, output_dir: str = 'output/reports'):
        """
        報告生成器
        
        Args:
            output_dir: 報告輸出目錄
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.chart_generator = ChartGenerator()
        self.performance_monitor = PerformanceMonitor()
        
    def generate_html_report(self,
                           trades: List[Dict],
                           market_data: pd.DataFrame,
                           report_date: Optional[datetime] = None,
                           title: str = "策略績效報告") -> str:
        """
        生成HTML格式的報告
        
        Args:
            trades: 交易記錄
            market_data: 市場數據
            report_date: 報告日期
            title: 報告標題
        """
        if report_date is None:
            report_date = datetime.now()
            
        # 計算績效指標
        daily_metrics = self.performance_monitor.calculate_daily_metrics(trades)
        strategy_metrics = self.performance_monitor.calculate_strategy_metrics(daily_metrics)
        risk_alerts = self.performance_monitor.monitor_risk_limits(daily_metrics)
        
        # 生成圖表
        price_chart = self.chart_generator.plot_price_and_signals(
            market_data, trades, "價格和交易信號"
        )
        
        performance_chart = self.chart_generator.plot_performance(
            daily_metrics['pnl'], strategy_metrics, "策略績效"
        )
        
        # 讀取HTML模板
        template_str = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>{{ title }}</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    background-color: #f5f5f5;
                }
                .container {
                    max-width: 1200px;
                    margin: 0 auto;
                    background-color: white;
                    padding: 20px;
                    border-radius: 5px;
                    box-shadow: 0 0 10px rgba(0,0,0,0.1);
                }
                .header {
                    text-align: center;
                    margin-bottom: 30px;
                }
                .metrics-container {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }
                .metric-card {
                    background-color: #f8f9fa;
                    padding: 15px;
                    border-radius: 5px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.05);
                }
                .chart-container {
                    margin-bottom: 30px;
                }
                .alert {
                    padding: 10px;
                    margin: 10px 0;
                    border-radius: 5px;
                    background-color: #fff3cd;
                    border: 1px solid #ffeeba;
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 20px;
                }
                th, td {
                    padding: 12px;
                    text-align: left;
                    border-bottom: 1px solid #ddd;
                }
                th {
                    background-color: #f8f9fa;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{{ title }}</h1>
                    <p>報告生成時間: {{ report_date }}</p>
                </div>
                
                <h2>策略績效指標</h2>
                <div class="metrics-container">
                    {% for key, value in strategy_metrics.items() %}
                    <div class="metric-card">
                        <h3>{{ key }}</h3>
                        <p>{{ "%.2f"|format(value) if value is number else value }}</p>
                    </div>
                    {% endfor %}
                </div>
                
                <h2>風險提醒</h2>
                {% if risk_alerts %}
                {% for alert in risk_alerts %}
                <div class="alert">
                    <strong>{{ alert.type }}</strong>
                    <p>{{ alert.message }}</p>
                    <small>日期: {{ alert.date }}</small>
                </div>
                {% endfor %}
                {% else %}
                <p>無風險提醒</p>
                {% endif %}
                
                <h2>圖表分析</h2>
                <div class="chart-container">
                    {{ price_chart | safe }}
                </div>
                <div class="chart-container">
                    {{ performance_chart | safe }}
                </div>
                
                <h2>最近交易記錄</h2>
                <table>
                    <thead>
                        <tr>
                            <th>日期</th>
                            <th>股票</th>
                            <th>操作</th>
                            <th>價格</th>
                            <th>數量</th>
                            <th>盈虧</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for trade in recent_trades %}
                        <tr>
                            <td>{{ trade.date }}</td>
                            <td>{{ trade.symbol }}</td>
                            <td>{{ trade.action }}</td>
                            <td>{{ "%.2f"|format(trade.price) }}</td>
                            <td>{{ trade.quantity }}</td>
                            <td>{{ "%.2f"|format(trade.pnl) if trade.pnl else "-" }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </body>
        </html>
        """
        
        # 準備模板數據
        template_data = {
            'title': title,
            'report_date': report_date.strftime('%Y-%m-%d %H:%M:%S'),
            'strategy_metrics': strategy_metrics,
            'risk_alerts': risk_alerts,
            'price_chart': price_chart.to_html(full_html=False),
            'performance_chart': performance_chart.to_html(full_html=False),
            'recent_trades': trades[-10:]  # 最近10筆交易
        }
        
        # 渲染模板
        template = Template(template_str)
        html_content = template.render(**template_data)
        
        # 保存報告
        filename = f"strategy_report_{report_date.strftime('%Y%m%d')}.html"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        return filepath
        
    def generate_pdf_report(self,
                          trades: List[Dict],
                          market_data: pd.DataFrame,
                          report_date: Optional[datetime] = None,
                          title: str = "策略績效報告") -> str:
        """
        生成PDF格式的報告
        
        Args:
            trades: 交易記錄
            market_data: 市場數據
            report_date: 報告日期
            title: 報告標題
        """
        # 首先生成HTML報告
        html_path = self.generate_html_report(trades, market_data, report_date, title)
        
        # 使用 wkhtmltopdf 將 HTML 轉換為 PDF
        pdf_path = html_path.replace('.html', '.pdf')
        os.system(f'wkhtmltopdf {html_path} {pdf_path}')
        
        return pdf_path
        
    def generate_excel_report(self,
                            trades: List[Dict],
                            market_data: pd.DataFrame,
                            report_date: Optional[datetime] = None) -> str:
        """
        生成Excel格式的報告
        
        Args:
            trades: 交易記錄
            market_data: 市場數據
            report_date: 報告日期
        """
        if report_date is None:
            report_date = datetime.now()
            
        # 計算績效指標
        daily_metrics = self.performance_monitor.calculate_daily_metrics(trades)
        strategy_metrics = self.performance_monitor.calculate_strategy_metrics(daily_metrics)
        risk_alerts = self.performance_monitor.monitor_risk_limits(daily_metrics)
        
        # 創建Excel文件
        filename = f"strategy_report_{report_date.strftime('%Y%m%d')}.xlsx"
        filepath = os.path.join(self.output_dir, filename)
        
        with pd.ExcelWriter(filepath) as writer:
            # 交易記錄
            pd.DataFrame(trades).to_excel(writer, sheet_name='交易記錄', index=False)
            
            # 每日指標
            daily_metrics.to_excel(writer, sheet_name='每日指標')
            
            # 策略指標
            pd.DataFrame([strategy_metrics]).to_excel(writer, sheet_name='策略指標')
            
            # 風險提醒
            pd.DataFrame(risk_alerts).to_excel(writer, sheet_name='風險提醒', index=False)
            
        return filepath 