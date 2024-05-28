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
from copy import copy
import json
import os

loglevel = logging.WARNING

logging.basicConfig(
    format="%(levelname)s:%(message)s",
    level=loglevel,
)

settings = {}
if os.path.exists("pocra_settings.json"):
    with open("pocra_settings.json", "r") as f:
        settings = json.load(f)
if settings.get("preprocess_settings") is not None:
    preprocess_settings.load_settings(settings["preprocess_settings"])
    preprocess_settings.update_lut()

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
auto_open_value.set(settings.get("auto_open", True))
auto_open_toggle = ttk.Checkbutton(
    left_frame,
    text="Auto-open Pokedex",
    variable=auto_open_value,
)
auto_open_toggle.pack(fill=tk.X)

pause_value = tk.BooleanVar()
pause_value.set(False)
pause_ocr_toggle = ttk.Checkbutton(
    left_frame,
    text="Pause OCR",
    variable=pause_value,
)
pause_ocr_toggle.pack(fill=tk.X)


def open_preprocess_settings():
    ppw = tk.Toplevel(root)
    ppw.title("Preprocessing settings")
    ppw.wm_attributes("-topmost", 1)

    ppw.columnconfigure(0, weight=2)
    ppw.columnconfigure(1, weight=8)

    before_settings = copy(preprocess_settings)

    # has to be defined before invert so that invert can change its value
    threshold_box = ttk.Spinbox(
        ppw,
        from_=0,
        to=255,
        format="%3.0f",
    )

    invert_var = tk.BooleanVar()
    invert_var.set(preprocess_settings.invert)
    invert_toggle = ttk.Checkbutton(
        ppw,
        text="Invert OCR text color",
        variable=invert_var,
        command=lambda: threshold_box.set(
            preprocess_settings.bw_threshold
            if not invert_var.get()
            else preprocess_settings.inv_bw_threshold
        ),
    )
    invert_toggle.grid(column=0, row=0, columnspan=2, sticky=tk.EW, padx=5, pady=5)
    invert_toggle.var = invert_var

    next_row = 1

    def setup_row(label, field):
        nonlocal next_row
        label.grid(column=0, row=next_row, padx=5, pady=5, sticky=tk.W)
        field.grid(column=1, row=next_row, padx=(0, 5), pady=5, sticky=tk.EW)
        next_row += 1

    threshold_box.set(
        preprocess_settings.bw_threshold
        if not preprocess_settings.invert
        else preprocess_settings.inv_bw_threshold
    )
    setup_row(
        ttk.Label(ppw, text="Threshold", justify=tk.LEFT, anchor="e"), threshold_box
    )

    resize_box = ttk.Spinbox(
        ppw,
        from_=0.5,
        to=4,
        increment=0.5,
        format="%3.1f",
    )
    resize_box.set(preprocess_settings.resize_factor)
    setup_row(
        ttk.Label(ppw, text="Resize factor", justify=tk.LEFT, anchor="e"), resize_box
    )

    blur_box = ttk.Spinbox(
        ppw,
        from_=0,
        to=5,
        increment=0.5,
        format="%3.1f",
    )
    blur_box.set(preprocess_settings.blur_size)
    setup_row(ttk.Label(ppw, text="Blur size", justify=tk.LEFT, anchor="e"), blur_box)

    minfilter_box = ttk.Spinbox(
        ppw,
        from_=1,
        to=7,
        increment=2,
        format="%3.0f",
    )
    minfilter_box.set(preprocess_settings.minfilter_size)
    setup_row(
        ttk.Label(ppw, text="Minfilter size", justify=tk.LEFT, anchor="e"),
        minfilter_box,
    )

    def apply_settings():
        preprocess_settings.invert = invert_var.get()
        if invert_var.get():
            preprocess_settings.inv_bw_threshold = int(threshold_box.get())
        else:
            preprocess_settings.bw_threshold = int(threshold_box.get())
        preprocess_settings.resize_factor = float(resize_box.get())
        preprocess_settings.blur_size = float(blur_box.get())
        preprocess_settings.minfilter_size = int(minfilter_box.get())
        preprocess_settings.update_lut()

    def dump_image():
        apply_settings()
        im = preprocess(ImageGrab.grab(get_coords()))
        boxed_image = get_boxes(im, get_api())
        boxed_image.save("dump.png")
        threading.Thread(target=boxed_image.show).start()

    dumper_button = ttk.Button(ppw, text="Preview image", command=dump_image)
    dumper_button.grid(
        column=0, row=next_row, columnspan=2, sticky=tk.EW, padx=5, pady=5
    )
    next_row += 1
    end_frame = ttk.Frame(ppw)
    end_frame.grid(column=0, row=next_row, columnspan=2, sticky=tk.EW, pady=(0, 5))

    def save_pp_settings():
        apply_settings()
        ppw.destroy()

    def cancel_pp_settings():
        preprocess_settings.invert = before_settings.invert
        preprocess_settings.bw_threshold = before_settings.bw_threshold
        preprocess_settings.inv_bw_threshold = before_settings.inv_bw_threshold
        preprocess_settings.resize_factor = before_settings.resize_factor
        preprocess_settings.blur_size = before_settings.blur_size
        preprocess_settings.minfilter_size = before_settings.minfilter_size
        preprocess_settings.update_lut()
        ppw.destroy()

    save_button = ttk.Button(end_frame, text="Save", command=save_pp_settings)
    cancel_button = ttk.Button(end_frame, text="Cancel", command=cancel_pp_settings)
    save_button.grid(column=0, row=0, sticky=tk.EW, padx=5)
    cancel_button.grid(column=1, row=0, sticky=tk.EW, padx=(0, 5))
    end_frame.columnconfigure(0, weight=7)
    end_frame.columnconfigure(0, weight=3)


preprocess_button = ttk.Button(
    left_frame, text="Preprocessing settings", command=open_preprocess_settings
)
preprocess_button.pack(fill=tk.X)

user_blacklist_string = ""
if settings.get("user_blacklist") is not None:
    user_blacklist_string = settings["user_blacklist"]


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
            if not pause_value.get():
                area = get_coords()
                im = preprocess(ImageGrab.grab(area))
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
    settings.update({"auto_open": auto_open_value.get()})
    settings.update({"preprocess_settings": vars(preprocess_settings)})
    settings.update({"user_blacklist": user_blacklist_string})
    with open("pocra_settings.json", "w") as f:
        json.dump(settings, f)


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
