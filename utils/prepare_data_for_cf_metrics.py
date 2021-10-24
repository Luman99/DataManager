import glob
import os
import shutil

import pandas as pd

from utils.OcrEngine import OcrEngine

PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
PATH_DATA = os.path.join(PATH, 'data')
PATH_DATA_NEW = os.path.join(PATH_DATA, 'json_for_cf')
PATH_DATA_OLD = os.path.join(PATH_DATA, 'json_files')


def delete_files():
    for engine in OcrEngine:
        directory = f'{PATH_DATA_NEW}/{engine.value}/*'

        files = glob.glob(directory)
        for f in files:
            os.remove(f)


def copy_files(data):
    for row in data.itertuples():

        if row[8] in ['B', 'D']:
            shutil.copy(row[3], f'{PATH_DATA_NEW}/{row[5]}/')


def rename_files():
    for engine in OcrEngine:
        directory = f'{PATH_DATA_NEW}/{engine.value}/*'

        files = glob.glob(directory)
        for f in files:
            os.rename(f, f'{os.path.splitext(f)[0]}.png.json')


def main():
    data = pd.read_csv(f'../dataset.csv')
    delete_files()
    copy_files(data)
    rename_files()


if __name__ == '__main__':
    main()
