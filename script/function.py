import json
import os
import zipfile
from urllib import request, error, parse

try:
    from xml.etree.cElementTree import XML
except ImportError:
    from xml.etree.ElementTree import XML

from PyQt5.QtGui import QColor, QTextCharFormat, QFont
from PyQt5.QtWidgets import QFileDialog, QWidget

color_list = {'red': QColor.fromRgb(237, 85, 59),
              'yellow': QColor.fromRgb(246, 213, 92),
              'green': QColor.fromRgb(39, 161, 108),
              'blue': QColor.fromRgb(32, 99, 155)}

for i, hex_string in enumerate(['#ed553b', '#f38e7c', '#f7b3a7', '#fad0c9', '#fde9e5']):
    color_list[f'red{i}'] = QColor(hex_string)
for i, hex_string in enumerate(['#578dbb', '#85aed1', '#a9c7e0', '#c9dcec', '#e5eef6']):
    color_list[f'blue{i}'] = QColor(hex_string)


def color_by_name(color):
    if color in color_list:
        return color_list[color]
    else:
        return QColor(color)


def match(tag):
    tag = tag[0].lower()
    if tag == 'j':
        return 'a'
    else:
        if tag in ['n', 'r', 'v']:
            return tag
        else:
            return 'n'


def text_format(bg, fg, style=''):
    if type(bg) == str:
        _bg_color = QColor(bg)
    else:
        _bg_color = bg
    if type(fg) == str:
        _fg_color = QColor(fg)
    else:
        _fg_color = fg
    _format = QTextCharFormat()
    _format.setBackground(_bg_color)
    _format.setForeground(_fg_color)
    if 'bold' in style:
        _format.setFontWeight(QFont.Bold)
    if 'italic' in style:
        _format.setFontItalic(True)
    return _format


def open_file():
    path, extension = QFileDialog.getOpenFileName(QWidget(), 'Open File', os.path.expanduser('~/Desktop'),
                                                  "All Files(*.*);; Word Files(*.docx);; Text Files(*.txt)")
    if path != '':
        if extension == 'Word Files(*.docx)' or path[-5:] == '.docx':
            content = get_docx_text(path)
        elif extension == 'Text Files(*.txt)' or path[-4:] == '.txt':
            with open(path, 'r', encoding='UTF-8') as f:
                content = f.read()
        else:
            try:
                with open(path, 'r', encoding='UTF-8') as f:
                    content = f.read()
            except (OSError, UnicodeDecodeError) as e:
                print('Error Handle - open file |', type(e).__name__, e)
                return None
        return content


def get_thesaurus_data(word, printf=False):
    word = word.strip()
    if len(word) == 0:
        return None
    word_url = parse.quote(word)
    url = f'https://www.thesaurus.com/browse/{word_url}'
    try:
        html = request.urlopen(url).read()
    except error.URLError as e:
        if str(e) == 'HTTP Error 404: Not Found':
            return [False, f'No searched data for {word}']
        elif str(e) == '<urlopen error [Errno 11001] getaddrinfo failed>':
            return [False, f'Check the internet connection']
        else:
            return [False, f'Unpredictable error\nNo searched data for {word}\nCheck for internet connection']

    # Parsing; index1 and index2 should be updated
    index1 = html.find(b'"posTabs":[')
    index2 = html.find(b'}],"synonyms":[', index1)
    if index2 == -1:
        return [False, f'No searched data for {word}']
    json_data = html[index1 + 10:index2 + 2]
    try:
        data = json.loads(json_data)
    except Exception as e:
        print('Error Handle - get_thesaurus_data', e)
        return [False, f'Error occurred while searching data for {word}']
    sorted_data = {}

    # Get data
    if printf:
        blacklist = []
        for x in data:
            sorted_data[x['definition']] = {'pos': x['pos'], 'synonyms': [], 'antonyms': []}
            print(f"definition | {x['definition']} / {x['pos']}")
            print(f"synonyms |", end=" ")
            for y in sorted(x['synonyms'], key=lambda w: (-int(w['similarity']), w['term'])):
                if y['isInformal'] == '0' and y['isVulgar'] is None:
                    print(f"{y['term']} {y['similarity']} /", end=" ")
                    sorted_data[x['definition']]['synonyms'].append((y['term'], y['similarity']))
                else:
                    blacklist.append(y)

            print()
            print(f"antonyms |", end=" ")
            for y in sorted(x['antonyms'], key=lambda w: (int(w['similarity']), w['term'])):
                if y['isInformal'] == '0' and y['isVulgar'] is None:
                    print(f"{y['term']} {y['similarity']} /", end=" ")
                    sorted_data[x['definition']]['antonyms'].append((y['term'], y['similarity']))
                else:
                    blacklist.append(y)

            print()
            print()

        print('blacklist')
        for x in blacklist:
            print(x)
        for x in sorted_data.keys():
            print(x, sorted_data[x])
    else:
        for x in data:
            sorted_data[x['definition']] = {'pos': x['pos'], 'synonyms': [], 'antonyms': []}
            for y in sorted(x['synonyms'], key=lambda w: (-int(w['similarity']), w['term'])):
                if y['isInformal'] == '0' and y['isVulgar'] is None:
                    sorted_data[x['definition']]['synonyms'].append((y['term'], y['similarity']))
            for y in sorted(x['antonyms'], key=lambda w: (int(w['similarity']), w['term'])):
                if y['isInformal'] == '0' and y['isVulgar'] is None:
                    sorted_data[x['definition']]['antonyms'].append((y['term'], y['similarity']))
    return [True, sorted_data]


def get_docx_text(path):
    word_namespace = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
    para_ = word_namespace + 'p'
    text_ = word_namespace + 't'

    document = zipfile.ZipFile(path)
    xml_content = document.read('word/document.xml')
    document.close()
    tree = XML(xml_content)

    paragraphs = []
    for paragraph in tree.iter(para_):
        texts = [node.text for node in paragraph.iter(text_) if node.text]
        if texts:
            paragraphs.append(''.join(texts) + '\n')
        else:
            paragraphs.append('\n')
    return ''.join(paragraphs)
