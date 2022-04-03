import pytesseract
from PIL import Image
import cv2
import numpy as np
from statistics import mean

from utils.Constants import PATH_IMAGES

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
    for i, line in enumerate(str(text).split('x_wconf')):
        sentence = (line.split('</span')[0]).split('>')[1:]
        joined_sentece = ' '.join(sentence)
        number_of_tokens += 1
        if joined_sentece.isspace():
            number_of_white_spaces += 1

    return {'number_of_tokens': number_of_tokens, 'percent_of_white_spaces': number_of_white_spaces/number_of_tokens}
