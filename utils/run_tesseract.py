#!/usr/bin/env python3

import lzma
import sys
from argparse import ArgumentParser, Namespace
from collections import defaultdict
from os import listdir, makedirs, path
from typing import Dict, Iterator, List, Optional, Tuple

from PIL import Image as PillowImage
from tesserocr import PyTessBaseAPI
from tqdm import tqdm


def _main():
    args = _parse_args()
    files = _filter_files(_find_images(args.image_dir), args)
    reader = _MetadataReader(args.metadata_path, args.header_path, args.file_id_column)
    by_language = _group_by_language(files, reader)
    recognizer = Recognizer(args.image_dir, no_dpi=args.no_dpi, store_hocr=args.hocr, dpi=args.dpi)
    # Who in his right mind set the maximum pixel limit?
    # Anyways, the OpenCV-generated images won't open. Thus the workaround.
    PillowImage.MAX_IMAGE_PIXELS = sys.maxsize
    for lang, files in tqdm(by_language.items(), desc='Languages'):
        texts = recognizer.recognize(files, lang)
        _save_text(args.target_dir, zip(files, texts), args.hocr)


def _parse_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument('image_dir', help='Path to the directory containing images to recognize')
    parser.add_argument('metadata_path', help='Path to the metadata file containing language')
    parser.add_argument('target_dir', help='Path to the directory to store recognized text')
    parser.add_argument('--header_path', help='Path to the metadata header (eg. in-header.tsv)', default=None)
    parser.add_argument('--no_dpi', action='store_true', help='Should Tesseract detect DPI on its own?')
    parser.add_argument('--hocr', action='store_true', help='Should Tesseract store HOCR instead of text?')
    parser.add_argument('--dpi', default=150, type=int, help='Pixel depth of an image')
    parser.add_argument('--file_id_column', help='Optional argument to override metadata file_id column index',
                        type=int, default=None)
    parser.add_argument('--filter_by', help='Path to file containing files to restrict processing to', default=None)
    parser.add_argument('--filter_column', help='Column index for filter_by file', type=int, default=0)
    return parser.parse_args()


def _find_images(image_dir: str) -> List[str]:
    if not path.isdir(image_dir):
        raise FileNotFoundError(f'Image directory does not exists: {image_dir}!')
    image_extensions = {'.png', '.jpg', '.jpe', '.jpeg', '.tif', '.tiff', '.gif'}
    return [f for f in listdir(image_dir) if path.splitext(f)[-1] in image_extensions]


def _filter_files(files: List[str], args: Namespace) -> List[str]:
    if args.filter_by:
        filter_lines = _TsvReader(args.filter_by).read_lines()
        restricted_filenames = {line[args.filter_column] for line in filter_lines}

        return list(restricted_filenames.intersection(files))
    else:
        return files


def _group_by_language(files: List[str], reader: '_MetadataReader') -> Dict[str, List[str]]:
    result = defaultdict(list)
    [result[reader.get_language(filename)].append(filename) for filename in files if reader.is_file_present(filename)]
    return result


def _save_text(target_dir: str, files_and_texts: Iterator[Tuple[str, str]], is_hocr: bool):
    makedirs(target_dir, exist_ok=True)
    extension = '.hocr' if is_hocr else '.txt'
    for filename, text in files_and_texts:
        _save(path.join(target_dir, f'{filename}{extension}'), text)


def _save(filename: str, contents: str):
    with open(filename, 'w') as f:
        f.write(contents)


# type checker does not get things like 'rt'
# noinspection PyTypeChecker
class _TsvReader:

    def __init__(self, file_path: str):
        self._file = file_path

    def read_lines(self) -> List[List[str]]:
        lines = self._read_lzma_lines(self._file) if self._file.endswith('.xz') else self._read_lines(self._file)
        # Avoid potential field length limit hardcoded into Python's csv Reader for no reason
        return [line.strip().split('\t') for line in lines]

    @staticmethod
    def _read_lzma_lines(filename) -> List[str]:
        with lzma.open(filename, 'rt') as f:
            return f.readlines()

    @staticmethod
    def _read_lines(filename) -> List[str]:
        with open(filename) as f:
            return f.readlines()


# noinspection PyTypeChecker
class _MetadataReader:

    def __init__(self, meta_path: str, header_file_path: Optional[str] = None, file_id_column: Optional[int] = None):
        if not path.isfile(meta_path):
            raise FileNotFoundError('Unable to find metadata!')
        directory, _ = path.split(meta_path)
        header_path = header_file_path if header_file_path else path.join(directory, 'metadata-header.tsv')
        if path.isfile(header_path):
            self._header = _TsvReader(header_path).read_lines()[0]
            self._metadata = _TsvReader(meta_path).read_lines()
        else:
            meta = _TsvReader(meta_path).read_lines()
            self._header = meta[0]
            self._metadata = meta[1:]
        if 'lang' not in self._header:
            raise ValueError('Language not found in metadata header!')
        self._lang_index = self._header.index('lang')
        if 'file_id' not in self._header and file_id_column is None:
            raise ValueError('File identifier (file_id) not found in metadata header!')
        self._file_index = file_id_column if file_id_column else self._header.index('file_id')
        self._codes = {'de': 'deu', 'en': 'eng', 'es': 'spa', 'fr': 'fra', 'it': 'ita', 'nl': 'ned',  'pl': 'pol',
                       'pt': 'por', 'tr': 'tur'}
        self._lang_by_filename = self._find_language()

    def _find_language(self) -> Dict[str, str]:
        result = {}
        for line in self._metadata:
            result[line[self._file_index]] = self._translate_iso_639_2_to_3(line[self._lang_index])
        return result

    def _translate_iso_639_2_to_3(self, iso_639_2_code: str) -> str:
        # already translated
        if len(iso_639_2_code) > 2:
            return iso_639_2_code
        return self._codes[iso_639_2_code]

    def is_file_present(self, filename: str) -> bool:
        return filename in self._lang_by_filename

    def get_language(self, filename: str) -> str:
        """
        Get ISO-639-3 language identifier of a file name.
        :param filename: The file name
        :return: The language code for the file name if it is found
        :raises ValueError: When there is no file name in the metadata
        """
        if filename in self._lang_by_filename:
            return self._lang_by_filename[filename]
        raise ValueError(f'File name missing in metadata: {filename}!')


class Recognizer:
    """
    Recognize the images with Tesseract.

    :param dpi: Pixel depth of images
    """

    def __init__(self, image_dir: str, dpi: int = 150, no_dpi: bool = False, store_hocr: bool = False):
        self._image_dir = image_dir
        self._dpi = self.__validate_dpi(dpi)
        self._no_dpi = no_dpi
        self._store_hocr = store_hocr

    @staticmethod
    def __validate_dpi(value: int) -> int:
        if value < 72:
            raise ValueError('Pixel depth must be at least 72 DPI')
        return value

    def recognize(self, images: List[str], lang: str) -> List[str]:
        """
        Recognize images with Tesseract.

        :param images: Page images
        :param lang: The language for text
        :return: Per-page text
        """
        with PyTessBaseAPI(lang=lang) as api:
            return [self.__recognize_image(api, image) for image in tqdm(images, desc=lang, unit='img')]

    def __set_resolution(self, api: PyTessBaseAPI):
        if not self._no_dpi:
            api.SetSourceResolution(self._dpi)

    def __recognize_image(self, api: PyTessBaseAPI, image: str) -> str:
        api.SetImage(PillowImage.open(path.join(self._image_dir, image)))
        self.__set_resolution(api)
        return self.__get_recognition_result(api)

    def __get_recognition_result(self, api: PyTessBaseAPI) -> str:
        if self._store_hocr:
            lang = api.GetLoadedLanguages()[0]
            header = f'<!DOCTYPE html>\n<head>\n<meta charset="UTF-8">\n</head>\n<body lang="{lang}">\n'
            body = api.GetHOCRText(0)
            footer = '</body>\n</html>'
            return f'{header}{body}{footer}'
        else:
            return api.GetUTF8Text()

    @property
    def dpi(self) -> int:
        """
        Return recognizer pixel depth.
        :return: The pixel depth
        """
        return self._dpi

    @dpi.setter
    def dpi(self, value: int):
        """
        Set recognizer's image pixel depth.

        :param value: Integer, 72 at minimum
        """
        self._dpi = self.__validate_dpi(value)


if __name__ == '__main__':
    _main()
