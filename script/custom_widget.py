import script.function as function

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QBrush, QPen
from PyQt5.QtWidgets import QWidget, QTabWidget, QLabel, QVBoxLayout, QAbstractItemView, QTableWidgetItem, QTableWidget, QTextEdit


class StatusWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        # Draw
        self.color = function.color_by_name('green')

    def update_color(self, color):
        self.color = function.color_by_name(color)
        self.repaint()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QPen(self.color, 8))
        painter.setBrush(QBrush(self.color))

        geometry = self.geometry()
        rad = min(geometry.width(), geometry.height()) // 2 - 11
        painter.drawEllipse(geometry.center().x() - rad, geometry.center().y() - rad, 2 * rad, 2 * rad)


class WordWidget(QTableWidget):
    def __init__(self, parent=None):
        QTableWidget.__init__(self, parent)

        self.setRowCount(1)
        self.setColumnCount(2)
        header = self.horizontalHeader()

        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        self.setHorizontalHeaderLabels(('Term', 'Count'))
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.resizeRowsToContents()

        self.data = []

    def update_data(self, data):
        self.data = data
        self.clear()

        self.setRowCount(len(self.data.keys()))
        self.setColumnCount(2)
        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        self.setHorizontalHeaderLabels(('Term', 'Count'))
        temp_data = sorted([(k, len(self.data[k])) for k in self.data.keys()], key=lambda x: x[1], reverse=True)
        for i, word in enumerate(temp_data):
            item = QTableWidgetItem(word[0])
            item.setTextAlignment(Qt.AlignCenter)
            self.setItem(i, 0, item)
            item = QTableWidgetItem(str(word[1]))
            item.setTextAlignment(Qt.AlignCenter)
            self.setItem(i, 1, item)


class ExplainWidget(QTabWidget):
    def __init__(self, parent=None):
        QTabWidget.__init__(self, parent)
        self.data = None
        self.option = 'synonyms'

    def exception_tab(self, data):
        self.clear()
        self.data = None
        self.addTab(ExplainTabbedWidget(None, data), ' ')

    def data_tab(self, data):
        self.clear()
        self.data = data
        for definition in self.data.keys():
            self.addTab(ExplainTabbedWidget(definition, self.data[definition], self.option), definition)

    def change_option(self, option):
        if self.option != option:
            self.option = option
            if self.data is not None:
                self.data_tab(self.data)


class ExplainTabbedWidget(QWidget):
    def __init__(self, definition, data, option=None, parent=None):
        QWidget.__init__(self, parent)
        self.definition = definition
        self.data = data
        self.data_update(option)

    def data_update(self, option):
        if option is None:
            label = QLabel(self.data)
            label.setAlignment(Qt.AlignCenter)
            vbox = QVBoxLayout()
            vbox.addWidget(label)
            self.setLayout(vbox)
            return

        label = QLabel(f'{self.data["pos"]} | {self.definition}', self)
        label.setAlignment(Qt.AlignHCenter)
        view = QTableWidget(len(self.data[option]), 2)
        view.setHorizontalHeaderLabels(('Similarity', 'Term'))
        header = view.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        view.verticalHeader().setVisible(False)
        view.setEditTriggers(QAbstractItemView.NoEditTriggers)
        for i, word in enumerate(self.data[option]):
            for j, info in enumerate([word[1], word[0]]):
                item = QTableWidgetItem(info)
                item.setTextAlignment(Qt.AlignCenter)
                view.setItem(i, j, item)

            color = 4
            similarity = abs(int(word[1]))
            if similarity == 100:
                color = 0
            elif 80 <= similarity < 100:
                color = 1
            elif 60 <= similarity < 80:
                color = 2
            elif 40 <= similarity < 60:
                color = 3
            color = function.color_list[f'red{color}']
            view.item(i, 0).setBackground(color)
        vbox = QVBoxLayout()
        vbox.addWidget(label)
        vbox.addWidget(view)
        self.setLayout(vbox)

    def resizeEvent(self, event):
        QWidget.resizeEvent(self, event)


class TextWidget(QTextEdit):
    def __init__(self, parent=None):
        QTextEdit.__init__(self, parent)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat('text/plain'):
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasFormat('text/plain'):
            QTextEdit.dropEvent(self, event)
