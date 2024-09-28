import sys # allows command line argument

from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QLineEdit, QVBoxLayout, QTextEdit
from PyQt6.QtGui import QIcon

class myApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('FocoBuddy')
        self.setWindowIcon(QIcon('maps.ico'))
        self.resize(500, 350) # width, height (the window size)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.inputField = QLineEdit()
        button = QPushButton("&Submit Please", clicked=self.sayHello)
        button.clicked.connect(self.sayHello)
        self.output = QTextEdit()

        layout.addWidget(self.inputField)
        layout.addWidget(button)
        layout.addWidget(self.output)

    def sayHello(self):
        inputText = self.inputField.text()
        self.output.setText('Hello {0}'.format(inputText))



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