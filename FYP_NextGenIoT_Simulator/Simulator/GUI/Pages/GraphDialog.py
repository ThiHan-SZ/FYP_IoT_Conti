from PyQt5.QtWidgets import QDialog, QVBoxLayout, QWidget, QScrollArea
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class ScrollableGraphDialog(QDialog):
    def __init__(self, parent=None):
        """
        Initializes the ScrollableGraphDialog.

        Args:
            parent (QWidget, optional): The parent widget of the dialog. Defaults to None.

        This constructor sets up the dialog window with a title and geometry,
        creates a scrollable area containing a container widget, and adds a 
        vertical layout to organize the container. A scroll area is used to 
        allow for scrolling of the contents within the dialog.
        
        Use .add_figure() to add Matplotlib figures to the dialog.
        """
        super().__init__(parent)
        self.setWindowTitle("Graph Viewer")
        self.setGeometry(150, 150, 2400, 1500)

        # Create a scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        # Create a container widget for the scroll area
        self.container = QWidget()
        self.scroll_area.setWidget(self.container)

        # Create a layout for the container
        self.container_layout = QVBoxLayout()
        self.container.setLayout(self.container_layout)

        # Add the scroll area to the dialog
        dialog_layout = QVBoxLayout()
        dialog_layout.addWidget(self.scroll_area)
        self.setLayout(dialog_layout)

    def add_figure(self, figure):
        # Create a canvas for the figure
        canvas = FigureCanvas(figure)

        # Add the canvas to the container layout
        self.container_layout.addWidget(canvas)