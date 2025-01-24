from PyQt5.QtWidgets import QDialog, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

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