# PyQt5_GUI.py

import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QDialog, QVBoxLayout, QHBoxLayout, QWidget,
    QPushButton, QLineEdit, QLabel, QTextEdit, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from ModulationClass import Modulator  # Import the Modulator class

class ModulationDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modulation")
        self.setGeometry(100, 100, 1200, 800)

        # Dark theme styling
        self.setStyleSheet("""
            QDialog { background-color: #2e2e2e; color: #ffffff; }
            QLabel, QLineEdit, QPushButton, QTextEdit { color: #ffffff; }
            QLineEdit { background-color: #3e3e3e; padding: 5px; border-radius: 5px; }
            QTextEdit { background-color: #3e3e3e; padding: 10px; }
            QPushButton {
                background-color: #4e4e4e; 
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover { background-color: #5e5e5e; }
        """)

        # Font settings
        font = QFont("SF Pro", 10)

        # Main layout
        main_layout = QVBoxLayout()

        # Carrier Frequency Input
        carrier_layout = QHBoxLayout()
        carrier_label = QLabel("Carrier Frequency:", font=font)
        self.carrier_freq_input = QLineEdit(self)
        self.carrier_freq_input.setPlaceholderText("Enter carrier frequency (Hz)")
        self.carrier_freq_input.setFont(font)
        self.carrier_freq_input.setFixedWidth(400)
        carrier_layout.addWidget(carrier_label)
        carrier_layout.addWidget(self.carrier_freq_input)
        carrier_layout.addStretch()
        main_layout.addLayout(carrier_layout)

        # Bit Rate Input
        bitrate_layout = QHBoxLayout()
        bitrate_label = QLabel("Bit Rate:", font=font)
        self.bit_rate_input = QLineEdit(self)
        self.bit_rate_input.setPlaceholderText("Enter bit rate (bps)")
        self.bit_rate_input.setFont(font)
        self.bit_rate_input.setFixedWidth(400)
        bitrate_layout.addWidget(bitrate_label)
        bitrate_layout.addWidget(self.bit_rate_input)
        bitrate_layout.addStretch()
        main_layout.addLayout(bitrate_layout)

        # Modulation Mode Buttons
        modulation_layout = QVBoxLayout()
        modulation_mode_label = QLabel("Modulation Mode:", font=QFont("SF Pro", 10))
        modulation_layout.addWidget(modulation_mode_label, alignment=Qt.AlignLeft)

        # BPSK and QPSK Buttons
        bpsk_qpsk_layout = QHBoxLayout()
        self.bpsk_button = QPushButton("BPSK", self)
        self.bpsk_button.setFont(font)
        self.bpsk_button.setFixedSize(150, 50)
        self.bpsk_button.clicked.connect(lambda: self.select_modulation_mode("BPSK"))

        self.qpsk_button = QPushButton("QPSK", self)
        self.qpsk_button.setFont(font)
        self.qpsk_button.setFixedSize(150, 50)
        self.qpsk_button.clicked.connect(lambda: self.select_modulation_mode("QPSK"))

        bpsk_qpsk_layout.addWidget(self.bpsk_button)
        bpsk_qpsk_layout.addWidget(self.qpsk_button)
        bpsk_qpsk_layout.addStretch()
        modulation_layout.addLayout(bpsk_qpsk_layout)

        # QAM Buttons
        qam_layout = QHBoxLayout()
        self.qam_buttons = {
            "QAM16": QPushButton("QAM16"),
            "QAM64": QPushButton("QAM64"),
            "QAM256": QPushButton("QAM256"),
            "QAM1024": QPushButton("QAM1024"),
            "QAM4096": QPushButton("QAM4096")
        }

        for mode, button in self.qam_buttons.items():
            button.setFont(font)
            button.setFixedSize(150, 50)
            button.clicked.connect(lambda checked, m=mode: self.select_modulation_mode(m))
            qam_layout.addWidget(button)
        qam_layout.addStretch()
        modulation_layout.addLayout(qam_layout)
        main_layout.addLayout(modulation_layout)

        # Message Input
        self.message_input = QLineEdit(self)
        self.message_input.setPlaceholderText("Enter message to modulate")
        self.message_input.setFont(font)
        main_layout.addWidget(self.message_input)

        # Run Simulation Button
        self.run_button = QPushButton("Run Simulation", self)
        self.run_button.setFont(font)
        self.run_button.setFixedSize(200, 50)
        self.run_button.clicked.connect(self.run_simulation)
        main_layout.addWidget(self.run_button, alignment=Qt.AlignCenter)

        # Output Display
        self.output_display = QTextEdit(self)
        self.output_display.setFont(font)
        self.output_display.setReadOnly(True)
        self.output_display.setFixedHeight(200)
        main_layout.addWidget(self.output_display)

        # Set main layout
        self.setLayout(main_layout)
        self.selected_mode = None

    def display_message(self, message):
        """Append a message to the output display."""
        self.output_display.append(message)

    def select_modulation_mode(self, mode):
        """Set selected modulation mode and update the display."""
        self.selected_mode = mode
        self.display_message(f"Selected Modulation Mode: {mode}")

    def run_simulation(self):
        """Run the modulation simulation with the provided parameters."""
        carrier_freq = self.carrier_freq_input.text()
        bit_rate = self.bit_rate_input.text()
        message = self.message_input.text()

        if not carrier_freq or not bit_rate or not self.selected_mode or not message:
            QMessageBox.warning(self, "Input Error", "Please provide all inputs and select a modulation mode.")
            return

        try:
            carrier_freq = int(carrier_freq)
            bit_rate = int(bit_rate)
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Carrier frequency and bit rate must be integers.")
            return

        # Instantiate the Modulator and run modulation
        try:
            modulator = Modulator(self.selected_mode, bit_rate, carrier_freq)
            bitstr = modulator.msgchar2bit(message)
            t, modulated_signal = modulator.modulate(bitstr)
            self.display_message("Modulation completed successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred during modulation: {e}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modulation Simulation")
        self.setGeometry(0, 0, 1200, 800)

        # Apply dark theme
        self.setStyleSheet("""
            QMainWindow { background-color: #2e2e2e; color: #ffffff; }
            QPushButton { 
                background-color: #4e4e4e; 
                border-radius: 5px; 
                padding: 15px;
                color: #ffffff;
            }
            QPushButton:hover { background-color: #5e5e5e; }
        """)

        font = QFont("SF Pro", 12, QFont.Bold)
        central_widget = QWidget()
        main_layout = QVBoxLayout()

        # Modulation Simulation Button
        self.simulation_button = QPushButton("Modulation Simulation", self)
        self.simulation_button.setFont(font)
        self.simulation_button.setFixedSize(300, 80)
        self.simulation_button.clicked.connect(self.open_modulation_dialog)

        # Demodulation Simulation Button (Placeholder for future implementation)
        self.future_button = QPushButton("Demodulation Simulation", self)
        self.future_button.setFont(font)
        self.future_button.setFixedSize(300, 80)

        # Align buttons
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.simulation_button)
        main_layout.addSpacing(20)
        main_layout.addWidget(self.future_button)

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def open_modulation_dialog(self):
        dialog = ModulationDialog()
        dialog.exec()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec_())
