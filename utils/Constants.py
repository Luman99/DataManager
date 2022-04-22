import os

PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PATH = os.path.abspath(os.path.join(PATH, ".."))
PATH_DATA = os.path.join(PATH, 'data')
PATH_IMAGES = os.path.join(PATH_DATA, 'images')
PATH_DATA_METRICS = os.path.join(PATH_DATA, 'data_for_calculate_metrics')
