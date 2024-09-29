from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtWidgets import QMainWindow, QWidget, QApplication, QLabel, QHBoxLayout, QPushButton, QVBoxLayout
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import pyqtSignal, pyqtSlot, Qt, QThread
from custom_widgets import *
from qt_material import apply_stylesheet

import sys
import cv2
import numpy


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Window Parameters
        self.setWindowTitle("FocoBuddy")
        self.display_width = 640
        self.display_height = 480

        # Central widget and layout
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # Widgets
        self.image_label = QLabel(self)
        self.side_menu = SideMenu()  # Pass the main window instance here

        # Window Setup
        hbox = QHBoxLayout()
        hbox.addWidget(self.image_label)
        hbox.addWidget(self.side_menu)
        self.central_widget.setLayout(hbox)

        # Make video thread
        self.vThread = VideoThread()
        self.vThread.change_pixmap_signal.connect(self.update_image)
        self.vThread.start()

    def open_page2(self):
        """Open Page 2 and hide the main window."""
        self.vThread.pause()  # Pause the video thread
        self.hide()  # Hide the main window
        self.page2 = Page2(self)  # Pass the main window instance to Page2
        self.page2.show()  # Show Page2

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
        event.accept()


class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(numpy.ndarray)

    def __init__(self):
        super().__init__()
        self._run_flag = True
        self._pause_flag = False

    def run(self):
        # Capture from web cam
        cap = cv2.VideoCapture(0)
        while self._run_flag:
            if not self._pause_flag:  # Only read frames if not paused
                ret, cv_img = cap.read()
                if ret:
                    self.change_pixmap_signal.emit(cv_img)

    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
        self.wait()

    def pause(self):
        """Pause the video feed"""
        self._pause_flag = True

    def resume(self):
        """Resume the video feed"""
        self._pause_flag = False


class Page2(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        super(Page2, self).__init__(parent)
        self.setWindowTitle("Page 2")

        layout = QVBoxLayout()

        label = QLabel("Additional information can go here.")
        layout.addWidget(label)

        # Button to go back to MainWindow
        back_button = QPushButton("Back to Main", self)
        back_button.clicked.connect(self.back_to_main)
        layout.addWidget(back_button)

        self.setLayout(layout)

    def back_to_main(self):
        """Close this page and return to MainWindow."""
        self.close()  # Close Page2
        self.main_window.vThread.resume()  # Resume video thread
        self.main_window.show()  # Show the original MainWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)
    apply_stylesheet(app, theme="dark_amber.xml")

    window = MainWindow()
    window.show()
    sys.exit(app.exec())
