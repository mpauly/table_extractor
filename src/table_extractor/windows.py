from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from grid import GridChooser
from image_text import ImageTextRowWidget


class GridWindow(QMainWindow):
    def __init__(self, image, **kwargs):
        super().__init__()
        self.image = image
        self.config_kwargs = kwargs
        self.setWindowTitle("Grid")
        self.widget = GridChooser(image, **kwargs)
        mainwidget = QWidget()
        layout = QVBoxLayout()
        buttonwidget = QWidget()
        buttonlayout = QHBoxLayout()
        self.dir_label = QLabel()
        self.dir_label.setText("vertical")
        self.progressbar = QProgressBar()
        next_button = QPushButton()
        next_button.setText("Recognize")
        next_button.clicked.connect(self.recognize_text)
        buttonlayout.addWidget(self.dir_label)
        buttonlayout.addWidget(self.progressbar)
        buttonlayout.addWidget(next_button)
        buttonwidget.setLayout(buttonlayout)
        layout.addWidget(buttonwidget)
        scroll = QScrollArea()
        scroll.setWidget(self.widget)
        layout.addWidget(scroll)
        mainwidget.setLayout(layout)

        self.widget.processing.connect(self.reportProgress)

        self.setCentralWidget(mainwidget)

    def reportProgress(self, val):
        self.progressbar.setValue(val)

    def keyPressEvent(self, event):
        if type(event) == QKeyEvent:
            if event.key() == Qt.Key_Shift:
                current = self.widget.toggle_mode()
                if current == self.widget.HORIZONTAL:
                    self.dir_label.setText("horizontal")
                else:
                    self.dir_label.setText("vertical")
            if event.key() == Qt.Key_Return:
                self.recognize_text()

    def recognize_text(self):
        self.progressbar.setMaximum(self.widget.cell_count())
        data = self.widget.recognize_text()
        self.close()
        self.next = DetailWindow(self.image, data, **self.config_kwargs)


class DetailWindow(QMainWindow):
    def __init__(self, image, data, **kwargs):
        super().__init__()
        self.data = data

        self.setWindowTitle("Detail")
        self.widget = ImageTextRowWidget(image, data, **kwargs)

        self.setCentralWidget(self.widget)
        self.show()
