print("Starting")

import board
import time
import usb_hid
#from kb import KMKKeyboard
import ulab.numpy as np
from kmk.kmk_keyboard import KMKKeyboard
from kmk.scanners.digitalio import MatrixScanner
from kmk.scanners import DiodeOrientation
from kmk.keys import KC
from kmk.handlers.sequences import send_string, simple_key_sequence
from kmk.modules.layers import Layers
from kmk.modules.encoder import EncoderHandler
from kmk.modules.tapdance import TapDance
from kmk.extensions.RGB import RGB
from kmk.extensions.media_keys import MediaKeys
from kmk.modules.potentiometer import PotentiometerHandler
import terminalio
import displayio
from adafruit_display_text import label
from adafruit_st7789 import ST7789
print(dir(board))
#from analogio import AnalogIn
XXXX = KC.NO
# KEYTBOARD SETUP
layers = Layers()
keyboard = KMKKeyboard()

encoder = EncoderHandler()
tapdance = TapDance()
tapdance.tap_time = 250
keyboard.modules = [layers, encoder,tapdance]

BORDER_WIDTH = 20
TEXT_SCALE = 3

# Release any resources currently in use for the displays
displayio.release_displays()

spi = board.SPI()
tft_cs = board.D2
tft_dc = board.D1

display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs,)

display = ST7789(display_bus, width=320, height=170, colstart=35, rotation=90)

# Make the display context
splash = displayio.Group()
display.show(splash)

color_bitmap = displayio.Bitmap(display.width, display.height, 1)
color_palette = displayio.Palette(1)
color_palette[0] = 0x00CAB1  # Bright Green
bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
splash.append(bg_sprite)

# Draw a smaller inner rectangle
inner_bitmap = displayio.Bitmap(
    display.width - (BORDER_WIDTH * 2), display.height - (BORDER_WIDTH * 2), 1
)
inner_palette = displayio.Palette(1)
inner_palette[0] = 0x00CAB1  # Purple
inner_sprite = displayio.TileGrid(
    inner_bitmap, pixel_shader=inner_palette, x=BORDER_WIDTH, y=BORDER_WIDTH
)
splash.append(inner_sprite)

# Draw a label
text_area = label.Label(
    terminalio.FONT,
    text="Hello Brielle!",
    color=0xFFFFFF,
    scale=TEXT_SCALE,
    anchor_point=(0.5, 0.5),
    anchored_position=(display.width // 2, display.height // 2),
)
splash.append(text_area)

keyboard.last_level = -1
# Windows 10
level_steps = 100
level_inc_step = 1

level_lut = [int(x) for x in np.linspace(0, level_steps, 64).tolist()]
def set_sys_vol(state):
    # convert to 0-100
    new_pos = int((state.position / 127) * 64)
    level = level_lut[new_pos]
    print(f"new vol level: {level}")
    print(f"last: {keyboard.last_level}")

    # check if uninitialized
    if keyboard.last_level == -1:
        keyboard.last_level = level
        return

    level_diff = abs(keyboard.last_level - level)
    if level_diff > 0:
        # set volume to new level
        vol_direction = "unknown"
        if level > keyboard.last_level:
            vol_direction = "up"
            cmd = KC.VOLU
        else:
            vol_direction = "down"
            cmd = KC.VOLD

        print(f"Setting system volume {vol_direction} by {level_diff} to reach {level}")
        for i in range(int(level_diff / level_inc_step)):
            hid_report = keyboard._hid_helper.create_report([cmd,NULL])
            hid_report.send()
            hid_report.clear_all()
            hid_report.send()

        keyboard.last_level = level
    return

def slider_handler(state):
    set_sys_vol(state)

fader = PotentiometerHandler()
fader.pins=((board.A3, slider_handler, True),)

#KEY MATRIX
keyboard.col_pins = (board.D9, board.D7, board.D5)
keyboard.row_pins = (board.D6, board.D8, board.D4, board.D3)
keyboard.diode_orientation = DiodeOrientation.COL2ROW
keyboard.matrix = MatrixScanner(keyboard.col_pins,keyboard.row_pins)
#ENCODERS
encoder.pins = ((board.A1, board.A2, board.A0, True, 2),)

# EXTENSIONS
rgb_ext = RGB(pixel_pin = board.D10, num_pixels=15, hue_default=100)
keyboard.extensions.append(rgb_ext)
keyboard.extensions.append(MediaKeys())
keyboard.modules.append(fader)
keyboard.debug_enabled = True

keyboard.keymap = [
    [KC.RGB_MODE_SWIRL, KC.RGB_MODE_KNIGHT, XXXX,
    KC.RGB_MODE_BREATHE_RAINBOW, KC.RGB_MODE_PLAIN, KC.RGB_MODE_BREATHE,
    KC.RGB_MODE_RAINBOW, KC.H, KC.I,
    KC.J, KC.K, KC.L]
]
encoder.map = [((KC.VOLD, KC.VOLU, KC.PAUSE),)]

if __name__ == '__main__':
    keyboard.go()

