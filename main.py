#!/bin/env python3
import sys

from PySide6.QtCore import Qt, Signal, Slot, QThread, QRect, QSize
from PySide6.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QLineEdit, QHBoxLayout, QVBoxLayout, QStyle, QTextEdit, QMessageBox

import httpx


class HtmlWorker(QThread):

    completed = Signal(httpx.Response)
    failed = Signal(object)

    def setUrl(self, url):
        self.url = url

    def run(self):
        try:
            resp = httpx.get(self.url, follow_redirects=True)
        except:
            self.failed.emit(sys.exc_info()[1])
        else:
            self.completed.emit(resp)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle('PySide6 Demo')
        rect = self.screen().geometry()
        size = self.size()
        self.setGeometry(QStyle.alignedRect(Qt.LayoutDirection.LeftToRight, Qt.AlignCenter, size, rect))

        self.htmlWorker = HtmlWorker()
        self.htmlWorker.completed.connect(self.showMessage)
        self.htmlWorker.failed.connect(self.showError)

        # ui
        widget = QWidget()
        self.setCentralWidget(widget)

        layout = QVBoxLayout()
        layout.addLayout(self.makeInputLayout())
        layout.addWidget(self.makeOutputWidget())
        widget.setLayout(layout)

    def makeInputLayout(self):
        self.edit = QLineEdit()
        self.btn = QPushButton('&Show Html')

        layout = QHBoxLayout()
        layout.addWidget(self.edit)
        layout.addWidget(self.btn)

        self.edit.returnPressed.connect(self.btn.click)
        self.btn.clicked.connect(self.fetchHtml)
        return layout

    def makeOutputWidget(self):
        self.output = QTextEdit()
        return self.output

    @Slot()
    def fetchHtml(self):
        if self.htmlWorker.isRunning():
            return
        url = self.edit.text()
        if not url:
            return
        self.output.clear()
        if not url.startswith('http'):
            url = 'https://' + url
        self.htmlWorker.setUrl(url)
        self.htmlWorker.start()

    @Slot(httpx.Response)
    def showMessage(self, resp):
        self.output.setPlainText(resp.text)

    @Slot(object)
    def showError(self, err):
        QMessageBox.warning(self, 'error', str(err))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
