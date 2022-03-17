import pytesseract
from PIL import Image
import cv2
import numpy as np
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
file_path= 'file.png'
im = Image.open(file_path)
im.save('ocr.png', dpi=(300, 300))

image = cv2.imread('file.png')
image = cv2.resize(image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
retval, threshold = cv2.threshold(image,127,255,cv2.THRESH_BINARY)

text = pytesseract.image_to_pdf_or_hocr(threshold, extension='hocr')

with open('Output.xml', 'wb') as text_file:
    text_file.write(text)