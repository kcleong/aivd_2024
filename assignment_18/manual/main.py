from itertools import takewhile, dropwhile

import numpy as np

from data.horizontal import H_QA
from data.vertical import V_QA

N = 21


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


def main(horiz_values, vert_values):
    padded_horiz_values = pad_thai(horiz_values, N * N)
    padded_vert_values = pad_thai(vert_values, N * N)

    horiz_matrix = np.array(padded_horiz_values).reshape(N, N)
    vert_matrix = np.array(padded_vert_values).reshape(N, N)
    vert_matrix = vert_matrix.T

    for h_row_index, h_row in enumerate(horiz_matrix):
        row = []
        for h_cell_index, h_cell in enumerate(h_row):
            row.append(
                f"{h_cell.upper()} / {vert_matrix[h_row_index][h_cell_index].upper()}"
            )

        print("\t|\t".join(row))


def pick_value(values, index):
    for value in values:
        if type(value) is list:
            yield value[index]
            continue

        yield value


if __name__ == "__main__":
    main(H_QA.values(), V_QA.values())
