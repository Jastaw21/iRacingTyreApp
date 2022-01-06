import tkinter as tk
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


class Root(tk.Tk):
    def __init__(self):
        super().__init__()

        # classes we need to call
        self.options = Options()


        # root info
        self.title("NRG Tyre App")
        self.configure(bg=self.options.colours["bg"])
        self.minsize(300, 150)
        self.ir_app = irta.Driver()

        # gutter
        self.gutter_frame = ttk.Frame()
        self.gutter_frame.pack()





root = Root()
root.mainloop()
