from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtWidgets import QWidget, QApplication, QLabel, QHBoxLayout
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import pyqtSignal, pyqtSlot, Qt, QObject, QThread
from custom_widgets import *
from qt_material import apply_stylesheet

import sys
import cv2
import numpy


# Subclass QMainWindow to customize your application's main window
class MainWindow(QWidget):
    def __init__(self):
        # For widget initialization
        super().__init__()

        # Window Parameters
        self.setWindowTitle("FocoBuddy")
        self.display_width = 640
        self.display_height = 480

        # Widgets
        self.image_label = QLabel(self)
        self.side_menu = SideMenu()

        # Window Setup
        hbox = QHBoxLayout()
        hbox.addWidget(self.image_label)
        hbox.addWidget(self.side_menu)
        self.setLayout(hbox)

        # Make video thread
        self.vThread = VideoThread()
        # Connect its signal to the update_image slot
        self.vThread.change_pixmap_signal.connect(self.update_image)
        self.vThread.start()

    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(
            rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format.Format_RGB888
        )
        p = convert_to_Qt_format.scaled(
            self.display_width,
            self.display_height,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.FastTransformation,
        )
        return QPixmap.fromImage(p)

    @pyqtSlot(numpy.ndarray)
    def update_image(self, cv_img):
        """Updates the image_label with a new opencv image"""
        qt_img = self.convert_cv_qt(cv_img)
        self.image_label.setPixmap(qt_img)

    def closeEvent(self, event):
        self.vThread.stop()
        event.accept


class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(numpy.ndarray)

    def __init__(self):
        super().__init__()
        self._run_flag = True

    def run(self):
        # capture from web cam
        cap = cv2.VideoCapture(0)
        while self._run_flag:
            ret, cv_img = cap.read()
            if ret:
                self.change_pixmap_signal.emit(cv_img)

    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
        self.wait()


if __name__ == "__main__":

    app = QApplication(sys.argv)
    apply_stylesheet(app, theme="dark_amber.xml")

    window = MainWindow()
    window.show()
    sys.exit(app.exec())
