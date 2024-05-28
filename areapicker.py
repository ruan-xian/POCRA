import tkinter
import PIL
import PIL.ImageGrab
import time

__all__ = ["get_coords", "open_picker"]

coords = None
active_picker = None
pwg = None  # previous window geometry


def get_coords():
    return coords


def open_picker():
    global active_picker

    win = tkinter.Tk("Screen area picker")
    win.title("Close this window to set the OCR area")

    if pwg is not None:
        win.geometry(f"{pwg[2]-pwg[0]}x{pwg[3]-pwg[1]}+{pwg[0]}+{pwg[1]}")
    else:
        win.geometry("350x200")
    win.attributes("-alpha", 0.6)
    win.wm_attributes("-topmost", 1)

    def save_coords():
        global coords, pwg
        coords = (
            win.winfo_rootx(),
            win.winfo_y(),
            win.winfo_rootx() + win.winfo_width(),
            win.winfo_rooty() + win.winfo_height(),
        )
        pwg = (
            win.winfo_x(),
            win.winfo_y(),
            win.winfo_x() + win.winfo_width(),
            win.winfo_y() + win.winfo_height(),
        )
        win.destroy()

    win.protocol("WM_DELETE_WINDOW", save_coords)
    active_picker = win
    return win


def main():
    while True:
        open_picker()
        active_picker.mainloop()
        im = PIL.ImageGrab.grab(coords)
        im.save("test_window.png")


if __name__ == "__main__":
    main()
