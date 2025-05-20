"""
Main entry point for the trade simulator application.
"""
import asyncio
import threading
import time
import json
from typing import Dict, Any

import pandas as pd
import numpy as np

from websocket_client import WebSocketClient, OrderbookData
from models.market_impact import AlmgrenChrissModel
from models.slippage import LinearRegressionSlippageModel, QuantileRegressionSlippageModel
from models.maker_taker import MakerTakerModel
from models.fee import FeeModel
from ui.app import run_app
from utils.logger import setup_logger
from utils.performance import performance_tracker
import config

logger = setup_logger("main")

class TradeSimulator:
    """Main class for the trade simulator."""
    
    def __init__(self):
        """Initialize the trade simulator."""
        self.websocket_clients = {}
        self.orderbook_data = {}
        self.market_impact_model = AlmgrenChrissModel(**config.ALMGREN_CHRISS_PARAMS)
        self.slippage_model = QuantileRegressionSlippageModel(quantile=0.95)
        self.maker_taker_model = MakerTakerModel()
        self.fee_model = FeeModel()
        
        # Initialize with some default values
        self.current_exchange = 'OKX'
        self.current_asset = 'BTC-USDT'
        
        # Start the WebSocket client
        self.start_websocket()
    
    def start_websocket(self):
        """Start the WebSocket client for the current exchange and asset."""
        key = f"{self.current_exchange}_{self.current_asset}"
        
        if key in self.websocket_clients:
            # Client already exists
            return
        
        # Get the WebSocket endpoint
        endpoint = config.WEBSOCKET_ENDPOINTS.get(self.current_exchange, {}).get(self.current_asset)
        
        if not endpoint:
            logger.error(f"No WebSocket endpoint found for {self.current_exchange} {self.current_asset}")
            return
        
        # Create and start the WebSocket client
        client = WebSocketClient(endpoint, self.on_orderbook_update)
        self.websocket_clients[key] = client
        
        # Start the client in a separate thread
        thread = threading.Thread(target=self.run_websocket_client, args=(client,))
        thread.daemon = True
        thread.start()
    
    def run_websocket_client(self, client):
        """
        Run the WebSocket client in an asyncio event loop.
        
        Args:
            client: WebSocketClient instance
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(client.connect())
    
    def on_orderbook_update(self, orderbook: OrderbookData):
        """
        Handle orderbook updates from the WebSocket client.
        
        Args:
            orderbook: OrderbookData instance
        """
        key = f"{orderbook.exchange}_{orderbook.symbol}"
        self.orderbook_data[key] = orderbook
        
        # Log some basic information
        logger.debug(f"Received orderbook update for {key}: "
                    f"mid_price={orderbook.mid_price:.2f}, "
                    f"spread={orderbook.spread:.2f}, "
                    f"spread_bps={orderbook.spread_bps:.2f}")
    
    def simulate_trade(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate a trade with the given parameters.
        
        Args:
            params: Dictionary with trade parameters
            
        Returns:
            Dictionary with simulation results
        """
        # Extract parameters
        exchange = params.get('exchange', 'OKX')
        asset = params.get('asset', 'BTC-USDT')
        order_type = params.get('order_type', 'Market')
        quantity = params.get('quantity', 100)
        volatility = params.get('volatility', 0.3)
        fee_tier = params.get('fee_tier', 'VIP0')
        
        # Get current orderbook data
        key = f"{exchange}_{asset}"
        orderbook = self.orderbook_data.get(key)
        
        if not orderbook:
            logger.warning(f"No orderbook data available for {key}")
            # Use default values
            price = 50000  # Default price for BTC-USDT
            spread_bps = 1.0
        else:
            price = orderbook.mid_price
            spread_bps = orderbook.spread_bps
        
        # Get market parameters
        market_params = config.DEFAULT_MARKET_PARAMS.get(exchange, {}).get(asset, {})
        market_volume = market_params.get('avg_daily_volume', 1000000000)
        
        # Calculate maker/taker proportion
        maker_taker = self.maker_taker_model.predict_maker_taker(
            quantity=quantity,
            volatility=volatility,
            spread_bps=spread_bps,
            order_type=order_type
        )
        
        # Calculate fees
        fees = self.fee_model.calculate_fee(
            quantity=quantity,
            price=price,
            fee_tier=fee_tier,
            maker_proportion=maker_taker['maker_proportion']
        )
        
        # Calculate market impact
        market_impact = self.market_impact_model.calculate_market_impact(
            quantity=quantity,
            price=price,
            market_volume=market_volume,
            volatility=volatility
        )
        
        # Calculate slippage
        slippage = self.slippage_model.estimate_slippage(
            quantity=quantity,
            price=price,
            volatility=volatility,
            spread_bps=spread_bps
        )
        
        # Calculate net cost
        net_cost_value = slippage['slippage'] + fees['total_fee'] + market_impact['total_impact']
        net_cost_bps = (net_cost_value / (quantity * price)) * 10000 if price > 0 else 0
        net_cost_percent = (net_cost_value / (quantity * price)) * 100 if price > 0 else 0
        
        # Measure latency
        latency = {
            'processing_time': performance_tracker.get_stats('trade_simulation').get('mean', 0) * 1000,  # Convert to ms
            'ui_time': performance_tracker.get_stats('ui_update').get('mean', 0) * 1000,  # Convert to ms
            'total_time': (performance_tracker.get_stats('trade_simulation').get('mean', 0) + 
                          performance_tracker.get_stats('ui_update').get('mean', 0)) * 1000  # Convert to ms
        }
        
        # Return results
        return {
            'slippage': slippage,
            'fees': fees,
            'market_impact': market_impact,
            'maker_taker': maker_taker,
            'net_cost': {
                'value': net_cost_value,
                'bps': net_cost_bps,
                'percent': net_cost_percent
            },
            'latency': latency,
            'price': price,
            'spread_bps': spread_bps
        }
    
    def stop(self):
        """Stop all WebSocket clients."""
        for client in self.websocket_clients.values():
            client.stop()


def main():
    """Main entry point."""
    logger.info("Starting trade simulator")
    
    # Create the trade simulator
    simulator = TradeSimulator()
    
    try:
        # Run the UI
        run_app()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received, shutting down")
    finally:
        # Stop the simulator
        simulator.stop()
        logger.info("Trade simulator stopped")


if __name__ == "__main__":
    main()
