from typing import List, Optional


def make_common_format_json(doc_id: str, tokens: List[str], tokens_positions: List[List[int]],
                            tokens_scores: List[str], pages_value: Optional[List[str]] = None,
                            pages_positions: Optional[List[str]] = None, lines_value: Optional[List[str]] = None,
                            lines_positions: Optional[List[str]] = None):

    if pages_value is None:
        pages_value = []
    if pages_positions is None:
        pages_positions = []
    if lines_value is None:
        lines_value = []
    if lines_positions is None:
        lines_positions = []

    pages = {'version': '1.0', 'structure_value': pages_value,
             'positions': pages_positions}
    lines = {'version': '1.0', 'structure_value': lines_value,
             'positions': lines_positions}
    structures = {'pages': pages,
                  'lines': lines}

    file_to_save = {'doc_id': doc_id, 'tokens': tokens,
                    'positions': tokens_positions,
                    'scores': tokens_scores,
                    'sctructures': structures}

    return file_to_save
