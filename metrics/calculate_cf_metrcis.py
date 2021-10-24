import dataclasses
import json
import os
from argparse import ArgumentParser, Namespace
from dataclasses import dataclass
from os import listdir, makedirs, path
from statistics import mean
from typing import List, Tuple, Dict

import editdistance
from unicodedata import combining, normalize


from utils.OcrEngine import OcrEngine

PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
PATH_DATA = os.path.join(PATH, 'data')


@dataclass
class Metrics:
    file_id: str
    distance: int
    char_count: int
    extra_tokens: List[Tuple]
    missing_tokens: List[Tuple]
    matching_tokens: List[Tuple]
    misplaced_tokens: List[Tuple]
    word_count: int
    ious: List[float]

    @property
    def cer(self) -> float:
        return self.distance / self.char_count

    @property
    def wer(self) -> float:
        inserted_word_count = len(self.extra_tokens)
        deleted_word_count = len(self.missing_tokens)
        swapped_word_count = len(self.misplaced_tokens)
        return (inserted_word_count + deleted_word_count + swapped_word_count) / self.word_count

    @property
    def iou(self) -> float:
        if len(self.ious) == 0:
            return 0
        return mean(self.ious) if len(self.ious) > 1 else self.ious[0]

    def save(self, target_dir: str):
        with open(path.join(target_dir, self.file_id), 'w') as f:
            json.dump(dataclasses.asdict(self), f, indent=1)


def main(engine):
    args = _parse_args(engine)
    files = _find_files(args)
    all_metrics = _process(files)
    makedirs(args.reports_path, exist_ok=True)
    [metric.save(args.reports_path) for metric in all_metrics]
    _save_report(all_metrics, args.reports_path)


def get_ocr_quality_cf_wer(engine) -> Dict:
    args = _parse_args(engine)
    files = _find_files(args)
    all_metrics = _process(files)
    makedirs(args.reports_path, exist_ok=True)
    [metric.save(args.reports_path) for metric in all_metrics]
    _save_report(all_metrics, args.reports_path)
    zip_iterator = zip([file[0] for file in files], [max(1 - metrics.wer, 0) for metrics in all_metrics])
    ocr_quality_dictionary = dict(zip_iterator)
    return ocr_quality_dictionary


def get_ocr_quality_cf_cer(engine) -> Dict:
    args = _parse_args(engine)
    files = _find_files(args)
    all_metrics = _process(files)
    makedirs(args.reports_path, exist_ok=True)
    [metric.save(args.reports_path) for metric in all_metrics]
    _save_report(all_metrics, args.reports_path)
    zip_iterator = zip([file[0] for file in files], [max(1 - metrics.cer, 0) for metrics in all_metrics])
    ocr_quality_dictionary = dict(zip_iterator)
    return ocr_quality_dictionary


def get_ocr_quality_cf_iou(engine) -> Dict:
    args = _parse_args(engine)
    files = _find_files(args)
    all_metrics = _process(files)
    makedirs(args.reports_path, exist_ok=True)
    [metric.save(args.reports_path) for metric in all_metrics]
    _save_report(all_metrics, args.reports_path)
    zip_iterator = zip([file[0] for file in files], [metrics.iou for metrics in all_metrics])
    ocr_quality_dictionary = dict(zip_iterator)
    return ocr_quality_dictionary


def _parse_args(engine) -> Namespace:
    parser = ArgumentParser()
    parser.add_argument('--gold_path', help='Path to gold standard CF files', default=f'{PATH_DATA}/common-format')
    parser.add_argument('--recognized_path', help='Path to OCR-recognized CF files', default=f'{PATH_DATA}/json_cf_PD/{engine}_cf')
    parser.add_argument('--reports_path', help='Path to metrics report directory', default=f'{PATH_DATA}/out_for_metrics/{engine}')
    return parser.parse_args()


def _find_files(args: Namespace) -> List[Tuple[str, str]]:
    if args.gold_path.endswith('.json') and args.recognized_path.endswith('.json'):
        assert path.isfile(args.gold_path), f'{args.gold_path} is not a regular file'
        assert path.isfile(args.recognized_path), f'{args.recognized_path} is not a regular file'
        return [(args.gold_path, args.recognized_path)]
    elif path.isdir(args.gold_path) and path.isdir(args.recognized_path):
        gold_files = [f for f in listdir(args.gold_path) if f.endswith('.json')]
        assert len(gold_files), f'No CF files found in {args.recognized_path}'
        ocr_files = [f for f in gold_files if path.isfile(path.join(args.recognized_path, f))]
        assert len(ocr_files) == len(gold_files), f'Missing gold files: {set(ocr_files).difference(gold_files)}'
        return [(path.join(args.gold_path, f), path.join(args.recognized_path, f)) for f in ocr_files]
    else:
        raise ValueError('Invalid input. Compare either two directories or two CF files.')


def _process(files: List[Tuple[str, str]]) -> List[Metrics]:
    return [_process_single(gold, ocr) for gold, ocr in files]


def _process_single(gold: str, ocr: str) -> Metrics:
    _, file_id = path.split(gold)
    gold_data = _read_cf(gold)
    ocr_data = _read_cf(ocr)
    return _calculate_metrics(file_id, gold_data, ocr_data)


def _read_cf(file_path: str) -> List[Tuple]:
    with open(file_path) as f:
        contents = json.load(f)
    assert 'tokens' in contents, f'There are no tokens in {file_path}'
    assert 'positions' in contents, f'There are no positions in {file_path}'
    tokens = contents['tokens']
    positions = contents['positions']
    assert len(tokens) == len(positions), f'Invalid CF file, number of tokens ({len(tokens)}) is not equal to number' \
                                          f' of bounding boxes ({len(positions)})'
    # left, top, right, bottom
    values = [(bbox[0], bbox[1], bbox[2], bbox[3], token) for bbox, token in zip(positions, tokens)]
    by_left = sorted(values, key=lambda x: x[0])
    # sorted by top-left for easy matching
    return sorted(by_left, key=lambda x: x[1])


def _calculate_metrics(file_id: str, gold: List[Tuple], ocr: List[Tuple]) -> Metrics:
    word_count = len(gold)
    char_count = sum([len(entry[4]) for entry in gold])
    extra_tokens = []
    missing_tokens = []
    matching_tokens = []
    misplaced_tokens = []
    ious = []
    distances = []
    while len(ocr):
        if len(gold) == 0:
            break
        ocr_entry = ocr.pop(0)
        matching_index = _find_matching_index(ocr_entry, gold)
        if matching_index >= 0:
            gold_entry = gold.pop(matching_index)
            ious.append(_calculate_iou(gold_entry, ocr_entry))
            distances.append(editdistance.eval(gold_entry[4], ocr_entry[4]))
            if _is_word_matching(gold_entry[4], ocr_entry[4]):
                matching_tokens.append(ocr_entry)
            else:
                misplaced_tokens.append(ocr_entry)
        else:
            extra_tokens.append(ocr_entry)
    # if there is anything left, there's no match
    missing_tokens.extend(gold)
    extra_tokens.extend(ocr)
    distance = sum(distances) + _calculate_tokens_length(missing_tokens) + _calculate_tokens_length(extra_tokens)
    return Metrics(file_id,
                   distance, char_count,
                   extra_tokens, missing_tokens, matching_tokens, misplaced_tokens, word_count,
                   ious)


def _find_matching_index(ocr_entry: Tuple, gold: List[Tuple]) -> int:
    result = -1
    for i, gold_entry in enumerate(gold):
        if not (_is_above(ocr_entry, gold_entry) or _is_above(gold_entry, ocr_entry) or _is_left(ocr_entry, gold_entry)
                or _is_left(gold_entry, ocr_entry)):
            result = i
            break
    return result


def _is_above(e1: Tuple, e2: Tuple) -> bool:
    # that bottom <= other top (coordinate system is located in the top left corner)
    return e1[3] <= e2[1]


def _is_left(e1: Tuple, e2: Tuple) -> bool:
    # that right <= other left
    return e1[2] <= e2[0]


# https://gist.github.com/meyerjo/dd3533edc97c81258898f60d8978eddc
def _calculate_iou(box_1: Tuple, box_2: Tuple) -> float:
    # determine the (x, y)-coordinates of the intersection rectangle
    max_top = max(box_1[0], box_2[0])
    max_left = max(box_1[1], box_2[1])
    min_bottom = min(box_1[2], box_2[2])
    min_right = min(box_1[3], box_2[3])

    # compute the area of intersection rectangle
    common_area = abs(max((min_bottom - max_top, 0)) * max((min_right - max_left), 0))
    if common_area == 0:
        return 0
    # compute the area of both the prediction and ground-truth rectangles
    area_1 = abs((box_1[2] - box_1[0]) * (box_1[3] - box_1[1]))
    area_2 = abs((box_2[2] - box_2[0]) * (box_2[3] - box_2[1]))

    return common_area / float(area_1 + area_2 - common_area)


def _is_word_matching(word1: str, word2: str) -> bool:
    # Case fold, diacritics fold, ignoring whitespaces ~ fuzzy match
    return _strip_accents(word1.strip().lower()) == _strip_accents(word2.strip().lower())


def _strip_accents(s: str) -> str:
    return ''.join([ch for ch in normalize('NFD', s) if combining(ch) == 0]).replace('ł', 'l')


def _calculate_tokens_length(tokens: List[Tuple]) -> int:
    return sum([len(token) for token in tokens])


def _save_report(all_metrics: List[Metrics], target_dir: str):
    metrics = _aggregate_metrics(all_metrics)
    with open(path.join(target_dir, 'report.txt'), 'w') as f:
        f.write(f'CER: {metrics.cer}\n')
        f.write(f'WER: {metrics.wer}\n')
        f.write(f'IoU: {metrics.iou}\n\n')
        f.write(f'Total missing words: {len(metrics.missing_tokens)}\n')
        f.write(f'Total extra words: {len(metrics.extra_tokens)}\n\n')
        f.write(f'Total matching words: {len(metrics.matching_tokens)}\n')
        f.write(f'Total misrecognized words: {len(metrics.misplaced_tokens)}\n\n')
        f.write(f'CER\n____\n')
        best_cer, worst_cer = _top_5_last_5_filenames(sorted(all_metrics, key=lambda x: x.cer))
        f.write(f'Top 5 files: {best_cer}\nLast 5 files: {worst_cer}\n\n')
        f.write(f'WER\n____\n')
        best_wer, worst_wer = _top_5_last_5_filenames(sorted(all_metrics, key=lambda x: x.wer))
        f.write(f'Top 5 files: {best_wer}\nLast 5 files: {worst_wer}\n\n')


def _aggregate_metrics(all_metrics: List[Metrics]) -> Metrics:
    distance = 0
    char_count = 0
    extra_tokens = []
    missing_tokens = []
    matching_tokens = []
    misplaced_tokens = []
    word_count = 0
    ious = []
    for metric in all_metrics:
        distance += metric.distance
        char_count += metric.char_count
        extra_tokens.extend(metric.extra_tokens)
        missing_tokens.extend(metric.missing_tokens)
        matching_tokens.extend(metric.matching_tokens)
        misplaced_tokens.extend(metric.misplaced_tokens)
        word_count += metric.word_count
        ious.extend(metric.ious)
    return Metrics('__all_aggregated__', distance, char_count, extra_tokens, missing_tokens, matching_tokens,
                   misplaced_tokens, word_count, ious)


def _top_5_last_5_filenames(metrics: List[Metrics]) -> Tuple[str, str]:
    filenames = [metric.file_id for metric in metrics]
    return ' '.join(filenames[:5]), ' '.join(filenames[-5:])


if __name__ == '__main__':
    get_ocr_quality_cf_wer(OcrEngine.tesseract.value)
