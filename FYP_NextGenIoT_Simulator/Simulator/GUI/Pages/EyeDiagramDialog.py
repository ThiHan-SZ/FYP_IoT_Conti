from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLineEdit, QLabel, QTextEdit, QSlider, QCheckBox
)

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class EyeDiagramDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Eye Diagram")
        self.setGeometry(100, 100, 1200, 800)

        # Apply dark theme styling
        self.setStyleSheet("""
            QDialog { background-color: #2e2e2e; color: #ffffff; }
            QLabel, QLineEdit, QPushButton, QTextEdit, QCheckBox { color: #ffffff; }
            QLineEdit { background-color: #3e3e3e; padding: 5px; border-radius: 5px; }
            QTextEdit { background-color: #3e3e3e; padding: 10px; }
            QPushButton {
                background-color: #4e4e4e; 
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover { background-color: #5e5e5e; }
            QPushButton[selected="true"] { background-color: #2b8cff; }
            QCheckBox { color: #ffffff; }
        """)

        font = QFont("SF Pro", 10)
        self.selected_modulations = set()  

        self.main_layout = QVBoxLayout(self)
        modulation_type_layout = QVBoxLayout()

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
        for mode, button in self.modulation_buttons.items():
            button.setFont(font)
            button.setFixedSize(150, 50)
            button.clicked.connect(lambda checked, m=mode: self.select_modulation_mode(m))
            button.setProperty("selected", "false")
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

        # Slider for Number of Input Characters
        char_input_layout = QVBoxLayout()
        char_input_label = QLabel("Number of Input Characters:", font=font)
        char_input_layout.addWidget(char_input_label, alignment=Qt.AlignLeft)

        self.char_slider = QSlider(Qt.Horizontal, self)
        self.char_slider.setRange(1, 100)  # Range mapped to 1000 - 100000
        self.char_slider.setSingleStep(1)
        self.char_slider.setValue(1)  # Default value corresponds to 1000
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

        self.char_label = QLabel("1000", self)
        self.char_label.setFont(font)
        self.char_label.setAlignment(Qt.AlignCenter)

        char_input_layout.addWidget(self.char_slider)
        char_input_layout.addWidget(self.char_label, alignment=Qt.AlignCenter)
        self.main_layout.addLayout(char_input_layout)

        # Constellation Plot Checkbox
        self.constellation_checkbox = QCheckBox("Enable Constellation Plot", self)
        self.constellation_checkbox.setFont(font)
        self.main_layout.addWidget(self.constellation_checkbox)

        # Run Button
        self.run_button = QPushButton("Run Eye Diagram Simulation", self)
        self.run_button.setFont(font)
        self.run_button.setFixedSize(500, 50)
        self.main_layout.addWidget(self.run_button, alignment=Qt.AlignCenter)

        # Output Display (Terminal-like)
        self.output_display = QTextEdit(self)
        self.output_display.setFont(font)
        self.output_display.setReadOnly(True)
        self.output_display.setFixedHeight(200)
        self.output_display.setStyleSheet("""
            QTextEdit {
                background-color: #3e3e3e;
                color: #ffffff;
                border-radius: 5px;
            }
        """)
        self.main_layout.addWidget(self.output_display)

    def select_modulation_button(self, mode):
        """Ensure only one modulation button is selected at a time."""
        # Reset all buttons
        for name, button in self.modulation_buttons.items():
            button.setProperty("selected", "false")
            button.setStyle(button.style())

        # Highlight the selected button
        button = self.modulation_buttons[mode]
        button.setProperty("selected", "true")
        button.setStyle(button.style())
        self.output_display.append(f"{mode} selected")

    def update_char_label(self, value):
        """Update the label for the number of input characters."""
        char_count = value * 1000  # Map range 1-100 to 1000-100000
        self.char_label.setText(f"{char_count:,}")

    def display_message(self, message):
        """Append a message to the output display."""
        self.output_display.append(message)

    def select_modulation_mode(self, mode):
        """Set selected modulation mode and update the display."""
        self.selected_mode = mode
        self.display_message(f"Selected Modulation Mode: {self.selected_mode}")