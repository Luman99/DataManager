from typing import Optional


class CsvFile:
    def __init__(self, name: str, ocr_quality_wer: float, tesseract_engine_score: float,
                 path_to_image: str,
                 data_source: str, ocr_engine: str, train_test: str, language: str,
                 test: Optional[str], number_of_tokens: int, percent_of_white_spaces: float):

        self.tesseract_engine_score = tesseract_engine_score
        self.test = test
        self.ocr_engine = ocr_engine
        self.language = language
        self.train_test = train_test
        self.data_source = data_source
        self.path_to_image = path_to_image
        self.ocr_quality_wer = ocr_quality_wer
        self.name = name
        self.number_of_tokens = number_of_tokens
        self.percent_of_white_spaces = percent_of_white_spaces
