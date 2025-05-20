# Trade Simulator

A high-performance trade simulator leveraging real-time market data to estimate transaction costs and market impact.

## Overview

This application connects to WebSocket endpoints that stream full L2 orderbook data for cryptocurrency exchanges. It processes this data in real-time to provide estimates of:

- Expected Slippage
- Expected Fees
- Expected Market Impact (using Almgren-Chriss model)
- Net Cost
- Maker/Taker proportion
- Internal Latency

## Requirements

- Python 3.8+
- PyQt5
- websockets
- pandas
- numpy
- scikit-learn
- matplotlib

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd trade-simulator
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows:
     ```
     .\venv\Scripts\activate
     ```
   - Linux/Mac:
     ```
     source venv/bin/activate
     ```

4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```
   python main.py
   ```

2. Use the input panel to set parameters:
   - Exchange (OKX)
   - Spot Asset (BTC-USDT, ETH-USDT, etc.)
   - Order Type (Market)
   - Quantity (USD equivalent)
   - Volatility
   - Fee Tier

3. Click "Simulate" to run the simulation and view the results in the output panel.

## Architecture

The application is structured as follows:

- `main.py`: Entry point for the application
- `websocket_client.py`: WebSocket connection and data handling
- `models/`: Directory for market impact and regression models
  - `market_impact.py`: Almgren-Chriss model implementation
  - `slippage.py`: Slippage estimation models
  - `maker_taker.py`: Maker/Taker proportion prediction
  - `fee.py`: Fee calculation model
- `ui/`: UI components
  - `app.py`: Main UI application
  - `input_panel.py`: Left panel for input parameters
  - `output_panel.py`: Right panel for output parameters
- `utils/`: Utility functions
  - `logger.py`: Logging functionality
  - `performance.py`: Performance measurement tools
- `config.py`: Configuration settings

## Models

### Almgren-Chriss Market Impact Model

The Almgren-Chriss model divides market impact into two components:
1. Temporary impact: Immediate price change due to the trade
2. Permanent impact: Long-term price change that remains after the trade

### Slippage Estimation

Two models are implemented for slippage estimation:
1. Linear Regression: Estimates the expected slippage
2. Quantile Regression: Estimates slippage at a specific quantile (e.g., 95th percentile)

### Maker/Taker Proportion

A logistic regression model is used to predict the proportion of maker vs taker orders.

## Performance Optimization

The application includes several performance optimizations:

- Efficient data structures for orderbook processing
- Asynchronous WebSocket communication
- Performance tracking for latency measurement
- UI updates optimized for responsiveness

## Notes

- You will need to use a VPN to access OKX for this assignment.
- Since the market data is public, there is no requirement to create an account.

## License

[MIT License](LICENSE)
