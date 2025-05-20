"""
Implementation of the Almgren-Chriss market impact model.

Reference: https://www.linkedin.com/pulse/understanding-almgren-chriss-model-optimal-portfolio-execution-pal-pmeqc/
"""
import numpy as np
from typing import Dict, Any, Optional

from utils.logger import setup_logger
from utils.performance import performance_tracker, timeit

logger = setup_logger("market_impact")

class AlmgrenChrissModel:
    """
    Implementation of the Almgren-Chriss market impact model for estimating market impact.
    
    The model divides market impact into two components:
    1. Temporary impact: Immediate price change due to the trade
    2. Permanent impact: Long-term price change that remains after the trade
    
    The model uses the following parameters:
    - sigma: Volatility of the asset
    - eta: Temporary impact factor
    - gamma: Permanent impact factor
    - T: Time horizon for execution
    - X: Total quantity to execute
    """
    
    def __init__(self, 
                 sigma: float = 0.3,  # Annual volatility
                 eta: float = 0.1,    # Temporary impact factor
                 gamma: float = 0.1,  # Permanent impact factor
                 T: float = 1.0,      # Time horizon in days
                 X: float = 1.0):     # Total quantity to execute
        """
        Initialize the Almgren-Chriss model.
        
        Args:
            sigma: Volatility of the asset (annualized)
            eta: Temporary impact factor
            gamma: Permanent impact factor
            T: Time horizon for execution (in days)
            X: Total quantity to execute
        """
        self.sigma = sigma
        self.eta = eta
        self.gamma = gamma
        self.T = T
        self.X = X
    
    @timeit(performance_tracker, "market_impact_calculation")
    def calculate_market_impact(self, 
                               quantity: float, 
                               price: float, 
                               market_volume: float,
                               volatility: Optional[float] = None) -> Dict[str, float]:
        """
        Calculate the market impact for a given trade.
        
        Args:
            quantity: Quantity to execute
            price: Current price of the asset
            market_volume: Daily market volume
            volatility: Volatility override (if None, use self.sigma)
            
        Returns:
            Dictionary with temporary impact, permanent impact, and total impact
        """
        # Use provided volatility or default
        sigma = volatility if volatility is not None else self.sigma
        
        # Calculate participation rate (quantity as a fraction of market volume)
        participation_rate = quantity / market_volume
        
        # Calculate temporary impact (immediate price change)
        # Formula: eta * sigma * sqrt(T) * (X/V) * price
        temporary_impact = self.eta * sigma * np.sqrt(self.T) * participation_rate * price
        
        # Calculate permanent impact (long-term price change)
        # Formula: gamma * (X/V) * price
        permanent_impact = self.gamma * participation_rate * price
        
        # Total impact
        total_impact = temporary_impact + permanent_impact
        
        # Calculate impact in basis points
        temporary_impact_bps = (temporary_impact / price) * 10000
        permanent_impact_bps = (permanent_impact / price) * 10000
        total_impact_bps = (total_impact / price) * 10000
        
        return {
            'temporary_impact': temporary_impact,
            'permanent_impact': permanent_impact,
            'total_impact': total_impact,
            'temporary_impact_bps': temporary_impact_bps,
            'permanent_impact_bps': permanent_impact_bps,
            'total_impact_bps': total_impact_bps,
            'participation_rate': participation_rate
        }
    
    def calibrate(self, 
                 historical_trades: list, 
                 historical_impacts: list) -> None:
        """
        Calibrate the model parameters based on historical data.
        
        Args:
            historical_trades: List of historical trades (quantity, price, market_volume)
            historical_impacts: List of observed market impacts
        """
        # This is a simplified calibration method
        # In a real implementation, you would use more sophisticated techniques
        
        # Calculate participation rates
        participation_rates = [trade[0] / trade[2] for trade in historical_trades]
        
        # Calculate price-normalized impacts
        normalized_impacts = [impact / trade[1] for impact, trade in zip(historical_impacts, historical_trades)]
        
        # Simple linear regression to estimate gamma
        if len(participation_rates) > 1:
            self.gamma = np.polyfit(participation_rates, normalized_impacts, 1)[0]
            
            # Estimate eta based on residuals
            residuals = [ni - self.gamma * pr for ni, pr in zip(normalized_impacts, participation_rates)]
            self.eta = np.std(residuals) / (self.sigma * np.sqrt(self.T))
            
            logger.info(f"Calibrated parameters: gamma={self.gamma}, eta={self.eta}")
        else:
            logger.warning("Not enough data for calibration")
