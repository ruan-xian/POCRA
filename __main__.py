from pokereader import *
from areapicker import *
from PIL import ImageGrab
import time
import logging

loglevel = logging.DEBUG

logging.basicConfig(
    format="%(levelname)s:%(message)s",
    level=loglevel,
)

area = engage_picker()

with get_api() as api:
    while True:
        im = preprocess(ImageGrab.grab(area))
        if loglevel <= logging.DEBUG:
            im.save("debug.png")
        logging.info(recognize_pokemon(im, api))
        time.sleep(2)
