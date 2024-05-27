from pokereader import *
from areapicker import *
from autodex import *
from PIL import ImageGrab
import time
import logging
import tkinter as tk
from tkinter import ttk
import sv_ttk
import threading

loglevel = logging.INFO

logging.basicConfig(
    format="%(levelname)s:%(message)s",
    level=loglevel,
)

terminate = False


root = tk.Tk("PokeRogue OCR Assistant")
root.title("PokeRogue OCR Assistant")
root.geometry("700x200")

sv_ttk.set_theme("dark")

ttk.Style().configure("TButton", justify=tk.CENTER, anchor="center")

left_frame = ttk.LabelFrame(root, text="Options", width=100, height=200, border=5)
left_frame.grid(row=0, column=0, padx=5, pady=5, sticky=tk.N + tk.S)
root.rowconfigure(0, weight=1)


def start_picker():
    logging.info("Starting area picker")
    w = open_picker()


picker_button = ttk.Button(left_frame, text="Set OCR area", command=start_picker)
picker_button.pack(fill=tk.X)

auto_open_value = tk.BooleanVar()
auto_open_value.set(True)
auto_open_toggle = ttk.Checkbutton(
    left_frame, text="Auto-open Pokedex", variable=auto_open_value
)
auto_open_toggle.pack(fill=tk.X)

invert_text_value = tk.BooleanVar()
invert_text_value.set(False)
invert_text_toggle = ttk.Checkbutton(
    left_frame, text="Invert OCR text color", variable=invert_text_value
)
invert_text_toggle.pack(fill=tk.X)

right_frame = ttk.LabelFrame(
    root, text="Detection Results", width=300, height=200, border=5
)
right_frame.grid(row=0, column=1, padx=5, pady=5, sticky=tk.NSEW)
root.columnconfigure(1, weight=1)


def dump_image():
    im = preprocess(ImageGrab.grab(get_coords()), invert=invert_text_value.get())
    im.save("dump.png")


picker_button = ttk.Button(left_frame, text="Dump read image", command=dump_image)
picker_button.pack(fill=tk.X)

ocr_results = []
last_opened_pokemon = None
last_auto_pokemon = None
dynamic_buttons = []


def open_entry(index):
    global last_opened_pokemon
    last_opened_pokemon = ocr_results[index][0][1]
    click_pokemon(last_opened_pokemon)


def generate_buttons():
    global dynamic_buttons

    def create_button(index):
        return ttk.Button(
            right_frame,
            text="Placeholder",
            command=lambda: open_entry(index),
        )

    if len(ocr_results) != len(dynamic_buttons):
        if len(dynamic_buttons) > len(ocr_results):
            for b in dynamic_buttons[len(ocr_results) :]:
                b.destroy()
            dynamic_buttons = dynamic_buttons[: len(ocr_results)]
        else:
            for i in range(len(dynamic_buttons), len(ocr_results)):
                b = create_button(i)
                b.pack(fill=tk.BOTH, side=tk.LEFT, expand=True, padx=5, pady=5)
                dynamic_buttons.append(b)

    for i, ((confidence, pkmn), read_text) in enumerate(ocr_results):
        dynamic_buttons[i].config(
            text=f"{pkmn}\n\nConfidence: {(int)(confidence*100)}%\n\nDetected text:\n{read_text}"
        )


def ocr_task():
    global ocr_text
    global ocr_results

    with get_api() as api:
        while True:
            if terminate:
                break
            area = get_coords()
            if area is not None:
                im = preprocess(ImageGrab.grab(area), invert=invert_text_value.get())
                if loglevel <= logging.INFO:
                    im.save("debug.png")
                ocr_results = recognize_pokemon(im, api)
                logging.info(ocr_results)

                ocr_text = "\n".join(
                    [f"{r[0][1]} ({(int)(r[0][0]*100)}%)" for r in ocr_results]
                )
            time.sleep(2)


ocr_thread = threading.Thread(target=ocr_task)
ocr_thread.start()


def end():
    global terminate
    terminate = True
    logging.info("Terminating")
    root.destroy()


def periodic_update():
    global last_auto_pokemon

    generate_buttons()
    if len(ocr_results) > 0:
        auto_candidate = ocr_results[0][0][1]
        if (
            auto_candidate != last_opened_pokemon
            and auto_candidate != last_auto_pokemon
            and auto_open_value.get()
        ):
            last_auto_pokemon = auto_candidate
            open_entry(0)
    root.after(500, periodic_update)


root.wm_attributes("-topmost", 1)
root.protocol("WM_DELETE_WINDOW", end)
root.after(500, periodic_update)
root.mainloop()
