import time
import math
import irsdk
import vars


class Driver:

    def __init__(self):
        self.actu_tyres = None
        self.ir = irsdk.IRSDK()
        self.ir_connected = False
        self.ir_label = 'iRacing Disconnected'
        self.in_box = 'Initialised'
        self.full = (66, 66, 66)
        self.corners = ['LF', 'RF', 'LR', 'RR']
        self.initial_tyres = {i: self.full for i in self.corners}
        self.current_tyres = self.initial_tyres
        self.tyre_variables = vars.tyre_wear()
        self.pit_count = 0
        self.stop_lib = {}
        self.lap_count = 0

    def internal_shutdown(self):
        self.ir_connected = False
        self.current_tyres = {}
        self.pit_count = 0
        self.stop_lib = {}
        self.lap_count = 0
        self.ir_label = 'iRacing Disconnected'
        self.ir.shutdown()

    def check_iracing(self):  # checks if IR connected and sets our labels
        if self.ir_connected and not (self.ir.is_initialized and self.ir.is_connected):
            self.internal_shutdown()
            return False

        elif not self.ir_connected and self.ir.startup() and self.ir.is_connected and self.ir.is_initialized:
            self.ir_connected = True
            self.ir_label = 'iRacing Connected'
            return True

    def check_in_box(self):  # checks if we're in the box

        if self.ir_connected:

            if self.ir['PlayerCarInPitStall'] and self.ir['IsOnTrack']:
                self.in_box = True

                return self.in_box

            else:
                self.in_box = False

                return self.in_box

        else:
            pass

    def tyre_state(self):

        if self.check_iracing() and self.check_in_box():

            self.lap_count = self.ir['LapCompleted']
            self.actu_tyres = {i: [self.ir[self.tyre_variables[i][ind]] for ind in range(0,3)] for i in self.corners}
            print(self.actu_tyres)

            if self.actu_tyres == self.current_tyres:
                pass
            else:
                self.current_tyres = self.actu_tyres
                self.pit_count += 1
                self.stop_lib['Stop' + str(self.pit_count)] = self.current_tyres

        elif not self.ir_connected:
            self.stop_lib['Initial'] = self.initial_tyres

        return self.stop_lib




if __name__ == '__main__':
    d = Driver()
    while True:
        d.tyre_state()
        time.sleep(12/3.764)
