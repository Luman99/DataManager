import warnings
from collections import namedtuple
from bs4 import BeautifulSoup, Tag

CommonFormatData = namedtuple('CommonFormatData', [
    'tokens',  # List[str]
    'token_positions',  # List[List[int]]
    'token_scores',  # List[float]
    'pages',  # List[List[int]]
    'pages_positions',  # List[List[int]]
    'lines',  # List[List[int]]
    'lines_positions',  # List[List[int]]
    'tokens_page_numbers',  # List[int]
    'lines_page_numbers'  # List[int]]
])


WORD_CLASSES = ["ocrx_word", "ocr_word"]
LINE_CLASSES = ["ocrx_line", "ocr_line"]


def build_common_format_data(hocr_data: bytes) -> CommonFormatData:
    soup = BeautifulSoup(hocr_data.decode('utf-8'), features="lxml")
    token_counter = 0

    # structure is updated inside other functions
    data = CommonFormatData([], [], [], [], [], [], [], [], [])

    for i_p, page_hocr in enumerate(soup.find_all("div", {"class": "ocr_page"})):
        page_start = token_counter
        token_counter = _add_tokens_of_element(data, page_hocr, i_p, token_counter)
        _add_lines(data, page_hocr, i_p, page_start)

        data.pages.append([page_start, token_counter])
        data.pages_positions.append(get_tag_bb(page_hocr))
    return data


def _add_tokens_of_element(data: CommonFormatData, element: BeautifulSoup, i_p: int,
                           token_counter: int):
    for t in element.find_all("span", {"class": WORD_CLASSES}):
        data.tokens.append(t.text)
        data.tokens_page_numbers.append(i_p)
        data.token_positions.append(get_tag_bb(t))
        data.token_scores.append(get_tag_conf(t))
        token_counter += 1
    return token_counter


def _add_lines(data: CommonFormatData, page_hocr: BeautifulSoup, i_p: int, page_start: int):
    hocr_spans = page_hocr.find_all("span")
    token_counter = page_start
    for span_hocr in hocr_spans:
        line_start = token_counter
        token_counter += _get_number_of_tokens_in_element(span_hocr)

        if any(c in LINE_CLASSES for c in span_hocr.get("class")):
            data.lines.append([line_start, token_counter])
            data.lines_positions.append(get_tag_bb(span_hocr))
            data.lines_page_numbers.append(i_p)


def _get_number_of_tokens_in_element(element: BeautifulSoup) -> int:
    return len(element.find_all("span", {"class": WORD_CLASSES}))


def get_tag_conf(bs_tag: Tag) -> float:
    score = None
    for snippet in get_tag_title(bs_tag):
        if 'x_wconf' in snippet:
            score = snippet.strip().split(" ")[1]
            break

    if score is None:
        warnings.warn("Processor: No scores provided, set 1")
        return 1

    return float(score) / 100


def get_tag_title(bs_tag: Tag):
    title_split = bs_tag.get("title").split(";")
    return [t_part for t_part in title_split]


def str2int(value: str) -> int:
    return int(float(value))


def get_tag_bb(bs_tag: Tag):
    ranges = None
    for snippet in get_tag_title(bs_tag):
        if 'bbox' in snippet:
            ranges = snippet.strip().split(" ")[1:]
            break

    if ranges is None:
        pass

    return [str2int(ranges[0]), str2int(ranges[1]), str2int(ranges[2]), str2int(ranges[3])]


