from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLineEdit, QLabel, QTextEdit, QSlider, QFileDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from traceback import format_exc

import sys; import os; sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from Simulator.SimulationClassCompact.ModulationClass import Modulator as Mod
from Simulator.SimulationClassCompact.DemodulationClass import Demodulator as Demod
from Simulator.SimulationClassCompact.ChannelClass import SimpleGWNChannel_dB as AWGN

from Simulator.GUI.Pages.GraphDialog import ScrollableGraphDialog

import matplotlib.pyplot as plt
from numpy import arange, array, sum, abs 

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
        section_font = QFont("SF Pro", 12, QFont.Bold)
        self.selected_modulations = set()  

        self.main_layout = QVBoxLayout(self)

        modulation_type_layout = QVBoxLayout()
        modulation_type_label = QLabel("Modulation Types for SNR BER Test:", font=section_font)
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


        # SNR Lower and Upper Bound Inputs
        snr_input_layout = QVBoxLayout()
        snr_label = QLabel("SNR Bounds:", font=section_font)
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
            self.selected_modulations.discard(mod_name)
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
            
            # Initialize the MODEMS
            modulators = {mod: Mod(mod, bit_rate, carrier_freq) for mod in selected_modes}
            demodulators = {mod: Demod(mod, bit_rate, modulators[mod].sampling_rate) for mod in selected_modes}
            
            # Initialize dictionaries for modulated signals and BER
            modulated_signals = {mod: (None, None) for mod in selected_modes}
            ber_dict = {mod: [] for mod in selected_modes}
            
            fig, ax = plt.subplots(1, 1)
            
            snr_up,snr_down = self.snr_upper_input.text(), self.snr_lower_input.text()
            
            if not self.file_path:
                raise ValueError("No file selected. Please select a file for message input.")
            
            if not self.char_label.text() or not self.char_label.text().isdigit():
                raise ValueError("Invalid character count. Please enter a valid integer.")
            
            slicer = int(self.char_label.text())
            
            with open(self.file_path, 'r', encoding='utf-8') as file:
                message = file.read()[:slicer]
        
            try:
                snr_up, snr_down = int(snr_up), int(snr_down)
            except ValueError:
                raise ValueError("Invalid SNR values. Please enter valid integers.")
            
            if snr_up < snr_down:
                raise ValueError("SNR upper limit must be greater than SNR lower limit")
            
            snr_test_range = arange(snr_down, snr_up + 1)
                
            seed = 1
            
            if self.noise_generator_seed_input.text():
                try:
                    seed = int(self.noise_generator_seed_input.text())
                except ValueError:
                    raise ValueError("Invalid seed value. Please enter a valid integer.")
            
            ChannelDict = {snr: AWGN(snr, seed=seed) for snr in snr_test_range}
            
            comparison_string = array([int(bit) for bit in Mod.msgchar2bit_static(message)])
            
            total_iter = len(snr_test_range) * len(selected_modes)
            current_iter = 0
            
            for modulation_type in selected_modes:
                modulator = modulators[modulation_type]
                demodulator = demodulators[modulation_type]
                
                bit_string = modulator.msgchar2bit(message)
                time_axis, modulated_signal = modulator.modulate(bit_string)
                modulated_signals[modulation_type] = (time_axis, modulated_signal)
                
                for snr in snr_test_range:
                    current_iter += 1
                    self.display_message(f"Processing {modulation_type} at SNR {snr} dB ({current_iter/total_iter*100:.2f})%")
                    channel = ChannelDict[snr]
                    noisy_signal = channel.add_noise(modulated_signal)
                    demodulated_signal = demodulator.demodulate(noisy_signal)
                    demodulated_bits = demodulator.demapping(demodulated_signal)[1][:len(comparison_string)]
                    error_bits = sum(abs(comparison_string - demodulated_bits))
                    ber_dict[modulation_type].append(error_bits / len(bit_string))
                    
            # Set y-axis to symlog scale
            ax.set_yscale('symlog', linthresh=1e-5)
            # Custom ticks to include 0 and log-scale values
            ticks = [0, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1, 1]
            ax.set_yticks(ticks)

            ax.grid(which="both", linestyle='--', linewidth=0.5)
            
            from matplotlib.ticker import MultipleLocator; ax.xaxis.set_major_locator(MultipleLocator(1))

            colors = ['blue', 'orange', 'green', 'red', 'purple', 'brown', 'black']
            markers = ['o', 's', '^', 'v', '<', '>', 'd']

            for modulation_type, color, marker in zip(selected_modes, colors, markers):
                ax.plot(snr_test_range, ber_dict[modulation_type], label=modulation_type, color=color, marker=marker)

            ax.set_xlabel('SNR (dB)')
            ax.set_ylabel('BER')
            ax.set_title('BER vs SNR')
            ax.legend()
            
            ScrollableGraphDialog.add_figure(self, fig)
            
            self.display_message("BER vs SNR Plot completed successfully!")
            ScrollableGraphDialog.clear_figures(self)
            fig.clear()
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
