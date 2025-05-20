"""
Maker/Taker proportion prediction model.
"""
import numpy as np
from typing import Dict, Any, Optional, List, Tuple
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

from utils.logger import setup_logger
from utils.performance import performance_tracker, timeit

logger = setup_logger("maker_taker")

class MakerTakerModel:
    """Model for predicting the proportion of maker vs taker orders."""
    
    def __init__(self):
        """Initialize the maker/taker model."""
        self.model = LogisticRegression()
        self.scaler = StandardScaler()
        self.is_fitted = False
    
    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        """
        Fit the model to training data.
        
        Args:
            X: Features (e.g., quantity, volatility, spread)
            y: Target (maker proportion, between 0 and 1)
        """
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
        self.is_fitted = True
        logger.info("Maker/Taker model fitted")
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Predict maker proportion for new data.
        
        Args:
            X: Features (e.g., quantity, volatility, spread)
            
        Returns:
            Predicted maker proportion (between 0 and 1)
        """
        if not self.is_fitted:
            raise ValueError("Model is not fitted yet")
        
        X_scaled = self.scaler.transform(X)
        return self.model.predict_proba(X_scaled)[:, 1]
    
    @timeit(performance_tracker, "maker_taker_prediction")
    def predict_maker_taker(self, 
                           quantity: float, 
                           volatility: float, 
                           spread_bps: float,
                           order_type: str = 'market') -> Dict[str, float]:
        """
        Predict maker/taker proportion for a trade.
        
        Args:
            quantity: Quantity to execute
            volatility: Volatility of the asset
            spread_bps: Spread in basis points
            order_type: Type of order ('market', 'limit', etc.)
            
        Returns:
            Dictionary with maker and taker proportions
        """
        # For market orders, we assume 100% taker
        if order_type.lower() == 'market':
            return {
                'maker_proportion': 0.0,
                'taker_proportion': 1.0
            }
        
        if not self.is_fitted:
            # If model is not fitted, use a simple heuristic
            logger.warning("Model not fitted, using heuristic")
            
            # Higher volatility and spread typically lead to more taker executions
            # Lower quantity typically leads to more maker executions
            base_maker = 0.5
            vol_factor = min(1.0, volatility * 2)  # Higher volatility reduces maker proportion
            spread_factor = min(1.0, spread_bps / 20)  # Higher spread reduces maker proportion
            quantity_factor = min(1.0, quantity / 10)  # Higher quantity reduces maker proportion
            
            maker_proportion = max(0.0, min(1.0, base_maker - vol_factor * 0.2 - spread_factor * 0.2 - quantity_factor * 0.1))
            taker_proportion = 1.0 - maker_proportion
        else:
            # Use the trained model
            features = np.array([[quantity, volatility, spread_bps]])
            maker_proportion = self.predict(features)[0]
            taker_proportion = 1.0 - maker_proportion
        
        return {
            'maker_proportion': maker_proportion,
            'taker_proportion': taker_proportion
        }


def create_synthetic_data(n_samples: int = 1000) -> Tuple[np.ndarray, np.ndarray]:
    """
    Create synthetic data for model training.
    
    Args:
        n_samples: Number of samples to generate
        
    Returns:
        Tuple of (X, y) where X is features and y is target
    """
    # Generate random features
    quantity = np.random.lognormal(0, 1, n_samples)
    volatility = np.random.uniform(0.1, 0.5, n_samples)
    spread_bps = np.random.uniform(1, 20, n_samples)
    
    # Generate target with some logic
    # Higher volatility, spread, and quantity lead to lower maker proportion
    base_maker = 0.5
    vol_factor = np.minimum(1.0, volatility * 2)
    spread_factor = np.minimum(1.0, spread_bps / 20)
    quantity_factor = np.minimum(1.0, quantity / 10)
    
    maker_proportion = np.maximum(0.0, np.minimum(1.0, 
                                                base_maker - vol_factor * 0.2 - spread_factor * 0.2 - quantity_factor * 0.1))
    
    # Add some noise
    maker_proportion = np.maximum(0.0, np.minimum(1.0, maker_proportion + np.random.normal(0, 0.1, n_samples)))
    
    # Convert to binary for logistic regression
    y = (maker_proportion > 0.5).astype(int)
    
    # Combine features
    X = np.column_stack([quantity, volatility, spread_bps])
    
    return X, y
