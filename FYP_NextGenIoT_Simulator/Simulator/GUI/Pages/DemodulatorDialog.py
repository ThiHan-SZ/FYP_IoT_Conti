from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLineEdit, QLabel, QTextEdit, QScrollArea, QComboBox, QFileDialog, QCheckBox
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from traceback import format_exc
import re

import sys; import os; sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from Pages.GraphDialog import ScrollableGraphDialog

from Simulator.SimulationClassCompact.DemodulationClass import Demodulator
import Simulator.SimulationClassCompact.ChannelClass as Channel


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
            background-color:#464646; /* Set the background color for the container */
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
        
        fading_widget = QWidget()
        fading_widget.setLayout(fading_layout)
        fading_widget.hide()  # Hide until Fading is selected
        self.scroll_layout.addWidget(fading_widget)

        self.fading_selection.addItems(["Select Fading Type", "Rician", "Rayleigh"])
        self.fading_selection.setFont(font)
        self.fading_selection.currentTextChanged.connect(self.handle_fading_selection)
        fading_layout.addWidget(self.fading_selection)
        self.conditional_inputs["Fading"] = self.fading_selection
        

        self.rician_input_layout = self.create_input_layout("Rician K Factor:", "Enter K Factor")
        self.rician_input_layout.hide()  # Hidden until "Rician" is selected
        fading_layout.addWidget(self.rician_input_layout)
        self.conditional_inputs["K value"] = self.rician_input_layout

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
        self.file_label = QLabel("No file selected", self)
        self.file_path = None
        self.file_label.setFont(font)
        file_button = QPushButton("Select File", self)
        file_button.setFont(font)
        file_button.setFixedSize(200, 40)

        # file selection logic
        def select_file():
            file_dialog = QFileDialog(self)
            file_path, _ = file_dialog.getOpenFileName(self, "Select a File", "", "All Files (*);;WAV Files (*.wav)")
            #truncate name
            if file_path:
                max_length = 60  
                if len(file_path) > max_length:
                    truncated_path = f"...{file_path[-max_length:]}"  
                else:
                    truncated_path = file_path
                regexstring = r"^vaw\.([0-9]{2,4})?[A-Z]{4}_spbk\d+_zHk\d+__[^\s]{1,16}__elif_(resu|tset)"
                # Regexstring is the reverse of ^(user|test)_file__([^\s]{1,16})__\d+kHz_\d+kbps_[A-Z]{4}(.[0-9]{2,4})?.wav
                # Reverse matching is done to match files faster
                if re.match(regexstring, file_path[::-1]):
                    self.file_label.setText(truncated_path)
                    self.file_path = file_path
                    self.display_message("File Selection Successful")
                else:
                    self.file_label.setText("Invalid File Selected")
                    self.display_message("Invalid File Selected")
            else:
                self.file_label.setText("No file selected")
                


        file_button.clicked.connect(select_file)

        file_selection_layout.addWidget(self.file_label)
        file_selection_layout.addSpacing(20)
        file_selection_layout.addWidget(file_button)
        file_selection_layout.addStretch()
        self.main_layout.addLayout(file_selection_layout)

        # Plot IQ and Constellation Checkbox
        self.plot_iq_checkbox = QCheckBox("Plot I and Q Components", self)
        self.plot_iq_checkbox.setFont(font)
        self.plot_iq_checkbox.stateChanged.connect(self.handle_plot_iq_checkbox)  
        self.plot_iq = False
        self.main_layout.addWidget(self.plot_iq_checkbox)
        
        self.constellation_checkbox = QCheckBox("Plot Constellation", self)
        self.constellation_checkbox.setFont(font)
        self.constellation_checkbox.stateChanged.connect(self.handle_constellation_checkbox)  # Connect to handler
        self.plot_constellation = False
        self.main_layout.addWidget(self.constellation_checkbox)

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
        
        self.selected_mode = None  # Store the selected modulation mode

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
        #self.conditional_inputs["Fading"] = selection
    
    def handle_plot_iq_checkbox(self, state):
        """Handle state change for Plot IQ checkbox."""
        self.plot_iq = state == Qt.Checked

    def handle_constellation_checkbox(self, state):
        """Handle state change for Plot IQ checkbox."""
        self.plot_constellation = state == Qt.Checked

    def display_message(self, message):
        self.output_display.append(message)

    def run_simulation(self):
        try:
            GraphViewer = ScrollableGraphDialog(self)
            
            if not self.bit_rate_input.text():
                self.display_message("Error: Please enter a bit rate.")
                return
            
            if not self.selected_mode:
                self.display_message("Error: Please select a demodulation mode.")
                return

            if not self.file_label.text() or self.file_label.text() == "No file selected":
                self.display_message("Error: Please select a file.")
                return

            if not self.selected_mode in self.file_label.text():
                self.display_message("Error: Please select a file that matches the selected demodulation mode or change demodulation mode.")
                return
            
            # Collect dynamic parameters (e.g., AWGN SNR, Freq Drift)
            channel_params = {}
            for channel, widget in self.conditional_inputs.items():
                if widget.isVisible():
                    text = None
                    input_field = widget.findChild(QLineEdit)
                    if not input_field: # Special case for combobox
                        text =  widget.currentText().strip()
                    if (input_field and input_field.text().strip()):
                        channel_params[channel] = float(input_field.text().strip())
                    elif text and text != "Select Fading Type":
                        channel_params[channel] = text
                    else:
                        self.display_message(f"Error: Please enter a valid value for {channel}.")
                        return

            bit_rate = int(self.bit_rate_input.text())
            mode = self.selected_mode #selected demod
            
            file_path = self.file_path

            sampling_rate, signal = Demodulator.readfile(file_path)
            

            # Initialize Demodulator
            demodulator = Demodulator(mode, bit_rate, sampling_rate)
            demodulator.plot_IQ = self.plot_iq
            demodulator.plot_constellation = self.plot_constellation

            # Apply channels if any
            if self.selected_channels:
                for channel, value in channel_params.items():
                    match channel:
                        case "AWGN":
                            AWGNChannel = Channel.SimpleGWNChannel_dB(SNR=value)
                            signal = AWGNChannel.add_noise(signal)
                            continue
                        case "Fading":
                            FlatFadingChannel = Channel.SimpleFlatFadingChannel(type=str(value).lower())
                            if value == "Rician":
                                assert "K value" in channel_params
                                FlatFadingChannel.rician_k = float(channel_params["K value"])
                            signal = FlatFadingChannel.add_fading(signal)
                            continue
                        case "Freq Drift":
                            FreqDriftChannel = Channel.SimpleFrequencyDriftChannel(frequency_drift_rate=value)
                            signal = FreqDriftChannel.add_drift(signal)
                            continue
                        case "Freq Offset":
                            FreqOffsetChannel = Channel.SimpleFrequencyOffsetChannel(frequency_offset=value)
                            signal = FreqOffsetChannel.add_offset(signal, sampling_rate)
                            continue
                        case "Delay":
                            DelayChannel = Channel.SimpleDelayChannel(delay=value)
                            signal = DelayChannel.add_delay(signal)
                            continue
                        case "K value":
                            # Case will only exist if Rician is selected but K is handled above
                            continue
                        case _:
                            raise ValueError(f"Invalid channel: {channel}")

            # Demodulate the signal
            demodulated_signal = demodulator.demodulate(signal)
            
            # Demapping the signal
            message, bit_array = demodulator.demapping(demodulated_signal)

            if self.plot_iq or self.plot_constellation:
                demodulator.ax = demodulator.plot_setup(demodulator.fig)
                demodulator.auto_plot(demodulated_signal)
                GraphViewer.add_figure(demodulator.fig)
                GraphViewer.exec_()
                GraphViewer.clear_figures()
                demodulator.fig.clear()
            
            self.display_message(f"Received Message: {message}")
            self.display_message(f"Number of Bits: {len(bit_array)}")
                
            # Display the results
            self.display_message("Demodulation complete!")

        except ValueError as e:
            self.display_message(f"ValueError: {str(e)}")
        except Exception as e:
            error_details = format_exc()
            self.display_message(f"Unexpected Error: {str(e)}\nDetails:\n{error_details}")