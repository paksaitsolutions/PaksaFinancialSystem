import numpy as np
import pandas as pd
from typing import List, Dict, Any
from ..ml_framework import MLFramework

class AnomalyDetectionService:
    def __init__(self):
        self.ml_framework = MLFramework()
        self.model_name = "transaction_anomaly_detector"
    
    def detect_transaction_anomalies(self, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect anomalous transactions"""
        if not transactions:
            return []
        
        # Convert to DataFrame
        df = pd.DataFrame(transactions)
        
        # Feature engineering
        features = self._extract_features(df)
        
        # Train or load model
        try:
            anomaly_scores = self.ml_framework.predict(self.model_name, features)
        except:
            # Train new model if not exists
            self.ml_framework.train_model(self.model_name, "isolation_forest", features)
            anomaly_scores = self.ml_framework.predict(self.model_name, features)
        
        # Mark anomalies
        anomalies = []
        for i, score in enumerate(anomaly_scores):
            if score == -1:  # Isolation Forest returns -1 for anomalies
                anomaly = transactions[i].copy()
                anomaly['anomaly_score'] = float(score)
                anomaly['anomaly_reason'] = self._get_anomaly_reason(transactions[i])
                anomalies.append(anomaly)
        
        return anomalies
    
    def _extract_features(self, df: pd.DataFrame) -> np.ndarray:
        """Extract features for anomaly detection"""
        features = []
        
        # Amount-based features
        features.append(df['amount'].values if 'amount' in df.columns else np.zeros(len(df)))
        
        # Time-based features (hour of day)
        if 'created_at' in df.columns:
            df['hour'] = pd.to_datetime(df['created_at']).dt.hour
            features.append(df['hour'].values)
        else:
            features.append(np.zeros(len(df)))
        
        # Account-based features
        if 'account_id' in df.columns:
            account_counts = df['account_id'].value_counts()
            features.append(df['account_id'].map(account_counts).values)
        else:
            features.append(np.ones(len(df)))
        
        return np.column_stack(features)
    
    def _get_anomaly_reason(self, transaction: Dict[str, Any]) -> str:
        """Determine reason for anomaly"""
        amount = transaction.get('amount', 0)
        
        if amount > 10000:
            return "Unusually high amount"
        elif amount < 0:
            return "Negative amount"
        else:
            return "Pattern deviation"