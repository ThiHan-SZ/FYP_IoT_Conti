from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLineEdit, QLabel, QTextEdit, QSlider, QFileDialog, QWidget, QScrollArea, QComboBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from traceback import format_exc

import sys; import os; sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from Simulator.SimulationClassCompact.SNRBERClass import SNRBERTest

from Simulator.GUI.Pages.GraphDialog import ScrollableGraphDialog

class SNRBERDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SNR / BER")
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
        section_font = QFont("SF Pro", 10)
        self.selected_channels = set()
        self.selected_modulations = []  # Store the selected modulation mode

        self.main_layout = QVBoxLayout(self)

        modulation_type_layout = QVBoxLayout()
        modulation_type_label = QLabel("Modem for SNR BER Test:", font=section_font)
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

        # Channel Mode Section
        channel_mode_layout = QVBoxLayout()
        channel_mode_label = QLabel("Channel Mode:", font=font)
        channel_mode_layout.addWidget(channel_mode_label, alignment=Qt.AlignLeft)

        # Buttons for Channel Modes
        channel_mode_buttons_layout = QHBoxLayout()
        self.channel_buttons = {
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


        # SNR Lower and Upper Bound Inputs
        snr_input_layout = QVBoxLayout()
        snr_label = QLabel("SNR Bounds:", font=section_font)
        snr_input_layout.addSpacing(20)
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
        
        # Noise Seed
        noise_generator_seed_layout = QVBoxLayout()
        noise_generator_seed_label = QLabel("Noise generator seed:", font=font)
        self.noise_generator_seed_input = QLineEdit(self)
        self.noise_generator_seed_input.setPlaceholderText("Enter Seed, leave blank for default seed")
        self.noise_generator_seed_input.setFont(font)
        self.noise_generator_seed_input.setFixedWidth(400)
        noise_generator_seed_layout.addWidget(noise_generator_seed_label)
        noise_generator_seed_layout.addWidget(self.noise_generator_seed_input)
        noise_generator_seed_layout.addStretch()
        snr_input_layout.addLayout(noise_generator_seed_layout)
        
        
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
            
            self.display_message(f"{mod_name} deselected")
        else:
            button.setProperty("selected", "true")
            button.setStyle(button.style())
            self.selected_modulations.add(mod_name)
            self.display_message(f"{mod_name} selected")

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
            
    def run_simulation(self):
        self.display_message("Simulation started")
        try:
            selected_modes = self.selected_modulations
            carrier_freq = self.carrier_freq_input.text()
            bit_rate = self.bit_rate_input.text()
            if not selected_modes:
                raise ValueError("No modulations selected. Please select at least one modulation.")
            if not bit_rate:
                raise ValueError("Bit rate not specified. Please enter a valid bit rate.")
            if not carrier_freq:
                raise ValueError("Carrier frequency not specified. Please enter a valid carrier frequency.")
            try:
                carrier_freq = int(carrier_freq)
                bit_rate = int(bit_rate)
            except ValueError:
                raise ValueError("Invalid bit rate or carrier frequency. Please enter valid integers.")
            
            snr_up,snr_down = self.snr_upper_input.text(), self.snr_lower_input.text()
            
            try:
                snr_up, snr_down = int(snr_up), int(snr_down)
            except ValueError:
                raise ValueError("Invalid SNR values. Please enter valid integers.")
            
            if snr_up < snr_down:
                raise ValueError("SNR upper limit must be greater than SNR lower limit")
            
            if not self.file_path:
                raise ValueError("No file selected. Please select a file for message input.")
            
            if not self.char_label.text() or not self.char_label.text().isdigit():
                raise ValueError("Invalid character count. Please enter a valid integer.")
            
            slicer = int(self.char_label.text())
            
            with open(self.file_path, 'r', encoding='utf-8') as file:
                message = file.read()[:slicer]
    
            seed = 1
            
            if self.noise_generator_seed_input.text():
                try:
                    seed = int(self.noise_generator_seed_input.text())
                except ValueError:
                    raise ValueError("Invalid seed value. Please enter a valid integer.")
                
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
            
            if channel_params:
                SNRBER_Test = SNRBERTest(selected_modes, bit_rate, carrier_freq, snr_up, snr_down, seed, self.selected_channels, channel_params)
            else:
                SNRBER_Test = SNRBERTest(selected_modes, bit_rate, carrier_freq, snr_up, snr_down, seed)
            
            figure = SNRBER_Test.plotSNRBER(message)
            GraphViewer = ScrollableGraphDialog(self)
            GraphViewer.add_figure(figure)
            GraphViewer.exec_()
            
            GraphViewer.clear_figures()
            SNRBER_Test = None # Clear the reference to the SNRBERTest object
            pass
        except ValueError as e:
            # Show verbose error information for ValueErrors
            error_details = format_exc()  # Get the full traceback
            self.display_message(f"ValueError: {str(e)}\nDetails:\n{error_details}")
        except Exception as e:
            # Show verbose error information for any other exceptions
            error_details = format_exc()  # Get the full traceback
            self.display_message(f"Unexpected Error: {str(e)}\nDetails:\n{error_details}")

    def display_message(self, message):
        self.output_display.append(message)    
