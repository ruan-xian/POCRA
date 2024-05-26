import tkinter
import threading
import time
import PIL
import PIL.ImageGrab


def thread_function(window):
    while True:
        time.sleep(2)
        coords = (
            window.winfo_rootx(),
            window.winfo_y(),
            window.winfo_rootx() + window.winfo_width(),
            window.winfo_rooty() + window.winfo_height(),
        )
        print(coords)
        im = PIL.ImageGrab.grab(coords)
        im.save("test_window.png")


win = tkinter.Tk()
win.geometry("400x400")
win.attributes("-alpha", 0.6)
win.wm_attributes("-topmost", 1)
t = threading.Thread(target=thread_function, args=(win,), daemon=True)
t.start()
win.mainloop()
