"""
Input panel for the trade simulator UI.
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QComboBox, QLineEdit, QPushButton, QFormLayout,
                            QGroupBox, QDoubleSpinBox, QSpinBox)
from PyQt5.QtCore import pyqtSignal, Qt

class InputPanel(QWidget):
    """Input panel for the trade simulator UI."""
    
    # Signal emitted when input parameters change
    input_changed = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        """Initialize the input panel."""
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI components."""
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignTop)
        
        # Title
        title_label = QLabel("Input Parameters")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        main_layout.addWidget(title_label)
        
        # Exchange selection
        exchange_group = QGroupBox("Exchange")
        exchange_layout = QVBoxLayout()
        self.exchange_combo = QComboBox()
        self.exchange_combo.addItem("OKX")
        exchange_layout.addWidget(self.exchange_combo)
        exchange_group.setLayout(exchange_layout)
        main_layout.addWidget(exchange_group)
        
        # Asset selection
        asset_group = QGroupBox("Spot Asset")
        asset_layout = QVBoxLayout()
        self.asset_combo = QComboBox()
        self.asset_combo.addItems(["BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT", "ADA-USDT"])
        asset_layout.addWidget(self.asset_combo)
        asset_group.setLayout(asset_layout)
        main_layout.addWidget(asset_group)
        
        # Order type
        order_type_group = QGroupBox("Order Type")
        order_type_layout = QVBoxLayout()
        self.order_type_combo = QComboBox()
        self.order_type_combo.addItems(["Market"])
        order_type_layout.addWidget(self.order_type_combo)
        order_type_group.setLayout(order_type_layout)
        main_layout.addWidget(order_type_group)
        
        # Quantity
        quantity_group = QGroupBox("Quantity (USD)")
        quantity_layout = QVBoxLayout()
        self.quantity_spin = QDoubleSpinBox()
        self.quantity_spin.setRange(1, 10000)
        self.quantity_spin.setValue(100)
        self.quantity_spin.setSingleStep(10)
        quantity_layout.addWidget(self.quantity_spin)
        quantity_group.setLayout(quantity_layout)
        main_layout.addWidget(quantity_group)
        
        # Volatility
        volatility_group = QGroupBox("Volatility (%)")
        volatility_layout = QVBoxLayout()
        self.volatility_spin = QDoubleSpinBox()
        self.volatility_spin.setRange(0.1, 100)
        self.volatility_spin.setValue(30)
        self.volatility_spin.setSingleStep(1)
        volatility_layout.addWidget(self.volatility_spin)
        volatility_group.setLayout(volatility_layout)
        main_layout.addWidget(volatility_group)
        
        # Fee tier
        fee_tier_group = QGroupBox("Fee Tier")
        fee_tier_layout = QVBoxLayout()
        self.fee_tier_combo = QComboBox()
        self.fee_tier_combo.addItems(["VIP0", "VIP1", "VIP2", "VIP3", "VIP4", "VIP5"])
        fee_tier_layout.addWidget(self.fee_tier_combo)
        fee_tier_group.setLayout(fee_tier_layout)
        main_layout.addWidget(fee_tier_group)
        
        # Simulate button
        self.simulate_button = QPushButton("Simulate")
        self.simulate_button.setStyleSheet("font-weight: bold; padding: 8px;")
        main_layout.addWidget(self.simulate_button)
        
        # Connect signals
        self.exchange_combo.currentTextChanged.connect(self.on_input_changed)
        self.asset_combo.currentTextChanged.connect(self.on_input_changed)
        self.order_type_combo.currentTextChanged.connect(self.on_input_changed)
        self.quantity_spin.valueChanged.connect(self.on_input_changed)
        self.volatility_spin.valueChanged.connect(self.on_input_changed)
        self.fee_tier_combo.currentTextChanged.connect(self.on_input_changed)
        self.simulate_button.clicked.connect(self.on_simulate_clicked)
        
        self.setLayout(main_layout)
    
    def on_input_changed(self):
        """Handle input parameter changes."""
        self.input_changed.emit(self.get_input_parameters())
    
    def on_simulate_clicked(self):
        """Handle simulate button click."""
        self.input_changed.emit(self.get_input_parameters())
    
    def get_input_parameters(self):
        """
        Get the current input parameters.
        
        Returns:
            Dictionary with input parameters
        """
        return {
            'exchange': self.exchange_combo.currentText(),
            'asset': self.asset_combo.currentText(),
            'order_type': self.order_type_combo.currentText(),
            'quantity': self.quantity_spin.value(),
            'volatility': self.volatility_spin.value() / 100,  # Convert to decimal
            'fee_tier': self.fee_tier_combo.currentText()
        }
