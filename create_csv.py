import csv
from typing import List
import pandas as pd
from metrics.calculate_cf_metrcis import get_ocr_quality_cf_wer, get_ocr_quality_cf_cer, get_ocr_quality_cf_iou
from metrics.calculate_metrics import get_ocr_qaulity
from utils.Constants import PATH_DATA, PATH_DATA_CF
from utils.CsvFile import CsvFile
from utils.OcrEngine import OcrEngine
from utils.get_data_for_model import get_data_for_model
from utils.get_tesseract_engine_score import get_tesseract_score


def get_ocr_qualities(ocr_engines, get_ocr_quality2):
    for i, engine in enumerate(ocr_engines):
        ocr_quality = get_ocr_quality2(engine)
        if i == 0:
            ocr_qualities = pd.DataFrame([name for name, _ in ocr_quality.items()], columns=['name'])
        ocr_qualities[f'ocr_quality_{engine}'] = [value for _, value in ocr_quality.items()]
    return ocr_qualities


def create_csv() -> List[CsvFile]:
    ocr_engines = ['tesseract']
    all_csv = []
    tests = ['A']
    for test in tests:
        list_csv = []
        tsv_file = open(f'utils/in.tsv', encoding='latin1')
        read_tsv = csv.reader(tsv_file, delimiter="\t")
        for i, row in enumerate(read_tsv):
            if i % 2 == 0:
                train_test = 'train'
            else:
                train_test = 'test'
            for engine in ocr_engines:
                csv_obj = CsvFile(name=f'{row[0]}',
                                  ocr_quality_wer=round(get_ocr_qaulity(i, f'utils'), 2),
                                  tesseract_engine_score=round(get_tesseract_score(row[0]), 2),
                                  path_to_image=f'{PATH_DATA}/images/{row[0]}',
                                  data_source='fiszki_ocr',
                                  ocr_engine=engine, train_test=train_test, language=row[1],
                                  test=test,
                                  number_of_tokens=get_data_for_model(row[0])['number_of_tokens'],
                                  percent_of_white_spaces=round(get_data_for_model(row[0])['percent_of_white_spaces']
                                                                , 2))
                list_csv.append(csv_obj)
        all_csv += list_csv
    return all_csv


if __name__ == '__main__':
    with open(f'{PATH_DATA}/dataset_local_new_model.csv', 'w', newline='') as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerow(['name', 'ocr_quality_wer', 'tesseract_engine_score', 'path_to_image',
                         'data_source', 'ocr_engine', 'train_test', 'language', 'test', 'number_of_tokens', 'percent_of_white_spaces'])
        for csvFile in create_csv():
            writer.writerow([csvFile.name, csvFile.ocr_quality_wer, csvFile.tesseract_engine_score,
                             csvFile.path_to_image, csvFile.data_source, csvFile.ocr_engine,
                             csvFile.train_test, csvFile.language, csvFile.test, csvFile.number_of_tokens,
                             csvFile.percent_of_white_spaces])
