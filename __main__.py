from pokereader import *
from areapicker import *
from PIL import ImageGrab
import time
import logging
import tkinter
import threading

loglevel = logging.DEBUG

logging.basicConfig(
    format="%(levelname)s:%(message)s",
    level=loglevel,
)

terminate = False


root = tkinter.Tk("PokeRogue OCR Assistant")
root.geometry("200x200")

text_var = tkinter.StringVar()

label = tkinter.Label(root, textvariable=text_var)
label.pack(fill=tkinter.X)


def start_picker():
    logging.info("Starting area picker")
    w = open_picker()


picker_button = tkinter.Button(root, text="Set OCR area", command=start_picker)
picker_button.pack(fill=tkinter.X)


def ocr_task():
    with get_api() as api:
        while True:
            if terminate:
                break
            area = get_coords()
            if area is not None:
                im = preprocess(ImageGrab.grab(area))
                if loglevel <= logging.DEBUG:
                    im.save("debug.png")
                results = recognize_pokemon(im, api)
                logging.info(results)

                resultString = "\n".join(
                    [f"{r[0][1]} ({(int)(r[0][0]*100)}%)" for r in results]
                )
                text_var.set(resultString)
            time.sleep(2)


ocr_thread = threading.Thread(target=ocr_task)
ocr_thread.start()


def end():
    global terminate
    terminate = True
    logging.info("Terminating")
    root.destroy()


root.protocol("WM_DELETE_WINDOW", end)
root.mainloop()
