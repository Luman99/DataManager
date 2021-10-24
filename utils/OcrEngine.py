from enum import Enum


class OcrEngine(Enum):
    tesseract = 'tesseract'
    easy_ocr_res = 'easy_ocr_res'
    ms_ocr_res = 'ms_ocr_res'
    ms_read_res = 'ms_read_res'
    paddle_paddle_results = 'paddle_paddle_results'
    textract_ocr_res = 'textract_ocr_res'
