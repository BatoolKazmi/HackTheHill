import sys
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QWidget,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
)
from PyQt6.QtGui import QIcon, QPalette, QColor


class Color(QWidget):
    def __init__(self, color):
        super(Color, self).__init__()
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(color))
        self.setPalette(palette)


class TimerPanel(QWidget):
    def __init__(self):
        super(TimerPanel, self).__init__()
        self.work_duration = 25 * 60  # 25 minutes in seconds
        self.break_duration = 5 * 60  # 5 minutes in seconds
        self.current_time = self.work_duration
        self.in_break = False  # Track if we're in a break session

        # Timer object
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)

        # Timer display
        self.time_display = QLabel(self.format_time(self.current_time), self)
        self.time_display.setStyleSheet("font-size: 30px; color: white;")
        self.time_display.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Buttons for the Pomodoro Timer
        self.start_button = QPushButton('Start')
        self.start_button.clicked.connect(self.start_timer)

        self.stop_button = QPushButton('Stop')
        self.stop_button.clicked.connect(self.stop_timer)

        self.reset_button = QPushButton('Reset')
        self.reset_button.clicked.connect(self.reset_timer)

        # Layout for the timer UI
        layout = QVBoxLayout()
        layout.addWidget(self.time_display)
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.reset_button)

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
            # Switch between work and break sessions
            if not self.in_break:
                self.current_time = self.break_duration
                self.in_break = True
                self.time_display.setText("Break Time!")
            else:
                self.current_time = self.work_duration
                self.in_break = False
                self.time_display.setText("Work Time!")

            # Restart the timer
            self.start_timer()

    def start_timer(self):
        """Starts the countdown."""
        self.timer.start(1000) 

    def stop_timer(self):
        """Stops the countdown."""
        self.timer.stop()

    def reset_timer(self):
        """Resets the timer to the initial work session."""
        self.timer.stop()
        self.current_time = self.work_duration
        self.in_break = False
        self.time_display.setText(self.format_time(self.current_time))


class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('FocoBuddy')
        self.setWindowIcon(QIcon('maps.ico'))
        self.resize(700, 500)  # width, height (the window size)

        # Create the main layout (Horizontal Layout)
        mainLayout = QHBoxLayout()

        # Create the timer panel layout
        timer_panel = TimerPanel()

        # Add the camera and timer panel layouts to the main layout
        mainLayout.addWidget(timer_panel)

        # Set the horizontal layout as the main layout
        self.setLayout(mainLayout)

        # Set styles for the main application window
        self.setStyleSheet('''
            QWidget {
                background-color: #5158ff; 
            }
            QPushButton, QLabel {
                color: black;  
            }
            QPushButton {
                background-color: #ffb3df;  
                color: black;
            }
            QPushButton::hover {
                background-color: #d260ff;
                color: white;
            }
        ''')


# Initialize the application
app = QApplication(sys.argv)
app.setStyleSheet('''
                  QWidget {
                  font-size: 5em;      
                  color: blue; 
                  }
                  QPushButton {
                    font-size: 10em;
                    background-color: yellow;   
                  }
''')

# Create the window
window = MyApp()
window.show()

# Execute event loop
app.exec()
