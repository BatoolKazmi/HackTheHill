import sys
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QWidget,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QSystemTrayIcon,
    QSpinBox,
    QMessageBox
)
from PyQt6.QtGui import QIcon, QPalette, QColor
from qt_material import apply_stylesheet

class Color(QWidget):
    def __init__(self, color):
        super(Color, self).__init__()
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(color))
        self.setPalette(palette)

class TimerPanel(QWidget):
    def __init__(self, tray_icon, main_window):
        super(TimerPanel, self).__init__()
        self.tray_icon = tray_icon  # Store the tray icon reference
        self.main_window = main_window  # Store the main window reference
        self.current_time = 0  # Initialize current time

        # Timer object
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)

        # Work duration input
        self.duration_input = QSpinBox(self)
        self.duration_input.setRange(1, 120)  # Allow user to set timer from 1 to 120 minutes
        self.duration_input.setSuffix(" min")  # Suffix for the input
        self.duration_input.setValue(25)  # Default value

        # Timer display
        self.time_display = QLabel(self.format_time(self.current_time), self)
        # self.time_display.setStyleSheet("font-size: 30px; color: black;")
        self.time_display.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Buttons for the timer
        self.start_button = QPushButton('Start')
        self.start_button.clicked.connect(self.start_timer)

        self.stop_button = QPushButton('Stop')
        self.stop_button.clicked.connect(self.stop_timer)

        self.reset_button = QPushButton('Reset')
        self.reset_button.clicked.connect(self.reset_timer)

        # Layout for the timer UI
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Set Work Duration:"))
        layout.addWidget(self.duration_input)
        layout.addWidget(self.time_display)
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.reset_button)

        # Center all widgets in the layout
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

    def format_time(self, seconds):
        """Formats time in mm:ss."""
        minutes, secs = divmod(seconds, 60)
        return f'{minutes:02}:{secs:02}'

    def update_time(self):
        """Updates the timer every second."""
        if self.current_time > 0:
            self.current_time -= 1
            self.time_display.setText(self.format_time(self.current_time))
        else:
            self.timer.stop()
            self.time_display.setText("Work Time Ended!")
            self.show_notification("Work Time Ended!", "Time's up! Take a break!")

    def start_timer(self):
        """Starts the countdown."""
        self.current_time = self.duration_input.value() * 60  # Convert minutes to seconds
        self.time_display.setText(self.format_time(self.current_time))
        self.timer.start(1000)  # Start timer with 1 second interval

    def stop_timer(self):
        """Stops the countdown and shows a notification."""
        self.timer.stop()
        self.show_notification("Timer Stopped", "The timer has been stopped.")
        self.time_display.setText("Timer Stopped")

    def reset_timer(self):
        """Resets the timer to the user-defined duration."""
        self.timer.stop()
        self.current_time = self.duration_input.value() * 60
        self.time_display.setText(self.format_time(self.current_time))

    def show_notification(self, title, message):
        """Displays a notification dialog."""
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setText(message)
        msg_box.setWindowTitle(title)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()

class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('FocoBuddy')

        self.tray_icon = QSystemTrayIcon(self)
        # Use a default icon if 'maps.ico' is not found
        try:
            self.tray_icon.setIcon(QIcon('maps.ico'))  # Replace with a valid path if you have one
        except Exception as e:
            print(f"Icon loading failed: {e}")
            self.tray_icon.setIcon(QIcon())  # Set a default icon

        self.tray_icon.setVisible(True)

        # Set the window icon
        try:
            self.setWindowIcon(QIcon('maps.ico'))
        except Exception as e:
            print(f"Window icon loading failed: {e}")
            self.setWindowIcon(QIcon())  # Set a default icon

        self.resize(700, 500)  # width, height (the window size)

        # Create the main layout (Horizontal Layout)
        mainLayout = QHBoxLayout()

        # Create the timer panel layout
        timer_panel = TimerPanel(self.tray_icon, self)

        # Center the timer panel in the main layout
        mainLayout.addWidget(timer_panel, alignment=Qt.AlignmentFlag.AlignCenter)

        # Set the horizontal layout as the main layout
        self.setLayout(mainLayout)

        # Set styles for the main application window
        # self.setStyleSheet('''
        #     QPushButton, QLabel {
        #         color: black;  
        #     }
        #     QPushButton {
        #         background-color: #ffb3df;  
        #         color: black;
        #     }
        #     QPushButton::hover {
        #         background-color: #d260ff;
        #         color: white;
        #     }
        # ''')

# Initialize the application
app = QApplication(sys.argv)
# app.setStyleSheet(''' 
#                   QWidget {
#                   font-size: 5em;      
#                   color: blue; 
#                   }
#                   QPushButton {
#                     font-size: 10em;
#                     background-color: yellow;   
#                   }
# ''')

# Create the window
window = MyApp()

# setup stylesheet
apply_stylesheet(app, theme='dark_amber.xml')

window.show()

# Execute event loop
app.exec()
