import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
    QWidget,QPushButton, QLabel
)

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont
from PyQt5.QtGui import QIcon

import sys; import os; sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from Pages.ModulatorDialog import ModulationDialog
from Pages.DemodulatorDialog import DemodulationDialog
from Pages.EyeDiagramDialog import EyeDiagramDialog
from Pages.SNRBERDialog import SNRBERDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Continental Wireless Comms SimTool")
        self.setGeometry(0, 0, 1200, 1200)
        self.setWindowIcon(QIcon(r"GUIAssets\continental-logo-black-jumping-horse.png"))

        # Dark theme styling
        self.setStyleSheet("""
            QMainWindow { background-color: #1e1e1e; color: #ffffff; }
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
        self.mod_button = QPushButton("Modulator", self)
        self.mod_button.setFont(button_font)
        self.mod_button.setIcon(QIcon(r"GUIAssets/mod_icon.png"))
        self.mod_button.setIconSize(QSize(250, 250))
        self.mod_button.setFixedSize(600, 500)
        self.mod_button.setStyleSheet("""
            QPushButton {
                text-align: center; 
                padding-top: 75px; 
                font-size: 36px; /* Increased text size */
                font-weight: bold;
                color: #ffa500;
            }
        """)
        self.mod_button.clicked.connect(self.open_modulation_dialog)

        self.demod_button = QPushButton("Demodulator", self)
        self.demod_button.setFont(button_font)
        self.demod_button.setIcon(QIcon(r"GUIAssets/demod_icon.png"))
        self.demod_button.setIconSize(QSize(250, 250))
        self.demod_button.setFixedSize(600, 500)
        self.demod_button.setStyleSheet("""
            QPushButton {
                text-align: center; 
                padding-top: 75px; 
                font-size: 36px; /* Increased text size */
                font-weight: bold;
                color: #ffa500;
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
        self.snrber_button = QPushButton("SNR / BER", self)
        self.snrber_button.setFont(button_font)
        self.snrber_button.setIcon(QIcon(r"GUIAssets/snr_icon.png"))
        self.snrber_button.setIconSize(QSize(250, 250))
        self.snrber_button.setFixedSize(600, 500)
        self.snrber_button.setStyleSheet("""
            QPushButton {
                text-align: center; 
                padding-top: 75px; 
                font-size: 36px; 
                font-weight: bold;
                color: #ffa500;
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
                padding-top: 75px; 
                font-size: 36px; /* Increased text size */
                font-weight: bold;
                color: #ffa500;
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
            self.dialog = EyeDiagramDialog()
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

