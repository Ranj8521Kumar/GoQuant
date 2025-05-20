"""
Output panel for the trade simulator UI.

This module provides the output panel component for the trade simulator UI:
1. Displays simulation results (slippage, fees, market impact, etc.)
2. Updates in real-time with new simulation results
3. Tracks and displays performance metrics

The panel is organized into several sections:
- Expected Slippage
- Expected Fees
- Expected Market Impact
- Net Cost
- Maker/Taker Proportion
- Internal Latency
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel,
                            QGroupBox, QFormLayout)
from PyQt5.QtCore import Qt, QTimer

class OutputPanel(QWidget):
    """
    Output panel for the trade simulator UI.

    This class provides:
    - Display of simulation results (slippage, fees, market impact, etc.)
    - Real-time updates of simulation results
    - Performance metrics display

    The UI is organized into several sections, each displaying a specific
    aspect of the simulation results.
    """



    def __init__(self, parent=None):
        """Initialize the output panel."""
        super().__init__(parent)
        self.init_ui()

        # Timer for updating latency
        self.latency_timer = QTimer()
        self.latency_timer.timeout.connect(self.update_latency)
        self.latency_timer.start(1000)  # Update every second

        # Connection status details
        self.connection_details = {
            'status': 'Disconnected',
            'internet': False,
            'vpn': False,
            'last_message': None,
            'reconnect_attempts': 0
        }

    def init_ui(self):
        """Initialize the UI components."""
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignTop)

        # Title
        title_label = QLabel("Output Parameters")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        main_layout.addWidget(title_label)

        # Slippage group
        slippage_group = QGroupBox("Expected Slippage")
        slippage_layout = QFormLayout()
        self.slippage_value_label = QLabel("0.00 USD")
        self.slippage_bps_label = QLabel("0.00 bps")
        slippage_layout.addRow("Value:", self.slippage_value_label)
        slippage_layout.addRow("Basis Points:", self.slippage_bps_label)
        slippage_group.setLayout(slippage_layout)
        main_layout.addWidget(slippage_group)

        # Fees group
        fees_group = QGroupBox("Expected Fees")
        fees_layout = QFormLayout()
        self.fees_value_label = QLabel("0.00 USD")
        self.fees_bps_label = QLabel("0.00 bps")
        fees_layout.addRow("Value:", self.fees_value_label)
        fees_layout.addRow("Basis Points:", self.fees_bps_label)
        fees_group.setLayout(fees_layout)
        main_layout.addWidget(fees_group)

        # Market impact group
        impact_group = QGroupBox("Expected Market Impact")
        impact_layout = QFormLayout()
        self.impact_value_label = QLabel("0.00 USD")
        self.impact_bps_label = QLabel("0.00 bps")
        self.temp_impact_label = QLabel("0.00 USD")
        self.perm_impact_label = QLabel("0.00 USD")
        impact_layout.addRow("Total Value:", self.impact_value_label)
        impact_layout.addRow("Basis Points:", self.impact_bps_label)
        impact_layout.addRow("Temporary:", self.temp_impact_label)
        impact_layout.addRow("Permanent:", self.perm_impact_label)
        impact_group.setLayout(impact_layout)
        main_layout.addWidget(impact_group)

        # Net cost group
        cost_group = QGroupBox("Net Cost")
        cost_layout = QFormLayout()
        self.cost_value_label = QLabel("0.00 USD")
        self.cost_bps_label = QLabel("0.00 bps")
        self.cost_percent_label = QLabel("0.00%")
        cost_layout.addRow("Value:", self.cost_value_label)
        cost_layout.addRow("Basis Points:", self.cost_bps_label)
        cost_layout.addRow("Percentage:", self.cost_percent_label)
        cost_group.setLayout(cost_layout)
        main_layout.addWidget(cost_group)

        # Maker/Taker proportion group
        proportion_group = QGroupBox("Maker/Taker Proportion")
        proportion_layout = QFormLayout()
        self.maker_label = QLabel("0%")
        self.taker_label = QLabel("100%")
        proportion_layout.addRow("Maker:", self.maker_label)
        proportion_layout.addRow("Taker:", self.taker_label)
        proportion_group.setLayout(proportion_layout)
        main_layout.addWidget(proportion_group)

        # Latency group
        latency_group = QGroupBox("Internal Latency")
        latency_layout = QFormLayout()
        self.processing_label = QLabel("0.00 ms")
        self.ui_label = QLabel("0.00 ms")
        self.total_label = QLabel("0.00 ms")
        latency_layout.addRow("Processing Time:", self.processing_label)
        latency_layout.addRow("UI Update Time:", self.ui_label)
        latency_layout.addRow("Total Time:", self.total_label)
        latency_group.setLayout(latency_layout)
        main_layout.addWidget(latency_group)



        self.setLayout(main_layout)

    def update_output(self, output_data):
        """
        Update the output panel with new data.

        Args:
            output_data: Dictionary with output parameters
        """
        # Update slippage
        slippage = output_data.get('slippage', {})
        self.slippage_value_label.setText(f"{slippage.get('slippage', 0):.4f} USD")
        self.slippage_bps_label.setText(f"{slippage.get('slippage_bps', 0):.2f} bps")

        # Update fees
        fees = output_data.get('fees', {})
        self.fees_value_label.setText(f"{fees.get('total_fee', 0):.4f} USD")
        self.fees_bps_label.setText(f"{fees.get('effective_bps', 0):.2f} bps")

        # Update market impact
        impact = output_data.get('market_impact', {})
        self.impact_value_label.setText(f"{impact.get('total_impact', 0):.4f} USD")
        self.impact_bps_label.setText(f"{impact.get('total_impact_bps', 0):.2f} bps")
        self.temp_impact_label.setText(f"{impact.get('temporary_impact', 0):.4f} USD")
        self.perm_impact_label.setText(f"{impact.get('permanent_impact', 0):.4f} USD")

        # Update net cost
        cost = output_data.get('net_cost', {})
        self.cost_value_label.setText(f"{cost.get('value', 0):.4f} USD")
        self.cost_bps_label.setText(f"{cost.get('bps', 0):.2f} bps")
        self.cost_percent_label.setText(f"{cost.get('percent', 0):.4f}%")

        # Update maker/taker proportion
        proportion = output_data.get('maker_taker', {})
        self.maker_label.setText(f"{proportion.get('maker_proportion', 0) * 100:.1f}%")
        self.taker_label.setText(f"{proportion.get('taker_proportion', 0) * 100:.1f}%")

        # Update latency
        latency = output_data.get('latency', {})
        self.processing_label.setText(f"{latency.get('processing_time', 0):.2f} ms")
        self.ui_label.setText(f"{latency.get('ui_time', 0):.2f} ms")
        self.total_label.setText(f"{latency.get('total_time', 0):.2f} ms")

    def update_connection_status(self, status_info):
        """
        Update the internal connection status information.

        This method only updates the internal connection details dictionary
        without updating any UI elements, as the connection status UI has been removed.

        The method accepts different types of status information:
        - Dictionary: Full status update with all details
        - String: Simple status update (just the status text)
        - Boolean: Legacy format (True for connected, False for disconnected)

        Args:
            status_info: Connection status information in one of the supported formats
        """
        # Update connection details
        if isinstance(status_info, dict):
            # Full status update
            self.connection_details.update(status_info)
        elif isinstance(status_info, str):
            # Simple status update
            self.connection_details['status'] = status_info
        else:
            # Boolean status (for backward compatibility)
            self.connection_details['status'] = "Connected" if status_info else "Disconnected"



    def update_latency(self):
        """Update the latency display with random values for testing."""
        # This method is just for testing UI updates
        # In the real application, this will be updated with actual latency measurements
        pass
