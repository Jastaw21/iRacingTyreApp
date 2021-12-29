import tkinter as tk
from datetime import datetime
import app as tyre_app
import ir_vars

LABELS = ["LF", "LR", "RF", "RR"]


class Options:  # Just to hold variables for GUI
    colours = dict(fg="#00313b", bg="#defcff")
    inv_colours = {"fg": colours["bg"], "bg": colours["fg"]}
    padding = dict(padx=1, pady=1)
    large_padding = dict(padx=5, pady=5)

    tyres = ir_vars.tyre_wear()
    info_for_creation = dict(
        LF={"side": "left", "text": "LF", "Tparent": "mf"},
        RF={"side": "right", "text": "RF", "Tparent": "mf"},
        LR={"side": "left", "text": "LR", "Tparent": "mf"},
        RR={"side": "left", "text": "LF", "Tparent": "mf"},
    )


class Button(tk.Button):  # Quit Button
    def __init__(self, Tparent, button_text):
        super().__init__(Tparent)
        self.butt = tk.Button
        self.configure(
            text=button_text,
            command=tyre_app.destroy,
            **options.colours,
            activeforeground=options.inv_colours["fg"],
            activebackground=options.inv_colours["bg"],
            relief="raised"
        )
        self.pack(fill="x", side="top")


class MainFrame(tk.Frame):  # holds all the shit on the left
    def __init__(self, Tparent):
        super().__init__(Tparent)
        self.configure(bg=options.colours["bg"])
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.pack(fill="both", side="left", expand="true")


class RightFrame(tk.Frame):  # to hold the drop down
    def __init__(self, Tparent):
        super().__init__(Tparent)

        self.stop_list = ["Initial"]  # will work out why I put this here
        self.configure(
            bg=options.colours["bg"], relief="raised", borderwidth=2
        )  # this is the frame

        # option menu options
        self.option = tk.StringVar(value="Initial")
        self.dropdown = tk.OptionMenu(self, self.option, *self.stop_list)
        self.dropdown.configure(
            **options.colours,
            activebackground=options.inv_colours["bg"],
            activeforeground=options.inv_colours["fg"]
        )
        self.dropdown.children["menu"].configure(
            **options.colours, activebackground=options.inv_colours["bg"]
        )

        self.dropdown.pack(fill="both")

        # pack itself
        self.pack(side="top", fill="y", **options.padding)

    def refresh(self, stops):
        self.stop_list = stops
        menu = self.dropdown.children["menu"]
        menu.delete(0, "end")
        for stop_index in stops:
            menu.add_command(
                label=stop_index, command=lambda v=stop_index: self.option.set(v)
            )


class Gutter(tk.Frame):  # this is the bottom frame to contain time & IR state
    def __init__(self, Tparent):
        super().__init__(Tparent)
        self.configure(bg=options.colours["bg"], borderwidth=3, relief="raised")
        # frame deets

        # time label
        self.time_label = tk.Label(self, text="TODO")
        self.time_label.configure(**options.colours)

        # iracing state label
        self.iracing_label = tk.Label(self, text="")
        self.iracing_label.configure(**options.colours)

        # packs
        self.iracing_label.pack(**options.padding, side="right")
        self.time_label.pack(**options.padding, side="left")
        self.pack(**options.padding, side="bottom", fill="x")


class TyreFrame(tk.Frame):  # Frames for each corner of the car
    def __init__(self, Tparent, text):
        super().__init__(Tparent)

        self.gridding_info = {  # this drives the gridding info
            "LF": {"row": 1, "column": 1},
            "RF": {"row": 1, "column": 2},
            "RR": {"row": 2, "column": 2},
            "LR": {"row": 2, "column": 1},
        }

        self.areas = ["L", "M", "R"]
        self.config = [text + "wear" + i for i in self.areas]
        # Constructs the variables to pass to  irsdk,
        # i.e LFwearM
        self.configure(
            bg=options.colours["fg"], borderwidth=5, relief="raised", **options.padding
        )

        self.tyre_label = tk.Label(self, text=self.config)
        self.tyre_label.configure(**options.inv_colours, font=50, width=10, height=9)

        self.tyre_label.pack()

        self.grid(**self.gridding_info[text], **options.padding)


class ResultFrame(tk.Frame):
    def __init__(self, Tparent):
        super().__init__(Tparent)
        self.configure(background="green")
        self.text = tk.Label(self, text="jackaksfakdka")
        self.text.pack()
        self.pack(side="bottom", fill="both", expand="true")


class App(tk.Tk):  # root window
    def __init__(self):
        super().__init__()
        self.title("NRG Tyre App")
        self.configure(bg=options.colours["bg"])
        self.minsize(300, 150)

    def my_destroy(self):
        ir_app.internal_shutdown()
        self.destroy()


class Variables:
    def __init__(self):
        # lap info vars
        self.current_tyres = None
        self.iracing_state = None
        self.completed_laps = None
        self.last_lap_time = None
        # grab the 'initial' data
        self.local_stop_dict = ir_app.stop_lib
        self.local_stop_list = [stop for stop in self.local_stop_dict.keys()]
        # time, obvs
        self.time_now = datetime.now().strftime("%A %b %y %H:%M:%S")

        # where to find the class instances to update the frames
        self.labels = {
            "LF": ch.lf_frame,
            "LR": ch.lr_frame,
            "RF": ch.rf_frame,
            "RR": ch.rr_frame,
        }

    def local_loop(self):
        # call the main_loop of irSDK
        ir_app.main_loop()

        # refresh session info
        self.time_now = datetime.now().strftime("%A %b %y %H:%M:%S")
        self.iracing_state = ir_app.ir_label
        self.current_tyres = ir_app.current_tyres

        # update our list of stops so we can later compare them
        self.local_stop_list = [stop for stop in self.local_stop_dict.keys()]

        # currently unutilised
        self.last_lap_time = ir_app.last_lap_time
        self.completed_laps = ir_app.completed_laps

        # check if there has been another stop, if so, update option menu

        self.refresh_stop_list()

        # call seperate function to update LABELS with refreshed info
        self.set_labels()
        tyre_app.after(1000, self.local_loop)  # loop it

    def set_labels(self):
        ch.gut.time_label.configure(text=self.time_now)
        ch.gut.iracing_label.configure(text=self.iracing_state)
        optiontoshow = ch.rightframe.option.get()
        stop_info = self.local_stop_dict[optiontoshow]
        for value in self.labels.keys():
            self.labels[value].tyre_label.configure(text=stop_info[0][value])

    def refresh_stop_list(self):
        if self.local_stop_list != ch.rightframe.stop_list:
            ch.rightframe.refresh(self.local_stop_list)

    def treat_wear(self, stop_values):
        pass
        # TODO


class MYChildren:  # just to wrap the child widgets up in a class to avoid top level decs
    def __init__(self):
        self.button = Button(tyre_app, "Close")
        self.gut = Gutter(Tparent=tyre_app)
        self.mf = MainFrame(Tparent=tyre_app)
        self.rightframe = RightFrame(Tparent=tyre_app)
        self.lf_frame = TyreFrame(Tparent=self.mf, text="LF")
        self.lr_frame = TyreFrame(Tparent=self.mf, text="LR")
        self.rf_frame = TyreFrame(Tparent=self.mf, text="RF")
        self.rr_frame = TyreFrame(Tparent=self.mf, text="RR")
        self.resf = ResultFrame(Tparent=self.rightframe)


if __name__ == "__main__":
    options = Options
    ir_app = tyre_app.Driver()
    tyre_app = App()
    ch = MYChildren()
    variables = Variables()
    variables.local_loop()
    tyre_app.mainloop()
