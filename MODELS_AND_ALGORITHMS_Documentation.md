# Models and Algorithms Documentation

This document provides comprehensive documentation for all the models and algorithms used in the Trade Simulator application. Each section explains the mathematical foundations, implementation details, and practical applications of the various components.

## Table of Contents

1. [Market Impact Model (Almgren-Chriss)](#market-impact-model-almgren-chriss)
2. [Slippage Estimation Models](#slippage-estimation-models)
3. [Maker/Taker Proportion Model](#makertaker-proportion-model)
4. [Fee Calculation Model](#fee-calculation-model)
5. [VPN Detection Algorithm](#vpn-detection-algorithm)
6. [Performance Tracking System](#performance-tracking-system)
7. [WebSocket Data Processing](#websocket-data-processing)

---

## Market Impact Model (Almgren-Chriss)

### Overview
The Almgren-Chriss model is a mathematical framework for estimating the market impact of large trades. It divides market impact into two components: temporary and permanent impact.

### Mathematical Foundation

The model is based on the following key equations:

#### Temporary Impact
```
Temporary Impact = η × σ × √T × (X/V) × P
```

Where:
- `η` (eta): Temporary impact factor (default: 0.1)
- `σ` (sigma): Asset volatility (annualized)
- `T`: Time horizon for execution (in days, default: 1.0)
- `X`: Quantity to execute
- `V`: Daily market volume
- `P`: Current asset price

#### Permanent Impact
```
Permanent Impact = γ × (X/V) × P
```

Where:
- `γ` (gamma): Permanent impact factor (default: 0.1)
- `X/V`: Participation rate (fraction of daily volume)

#### Total Impact
```
Total Impact = Temporary Impact + Permanent Impact
```

### Implementation Details

**File**: `models/market_impact.py`

**Key Features**:
- Configurable parameters (η, γ, σ, T)
- Participation rate calculation
- Impact calculation in both absolute values and basis points
- Performance tracking with decorators
- Model calibration capability

**Usage Example**:
```python
model = AlmgrenChrissModel(sigma=0.3, eta=0.1, gamma=0.1)
impact = model.calculate_market_impact(
    quantity=100000,
    price=50000,
    market_volume=1000000000,
    volatility=0.25
)
```

### Practical Applications
- Estimating the cost of large trades
- Optimizing execution strategies
- Risk management for institutional trading
- Portfolio rebalancing cost estimation

---

## Slippage Estimation Models

### Overview
Slippage represents the difference between the expected price of a trade and the actual executed price. The application implements two models for slippage estimation.

### Linear Regression Slippage Model

#### Mathematical Foundation
```
Slippage = β₀ + β₁ × log(Quantity) + β₂ × Volatility + β₃ × Spread + ε
```

Where:
- `β₀, β₁, β₂, β₃`: Regression coefficients
- `Quantity`: Trade size
- `Volatility`: Asset volatility
- `Spread`: Bid-ask spread
- `ε`: Error term

#### Implementation
**File**: `models/slippage.py` - `LinearRegressionSlippageModel`

**Features**:
- Logarithmic transformation of quantity
- Multiple feature regression
- Model training capability
- Prediction with confidence intervals

### Quantile Regression Slippage Model

#### Mathematical Foundation
The quantile regression model estimates slippage at specific quantiles (e.g., 95th percentile) to capture worst-case scenarios:

```
Slippage_q = α + β × Features + γ × Quantile_Factor
```

#### Implementation
**File**: `models/slippage.py` - `QuantileRegressionSlippageModel`

**Features**:
- Quantile-based estimation (default: 95th percentile)
- Risk-adjusted slippage calculation
- Volatility and spread consideration
- Basis points conversion

**Usage Example**:
```python
model = QuantileRegressionSlippageModel(quantile=0.95)
slippage = model.estimate_slippage(
    quantity=50000,
    price=45000,
    volatility=0.2,
    spread_bps=1.5
)
```

---

## Maker/Taker Proportion Model

### Overview
This model predicts the proportion of a trade that will be executed as maker orders (providing liquidity) versus taker orders (consuming liquidity).

### Mathematical Foundation

#### Base Proportion Calculation
```
Maker Proportion = f(Order_Type, Market_Conditions, Trade_Size)
```

#### Order Type Mapping
- **Market Orders**: 0% maker, 100% taker
- **Limit Orders**: Variable based on market conditions
- **Stop Orders**: Typically high taker proportion

#### Market Condition Factors
```
Adjustment = Volatility_Factor × Spread_Factor × Size_Factor
```

Where:
- `Volatility_Factor`: Higher volatility → Lower maker proportion
- `Spread_Factor`: Wider spreads → Higher maker proportion
- `Size_Factor`: Larger trades → Lower maker proportion

### Implementation Details

**File**: `models/maker_taker.py`

**Key Features**:
- Order type classification
- Dynamic proportion calculation
- Market condition adjustments
- Volatility and spread impact modeling

**Algorithm**:
1. Determine base proportion from order type
2. Apply market condition adjustments
3. Consider trade size impact
4. Ensure proportions sum to 1.0

---

## Fee Calculation Model

### Overview
The fee model calculates trading fees based on exchange fee tiers, maker/taker proportions, and trade characteristics.

### Mathematical Foundation

#### Total Fee Calculation
```
Total Fee = (Maker Proportion × Maker Rate + Taker Proportion × Taker Rate) × Trade Value
```

#### Fee Tier Structure
Different VIP levels have different fee rates:

| Tier | Maker Rate | Taker Rate |
|------|------------|------------|
| VIP0 | 0.10%      | 0.15%      |
| VIP1 | 0.08%      | 0.12%      |
| VIP2 | 0.06%      | 0.10%      |
| VIP3 | 0.04%      | 0.08%      |
| VIP4 | 0.02%      | 0.06%      |
| VIP5 | 0.00%      | 0.04%      |

### Implementation Details

**File**: `models/fee.py`

**Features**:
- Multi-tier fee structure
- Maker/taker rate differentiation
- Effective rate calculation
- Basis points conversion

**Calculation Process**:
1. Determine fee tier rates
2. Calculate weighted average based on maker/taker proportion
3. Apply to trade value
4. Convert to basis points for comparison

---

## VPN Detection Algorithm

### Overview
The VPN detection system uses multiple methods to determine if a VPN connection is active, which is important for accessing certain exchanges.

### Detection Methods

#### Method 1: Network Interface Detection
```python
# Check for VPN-related network adapters
vpn_keywords = ['vpn', 'virtual private', 'tap-windows', 'tunnel',
                'cisco', 'nord', 'express', 'proton', 'wireguard']
```

**Process**:
1. Execute `ipconfig /all` command
2. Parse output for VPN-related interface names
3. Return True if any VPN interfaces found

#### Method 2: Process Detection
```python
# Check for VPN-related processes
vpn_processes = ['vpn', 'openvpn', 'nordvpn', 'expressvpn',
                 'protonvpn', 'wireguard', 'cisco', 'anyconnect']
```

**Process**:
1. Execute `tasklist` command
2. Search for VPN-related process names
3. Return True if any VPN processes found

#### Method 3: Routing Table Analysis
```python
# Check for VPN-specific routing entries
route_indicators = ['0.0.0.0', '128.0.0.0']
```

**Process**:
1. Execute `route print` command
2. Analyze routing table for VPN patterns
3. Look for multiple default gateways or unusual metrics

### Implementation Details

**File**: `utils/connection_manager.py`

**Features**:
- Multi-method detection for reliability
- Manual override capability
- Background monitoring thread
- Error handling and fallback logic

**Algorithm Flow**:
1. Check for manual override
2. Verify internet connectivity
3. Run all detection methods
4. Return True if any method detects VPN
5. Log detection results for debugging

---

## Performance Tracking System

### Overview
The performance tracking system monitors execution times and system performance across different components of the application.

### Metrics Collected

#### Processing Time Metrics
- Trade simulation processing time
- UI update time
- WebSocket message processing time
- Model calculation time

#### Statistical Analysis
```python
Statistics = {
    'mean': Average execution time,
    'std': Standard deviation,
    'min': Minimum execution time,
    'max': Maximum execution time,
    'count': Number of measurements
}
```

### Implementation Details

**File**: `utils/performance.py`

**Key Components**:
- `PerformanceTracker` class for metric collection
- `@timeit` decorator for automatic timing
- Statistical analysis functions
- Memory-efficient circular buffer storage

**Usage Pattern**:
```python
@timeit(performance_tracker, "operation_name")
def some_operation():
    # Operation code here
    pass

# Get statistics
stats = performance_tracker.get_stats("operation_name")
```

---

## WebSocket Data Processing

### Overview
The WebSocket client processes real-time L2 orderbook data and converts it into structured format for analysis.

### Data Structure

#### Orderbook Data Format
```json
{
    "exchange": "OKX",
    "symbol": "BTC-USDT-SWAP",
    "timestamp": "2024-01-01T12:00:00Z",
    "asks": [["50000.0", "1.5"], ["50001.0", "2.0"]],
    "bids": [["49999.0", "1.2"], ["49998.0", "1.8"]]
}
```

#### Processed Metrics
- **Mid Price**: `(Best Ask + Best Bid) / 2`
- **Spread**: `Best Ask - Best Bid`
- **Spread BPS**: `(Spread / Mid Price) × 10000`
- **Liquidity Analysis**: Cumulative quantities and notional values

### Processing Algorithm

#### Data Transformation
1. **Parse JSON Message**: Extract orderbook data
2. **Create DataFrames**: Convert to pandas DataFrames for analysis
3. **Sort Orders**: Asks ascending, bids descending by price
4. **Calculate Cumulative Values**: Running totals for quantity and notional
5. **Compute Metrics**: Mid price, spread, and liquidity measures

#### Liquidity Analysis
```python
# Calculate cumulative quantities
asks_df['cumulative_quantity'] = asks_df['quantity'].cumsum()
bids_df['cumulative_quantity'] = bids_df['quantity'].cumsum()

# Calculate notional values
asks_df['notional'] = asks_df['price'] * asks_df['quantity']
bids_df['notional'] = bids_df['price'] * bids_df['quantity']
```

### Implementation Details

**File**: `websocket_client.py`

**Key Classes**:
- `OrderbookData`: Processes and analyzes orderbook data
- `WebSocketClient`: Manages connections and message handling

**Features**:
- Real-time data processing
- Automatic reconnection handling
- Performance monitoring
- Error handling and logging

**Connection Management**:
1. Check internet and VPN connectivity
2. Establish WebSocket connection
3. Process incoming messages
4. Handle connection failures
5. Implement reconnection logic

---

## Configuration and Parameters

### Model Parameters

#### Default Configuration
```python
# Almgren-Chriss Model
ALMGREN_CHRISS_PARAMS = {
    'sigma': 0.3,    # Annual volatility
    'eta': 0.1,      # Temporary impact factor
    'gamma': 0.1,    # Permanent impact factor
    'T': 1.0,        # Time horizon (days)
    'X': 1.0         # Quantity normalization
}

# Market Parameters
DEFAULT_MARKET_PARAMS = {
    'OKX': {
        'BTC-USDT': {
            'avg_daily_volume': 1000000000,  # $1B daily volume
            'typical_spread_bps': 1.0,
            'volatility': 0.3
        }
    }
}
```

### WebSocket Endpoints
```python
WEBSOCKET_ENDPOINTS = {
    'OKX': {
        'BTC-USDT': 'wss://ws.gomarket-cpp.goquant.io/ws/l2-orderbook/okx/BTC-USDT-SWAP',
        'ETH-USDT': 'wss://ws.gomarket-cpp.goquant.io/ws/l2-orderbook/okx/ETH-USDT-SWAP',
        # Additional endpoints...
    }
}
```

---

## Usage Examples and Best Practices

### Complete Simulation Example
```python
# Initialize simulator
simulator = TradeSimulator()

# Set up trade parameters
params = {
    'exchange': 'OKX',
    'asset': 'BTC-USDT',
    'order_type': 'Market',
    'quantity': 100000,  # $100k trade
    'volatility': 0.25,
    'fee_tier': 'VIP1'
}

# Run simulation
results = simulator.simulate_trade(params)

# Access results
print(f"Total Cost: ${results['net_cost']['value']:.2f}")
print(f"Cost in BPS: {results['net_cost']['bps']:.2f}")
```

### Model Calibration
```python
# Calibrate market impact model with historical data
historical_trades = [
    (50000, 45000, 1000000000),  # (quantity, price, market_volume)
    (75000, 46000, 1200000000),
    # More historical data...
]

historical_impacts = [125.0, 180.0, ...]  # Observed impacts

model.calibrate(historical_trades, historical_impacts)
```

### Performance Monitoring
```python
# Get performance statistics
processing_stats = performance_tracker.get_stats('trade_simulation')
ui_stats = performance_tracker.get_stats('ui_update')

print(f"Average processing time: {processing_stats['mean']*1000:.2f}ms")
print(f"Average UI update time: {ui_stats['mean']*1000:.2f}ms")
```

### VPN Detection Usage
```python
# Initialize connection manager
conn_manager = ConnectionManager()

# Check connection status
status = conn_manager.check_connection()
print(f"Internet: {status['internet_connected']}")
print(f"VPN Active: {status['vpn_active']}")

# Manual override for testing
conn_manager.set_vpn_override(True)  # Force VPN active
```

---

## Algorithm Complexity and Performance

### Time Complexity Analysis

| Algorithm | Time Complexity | Space Complexity | Notes |
|-----------|----------------|------------------|-------|
| Market Impact Calculation | O(1) | O(1) | Simple mathematical operations |
| Slippage Estimation | O(1) | O(1) | Linear/quantile regression |
| Maker/Taker Prediction | O(1) | O(1) | Rule-based classification |
| Fee Calculation | O(1) | O(1) | Lookup and multiplication |
| VPN Detection | O(n) | O(1) | n = number of processes/interfaces |
| Orderbook Processing | O(n log n) | O(n) | n = number of price levels |

### Performance Benchmarks

Typical execution times on modern hardware:
- Market Impact Calculation: < 0.1ms
- Slippage Estimation: < 0.1ms
- Complete Trade Simulation: < 1ms
- UI Update: < 5ms
- WebSocket Message Processing: < 0.5ms

### Optimization Strategies

1. **Caching**: Cache frequently accessed market parameters
2. **Vectorization**: Use NumPy for batch calculations
3. **Lazy Loading**: Load models only when needed
4. **Connection Pooling**: Reuse WebSocket connections
5. **Memory Management**: Use circular buffers for performance data

---

## Error Handling and Edge Cases

### Market Impact Model
- **Zero Volume**: Handle division by zero with default impact values
- **Negative Prices**: Validate input parameters
- **Extreme Volatility**: Cap volatility at reasonable bounds

### Slippage Models
- **Missing Data**: Use fallback estimates when market data unavailable
- **Model Convergence**: Handle regression failures gracefully
- **Outlier Detection**: Filter extreme slippage values

### VPN Detection
- **Command Failures**: Graceful degradation when system commands fail
- **Permission Issues**: Handle cases where process listing is restricted
- **False Positives**: Minimize incorrect VPN detection

### WebSocket Processing
- **Connection Drops**: Automatic reconnection with exponential backoff
- **Malformed Data**: Robust JSON parsing with error recovery
- **Rate Limiting**: Handle exchange rate limits appropriately

---

## Testing and Validation

### Unit Testing Strategy
```python
# Example test for market impact model
def test_market_impact_calculation():
    model = AlmgrenChrissModel()
    result = model.calculate_market_impact(
        quantity=100000,
        price=50000,
        market_volume=1000000000,
        volatility=0.3
    )

    assert result['total_impact'] > 0
    assert result['temporary_impact'] >= 0
    assert result['permanent_impact'] >= 0
    assert abs(result['participation_rate'] - 0.0001) < 1e-6
```

### Integration Testing
- End-to-end simulation testing
- WebSocket connection testing
- UI interaction testing
- Performance regression testing

### Validation Methods
- **Backtesting**: Compare model predictions with historical data
- **Cross-Validation**: Use k-fold validation for model parameters
- **Stress Testing**: Test with extreme market conditions
- **A/B Testing**: Compare different model configurations

---

## References and Further Reading

### Academic Papers
1. **Almgren, R., & Chriss, N. (2001)**. "Optimal execution of portfolio transactions." *Journal of Risk*, 3, 5-40.

2. **Bertsimas, D., & Lo, A. W. (1998)**. "Optimal control of execution costs." *Journal of Financial Markets*, 1(1), 1-50.

3. **Hasbrouck, J. (2009)**. "Trading costs and returns for US equities: Estimating effective costs from daily data." *The Journal of Finance*, 64(3), 1445-1477.

### Books
1. **O'Hara, M. (1995)**. *Market Microstructure Theory*. Blackwell Publishers.

2. **Harris, L. (2003)**. *Trading and Exchanges: Market Microstructure for Practitioners*. Oxford University Press.

3. **Chan, E. (2009)**. *Quantitative Trading: How to Build Your Own Algorithmic Trading Business*. Wiley.

### Online Resources
1. **QuantLib**: Open-source library for quantitative finance
2. **Zipline**: Algorithmic trading library
3. **CCXT**: Cryptocurrency exchange trading library

---

## Mathematical Notation Reference

| Symbol | Description | Units | Typical Range |
|--------|-------------|-------|---------------|
| η (eta) | Temporary impact factor | Dimensionless | 0.01 - 0.5 |
| γ (gamma) | Permanent impact factor | Dimensionless | 0.01 - 0.3 |
| σ (sigma) | Volatility | Annualized % | 0.1 - 2.0 |
| T | Time horizon | Days | 0.1 - 30 |
| X | Quantity to execute | Shares/USD | Variable |
| V | Market volume | Shares/USD | Variable |
| P | Asset price | USD | Variable |
| BPS | Basis points | 1/10000 | 0 - 1000+ |
| λ | Arrival rate | Trades/second | 0.1 - 100 |
| ρ | Correlation coefficient | Dimensionless | -1 to 1 |

---

## Appendix: Code Examples

### Custom Model Implementation
```python
class CustomSlippageModel:
    """Example of implementing a custom slippage model."""

    def __init__(self, base_slippage=0.001):
        self.base_slippage = base_slippage

    def estimate_slippage(self, quantity, price, volatility, spread_bps):
        # Custom logic here
        size_factor = np.log(quantity / 10000) * 0.0001
        vol_factor = volatility * 0.002
        spread_factor = spread_bps * 0.00001

        slippage = self.base_slippage + size_factor + vol_factor + spread_factor

        return {
            'slippage': slippage * quantity,
            'slippage_bps': (slippage / price) * 10000
        }
```

### Performance Optimization Example
```python
import numpy as np
from numba import jit

@jit(nopython=True)
def fast_market_impact(quantities, prices, volumes, eta, gamma, sigma, T):
    """Vectorized market impact calculation using Numba."""
    participation_rates = quantities / volumes
    temp_impacts = eta * sigma * np.sqrt(T) * participation_rates * prices
    perm_impacts = gamma * participation_rates * prices
    return temp_impacts + perm_impacts
```

---

*This documentation is maintained alongside the codebase and should be updated when models or algorithms are modified. Last updated: 2024*
