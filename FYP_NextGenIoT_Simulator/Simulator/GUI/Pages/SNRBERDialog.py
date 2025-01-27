from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLineEdit, QLabel, QTextEdit, QSlider
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class SNRBERDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SNR BER")
        self.setGeometry(100, 100, 1200, 1000)

        # Apply dark theme styling
        self.setStyleSheet("""
            QDialog { background-color: #2e2e2e; color: #ffffff; }
            QLabel, QLineEdit, QPushButton, QTextEdit, QDial { color: #ffffff; }
            QLineEdit { background-color: #3e3e3e; padding: 5px; border-radius: 5px; }
            QTextEdit { background-color: #3e3e3e; padding: 10px; color: #ffffff; border: none; }
            QPushButton {
                background-color: #4e4e4e; 
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover { background-color: #5e5e5e; }
            QPushButton[selected="true"] { background-color: #2b8cff; }
            QDial { background-color: #3e3e3e; }
        """)

        font = QFont("SF Pro", 10)
        self.selected_modulations = set()  

        self.main_layout = QVBoxLayout(self)

        modulation_type_layout = QVBoxLayout()
        modulation_type_label = QLabel("Modulation Types for SNR BER Test:", font=font)
        modulation_type_layout.addWidget(modulation_type_label, alignment=Qt.AlignLeft)

        # Buttons for Modulation Types
        self.modulation_buttons = {
            "BPSK": QPushButton("BPSK", self),
            "QPSK": QPushButton("QPSK", self),
            "QAM16": QPushButton("QAM16", self),
            "QAM64": QPushButton("QAM64", self),
            "QAM256": QPushButton("QAM256", self),
            "QAM1024": QPushButton("QAM1024", self),
            "QAM4096": QPushButton("QAM4096", self),
        }

        modulation_buttons_layout = QHBoxLayout()
        for name, button in self.modulation_buttons.items():
            button.setFont(font)
            button.setFixedSize(150, 50)
            button.setProperty("selected", "false")
            button.clicked.connect(lambda checked, n=name: self.toggle_modulation_button(n))
            modulation_buttons_layout.addWidget(button)

        modulation_buttons_layout.addStretch()
        modulation_type_layout.addLayout(modulation_buttons_layout)
        self.main_layout.addLayout(modulation_type_layout)
        self.main_layout.addSpacing(50)

        # Bit Rate and Carrier Frequency Inputs
        input_layout = QVBoxLayout()

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
        input_layout.addLayout(bitrate_layout)

        # Carrier Frequency Input
        carrier_freq_layout = QHBoxLayout()
        carrier_freq_label = QLabel("Carrier Frequency:", font=font)
        self.carrier_freq_input = QLineEdit(self)
        self.carrier_freq_input.setPlaceholderText("Enter carrier frequency (Hz)")
        self.carrier_freq_input.setFont(font)
        self.carrier_freq_input.setFixedWidth(400)
        carrier_freq_layout.addWidget(carrier_freq_label)
        carrier_freq_layout.addWidget(self.carrier_freq_input)
        carrier_freq_layout.addStretch()
        input_layout.addLayout(carrier_freq_layout)
        self.main_layout.addLayout(input_layout)
        self.main_layout.addSpacing(50)

        # Replace the QDial section in `SNRBERDialog` with the following:
        char_input_layout = QVBoxLayout()
        char_input_label = QLabel("Number of Input Characters:", font=font)
        char_input_layout.addWidget(char_input_label, alignment=Qt.AlignLeft)

        self.char_slider = QSlider(Qt.Horizontal, self)
        self.char_slider.setRange(0, 100)  #0 - 20000
        self.char_slider.setSingleStep(1)
        self.char_slider.setValue(1) 
        self.char_slider.setStyleSheet("""
                QSlider::groove:horizontal {
                    background: #3e3e3e;
                    height: 10px;
                    border-radius: 5px;
                }
                QSlider::handle:horizontal {
                    background: #2b8cff;
                    width: 20px;
                    height: 20px;
                    margin: -5px 0;
                    border-radius: 10px;
                }
                QSlider::sub-page:horizontal {
                    background: #2b8cff;
                    border-radius: 5px;
                }
            """)
        self.char_slider.valueChanged.connect(self.update_char_label)

        self.char_label = QLabel("0", self)
        self.char_label.setFont(font)
        self.char_label.setAlignment(Qt.AlignCenter)

        char_input_layout.addWidget(self.char_slider)
        char_input_layout.addWidget(self.char_label, alignment=Qt.AlignCenter)
        self.main_layout.addLayout(char_input_layout)


        # SNR Lower and Upper Bound Inputs
        snr_input_layout = QVBoxLayout()
        snr_label = QLabel("SNR Bounds:", font=font)
        snr_input_layout.addWidget(snr_label, alignment=Qt.AlignLeft)

        # SNR Lower Bound
        snr_lower_layout = QHBoxLayout()
        snr_lower_label = QLabel("Lower Bound:", font=font)
        self.snr_lower_input = QLineEdit(self)
        self.snr_lower_input.setPlaceholderText("Enter SNR Lower Bound (dB)")
        self.snr_lower_input.setFont(font)
        self.snr_lower_input.setFixedWidth(400)
        snr_lower_layout.addWidget(snr_lower_label)
        snr_lower_layout.addWidget(self.snr_lower_input)
        snr_lower_layout.addStretch()
        snr_input_layout.addLayout(snr_lower_layout)

        # SNR Upper Bound
        snr_upper_layout = QHBoxLayout()
        snr_upper_label = QLabel("Upper Bound:", font=font)
        self.snr_upper_input = QLineEdit(self)
        self.snr_upper_input.setPlaceholderText("Enter SNR Upper Bound (dB)")
        self.snr_upper_input.setFont(font)
        self.snr_upper_input.setFixedWidth(400)
        snr_upper_layout.addWidget(snr_upper_label)
        snr_upper_layout.addWidget(self.snr_upper_input)
        snr_upper_layout.addStretch()
        snr_input_layout.addLayout(snr_upper_layout)

        self.main_layout.addLayout(snr_input_layout)

        # Add Run Simulation Button
        self.run_simulation_button = QPushButton("Run Simulation", self)
        self.run_simulation_button.setFont(font)
        self.run_simulation_button.setFixedSize(300, 50)
        self.run_simulation_button.clicked.connect(self.run_simulation)
        self.main_layout.addWidget(self.run_simulation_button, alignment=Qt.AlignCenter)

        # Output Display (Terminal-like)
        self.output_display = QTextEdit(self)
        self.output_display.setFont(font)
        self.output_display.setReadOnly(True)
        self.output_display.setFixedHeight(200)
        self.output_display.setStyleSheet("""
            QTextEdit {
                background-color: #3e3e3e; 
                color: #ffffff; 
                border: none; 
                padding: 10px;
            }
        """)
        self.main_layout.addWidget(self.output_display)

    def toggle_modulation_button(self, mod_name):
        """Toggle the state of a modulation button."""
        button = self.modulation_buttons[mod_name]
        if button.property("selected") == "true":
            button.setProperty("selected", "false")
            button.setStyle(button.style())
            self.selected_modulations.discard(mod_name)
            self.display_message(f"{mod_name} deselected")
        else:
            button.setProperty("selected", "true")
            button.setStyle(button.style())
            self.selected_modulations.add(mod_name)
            self.display_message(f"{mod_name} selected")

    def update_char_label(self, value):
            """Map slider value to increments of 200"""
            char_count = value * 200
            self.char_label.setText(f"{char_count:,}") 

    def run_simulation(self):
        self.display_message("Simulation started")

    def display_message(self, message):
        self.output_display.append(message)    
