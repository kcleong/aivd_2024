from itertools import takewhile, dropwhile
from pprint import pprint

import numpy as np

from data.horizontal import H_QA
from data.vertical import V_QA

N = 21


def generator(limit, values):
    count = 0
    while count < limit:
        for letter in values:
            if count >= limit:
                return
            yield letter
            count += 1


def pad_thai(values, length, padding_char="."):

    top_values = list(takewhile(lambda x: x != "", values))
    bottom_values = list(dropwhile(lambda x: x != "", values))
    bottom_values = list(dropwhile(lambda x: x == "", bottom_values))

    top_chars = [x for x in "".join(top_values)]
    bottom_chars = [x for x in "".join(bottom_values)]

    return (
        top_chars
        + [padding_char] * (length - len(top_chars + bottom_chars))
        + bottom_chars
    )


horiz_values = pad_thai(H_QA.values(), N * N)
vert_values = pad_thai(V_QA.values(), N * N)

horiz_matrix = np.array(horiz_values).reshape(N, N)
vert_matrix = np.array(vert_values).reshape(N, N)
vert_matrix = vert_matrix.T

print("")
for h_row_index, h_row in enumerate(horiz_matrix):
    row = []
    for h_cell_index, h_cell in enumerate(h_row):
        row.append(
            f"{h_cell.upper()} / {vert_matrix[h_row_index][h_cell_index].upper()}"
        )

    print("\t|\t".join(row))
