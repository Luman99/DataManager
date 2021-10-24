import csv
import os
import shutil

PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
PATH_DATA = os.path.join(PATH, 'data')
PATH_IMAGES = os.path.join(PATH_DATA, 'images')
PATH_IMAGES_MANUAL = os.path.join(PATH_DATA, 'images_to_check_manual')

PATH_METRICS = os.path.join(PATH_DATA, 'data_for_calculate_metrics')
PATH_tesseract = os.path.join(PATH_METRICS, 'tesseract')

path_a_in = os.path.join(PATH_tesseract, 'test-A-tesseract')
path_b_in = os.path.join(PATH_tesseract, 'test-B-tesseract')
path_c_in = os.path.join(PATH_tesseract, 'test-C-tesseract')
path_d_in = os.path.join(PATH_tesseract, 'test-D-tesseract')

path_a = os.path.join(PATH_IMAGES_MANUAL, 'test-A')
path_b = os.path.join(PATH_IMAGES_MANUAL, 'test-B')
path_c = os.path.join(PATH_IMAGES_MANUAL, 'test-C')
path_d = os.path.join(PATH_IMAGES_MANUAL, 'test-D')
path_eng_out = os.path.join(PATH_IMAGES_MANUAL, 'eng')
path_pol_out = os.path.join(PATH_IMAGES_MANUAL, 'pol')


def pack_to_folders():
    paths = [path_a, path_b, path_c, path_d]
    paths_in = [path_a_in, path_b_in, path_c_in, path_d_in]
    for path, path_in in zip(paths, paths_in):
        tsv_file = open(f'{path_in}/in.tsv')
        read_tsv = csv.reader(tsv_file, delimiter="\t")
        for i, row in enumerate(read_tsv):
            if row[1] == 'eng':
                shutil.copy(f'{PATH_IMAGES}/{row[0]}', path_eng_out)
            elif row[1] == 'pol':
                shutil.copy(f'{PATH_IMAGES}/{row[0]}', path_pol_out)
            shutil.copy(f'{PATH_IMAGES}/{row[0]}', path)


if __name__ == '__main__':
    pack_to_folders()
