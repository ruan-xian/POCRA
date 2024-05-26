import tkinter
import threading
import time
import PIL
import PIL.ImageGrab

__all__ = ["get_coords", "engage_picker"]

coords = (0, 0, 100, 100)


def get_coords():
    return coords


def engage_picker():
    win = tkinter.Tk()
    win.geometry("400x400")
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
    win.mainloop()
    return coords


def main():
    engage_picker()
    im = PIL.ImageGrab.grab(coords)
    im.save("test_window.png")


if __name__ == "__main__":
    main()
