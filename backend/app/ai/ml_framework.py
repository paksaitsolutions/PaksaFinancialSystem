import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, accuracy_score, classification_report
from sklearn.cluster import KMeans
from typing import Dict, List, Any, Optional, Tuple
import joblib
import os
import logging

class MLFramework:
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.model_dir = "models"
        self.model_metadata = {}
        os.makedirs(self.model_dir, exist_ok=True)
        self.logger = logging.getLogger(__name__)
    
    def train_model(self, model_name: str, model_type: str, X: np.ndarray, y: Optional[np.ndarray] = None):
        """Train and save a model"""
        if model_type == "isolation_forest":
            model = IsolationForest(contamination=0.1, random_state=42)
            model.fit(X)
        elif model_type == "linear_regression":
            model = LinearRegression()
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            model.fit(X_scaled, y)
            self.scalers[model_name] = scaler
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
        
        self.models[model_name] = model
        self._save_model(model_name, model)
        return model
    
    def predict(self, model_name: str, X: np.ndarray) -> np.ndarray:
        """Make predictions using a trained model"""
        if model_name not in self.models:
            self._load_model(model_name)
        
        model = self.models[model_name]
        if model_name in self.scalers:
            X = self.scalers[model_name].transform(X)
        
        return model.predict(X)
    
    def _save_model(self, model_name: str, model):
        """Save model to disk"""
        model_path = os.path.join(self.model_dir, f"{model_name}.joblib")
        joblib.dump(model, model_path)
        
        if model_name in self.scalers:
            scaler_path = os.path.join(self.model_dir, f"{model_name}_scaler.joblib")
            joblib.dump(self.scalers[model_name], scaler_path)
    
    def _load_model(self, model_name: str):
        """Load model from disk"""
        model_path = os.path.join(self.model_dir, f"{model_name}.joblib")
        if os.path.exists(model_path):
            self.models[model_name] = joblib.load(model_path)
            
            scaler_path = os.path.join(self.model_dir, f"{model_name}_scaler.joblib")
            if os.path.exists(scaler_path):
                self.scalers[model_name] = joblib.load(scaler_path)