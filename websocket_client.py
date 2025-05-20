"""
WebSocket client for connecting to L2 orderbook data stream.
"""
import json
import asyncio
import logging
import time
from datetime import datetime
from typing import Dict, List, Tuple, Callable, Optional

import websockets
import pandas as pd
import numpy as np

from utils.logger import setup_logger

logger = setup_logger("websocket_client")

class OrderbookData:
    """Class to store and process orderbook data."""
    
    def __init__(self, exchange: str, symbol: str, timestamp: str, 
                 asks: List[List[str]], bids: List[List[str]]):
        """
        Initialize OrderbookData with raw orderbook data.
        
        Args:
            exchange: Exchange name
            symbol: Trading pair symbol
            timestamp: ISO format timestamp
            asks: List of [price, quantity] for ask orders
            bids: List of [price, quantity] for bid orders
        """
        self.exchange = exchange
        self.symbol = symbol
        self.timestamp = timestamp
        self.datetime = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        
        # Convert to DataFrames for easier processing
        self.asks_df = pd.DataFrame(asks, columns=['price', 'quantity']).astype(float)
        self.bids_df = pd.DataFrame(bids, columns=['price', 'quantity']).astype(float)
        
        # Sort asks by price (ascending) and bids by price (descending)
        self.asks_df = self.asks_df.sort_values('price', ascending=True)
        self.bids_df = self.bids_df.sort_values('price', ascending=False)
        
        # Calculate cumulative quantities
        self.asks_df['cumulative_quantity'] = self.asks_df['quantity'].cumsum()
        self.bids_df['cumulative_quantity'] = self.bids_df['quantity'].cumsum()
        
        # Calculate cumulative notional values (price * quantity)
        self.asks_df['notional'] = self.asks_df['price'] * self.asks_df['quantity']
        self.bids_df['notional'] = self.bids_df['price'] * self.bids_df['quantity']
        self.asks_df['cumulative_notional'] = self.asks_df['notional'].cumsum()
        self.bids_df['cumulative_notional'] = self.bids_df['notional'].cumsum()
    
    @property
    def mid_price(self) -> float:
        """Calculate the mid price between best bid and best ask."""
        best_ask = self.asks_df.iloc[0]['price'] if not self.asks_df.empty else 0
        best_bid = self.bids_df.iloc[0]['price'] if not self.bids_df.empty else 0
        return (best_ask + best_bid) / 2 if best_ask and best_bid else 0
    
    @property
    def spread(self) -> float:
        """Calculate the spread between best bid and best ask."""
        best_ask = self.asks_df.iloc[0]['price'] if not self.asks_df.empty else 0
        best_bid = self.bids_df.iloc[0]['price'] if not self.bids_df.empty else 0
        return best_ask - best_bid if best_ask and best_bid else 0
    
    @property
    def spread_bps(self) -> float:
        """Calculate the spread in basis points."""
        mid = self.mid_price
        return (self.spread / mid) * 10000 if mid else 0
    
    def get_liquidity_at_level(self, level: int = 5) -> Tuple[float, float]:
        """
        Get the liquidity available at a specific level.
        
        Args:
            level: Number of price levels to consider
            
        Returns:
            Tuple of (ask_liquidity, bid_liquidity) in notional value
        """
        ask_liquidity = self.asks_df.iloc[:level]['notional'].sum() if len(self.asks_df) >= level else self.asks_df['notional'].sum()
        bid_liquidity = self.bids_df.iloc[:level]['notional'].sum() if len(self.bids_df) >= level else self.bids_df['notional'].sum()
        return ask_liquidity, bid_liquidity
    
    def get_price_for_quantity(self, quantity: float, side: str) -> float:
        """
        Get the average price for a given quantity.
        
        Args:
            quantity: Quantity to buy/sell
            side: 'buy' or 'sell'
            
        Returns:
            Average price for the given quantity
        """
        if side.lower() == 'buy':
            # For buy orders, we take from the asks
            df = self.asks_df
        else:
            # For sell orders, we take from the bids
            df = self.bids_df
        
        # Find the index where cumulative quantity exceeds our target quantity
        idx = df['cumulative_quantity'].searchsorted(quantity)
        
        if idx >= len(df):
            # Not enough liquidity
            return None
        
        # Calculate the average price
        if idx == 0:
            return df.iloc[0]['price']
        
        # Calculate the weighted average price
        total_notional = df.iloc[:idx]['notional'].sum()
        remaining_quantity = quantity - df.iloc[:idx-1]['cumulative_quantity'].iloc[-1]
        total_notional += remaining_quantity * df.iloc[idx]['price']
        
        return total_notional / quantity


class WebSocketClient:
    """Client for connecting to WebSocket endpoints and processing orderbook data."""
    
    def __init__(self, url: str, callback: Callable[[OrderbookData], None]):
        """
        Initialize WebSocket client.
        
        Args:
            url: WebSocket endpoint URL
            callback: Function to call with processed orderbook data
        """
        self.url = url
        self.callback = callback
        self.running = False
        self.last_message_time = 0
        self.processing_times = []
        self.connection = None
    
    async def connect(self):
        """Connect to the WebSocket endpoint and start processing messages."""
        logger.info(f"Connecting to {self.url}")
        self.running = True
        
        while self.running:
            try:
                async with websockets.connect(self.url) as websocket:
                    self.connection = websocket
                    logger.info(f"Connected to {self.url}")
                    
                    while self.running:
                        try:
                            message = await websocket.recv()
                            start_time = time.time()
                            self.last_message_time = start_time
                            
                            # Process the message
                            await self._process_message(message)
                            
                            # Calculate processing time
                            processing_time = time.time() - start_time
                            self.processing_times.append(processing_time)
                            
                            # Keep only the last 1000 processing times
                            if len(self.processing_times) > 1000:
                                self.processing_times.pop(0)
                                
                        except websockets.exceptions.ConnectionClosed:
                            logger.warning("Connection closed, reconnecting...")
                            break
                            
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                
            # Wait before reconnecting
            if self.running:
                logger.info("Reconnecting in 5 seconds...")
                await asyncio.sleep(5)
    
    async def _process_message(self, message: str):
        """
        Process a WebSocket message.
        
        Args:
            message: JSON message from WebSocket
        """
        try:
            data = json.loads(message)
            
            # Create OrderbookData object
            orderbook = OrderbookData(
                exchange=data.get('exchange'),
                symbol=data.get('symbol'),
                timestamp=data.get('timestamp'),
                asks=data.get('asks', []),
                bids=data.get('bids', [])
            )
            
            # Call the callback with the processed data
            self.callback(orderbook)
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    def stop(self):
        """Stop the WebSocket client."""
        logger.info("Stopping WebSocket client")
        self.running = False
        
    @property
    def avg_processing_time(self) -> float:
        """Get the average processing time in milliseconds."""
        if not self.processing_times:
            return 0
        return np.mean(self.processing_times) * 1000  # Convert to ms
    
    @property
    def max_processing_time(self) -> float:
        """Get the maximum processing time in milliseconds."""
        if not self.processing_times:
            return 0
        return np.max(self.processing_times) * 1000  # Convert to ms
    
    @property
    def is_connected(self) -> bool:
        """Check if the client is connected."""
        return self.connection is not None and self.connection.open
