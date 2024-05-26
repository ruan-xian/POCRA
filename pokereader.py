from tesserocr import PyTessBaseAPI, PSM, RIL, iterate_level
from PIL import Image
from PIL import ImageFilter
import pandas as pd
import textdistance
import tkinter
import logging

__all__ = ["extract_pokemon", "recognize_pokemon", "get_api", "pkmn_list", "preprocess"]

df = pd.read_csv(r"Pokemon.csv")
pkmn_list = df["Name"].tolist()

BW_THRESHOLD = 240
lut = [0 if x > BW_THRESHOLD else 255 for x in range(256)]

SIMILARITY_THRESHOLD = 0.68


def extract_pokemon(word):
    best_candidate = (0, "placeholder")
    for candidate in pkmn_list:
        dist = textdistance.levenshtein.normalized_similarity(word, candidate)
        if dist > best_candidate[0]:
            best_candidate = (dist, candidate)
    res = best_candidate if best_candidate[0] >= SIMILARITY_THRESHOLD else None

    if res is None and best_candidate[0] > SIMILARITY_THRESHOLD - 0.2:
        logging.debug(best_candidate)

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


def get_api():
    return PyTessBaseAPI(
        r"C:\Program Files\Tesseract-OCR\tessdata", psm=PSM.SPARSE_TEXT
    )


def preprocess(image):
    im2 = image.convert("L").point(lut)
    im2 = im2.filter(ImageFilter.SMOOTH)
    return im2


def main():

    # preprocess image

    im = Image.open(r"sample3.png")
    im = preprocess(im)
    im.save("sample_out.png")

    with get_api() as api:
        print(recognize_pokemon(im, api))


if __name__ == "__main__":
    main()
