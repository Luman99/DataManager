import csv
from typing import List
import pandas as pd
from metrics.calculate_cf_metrcis import get_ocr_quality_cf_wer, get_ocr_quality_cf_cer, get_ocr_quality_cf_iou
from metrics.calculate_metrics import get_ocr_qaulity
from utils.Constants import PATH_DATA, PATH_DATA_CF
from utils.CsvFile import CsvFile
from utils.OcrEngine import OcrEngine


def get_ocr_qualities(ocr_engines, get_ocr_quality2):
    for i, engine in enumerate(ocr_engines):
        ocr_quality = get_ocr_quality2(engine)
        if i == 0:
            ocr_qualities = pd.DataFrame([name for name, _ in ocr_quality.items()], columns=['name'])
        ocr_qualities[f'ocr_quality_{engine}'] = [value for _, value in ocr_quality.items()]
    return ocr_qualities


def create_csv() -> List[CsvFile]:
    ocr_engines = ['tesseract']
    # ocr_engines = [engine.value for engine in OcrEngine]
    # ocr_engines.remove('easy_ocr_res')
    # ocr_engines.remove('paddle_paddle_results')
    # ocr_engines.remove('ms_ocr_res')

    #ocr_qualities_wer = get_ocr_qualities(ocr_engines, get_ocr_quality)
    # ocr_qualities_cer = get_ocr_qualities(ocr_engines, get_ocr_quality_cf_cer)
    # ocr_qualities_iou = get_ocr_qualities(ocr_engines, get_ocr_quality_cf_iou)

    # path_to_json = f'/data/shared/ocr-quality-scorer/data/json_files/engine/row[0].json'
    # bad_files = ['0be4e58d435771a4b398acbce111f3f2.png', '0ecce0c3984961fd48a16efe8459a26d.png',
    #              '0f2164230ee0f776fbebc22f5f4f6d35.png', 'HBHOJO_2015-094.png',
    #              'HBHOJO_2015-161.png', 'FSABLB_2015-077.png']
    all_csv = []
    # tests = ['A', 'B', 'C', 'D']
    tests = ['A']
    for test in tests:
        list_csv = []
        tsv_file = open(f'{PATH_DATA}/dev-0/in.tsv', encoding='latin1')
        read_tsv = csv.reader(tsv_file, delimiter="\t")
        for i, row in enumerate(read_tsv):
            if i % 2 == 0:
                train_test = 'train'
            else:
                train_test = 'test'
            for engine in ocr_engines:
                # try:
                    csv_obj = CsvFile(name=f'{row[0]}',
                                      ocr_quality_wer=round(get_ocr_qaulity(i, f'{PATH_DATA}/dev-0/'),2),
                                      ocr_quality_cer=0.3,
                                      ocr_quality_iou=0.4,
                                      path_to_image=f'{PATH_DATA}/images/{row[0]}',
                                      data_source='fiszki_ocr',
                                      ocr_engine=engine, train_test=train_test, language=row[1],
                                      test=test)
                                    # ocr_quality_wer = ocr_qualities_wer.loc[
                                    #                       ocr_qualities_wer['name'] == f'{PATH_DATA_CF}/{row[0]}.json',
                                    #                       f'ocr_quality_{engine}'].values[0],
                                    # ocr_quality_cer = ocr_qualities_cer.loc[
                                    #                       ocr_qualities_cer['name'] == f'{PATH_DATA_CF}/{row[0]}.json',
                                    #                       f'ocr_quality_{engine}'].values[0],
                                    # ocr_quality_iou = ocr_qualities_iou.loc[
                                    #                       ocr_qualities_iou['name'] == f'{PATH_DATA_CF}/{row[0]}.json',
                                    #                       f'ocr_quality_{engine}'].values[0],
                                    # path_to_json = f'{PATH_DATA}/json_cf_PD/{engine}_cf/{row[0]}.json',
                                    # data_source = 'ocr-test-challenge',
                                    # ocr_engine = engine, train_test = train_test, language = row[1],
                                    # test = test)
                    list_csv.append(csv_obj)
                # except:
                #     pass

        all_csv += list_csv
    return all_csv


if __name__ == '__main__':
    with open(f'{PATH_DATA}/dataset_local2.csv', 'w', newline='') as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerow(['name', 'ocr_quality_wer', 'ocr_quality_cer', 'ocr_quality_iou', 'path_to_json',
                         'data_source', 'ocr_engine', 'train_test', 'language', 'test'])
        for csvFile in create_csv():
            writer.writerow([csvFile.name, csvFile.ocr_quality_wer, csvFile.ocr_quality_cer, csvFile.ocr_quality_iou,
                             csvFile.path_to_json, csvFile.data_source, csvFile.ocr_engine,
                             csvFile.train_test, csvFile.language, csvFile.test])
