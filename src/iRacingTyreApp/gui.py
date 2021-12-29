import tkinter as tk
from datetime import datetime
import app as tyre_app
import ir_vars

LABELS = ['LF', 'LR', 'RF', 'RR']


class Options:  # Just to hold variables for GUI
    colours = dict(fg='#00313b', bg='#defcff')
    inv_colours = {'fg': colours['bg'], 'bg': colours['fg']}
    padding = dict(padx=1, pady=1)
    large_padding = dict(padx=5, pady=5)

    tyres = ir_vars.tyre_wear()
    info_for_creation = dict(LF={'side': 'left', 'text': 'LF', 'container': 'mainframe'},
                             RF={'side': 'right', 'text': 'RF', 'container': 'mainframe'},
                             LR={'side': 'left', 'text': 'LR', 'container': 'mainframe'},
                             RR={'side': 'left', 'text': 'LF', 'container': 'mainframe'})


class Button(tk.Button):  # Quit Button
    def __init__(self, container, button_text):
        super().__init__(container)
        self.butt = tk.Button
        self.configure(text=button_text, command=tyre_app.destroy,
                       **options.colours, activeforeground=options.inv_colours['fg'],
                       activebackground=options.inv_colours['bg'], relief='raised')
        self.pack(fill='x', side='top')


class MainFrame(tk.Frame):  # holds all the shit on the left
    def __init__(self, container):
        super().__init__(container)
        self.configure(bg=options.colours['bg'])
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=2)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=2)
        self.pack(fill='both', side='left', expand='true')


class RightFrame(tk.Frame):  # to hold the drop down
    def __init__(self, container):
        super().__init__(container)
        self.stop_list = ['Initial']
        self.configure(bg=options.colours['bg'])
        self.option = tk.StringVar(value='Initial')
        self.filler = tk.OptionMenu(self, self.option, *self.stop_list)
        self.filler.configure(**options.colours, width=25,
                              activebackground=options.inv_colours['bg'], activeforeground=options.inv_colours['fg'])
        self.filler.pack(fill='both')
        self.pack(side='right', fill='both', expand='true', **options.large_padding)

    def refresh(self, stops):
        self.stop_list = stops
        menu = self.filler.children['menu']
        menu.delete(0, 'end')
        for stop_index in stops:
            menu.add_command(label=stop_index, command=lambda v=stop_index: self.option.set(v))


class Gutter(tk.Frame):  # this is the bottom frame to contain time & IR state
    def __init__(self, container):
        super().__init__(container)
        self.configure(bg=options.colours['bg'],
                       borderwidth=3, relief='raised')
        # frame deets

        # time label
        self.time_label = tk.Label(self, text='TODO')
        self.time_label.configure(**options.colours)

        # iracing state label
        self.iracing_label = tk.Label(self, text='')
        self.iracing_label.configure(**options.colours)

        # packs
        self.iracing_label.pack(**options.padding, side='right')
        self.time_label.pack(**options.padding, side='left')
        self.pack(**options.padding, side='bottom', fill='x')


class TyreFrame(tk.Frame):  # Frames for each corner of the car

    def __init__(self, container, side, text):
        super().__init__(container)
        self.gridding_info = {'LF': {'row': 1, 'column': 1},
                              'RF': {'row': 1, 'column': 2},
                              'RR': {'row': 2, 'column': 2},
                              'LR': {'row': 2, 'column': 1}}  # this drives the packing info

        self.side = side  # takes the input
        self.text = text
        self.areas = ['L', 'M', 'R']
        self.config = [self.text + 'wear' + i for i in self.areas]  # Constructs the variables to pass to  irsdk,
        # i.e LFwearM
        self.configure(bg=options.colours['fg'], borderwidth=2, relief='raised', **options.large_padding)
        self.tyre_label = tk.Label(self, text=self.config)
        self.tyre_label.configure(**options.inv_colours, font=50)
        self.tyre_label.pack()
        self.grid(**self.gridding_info[self.text],
                  **options.large_padding, sticky='ew')


class App(tk.Tk):  # root window
    def __init__(self):
        super().__init__()
        self.title('NRG Tyre App')
        self.configure(bg=options.colours['bg'])
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
        self.time_now = datetime.now().strftime('%A %b %y %H:%M:%S')

        # where to find the class instances to update the frames
        self.labels = {'LF': mychildren.lf_frame, 'LR': mychildren.lr_frame,
                       'RF': mychildren.rf_frame, 'RR': mychildren.rr_frame}

    def local_loop(self):
        # call the main_loop of irSDK
        ir_app.main_loop()

        # refresh session info
        self.time_now = datetime.now().strftime('%A %b %y %H:%M:%S')
        self.iracing_state = ir_app.ir_label
        self.current_tyres = ir_app.current_tyres

        # update our list of stops so we can later compare them
        self.local_stop_list = [stop for stop in self.local_stop_dict.keys()]

        # currently unutilised
        self.last_lap_time = ir_app.last_lap_time
        self.completed_laps = ir_app.completed_laps

        # check if there has been another stop, if so, update option menu
        if self.local_stop_list != mychildren.rightframe.stop_list:
            mychildren.rightframe.refresh(self.local_stop_list)  # probably not ideal but i think it works
        else:
            pass

        # call seperate function to update LABELS with refreshed info
        self.set_labels()

        tyre_app.after(10, self.local_loop)

    def set_labels(self):
        mychildren.gutter.time_label.configure(text=self.time_now)
        mychildren.gutter.iracing_label.configure(text=self.iracing_state)
        optiontoshow = mychildren.rightframe.option.get()
        stop_info = self.local_stop_dict[optiontoshow]
        for value in self.labels.keys():
            self.labels[value].tyre_label.configure(text=stop_info[0][value])

    def treat_wear(self, stop_values):
        pass
        # TODO


class MYChildren:
    def __init__(self):
        self.button = Button(tyre_app, 'Close')
        self.gutter = Gutter(container=tyre_app)
        self.mainframe = MainFrame(container=tyre_app)
        self.rightframe = RightFrame(container=tyre_app)
        frames = [TyreFrame(container=self.mainframe, side=options.info_for_creation[i]['side'],
                            text=options.info_for_creation[i]['text']) for i in LABELS]
        names = ['lf_frame', 'lr_frame', 'rf_frame', 'rr_frame']

        self.lf_frame = TyreFrame(container=self.mainframe, side='left', text='LF')
        self.lr_frame = TyreFrame(container=self.mainframe, side='left', text='LR')
        self.rf_frame = TyreFrame(container=self.mainframe, side='right', text='RF')
        self.rr_frame = TyreFrame(container=self.mainframe, side='right', text='RR')


if __name__ == '__main__':
    options = Options
    ir_app = tyre_app.Driver()
    tyre_app = App()
    mychildren = MYChildren()
    variables = Variables()
    variables.local_loop()
    tyre_app.mainloop()
