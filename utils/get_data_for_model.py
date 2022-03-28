import pytesseract
from PIL import Image
import cv2
import numpy as np
from statistics import mean

from utils.Constants import PATH_IMAGES

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def get_data_for_model(file_name: str):
    # file_path= 'file.png'
    im = Image.open(f'{PATH_IMAGES}\\{file_name}')
    im.save('ocr.png', dpi=(300, 300))
    #print(f'{PATH_IMAGES}\\{file_name}')
    # image = cv2.imread(f'{PATH_IMAGES}/{file_path}')
    image = cv2.imread('ocr.png')
    image = cv2.resize(image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    _, threshold = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)

    text = pytesseract.image_to_pdf_or_hocr(threshold, extension='hocr')
    # print(text)
    #print(str(text))
    scores = []
    number_of_tokens = 0
    number_of_white_spaces = 0
    for i, line in enumerate(str(text).split('x_wconf')):
        sentence = (line.split('</span')[0]).split('>')[1:]
        joined_sentece = ' '.join(sentence)
        # print(joined_sentece)
        number_of_tokens += 1
        if joined_sentece.isspace():
            # print('xd')
            number_of_white_spaces += 1
        # if i != 0:
        #     scores.append(int((line.split('</span>')[0]).split('\\')[0]))

    return {'number_of_tokens': number_of_tokens, 'number_of_white_spaces': number_of_white_spaces}

    # with open('Output.xml', 'wb') as text_file:
    #     text_file.write(text)


if __name__ == '__main__':
    with open('in.tsv', encoding='latin1') as data:
        for row in data:
            print(get_tesseract_score(row[:44]))

    # print(get_tesseract_score('file.png'))
