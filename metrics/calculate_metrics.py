import re
from os import path
from typing import List, Optional
from jiwer import wer

SQUASH_WHITESPACE_PATTERN = re.compile(r'[\s\x00-\x1F]+')


def get_ocr_quality(line_nr: int, path_in: str, show_texts: Optional[bool] = False) -> float:
    if not path.isdir(path_in):
        raise FileNotFoundError(f'Not a directory: {path_in}')

    expected_data = _read_expected_data(path_in, line_nr)
    actual_data = _read_actual_data(path_in, line_nr)
    if show_texts:
        print(expected_data)
        print(actual_data)
    assert len(expected_data) == len(actual_data), 'Different number of lines!'
    return _calculate_metrics(expected_data, actual_data, line_nr)


def _read_expected_data(test_dir, line_nr: int):
    expected = path.join(test_dir, '../utils/expected.tsv')
    if not path.isfile(expected):
        raise FileNotFoundError(f'Expected not found here: {expected}')
    return _read(expected, False, line_nr)


def _read_actual_data(test_dir, line_nr: int):
    actual = path.join(test_dir, '../utils/in.tsv')
    if not path.isfile(actual):
        raise FileNotFoundError(f'Actual output not found here: {actual}')
    return _read(actual, True, line_nr)


def _read(data_path: str, additional_information: bool, nr: int) -> List[str]:
    text = []
    parting = 0
    if additional_information:
        parting = 53
    with open(data_path, 'rt', encoding='utf8') as f:
        for i, line in enumerate(f):
            if i == nr:
                text.append(line[parting:].strip())
        return text


def _calculate_metrics(expected_data, actual_data, nr) -> float:
    squashed_expected = prepare_data(expected_data)
    squashed_actual = prepare_data(actual_data)
    expected = ' '
    final_expected = expected.join(squashed_expected)
    actual = ' '
    final_actual = actual.join(squashed_actual)
    result = float(wer(final_expected, final_actual))
    if result > 1.0:
        result = 1.0
    wer_r = 1 - result
    return wer_r


def prepare_data(data) -> List[str]:
    squashed_data = _squash_whitespace(data)
    data_no_n = []
    for word in squashed_data:
        word = word.replace('\\n', ' ')
        data_no_n.append(word)
    return data_no_n


def _squash_whitespace(data: List[str]) -> List[str]:
    return [SQUASH_WHITESPACE_PATTERN.sub(' ', datum) for datum in data]
