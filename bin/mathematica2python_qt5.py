#!/usr/bin/env python3
""" This file contains a graphical application for converting code """

import sys, os
from PyQt5 import QtGui, QtCore, QtWidgets

# add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.parser_line import ParserLine
from src.parser_text import ParserText
from src.formatter import Formatter
from src.language import LanguageMathematica, LanguagePython


class GUI(QtWidgets.QWidget):
    """ Class containing the graphical user interface """

    def __init__(self):
        """ setup the application """
        super().__init__()

        # parser setup
        self.line_parser = ParserLine(LanguageMathematica())
        self.text_parser = ParserText(LanguageMathematica())
        self.formatter = Formatter(LanguagePython(int2float=True))

        # Quit Button
        quitButton = QtWidgets.QPushButton("Close", self)
        quitButton.clicked.connect(QtWidgets.qApp.quit)
        convertButton = QtWidgets.QPushButton("Convert", self)
        convertButton.clicked.connect(self.onChanged)

        # Widgets
        self.matLabel = QtWidgets.QLabel("Mathematica Code:")
        self.matEdit = QtWidgets.QTextEdit()
        self.matEdit.textChanged.connect(self.onChanged)
        self.pyLabel = QtWidgets.QLabel("Python Code:")
        self.pyEdit = QtWidgets.QTextEdit()
        self.pyEdit.setReadOnly(True)

        self.multilineCb = QtWidgets.QCheckBox("Support Multiple Lines", self)
        self.multilineCb.stateChanged.connect(self.onChanged)

        # Bottom Row
        bottomRow = QtWidgets.QHBoxLayout()
        bottomRow.addWidget(self.multilineCb)
        bottomRow.addStretch(1)
        bottomRow.addWidget(convertButton)
        bottomRow.addWidget(quitButton)

        # Complete Layout
        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.matLabel)
        vbox.addWidget(self.matEdit)
        vbox.addWidget(self.pyLabel)
        vbox.addWidget(self.pyEdit)
        vbox.addLayout(bottomRow)

        # set layout
        self.setLayout(vbox)
        self.setWindowTitle("Mathematica to Python Converter")
        self.resize(500, 350)

    def onChanged(self):
        """ function doing the actual conversion """
        try:
            matCode = str(self.matEdit.toPlainText())

            if self.multilineCb.isChecked():
                self.text_parser.parse_text(matCode)
                pyCode = self.formatter(self.text_parser)

            else:
                matCode = " ".join(matCode.splitlines())
                output = self.line_parser.parse_string(matCode)
                pyCode = self.formatter(output)

            self.pyEdit.setText(pyCode)
            self.pyLabel.setText("Python Code:")

        except Exception:
            if hasattr(self, "pyLabel"):
                self.pyLabel.setText(
                    'Python Code <font color="#FF0000">(invalid)</font>:'
                )


# setup QT application
app = QtWidgets.QApplication(sys.argv)
window = GUI()
window.show()
window.raise_()

sys.exit(app.exec_())
