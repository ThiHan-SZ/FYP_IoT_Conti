import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QPushButton, QLineEdit, QLabel, QWidget
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from testmodulator import SimpleModulator  # Import the renamed SimpleModulator class

class TestGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Test GUI - Sine Wave")
        self.setGeometry(100, 100, 800, 600)

        # Main widget and layout
        self.central_widget = QWidget()
        self.layout = QVBoxLayout()

        # Carrier frequency input
        self.freq_label = QLabel("Carrier Frequency (Hz):")
        self.layout.addWidget(self.freq_label)

        self.freq_input = QLineEdit()
        self.freq_input.setPlaceholderText("Enter carrier frequency (e.g., 10)")
        self.layout.addWidget(self.freq_input)

        # Generate button
        self.generate_button = QPushButton("Generate Sine Wave")
        self.generate_button.clicked.connect(self.generate_graph)
        self.layout.addWidget(self.generate_button)

        # Matplotlib canvas for displaying the graph
        self.canvas = FigureCanvas(None)  # Placeholder for the canvas
        self.layout.addWidget(self.canvas)

        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)

    def generate_graph(self):
        """Generate and display the sine wave graph."""
        try:
            # Get carrier frequency from input
            carrier_freq = float(self.freq_input.text())

            # Instantiate the modulator and generate the graph
            modulator = SimpleModulator(carrier_freq)
            fig = modulator.generate_sine_wave()

            # Update the canvas with the new figure
            self.canvas.figure = fig
            self.canvas.draw()
        except ValueError:
            self.freq_label.setText("Error: Please enter a valid number for the frequency.")

# Application entry point
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestGUI()
    window.show()
    sys.exit(app.exec_())
