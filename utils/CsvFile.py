from typing import Optional


class CsvFile:
    def __init__(self, name: str, ocr_quality_wer: float, ocr_quality_cer: float, ocr_quality_iou: float,
                 path_to_json: str,
                 data_source: str, ocr_engine: str, train_test: str, language: str, test: Optional[str]):
        self.ocr_quality_iou = ocr_quality_iou
        self.ocr_quality_cer = ocr_quality_cer
        self.test = test
        self.ocr_engine = ocr_engine
        self.language = language
        self.train_test = train_test
        self.data_source = data_source
        self.path_to_json = path_to_json
        self.ocr_quality_wer = ocr_quality_wer
        self.name = name
