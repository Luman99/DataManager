import pytesseract
from PIL import Image
import cv2
import numpy as np

from utils.Constants import PATH_IMAGES

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def get_tesseract_score(file_path: str) -> float:
    # file_path= 'file.png'
    im = Image.open(f'{PATH_IMAGES}\\{file_path}')
    im.save('ocr.png', dpi=(300, 300))
    print(f'{PATH_IMAGES}\\{file_path}')
    # image = cv2.imread(f'{PATH_IMAGES}/{file_path}')
    image = cv2.imread('ocr.png')
    image = cv2.resize(image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    _, threshold = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)

    text = pytesseract.image_to_pdf_or_hocr(threshold, extension='hocr')
    print(str(text))
    scores = []
    for i, line in enumerate(str(text).split('x_wconf')):
        if i != 0:
            scores.append(int((line.split('</span>')[0]).split('\\')[0]))

    return sum(scores) / len(scores)

    # with open('Output.xml', 'wb') as text_file:
    #     text_file.write(text)


if __name__ == '__main__':
    with open('in.tsv', encoding='latin1') as data:
        for row in data:
            print(get_tesseract_score(row[:44]))

    # print(get_tesseract_score('file.png'))
