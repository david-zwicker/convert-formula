#!/usr/bin/env python2
""" This file contains a graphical application for converting code """

import sys, os
from PyQt4 import QtGui, QtCore

# add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.parser_line import ParserLine
from src.parser_text import ParserText
from src.formatter import Formatter
from src.language import LanguageMathematica, LanguagePython

class GUI(QtGui.QWidget):
    """ Class containing the graphical user interface """

    def __init__(self, parent=None):
        """ setup the application """
        QtGui.QWidget.__init__(self, parent)

        # parser setup
        self.line_parser = ParserLine(LanguageMathematica())
        self.text_parser = ParserText(LanguageMathematica())
        self.formatter = Formatter(LanguagePython(int2float=True))

        # Quit Button
        quitButton = QtGui.QPushButton('Close', self)
        self.connect(
            quitButton, QtCore.SIGNAL('clicked()'),
            QtGui.qApp, QtCore.SLOT('quit()')
       )
        convertButton = QtGui.QPushButton('Convert', self)
        self.connect(
            convertButton, QtCore.SIGNAL('clicked()'), self.onChanged
       )

        # Widgets
        self.matLabel = QtGui.QLabel('Mathematica Code:')
        self.matEdit = QtGui.QTextEdit()
        self.pyLabel = QtGui.QLabel('Python Code:')
        self.pyEdit = QtGui.QTextEdit()
        self.connect(
            self.matEdit, QtCore.SIGNAL('textChanged()'),
            self.onChanged
       )
        self.multilineCb = QtGui.QCheckBox('Support Multiple Lines', self)
        self.connect(
            self.multilineCb, QtCore.SIGNAL('stateChanged(int)'),
            lambda i:self.onChanged()
       )

        # Bottom Row
        bottomRow = QtGui.QHBoxLayout()
        bottomRow.addWidget(self.multilineCb)
        bottomRow.addStretch(1)
        bottomRow.addWidget(convertButton)
        bottomRow.addWidget(quitButton)

        # Complete Layout
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.matLabel)
        vbox.addWidget(self.matEdit)
        vbox.addWidget(self.pyLabel)
        vbox.addWidget(self.pyEdit)
        vbox.addLayout(bottomRow)

        # set layout
        self.setLayout(vbox)
        self.setWindowTitle('Mathematica to Python Converter')
        self.resize(500, 350)


    def onChanged(self):
        """ function doing the actual conversion """
        try:
            matCode = str(self.matEdit.toPlainText())

            if self.multilineCb.isChecked():
                self.text_parser.parse_text(matCode)
                pyCode = self.formatter(self.text_parser)

            else:
                matCode = ' '.join(matCode.splitlines())
                output = self.line_parser.parse_string(matCode)
                pyCode = self.formatter(output)

            self.pyEdit.setText(pyCode)
            self.pyLabel.setText('Python Code:')

        except Exception:
            if hasattr(self, 'pyLabel'):
                self.pyLabel.setText(
                    'Python Code <font color="#FF0000">(invalid)</font>:'
               )


# setup QT application
app = QtGui.QApplication(sys.argv)
window = GUI()
window.show()
window.raise_()

sys.exit(app.exec_())
