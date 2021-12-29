from datetime import datetime
import irsdk
import time
from src import ir_vars


class State:  # general variables
    ir_connected = False
    last_car_setup_tick = -1
    last_stop_tyre_state = 0
    welcome_message = r"""
 __    __  _______    ______  
|  \  |  \|       \  /      \ 
| $$\ | $$| $$$$$$$\|  $$$$$$\
| $$$\| $$| $$__| $$| $$ __\$$
| $$$$\ $$| $$    $$| $$|    \
| $$\$$ $$| $$$$$$$\| $$ \$$$$
| $$ \$$$$| $$  | $$| $$__| $$
| $$  \$$$| $$  | $$ \$$    $$
 \$$   \$$ \$$   \$$  \$$$$$$ 
                                
"""  # NRG ASCI LOGO
    tyre_state = {}
    tyre_variables = ir_vars.tyre_wear()


class Tyre:  # takes one corner at a time and puts it into a human readable list

    def __init__(self, inner, middle, outer, corner):
        self.inner = 'I' + str(round(inner * 100, 2)) + '%'
        self.middle = 'M' + str(round(middle * 100, 2)) + '%'
        self.outer = 'O' + str(round(outer * 100, 2)) + '%'
        self.corner = corner

    def list(self):
        tyre_list = (self.corner, self.inner, self.middle, self.outer)
        tyre_tuple = tuple(tyre_list)
        return tyre_tuple

    def min_remaining(self):
        minimum = min(self.list())
        return [self.corner, minimum]


def tyre_dict(leftrear, rightrear, leftfront, rightfront):
    list_of_tuples = [leftfront, rightfront, leftrear, rightrear]
    tyre_dictionary = {}
    for i in list_of_tuples:
        tyre_dictionary[i[0]] = i[1:4]
    return tyre_dictionary


def dict_parser(dict_of_stuff):
    for i in dict_of_stuff:
        tup = dict_of_stuff[i]
        for j in tup:
            print(j)


def tyre_initialise():  # function to set tyres

    lf = Tyre(inner=1.0, middle=1.0, outer=1.0, corner='LF').list()
    rf = Tyre(inner=1.0, middle=1.0, outer=1.0, corner='RF').list()
    lr = Tyre(inner=1.0, middle=1.0, outer=1.0, corner='LR').list()
    rr = Tyre(inner=1.0, middle=1.0, outer=1.0, corner='RR').list()
    State.tyre_state = (tyre_dict(leftrear=lr, rightfront=rf, rightrear=rr, leftfront=lf))


def check_iracing():  # should run run continuously
    if state.ir_connected and not (ir.is_initialized and ir.is_connected):
        state.ir_connected = False
        state.last_car_setup_tick = -1
        state.last_stop_tyre_state = -1
        ir.shutdown()

    elif not state.ir_connected and ir.startup() and ir.is_initialized and ir.is_connected:
        state.ir_connected = True


def get_tyre_wear():
    current_lf = Tyre(inner=ir['LFwearR'], middle=ir['LFwearM'], outer=ir['LFwearL'], corner='LF').list()
    current_lr = Tyre(inner=ir['LRwearR'], middle=ir['LRwearM'], outer=ir['LRwearL'], corner='LR').list()
    current_rr = Tyre(inner=ir['RRwearR'], middle=ir['RRwearM'], outer=ir['RRwearL'], corner='RR').list()
    current_rf = Tyre(inner=ir['RFwearR'], middle=ir['RFwearM'], outer=ir['RFwearL'], corner='RF').list()
    return tyre_dict(current_lr, current_rr, current_lf, current_rf)


def pit_stop_detector():  # checks if we're in the box
    if ir['PlayerCarInPitStall'] and ir['IsOnTrack']:
        in_box = True
    else:
        in_box = False
    return in_box


def do_this():  # placeholder
    if pit_stop_detector():

        current = get_tyre_wear()
        if current == State.tyre_state:
            State.last_stop_tyre_state = 0
        elif State.last_stop_tyre_state < 1:

            State.last_stop_tyre_state += 1
            return dict_parser(current)


def welcome_screen():  # just prettiness
    print(state.welcome_message)
    time.sleep(0.5)
    print('Welcome to the Tyre App')
    time.sleep(0.3)
    now = datetime.now()
    struct_time = now.strftime('%H:%M:%S')
    print(struct_time)


if __name__ == '__main__':  # main loop
    ir = irsdk.IRSDK()
    state = State()
    tyre_initialise()

