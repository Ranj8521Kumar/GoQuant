"""
Main UI application for the trade simulator.

This module provides the main UI components for the trade simulator application:
1. SimulatorApp: Main window that contains the input and output panels
2. Integration with the trade simulator backend
3. Performance tracking for UI updates
4. Connection status handling and display
5. Callback management for simulation and reconnection

The UI is built using PyQt5 and follows a two-panel design:
- Left panel: Input parameters for trade simulation
- Right panel: Output parameters showing simulation results and connection status
"""
import sys
import time
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, QStatusBar)
from PyQt5.QtCore import QTimer

from ui.input_panel import InputPanel
from ui.output_panel import OutputPanel
from utils.logger import setup_logger
from utils.performance import performance_tracker

logger = setup_logger("ui_app")

class SimulatorApp(QMainWindow):
    """
    Main window for the trade simulator application.

    This class provides:
    - The main application window with input and output panels
    - Handling of input parameter changes
    - Simulation of trades (dummy implementation or via callback)
    - UI updates with simulation results
    - Connection status handling and display
    - Performance tracking for UI updates

    The window is divided into two main panels:
    - Left panel (InputPanel): For setting simulation parameters
    - Right panel (OutputPanel): For displaying simulation results

    The class also provides callback mechanisms to connect the UI to the
    backend simulation logic and WebSocket connection management.
    """

    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        self.init_ui()

        # Timer for updating UI
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_ui)
        self.update_timer.start(100)  # Update every 100ms

        # Performance tracking
        self.last_update_time = time.time()

        # Callbacks
        self.reconnect_callback = None
        self.simulate_callback = None

    def init_ui(self):
        """Initialize the UI components."""
        self.setWindowTitle("Trade Simulator")
        self.setGeometry(100, 100, 1200, 800)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QHBoxLayout()

        # Input panel
        self.input_panel = InputPanel()
        self.input_panel.input_changed.connect(self.on_input_changed)
        main_layout.addWidget(self.input_panel, 1)

        # Output panel
        self.output_panel = OutputPanel()
        main_layout.addWidget(self.output_panel, 2)

        central_widget.setLayout(main_layout)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def on_input_changed(self, input_params):
        """
        Handle input parameter changes.

        Args:
            input_params: Dictionary with input parameters
        """
        logger.info(f"Input parameters changed: {input_params}")
        self.status_bar.showMessage(f"Simulating trade with {input_params['quantity']} USD of {input_params['asset']}")

        # In a real application, this would trigger the simulation
        # For now, we'll just update the UI with dummy data
        self.simulate_trade(input_params)

    def simulate_trade(self, input_params):
        """
        Simulate a trade with the given parameters.

        Args:
            input_params: Dictionary with input parameters
        """
        # Record start time for performance measurement
        start_time = time.time()

        # In a real application, this would call the actual simulation models
        # For now, we'll just generate dummy output data

        # Dummy slippage calculation
        slippage_bps = 2.5 + (input_params['volatility'] * 10)
        slippage = (slippage_bps / 10000) * input_params['quantity']

        # Dummy fee calculation
        fee_tier = input_params['fee_tier']
        fee_rates = {
            'VIP0': 0.0010,
            'VIP1': 0.0009,
            'VIP2': 0.0008,
            'VIP3': 0.0007,
            'VIP4': 0.0006,
            'VIP5': 0.0005
        }
        fee_rate = fee_rates.get(fee_tier, 0.0010)
        fee = input_params['quantity'] * fee_rate

        # Dummy market impact calculation
        impact_factor = 0.0001 + (input_params['volatility'] * 0.0005)
        total_impact = input_params['quantity'] * impact_factor
        temp_impact = total_impact * 0.7
        perm_impact = total_impact * 0.3

        # Dummy net cost calculation
        net_cost = slippage + fee + total_impact

        # Dummy maker/taker proportion
        maker_proportion = 0.0  # For market orders, it's all taker
        taker_proportion = 1.0

        # Calculate processing time
        processing_time = (time.time() - start_time) * 1000  # Convert to ms

        # Record performance
        performance_tracker.record("trade_simulation", processing_time / 1000)  # Record in seconds

        # Create output data
        output_data = {
            'slippage': {
                'slippage': slippage,
                'slippage_bps': slippage_bps
            },
            'fees': {
                'total_fee': fee,
                'effective_bps': fee_rate * 10000
            },
            'market_impact': {
                'total_impact': total_impact,
                'total_impact_bps': impact_factor * 10000,
                'temporary_impact': temp_impact,
                'permanent_impact': perm_impact
            },
            'net_cost': {
                'value': net_cost,
                'bps': (net_cost / input_params['quantity']) * 10000,
                'percent': (net_cost / input_params['quantity']) * 100
            },
            'maker_taker': {
                'maker_proportion': maker_proportion,
                'taker_proportion': taker_proportion
            },
            'latency': {
                'processing_time': processing_time,
                'ui_time': 0,  # Will be updated in update_ui
                'total_time': processing_time  # Will be updated in update_ui
            }
        }

        # Update the output panel
        self.output_data = output_data

    def update_ui(self):
        """Update the UI with the latest data."""
        if hasattr(self, 'output_data'):
            # Measure UI update time
            start_time = time.time()

            # Update the output panel
            self.output_panel.update_output(self.output_data)

            # Calculate UI update time
            ui_time = (time.time() - start_time) * 1000  # Convert to ms

            # Update latency information
            self.output_data['latency']['ui_time'] = ui_time
            self.output_data['latency']['total_time'] = self.output_data['latency']['processing_time'] + ui_time

            # Record performance
            performance_tracker.record("ui_update", ui_time / 1000)  # Record in seconds

    def update_connection_status(self, status_info):
        """
        Update the connection status in the UI.

        Args:
            status_info: Dictionary with connection status information
        """
        # Update the output panel
        self.output_panel.update_connection_status(status_info)

        # Update the status bar
        if isinstance(status_info, dict):
            self.status_bar.showMessage(f"Connection: {status_info.get('status', 'Unknown')}")
        elif isinstance(status_info, str):
            self.status_bar.showMessage(f"Connection: {status_info}")
        else:
            self.status_bar.showMessage(f"Connection: {'Connected' if status_info else 'Disconnected'}")

    def on_reconnect_clicked(self):
        """Handle reconnect button click."""
        logger.info("Reconnect button clicked")

        # Call the reconnect callback if available
        if self.reconnect_callback:
            self.reconnect_callback()
        else:
            logger.warning("No reconnect callback set")

    def set_reconnect_callback(self, callback):
        """
        Set the callback for reconnect button clicks.

        Args:
            callback: Function to call when reconnect button is clicked
        """
        self.reconnect_callback = callback

    def set_simulate_callback(self, callback):
        """
        Set the callback for simulate button clicks.

        Args:
            callback: Function to call when simulate button is clicked
        """
        self.simulate_callback = callback

        # If we have a callback, use it instead of the dummy implementation
        if callback:
            self.original_simulate_trade = self.simulate_trade
            self.simulate_trade = self._simulate_trade_with_callback

    def _simulate_trade_with_callback(self, input_params):
        """
        Simulate a trade using the callback.

        Args:
            input_params: Dictionary with input parameters
        """
        # Call the callback
        if self.simulate_callback:
            # Record start time for performance measurement
            start_time = time.time()

            # Call the callback
            result = self.simulate_callback(input_params)

            # Calculate processing time
            processing_time = (time.time() - start_time) * 1000  # Convert to ms

            # Record performance
            performance_tracker.record("trade_simulation", processing_time / 1000)  # Record in seconds

            # Update the output panel
            self.output_data = result
        else:
            # Fall back to the dummy implementation
            self.original_simulate_trade(input_params)

    def run(self):
        """Run the application."""
        self.show()
        QApplication.instance().exec_()


def run_app():
    """Run the application."""
    app = QApplication(sys.argv)
    window = SimulatorApp()
    window.show()
    sys.exit(app.exec_())
