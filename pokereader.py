from tesserocr import PyTessBaseAPI, PSM, RIL, iterate_level
from PIL import Image
from PIL import ImageFilter
from PIL import ImageDraw
import json
import textdistance
import logging
import io
from os import path

__all__ = [
    "extract_pokemon",
    "recognize_pokemon",
    "get_api",
    "pkmn_list",
    "preprocess",
    "get_boxes",
    "process_user_blacklist",
    "preprocess_settings",
]

names_path = path.abspath(path.join(path.dirname(__file__), "pokemon_names.json"))
with io.open(names_path, encoding="utf8") as f:
    pkmn_list = json.load(f)
# charset = {c for p in pkmn_list for c in p}
# print("".join(sorted(charset)))
charset_string = " '-.2:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzé♀♂"


class PreprocessSettings:
    def __init__(
        self, bw_thresh, inv_bw_thresh, invert, resize_factor, blur_size, minfilter_size
    ):
        self.bw_threshold = bw_thresh
        self.inv_bw_threshold = inv_bw_thresh
        self.invert = invert
        self.resize_factor = resize_factor
        self.blur_size = blur_size
        self.minfilter_size = minfilter_size

        self.lut = []
        self.inverted_lut = []
        self.update_lut()

    def update_lut(self):
        self.lut = [0 if x > self.bw_threshold else 255 for x in range(256)]
        inverted_lut = [0 if x < self.inv_bw_threshold else 255 for x in range(256)]


preprocess_settings = PreprocessSettings(
    bw_thresh=240,
    inv_bw_thresh=75,
    invert=False,
    resize_factor=1,
    blur_size=0,
    minfilter_size=3,
)


def preprocess(image):
    pps = preprocess_settings
    im2 = image.convert("L").point(pps.lut if not pps.invert else pps.inverted_lut)
    im2 = im2.resize(
        ((int)(im2.width * pps.resize_factor), (int)(im2.height * pps.resize_factor)),
        Image.LANCZOS,
    )
    if pps.blur_size > 0:
        im2 = im2.filter(ImageFilter.GaussianBlur(pps.blur_size))
    if pps.minfilter_size > 1:
        im2 = im2.filter(ImageFilter.MinFilter(pps.minfilter_size))
    return im2


SIMILARITY_THRESHOLD = 0.55
BLACKLIST = ["Revive", "Ether", "Potion", "Super Potion", "Full Heal", "Lure"]

user_blacklist = []


def process_user_blacklist(lines):
    global user_blacklist
    user_blacklist = [line.strip() for line in lines.splitlines()]


def extract_pokemon(word):
    lw = word.lower()
    best_candidate = (0, "Placeholder")
    for candidate in pkmn_list:
        dist = textdistance.levenshtein.normalized_similarity(lw, candidate.lower())
        if dist > best_candidate[0]:
            best_candidate = (dist, candidate)
    for candidate in BLACKLIST:
        dist = textdistance.levenshtein.normalized_similarity(lw, candidate.lower())
        if dist >= best_candidate[0] and dist > SIMILARITY_THRESHOLD:
            logging.debug(f"Skipped blacklisted word {candidate} (input: {word})")
            return None
    for candidate in user_blacklist:
        dist = textdistance.levenshtein.normalized_similarity(lw, candidate.lower())
        if dist >= best_candidate[0] and dist > SIMILARITY_THRESHOLD:
            logging.debug(f"Skipped user blacklist word {candidate} (input: {word})")
            return None
    res = best_candidate if best_candidate[0] >= SIMILARITY_THRESHOLD else None

    if res is None and best_candidate[0] > SIMILARITY_THRESHOLD - 0.2:
        logging.debug(f"{word}: {best_candidate}")

    return res


def recognize_pokemon(image, api):
    result = []
    api.SetImage(image)
    api.Recognize()
    ri = api.GetIterator()
    level = RIL.TEXTLINE

    for r in iterate_level(ri, level):

        try:
            text = r.GetUTF8Text(level).strip()
        except Exception as err:
            logging.info(err)
            continue

        res = extract_pokemon(text)
        if res is not None:
            result.append((res, text))

    return result


def get_boxes(image, api):
    api.SetImage(image)
    api.Recognize()
    ri = api.GetIterator()
    level = RIL.TEXTLINE

    boxed_image = image.copy().convert("RGB")
    draw = ImageDraw.Draw(boxed_image)

    for r in iterate_level(ri, level):
        try:
            text = r.GetUTF8Text(level).strip()
        except Exception as err:
            logging.warning(err)
            continue
        bbox = r.BoundingBox(level)
        draw.rectangle(bbox, outline="red", width=2)
        draw.text(
            ((bbox[0] + bbox[2]) / 2, bbox[1]),
            text,
            fill="red",
            align="center",
            anchor="md",
            font_size=25 * preprocess_settings.resize_factor,
        )

    return boxed_image


def get_api():
    api = PyTessBaseAPI(r"C:\Program Files\Tesseract-OCR\tessdata", psm=PSM.SPARSE_TEXT)
    api.SetVariable(
        "tessedit_char_whitelist",
        charset_string,
    )

    return api


def main():

    # preprocess image

    im = Image.open(r"samples/sample4.png")
    im = preprocess(im)

    with get_api() as api:
        print(recognize_pokemon(im, api))
        get_boxes(im, api).save("boxed.png")


if __name__ == "__main__":
    main()
