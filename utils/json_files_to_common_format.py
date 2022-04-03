import json
import os

from utils.common_format import build_common_format_data
from utils.common_format_JSON import make_common_format_json
from utils.OcrEngine import OcrEngine

PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
PATH_DATA = os.path.join(PATH, 'data')
dataset = os.path.join(PATH_DATA, '../dataset.csv')
PATH_JSON = os.path.join(PATH_DATA, 'json_files')


def common_format_from_hocr(path_to_hocr: str):
    file = open(f'{PATH_DATA}/tesseract_hocr/{path_to_hocr}').read()
    byte_file = bytes(file, 'utf-8')
    common_format_data = build_common_format_data(byte_file)

    return make_common_format_json(doc_id=path_to_hocr, tokens=common_format_data.number_of_tokens,
                                   tokens_positions=common_format_data.token_positions,
                                   tokens_scores=common_format_data.token_scores,
                                   pages_value=common_format_data.pages,
                                   pages_positions=common_format_data.pages_positions,
                                   lines_value=common_format_data.lines,
                                   lines_positions=common_format_data.lines_positions)


def textract_ocr_res(doc_id: str):
    tokens = []
    tokens_scores = []
    coordinates = []
    with open(f'{PATH_DATA}/{OcrEngine.textract_ocr_res.value}/{doc_id}', 'r') as file:
        json_object = json.load(file)
        for i, a in enumerate(json_object['Blocks']):
            if a['BlockType'] == 'WORD':
                tokens.append(a['Text'])
                tokens_scores.append(a['Confidence'])
                cordinates = a['Geometry']['Polygon']
                coordinates.append([cordinates[0]['X'], cordinates[0]['Y'], cordinates[2]['X'], cordinates[2]['Y']])

    return make_common_format_json(doc_id=doc_id, tokens=tokens, tokens_scores=tokens_scores,
                                   tokens_positions=coordinates)


def easy_ocr_res(doc_id: str):
    tokens = []
    tokens_scores = []
    coordinates = []
    with open(f'{PATH_DATA}/{OcrEngine.easy_ocr_res.value}/{doc_id}', 'r') as file:
        json_object = json.load(file)
        for i, word in enumerate(json_object):
            tokens.append(word['text'])
            tokens_scores.append(word['confidence'])
            coordinates.append([word['bbox'][1], word['bbox'][0], word['bbox'][3], word['bbox'][2]])

    return make_common_format_json(doc_id=doc_id, tokens=tokens, tokens_scores=tokens_scores,
                                   tokens_positions=coordinates)


def ms_ocr_res(doc_id: str):
    tokens = []
    coordinates = []
    with open(f'{PATH_DATA}/{OcrEngine.ms_ocr_res.value}/{doc_id}', 'r') as file:
        json_object = json.load(file)
        for item in json_object['regions']:
            for lines in item['lines']:
                for words in lines['words']:
                    tokens.append(words['text'])
                    numbers = words['boundingBox'].split(',')

                    bounding_box = [(int(numbers[0])), int(numbers[1]),
                                    int(numbers[0]) + int(numbers[2]),
                                    int(numbers[1]) + int(numbers[3])]
                    coordinates.append(bounding_box)

    return make_common_format_json(doc_id=doc_id, tokens=tokens, tokens_scores=[],
                                   tokens_positions=coordinates)


def ms_read_res(doc_id: str):
    tokens = []
    tokens_scores = []
    coordinates = []
    with open(f'{PATH_DATA}/{OcrEngine.ms_read_res.value}/{doc_id}', 'r') as file:
        json_object = json.load(file)

        for item in json_object['analyzeResult']['readResults']:
            for lines in item['lines']:
                for word in lines['words']:
                    tokens.append(word['text'])
                    tokens_scores.append(word['confidence'])
                    coordinates.append(word['boundingBox'][:2] + word['boundingBox'][4:6])

    return make_common_format_json(doc_id=doc_id, tokens=tokens, tokens_scores=[],
                                   tokens_positions=coordinates)


def paddle_paddle_results(doc_id: str):
    tokens = []
    tokens_scores = []
    coordinates = []
    with open(f'{PATH_DATA}/{OcrEngine.paddle_paddle_results.value}/{doc_id}', 'r') as file:
        json_object = json.load(file)
        for i, a in enumerate(json_object['texts']):
            tokens.append(a['text'])
            tokens_scores.append(a['score'])
            coordinates.append(a['bbox'])

    return make_common_format_json(doc_id=doc_id, tokens=tokens, tokens_scores=[],
                                   tokens_positions=coordinates)


for name in os.listdir(f'{PATH_DATA}/images/'):
    name_in = f'{name}.json'
    file_to_save = common_format_from_hocr(f'{name[:-3]}hocr')
    with open(f'{PATH_JSON}/{OcrEngine.tesseract.value}/{name[:-3]}json', 'w') as outfile:
        json.dump(file_to_save, outfile)

    file_to_save = textract_ocr_res(name_in)
    with open(f'{PATH_JSON}/{OcrEngine.textract_ocr_res.value}/{name[:-3]}json', 'w') as outfile:
        json.dump(file_to_save, outfile)

    file_to_save = easy_ocr_res(name_in)
    with open(f'{PATH_JSON}/{OcrEngine.easy_ocr_res.value}/{name[:-3]}json', 'w') as outfile:
        json.dump(file_to_save, outfile)

    file_to_save = ms_ocr_res(name_in)
    with open(f'{PATH_JSON}/{OcrEngine.ms_ocr_res.value}/{name[:-3]}json', 'w') as outfile:
        json.dump(file_to_save, outfile)

    file_to_save = ms_read_res(name_in)
    with open(f'{PATH_JSON}/{OcrEngine.ms_read_res.value}/{name[:-3]}json', 'w') as outfile:
        json.dump(file_to_save, outfile)
