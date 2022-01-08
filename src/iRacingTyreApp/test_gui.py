from datetime import datetime
from random import uniform
import time
import tkinter as tk
import tkinter.messagebox
from tkinter import ttk
import app as irta
import config as CFG
from PIL import ImageColor, Image, ImageTk


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
        self.current_tyres = None
        self.ir_app = irta.Driver()
        self.stop_list = ['Initial']

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
            return "XX"

    @property
    def current_tyre_state(self):
        j = self.ir_app.current_tyres
        self.current_tyres = j
        return j

    @property
    def current_tyre_temps(self):
        return self.ir_app.current_temps

    @property
    def last_lap(self):
        if self.ir_app.ir_connected:
            return self.ir_app.last_lap_time
        else:
            return "xx"

    @property
    def stop_lib(self):
        if self.ir_app.ir_connected:
            return self.ir_app.stop_lib


class TyreFrame(ttk.Frame):
    def __init__(self, parent, corner, reference):
        super().__init__(parent)
        self.reference = reference
        self.configure(height=240, width=120, borderwidth=5, relief="groove")
        for i in range(1, 4):
            self.columnconfigure(i, weight=1, minsize=35)
        self.grid_propagate(False)
        # pointer labels
        self.label = ttk.Label(self, text=corner, anchor="center")
        self.label.grid(row=1, column=1, columnspan=3, sticky="WE")
        self.wear_pointer = ttk.Label(self, text="Wear", anchor="center")
        self.wear_pointer.grid(row=2, column=1, columnspan=3, sticky="WE")
        self.temps_pointer = ttk.Label(self, text="TEMPS", anchor="center")
        self.temps_pointer.grid(row=5, column=1, columnspan=3, sticky="WE")
        self.left = ttk.Label(self)
        self.middle = ttk.Label(self)
        self.right = ttk.Label(self)
        if corner[0].lower() == "l":
            self.left.configure(text="O")
            self.middle.configure(text="M")
            self.right.configure(text="I")
        else:
            self.left.configure(text="I")
            self.middle.configure(text="M")
            self.right.configure(text="O")
        self.left.grid(row=3, column=1)
        self.middle.grid(row=3, column=2)
        self.right.grid(row=3, column=3)

        # wear labels
        self.left_wear = tk.StringVar(value=100)
        self.middle_wear = tk.StringVar(value=100)
        self.right_wear = tk.StringVar(value=100)
        self.l_lab = ttk.Label(self, textvariable=self.left_wear)
        self.m_lab = ttk.Label(self, textvariable=self.middle_wear)
        self.r_lab = ttk.Label(self, textvariable=self.right_wear)
        self.l_lab.grid(row=4, column=1)
        self.m_lab.grid(row=4, column=2)
        self.r_lab.grid(row=4, column=3)

        # temp labels
        self.left_temp = tk.StringVar()
        self.middle_temp = tk.StringVar()
        self.right_temp = tk.StringVar()
        self.l_temp = ttk.Label(self, textvariable=self.left_temp)
        self.m_temp = ttk.Label(self, textvariable=self.middle_temp)
        self.r_temp = ttk.Label(self, textvariable=self.right_temp)
        self.l_temp.grid(row=6, column=1)
        self.m_temp.grid(row=6, column=2)
        self.r_temp.grid(row=6, column=3)

    def set_labels(self, values, mode):
        if mode == "wear":
            self.left_wear.set(values[0])
            self.middle_wear.set(values[1])
            self.right_wear.set(values[2])
        else:
            self.left_temp.set(values[0])
            self.middle_temp.set(values[1])
            self.right_temp.set(values[2])


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
        self.DARKF = "Gutter.TFrame"

        # root info
        self.HEIGHT = "650"
        self.WIDTH = "700"
        self.title("NRG Tyre App")
        self.configure(bg=self.options.colours["background"])
        self.geometry(self.WIDTH + "x" + self.HEIGHT)
        self.resizable(False, False)

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
        self.option_menu = ttk.OptionMenu(self.right_frame, self.stop_selected, *self.variables.stop_list,
                                          command=self.print_var)
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
        self.sess_time_pointer.grid(row=2, column=1, sticky="w")
        self.sess_time_value = ttk.Label(self.right_frame, style=self.LIGHTL)
        self.sess_time_value.configure(textvariable=self.session_time)
        self.sess_time_value.grid(row=2, column=2)

        # track temp
        self.track_temp = tk.StringVar()
        self.tt_pointer = ttk.Label(self.right_frame, style=self.LIGHTL)
        self.tt_pointer.configure(text="Track Temp:")
        self.tt_pointer.grid(row=3, column=1, sticky="w")
        self.tt_value = ttk.Label(self.right_frame, style=self.LIGHTL)
        self.tt_value.configure(textvariable=self.track_temp)
        self.tt_value.grid(row=3, column=2)

        # track name
        self.track_name = tk.StringVar()
        self.track_pointer = ttk.Label(self.right_frame, style=self.LIGHTL)
        self.track_pointer.configure(text="Track:")
        self.track_pointer.grid(row=4, column=1, sticky="w")
        self.track_value = ttk.Label(self.right_frame, style=self.LIGHTL)
        self.track_value.configure(textvariable=self.track_name)
        self.track_value.grid(row=4, column=2)

        # lap time
        self.last_lap = tk.StringVar()
        self.lap_pointer = ttk.Label(self.right_frame, style=self.LIGHTL)
        self.lap_pointer.configure(text="Lap time:")
        self.lap_pointer.grid(row=5, column=1, sticky="w")
        self.lap_time = ttk.Label(self.right_frame, style=self.LIGHTL)
        self.lap_time.configure(textvariable=self.last_lap)
        self.lap_time.grid(row=5, column=2)
        self.right_frame.pack(side="right", fill="y")

        """LEFT FRAME TO HOLD INDIVIDUAL TYRES"""
        self.left_frame = ttk.Frame(self, style=self.DARKF)
        self.left_frame.configure(width=int(self.WIDTH) * (2 / 3))
        self.left_frame.configure(borderwidth=5, relief="groove")
        self.left_frame.pack(fill="both", expand=True)
        for i in [1, 2]:
            self.left_frame.grid_rowconfigure(i, weight=1)
            self.left_frame.grid_columnconfigure(i, weight=1)

        """TYRE FRAMES"""
        lr = TyreFrame(
            parent=self.left_frame, corner="Left Rear".upper(), reference="LR"
        )
        lr.grid(row=2, column=1)
        rr = TyreFrame(
            parent=self.left_frame, corner="Right Rear".upper(), reference="RR"
        )
        rr.grid(column=2, row=2)
        lf = TyreFrame(
            parent=self.left_frame, corner="Left Front".upper(), reference="LF"
        )
        lf.grid(column=1, row=1)
        rf = TyreFrame(
            parent=self.left_frame, corner="Right Front".upper(), reference="RF"
        )
        rf.grid(row=1, column=2)
        for child in self.left_frame.winfo_children():
            child.grid_configure(**self.options.large_padding)
            for label in child.winfo_children():
                label.configure(style=self.LIGHTL)
                label.grid_configure(**self.options.padding)

        """LOGO PANE"""
        self.logo = tk.Canvas(self.right_frame, width=382, height=87)
        self.logo.pack(side="bottom")
        self.img = Image.open("NRG.png")
        self.source_img = ImageTk.PhotoImage(self.img)
        self.logo.create_image(0, 0, anchor=tk.NW, image=self.source_img)

    def refresh_labels(self):
        self.current_time.set(self.variables.get_time())
        self.iracing_state.set(self.variables.get_ir_state)
        self.session_time.set(self.variables.get_session_time)
        self.track_temp.set(self.variables.track_temp)
        self.track_name.set(self.variables.track_id)
        self.last_lap.set(self.variables.last_lap)
        self.handle_tyre_wear(
            wear_dict=self.variables.current_tyre_state,
            temp_dict=self.variables.current_tyre_temps,
        )

    def handle_tyre_wear(self, wear_dict, temp_dict):
        for tyre in self.left_frame.winfo_children():
            corner = tyre.reference
            wear = wear_dict[corner]
            temp = temp_dict[corner]
            tyre.set_labels(wear, mode="wear")
            tyre.set_labels(temp, mode="temp")

    def local_loop(self):
        self.variables.ir_app.main_loop()
        self.refresh_labels()
        self.after(6, self.local_loop)

    def my_destroy(self):
        self.variables.ir_app.internal_shutdown()
        time.sleep(uniform(0.3, 1.6))
        self.destroy()

    def print_var(self,value):
        print(value)


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
