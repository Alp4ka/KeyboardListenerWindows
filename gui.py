import threading
from tkinter import *

from keylogger import KeyLoggerCallback


class MainApp(threading.Thread, KeyLoggerCallback):
    WINDOW_WIDTH = 600
    WINDOW_HEIGHT = 130
    WINDOW_BACKGROUND_COLOR = "black"
    WINDOW_ALPHA = 0.5
    LABEL_FONT = ("Arial", 44)
    LABEL_FOREGROUND_COLOR = "white"
    LABEL_BACKGROUND_COLOR = "black"

    def __init__(self):
        super().__init__()
        self.label = None
        self.app = None

    def run(self):
        self.app = Tk()

        # +------- CALCULATIONS -------+
        x_shift = int((self.app.winfo_screenwidth() / 2) - (self.WINDOW_WIDTH / 2))
        y_shift = int((self.app.winfo_screenheight() / 2) - (self.WINDOW_HEIGHT / 2))

        # +------- CONFIGURE WINDOW -------+
        self.app.protocol("WM_DELETE_WINDOW", self.close)
        self.app.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}+{x_shift}+{y_shift}")
        self.app.overrideredirect(True)
        self.app.wm_attributes("-topmost", True)
        self.app.wm_attributes("-alpha", self.WINDOW_ALPHA)
        self.app.configure(background=self.WINDOW_BACKGROUND_COLOR)

        # +------ CONFIGURE LABEL -------+
        self.label = Label(self.app)
        self.label.configure(justify=CENTER,
                             fg=self.LABEL_FOREGROUND_COLOR,
                             bg=self.LABEL_BACKGROUND_COLOR,
                             width=self.WINDOW_WIDTH,
                             height=self.WINDOW_HEIGHT,
                             font=self.LABEL_FONT)
        self.label.pack()

        # +------- MAIN LOOP -------+
        self.app.mainloop()

    def clear_input(self):
        self.label.configure(text="")

    def set_input(self, value: str):
        self.label.configure(text=value)

    def get_input(self):
        return self.label["text"]

    def show(self):
        self.app.focus_force()
        self.app.deiconify()

    def hide(self):
        self.app.withdraw()

    def toggle_state(self):
        if self.app.state() != "withdrawn":
            self.hide()
        else:
            self.show()

    def close(self):
        self.app.destroy()

