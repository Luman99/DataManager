import lzma
import re
import unicodedata
from argparse import ArgumentParser, Namespace
from collections import defaultdict
from os import path
from typing import Iterator, List, Tuple
from unicodedata import combining, normalize
from jiwer import wer
import editdistance

SQUASH_WHITESPACE_PATTERN = re.compile(r'[\s\x00-\x1F]+')


def get_ocr_qaulity(nr: int, path_in: str) -> float:
    args = _parse_args(path_in)
    test_dir = args.test_dir
    if not path.isdir(test_dir):
        raise FileNotFoundError(f'Not a directory: {test_dir}')

    expected_data = _read_expected_data(test_dir, nr)
    actual_data = _read_actual_data(test_dir, nr)
    print(expected_data)
    print(actual_data)
    assert len(expected_data) == len(actual_data), 'Different number of lines!'
    return _calculate_metrics(expected_data, actual_data, nr)


def _parse_args(path_in: str) -> Namespace:
    parser = ArgumentParser()
    parser.add_argument('--test_dir', default=path_in)
    return parser.parse_args()


def _read_expected_data(test_dir, nr: int):
    expected = path.join(test_dir, 'expected.tsv')
    if not path.isfile(expected):
        raise FileNotFoundError(f'Expected not found here: {expected}')
    return _read(expected, False, nr)


def _read(data_path: str, compressed: bool, nr: int) -> List[str]:
    text = []
    x = 0
    y = 0
    if compressed:
        lines = []
        with open(data_path, 'rt', encoding='Latin1') as f:
            # print(data_path)
            # print(f)
            for line in f:
                #print(line[53:])
                lines.append(line[53:])
                if x == nr:
                    text.append(line[53:].strip())
                x += 1
            return text
    with open(data_path, encoding='Latin1') as f:
        for line in f:
            if y == nr:
                text.append(line.strip())
            y += 1
        return text


def _read_actual_data(test_dir, nr: int):
    actual = path.join(test_dir, 'in.tsv')
    if not path.isfile(actual):
        raise FileNotFoundError(f'Actual output not found here: {actual}')
    return _read(actual, True, nr)


def prepare_data(data) -> List[str]:
    squashed_data = _squash_whitespace(data)
    data_no_n = []
    for word in squashed_data:
        word = word.replace('\\n', ' ')
        data_no_n.append(word)

    return data_no_n


def _calculate_metrics(expected_data, actual_data, nr) -> float:
    squashed_expected = prepare_data(expected_data)
    squashed_actual = prepare_data(actual_data)

    expected = ' '
    final_expected = expected.join(squashed_expected)
    actual = ' '
    final_actual = actual.join(squashed_actual)

    squashed_distances = _calculate_distances(zip(squashed_expected, squashed_actual))
    squashed_lengths = [len(squashed) for squashed in squashed_expected]
    total_chars = sum(squashed_lengths)
    cer = _calculate_statistics(_calculate_cer(squashed_distances, squashed_lengths), total_chars,
                                sum(squashed_distances), 'CER_squashed')
    result = float(wer(final_expected, final_actual))
    if result > 1.0:
        result = 1.0
    wer_r = 1 - result
    return wer_r


def _calculate_distances(data: Iterator[Tuple[str, str]]) -> List[int]:
    return [editdistance.eval(expected, actual) for expected, actual in data]


def _calculate_cer(distances: List[int], expected_lengths: List[int]) -> List[float]:
    return [distance / expected_len for distance, expected_len in zip(distances, expected_lengths)]


def _calculate_statistics(metrics: List[float], chars: int, errors: int, metric_name: str) -> float:
    accuracy = [_calculate_accuracy(cer) for cer in metrics]
    harmonic_acc = _calculate_harmonic_mean(accuracy)
    return round(harmonic_acc, 2)


def _calculate_accuracy(metric: float) -> float:
    if metric >= 1.0:
        return 0
    return 1.0 - metric


def _calculate_harmonic_mean(metrics):
    metrics = [0.01 if metric == 0 else metric for metric in metrics]
    return len(metrics) / sum([1 / metric for metric in metrics])


def _squash_whitespace(data: List[str]) -> List[str]:
    return [SQUASH_WHITESPACE_PATTERN.sub(' ', datum) for datum in data]


def _normalize(data: List[str]) -> List[str]:
    # Compatibility decomposition followed by composition, to remove ligatures etc.
    return [normalize('NFKC', datum) for datum in data]


def _strip_accents(s: str) -> str:
    return ''.join([ch for ch in normalize('NFD', s) if combining(ch) == 0]).replace('ł', 'l')


def _calculate_unicode_categories_errors(expected: List[str], actual: List[str]) -> str:
    exp_classes = _count_charactes_by_category(expected)
    act_classes = _count_charactes_by_category(actual)
    keys = sorted(set(exp_classes.keys()).union(act_classes.keys()))
    char_categories = [_category_report_line(key, exp_classes[key], act_classes[key]) for key in keys]
    classes_report = '\n'.join(char_categories)

    return f'\nExpected len: {sum([len(s) for s in expected])}\n' \
           f'Actual len: {sum([len(s) for s in actual])}\n' \
           f'Character classes:\n{"Class":11s}    Expected      Actual    % Errors\n{classes_report}'


def _count_charactes_by_category(data: List[str]):
    categories = defaultdict(int)
    for datum in data:
        for ch in datum:
            categories[unicodedata.category(ch)] += 1
    return categories


def _category_report_line(category: str, expected_count: int, actual_count: int) -> str:
    error: float = 0.0
    if expected_count == 0 and actual_count > 0:
        error = 100.0
    elif expected_count > 0:
        error = 100 * abs(expected_count - actual_count) / expected_count
    return f'{category:11s} {expected_count:11d} {actual_count:11d} {error:11.2f}'
