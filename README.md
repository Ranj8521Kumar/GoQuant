# Trade Simulator

A sophisticated, real-time trade simulator that leverages live market data to estimate transaction costs and market impact for cryptocurrency trading. Built with advanced quantitative models and a modern PyQt5 interface.

![Trade Simulator UI](ui_screenshot.png)

## 🚀 Features

### Real-Time Market Analysis
- **Live WebSocket Data**: Connects to OKX exchange for real-time L2 orderbook data
- **Multi-Asset Support**: BTC-USDT, ETH-USDT, SOL-USDT, XRP-USDT, ADA-USDT
- **Advanced VPN Detection**: Intelligent detection system for secure exchange access
- **Automatic Reconnection**: Robust connection management with retry logic

### Quantitative Models
- **Almgren-Chriss Market Impact Model**: Industry-standard model for estimating temporary and permanent market impact
- **Dual Slippage Models**: Linear and Quantile Regression for comprehensive slippage estimation
- **Maker/Taker Prediction**: Dynamic proportion calculation based on order type and market conditions
- **Multi-Tier Fee Structure**: Accurate fee calculation across different VIP levels

### Performance & Monitoring
- **Real-Time Performance Tracking**: Latency monitoring for processing and UI updates
- **Comprehensive Logging**: Detailed logging system for debugging and analysis
- **Memory Efficient**: Optimized data structures and circular buffers
- **Sub-millisecond Processing**: High-performance calculations for real-time trading

### User Interface
- **Intuitive Design**: Clean, professional PyQt5 interface
- **Real-Time Updates**: Live display of simulation results
- **Parameter Flexibility**: Configurable trading parameters and market conditions
- **Status Monitoring**: Connection status tracking in the status bar

## 📋 Requirements

### System Requirements
- **Python**: 3.8 or higher
- **Operating System**: Windows 10/11, macOS 10.14+, or Linux
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Network**: Stable internet connection (VPN required for OKX access)

### Python Dependencies
```
PyQt5>=5.15.0          # Modern GUI framework
websockets>=10.0       # WebSocket client for real-time data
pandas>=1.3.0          # Data manipulation and analysis
numpy>=1.21.0          # Numerical computing
scikit-learn>=1.0.0    # Machine learning models
matplotlib>=3.5.0      # Plotting and visualization
asyncio                # Asynchronous programming
threading              # Multi-threading support
```

## 🛠️ Installation

### Quick Start
```bash
# Clone the repository
git clone <repository-url>
cd GoQuant

# Create and activate virtual environment
python -m venv venv

# Windows
.\venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

### Development Setup
```bash
# Install additional development dependencies
pip install pytest pytest-cov black flake8

# Run tests
pytest tests/

# Format code
black .

# Check code quality
flake8 .
```

## 🎯 Usage

### Getting Started
1. **Launch the Application**
   ```bash
   python main.py
   ```

2. **Configure Trade Parameters**
   - **Exchange**: Select OKX (currently supported)
   - **Spot Asset**: Choose from BTC-USDT, ETH-USDT, SOL-USDT, XRP-USDT, ADA-USDT
   - **Order Type**: Market, Limit, or Stop orders
   - **Quantity**: Trade size in USD equivalent
   - **Volatility**: Expected asset volatility (0-100%)
   - **Fee Tier**: Your exchange VIP level (VIP0-VIP5)

3. **Run Simulation**
   - Click "Simulate" to execute the trade simulation
   - View real-time results in the output panel
   - Monitor connection status in the status bar

### Key Metrics Displayed
- **Expected Slippage**: Price impact due to market conditions
- **Expected Fees**: Trading fees based on maker/taker proportion
- **Market Impact**: Temporary and permanent price impact (Almgren-Chriss)
- **Net Cost**: Total transaction cost in USD and basis points
- **Maker/Taker Proportion**: Predicted order execution breakdown
- **Internal Latency**: Processing and UI update performance

## 🏗️ Architecture

### Project Structure
```
GoQuant/
├── main.py                     # Application entry point
├── websocket_client.py         # Real-time data connection
├── config.py                   # Configuration settings
├── MODELS_AND_ALGORITHMS.md    # Comprehensive model documentation
├── models/                     # Quantitative models
│   ├── market_impact.py        # Almgren-Chriss implementation
│   ├── slippage.py            # Linear & Quantile regression
│   ├── maker_taker.py         # Order type prediction
│   └── fee.py                 # Multi-tier fee calculation
├── ui/                        # User interface components
│   ├── app.py                 # Main application window
│   ├── input_panel.py         # Parameter input interface
│   └── output_panel.py        # Results display interface
└── utils/                     # Utility modules
    ├── connection_manager.py   # Network & VPN management
    ├── logger.py              # Logging system
    └── performance.py         # Performance tracking
```

### Component Interaction
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   UI Layer      │    │   Business Logic │    │   Data Layer    │
│                 │    │                  │    │                 │
│ ┌─────────────┐ │    │ ┌──────────────┐ │    │ ┌─────────────┐ │
│ │ Input Panel │ │───▶│ │ Trade        │ │    │ │ WebSocket   │ │
│ └─────────────┘ │    │ │ Simulator    │ │◀───│ │ Client      │ │
│ ┌─────────────┐ │    │ └──────────────┘ │    │ └─────────────┘ │
│ │Output Panel │ │◀───│ ┌──────────────┐ │    │ ┌─────────────┐ │
│ └─────────────┘ │    │ │ Models       │ │    │ │ Connection  │ │
│                 │    │ │ - Market     │ │    │ │ Manager     │ │
└─────────────────┘    │ │ - Slippage   │ │    │ └─────────────┘ │
                       │ │ - Fees       │ │    │                 │
                       │ └──────────────┘ │    └─────────────────┘
                       └──────────────────┘
```

## 🧮 Quantitative Models

### Almgren-Chriss Market Impact Model
**Industry-standard model for institutional trading**
- **Temporary Impact**: `η × σ × √T × (X/V) × P`
- **Permanent Impact**: `γ × (X/V) × P`
- **Configurable Parameters**: η (0.1), γ (0.1), σ (volatility), T (time horizon)
- **Applications**: Large order execution, portfolio rebalancing, risk management

### Slippage Estimation Models
**Dual-model approach for comprehensive analysis**
1. **Linear Regression Model**
   - Multi-factor regression with quantity, volatility, and spread
   - Logarithmic transformation for non-linear relationships
   - Confidence interval estimation

2. **Quantile Regression Model**
   - 95th percentile estimation for worst-case scenarios
   - Risk-adjusted slippage calculation
   - Robust to outliers and extreme market conditions

### Maker/Taker Proportion Model
**Dynamic order execution prediction**
- **Order Type Classification**: Market (100% taker), Limit (variable), Stop (high taker)
- **Market Condition Adjustments**: Volatility, spread, and trade size factors
- **Real-time Adaptation**: Updates based on current market conditions

### Fee Calculation Model
**Multi-tier exchange fee structure**
- **VIP Levels**: VIP0 (0.10%/0.15%) to VIP5 (0.00%/0.04%)
- **Weighted Calculation**: Based on predicted maker/taker proportion
- **Basis Points Conversion**: For easy comparison and analysis

## 🔧 Advanced Features

### VPN Detection System
**Multi-method detection for secure exchange access**
- **Network Interface Detection**: Scans for VPN adapters
- **Process Detection**: Identifies VPN software
- **Routing Analysis**: Examines network routing tables
- **Manual Override**: For testing and troubleshooting

### Performance Monitoring
**Real-time system performance tracking**
- **Processing Latency**: Sub-millisecond model calculations
- **UI Responsiveness**: Real-time update performance
- **Memory Management**: Efficient circular buffers
- **Statistical Analysis**: Mean, std dev, min/max tracking

### Connection Management
**Robust network handling**
- **Automatic Reconnection**: Exponential backoff strategy
- **Health Monitoring**: Continuous connection status checks
- **Error Recovery**: Graceful handling of network issues
- **Status Reporting**: Real-time connection status updates

## 📊 Performance Benchmarks

| Component | Typical Latency | Optimization |
|-----------|----------------|--------------|
| Market Impact Calculation | < 0.1ms | Vectorized operations |
| Slippage Estimation | < 0.1ms | Pre-computed coefficients |
| Complete Trade Simulation | < 1ms | Efficient data structures |
| UI Update | < 5ms | Optimized rendering |
| WebSocket Processing | < 0.5ms | Asynchronous handling |

## 📚 Documentation

### Comprehensive Model Documentation
- **[MODELS_AND_ALGORITHMS.md](MODELS_AND_ALGORITHMS.md)**: Complete mathematical foundations and implementation details
- **Code Comments**: Detailed inline documentation
- **Type Hints**: Full type annotation for better code clarity
- **Docstrings**: Comprehensive function and class documentation

### Key Resources
- **Academic References**: Almgren-Chriss original papers
- **Implementation Examples**: Practical usage patterns
- **Performance Guidelines**: Optimization best practices
- **Testing Strategies**: Unit and integration testing approaches

## 🚨 Important Notes

### VPN Requirements
- **OKX Access**: VPN required for connecting to OKX exchange
- **Automatic Detection**: Application detects VPN status automatically
- **Status Display**: VPN status shown in connection monitoring
- **No Account Required**: Public market data access only

### Network Considerations
- **Stable Connection**: Reliable internet required for real-time data
- **Firewall Settings**: Ensure WebSocket connections are allowed
- **Rate Limiting**: Application respects exchange rate limits
- **Data Usage**: Minimal bandwidth for L2 orderbook data

## 🤝 Contributing

### Development Guidelines
```bash
# Fork the repository
git fork <repository-url>

# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and test
python -m pytest tests/

# Format code
black . && flake8 .

# Submit pull request
```

### Code Standards
- **PEP 8**: Python style guide compliance
- **Type Hints**: Full type annotation required
- **Documentation**: Comprehensive docstrings
- **Testing**: Unit tests for all new features

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Almgren & Chriss**: For the foundational market impact model
- **OKX Exchange**: For providing public market data access
- **PyQt5 Community**: For the excellent GUI framework
- **Open Source Contributors**: For the various libraries used

---

*Built with ❤️ for quantitative trading and market microstructure analysis*
