import csv
from typing import List
from metrics.calculate_metrics import get_ocr_qaulity
from utils.Constants import PATH_DATA
from utils.CsvFile import CsvFile


def create_csv() -> List[CsvFile]:
    list_csv = []
    tsv_file = open(f'utils/in.tsv', encoding='latin1')
    read_tsv = csv.reader(tsv_file, delimiter="\t")
    data_for_model = open(f'{PATH_DATA}/data_for_model.txt', 'r')
    for i, (row_tsv, row_txt) in enumerate(zip(read_tsv, data_for_model)):
        row_txt = row_txt.split(',')
        engine_score = float(row_txt[1])
        number_of_tokens = int(row_txt[2])
        percent_of_white_spaces = float(row_txt[3])
        if i % 2 == 0:
            train_test = 'train'
        else:
            train_test = 'test'
        csv_obj = CsvFile(name=f'{row_tsv[0]}',
                          ocr_quality_wer=round(get_ocr_qaulity(i, f'utils'), 2),
                          tesseract_engine_score=round(engine_score, 2),
                          path_to_image=f'{PATH_DATA}/images/{row_tsv[0]}',
                          data_source='fiszki_ocr',
                          ocr_engine='tesseract',
                          train_test=train_test, language=row_tsv[1],
                          test='A',
                          number_of_tokens=number_of_tokens,
                          percent_of_white_spaces=round(percent_of_white_spaces, 2))
        list_csv.append(csv_obj)
    return list_csv


if __name__ == '__main__':
    with open(f'{PATH_DATA}/dataset_local_new_model.csv', 'w', newline='') as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerow(['name', 'ocr_quality_wer', 'tesseract_engine_score', 'path_to_image',
                         'data_source', 'ocr_engine', 'train_test', 'language', 'test',
                         'number_of_tokens', 'percent_of_white_spaces'])
        for csvFile in create_csv():
            writer.writerow([csvFile.name, csvFile.ocr_quality_wer, csvFile.tesseract_engine_score,
                             csvFile.path_to_image, csvFile.data_source, csvFile.ocr_engine,
                             csvFile.train_test, csvFile.language, csvFile.test, csvFile.number_of_tokens,
                             csvFile.percent_of_white_spaces])
