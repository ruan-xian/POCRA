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

loglevel = logging.WARNING

logging.basicConfig(
    format="%(levelname)s:%(message)s",
    level=loglevel,
)


ocr_initialized = False
terminate = False


root = tk.Tk("PokeRogue OCR Assistant")
root.title("PokeRogue OCR Assistant")
root.geometry("1000x200")

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


def dump_image():
    im = preprocess(ImageGrab.grab(get_coords()), invert=invert_text_value.get())
    boxed_image = get_boxes(im, get_api())
    boxed_image.save("dump.png")
    boxed_image.show()


dumper_button = ttk.Button(left_frame, text="Dump read image", command=dump_image)
dumper_button.pack(fill=tk.X)

user_blacklist_string = ""


def open_blacklist():
    global user_blacklist_string

    blacklist_window = tk.Toplevel(root)
    blacklist_window.title("User blacklist")
    blacklist_window.geometry("300x400")
    blacklist_window.wm_attributes("-topmost", 1)

    blacklist_input = tk.Text(blacklist_window, relief=tk.SOLID, yscrollcommand=True)
    blacklist_input.grid(row=0, column=0, sticky=tk.NSEW, padx=5, pady=5)
    blacklist_window.rowconfigure(0, weight=1)
    blacklist_window.columnconfigure(0, weight=1)
    blacklist_input.insert(tk.END, user_blacklist_string)

    button_frame = ttk.Frame(blacklist_window)
    button_frame.grid(row=1, column=0, sticky=tk.NSEW, padx=5, pady=(0, 5))

    def save_blacklist():
        global user_blacklist_string
        user_blacklist_string = blacklist_input.get("1.0", tk.END).strip() + "\n"
        process_user_blacklist(user_blacklist_string)
        blacklist_window.destroy()

    def cancel_blacklist():
        blacklist_window.destroy()

    save_blacklist_button = ttk.Button(
        button_frame, text="Save", command=save_blacklist
    )
    cancel_blacklist_button = ttk.Button(
        button_frame, text="Cancel", command=cancel_blacklist
    )
    save_blacklist_button.grid(row=0, column=0, sticky=tk.EW, padx=5)
    cancel_blacklist_button.grid(row=0, column=1, sticky=tk.EW, padx=5)
    button_frame.columnconfigure(0, weight=7)
    button_frame.columnconfigure(0, weight=3)


open_blacklist_button = ttk.Button(
    left_frame, text="Edit blacklist", command=open_blacklist
)
open_blacklist_button.pack(fill=tk.X, pady=5)

right_frame = ttk.LabelFrame(
    root,
    text="Detection Results (click to open Dex entry)",
    width=300,
    height=200,
    border=5,
)
right_frame.grid(row=0, column=1, padx=5, pady=5, sticky=tk.NSEW)
root.columnconfigure(1, weight=1)


ocr_results = []
last_opened_pokemon = None
last_auto_pokemon = None
dynamic_buttons = []

set_area_prompt = ttk.Label(
    right_frame, text="Set the OCR area to begin", anchor=tk.CENTER, justify=tk.CENTER
)
set_area_prompt.grid(row=0, column=0, sticky=tk.NSEW)
right_frame.rowconfigure(0, weight=8)
right_frame.columnconfigure(0, weight=1)


def open_entry(index):
    global last_opened_pokemon
    last_opened_pokemon = ocr_results[index][0][1]
    click_pokemon(last_opened_pokemon)


def generate_buttons():
    global dynamic_buttons
    global set_area_prompt

    if not ocr_initialized:
        return

    if set_area_prompt is not None:
        set_area_prompt.destroy()
        set_area_prompt = None

    def create_buttons(index):
        def open_task():
            focus_window()
            t = threading.Thread(target=lambda: open_entry(index))
            t.start()

        def blacklist_pokemon():
            global user_blacklist_string
            user_blacklist_string += ocr_results[index][0][1] + "\n"
            process_user_blacklist(user_blacklist_string)

        button = ttk.Button(
            right_frame,
            text="Placeholder",
            command=open_task,
        )
        button.grid(row=0, column=index, sticky=tk.NSEW, padx=5, pady=5)

        blacklist_button = ttk.Button(
            right_frame,
            text="Blacklist",
            command=blacklist_pokemon,
        )
        blacklist_button.grid(row=1, column=index, sticky=tk.NSEW, padx=5, pady=(0, 5))

        right_frame.columnconfigure(index, weight=1)
        dynamic_buttons.append((button, blacklist_button))

    if len(ocr_results) != len(dynamic_buttons):
        if len(dynamic_buttons) > len(ocr_results):
            for b, bb in dynamic_buttons[len(ocr_results) :]:
                b.destroy()
                bb.destroy()
            dynamic_buttons = dynamic_buttons[: len(ocr_results)]
        else:
            for i in range(len(dynamic_buttons), len(ocr_results)):
                create_buttons(i)

    for i, ((confidence, pkmn), read_text) in enumerate(ocr_results):
        dynamic_buttons[i][0].config(
            text=f"{pkmn}\nConfidence: {(int)(confidence*100)}%\nDetected text:\n{read_text}"
        )


def ocr_task():
    global ocr_text
    global ocr_results
    global ocr_initialized

    with get_api() as api:
        while get_coords() is None:
            if terminate:
                return
            time.sleep(0.2)
        ocr_initialized = True

        while True:
            if terminate:
                break

            area = get_coords()
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
    close_window()


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
            t = threading.Thread(target=lambda: open_entry(0))
            t.start()

    root.after(500, periodic_update)


root.wm_attributes("-topmost", 1)
root.protocol("WM_DELETE_WINDOW", end)
root.after(500, periodic_update)
root.mainloop()
