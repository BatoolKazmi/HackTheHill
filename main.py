from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtWidgets import (
    QWidget,
    QApplication,
    QLabel,
    QWidget,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QSystemTrayIcon,
    QSpinBox,
    QMessageBox,
    QAbstractSpinBox,
)
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import pyqtSignal, pyqtSlot, Qt, QTimer, QThread
from qt_material import apply_stylesheet

import sys
import time
import os
import cv2
import numpy
import matplotlib.pyplot as plt


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
        self.side_menu.setFixedSize(250, 500)
        self.diagram_btn = QPushButton("Result")
        self.diagram_btn.clicked.connect(self.show_results)

        # Window Setup
        hbox = QHBoxLayout()
        hbox.addWidget(self.image_label)
        hbox.addWidget(self.side_menu)
        hbox.addWidget(self.diagram_btn)
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

    def show_results(self):
        # window.image_label.hide()
        # window.side_menu.hide()
        self.vThread.plot_pie_chart()


class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(numpy.ndarray)

    def __init__(self):
        super().__init__()
        self._run_flag = True

    def run(self):
        # Open the capture
        directory = os.path.dirname(__file__)
        capture = cv2.VideoCapture(1)  # Camera
        if not capture.isOpened():
            print("Camera not opened.")
            return

        Value = 3

        # Load the model
        weights = os.path.join(directory, "assets/face_detection_yunet_2023mar.onnx")
        face_detector = cv2.FaceDetectorYN.create(weights, "", (0, 0))

        # Initialize timers for on-screen and off-screen states
        self.on_screen_time = 0  # Time in seconds the face was on screen
        self.off_screen_time = 0  # Time in seconds the face was off screen

        # Initialize previous state to None
        previous_state = None

        # Time counter for the last update
        last_update_time = time.time()

        try:
            while self._run_flag:
                start_time = time.time()
                duration = 5  # Duration to check gaze direction in seconds

                # To track the last states for S and A
                last_states = []

                while self._run_flag:
                    # Capture the frame and load the image
                    result, image = capture.read()
                    if not result:
                        print("Failed to capture image.")
                        break

                    # Convert image to 3-channel if it is not already
                    channels = 1 if len(image.shape) == 2 else image.shape[2]
                    if channels == 1:
                        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
                    if channels == 4:
                        image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)

                    # Set the input size
                    height, width, _ = image.shape
                    face_detector.setInputSize((width, height))

                    # Detect faces
                    _, faces = face_detector.detect(image)
                    faces = faces if faces is not None else []

                    closest_face = None
                    closest_y = float("inf")  # Start with a large value

                    # Find the closest face
                    for face in faces:
                        box = list(map(int, face[:4]))
                        y_coordinate = box[
                            1
                        ]  # Get the y-coordinate of the bounding box

                        if y_coordinate < closest_y:
                            closest_y = y_coordinate
                            closest_face = face

                    if closest_face is not None:
                        box = list(map(int, closest_face[:4]))
                        color = (0, 0, 255)
                        thickness = 2
                        cv2.rectangle(image, box, color, thickness, cv2.LINE_AA)

                        # Landmarks (right eye, left eye, nose)
                        landmarks = list(
                            map(int, closest_face[4 : len(closest_face) - 1])
                        )
                        landmarks = numpy.array_split(landmarks, len(landmarks) // 2)
                        right_eye = landmarks[0]
                        left_eye = landmarks[1]
                        nose = landmarks[2]  # Assuming the nose is the third landmark

                        # Draw eyes and nose
                        cv2.circle(
                            image,
                            tuple(right_eye),
                            5,
                            (0, 0, 255),
                            thickness,
                            cv2.LINE_AA,
                        )
                        cv2.circle(
                            image,
                            tuple(left_eye),
                            5,
                            (0, 0, 255),
                            thickness,
                            cv2.LINE_AA,
                        )
                        cv2.circle(
                            image, tuple(nose), 5, (255, 0, 0), thickness, cv2.LINE_AA
                        )

                        # Check if user is looking straight or away
                        if (
                            abs(right_eye[1] - left_eye[1]) < 10
                            and abs(nose[0] - ((right_eye[0] + left_eye[0]) // 2)) < 10
                        ):
                            current_state = "S"  # Look straight
                        else:
                            current_state = "A"  # Look away

                        last_states.append(current_state)

                        if len(last_states) > 5:
                            last_states.pop(0)

                        # Update the timer based on the current state
                        current_time = time.time()
                        time_elapsed = current_time - last_update_time

                        if current_state == "S":
                            self.on_screen_time += time_elapsed
                        elif current_state == "A":
                            self.off_screen_time += time_elapsed

                        last_update_time = current_time
                        previous_state = current_state

                    elapsed_time = time.time() - start_time
                    if elapsed_time >= duration:
                        if len(last_states) == 5 and all(
                            state == "S" for state in last_states
                        ):
                            Value = 1
                            print("Look straight", Value)
                            print(
                                f"Face has been off screen for: {time.strftime('%H:%M:%S', time.gmtime(self.off_screen_time))}"
                            )

                        elif len(last_states) == 5 and all(
                            state == "A" for state in last_states
                        ):
                            Value = 0
                            print("Look away", Value)
                            print(
                                f"Face has been on screen for: {time.strftime('%H:%M:%S', time.gmtime(self.on_screen_time))}"
                            )

                        last_states = []
                        start_time = time.time()

                    # cv2.imshow("face detection", image)

                    self.change_pixmap_signal.emit(cv2.flip(image, 1))

                    if cv2.waitKey(10) & 0xFF == ord("q"):
                        break

        except KeyboardInterrupt:
            self.plot_pie_chart()
            print(
                f"Face has been off screen for: {time.strftime('%H:%M:%S', time.gmtime(self.off_screen_time))}"
            )
            print(
                f"Face has been on screen for: {time.strftime('%H:%M:%S', time.gmtime(self.on_screen_time))}"
            )
            print("Program interrupted.")
        finally:
            capture.release()
            cv2.destroyAllWindows()

        # capture from web cam
        # cap = cv2.VideoCapture(1)
        # while self._run_flag:
        #     ret, cv_img = cap.read()
        #     if ret:
        #         self.change_pixmap_signal.emit(cv_img)

    def plot_pie_chart(self):
        # Prepare data for the pie chart
        labels = ["On Screen", "Off Screen"]
        sizes = [self.on_screen_time, self.off_screen_time]
        colors = ["#F6D0C9", "#DEDDE6"]

        # Create a pie chart
        plt.figure(figsize=(8, 6))
        plt.pie(
            sizes,
            labels=labels,
            colors=colors,
            autopct="%1.1f%%",
            startangle=140,
            wedgeprops={"linewidth": 1, "edgecolor": "white"},
        )
        plt.axis("equal")  # Equal aspect ratio ensures the pie chart is circular.
        plt.title("Face Detection Time Distribution", fontsize=16, fontweight="bold")

        # Remove grid and make the chart minimal
        plt.gca().set_facecolor("white")
        plt.gca().spines["top"].set_color("none")
        plt.gca().spines["right"].set_color("none")

        # Show the pie chart
        plt.show()

    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
        self.wait()


class SideMenu(QWidget):
    def __init__(self):
        super().__init__()

        self.tray_icon = QSystemTrayIcon(self)
        # Use a default icon if 'maps.ico' is not found
        try:
            self.tray_icon.setIcon(
                QIcon("maps.ico")
            )  # Replace with a valid path if you have one
        except Exception as e:
            print(f"Icon loading failed: {e}")
            self.tray_icon.setIcon(QIcon())  # Set a default icon

        self.tray_icon.setVisible(True)

        # Set the window icon
        try:
            self.setWindowIcon(QIcon("maps.ico"))
        except Exception as e:
            print(f"Window icon loading failed: {e}")
            self.setWindowIcon(QIcon())  # Set a default icon

        self.resize(700, 500)  # width, height (the window size)

        # Create the main layout (Vertical Layout)
        main_layout = QVBoxLayout()

        # Widgets
        timer_panel = Timer(self.tray_icon, self)

        # Add to layout
        main_layout.addWidget(timer_panel, alignment=Qt.AlignmentFlag.AlignCenter)

        # Set the horizontal layout as the main layout
        self.setLayout(main_layout)



class Timer(QWidget):
    def __init__(self, tray_icon, main_window):
        super(Timer, self).__init__()
        self.tray_icon = tray_icon  # Store the tray icon reference
        self.main_window = main_window  # Store the main window reference
        self.current_time = 0  # Initialize current time

        # 0: Waiting to start
        # 1: Started
        # 2: Paused
        self.analysis_state = 0

        # Timer object
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)

        # Work duration input
        self.min_field = self.TimeSpinBox(self)
        self.sec_field = self.TimeSpinBox(self)

        # Timer display
        self.time_display = QLabel(self.format_time(self.current_time), self)
        self.time_display.setFixedSize(200, 100)
        self.time_display.setStyleSheet("font-size: 30px; color: white;")
        self.time_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_display.hide()

        # Buttons for the timer

        # Start/Pause Button
        self.start_pause_button = QPushButton()
        self.start_pause_button.setIcon(QIcon("media/start.png"))
        self.start_pause_button.clicked.connect(self.start_pause_timer)
        self.start_pause_button.setFixedSize(50, 50)

        # Stop Button
        self.stop_button = QPushButton()
        self.stop_button.setIcon(QIcon("media/stop.png"))
        self.stop_button.clicked.connect(self.stop_timer)
        self.stop_button.setFixedSize(50, 50)

        # Reset Button
        self.reset_button = QPushButton()
        self.reset_button.setIcon(QIcon("media/reset.png"))
        self.reset_button.clicked.connect(self.reset_timer)
        self.reset_button.setFixedSize(50, 50)

        # Timer UI layout
        timer_layout = QVBoxLayout()

        # Timer Display layout
        self.timer_display_layout = QHBoxLayout()
        self.timer_display_layout.addWidget(self.time_display)
        self.timer_display_layout.addWidget(self.min_field)
        self.timer_display_layout.addWidget(self.sec_field)

        # Timer Control Layout
        timer_control_layout = QHBoxLayout()
        timer_control_layout.addWidget(self.stop_button)
        timer_control_layout.addWidget(self.start_pause_button)
        timer_control_layout.addWidget(self.reset_button)

        # Center all widgets in the layout
        timer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Add to Timer UI
        timer_layout.addLayout(self.timer_display_layout)
        timer_layout.addLayout(timer_control_layout)

        self.setLayout(timer_layout)

    def format_time(self, seconds):
        """Formats time in mm:ss."""
        minutes, secs = divmod(seconds, 60)
        return f"{minutes:02}:{secs:02}"

    def update_time(self):
        """Updates the timer every second."""
        if self.current_time > 0:
            self.current_time -= 1
            self.time_display.setText(self.format_time(self.current_time))
        else:
            self.analysis_state = 0
            # Change button icon
            self.start_pause_button.setIcon(QIcon("media/start.png"))

            # Show fields
            self.min_field.show()
            self.sec_field.show()

            # Hide display
            self.time_display.hide()
            self.timer.stop()
            self.show_notification("Work Time Ended!", "Time's up! Take a break!")
            # self.main_window.setStyleSheet("background-color: red;")  # Change background color

    def start_pause_timer(self):
        """Starts the countdown."""
        if self.analysis_state == 0:
            # Convert to seconds
            self.current_time = self.min_field.value() * 60 + self.sec_field.value()

        # Start Analyzing
        if (
            self.current_time != 0
            and self.analysis_state == 0
            or self.analysis_state == 2
        ):
            self.analysis_state = 1

            # Show Display
            self.time_display.show()

            # Hide input fields
            self.min_field.hide()
            self.sec_field.hide()

            # Change button icon
            self.start_pause_button.setIcon(QIcon("media/pause.png"))

            # Set and start
            self.time_display.setText(self.format_time(self.current_time))
            self.timer.start(1000)  # Start timer with 1 second interval
        # Pause Analysis
        elif self.analysis_state == 1:
            self.analysis_state = 2

            # Pause timer
            self.timer.stop()

            # Change button icon
            self.start_pause_button.setIcon(QIcon("media/start.png"))

    def stop_timer(self):
        """Stops the countdown and shows a notification."""
        if self.analysis_state != 0:
            self.analysis_state = 0

            # Show fields
            self.min_field.show()
            self.sec_field.show()

            # Hide display
            self.time_display.hide()

            self.timer.stop()
            self.show_notification("Timer Stopped", "The timer has been stopped.")

    def reset_timer(self):
        """Resets the timer to the user-defined duration."""
        self.current_time = self.min_field.value() * 60 + self.sec_field.value()
        self.time_display.setText(self.format_time(self.current_time))

    def show_notification(self, title, message):
        """Displays a notification dialog."""
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setText(message)
        msg_box.setWindowTitle(title)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()

    class TimeSpinBox(QSpinBox):
        def __init__(self, *args):
            QSpinBox.__init__(self, *args)

            # Limit to 0 - 60 min or sec
            self.setRange(0, 60)
            # Remove buttons
            self.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
            # Disable background autofill
            self.setAutoFillBackground(False)
            # Set a default value
            self.setValue(0)  # Default value
            # Set alignment to middle
            self.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            # Set size
            self.setFixedSize(100, 100)

            # Styling
            self.setStyleSheet("font: 30px")

        def textFromValue(self, value):
            return "%02d" % value


if __name__ == "__main__":

    app = QApplication(sys.argv)
    # apply_stylesheet(app, theme="dark_amber.xml")

    window = MainWindow()
    window.show()
    sys.exit(app.exec())
