import sys
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QDialog, QVBoxLayout, QHBoxLayout, 
    QWidget,QPushButton, QLineEdit, QLabel, QTextEdit, QCheckBox, 
    QMessageBox, QFileDialog,QScrollArea,QComboBox,QGridLayout,QDial,QSlider
)

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont
from PyQt5.QtGui import QIcon

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
        
        # File Name Input (Hidden by default)
        self.file_name_input = QLineEdit(self)
        self.file_name_input.setPlaceholderText("Enter file name (e.g., signal.wav)")
        self.file_name_input.setFont(font)
        self.file_name_input.setVisible(False)  # Hidden by default
        main_layout.addWidget(self.file_name_input)

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
        self.file_name_input.setVisible(self.save_signal)  # Show or hide the file name input

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
        self.bpsk_button.clicked.connect(lambda: self.select_demod_mode("BPSK"))

        self.qpsk_button = QPushButton("QPSK", self)
        self.qpsk_button.setFont(font)
        self.qpsk_button.setFixedSize(150, 50)
        self.qpsk_button.clicked.connect(lambda: self.select_demod_mode("QPSK"))

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
            button.clicked.connect(lambda checked, m=mode: self.select_demod_mode(m))
            qam_layout.addWidget(button)
        qam_layout.addStretch()
        demodulation_layout.addLayout(qam_layout)
        self.main_layout.addLayout(demodulation_layout)

        # File Selection Section
        file_selection_layout = QHBoxLayout()
        file_label = QLabel("No file selected", self)
        file_label.setFont(font)
        file_button = QPushButton("Select File", self)
        file_button.setFont(font)
        file_button.setFixedSize(200, 40)

        # file selection logic
        def select_file():
            file_dialog = QFileDialog(self)
            file_path, _ = file_dialog.getOpenFileName(self, "Select a File", "", "All Files (*);;Text Files (*.txt)")
            #truncate name
            if file_path:
                max_length = 60  
                if len(file_path) > max_length:
                    truncated_path = f"...{file_path[-max_length:]}"  
                else:
                    truncated_path = file_path
                file_label.setText(truncated_path)
            else:
                file_label.setText("No file selected")


        file_button.clicked.connect(select_file)

        file_selection_layout.addWidget(file_label)
        file_selection_layout.addSpacing(20)
        file_selection_layout.addWidget(file_button)
        file_selection_layout.addStretch()
        self.main_layout.addLayout(file_selection_layout)

        # Run Demodulation Button
        self.run_button = QPushButton("Run Simulation", self)
        self.run_button.setFont(font)
        self.run_button.setFixedSize(300, 50)
        self.run_button.clicked.connect(self.run_simulation) #connect to handler
        self.main_layout.addWidget(self.run_button, alignment=Qt.AlignCenter)

        # Output Display (Terminal-like)
        self.output_display = QTextEdit(self)
        self.output_display.setFont(font)
        self.output_display.setReadOnly(True)
        self.output_display.setFixedHeight(200)
        self.main_layout.addWidget(self.output_display)

    def select_demod_mode(self,mode):
        """Set selected demod mode and update display"""
        self.selected_mode = mode
        self.display_message(f"Selected Demodulation Mode: {self.selected_mode}")

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
        if selection == "Rician":
            self.rician_input_layout.show()
        else:
            self.rician_input_layout.hide()
    
    def display_message(self, message):
        self.output_display.append(message)

    def run_simulation(self):
        try:
            if not self.selected_mode:
                self.display_message("Error: Please select a demodulation mode.")
                return

            if not self.bit_rate_input.text():
                self.display_message("Error: Please enter a bit rate.")
                return
            bit_rate = int(self.bit_rate_input.text())

            if not self.selected_channels:
                self.display_message("Error: Please select at least one channel mode.")
                return

            if not self.file_label.text() or self.file_label.text() == "No file selected":
                self.display_message("Error: Please select a file.")
                return

            # Collect dynamic parameters (e.g., AWGN SNR, Freq Drift)
            channel_params = {}
            for channel, widget in self.conditional_inputs.items():
                if widget.isVisible():
                    input_field = widget.findChild(QLineEdit)
                    if input_field and input_field.text().strip():
                        channel_params[channel] = float(input_field.text().strip())

            # Initialize Demodulator
            demodulator = Demodulator()

            # Run demodulation
            

            # Display the results
            self.display_message("Demodulation complete!")
            
        except ValueError as e:
            self.display_message(f"ValueError: {str(e)}")
        except Exception as e:
            error_details = traceback.format_exc()
            self.display_message(f"Unexpected Error: {str(e)}\nDetails:\n{error_details}")


        
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
        self.char_slider.setRange(1, 100)  #1000 - 100000
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

        self.char_label = QLabel("1000", self)
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
            """Map slider value to increments of 1000"""
            char_count = value * 1000  
            self.char_label.setText(f"{char_count:,}") 

    def run_simulation(self):
        self.display_message("Simulation started")

    def display_message(self, message):
        self.output_display.append(message)    

class EyediagDialog(QDialog):
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

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Continental Wireless Comms SimTool")
        self.setGeometry(0, 0, 1200, 1200)
        self.setWindowIcon(QIcon(r"GUIAssets\continental-logo-black-jumping-horse.png"))

        # Dark theme styling
        self.setStyleSheet("""
            QMainWindow { background-color: #2e2e2e; color: #ffffff; }
            QLabel { color: #ffffff; font-weight: bold; font-size: 30px; }
            QPushButton { 
                background-color: #4e4e4e; 
                border-radius: 10px; 
                color: #ffffff; 
                padding: 20px; 
                font-size: 20px; 
                font-weight: bold; 
                text-align: center;
            }
            QPushButton:hover { background-color: #5e5e5e; }
        """)

        # Fonts
        header_font = QFont("SF Pro", 30, QFont.Bold)
        button_font = QFont("SF Pro", 18)

        # Central widget
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setAlignment(Qt.AlignTop)

        # SDR Mode Section
        main_layout.addSpacing(50)
        sdr_label = QLabel("SDR MODE")
        sdr_label.setFont(header_font)
        sdr_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(sdr_label)

        # Modulator and Demodulator Buttons
        sdr_layout = QHBoxLayout()
        self.mod_button = QPushButton("  Modulator", self)
        self.mod_button.setFont(button_font)
        self.mod_button.setIcon(QIcon(r"GUIAssets/mod_icon.png"))
        self.mod_button.setIconSize(QSize(250, 250))
        self.mod_button.setFixedSize(600, 500)
        self.mod_button.setStyleSheet("""
            QPushButton {
                text-align: center; 
                padding-top: 120px; 
                font-size: 36px; /* Increased text size */
                font-weight: bold;
            }
        """)
        self.mod_button.clicked.connect(self.open_modulation_dialog)

        self.demod_button = QPushButton("  Demodulator", self)
        self.demod_button.setFont(button_font)
        self.demod_button.setIcon(QIcon(r"GUIAssets/demod_icon.png"))
        self.demod_button.setIconSize(QSize(250, 250))
        self.demod_button.setFixedSize(600, 500)
        self.demod_button.setStyleSheet("""
            QPushButton {
                text-align: center; 
                padding-top: 120px; 
                font-size: 36px; /* Increased text size */
                font-weight: bold;
            }
        """)
        self.demod_button.clicked.connect(self.open_demodulation_dialog)

        sdr_layout.addWidget(self.mod_button)
        sdr_layout.addSpacing(50)
        sdr_layout.addWidget(self.demod_button)
        main_layout.addLayout(sdr_layout)

        # Performance Insights Section Header
        main_layout.addSpacing(50)
        perf_label = QLabel("PERFORMANCE INSIGHTS")
        perf_label.setFont(header_font)
        perf_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(perf_label)

        # SNR BER and Eye Diagram Buttons
        perf_layout = QHBoxLayout()
        self.snrber_button = QPushButton("  SNR BER", self)
        self.snrber_button.setFont(button_font)
        self.snrber_button.setIcon(QIcon(r"GUIAssets/snr_icon.png"))
        self.snrber_button.setIconSize(QSize(250, 250))
        self.snrber_button.setFixedSize(600, 500)
        self.snrber_button.setStyleSheet("""
            QPushButton {
                text-align: center; 
                padding-top: 120px; 
                font-size: 36px; 
                font-weight: bold;
            }
        """)
        self.snrber_button.clicked.connect(self.open_snrber_dialog)

        self.eyediag_button = QPushButton("Eye Diagram", self)
        self.eyediag_button.setFont(button_font)
        self.eyediag_button.setIcon(QIcon(r"GUIAssets/eye_icon.png"))
        self.eyediag_button.setIconSize(QSize(250, 250))
        self.eyediag_button.setFixedSize(600, 500)
        self.eyediag_button.setStyleSheet("""
            QPushButton {
                text-align: center; 
                padding-top: 120px; 
                font-size: 36px; /* Increased text size */
                font-weight: bold;
            }
        """)
        self.eyediag_button.clicked.connect(self.open_eyediag_dialog)

        perf_layout.addWidget(self.snrber_button)
        perf_layout.addSpacing(50)
        perf_layout.addWidget(self.eyediag_button)
        main_layout.addLayout(perf_layout)

        # Set central widget
        self.setCentralWidget(central_widget)

        self.dialog = None  # Dialog instance tracker

    def open_modulation_dialog(self):
        if self.dialog is None:
            self.dialog = ModulationDialog()
            self.dialog.finished.connect(self.on_dialog_closed)
            self.dialog.show()

    def open_demodulation_dialog(self):
        if self.dialog is None:
            self.dialog = DemodulationDialog()
            self.dialog.finished.connect(self.on_dialog_closed)
            self.dialog.show()

    def open_snrber_dialog(self):
        if self.dialog is None:
            self.dialog = SNRBERDialog()
            self.dialog.finished.connect(self.on_dialog_closed)
            self.dialog.show()

    def open_eyediag_dialog(self):
        if self.dialog is None:
            self.dialog = EyediagDialog()
            self.dialog.finished.connect(self.on_dialog_closed)
            self.dialog.show()

    def on_dialog_closed(self):
        """Reset dialog reference when closed."""
        self.dialog = None


# Application Entry Point
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

