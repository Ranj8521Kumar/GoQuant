"""
Connection manager for handling WebSocket connections and VPN detection.
"""
import socket
import requests
import time
import threading
from typing import Dict, Any, Optional, Callable

from utils.logger import setup_logger

logger = setup_logger("connection_manager")

class ConnectionManager:
    """Manager for handling WebSocket connections and VPN detection."""
    
    def __init__(self, 
                 connection_check_interval: int = 30,
                 max_reconnect_attempts: int = 5,
                 reconnect_delay: int = 5):
        """
        Initialize the connection manager.
        
        Args:
            connection_check_interval: Interval in seconds to check connection status
            max_reconnect_attempts: Maximum number of reconnection attempts
            reconnect_delay: Delay in seconds between reconnection attempts
        """
        self.connection_check_interval = connection_check_interval
        self.max_reconnect_attempts = max_reconnect_attempts
        self.reconnect_delay = reconnect_delay
        self.is_vpn_active = False
        self.is_internet_connected = False
        self.connection_status = "Disconnected"
        self.reconnect_attempts = 0
        self.last_check_time = 0
        self.status_callback = None
        self.reconnect_callback = None
        
        # Start connection monitoring thread
        self.monitoring_thread = threading.Thread(target=self._monitor_connection)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
    
    def set_callbacks(self, 
                     status_callback: Callable[[str], None],
                     reconnect_callback: Callable[[], None]):
        """
        Set callbacks for status updates and reconnection.
        
        Args:
            status_callback: Function to call with status updates
            reconnect_callback: Function to call for reconnection
        """
        self.status_callback = status_callback
        self.reconnect_callback = reconnect_callback
    
    def _monitor_connection(self):
        """Monitor connection status in a background thread."""
        while True:
            current_time = time.time()
            
            # Check connection status at regular intervals
            if current_time - self.last_check_time > self.connection_check_interval:
                self.check_connection()
                self.last_check_time = current_time
            
            # Sleep to avoid high CPU usage
            time.sleep(1)
    
    def check_connection(self) -> Dict[str, Any]:
        """
        Check internet and VPN connection status.
        
        Returns:
            Dictionary with connection status information
        """
        # Check internet connection
        self.is_internet_connected = self._check_internet_connection()
        
        # Check VPN connection
        self.is_vpn_active = self._check_vpn_connection()
        
        # Update connection status
        if not self.is_internet_connected:
            self.connection_status = "No Internet Connection"
        elif not self.is_vpn_active:
            self.connection_status = "VPN Not Detected"
        else:
            self.connection_status = "VPN Connected"
        
        # Call status callback if available
        if self.status_callback:
            self.status_callback(self.connection_status)
        
        return {
            'internet_connected': self.is_internet_connected,
            'vpn_active': self.is_vpn_active,
            'status': self.connection_status
        }
    
    def _check_internet_connection(self) -> bool:
        """
        Check if there is an active internet connection.
        
        Returns:
            True if internet is connected, False otherwise
        """
        try:
            # Try to connect to a reliable host
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except OSError:
            return False
    
    def _check_vpn_connection(self) -> bool:
        """
        Check if a VPN connection is active.
        
        Returns:
            True if VPN is detected, False otherwise
        """
        try:
            # Try to get public IP and check if it's from a known VPN provider
            response = requests.get("https://ipinfo.io/json", timeout=5)
            data = response.json()
            
            # Check if the IP is from a known VPN provider
            # This is a simplified check and may not be accurate for all VPNs
            org = data.get("org", "").lower()
            vpn_keywords = ["vpn", "proxy", "hosting", "cloud", "data center"]
            
            return any(keyword in org for keyword in vpn_keywords)
        except Exception as e:
            logger.error(f"Error checking VPN connection: {e}")
            return False
    
    def handle_connection_failure(self, error: Optional[Exception] = None) -> bool:
        """
        Handle connection failure and attempt reconnection.
        
        Args:
            error: Exception that caused the connection failure
            
        Returns:
            True if reconnection should be attempted, False otherwise
        """
        if error:
            logger.error(f"Connection failure: {error}")
        
        self.reconnect_attempts += 1
        
        if self.reconnect_attempts > self.max_reconnect_attempts:
            logger.warning(f"Maximum reconnection attempts ({self.max_reconnect_attempts}) reached")
            self.connection_status = "Reconnection Failed"
            
            if self.status_callback:
                self.status_callback(self.connection_status)
            
            return False
        
        logger.info(f"Reconnection attempt {self.reconnect_attempts}/{self.max_reconnect_attempts}")
        self.connection_status = f"Reconnecting ({self.reconnect_attempts}/{self.max_reconnect_attempts})"
        
        if self.status_callback:
            self.status_callback(self.connection_status)
        
        # Wait before reconnecting
        time.sleep(self.reconnect_delay)
        
        return True
    
    def reset_reconnect_attempts(self):
        """Reset the reconnection attempt counter."""
        self.reconnect_attempts = 0
    
    def manual_reconnect(self):
        """Manually trigger a reconnection."""
        self.reset_reconnect_attempts()
        
        if self.reconnect_callback:
            self.reconnect_callback()
        
        return True
