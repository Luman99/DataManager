import pyslibtesseract
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
tesseract_config = pyslibtesseract.TesseractConfig(psm=pyslibtesseract.PageSegMode.PSM_SINGLE_LINE, hocr=True)
print(pyslibtesseract.LibTesseract.simple_read(tesseract_config, 'phrase0.png'))