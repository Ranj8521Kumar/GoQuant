"""
Fee calculation model.
"""
from typing import Dict, Any, Optional

from utils.logger import setup_logger
from utils.performance import performance_tracker, timeit

logger = setup_logger("fee")

# OKX fee tiers (as of 2023)
# Source: https://www.okx.com/fees
OKX_FEE_TIERS = {
    'VIP0': {'maker': 0.0008, 'taker': 0.0010},  # 0.08% maker, 0.10% taker
    'VIP1': {'maker': 0.0007, 'taker': 0.0009},  # 0.07% maker, 0.09% taker
    'VIP2': {'maker': 0.0006, 'taker': 0.0008},  # 0.06% maker, 0.08% taker
    'VIP3': {'maker': 0.0005, 'taker': 0.0007},  # 0.05% maker, 0.07% taker
    'VIP4': {'maker': 0.0004, 'taker': 0.0006},  # 0.04% maker, 0.06% taker
    'VIP5': {'maker': 0.0003, 'taker': 0.0005},  # 0.03% maker, 0.05% taker
}

class FeeModel:
    """Model for calculating trading fees."""
    
    def __init__(self, exchange: str = 'OKX'):
        """
        Initialize the fee model.
        
        Args:
            exchange: Exchange name
        """
        self.exchange = exchange
        
        # Set fee tiers based on exchange
        if exchange.upper() == 'OKX':
            self.fee_tiers = OKX_FEE_TIERS
        else:
            logger.warning(f"Unknown exchange: {exchange}, using OKX fee tiers")
            self.fee_tiers = OKX_FEE_TIERS
    
    @timeit(performance_tracker, "fee_calculation")
    def calculate_fee(self, 
                     quantity: float, 
                     price: float, 
                     fee_tier: str = 'VIP0',
                     maker_proportion: float = 0.0) -> Dict[str, float]:
        """
        Calculate trading fees.
        
        Args:
            quantity: Quantity to execute
            price: Price of the asset
            fee_tier: Fee tier (e.g., 'VIP0', 'VIP1', etc.)
            maker_proportion: Proportion of maker orders (between 0 and 1)
            
        Returns:
            Dictionary with fee details
        """
        # Get fee rates for the specified tier
        if fee_tier not in self.fee_tiers:
            logger.warning(f"Unknown fee tier: {fee_tier}, using VIP0")
            fee_tier = 'VIP0'
        
        maker_rate = self.fee_tiers[fee_tier]['maker']
        taker_rate = self.fee_tiers[fee_tier]['taker']
        
        # Calculate notional value
        notional = quantity * price
        
        # Calculate maker and taker fees
        maker_fee = notional * maker_rate * maker_proportion
        taker_fee = notional * taker_rate * (1 - maker_proportion)
        
        # Total fee
        total_fee = maker_fee + taker_fee
        
        # Calculate effective fee rate
        effective_rate = total_fee / notional if notional > 0 else 0
        
        return {
            'maker_fee': maker_fee,
            'taker_fee': taker_fee,
            'total_fee': total_fee,
            'effective_rate': effective_rate,
            'effective_bps': effective_rate * 10000,
            'notional': notional
        }
