import sys
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QDialog, QVBoxLayout, QHBoxLayout, QWidget,
    QPushButton, QLineEdit, QLabel, QTextEdit, QCheckBox, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from testmodulator import SimpleModulator  # Import the Modulator class for signal modulation logic
from matplotlib.figure import Figure

# Dialog for Modulation
class ModulationDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modulation")  # Set the dialog title
        self.setGeometry(100, 100, 1200, 800)  # Set the size of the dialog window

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
        main_layout.addWidget(self.save_checkbox)

        self.plot_iq_checkbox = QCheckBox("Plot I and Q Components", self)
        self.plot_iq_checkbox.setFont(font)
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

        # Placeholder for the canvas
        self.canvas = FigureCanvas(Figure())  # Create a blank canvas
        main_layout.addWidget(self.canvas)   # Add it to the layout    

    def display_message(self, message):
        """Append a message to the output display."""
        self.output_display.append(message)

    def select_modulation_mode(self, mode):
        """Set selected modulation mode and update the display."""
        self.selected_mode = mode
        self.display_message(f"Selected Modulation Mode: {self.selected_mode}")

    def run_simulation(self):
        #Display Digital & Modulated S
        try:
            # Get inputs
            carrier_freq = self.carrier_freq_input.text()
            bit_rate = self.bit_rate_input.text()
            message = self.message_input.text()

            # Validate inputs
            if not carrier_freq or not bit_rate or not self.selected_mode or not message:
                self.display_message("Please provide all inputs and select a modulation mode.")
                return

            carrier_freq = int(carrier_freq)
            bit_rate = int(bit_rate)

            # Initialize the modulator and perform calculations
            modulator = SimpleModulator(self.selected_mode, bit_rate, carrier_freq)
            bitstr = modulator.msgchar2bit(message)
            t_Shaped_Pulse, modulated_signal = modulator.modulate(bitstr)

            '''
            # Generate the figure
            fig = modulator.digital_modulated_plot(bitstr, t_Shaped_Pulse, modulated_signal)

            # Update the canvas
            self.canvas.figure = fig  # Replace the current figure with the new one
            self.canvas.draw()        # Refresh the canvas

            self.display_message("Simulation completed successfully.")'''

        except ValueError as e:
            self.display_message(f"Error: {str(e)}")
        except Exception as e:
            self.display_message(f"An unexpected error occurred: {str(e)}")

        self.display_message("Simulation completed successfully.")


# Main Application Window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Wireless Comms SimTool")  
        self.setGeometry(0, 0, 1200, 800)  # Set size 

        # Dark theme 
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

        #setting fonts and layout
        font = QFont("SF Pro", 12, QFont.Bold)
        central_widget = QWidget()
        main_layout = QVBoxLayout()

        # Modulation Button
        self.mod_button = QPushButton("Modulator", self)
        self.mod_button.setFont(font)
        self.mod_button.setFixedSize(1000, 80)
        self.mod_button.clicked.connect(self.open_modulation_dialog)

        #  DeModulation Button
        self.demod_button = QPushButton("Demodulator", self)
        self.demod_button.setFont(font)
        self.demod_button.setFixedSize(1000, 80)

        # Add buttons to the main layout
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.mod_button)
        main_layout.addSpacing(20)
        main_layout.addWidget(self.demod_button)

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.dialog = None  # Store the dialog instance

    def open_modulation_dialog(self):
        """Open the modulation dialog."""
        if self.dialog is None:  # Ensure only one dialog instance
            self.dialog = ModulationDialog()
            self.dialog.finished.connect(self.on_dialog_closed)
            self.dialog.show()

    def on_dialog_closed(self):
        """Handle dialog closure."""
        self.dialog = None  # Reset the dialog reference

# Application Entry Point
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())