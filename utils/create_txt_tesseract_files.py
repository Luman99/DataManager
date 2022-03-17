import os

PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PATH = os.path.abspath(os.path.join(PATH, ".."))
PATH_DATA = os.path.join(PATH, 'data')
PATH_TEXT = os.path.join(PATH_DATA, 'tesseract-text')

text = []
with open('in.tsv', encoding='latin1') as data:
    for row in data:
        f = open(f'{PATH_TEXT}\{row[:41]}txt', 'w+', encoding='latin1')
        f.write(row[53:])
        f.close()
