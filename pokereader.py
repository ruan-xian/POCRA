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
]

names_path = path.abspath(path.join(path.dirname(__file__), "pokemon_names.json"))
with io.open(names_path, encoding="utf8") as f:
    pkmn_list = json.load(f)
# charset = {c for p in pkmn_list for c in p}
# print("".join(sorted(charset)))
charset_string = " '-.2:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzé♀♂"

BW_THRESHOLD = 240
INV_BW_THRESHOLD = 75
LAX_THRESHOLD = 175
INV_LAX_THRESHOLD = 80

lut = [0 if x > BW_THRESHOLD else 255 for x in range(256)]
inverted_lut = [0 if x < INV_BW_THRESHOLD else 255 for x in range(256)]
lax_lut = [0 if x < LAX_THRESHOLD else 255 for x in range(256)]
lax_inverted_lut = [0 if x > INV_LAX_THRESHOLD else 255 for x in range(256)]

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
            font_size=50,
        )

    return boxed_image


def get_api():
    api = PyTessBaseAPI(r"C:\Program Files\Tesseract-OCR\tessdata", psm=PSM.SPARSE_TEXT)
    api.SetVariable(
        "tessedit_char_whitelist",
        charset_string,
    )

    return api


def preprocess(image, invert=False):
    im2 = image.convert("L").point(lut if not invert else inverted_lut)
    im2 = im2.resize((im2.width * 2, im2.height * 2), Image.LANCZOS)
    im2 = im2.filter(ImageFilter.GaussianBlur(2))
    return im2


def main():

    # preprocess image

    im = Image.open(r"sample4.png")
    im = preprocess(im)

    with get_api() as api:
        print(recognize_pokemon(im, api))
        get_boxes(im, api).save("boxed.png")


if __name__ == "__main__":
    main()
