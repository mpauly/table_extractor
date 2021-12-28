import glob
import os
import subprocess

import cv2
from PIL import Image
from PyQt5.QtCore import QPoint, Qt, pyqtSignal
from PyQt5.QtGui import QPainter, QPen, QPixmap
from PyQt5.QtWidgets import QWidget

from contour_filters import filter_contours
from datahandler import ImperialData
from line_estimator import horizontal_estimator, vertical_estimator


class GridChooser(QWidget):
    data_class = ImperialData
    VERTICAL = 0
    HORIZONTAL = 1
    stretch = 2
    padding_horizontal = 10
    padding_vertical = -10
    tess_config = {}
    path_original_imgs = "pics/original_{}_{}.png"
    path_cropped_imgs = "pics/cropped_{}_{}.png"
    processing = pyqtSignal(int)

    def __init__(self, image, debug=False, keepfiles=True, stretch=2, tess_config={}):
        super().__init__()
        self.image = image
        self.debug = debug
        self.stretch = stretch
        self.keepfiles = keepfiles
        self.tess_config = tess_config
        self.pagename = os.path.splitext(os.path.basename(self.image))[0]
        if self.keepfiles and not os.path.exists(self.tess_config["training_dir"]):
            os.makedirs(self.tess_config["training_dir"])

        if not os.path.exists("pics"):
            os.makedirs("pics")

        # delte old files
        for f in glob.glob(self.path_original_imgs.format("*", "*")):
            os.remove(f)
        for f in glob.glob(self.path_cropped_imgs.format("*", "*")):
            os.remove(f)

        self.pixmap = QPixmap(self.image)
        self.setFixedSize(
            int(self.pixmap.width() / self.stretch),
            int(self.pixmap.height() / self.stretch),
        )
        self.mode = self.VERTICAL
        self.lines_horizontal = horizontal_estimator(image)
        self.lines_vertical = vertical_estimator(image)

    def cell_count(self):
        return len(self.lines_horizontal) * len(self.lines_vertical)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.pixmap)
        painter.setPen(QPen(Qt.red, 3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        for x in self.lines_vertical:
            pt1 = QPoint(int(x / self.stretch), 0)
            pt2 = QPoint(int(x / self.stretch), self.pixmap.height())
            painter.drawLine(pt1, pt2)
        for y in self.lines_horizontal:
            pt1 = QPoint(0, int(y / self.stretch))
            pt2 = QPoint(self.pixmap.width(), int(y / self.stretch))
            painter.drawLine(pt1, pt2)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.mode == self.VERTICAL:
                self.lines_vertical.append(int(event.pos().x() * self.stretch))
            else:
                self.lines_horizontal.append(int(event.pos().y() * self.stretch))
            self.update()
        if event.button() == Qt.RightButton:
            self.delete_lines_close_to(
                event.pos().x() * self.stretch, event.pos().y() * self.stretch
            )
            self.update()

    def delete_lines_close_to(self, x, y):
        THRESHOLD = 10

        new_list = []
        for line in self.lines_horizontal:
            if abs(line - y) > THRESHOLD:
                new_list.append(line)
        self.lines_horizontal = new_list
        new_list = []
        for line in self.lines_vertical:
            if abs(line - x) > THRESHOLD:
                new_list.append(line)
        self.lines_vertical = new_list

    def recognize_text(self):
        self.lines_horizontal.sort()
        self.lines_vertical.sort()
        data = self.data_class(
            len(self.lines_horizontal) - 1, len(self.lines_vertical) - 1
        )
        self.image_file = Image.open(self.image)
        count = 0
        for yi, (y1, y2) in enumerate(
            zip(self.lines_horizontal[:-1], self.lines_horizontal[1:])
        ):
            for xi, (x1, x2) in enumerate(
                zip(self.lines_vertical[:-1], self.lines_vertical[1:])
            ):
                count += 1
                self.processing.emit(count)
                txt = self.recognize_cell(xi, yi, x1, x2, y1, y2)
                data.store_data(yi, xi, txt)
        return data

    def prepare_image(self, image_path):
        im = cv2.imread(image_path)

        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY_INV)

        contours, _hierarchy = cv2.findContours(
            binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE
        )

        filtered_contours = []

        filtered_contours = filter_contours(contours, im.shape)

        if len(filtered_contours) == 0:
            return None

        min_y, min_x, _ = im.shape
        max_x, max_y = 0, 0

        for con in filtered_contours:
            rect = cv2.boundingRect(con)
            min_x = min(rect[0], min_x)
            min_y = min(rect[1], min_y)
            max_x = max(max_x, rect[0] + rect[2])
            max_y = max(max_y, rect[1] + rect[3])

        padding = 2
        min_y = max(0, min_y - padding)
        min_x = max(0, min_x - padding)
        max_y = min(im.shape[0] - 1, max_y + padding)
        max_x = min(im.shape[1] - 1, max_x + padding)
        if self.debug:
            print("Image has dimensions {}".format(im.shape))
            print("  using x:({}, {}), y:({}, {})".format(min_x, max_x, min_y, max_y))
        imcut = im[min_y:max_y, min_x:max_x]
        return Image.fromarray(imcut)

    def recognize_cell(self, xi, yi, x1, x2, y1, y2):
        y11 = y1 + self.padding_vertical if not yi == 0 else y1
        y22 = (
            y2 - self.padding_vertical if not yi + 1 == len(self.lines_vertical) else y2
        )
        img = self.image_file.crop(
            (
                x1 + self.padding_horizontal,
                y11,
                x2 - self.padding_horizontal,
                y22,
            )
        )
        img_path = self.path_original_imgs.format(yi, xi)
        try:
            img.save(img_path)
        except SystemError:
            return ""
        if self.keepfiles:
            img_path_tess = "{}/{}_{}_{}.png".format(
                self.tess_config["training_dir"], self.pagename, yi, xi
            )
            img.save(img_path_tess)
        img = self.prepare_image(img_path)
        img_path = self.path_cropped_imgs.format(yi, xi)
        if img:
            img.save(img_path)
            txt = self.run_tesseract(img_path)
        else:
            txt = ""
        return txt

    def toggle_mode(self):
        self.mode = self.VERTICAL if self.mode == self.HORIZONTAL else self.HORIZONTAL
        return self.mode

    def run_tesseract(self, path):
        lang = self.tess_config.get("lang", "eng")
        tess_string = "tesseract -l {} --dpi 500 -c tessedit_char_whitelist=0123456789 --psm 7 {} stdout".format(
            lang, path
        )
        if self.debug:
            print("Running tesseract: {}".format(tess_string))
        kwargs = {}
        if "data" in self.tess_config:
            kwargs.update({"env": {"TESSDATA_PREFIX": self.tess_config["data"]}})
        result = subprocess.run(
            tess_string.split(" "),
            stdout=subprocess.PIPE,
            universal_newlines=True,
            **kwargs
        )
        return result.stdout.decode(encoding="ascii", errors="ignore").strip()
