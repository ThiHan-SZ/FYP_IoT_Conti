# PyQt5_GUI.py

import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QDialog, QVBoxLayout, QHBoxLayout, QWidget,
    QPushButton, QLineEdit, QLabel
)

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from ModulationClass import Modulator  # Reference to your existing Modulator class

class ModulationSettingsDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modulation")
        self.setGeometry(100, 100, 1200, 800)  # Adjusted window size

        # Apply dark theme
        self.setStyleSheet("""
            QDialog { background-color: #2e2e2e; color: #ffffff; }
            QLabel, QLineEdit, QPushButton { color: #ffffff; }
            QLineEdit { background-color: #3e3e3e; padding: 5px; border-radius: 5px; }
            QPushButton {
                background-color: #4e4e4e; 
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover { background-color: #5e5e5e; }
        """)

        # Font settings
        font = QFont("SF Pro", 10)

        # Layouts
        main_layout = QVBoxLayout()
        
        # Input Section Layout
        input_section_layout = QVBoxLayout()

        # Carrier Frequency Input Layout
        carrier_layout = QHBoxLayout()
        carrier_label = QLabel("Carrier Frequency:", font=font)
        self.carrier_freq_input = QLineEdit(self)
        self.carrier_freq_input.setPlaceholderText("Enter carrier frequency (Hz)")
        self.carrier_freq_input.setFont(font)
        self.carrier_freq_input.setFixedWidth(400)
        self.carrier_freq_input.editingFinished.connect(self.display_input_values)  # Connect to terminal output
        carrier_layout.addWidget(carrier_label)
        carrier_layout.addWidget(self.carrier_freq_input)
        carrier_layout.addStretch()  # Pushes elements to the left
        input_section_layout.addLayout(carrier_layout)

        # Bit Rate Input Layout
        bitrate_layout = QHBoxLayout()
        bitrate_label = QLabel("Bit Rate:", font=font)
        self.bit_rate_input = QLineEdit(self)
        self.bit_rate_input.setPlaceholderText("Enter bit rate (bps)")
        self.bit_rate_input.setFont(font)
        self.bit_rate_input.setFixedWidth(400)
        self.bit_rate_input.editingFinished.connect(self.display_input_values)  # Connect to terminal output
        bitrate_layout.addWidget(bitrate_label)
        bitrate_layout.addWidget(self.bit_rate_input)
        bitrate_layout.addStretch()  # Pushes elements to the left
        input_section_layout.addLayout(bitrate_layout)

        # Modulation Mode Label and Buttons in a single layout with no extra spacing
        modulation_layout = QVBoxLayout()
        
        # Modulation Mode Heading
        modulation_mode_label = QLabel("Modulation Mode:", font=QFont("SF Pro", 10))
        modulation_layout.addWidget(modulation_mode_label, alignment=Qt.AlignLeft)

        # BPSK and QPSK buttons in the same row, left-aligned
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
        bpsk_qpsk_layout.addStretch()  # Pushes buttons to the left
        modulation_layout.addLayout(bpsk_qpsk_layout)

        # QAM Buttons in a single row, left-aligned
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
            button.clicked.connect(lambda checked, m=mode: self.select_modulation_mode(m))  # Connect to terminal output
            qam_layout.addWidget(button)
        qam_layout.addStretch()  # Pushes buttons to the left
        modulation_layout.addLayout(qam_layout)

        # Arrange layouts in main layout
        main_layout.addLayout(input_section_layout)
        main_layout.addLayout(modulation_layout)

        # Set main layout
        self.setLayout(main_layout)

        # Selected Modulation Mode
        self.selected_mode = None

    def display_input_values(self):
        # Print input values to the terminal
        carrier_freq = self.carrier_freq_input.text()
        bit_rate = self.bit_rate_input.text()
        print(f"Carrier Frequency: {carrier_freq}")
        print(f"Bit Rate: {bit_rate}")

    def select_modulation_mode(self, mode):
        # Store selected mode and print to terminal
        self.selected_mode = mode
        print(f"Selected Modulation Mode: {mode}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modulation Simulation")
        self.setGeometry(0, 0, 1200, 800)  # Set larger initial window size

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

        # Font settings
        font = QFont("SF Pro", 12, QFont.Bold)

        # Main Layout
        central_widget = QWidget()
        main_layout = QVBoxLayout()

        # Button: Modulation Simulation
        self.simulation_button = QPushButton("Modulation", self)
        self.simulation_button.setFont(font)
        self.simulation_button.setFixedSize(300, 80)
        self.simulation_button.clicked.connect(self.open_modulation_dialog)

        # Button: Demodulation Simulation
        self.future_button = QPushButton("Demodulation", self)
        self.future_button.setFont(font)
        self.future_button.setFixedSize(300, 80)

        # Center Align the buttons
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.simulation_button)
        main_layout.addSpacing(20)  # Add space between buttons
        main_layout.addWidget(self.future_button)

        # Set the main layout to central widget
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def open_modulation_dialog(self):
        dialog = ModulationSettingsDialog()
        dialog.exec()  # Show the dialog


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec_())
