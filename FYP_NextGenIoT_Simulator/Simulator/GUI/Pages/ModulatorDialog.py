from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLineEdit, QLabel, QTextEdit, QCheckBox, QMessageBox, QFileDialog, QSlider
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

from Simulator.GUI.Pages.GraphDialog import ScrollableGraphDialog
from traceback import format_exc

import sys; import os; sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
import re


from Simulator.SimulationClassCompact.ModulationClass import Modulator
class ModulationDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modulation")  
        self.setGeometry(100, 100, 1200, 800)  

        ##### Auxillary Variables #####
        self.plot_iq = False
        self.save_signal = False
        self.file_disabled_notified = False
        self.file_path = None  
        self.max_chars = 0 

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

        font = QFont("SF Pro", 10)  

        # Main layout
        self.main_layout = QVBoxLayout()

        # Carrier Frequency
        carrier_layout = QHBoxLayout()
        carrier_label = QLabel("Carrier Frequency:", font=font)  
        self.carrier_freq_input = QLineEdit(self)  
        self.carrier_freq_input.setPlaceholderText("Enter carrier frequency (Hz)")
        self.carrier_freq_input.setFont(font)
        self.carrier_freq_input.setFixedWidth(400)
        carrier_layout.addWidget(carrier_label)
        carrier_layout.addWidget(self.carrier_freq_input)
        carrier_layout.addStretch()
        self.main_layout.addLayout(carrier_layout)

        # Input for Bit Rate
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

        # Modulation Mode
        modulation_layout = QVBoxLayout()
        modulation_mode_label = QLabel("Modulation Mode:", font=QFont("SF Pro", 10))  
        modulation_layout.addWidget(modulation_mode_label, alignment=Qt.AlignLeft)

        # Buttons for BPSK and QPSK 
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
        self.main_layout.addLayout(modulation_layout)

        # Message Input
        self.main_layout.addSpacing(20)
        self.message_label = QLabel("Input message/.txt file to Modulate: ", font=font)
        self.main_layout.addWidget(self.message_label)  
        self.message_input = QLineEdit(self)
        self.message_input.setPlaceholderText("Enter message to modulate")
        self.message_input.textChanged.connect(self.disable_file_selection)  
        self.message_input.setFont(font)
        self.main_layout.addWidget(self.message_input)

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

        # Save signal
        self.main_layout.addSpacing(20)
        self.save_checkbox = QCheckBox("Save Modulated Signal", self)
        self.save_checkbox.setFont(font)
        self.save_checkbox.stateChanged.connect(self.handle_save_checkbox)  
        self.main_layout.addWidget(self.save_checkbox)
        
        # File Name (Hidden)
        self.file_name_input = QLineEdit(self)
        self.file_name_input.setPlaceholderText("Enter file name (e.g., signal) [UP TO 16 Chars]")
        self.file_name_input.setFont(font)
        self.file_name_input.setVisible(False)  
        self.main_layout.addWidget(self.file_name_input)

        self.plot_iq_checkbox = QCheckBox("Plot I and Q Components", self)
        self.plot_iq_checkbox.setFont(font)
        self.plot_iq_checkbox.stateChanged.connect(self.handle_plot_iq_checkbox)  
        self.main_layout.addWidget(self.plot_iq_checkbox)

        # Run Simulation
        self.run_button = QPushButton("Run Simulation", self)
        self.run_button.setFont(font)
        self.run_button.setFixedSize(200, 50)
        self.run_button.clicked.connect(self.run_simulation)  
        self.main_layout.addWidget(self.run_button, alignment=Qt.AlignCenter)

        # Output Display 
        self.output_display = QTextEdit(self)
        self.output_display.setFont(font)
        self.output_display.setReadOnly(True)
        self.output_display.setFixedHeight(200)
        self.main_layout.addWidget(self.output_display)

        # Set the layout of the dialog
        self.setLayout(self.main_layout)
        self.selected_mode = None  

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
        self.file_name_input.setVisible(self.save_signal)  

    def handle_plot_iq_checkbox(self, state):
        """Handle state change for Plot IQ checkbox."""
        self.plot_iq = state == Qt.Checked

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
                                
    def run_simulation(self):
        try:
            # Get inputs
            carrier_freq = self.carrier_freq_input.text()
            bit_rate = self.bit_rate_input.text()
            message = self.message_input.text()

            # Validate inputs
            if not carrier_freq or not bit_rate or not self.selected_mode :
                self.display_message("Please provide all inputs and select a modulation mode.")
                return
            
            if (not self.message_input.text() and not self.file_path) or (self.message_input.text() and self.file_path):
                self.display_message("Please enter a message OR select a text file.")
                return

            carrier_freq = int(carrier_freq)
            bit_rate = int(bit_rate)

            # Initialize the modulator and perform calculations
            modulator = Modulator(self.selected_mode, bit_rate, carrier_freq)
            modulator.IQ_Return = self.plot_iq
            modulator.save_signal = self.save_signal
            bitstr = modulator.msgchar2bit(message)
            digital_signal, x_axis_digital = modulator.digitalsignal(bitstr)

            if modulator.IQ_Return == False:
                t_axis, modulated_sig = modulator.modulate(bitstr)
            else:
                t_axis, Shaped_Pulse, I_FC, Q_FC, I_SP, Q_SP, Dirac_Comb, RRC_delay = modulator.modulate(bitstr)
                modulated_sig = I_FC + Q_FC
            
            if modulator.save_signal == True:
                message = message.replace(" ", "_")
                filename = self.file_name_input.text()
                
                try:
                    if (len(filename) > 16) or (len(message) > 16 and not filename):
                        raise ValueError("PLEASE ENTER A FILE NAME WITH UP TO 16 CHARACTERS. [MESSAGE TOO LONG FOR DEFAULT MODE]")
                except ValueError as e:
                    self.display_message(e)
                    
                if "QAM" in modulator.modulation_mode:
                    save_mode = 'N'+modulator.modulation_mode
                else:
                    save_mode = modulator.modulation_mode
                    
                # If no name entered use default saving instructions, else use entered name
                
                if (not filename) or (" " in filename):
                    self.display_message(f"File saved with default mode: {message}")
                    modulator.save(f'user_file__{message}__{int(modulator.carrier_freq/1000)}kHz_{int(bit_rate/1000)}kbps_{save_mode}.wav', modulated_sig) 
                else:
                    self.display_message(f"File saved with named mode: {self.file_name_input.text()}")
                    modulator.save(f'user_file__{self.file_name_input.text()}__{int(modulator.carrier_freq/1000)}kHz_{int(bit_rate/1000)}kbps_{save_mode}.wav', modulated_sig)
            # Generate the figure
            GraphViewer = ScrollableGraphDialog(self)
            
            digitalAndMixed_fig = modulator.digital_modulated_plot(digital_signal, x_axis_digital, t_axis, modulated_sig)
            GraphViewer.add_figure(digitalAndMixed_fig)
            
            if modulator.IQ_Return == True:
                IQplot_fig = modulator.IQ_plot(t_axis, Shaped_Pulse, I_FC, Q_FC, I_SP, Q_SP, Dirac_Comb, RRC_delay)
                GraphViewer.add_figure(IQplot_fig)
            
            GraphViewer.exec_()
            GraphViewer.clear_figures()
            
                
        except ValueError as e:
            # Show verbose error information for ValueErrors
            error_details = format_exc()  # Get the full traceback
            self.display_message(f"ValueError: {str(e)}\nDetails:\n{error_details}")
        except Exception as e:
            # Show verbose error information for any other exceptions
            error_details = format_exc()  # Get the full traceback
            self.display_message(f"Unexpected Error: {str(e)}\nDetails:\n{error_details}")

        self.display_message("Simulation completed successfully.")