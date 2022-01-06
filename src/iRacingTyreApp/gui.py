import tkinter as tk
from datetime import datetime
import app as irta
import ir_vars
import config as CFG

LABELS = ["LF", "LR", "RF", "RR"]


class App(tk.Tk):  # root window
    def __init__(self):
        super().__init__()
        self.options = Options()
        self.title("NRG Tyre App")
        self.configure(bg=self.options.colours["bg"])
        self.minsize(300, 150)
        self.ir_app = irta.Driver()


    def my_destroy(self):
        ir_app.internal_shutdown()
        self.destroy()


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


class Button(tk.Button):  # Quit Button
    def __init__(self, Tparent, button_text):
        super().__init__(Tparent)
        self.butt = tk.Button
        self.configure(
            text=button_text,
            command=gui.destroy,
            **gui.options.colours,
            activeforeground=gui.options.inv_colours["fg"],
            activebackground=gui.options.inv_colours["bg"],
            relief="raised",
        )
        self.pack(fill="x", side="top")


class MainFrame(tk.Frame):  # holds all the shit on the left
    def __init__(self, Tparent):
        super().__init__(Tparent)
        self.configure(bg=gui.options.colours["bg"])
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.pack(fill="both", side="left", expand="true")


# noinspection PyUnresolvedReferences
class RightFrame(tk.Frame):  # to hold the drop down
    def __init__(self, Tparent):
        super().__init__(Tparent)

        self.stop_list = ["Initial"]  # will work out why I put this here
        self.configure(
            bg=gui.options.colours["bg"], relief="raised", borderwidth=2
        )  # this is the frame

        # option menu options
        self.option = tk.StringVar(value="Initial")
        self.dropdown = tk.OptionMenu(self, self.option, *self.stop_list)
        self.dropdown.configure(
            **gui.options.colours,
            activebackground=gui.options.inv_colours["bg"],
            activeforeground=gui.options.inv_colours["fg"],
        )
        self.dropdown.children["menu"].configure(
            **gui.options.colours, activebackground=gui.options.inv_colours["bg"]
        )

        self.dropdown.pack(fill="both")

        # pack itself
        self.pack(fill="y", **gui.options.padding)

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
        self.configure(bg=gui.options.colours["bg"], borderwidth=3, relief="raised")
        # frame deets

        # time label
        self.time_label = tk.Label(self, text="TODO")
        self.time_label.configure(**gui.options.colours)

        # iracing state label
        self.iracing_label = tk.Label(self, text="")
        self.iracing_label.configure(**gui.options.colours)

        # packs
        self.iracing_label.pack(**gui.options.padding, side="right")
        self.time_label.pack(**gui.options.padding, side="left")
        self.pack(**gui.options.padding, side="bottom", fill="x")


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
            bg=gui.options.colours["fg"],
            borderwidth=5,
            relief="raised",
            **gui.options.padding,
        )

        self.tyre_label = tk.Label(self, text=self.config)
        self.tyre_label.configure(**gui.options.inv_colours, width=10, height=9)

        self.tyre_label.pack()

        self.grid(**self.gridding_info[text], **gui.options.padding)


class ResultFrame(tk.Frame):
    def __init__(self, Tparent):
        super().__init__(Tparent)
        self.stint_length = tk.IntVar()
        self.track_temp = tk.DoubleVar()
        self.track = tk.StringVar()
        self.configure(bg=gui.options.colours["bg"])

        # stint length pointer label
        self.stint_length_label = tk.Label(self, textvariable=self.stint_length, **gui.options.colours)
        self.stint_length_label.grid(column=2, row=1, sticky='e')
        # stint length value label
        self.stint_label = tk.Label(self, text="Stint Length:", **gui.options.colours)
        self.stint_label.grid(column=1, row=1, sticky='w')

        # track temp pointer label
        self.track_temp_pointer = tk.Label(self, text="Track Temp:", **gui.options.colours)
        self.track_temp_pointer.grid(row=2, column=1, sticky='w')
        # track temp value label
        self.track_temp_value = tk.Label(self, textvariable=self.track_temp, **gui.options.colours)
        self.track_temp_value.grid(row=2, column=2, sticky='e')

        # session time pointer label
        self.session_time = tk.StringVar()
        self.sess_time_pointer = tk.Label(self, text="Session Time:", **gui.options.colours)
        self.sess_time_pointer.grid(row=3, column=1, sticky='w')
        # session time value label
        self.sess_time_value = tk.Label(self, textvariable=self.session_time, **gui.options.colours)
        self.sess_time_value.grid(row=3, column=2, sticky='e')

        # track info pointer
        self.track_pointer = tk.Label(self, text="Track:", **gui.options.colours)
        self.track_pointer.grid(row=4, column=1, sticky='w')
        # track info value
        self.track_label = tk.Label(self, textvariable=self.track, **gui.options.colours)
        self.track_label.grid(row=4, column=2, sticky='e')

        # self pack
        self.pack(side="bottom", fill="both", expand="true")


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
        # call the main_loop of irSDK - this will refresh all
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
        gui.after(5, self.local_loop)  # loop it

    def set_labels(self):
        # iracing independent variables
        ch.gut.time_label.configure(text=self.time_now)
        ch.gut.iracing_label.configure(text=self.iracing_state)

        # bring info from option menu and handle
        optiontoshow = ch.rightframe.option.get()
        stop_info = self.local_stop_dict[optiontoshow]
        for value in self.labels.keys():
            self.labels[value].tyre_label.configure(text=stop_info["wear"][value])
        ch.resf.stint_length.set(stop_info["length"])

        # iRacing Dependent variables, we need to check if iRacing is connected before doing anything
        if ir_app.ir_connected:
            ch.resf.track_temp.set(ir_app.track_tempVar)
            ch.resf.session_time.set(ir_app.session_time)
            ch.resf.track.set(ir_app.track_short)
        else:
            ch.resf.track_temp.set(gui.options.no_ir_message)
            ch.resf.session_time.set(gui.options.no_ir_message)
            ch.resf.track.set(gui.options.no_ir_message)

    def refresh_stop_list(self):
        if self.local_stop_list != ch.rightframe.stop_list:
            ch.rightframe.refresh(self.local_stop_list)


class ChildWidgets:  # just to wrap the child widgets up in a class to avoid top level decs
    def __init__(self):
        self.button = Button(gui, "Close")
        self.gut = Gutter(Tparent=gui)
        self.mf = MainFrame(Tparent=gui)
        self.rightframe = RightFrame(Tparent=gui)
        self.lf_frame = TyreFrame(Tparent=self.mf, text="LF")
        self.lr_frame = TyreFrame(Tparent=self.mf, text="LR")
        self.rf_frame = TyreFrame(Tparent=self.mf, text="RF")
        self.rr_frame = TyreFrame(Tparent=self.mf, text="RR")
        self.resf = ResultFrame(Tparent=self.rightframe)


if __name__ == "__main__":
    ir_app = irta.Driver()
    gui = App()
    ch = ChildWidgets()
    variables = Variables()
    variables.local_loop()
    gui.mainloop()
