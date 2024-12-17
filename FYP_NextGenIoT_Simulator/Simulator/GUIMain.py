import sys
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QDialog, QVBoxLayout, QHBoxLayout, QWidget,
    QPushButton, QLineEdit, QLabel, QTextEdit, QCheckBox, QMessageBox, QScrollArea
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from matplotlib.figure import Figure

from SimulationClassCompact.ChannelClass import SimpleGWNChannel_dB
from SimulationClassCompact.DemodulationClass import Demodulator
from SimulationClassCompact.ModulationClass import Modulator

import traceback

class ScrollableFigureDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.container = QWidget()
        self.container_layout = QVBoxLayout()
        self.container.setLayout(self.container_layout)

        self.scroll_area.setWidget(self.container)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.scroll_area)
        self.setLayout(self.layout)

    def add_figure(self, figure):
        canvas = FigureCanvas(figure)
        self.container_layout.addWidget(canvas)

class ModulationDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modulation")  # Set the dialog title
        self.setGeometry(100, 100, 1200, 800)  # Set the size of the dialog window

        ##### Auxillary Variables #####
        self.plot_iq = False
        self.save_signal = False

        # Apply dark theme styling for the dialog
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
            QCheckBox { color: #ffffff; }
        """)

        font = QFont("SF Pro", 10)  # Default font for the GUI elements

        # Main layout of the dialog
        main_layout = QVBoxLayout()

        # Input for Carrier Frequency
        carrier_layout = QHBoxLayout()
        carrier_label = QLabel("Carrier Frequency:", font=font)  # Label for the input
        self.carrier_freq_input = QLineEdit(self)  # Input field for carrier frequency
        self.carrier_freq_input.setPlaceholderText("Enter carrier frequency (Hz)")
        self.carrier_freq_input.setFont(font)
        self.carrier_freq_input.setFixedWidth(400)
        carrier_layout.addWidget(carrier_label)
        carrier_layout.addWidget(self.carrier_freq_input)
        carrier_layout.addStretch()
        main_layout.addLayout(carrier_layout)

        # Input for Bit Rate
        bitrate_layout = QHBoxLayout()
        bitrate_label = QLabel("Bit Rate:", font=font)  # Label for bit rate input
        self.bit_rate_input = QLineEdit(self)  # Input field for bit rate
        self.bit_rate_input.setPlaceholderText("Enter bit rate (bps)")
        self.bit_rate_input.setFont(font)
        self.bit_rate_input.setFixedWidth(400)
        bitrate_layout.addWidget(bitrate_label)
        bitrate_layout.addWidget(self.bit_rate_input)
        bitrate_layout.addStretch()
        main_layout.addLayout(bitrate_layout)

        # Modulation Mode Buttons
        modulation_layout = QVBoxLayout()
        modulation_mode_label = QLabel("Modulation Mode:", font=QFont("SF Pro", 10))  # Section label
        modulation_layout.addWidget(modulation_mode_label, alignment=Qt.AlignLeft)

        # Buttons for BPSK and QPSK Modulation Modes
        bpsk_qpsk_layout = QHBoxLayout()
        self.bpsk_button = QPushButton("BPSK", self)  # Button for BPSK
        self.bpsk_button.setFont(font)
        self.bpsk_button.setFixedSize(150, 50)
        self.bpsk_button.clicked.connect(lambda: self.select_modulation_mode("BPSK"))  # On-click handler

        self.qpsk_button = QPushButton("QPSK", self)  # Button for QPSK
        self.qpsk_button.setFont(font)
        self.qpsk_button.setFixedSize(150, 50)
        self.qpsk_button.clicked.connect(lambda: self.select_modulation_mode("QPSK"))

        bpsk_qpsk_layout.addWidget(self.bpsk_button)
        bpsk_qpsk_layout.addWidget(self.qpsk_button)
        bpsk_qpsk_layout.addStretch()
        modulation_layout.addLayout(bpsk_qpsk_layout)

        # Buttons for QAM Modes
        qam_layout = QHBoxLayout()
        self.qam_buttons = {
            "QAM16": QPushButton("QAM16"),
            "QAM64": QPushButton("QAM64"),
            "QAM256": QPushButton("QAM256"),
            "QAM1024": QPushButton("QAM1024"),
            "QAM4096": QPushButton("QAM4096")
        }

        # Add QAM buttons dynamically and connect their signals
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

        # Checkboxes for Additional Options
        self.save_checkbox = QCheckBox("Save Modulated Signal", self)
        self.save_checkbox.setFont(font)
        self.save_checkbox.stateChanged.connect(self.handle_save_checkbox)  # Connect to handler
        main_layout.addWidget(self.save_checkbox)

        self.plot_iq_checkbox = QCheckBox("Plot I and Q Components", self)
        self.plot_iq_checkbox.setFont(font)
        self.plot_iq_checkbox.stateChanged.connect(self.handle_plot_iq_checkbox)  # Connect to handler
        main_layout.addWidget(self.plot_iq_checkbox)

        # Button to Run the Simulation
        self.run_button = QPushButton("Run Simulation", self)
        self.run_button.setFont(font)
        self.run_button.setFixedSize(200, 50)
        self.run_button.clicked.connect(self.run_simulation)  # Connect button click to the run_simulation method
        main_layout.addWidget(self.run_button, alignment=Qt.AlignCenter)

        # Output Display for Simulation Results
        self.output_display = QTextEdit(self)
        self.output_display.setFont(font)
        self.output_display.setReadOnly(True)
        self.output_display.setFixedHeight(200)
        main_layout.addWidget(self.output_display)

        # Set the layout of the dialog
        self.setLayout(main_layout)
        self.selected_mode = None  # Store the selected modulation mode
    
    def display_message(self, message):
        """Append a message to the output display."""
        self.output_display.append(message)

    def select_modulation_mode(self, mode):
        """Set selected modulation mode and update the display."""
        self.selected_mode = mode
        self.display_message(f"Selected Modulation Mode: {self.selected_mode}")

    def handle_save_checkbox(self, state):
        """Handle state change for Save checkbox."""
        self.save_signal = state == Qt.Checked

    def handle_plot_iq_checkbox(self, state):
        """Handle state change for Plot IQ checkbox."""
        self.plot_iq = state == Qt.Checked

    def run_simulation(self):
        #Display Digital & Modulated S
        try:
            # Get inputs
            carrier_freq = self.carrier_freq_input.text()
            bit_rate = self.bit_rate_input.text()
            message = self.message_input.text()

            if not carrier_freq or not bit_rate or not self.selected_mode or not message:
                self.display_message("Please provide all inputs and select a modulation mode.")
                return
            
            carrier_freq = int(carrier_freq)
            bit_rate = int(bit_rate)

            # Initialize the modulator and perform calculations
            modulator = Modulator(self.selected_mode, bit_rate, carrier_freq)
            modulator.IQ_Return = self.plot_iq
            modulator.save_signal = self.save_signal
            bitstr = modulator.msgchar2bit(message)
            digital_signal, x_axis_digital = modulator.digitalsignal(bitstr)

            if modulator.IQ_Return != True:
                t_axis, modualted_sig = modulator.modulate(bitstr)
            else:
                t_axis, modualted_sig, I_FC, Q_FC, I_SP, Q_SP, Dirac_Comb, RRC_delay = modulator.modulate(bitstr)
            
            if modulator.save_signal == True:
                message_filename = message.replace(" ", "_")
                modulator.save(f'Simulator_File__{message_filename}__{carrier_freq/1000}kHz_{bit_rate/1000}kbps_N{modulator.modulation_mode}.wav', modualted_sig)
                self.display_message("Signal saved successfully.")

        except ValueError as e:
            # Show verbose error information for ValueErrors
            error_details = traceback.format_exc()  # Get the full traceback
            self.display_message(f"ValueError: {str(e)}\nDetails:\n{error_details}")
        except Exception as e:
            # Show verbose error information for any other exceptions
            error_details = traceback.format_exc()  # Get the full traceback
            self.display_message(f"Unexpected Error: {str(e)}\nDetails:\n{error_details}")

        self.display_message("Simulation completed successfully.")
