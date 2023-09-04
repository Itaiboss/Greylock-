
import board

from kmk.kmk_keyboard import KMKKeyboard as _KMKKeyboard

from kmk.scanners import DiodeOrientation

class MyKeyboard(_KMKKeyboard):
    def __init__(self):
        # create and register the scanner
        self.matrix = MatrixScanner(
            # required arguments:
            column_pins=self.col_pins,
            row_pins=self.row_pins,
            # optional arguments with defaults:
            columns_to_anodes=DiodeOrientation.COL2ROW,
            interval=0.02,  # Debounce time in floating point seconds
            max_events=64
        )
