import csv

import pytesseract
from PIL import Image
import cv2
from statistics import mean

from utils.Constants import PATH_IMAGES
from utils.Constants import PATH_DATA

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def get_data_for_model(file_name: str):
    im = Image.open(f'{PATH_IMAGES}\\{file_name}')
    im.save('ocr.png', dpi=(300, 300))
    image = cv2.imread('ocr.png')
    image = cv2.resize(image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    _, threshold = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)

    text = pytesseract.image_to_pdf_or_hocr(threshold, extension='hocr')
    number_of_tokens = 0
    number_of_white_spaces = 0
    scores = []
    for i, line in enumerate(str(text).split('x_wconf')):
        if i != 0:
            scores.append(int((line.split('</span>')[0]).split('\\')[0]))
        sentence = (line.split('</span')[0]).split('>')[1:]
        joined_sentence = ' '.join(sentence)
        number_of_tokens += 1
        if joined_sentence.isspace():
            number_of_white_spaces += 1

    return f'{file_name},{float(mean(scores) / 100)},{number_of_tokens},{number_of_white_spaces / number_of_tokens}'


if __name__ == '__main__':
    tsv_file = open(f'in.tsv', encoding='latin1')
    read_tsv = csv.reader(tsv_file, delimiter="\t")
    f = open(f'{PATH_DATA}\\data_for_model.txt', 'w+', encoding='latin1')
    for i, row in enumerate(read_tsv):
        f.write(f'{get_data_for_model(row[0])}\n')
    f.close()

    # return {'engine_score': float(mean(scores) / 100), 'number_of_tokens': number_of_tokens,
    #         'percent_of_white_spaces': number_of_white_spaces / number_of_tokens}
