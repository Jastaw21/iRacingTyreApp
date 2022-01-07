import datetime
import time
import tkinter as tk
import tkinter.messagebox
from tkinter import ttk
import app as irta
import config as CFG
import ir_vars


class Options:  # Just to hold variables for GUI
    def __init__(self):
        self.cfg = CFG.AppConfig()
        self.config = self.cfg.config_dict
        self.colours = dict(fg="#00313b", bg="#defcff")
        self.inv_colours = dict(fg=self.colours["bg"], bg=self.colours["fg"])
        self.padding = dict(padx=1, pady=1)
        self.large_padding = dict(padx=5, pady=5)
        self.tyres = ir_vars.tyre_wear()
        self.info_for_creation = dict(
            LF={"side": "left", "text": "LF", "Tparent": "mf"},
            RF={"side": "right", "text": "RF", "Tparent": "mf"},
            LR={"side": "left", "text": "LR", "Tparent": "mf"},
            RR={"side": "left", "text": "LF", "Tparent": "mf"},
        )
        self.no_ir_message = "where iR?"


class Variables:
    def __init__(self):
        self.ir_app = irta.Driver()

    @staticmethod
    def get_time():
        time_now = datetime.datetime.now()
        formatted_time = datetime.datetime.strftime(time_now, "%H:%M:%S")
        return formatted_time

    def get_ir_state(self):
        return self.ir_app.ir_label


class Root(tk.Tk):
    def __init__(self):
        super().__init__()

        # classes we need to call
        self.options = Options()

        # variables instance
        self.variables = Variables()

        # root info
        self.HEIGHT = "450"
        self.WIDTH = "700"
        self.title("NRG Tyre App")
        self.configure(bg=self.options.colours["bg"])
        self.geometry(self.WIDTH + "x" + self.WIDTH)

        # gutter
        self.gutter_frame = ttk.Frame(self)
        self.gutter_frame.configure(borderwidth=5, relief="raised")
        # time label
        self.current_time = tk.StringVar()
        self.gutt_time = ttk.Label(self.gutter_frame)
        self.gutt_time.configure(textvariable=self.current_time)
        self.gutt_time.pack(side="left")
        # iracing state
        self.iracing_state = tk.StringVar(value="Initialised")
        self.iracing_label = ttk.Label(self.gutter_frame)
        self.iracing_label.configure(textvariable=self.iracing_state)
        self.iracing_label.pack(side="right")
        # pack
        self.gutter_frame.pack(side="bottom", fill="x")

        # quit button
        self.button = ttk.Button(self)
        self.button.configure(text="Close", command=self.my_destroy)
        self.button.pack(side="top", fill="x")

        # right frame
        self.right_frame = ttk.Frame(self)
        self.right_frame.configure(
            width=int(self.WIDTH) / 3, borderwidth=3, relief="groove"
        )
        self.right_frame.pack_propagate(False)
        # option menu
        self.stop_selected = tk.StringVar(value="Initial")
        self.option_menu = ttk.OptionMenu(self.right_frame, variable=self.stop_selected)
        self.option_menu.configure(takefocus=True)
        self.option_menu.pack()
        self.right_frame.pack(side="right", fill="y")

    def refresh_time(self):
        self.current_time.set(self.variables.get_time())

    def refresh_irState(self):
        self.iracing_state.set(self.variables.get_ir_state())

    def local_loop(self):
        self.variables.ir_app.main_loop()
        self.refresh_time()
        self.refresh_irState()
        self.after(5, self.local_loop)

    def my_destroy(self):
        self.variables.ir_app.internal_shutdown()
        time.sleep(2)
        self.destroy()


class NRG:
    def __init__(self):
        self.gui = Root()
        self.gui.button.configure(command=self.on_closing)
        self.gui.local_loop()
        self.gui.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.gui.mainloop()

    def on_closing(
        self,
    ):  # catch window close - will build this out later to handle logging etc
        if tkinter.messagebox.askokcancel(
            "End Process", "Are you sure you want to quit?"
        ):
            self.gui.my_destroy()


if __name__ == "__main__":
    nrg = NRG()
