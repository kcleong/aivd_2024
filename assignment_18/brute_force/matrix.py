from itertools import takewhile, dropwhile

import numpy


class Matrix:
    N = 21

    def __init__(self, horiz_values, vert_values):
        self.horiz_values = horiz_values
        self.vert_values = vert_values

    def print(self):
        padded_horiz_values = self._pad_thai(self.horiz_values, self.N * self.N)
        padded_vert_values = self._pad_thai(self.vert_values, self.N * self.N)

        horiz_matrix = numpy.array(padded_horiz_values).reshape(self.N, self.N)
        vert_matrix = numpy.array(padded_vert_values).reshape(self.N, self.N)
        vert_matrix = vert_matrix.T

        for h_row_index, h_row in enumerate(horiz_matrix):
            row = []
            for h_cell_index, h_cell in enumerate(h_row):
                h_value = h_cell.upper()
                v_value = vert_matrix[h_row_index][h_cell_index].upper()

                if h_value == v_value and h_value != ".":
                    row.append(f"\033[32m{h_value} / {v_value}\033[0m")
                else:
                    row.append(f"{h_value} / {v_value}")

            print("\t|\t".join(row))

    def count_matches(self):
        """
        Count the number of cells where the horizontal and vertical characters match.
        """
        # Calculate the padded values once
        padded_horiz_values = self._pad_thai(self.horiz_values, self.N * self.N)
        padded_vert_values = self._pad_thai(self.vert_values, self.N * self.N)

        # Create NumPy arrays and reshape
        horiz_matrix = numpy.array(padded_horiz_values, dtype=str).reshape(
            self.N, self.N
        )
        vert_matrix = numpy.array(padded_vert_values, dtype=str).reshape(self.N, self.N)
        vert_matrix = vert_matrix.T

        # Ignore dots
        mask = (horiz_matrix != ".") & (vert_matrix != ".")

        # Compare the matrices directly
        match_count = numpy.sum((horiz_matrix == vert_matrix) & mask)

        # Calculate success rate
        total_cells = self.N * self.N
        success_rate = match_count / total_cells

        return match_count, success_rate

    @staticmethod
    def _pad_thai(values, length, padding_char="."):
        top_values = list(takewhile(lambda x: x is not None, values))
        bottom_values = list(dropwhile(lambda x: x is not None, values))
        bottom_values = list(dropwhile(lambda x: x is None, bottom_values))

        top_chars = [x for x in "".join(top_values)]
        bottom_chars = [x for x in "".join(bottom_values)]

        return (
            top_chars
            + [padding_char] * (length - len(top_chars + bottom_chars))
            + bottom_chars
        )
