import script.function as function

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QBrush, QPen
from PyQt5.QtWidgets import QWidget, QTabWidget, QLabel, QVBoxLayout, QAbstractItemView, QTableWidgetItem, QTableWidget, QTextEdit, QMessageBox


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

        self.setColumnCount(2)
        header = self.horizontalHeader()

        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        self.setHorizontalHeaderLabels(('Term', 'Count'))

        # self.verticalHeader().setVisible(False)

        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.resizeRowsToContents()

        self.data = []
        # TODO resize 시 한 줄에 두 개씩 보여주는 거

    def update_data(self, data):
        print('update_data in WordWidget |', data)
        self.data = data
        self.clearContents()

        self.setRowCount(len(self.data.keys()))
        self.setColumnCount(2)

        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        self.setHorizontalHeaderLabels(('Term', 'Count'))
        '''        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)'''
        for i, word in enumerate(self.data.keys()):
            item = QTableWidgetItem(word)
            item.setTextAlignment(Qt.AlignCenter)
            self.setItem(i, 0, item)
            item = QTableWidgetItem(str(len(self.data[word])))
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
        print('data_update')
        if option is None:
            print('exception')
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
        # view.setShowGrid(False)
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
        # print(self.size())


class TextWidget(QTextEdit):
    def __init__(self, parent=None):
        QTextEdit.__init__(self, parent)

    def dragEnterEvent(self, event):  # TODO
        if event.mimeData().hasFormat('text/plain'):
            event.accept()
        else:
            event.ignore()
        '''
        mime = event.mimeData()
        if mime.hasUrls():
            path = mime.urls()[0].toString()[8:]
            path = parse.unquote(path)
            if path[-5:] == '.docx' or path[-4:] == '.txt':
                event.accept()
            else:
                try:
                    with open(path, 'r') as f:
                        f.read()
                    event.accept()
                except (OSError, UnicodeDecodeError) as e:
                    print('Error Handle - dragEnter |', type(e).__name__, e)
                    event.ignore()
        elif mime.hasText():
            event.accept()
        '''

    def dropEvent(self, event):  # TODO
        if event.mimeData().hasFormat('text/plain'):
            QTextEdit.dropEvent(self, event)
        '''
        mime = event.mimeData()
        if mime.hasUrls():
            path = mime.urls()[0].toString()[8:]
            path = parse.unquote(path)
            if path[-5:] == '.docx':
                content = function.get_docx_text(path)
            elif path[-4:] == '.txt':
                with open(path, 'r') as f:
                    content = f.read()
            else:
                with open(path, 'r') as f:
                    content = f.read()
            if content is not None:
                reply = QMessageBox.question(self, 'Confirm Load',
                                             'Are you sure you want to erase current content and load new content?',
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    # TODO drag and drop -> cursor error
                    self.text.setText(content)
                    self.text.textCursor().setPosition(0)

        elif mime.hasText():
            QTextEdit.dropEvent(self, event)
        '''
