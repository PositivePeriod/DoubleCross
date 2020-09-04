import script.function as function

from PyQt5.QtGui import QTextCursor


class Highlighter:
    def __init__(self, text):
        self.text = text
        self.style = {'normal': function.text_format(bg='white', fg='black'),
                      'focus_word': function.text_format(bg=function.color_by_name('red'), fg='white'),
                      'focus_group': function.text_format(bg=function.color_by_name('yellow'), fg='white'),
                      'unfocus_group': function.text_format(bg=function.color_by_name('blue'), fg='white')}
        self.focus_word = None
        self.exception = []
        self.able = True

    def highlight(self, data):
        if not self.able:
            return None
        cursor = self.text.textCursor()
        cursor.select(QTextCursor.Document)
        cursor.setCharFormat(self.style['normal'])
        cursor.clearSelection()
        for positions in data.values():
            for index, length in positions:
                cursor.setPosition(index)
                cursor.movePosition(QTextCursor.NextCharacter, mode=QTextCursor.KeepAnchor, n=length)
                cursor.setCharFormat(self.style['unfocus_group'])
                cursor.clearSelection()
        cursor.setCharFormat(self.style['normal'])

    def focus_change(self, data, word=None, focus=True):
        if not self.able:
            return None
        cursor = self.text.textCursor()
        pos = cursor.position()
        if self.focus_word is not None and self.focus_word in data.keys():
            for index, length in data[self.focus_word]:
                cursor.setPosition(index)
                cursor.movePosition(QTextCursor.NextCharacter, mode=QTextCursor.KeepAnchor, n=length)
                cursor.setCharFormat(self.style['unfocus_group'])
                cursor.clearSelection()
        cursor.setCharFormat(self.style['normal'])

        if word is not None:
            self.focus_word = word
        else:
            self.focus_word = None
            flag = False
            for word, positions in data.items():
                for index, length in positions:
                    if index <= pos <= index+length:
                        self.focus_word = word
                        flag = True
                        break
                if flag:
                    break
        if self.focus_word is not None:
            for index, length in data[self.focus_word]:
                cursor.setPosition(index)
                cursor.movePosition(QTextCursor.NextCharacter, mode=QTextCursor.KeepAnchor, n=length)
                if focus and index <= pos <= index+length:
                    cursor.setCharFormat(self.style['focus_word'])
                else:
                    cursor.setCharFormat(self.style['focus_group'])
                cursor.clearSelection()
        cursor.setCharFormat(self.style['normal'])

    def reset(self):
        cursor = self.text.textCursor()
        cursor.select(QTextCursor.Document)
        cursor.setCharFormat(self.style['normal'])
        cursor.clearSelection()
