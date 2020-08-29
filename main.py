import json
import sys
import threading
import time
import ctypes
import os
import shutil

import script.function as function
import script.highlight as highlight

from PyQt5.uic import loadUiType
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import QMainWindow, QApplication, QFontDialog, QFileDialog, QMessageBox

import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tag import pos_tag
from nltk.tokenize import WordPunctTokenizer

gui_path = './data/gui/doublecross_gui.ui'
icon_path = './data/icon/icon.png'
search_data_path = './data/word/'
nltk_data_path = './data/nltk_data'

nltk.data.path.append(nltk_data_path)

form_class = loadUiType(gui_path)[0]

# import word or txt then no cursor in self.text, qtexteidt


class WindowClass(QMainWindow, form_class):
    version = '1.0'

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Check
        self.check_able = True
        self.checking_lock = threading.Lock()
        self.while_checking = None

        self.tokenizer = WordPunctTokenizer()
        self.lemmatizer = WordNetLemmatizer()

        threading.Thread(target=self.initial, daemon=True).start()

        self.stop_words = set(stopwords.words('english'))
        self.stop_words.update(['.', ',', ';', ':', '-'])

        # Icon
        myappid = f'DoubleCross {WindowClass.version}'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        self.setWindowIcon(QIcon(icon_path))

        # search data
        if not os.path.isdir(search_data_path):
            os.mkdir(search_data_path)

        # Timer
        self.rate = 1000  # ms
        self.timer = QTimer()
        self.timer.setInterval(self.rate)
        self.timer.timeout.connect(self.check)

        # ListWidget
        self.table_word.itemClicked.connect(lambda: self.choose_mistake('single'))
        self.table_word.itemDoubleClicked.connect(lambda: self.choose_mistake('double'))

        # Double
        self.double = {}

        # Highlighter
        self.highlighter = highlight.Highlighter(self.text)

        # Text binding
        self.text.textChanged.connect(self.text_change)
        self.text.cursorPositionChanged.connect(self.cursor_change)
        self.plain_text = ''
        self.text_font = QFont('Times New Roman', 20)
        self.text.document().setDefaultFont(self.text_font)

        # Search
        self.search_lock = threading.Lock()
        self.while_searching = False
        self.search.returnPressed.connect(self.search_data)
        self.tab_initial.setOpenExternalLinks(True)
        self.synonym.clicked.connect(self.change_option)
        self.antonym.clicked.connect(self.change_option)

        # Bar binding
        self.actionNew.triggered.connect(self.new)
        self.actionSave.triggered.connect(self.save)
        self.actionLoad.triggered.connect(self.load)
        self.actionExit.triggered.connect(self.exit)

        self.actionUndo.triggered.connect(self.text.undo)
        self.actionRedo.triggered.connect(self.text.redo)
        self.actionCut.triggered.connect(self.text.cut)
        self.actionCopy.triggered.connect(self.text.copy)
        self.actionPaste.triggered.connect(self.text.paste)
        self.actionSelect_All.triggered.connect(self.text.selectAll)

        self.actionCheck.triggered.connect(self.check)
        self.actionStart.triggered.connect(lambda: self.toggle_check(True))
        self.actionStop.triggered.connect(lambda: self.toggle_check(False))

        self.actionArialFont.triggered.connect(lambda: self.update_font(ask=False, font_name='Arial'))
        self.actionCalibriFont.triggered.connect(lambda: self.update_font(ask=False, font_name='Calibri'))
        self.actionGulimFont.triggered.connect(lambda: self.update_font(ask=False, font_name='Guilm'))
        self.actionTimesFont.triggered.connect(lambda: self.update_font(ask=False, font_name='Times New Roman'))
        self.actionSelectFont.triggered.connect(lambda: self.update_font())
        self.actionDelete_word_data.triggered.connect(self.delete_word_data)

        self.actionHowtouse.triggered.connect(self.how_to_use)
        self.actionAbout.triggered.connect(self.about)

        # Initial state
        self.splitter_main.setSizes([2000, 900])
        self.splitter_right.setSizes([100, 4000, 100, 4000])
        self.last_check = time.time()

    def initial(self):
        with self.checking_lock:
            self.while_checking = 'initialize'
        ti = time.time()
        self.lemmatizer.lemmatize('double', 'n')
        print('Lemmatizer initialize : ', time.time() - ti)
        self.status.update_color('red')
        with self.checking_lock:
            self.while_checking = None
        self.check()

    def toggle_check(self, command):
        print(command)
        with self.checking_lock:
            self.check_able = command
            self.highlighter.able = command
            print(self.text.textCursor())
            print('able', self.check_able)
        if not self.check_able:
            self.highlighter.reset()
        else:
            self.check()

    def search_data(self):
        with self.search_lock:
            if self.while_searching:
                return
            else:
                self.while_searching = True

        self.explain.exception_tab('Searching...')
        self.explain.repaint()
        word_data_path = search_data_path + f'{self.search.text()}.json'
        if os.path.isdir(word_data_path):
            with open(word_data_path, 'r') as file:
                self.explain.data_tab(json.load(file))
        else:
            response = function.get_thesaurus_data(self.search.text())
            if response is None:
                return None
            elif response[0]:
                with open(word_data_path, 'w') as file:
                    print(response[1])
                    json.dump(response[1], file)
                self.explain.data_tab(response[1])
            elif not response[0]:
                self.explain.exception_tab(response[1])
        with self.search_lock:
            self.while_searching = False

    def cursor_change(self):
        print('cursor_change')
        with self.checking_lock:
            if self.while_checking is not None:
                return
            else:
                self.while_checking = 'cursor_change'
        print('cursor', self.text.textCursor().position())
        self.highlighter.focus_change(self.double)
        with self.checking_lock:
            self.while_checking = None

    def text_change(self):
        # print('text_change')
        with self.checking_lock:
            if self.while_checking is not None or self.plain_text == self.text.toPlainText():
                return
            else:
                self.while_checking = 'text_change'
        print('Timer start')
        self.status.update_color('red')
        self.timer.start()
        with self.checking_lock:
            self.while_checking = None

    def choose_mistake(self, click_type):
        print('choose mistake')
        if click_type == 'single':
            word = self.table_word.item(self.table_word.currentRow(), 0).text()
            self.highlighter.focus_change(self.double, word, focus=False)
        elif click_type == 'double':
            word = self.table_word.item(self.table_word.currentRow(), 0).text()
            print(word, type(word))
            self.search.setText(word)
            # QCoreApplication.postEvent(self.search, QKeyEvent(QEvent.KeyPress, Qt.Key_Enter, Qt.NoModifier))
            self.highlighter.focus_change(self.double, word, focus=False)
        elif click_type == 'check':  # TODO
            pass

    def analytic_update(self, character, word, sentence):
        self.character.setText(f'Character : {character}')
        self.word.setText(f'Word : {word}')
        self.sentence.setText(f'Sentence : {sentence}')

    def check(self):
        print('check')
        with self.checking_lock:
            if self.check_able and self.while_checking is None:
                self.while_checking = 'check'
            else:
                return
        self.timer.stop()

        self.status.update_color('yellow')

        self.plain_text = self.text.toPlainText()

        if self.plain_text == '':
            self.analytic_update(0, 0, 0)
            self.double = {}
            self.table_word.update_data(self.double)
            self.status.update_color('green')
            with self.checking_lock:
                self.while_checking = None
            return
        else:
            character = len(self.plain_text)
            word = len(self.plain_text.split())
            sentence = self.plain_text.count('.')
            self.analytic_update(character, word, sentence)
        text = self.plain_text.splitlines()

        # print('text', text)

        tokenized_text = []

        line_index = 0

        for line in text:
            words = self.tokenizer.tokenize(line)
            tags = pos_tag(words)
            index = 0
            for word, tag in tags:
                index = line.find(word, index)
                word = word.lower()
                if word not in self.stop_words:
                    tokenized_text.append([self.lemmatizer.lemmatize(word, pos=function.match(tag)),
                                           function.match(tag), index + line_index, len(word)])
                index += len(word)
            line_index += len(line) + 1
        # print('tokenized_text', tokenized_text)
        grouped_text = {}
        for word, tag, index, length in tokenized_text:
            if word not in grouped_text:
                grouped_text[word] = [(index, length)]
            else:
                grouped_text[word].append((index, length))

        double = {}
        for word in grouped_text.keys():
            if len(grouped_text[word]) != 1:
                double[word] = grouped_text[word]
        # print('double', double)

        self.double = double
        self.highlighter.highlight(self.double)
        self.table_word.update_data(self.double)

        if len(double) == 0:
            self.status.update_color('green')
        else:
            self.status.update_color('red')

        with self.checking_lock:
            self.while_checking = None

    def update_font(self, ask=True, font_name=None):
        print('update_font')
        if ask:
            font, yes = QFontDialog().getFont()
            if yes:
                self.text_font = font
        else:
            if font_name is not None:
                self.text_font = QFont(font_name, self.text_font.pointSize())
        self.text.document().setDefaultFont(self.text_font)
        '''
        cursor = self.text.textCursor()
        self.text.selectAll()
        self.text.setCurrentFont(self.text_font)
        self.text.setTextCursor(cursor)
        '''

    def new(self):
        reply = QMessageBox.question(self, 'Confirm New',
                                     'Are you sure you want to erase current content?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.text.setText('')

    def save(self):
        path, extension = QFileDialog.getSaveFileName(self, 'Save File', '', "Text Files(*.txt)")
        if path != '':
            try:
                with open(path, 'w') as f:
                    f.write(self.text.toPlainText())
            except Exception as e:
                print('Error Handle - save |', type(e).__name__, e)

    def load(self):
        content = function.open_file()
        if content is not None:
            reply = QMessageBox.question(self, 'Confirm Load',
                                         'Are you sure you want to erase current content and load new content?',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.text.setText(content)
                self.text.textCursor().setPosition(0)

    def exit(self):
        reply = QMessageBox.warning(self, 'Confirm Exit', 'Are you sure you want to exit DoubleCross?',
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.destroy()

    def closeEvent(self, event):
        reply = QMessageBox.warning(self, 'Confirm Exit', 'Are you sure you want to exit DoubleCross?',
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def how_to_use(self):
        about = f'''Just try it
:)
Sorry for poor information
'''
        QMessageBox.information(self, 'About', about)

    def about(self):
        about = f'''DoubleCross {WindowClass.version}
License : MIT
Developer : Jeuk Hwang
Contact : https://github.com/PositivePeriod/DoubleCross
Word resource : https://www.thesaurus.com/
'''
        QMessageBox.information(self, 'About', about)

    def change_option(self):
        if self.synonym.isChecked():
            self.explain.change_option('synonyms')
        elif self.antonym.isChecked():
            self.explain.change_option('antonyms')
        else:
            print('Error; change_option')

    def delete_word_data(self):
        reply = QMessageBox.warning(self, 'Confirm Delete', 'Are you sure you want to delete saved word data?',
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            if os.path.isdir(search_data_path):
                shutil.rmtree(search_data_path)
            os.mkdir(search_data_path)


if __name__ == '__main__':
    # TODO update check
    # TODO optimize - tokenized_text, grouped_text, double
    # TODO 단어 추천 및 클릭으로 바꾸기 - naver dict 및 power thesaurus
    # TODO what's this - status bar / tooltip 추가 https://www.delftstack.com/ko/tutorial/pyqt5/pyqt5-menubar/
    # TODO stopword 원하면 넣을 수 있음 / 줄간격
    # TODO watermark
    '''
    python version : 3.8.5
    nltk version : 3.5
    PyQt version : 5.15.0
    '''
    app = QApplication(sys.argv)
    t = time.time()
    main_window = WindowClass()
    print('Init time:', time.time() - t)
    main_window.show()
    app.exec_()
