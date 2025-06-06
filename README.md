# Gap and Go Scanner 缺口策略掃描器

一個強大的股票掃描器，用於識別和分析股票市場中的缺口交易機會。該系統支持對大型科技股和小型股票進行監控，並提供完整的風險管理、回測和分析功能。

A powerful stock scanner that identifies and analyzes gap trading opportunities in both small-cap stocks and big tech companies. The system supports monitoring of both large tech stocks and small-cap stocks, with comprehensive risk management, backtesting, and analysis capabilities.

## 功能特點 Features

### 掃描功能 Scanning Features
- 大型科技股下跌缺口掃描 (Tech stocks gap-down scanning)
- 小型股票上漲缺口掃描 (Small-cap stocks gap-up scanning)
- 自動移動平均線分析 (Automated moving average analysis)
- 實時市場數據監控 (Real-time market data monitoring)

### 風險管理 Risk Management
- 倉位規模控制 (Position sizing control)
- 每日最大虧損限制 (Daily loss limits)
- 最大持倉數量限制 (Maximum position limits)
- 單一股票風險控制 (Single stock risk control)

### 回測系統 Backtesting System
- 歷史數據回測 (Historical data backtesting)
- 策略績效分析 (Strategy performance analysis)
- 交易記錄追蹤 (Trade tracking)
- 風險指標計算 (Risk metrics calculation)

### 機器學習功能 Machine Learning Features
- 缺口預測模型 (Gap prediction model)
- 特徵工程 (Feature engineering)
- 模型訓練與評估 (Model training and evaluation)
- 預測結果分析 (Prediction analysis)

### 監控系統 Monitoring System
- 實時績效監控 (Real-time performance monitoring)
- 風險指標追蹤 (Risk metrics tracking)
- 警報系統 (Alert system)
- 自動報告生成 (Automated reporting)

### 報告生成 Reporting
- HTML報告 (HTML reports)
- PDF報告 (PDF reports)
- Excel報告 (Excel reports)
- 圖表可視化 (Chart visualization)

## 安裝說明 Installation

1. 克隆存儲庫 Clone the repository
```bash
git clone https://github.com/yourusername/Gap_and_Go_Scanner.git
cd Gap_and_Go_Scanner
```

2. 創建虛擬環境 Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
```

3. 安裝依賴 Install dependencies
```bash
pip install -r requirements.txt
```

4. 設置環境變量 Set up environment variables
```bash
cp env.example .env
```
編輯 `.env` 文件，填入您的 API 密鑰和其他配置
Edit the `.env` file and fill in your API keys and other configurations

## 使用方法 Usage

### 掃描器使用 Using Scanners

1. 大型科技股下跌掃描 Tech Stocks Gap-Down Scanner
```python
from src.scanners.tech_gap_down_scanner import TechGapDownScanner

scanner = TechGapDownScanner(gap_percent=3.0)
signals = scanner.run()
```

2. 小型股票上漲掃描 Small-cap Stocks Gap-Up Scanner
```python
from src.scanners.smallcap_gap_up_scanner import SmallCapGapUpScanner

scanner = SmallCapGapUpScanner(gap_percent=3.0)
signals = scanner.run()
```

### 機器學習模型使用 Using ML Models

```python
from src.ml_models.gap_predictor import GapPredictor

# 訓練模型
predictor = GapPredictor()
report = predictor.train(historical_data)

# 預測缺口
predictions = predictor.predict(market_data)
```

### 回測系統使用 Using Backtesting System

```python
from src.backtesting.backtest_engine import BacktestEngine
from datetime import datetime

engine = BacktestEngine(
    strategy=your_strategy_function,
    symbols=['AAPL', 'MSFT', 'GOOGL'],
    start_date=datetime(2023, 1, 1),
    end_date=datetime(2023, 12, 31),
    initial_capital=100000
)

results = engine.run()
```

### 監控系統使用 Using Monitoring System

```python
from src.monitoring.performance_monitor import PerformanceMonitor

monitor = PerformanceMonitor()
daily_metrics = monitor.calculate_daily_metrics(trades)
alerts = monitor.monitor_risk_limits(daily_metrics)
```

### 報告生成 Generating Reports

```python
from src.reporting.report_generator import ReportGenerator

generator = ReportGenerator()

# 生成HTML報告
html_report = generator.generate_html_report(trades, market_data)

# 生成PDF報告
pdf_report = generator.generate_pdf_report(trades, market_data)

# 生成Excel報告
excel_report = generator.generate_excel_report(trades, market_data)
```

## 項目結構 Project Structure

```
Gap_and_Go_Scanner/
├── src/                    # 源代碼 Source code
│   ├── scanners/          # 掃描器模塊 Scanner modules
│   ├── risk_management/   # 風險管理模塊 Risk management
│   ├── backtesting/       # 回測系統 Backtesting system
│   ├── visualization/     # 視覺化模塊 Visualization
│   ├── ml_models/        # 機器學習模型 ML models
│   ├── monitoring/       # 監控系統 Monitoring
│   ├── reporting/       # 報告生成 Reporting
│   ├── analysis/        # 分析工具 Analysis tools
│   └── utils/           # 工具函數 Utility functions
├── data/                # 數據文件 Data files
├── output/             # 輸出文件 Output files
│   ├── charts/        # 圖表輸出 Chart output
│   ├── reports/       # 報告輸出 Report output
│   └── monitoring/    # 監控輸出 Monitoring output
├── logs/              # 日誌文件 Log files
├── models/            # 模型文件 Model files
├── notebooks/         # Jupyter notebooks
├── tests/            # 測試文件 Test files
├── requirements.txt   # 依賴列表 Dependencies
├── env.example       # 環境變量示例 Environment variables example
└── README.md        # 項目文檔 Documentation
```

## 配置說明 Configuration

主要配置參數 Main configuration parameters:

- `GAP_PERCENT`: 缺口百分比閾值 Gap percentage threshold
- `MOVING_AVERAGE_DAYS`: 移動平均線天數 Moving average days
- `ORDER_DOLLAR_SIZE`: 單筆訂單金額 Order size in dollars
- `MAX_POSITIONS`: 最大持倉數量 Maximum positions
- `MAX_DAILY_LOSS`: 最大日虧損比例 Maximum daily loss percentage
- `ML_MODEL_PARAMS`: 機器學習模型參數 ML model parameters
- `RISK_LIMITS`: 風險限制參數 Risk limit parameters

## 注意事項 Notes

- 請確保在使用前正確設置 API 密鑰 Make sure to set up API keys before use
- 建議先在模擬賬戶上測試 Recommended to test on paper trading account first
- 注意風險管理設置 Pay attention to risk management settings
- 定期檢查日誌文件 Regularly check log files
- 定期更新機器學習模型 Regularly update ML models
- 監控系統警報設置 Monitor system alert settings

## 貢獻 Contributing

歡迎提交問題和改進建議。
Feel free to submit issues and enhancement requests.

## 許可證 License

MIT License
