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
        print('highlight')
        cursor = self.text.textCursor()
        cursor.select(QTextCursor.Document)
        cursor.setCharFormat(self.style['normal'])
        cursor.clearSelection()
        # print('highlight', data)
        for positions in data.values():
            for index, length in positions:
                cursor.setPosition(index)
                cursor.movePosition(QTextCursor.NextCharacter, mode=QTextCursor.KeepAnchor, n=length)
                cursor.setCharFormat(self.style['unfocus_group'])
                cursor.clearSelection()
        cursor.setCharFormat(self.style['normal'])

    def focus_change(self, data, word=None, focus=True):  # new test 갱신과 안 겹치게 lock 쓸 필요가 있을 듯
        if not self.able:
            return None
        print('focus_change')
        cursor = self.text.textCursor()
        pos = cursor.position()
        print('Pos | focus_change |', pos)
        if self.focus_word is not None and self.focus_word in data.keys():  # might not exist valid as key
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
        # print(self.focus_word)
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

    def change_state(self, word):  # TODO
        if not self.able:
            print('Change_state |', word)
            return None

    def reset(self):
        cursor = self.text.textCursor()
        cursor.select(QTextCursor.Document)
        cursor.setCharFormat(self.style['normal'])
        cursor.clearSelection()

# https://wiki.python.org/moin/PyQt/Python%20syntax%20highlighting
