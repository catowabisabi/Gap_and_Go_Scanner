import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from typing import Tuple, Dict, List
import joblib
import os
from ..utils.logger import setup_logger

class GapPredictor:
    def __init__(self, model_dir: str = 'models'):
        """
        缺口預測模型
        
        Args:
            model_dir: 模型保存目錄
        """
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)
        self.logger = setup_logger('gap_predictor')
        self.model = None
        self.scaler = StandardScaler()
        
    def prepare_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        準備特徵數據
        """
        features = pd.DataFrame()
        
        # 價格特徵
        features['price_change'] = data['close'].pct_change()
        features['high_low_diff'] = (data['high'] - data['low']) / data['low']
        features['close_open_diff'] = (data['close'] - data['open']) / data['open']
        
        # 成交量特徵
        features['volume_change'] = data['volume'].pct_change()
        features['volume_ma5'] = data['volume'].rolling(5).mean()
        features['volume_ma20'] = data['volume'].rolling(20).mean()
        
        # 技術指標
        features['ma5'] = data['close'].rolling(5).mean()
        features['ma20'] = data['close'].rolling(20).mean()
        features['ma5_ma20_cross'] = features['ma5'] > features['ma20']
        
        # 波動率
        features['volatility'] = data['close'].rolling(20).std()
        
        # 移除 NaN 值
        features = features.dropna()
        
        return features
        
    def prepare_labels(self, data: pd.DataFrame, threshold: float = 0.03) -> pd.Series:
        """
        準備標籤數據
        
        Args:
            data: 價格數據
            threshold: 缺口閾值
        """
        # 計算次日缺口
        next_day_gap = data['open'].shift(-1) / data['close'] - 1
        
        # 分類標籤：1 表示上漲缺口，-1 表示下跌缺口，0 表示無顯著缺口
        labels = pd.Series(0, index=next_day_gap.index)
        labels[next_day_gap > threshold] = 1
        labels[next_day_gap < -threshold] = -1
        
        return labels[:-1]  # 移除最後一個無法計算的數據點
        
    def train(self, 
             data: pd.DataFrame, 
             threshold: float = 0.03,
             test_size: float = 0.2) -> Dict:
        """
        訓練模型
        
        Args:
            data: 訓練數據
            threshold: 缺口閾值
            test_size: 測試集比例
        """
        # 準備特徵和標籤
        X = self.prepare_features(data)
        y = self.prepare_labels(data, threshold)
        
        # 分割訓練集和測試集
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
        
        # 標準化特徵
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # 訓練模型
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        
        self.model.fit(X_train_scaled, y_train)
        
        # 評估模型
        y_pred = self.model.predict(X_test_scaled)
        report = classification_report(y_test, y_pred, output_dict=True)
        
        # 保存模型
        model_path = os.path.join(self.model_dir, 'gap_predictor.joblib')
        scaler_path = os.path.join(self.model_dir, 'scaler.joblib')
        
        joblib.dump(self.model, model_path)
        joblib.dump(self.scaler, scaler_path)
        
        self.logger.info("模型訓練完成並保存")
        
        return report
        
    def predict(self, data: pd.DataFrame) -> List[Dict]:
        """
        預測缺口機會
        
        Args:
            data: 市場數據
        """
        if self.model is None:
            model_path = os.path.join(self.model_dir, 'gap_predictor.joblib')
            scaler_path = os.path.join(self.model_dir, 'scaler.joblib')
            
            if os.path.exists(model_path) and os.path.exists(scaler_path):
                self.model = joblib.load(model_path)
                self.scaler = joblib.load(scaler_path)
            else:
                raise ValueError("模型未訓練，請先調用 train() 方法")
        
        # 準備特徵
        features = self.prepare_features(data)
        features_scaled = self.scaler.transform(features)
        
        # 預測
        predictions = self.model.predict(features_scaled)
        probabilities = self.model.predict_proba(features_scaled)
        
        # 準備結果
        results = []
        for i, (pred, prob) in enumerate(zip(predictions, probabilities)):
            if pred != 0:  # 只返回有缺口預測的結果
                results.append({
                    'date': features.index[i],
                    'symbol': data.index[i][1] if isinstance(data.index, pd.MultiIndex) else data.index[i],
                    'prediction': 'gap_up' if pred == 1 else 'gap_down',
                    'probability': prob.max(),
                    'features': dict(zip(features.columns, features.iloc[i]))
                })
        
        return results
        
    def get_feature_importance(self) -> pd.Series:
        """
        獲取特徵重要性
        """
        if self.model is None:
            raise ValueError("模型未訓練")
            
        importance = pd.Series(
            self.model.feature_importances_,
            index=self.prepare_features(pd.DataFrame()).columns
        )
        
        return importance.sort_values(ascending=False) 