import sys # allows command line argument

from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QLineEdit, QVBoxLayout, QTextEdit
from PyQt6.QtGui import QIcon, QPalette, QColor

class Color(QWidget):

    def __init__(self, color):
        super(Color, self).__init__()
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(color))
        self.setPalette(palette)

class myApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('FocoBuddy')
        self.setWindowIcon(QIcon('maps.ico'))
        self.resize(500, 350) # width, height (the window size)

        camera = QVBoxLayout()
        toolPanel = QVBoxLayout()

        camera.addWidget(Color('#FCD6DC'))
        toolPanel.addWidget(Color('#1D1C21'))

        # Create a horizontal layout to place both the camera and toolPanel side by side
        mainLayout = QHBoxLayout()
        mainLayout.addLayout(camera)
        mainLayout.addLayout(toolPanel)

        # Shows everything together
        self.setLayout(mainLayout)





app = QApplication(sys.argv)
app.setStyleSheet('''
                  QWidget {
                  font-size: 5em;      
                  color: blue; 
                      
                  }

                  QPushButton{
                    font-size: 10em;
                    background-color: yellow;   
                  }
    
                  
                  
''')

window = myApp()
# window = QWidget();
# window = QPushButton() #CAN BE PUSH BUTTON!!!
window.show()

#execute event loop
app.exec()