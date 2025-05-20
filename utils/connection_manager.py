"""
Connection manager for handling WebSocket connections and VPN detection.

This module provides functionality to:
1. Monitor internet connectivity
2. Detect VPN connections (required for accessing certain exchanges)
3. Track connection status
4. Handle reconnection attempts with configurable retry logic
5. Provide callbacks for status updates

The ConnectionManager runs a background thread that periodically checks connection status
and can trigger reconnection attempts when needed.
"""
import socket
import time
import threading
from typing import Dict, Any, Optional, Callable

from utils.logger import setup_logger

logger = setup_logger("connection_manager")

class ConnectionManager:
    """
    Manager for handling WebSocket connections and VPN detection.

    This class provides methods to:
    - Monitor internet and VPN connectivity
    - Track connection status
    - Handle reconnection attempts
    - Provide callbacks for status updates
    - Allow manual override of VPN status

    The ConnectionManager runs in a background thread to periodically check connection
    status without blocking the main application thread.
    """

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

        # Manual override for VPN status (for testing or when automatic detection fails)
        self.vpn_override = None  # None = use automatic detection, True/False = override

        # Start connection monitoring thread
        self.monitoring_thread = threading.Thread(target=self._monitor_connection)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()

    def set_vpn_override(self, override: Optional[bool]):
        """
        Set a manual override for VPN status.

        Args:
            override: True to force VPN active, False to force VPN inactive, None to use automatic detection
        """
        self.vpn_override = override
        logger.info(f"VPN status override set to: {override}")

        # Trigger an immediate connection check
        self.check_connection()

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
        """
        Monitor connection status in a background thread.

        This method runs continuously in a separate thread, periodically checking
        the connection status based on the configured interval. It's designed to
        run as a daemon thread so it won't prevent the application from exiting.

        The method:
        1. Checks if it's time to verify connection status
        2. Calls check_connection() if the interval has elapsed
        3. Sleeps briefly to avoid consuming CPU resources
        """
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

        This method:
        1. Checks if there is an active internet connection
        2. Determines if a VPN connection is active using proper detection methods
        3. Updates the connection status based on these checks
        4. Calls the status callback with the updated status

        Returns:
            Dictionary with connection status information including:
            - internet_connected: Whether internet is available
            - vpn_active: Whether VPN is detected
            - status: Human-readable connection status
        """
        # Check internet connection
        self.is_internet_connected = self._check_internet_connection()

        # Check VPN connection using proper detection methods
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

        This method uses multiple approaches to detect VPN connections:
        1. Checks for VPN-related network interfaces on Windows
        2. Checks for VPN-related processes running on the system
        3. Examines network routing tables for VPN indicators

        Note: This is a best-effort detection and may not detect all VPN types.
        The user should ensure their VPN is properly configured.

        Returns:
            True if VPN is detected, False otherwise
        """
        # Check if VPN override is set
        if self.vpn_override is not None:
            logger.info(f"Using VPN override: {self.vpn_override}")
            return self.vpn_override

        # If no internet, then definitely no VPN
        if not self._check_internet_connection():
            logger.info("No internet connection, VPN cannot be active")
            return False

        try:
            import subprocess

            # Method 1: Check for VPN network interfaces on Windows
            result = subprocess.run(['ipconfig', '/all'], capture_output=True, text=True)
            output = result.stdout.lower()

            # Check for common VPN adapter names
            vpn_interface_keywords = [
                'vpn', 'virtual private', 'tap-windows', 'tunnel',
                'cisco', 'nord', 'express', 'proton', 'wireguard'
            ]

            for keyword in vpn_interface_keywords:
                if keyword in output:
                    logger.info(f"VPN detected: Found network interface containing '{keyword}'")
                    return True

            # Method 2: Check for VPN processes
            processes_result = subprocess.run(['tasklist'], capture_output=True, text=True)
            processes = processes_result.stdout.lower()

            vpn_process_keywords = [
                'vpn', 'openvpn', 'nordvpn', 'expressvpn', 'protonvpn',
                'wireguard', 'cisco', 'anyconnect', 'tunnelblick'
            ]

            for keyword in vpn_process_keywords:
                if keyword in processes:
                    logger.info(f"VPN detected: Found process containing '{keyword}'")
                    return True

            # Method 3: Check for non-standard routing
            # This is a more advanced check that looks for routing table entries
            # that might indicate VPN traffic
            route_result = subprocess.run(['route', 'print'], capture_output=True, text=True)
            route_output = route_result.stdout.lower()

            # Look for routing entries that might indicate VPN
            if '0.0.0.0' in route_output and '128.0.0.0' in route_output:
                # Check if there are multiple default gateways or unusual metrics
                # This is a heuristic and may need adjustment
                logger.info("VPN possibly detected through routing table analysis")
                return True

            # No VPN detected through any method
            logger.info("No VPN detected through network interfaces, processes, or routing")
            return False

        except Exception as e:
            logger.error(f"Error checking VPN connection: {e}")
            # If we can't check, default to not detected
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
