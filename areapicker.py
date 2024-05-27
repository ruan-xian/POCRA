import tkinter
import PIL
import PIL.ImageGrab
import time

__all__ = ["get_coords", "open_picker"]

coords = None


def get_coords():
    return coords


def open_picker():
    win = tkinter.Tk("Screen area picker")
    win.title("Close this window to select the OCR area")
    win.geometry("600x300")
    win.attributes("-alpha", 0.6)
    win.wm_attributes("-topmost", 1)

    def save_coords():
        global coords
        coords = (
            win.winfo_rootx(),
            win.winfo_y(),
            win.winfo_rootx() + win.winfo_width(),
            win.winfo_rooty() + win.winfo_height(),
        )
        win.destroy()

    win.protocol("WM_DELETE_WINDOW", save_coords)
    return win


def main():
    open_picker()
    while coords is None:
        time.sleep(1)
    im = PIL.ImageGrab.grab(coords)
    im.save("test_window.png")


if __name__ == "__main__":
    main()
