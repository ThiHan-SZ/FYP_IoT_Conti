from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLineEdit, QLabel, QTextEdit, QSlider, QCheckBox, QFileDialog, QWidget, QComboBox, QScrollArea
)

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from traceback import format_exc

import sys; import os; sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from Simulator.SimulationClassCompact.ModulationClass import Modulator
from Simulator.SimulationClassCompact.DemodulationClass import Demodulator
import Simulator.SimulationClassCompact.ChannelClass as Channel

from Pages.GraphDialog import ScrollableGraphDialog

class EyeDiagramDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Eye Diagram")
        self.setGeometry(100, 100, 1200, 800)

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

        self.main_layout = QVBoxLayout(self)
        modulation_type_layout = QVBoxLayout()
        modem_label = QLabel("Modem Selection:", font=font)

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
        self.main_layout.addWidget(modem_label)
        self.main_layout.addLayout(modulation_type_layout)
        self.main_layout.addSpacing(50)

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
            background-color:rgb(50, 50, 50); /* Set the background color for the container */
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
                background-color: #8e8e8e;
                color: #000000;
                border: 1px solid #aaaaaa;
                border-radius: 5px;
            }
            QComboBox QAbstractItemView {
                border: 2px solid darkgray;
                border-radius: 5px;
                selection-background-color: lightgray;
                selection-color: black;
                background-color: #8e8e8e;
                color: #000000;
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
        

        self.rician_input_layout = self.create_input_layout("Rician K Factor:", "Enter K Factor (dB)")
        self.rician_input_layout.hide()  # Hidden until "Rician" is selected
        fading_layout.addWidget(self.rician_input_layout)
        self.conditional_inputs["K value"] = self.rician_input_layout

        # Freq Drift Input
        self.conditional_inputs["Freq Drift"] = self.create_input_layout("Freq Drift Rate:", "Enter drift rate (Hz/sample)")

        # Freq Offset Input
        self.conditional_inputs["Freq Offset"] = self.create_input_layout("Freq Offset:", "Enter freq offset (Hz)")

        # Delay Input
        self.conditional_inputs["Delay"] = self.create_input_layout("Delay:", "Enter delay (samples fraction) btw 0-1")

        # Add all conditional inputs to the scroll layout
        for widget in self.conditional_inputs.values():
            self.scroll_layout.addWidget(widget)
            widget.hide()

        # Add scrollable area to the main layout
        self.main_layout.addWidget(self.scroll_area)

        # Bit Rate and Carrier Frequency Inputs
        input_layout = QVBoxLayout()

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

        

        # Text File Select for Modulation
        # File Selection Section
        self.file_selection_layout = QHBoxLayout()
        self.file_label = QLabel("No file selected", self)
        self.file_path = None
        self.file_label.setFont(font)
        self.file_button = QPushButton("Select a .txt File", self)
        self.file_button.setFont(font)
        self.file_button.setFixedSize(250, 50)
                
        self.file_button.clicked.connect(self.select_file)

        self.file_selection_layout.addWidget(self.file_label)
        self.file_selection_layout.addSpacing(20)
        self.file_selection_layout.addWidget(self.file_button)
        self.file_selection_layout.addStretch()
        self.main_layout.addLayout(self.file_selection_layout)
        
        # **Character Slider Bar (Initially Hidden)**
        self.char_input_layout = QVBoxLayout()
        self.char_input_label = QLabel("Number of Input Characters:", font=font)
        self.char_input_layout.addWidget(self.char_input_label, alignment=Qt.AlignLeft)

        self.char_slider = QSlider(Qt.Horizontal, self)
        self.char_slider.setRange(0, 1)  
        self.char_slider.setSingleStep(1)
        self.char_slider.setValue(0)
        self.char_slider.setEnabled(False)  
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

        self.char_input_layout.addWidget(self.char_slider)
        self.char_input_layout.addWidget(self.char_label, alignment=Qt.AlignCenter)

        self.char_input_label.hide()
        self.char_slider.hide()
        self.char_label.hide()

        self.main_layout.addLayout(self.char_input_layout)
        self.setLayout(self.main_layout)

        # Constellation Plot Checkbox
        self.constellation_checkbox = QCheckBox("Enable Constellation Plot", self)
        self.constellation_checkbox.setFont(font)
        self.constellation_checkbox.stateChanged.connect(self.handle_constellation_checkbox)  # Connect to handler
        self.plot_constellation = False
        self.main_layout.addWidget(self.constellation_checkbox)

        # Run Button
        self.run_simulation_button = QPushButton("Run Eye Diagram Simulation", self)
        self.run_simulation_button.setFont(font)
        self.run_simulation_button.setFixedSize(500, 50)
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
                border-radius: 5px;
            }
        """)
        self.main_layout.addWidget(self.output_display)

        self.selected_mode = None  # Store the selected modulation mode

    def select_modulation_button(self, mode):
        # Reset all buttons
        for name, button in self.modulation_buttons.items():
            button.setProperty("selected", "false")
            button.setStyle(button.style())

        # Highlight the selected button
        button = self.modulation_buttons[mode]
        button.setProperty("selected", "true")
        button.setStyle(button.style())
        self.output_display.append(f"{mode} selected")
        
    def select_file(self):
        # File selection
        file_dialog = QFileDialog(self)
        file_path, _ = file_dialog.getOpenFileName(self, "Select a File", "", "Text Files (*.txt)")

        if file_path:
            max_length = 50
            truncated_path = f"...{file_path[-max_length:]}" if len(file_path) > max_length else file_path

            self.file_label.setText(truncated_path)
            self.file_path = file_path
            self.display_message("File Selection Successful")

            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    self.max_chars = len(content.strip())  

                    if self.max_chars > 0:
                        # slider range to max char
                        self.char_slider.setRange(1, self.max_chars)
                        self.char_slider.setValue(1)  
                        self.char_slider.setEnabled(True)

                        # Unhide the slider
                        self.char_input_label.show()
                        self.char_slider.show()
                        self.char_label.show()

                        self.update_char_label(1) 
                    else:
                        self.display_message("The selected file is empty. Please choose a different file.")
                        self.char_input_label.hide()
                        self.char_slider.hide()
                        self.char_label.hide()
            except Exception as e:
                self.display_message(f"Error reading the file: {str(e)}")
                self.file_label.setText("No file selected")
                self.file_path = None

                # Hide slider
                self.char_input_label.hide()
                self.char_slider.hide()
                self.char_label.hide()
        else:
            self.file_label.setText("No file selected")
            self.file_path = None

            # Hide slider 
            self.char_input_label.hide()
            self.char_slider.hide()
            self.char_label.hide()


    def disable_file_selection(self):
        if self.message_input.text():
            self.file_label.setText("No file selected")
            self.file_path = None

            if not self.file_disabled_notified: 
                self.display_message("Manual message input detected. File selection disabled.")
                self.file_disabled_notified = True  

            self.file_button.setDisabled(True) #Disables 
            self.file_button.setStyleSheet("background-color: #555; color: #999; border-radius: 5px;")

            # **Hide the character slider**
            self.char_input_label.hide()
            self.char_slider.hide()
            self.char_label.hide()  
        else:  
            self.file_button.setDisabled(False) #Enables
            self.file_button.setStyleSheet("background-color: #4e4e4e; color: white; border-radius: 5px;")  # Restore 
            self.file_disabled_notified = False  

    def update_char_label(self, value):
            """Update the character input label based on the dial value."""
            self.char_label.setText(str(value))
            
    def display_message(self, message):
        self.output_display.append(message)

    def select_modulation_mode(self, mode):
        self.selected_mode = mode
        self.display_message(f"Selected Modulation Mode: {self.selected_mode}")

    def create_input_layout(self, label_text, placeholder_text):
        layout = QHBoxLayout()
        label = QLabel(label_text)
        label.setFont(QFont("SF Pro", 10))
        input_field = QLineEdit(self)
        input_field.setStyleSheet("""
            QLineEdit {
                background-color: #5e5e5e;  /* Lighter gray */
                color: #ffffff;           /* White text */
                border-radius: 5px;       /* Rounded edges */
                padding: 5px;             /* Padding for better spacing */
            }
            QLineEdit:focus {
                border: 2px solid #2b8cff; /* Highlight border when focused */
            }
        """)
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

        if channel_name == "Fading":
            self.handle_fading_selection(self.fading_selection.currentText())
            
    #K factor input
    def handle_fading_selection(self, selection):
        if "Fading" not in self.selected_channels:
            self.rician_input_layout.hide()  # Ensure it stays hidden if "Fading" is not selected
            return
        
        if selection == "Rician":
            self.rician_input_layout.show()
        else:
            self.rician_input_layout.hide()
    def handle_constellation_checkbox(self, state):
            """Handle state change for Plot IQ checkbox."""
            self.plot_constellation = state == Qt.Checked
    def run_simulation(self):
        try:
            GraphViewer = ScrollableGraphDialog(self)
            if not self.selected_mode:
                self.display_message("Error: Please select a Modem mode.")
                return
            
            if not self.carrier_freq_input.text():
                self.display_message("Error: Please enter a carrier frequency.")
                return

            if not self.bit_rate_input.text():
                self.display_message("Error: Please enter a bit rate.")
                return

            if not self.file_path:
                self.display_message("Error: Please select a file to modulate to perfom Eye Diagram analysis.")
                return
            
            if not self.char_label.text() or not self.char_label.text().isdigit():
                raise ValueError("Invalid character count. Please enter a valid integer.")
            
            slicer = int(self.char_label.text())

            with open(self.file_path, 'r', encoding='utf-8') as file:
                message = file.read()[:slicer]
            
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

            carrier_freq = int(self.carrier_freq_input.text())
            bit_rate = int(self.bit_rate_input.text())
            mode = self.selected_mode #selected demod

            modulator = Modulator(mode, bit_rate, carrier_freq)
            demodulator = Demodulator(mode, bit_rate, modulator.sampling_rate)
            demodulator.plot_EyeDiagram = True #Set to true to plot eye diagram
            demodulator.plot_constellation = self.plot_constellation 
            bitstr = modulator.msgchar2bit(message)

            t_axis, signal = modulator.modulate(bitstr)

            # Apply selected channels
            if self.selected_channels:
               signal = Channel.ApplyChannels(self.selected_channels, channel_params, signal, modulator.sampling_rate)

            # Demodulate the signal
            demodulated_signal = demodulator.demodulate(signal)

            demodulator.ax = demodulator.plot_setup(demodulator.fig)
            demodulator.auto_plot(demodulated_signal)
            GraphViewer.add_figure(demodulator.fig)
            GraphViewer.exec_()
            GraphViewer.clear_figures()
            demodulator.fig.clear()

        except ValueError as e:
            # Show verbose error information for ValueErrors
            error_details = format_exc()  # Get the full traceback
            self.display_message(f"ValueError: {str(e)}\nDetails:\n{error_details}")
        except Exception as e:
            # Show verbose error information for any other exceptions
            error_details = format_exc()  # Get the full traceback
            self.display_message(f"Unexpected Error: {str(e)}\nDetails:\n{error_details}")