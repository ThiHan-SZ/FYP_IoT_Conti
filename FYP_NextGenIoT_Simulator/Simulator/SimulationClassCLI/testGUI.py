import sys
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QDialog, QVBoxLayout, QHBoxLayout, 
    QWidget,QPushButton, QLineEdit, QLabel, QTextEdit, QCheckBox, 
    QMessageBox, QFileDialog,QScrollArea,QComboBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from testmodulator import Modulator
from testdemodulator import Demodulator

from matplotlib.figure import Figure
import traceback

class GraphDialog(QDialog):
    def __init__(self, figure, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Graph Viewer")
        self.setGeometry(150, 150, 2400, 1500)

        # Layout for the dialog
        layout = QVBoxLayout()
        # Matplotlib canvas
        self.canvas = FigureCanvas(figure)
        layout.addWidget(self.canvas)
        self.setLayout(layout)

# Dialog for Modulation
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

            # Validate inputs
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
                modulator.save(f'test_file__{message_filename}__{modulator.carrier_freq/1000}kHz_{bit_rate/1000}kbps_N{modulator.modulation_mode}.wav', modualted_sig)
            # Generate the figure
            digimod_fig = modulator.digital_modulated_plot(digital_signal, x_axis_digital, t_axis, modualted_sig)

            digimod_dialog = GraphDialog(digimod_fig, self)  # Display digimod plot in a dialog
            digimod_dialog.exec_()

            if modulator.IQ_Return == True:
                IQplot_fig = modulator.IQ_plot(t_axis, modualted_sig, I_FC, Q_FC, I_SP, Q_SP, Dirac_Comb, RRC_delay)
                IQplot_dialog = GraphDialog(IQplot_fig, self)  # Display IQ plot in a dialog
                IQplot_dialog.exec_()

        except ValueError as e:
            # Show verbose error information for ValueErrors
            error_details = traceback.format_exc()  # Get the full traceback
            self.display_message(f"ValueError: {str(e)}\nDetails:\n{error_details}")
        except Exception as e:
            # Show verbose error information for any other exceptions
            error_details = traceback.format_exc()  # Get the full traceback
            self.display_message(f"Unexpected Error: {str(e)}\nDetails:\n{error_details}")

        self.display_message("Simulation completed successfully.")

class DemodulationDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("De-Modulation")
        self.setGeometry(100, 100, 1200, 1000)

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
        self.selected_channels = set()

        # Main layout
        self.main_layout = QVBoxLayout(self)

        # Channel Mode Section
        channel_mode_layout = QVBoxLayout()
        channel_mode_label = QLabel("Channel Mode:", font=font)
        channel_mode_layout.addWidget(channel_mode_label, alignment=Qt.AlignLeft)

        # Buttons for Channel Modes
        channel_mode_buttons_layout = QHBoxLayout()
        self.channel_buttons = {
            "AWGN": QPushButton("AWGN", self),
            "Fading": QPushButton("Fading", self),
            "Freq Drift": QPushButton("Freq Drift", self),
            "Freq Offset": QPushButton("Freq Offset", self),
            "Delay": QPushButton("Delay", self)
        }

        for name, button in self.channel_buttons.items():
            button.setFont(font)
            button.setFixedSize(150, 50)
            button.setProperty("selected", "false")
            button.clicked.connect(lambda checked, n=name: self.toggle_channel_button(n))
            channel_mode_buttons_layout.addWidget(button)

        channel_mode_buttons_layout.addStretch()
        channel_mode_layout.addLayout(channel_mode_buttons_layout)
        self.main_layout.addLayout(channel_mode_layout)

        # Scrollable Conditional Inputs
        """Scroll Container"""
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)

        self.scroll_container = QWidget()
        self.scroll_container.setStyleSheet("""
            background-color:rgb(71, 70, 70); /* Set the background color for the container */
        """)

        self.scroll_layout = QVBoxLayout(self.scroll_container)
        self.scroll_area.setWidget(self.scroll_container)
        
        """All Conditional Inputs"""
        self.conditional_inputs = {}

        # SNR Input for AWGN
        self.conditional_inputs["AWGN"] = self.create_input_layout("SNR of channel:", "Enter SNR (dB)")

        # Fading Inputs
        fading_layout = QVBoxLayout()
        self.fading_selection = QComboBox(self)
        self.fading_selection.setStyleSheet("""
            QComboBox {
                background-color: #ffffff;
                color: #000000;
                border: 1px solid #aaaaaa;
            }
        """)
        self.fading_selection.addItems(["Select Fading Type", "Rician", "Rayleigh"])
        self.fading_selection.setFont(font)
        self.fading_selection.currentTextChanged.connect(self.handle_fading_selection)
        fading_layout.addWidget(self.fading_selection)

        self.rician_input_layout = self.create_input_layout("Rician K Factor:", "Enter K Factor")
        self.rician_input_layout.hide()  # Hidden until "Rician" is selected
        fading_layout.addWidget(self.rician_input_layout)

        fading_widget = QWidget()
        fading_widget.setLayout(fading_layout)
        fading_widget.hide()  # Hide until Fading is selected
        self.conditional_inputs["Fading"] = fading_widget
        self.scroll_layout.addWidget(fading_widget)

        # Freq Drift Input
        self.conditional_inputs["Freq Drift"] = self.create_input_layout("Freq Drift Rate:", "Enter drift rate (Hz/sample)")

        # Freq Offset Input
        self.conditional_inputs["Freq Offset"] = self.create_input_layout("Freq Offset:", "Enter freq offset (Hz)")

        # Delay Input
        self.conditional_inputs["Delay"] = self.create_input_layout("Delay:", "Enter delay (samples fraction)")

        # Add all conditional inputs to the scroll layout
        for widget in self.conditional_inputs.values():
            self.scroll_layout.addWidget(widget)
            widget.hide()

        # Add scrollable area to the main layout
        self.main_layout.addWidget(self.scroll_area)

        # Bit Rate Section
        bitrate_layout = QHBoxLayout()
        bitrate_label = QLabel("Bit Rate:", font=font)
        self.bit_rate_input = QLineEdit(self)
        self.bit_rate_input.setPlaceholderText("Enter bit rate (bps)")
        self.bit_rate_input.setFont(font)
        self.bit_rate_input.setFixedWidth(400)
        bitrate_layout.addWidget(bitrate_label)
        bitrate_layout.addWidget(self.bit_rate_input)
        bitrate_layout.addStretch()
        self.main_layout.addLayout(bitrate_layout)

        """All Demodulation Modes"""
        # Demodulation Modes Section
        demodulation_layout = QVBoxLayout()
        demodulation_mode_label = QLabel("Demodulation Mode:", font=font)
        demodulation_layout.addWidget(demodulation_mode_label, alignment=Qt.AlignLeft)

        # Buttons for BPSK and QPSK
        bpsk_qpsk_layout = QHBoxLayout()
        self.bpsk_button = QPushButton("BPSK", self)
        self.bpsk_button.setFont(font)
        self.bpsk_button.setFixedSize(150, 50)
        self.bpsk_button.clicked.connect(lambda: self.display_message("BPSK selected"))

        self.qpsk_button = QPushButton("QPSK", self)
        self.qpsk_button.setFont(font)
        self.qpsk_button.setFixedSize(150, 50)
        self.qpsk_button.clicked.connect(lambda: self.display_message("QPSK selected"))

        bpsk_qpsk_layout.addWidget(self.bpsk_button)
        bpsk_qpsk_layout.addWidget(self.qpsk_button)
        bpsk_qpsk_layout.addStretch()
        demodulation_layout.addLayout(bpsk_qpsk_layout)

        # Buttons for QAM Modes
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
            button.clicked.connect(lambda checked, m=mode: self.display_message(f"{m} selected"))
            qam_layout.addWidget(button)
        qam_layout.addStretch()
        demodulation_layout.addLayout(qam_layout)
        self.main_layout.addLayout(demodulation_layout)

        # Run Demodulation Button
        self.run_demod_button = QPushButton("Run Demodulation", self)
        self.run_demod_button.setFont(font)
        self.run_demod_button.setFixedSize(300, 50)
        self.main_layout.addWidget(self.run_demod_button, alignment=Qt.AlignCenter)

        # Output Display (Terminal-like)
        self.output_display = QTextEdit(self)
        self.output_display.setFont(font)
        self.output_display.setReadOnly(True)
        self.output_display.setFixedHeight(200)
        self.main_layout.addWidget(self.output_display)


    def create_input_layout(self, label_text, placeholder_text):
        
        layout = QHBoxLayout()
        label = QLabel(label_text)
        label.setFont(QFont("SF Pro", 10))
        input_field = QLineEdit(self)
        input_field.setPlaceholderText(placeholder_text)
        input_field.setFont(QFont("SF Pro", 10))
        input_field.setFixedWidth(400)
        layout.addWidget(label)
        layout.addWidget(input_field)
        layout.addStretch()
        widget = QWidget()
        widget.setLayout(layout)
        return widget

    #toggling state
    def toggle_channel_button(self, channel_name):
        """Toggle the state of a channel button."""
        button = self.channel_buttons[channel_name]
        if button.property("selected") == "true":
            button.setProperty("selected", "false")
            button.setStyle(button.style())
            self.selected_channels.discard(channel_name)
            self.display_message(f"{channel_name} deselected")
            self.conditional_inputs[channel_name].hide()
        else:
            button.setProperty("selected", "true")
            button.setStyle(button.style())
            self.selected_channels.add(channel_name)
            self.display_message(f"{channel_name} selected")
            self.conditional_inputs[channel_name].show()

    #K factor input
    def handle_fading_selection(self, selection):
        """Handle the fading type selection."""
        if selection == "Rician":
            self.rician_input_layout.show()
        else:
            self.rician_input_layout.hide()
    
    def display_message(self, message):
        """Append a message to the output display."""
        self.output_display.append(message)


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
        self.demod_button.clicked.connect(self.open_demodulation_dialog)
        
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

    def open_demodulation_dialog(self):
        """Open the demodulation dialog."""
        if self.dialog is None:  # Ensure only one dialog instance
            self.dialog = DemodulationDialog()
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