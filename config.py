"""
Configuration settings for the application.
"""

# WebSocket endpoints
WEBSOCKET_ENDPOINTS = {
    'OKX': {
        'BTC-USDT': 'wss://ws.gomarket-cpp.goquant.io/ws/l2-orderbook/okx/BTC-USDT-SWAP',
        'ETH-USDT': 'wss://ws.gomarket-cpp.goquant.io/ws/l2-orderbook/okx/ETH-USDT-SWAP',
        'SOL-USDT': 'wss://ws.gomarket-cpp.goquant.io/ws/l2-orderbook/okx/SOL-USDT-SWAP',
        'XRP-USDT': 'wss://ws.gomarket-cpp.goquant.io/ws/l2-orderbook/okx/XRP-USDT-SWAP',
        'ADA-USDT': 'wss://ws.gomarket-cpp.goquant.io/ws/l2-orderbook/okx/ADA-USDT-SWAP'
    }
}

# Default market parameters
DEFAULT_MARKET_PARAMS = {
    'OKX': {
        'BTC-USDT': {
            'volatility': 0.3,  # Annual volatility
            'avg_daily_volume': 1000000000,  # Average daily volume in USD
            'avg_spread_bps': 1.0  # Average spread in basis points
        },
        'ETH-USDT': {
            'volatility': 0.4,
            'avg_daily_volume': 500000000,
            'avg_spread_bps': 1.5
        },
        'SOL-USDT': {
            'volatility': 0.6,
            'avg_daily_volume': 100000000,
            'avg_spread_bps': 2.0
        },
        'XRP-USDT': {
            'volatility': 0.5,
            'avg_daily_volume': 50000000,
            'avg_spread_bps': 2.5
        },
        'ADA-USDT': {
            'volatility': 0.55,
            'avg_daily_volume': 30000000,
            'avg_spread_bps': 3.0
        }
    }
}

# Fee tiers
FEE_TIERS = {
    'OKX': {
        'VIP0': {'maker': 0.0008, 'taker': 0.0010},  # 0.08% maker, 0.10% taker
        'VIP1': {'maker': 0.0007, 'taker': 0.0009},  # 0.07% maker, 0.09% taker
        'VIP2': {'maker': 0.0006, 'taker': 0.0008},  # 0.06% maker, 0.08% taker
        'VIP3': {'maker': 0.0005, 'taker': 0.0007},  # 0.05% maker, 0.07% taker
        'VIP4': {'maker': 0.0004, 'taker': 0.0006},  # 0.04% maker, 0.06% taker
        'VIP5': {'maker': 0.0003, 'taker': 0.0005},  # 0.03% maker, 0.05% taker
    }
}

# Almgren-Chriss model parameters
ALMGREN_CHRISS_PARAMS = {
    'eta': 0.1,    # Temporary impact factor
    'gamma': 0.1,  # Permanent impact factor
    'T': 1.0       # Time horizon in days
}

# Performance tracking
PERFORMANCE_TRACKING = {
    'max_samples': 1000,  # Maximum number of samples to keep for each metric
    'log_interval': 60    # Log performance metrics every X seconds
}

# Logging
LOGGING = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'log_to_file': True,
    'log_dir': 'logs'
}
