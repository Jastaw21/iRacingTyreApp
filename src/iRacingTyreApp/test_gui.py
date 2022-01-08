from datetime import datetime
from random import uniform
import time
import tkinter as tk
import tkinter.messagebox
from tkinter import ttk
import app as irta
import config as CFG
import ir_vars
from PIL import ImageColor


class Options:  # Just to hold variables for GUI
    def __init__(self):
        self.cfg = CFG.AppConfig()
        self.config = self.cfg.config_dict
        self.colours = dict(foreground="#000421", background="#dee2ff")
        self.darkened = dict(
            foreground=self.darken(self.colours["foreground"]),
            background=self.darken(self.colours["background"]),
        )
        self.lightened = dict(
            foreground=self.lighten(self.colours["foreground"]),
            background=self.lighten(self.colours["background"]),
        )
        self.inv_colours = dict(
            foreground=self.colours["background"], background=self.colours["foreground"]
        )
        self.padding = dict(padx=1, pady=1)
        self.large_padding = dict(padx=5, pady=5)
        self.tyres = ir_vars.tyre_wear()


    @staticmethod
    def darken(hexd):
        rgb = ImageColor.getcolor(hexd, "RGB")
        darkened = tuple([int(round(i * 0.85, 0)) for i in rgb])
        hexd = "#{:02x}{:02x}{:02x}".format(*darkened)
        return hexd

    @staticmethod
    def lighten(hexl):
        rgb = ImageColor.getcolor(hexl, "RGB")
        darkened = tuple([min(255, int(round(i * 1.05, 0))) for i in rgb])
        hexl = "#{:02x}{:02x}{:02x}".format(*darkened)
        return hexl


class Variables:
    def __init__(self):
        self.stop_lib = None
        self.ir_app = irta.Driver()

    @staticmethod
    def get_time():
        time_now = datetime.now()
        formatted_time = datetime.strftime(time_now, "%H:%M:%S")
        return formatted_time

    @property
    def get_ir_state(self):
        return self.ir_app.ir_label

    @property
    def get_session_time(self):
        if self.ir_app.ir_connected:
            return self.ir_app.session_time
        else:
            return "xx"

    @property
    def track_temp(self):
        if self.ir_app.ir_connected:
            return self.ir_app.track_tempVar
        else:
            return "xx"

    @property
    def track_id(self):
        if self.ir_app.ir_connected:
            return self.ir_app.track_short
        else:
            return 'XX'

    @property
    def current_tyres(self):
        if self.ir_app.ir_connected:
            self.stop_lib = self.ir_app.stop_lib
            return self.current_tyres
        else:
            return 'XX'

    @property
    def last_lap(self):
        if self.ir_app.ir_connected:
            return self.ir_app.last_lap_time
        else:
            return "xx"

        


class Root(tk.Tk):
    def __init__(self):
        super().__init__()

        """SUBCLASS THE CLASSES  - GOAL BEING TO MAKE THE GUI ONE CALLABLE OBJECT """
        self.options = Options()
        self.style = ttk.Style()
        self.variables = Variables()

        """STYLES"""
        self.style.configure(
            "Gutter.TFrame",
            foreground=self.options.darkened["foreground"],
            background=self.options.darkened["background"],
        )
        self.style.configure("RightFrame.TFrame", **self.options.lightened)
        self.style.configure("Quit.TButton", **self.options.darkened)
        self.style.configure("Darkened.TLabel", **self.options.darkened)
        self.style.configure("Lightened.TLabel", **self.options.lightened)
        self.style.configure("Lightened.TMenubutton", **self.options.lightened)
        self.LIGHTL = "Lightened.TLabel"

        # root info
        self.HEIGHT = "650"
        self.WIDTH = "700"
        self.title("NRG Tyre App")
        self.configure(bg=self.options.colours["background"])
        self.geometry(self.WIDTH + "x" + self.HEIGHT)
        self.minsize()

        """THE GUTTER BAR"""
        self.gutter_frame = ttk.Frame(self, style="Gutter.TFrame")
        self.gutter_frame.configure(borderwidth=5, relief="raised")
        # time label
        self.current_time = tk.StringVar()
        self.gutt_time = ttk.Label(self.gutter_frame, style="Darkened.TLabel")
        self.gutt_time.configure(textvariable=self.current_time)
        self.gutt_time.pack(side="left")
        # iracing state
        self.iracing_state = tk.StringVar(value="Initialised")
        self.iracing_label = ttk.Label(self.gutter_frame, style="Darkened.TLabel")
        self.iracing_label.configure(textvariable=self.iracing_state)
        self.iracing_label.pack(side="right")
        # NRG LABEL
        self.nrg_label = ttk.Label(self.gutter_frame, style="Darkened.TLabel")
        self.nrg_label.configure(text="NRG - Tyre App")
        self.nrg_label.pack()

        self.gutter_frame.pack(side="bottom", fill="x")

        """QUIT BUTTON"""
        self.button = ttk.Button(self, style="Quit.TButton")
        self.button.configure(text="Close", command=self.my_destroy)
        self.button.pack(side="top", fill="x")

        """RIGHT FRAME"""
        self.right_frame = ttk.Frame(self, style="RightFrame.TFrame")
        self.right_frame.configure(
            width=int(self.WIDTH) / 3, borderwidth=3, relief="groove"
        )
        self.right_frame.grid_propagate(False)
        self.columnconfigure(1, weight=2)
        self.columnconfigure(2, weight=1)
        # option menu
        self.stop_selected = tk.StringVar(value="Initial")
        self.option_menu = ttk.OptionMenu(
            self.right_frame, variable=self.stop_selected, style="Lightened.TMenubutton"
        )
        self.option_menu.configure(takefocus=True)
        self.option_menu.grid(column=2, row=1, sticky="e")
        self.option_label = ttk.Label(
            self.right_frame, text="Select a Stop:", style="Lightened.TLabel"
        )
        self.option_label.grid(column=1, row=1, sticky="w")

        # session time
        self.session_time = tk.StringVar()
        self.sess_time_pointer = ttk.Label(self.right_frame, style=self.LIGHTL)
        self.sess_time_pointer.configure(text="iR Session Time:")
        self.sess_time_pointer.grid(row=2, column=1,sticky='w')
        self.sess_time_value = ttk.Label(self.right_frame, style=self.LIGHTL)
        self.sess_time_value.configure(textvariable=self.session_time)
        self.sess_time_value.grid(row=2, column=2)

        # track temp
        self.track_temp = tk.StringVar()
        self.tt_pointer = ttk.Label(self.right_frame, style=self.LIGHTL)
        self.tt_pointer.configure(text='Track Temp:')
        self.tt_pointer.grid(row=3, column=1,sticky='w')
        self.tt_value = ttk.Label(self.right_frame, style=self.LIGHTL)
        self.tt_value.configure(textvariable=self.track_temp)
        self.tt_value.grid(row=3, column=2)

        # track name
        self.track_name = tk.StringVar()
        self.track_pointer = ttk.Label(self.right_frame, style=self.LIGHTL)
        self.track_pointer.configure(text='Track:')
        self.track_pointer.grid(row=4, column=1,sticky='w')
        self.track_value = ttk.Label(self.right_frame, style=self.LIGHTL)
        self.track_value.configure(textvariable=self.track_name)
        self.track_value.grid(row=4, column=2)

        # lap time
        self.last_lap = tk.StringVar()
        self.lap_pointer = ttk.Label(self.right_frame,style=self.LIGHTL)
        self.lap_pointer.configure(text='Lap time:')
        self.lap_pointer.grid(row=5,column=1,sticky='w')
        self.lap_time = ttk.Label(self.right_frame,style=self.LIGHTL)
        self.lap_time.configure(textvariable=self.last_lap)
        self.lap_time.grid(row=5,column=2)
        self.right_frame.pack(side="right", fill="y")

    def refresh_labels(self):
        self.current_time.set(self.variables.get_time())
        self.iracing_state.set(self.variables.get_ir_state)
        self.session_time.set(self.variables.get_session_time)
        self.track_temp.set(self.variables.track_temp)
        self.track_name.set(self.variables.track_id)
        self.last_lap.set(self.variables.last_lap)

    def local_loop(self):
        self.variables.ir_app.main_loop()
        self.refresh_labels()
        self.after(5, self.local_loop)

    def my_destroy(self):
        self.variables.ir_app.internal_shutdown()
        time.sleep(uniform(0.3, 1.6))
        self.destroy()


class NRG:
    def __init__(self):
        self.gui = Root()
        self.gui.button.configure(command=self.on_closing)
        self.gui.local_loop()

        self.gui.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.gui.mainloop()

    def on_closing(self):
        # catch window close - will build this out later to handle logging etc
        if tkinter.messagebox.askokcancel(
                "End Process", "Are you sure you want to quit?"
        ):
            self.gui.my_destroy()


if __name__ == "__main__":
    nrg = NRG()
