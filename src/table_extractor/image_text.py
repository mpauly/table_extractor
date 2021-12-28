import os

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QKeyEvent, QPixmap
from PyQt5.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class ImageTextRowWidget(QWidget):
    def __init__(self, image, data, tess_config={}, keepfiles=True, **kwargs):
        super().__init__()

        self.data = data
        self.xcount = data.xcount
        self.ycount = data.ycount
        self.tess_config = tess_config
        self.keepfiles = keepfiles
        self.pagename = os.path.splitext(os.path.basename(image))[0]
        self.row = -1
        self.progress_bar = QProgressBar()
        self.counterLabel = QLabel()
        self.prev_button = QPushButton()
        self.prev_button.setText("Previous")
        self.prev_button.clicked.connect(self.prev_row)
        self.prev_button.setDisabled(True)
        self.next_button = QPushButton()
        self.next_button.setText("Next")
        self.next_button.clicked.connect(self.next_row)
        self.export_button = QPushButton()
        self.export_button.setText("Export")
        self.export_button.clicked.connect(self.export_data)
        layout = QHBoxLayout()
        self.widgets = []
        for i in range(self.ycount):
            widget = ImageTextWidget(i)
            widget.changed.connect(self.update_data)
            layout.addWidget(widget)
            self.widgets.append(widget)
        subwidget = QWidget()
        sublayout = QVBoxLayout()
        sublayout.addWidget(self.counterLabel)
        sublayout.addWidget(self.prev_button)
        sublayout.addWidget(self.next_button)
        sublayout.addWidget(self.export_button)
        subwidget.setLayout(sublayout)
        layout.addWidget(subwidget)
        self.setLayout(layout)
        self.next_row()

    def keyPressEvent(self, event):
        if type(event) == QKeyEvent:
            if event.key() == Qt.Key_Right:
                self.next_row()

    def update_data(self, iy):
        txt = self.widgets[iy].line_edit.text()
        try:
            self.data.store_data(self.row, iy, txt)
        except Exception:
            pass
        self.checkLine()

    def next_row(self):
        self.row += 1
        self.counterLabel.setText("{} / {}".format(self.row + 1, self.xcount))
        for iy in range(self.ycount):
            self.widgets[iy].load_image(
                self.row, iy, self.data.get_data_txt(self.row, iy)
            )
        self.updateButtons()

    def checkLine(self):
        error_lines = self.data.check_row(self.row)
        for iy in range(self.ycount):
            if iy in error_lines:
                self.widgets[iy].line_edit.setStyleSheet("border: 1px solid red;")
            else:
                self.widgets[iy].line_edit.setStyleSheet("border: 1px solid black;")

    def prev_row(self):
        self.row -= 1
        self.counterLabel.setText("{} / {}".format(self.row + 1, self.xcount))
        for iy in range(self.ycount):
            self.widgets[iy].load_image(
                self.row, iy, self.data.get_data_txt(self.row, iy)
            )
        self.updateButtons()
        self.checkLine()

    def updateButtons(self):
        if self.row <= 0:
            self.prev_button.setDisabled(True)
        else:
            self.prev_button.setDisabled(False)
        if self.row + 1 >= self.xcount:
            self.next_button.setDisabled(True)
        else:
            self.next_button.setDisabled(False)

    def export_data(self):
        print(
            "Exporting Data - wd: {} - target filename: {}".format(
                os.getcwd(), self.pagename
            )
        )
        if self.keepfiles:
            for xi in range(self.xcount):
                for yi in range(self.ycount):
                    txt = self.data.get_data_txt(xi, yi)
                    fi = open(
                        "{}/{}_{}_{}.gt.txt".format(
                            self.tess_config["training_dir"], self.pagename, yi, xi
                        ),
                        "w",
                    )
                    fi.write(txt)
                    fi.close()
        self.data.export(self.pagename)


class ImageTextWidget(QWidget):
    changed = pyqtSignal(int)
    path_original_imgs = "pics/original_{}_{}.png"
    path_cropped_imgs = "pics/cropped_{}_{}.png"

    def __init__(self, yi):
        super().__init__()

        self.yi = yi
        self.label_original_image = QLabel()
        self.label_cropped_image = QLabel()
        self.line_edit = QLineEdit()
        self.line_edit.textChanged.connect(lambda: self.changed.emit(yi))
        layout = QVBoxLayout()
        layout.addWidget(self.label_original_image)
        layout.addWidget(self.label_cropped_image)
        layout.addWidget(self.line_edit)
        self.setLayout(layout)

    def load_image(self, ix, iy, data):
        self.label_original_image.setPixmap(
            QPixmap(self.path_original_imgs.format(ix, iy))
        )
        self.label_cropped_image.setPixmap(
            QPixmap(self.path_cropped_imgs.format(ix, iy))
        )
        self.line_edit.setText(data)
