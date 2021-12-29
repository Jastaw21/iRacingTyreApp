import irsdk
import vars


class Driver:

    def __init__(self):
        self.current_tyres = None
        self.completed_laps = None
        self.actu_tyres = None
        self.ir = irsdk.IRSDK() # initialise the SDK connection
        self.ir_connected = False
        self.ir_label = 'iRacing Disconnected'
        self.in_box = 'Initialised' # testing placeholder

        self.full = (100, 100, 100)
        self.corners = ['LF', 'RF', 'LR', 'RR']
        self.initial_tyres, self.current_tyres = {i: self.full for i in self.corners},\
                                                 {i: self.full for i in self.corners} # sets initial tyres to be full

        self.tyre_variables = vars.tyre_wear() # grabs the values to pass to the SDK
        self.pit_count = 0
        self.stop_lib = {}
        self.lap_count = 0

    def internal_shutdown(self):
        self.ir_connected = False
        self.pit_count = 0
        self.stop_lib = {}
        self.lap_count = 0
        self.ir_label = 'iRacing Disconnected'
        self.ir.shutdown()

    def check_iracing(self):  # checks if IR connected and sets our LABELS
        if self.ir_connected and not (self.ir.is_initialized and self.ir.is_connected):
            self.internal_shutdown()
            return False
        elif not self.ir_connected and self.ir.startup() and self.ir.is_connected and self.ir.is_initialized:
            self.ir_connected = True
            self.ir_label = 'iRacing Connected'
            return True

    def check_in_box(self):  # checks if we're in the box
        if self.ir['PlayerCarInPitStall'] and self.ir['IsOnTrack']:
            self.in_box = True
            return self.in_box
        else:
            self.in_box = False
            return self.in_box


    def tyre_state(self):
        if self.check_in_box():
            self.actu_tyres = {corner: [self.ir[self.tyre_variables[corner][ind]]
                                        for ind in range(0, 3)] for corner in self.corners}
            if self.actu_tyres == self.current_tyres:
                pass
            else:
                self.current_tyres = self.actu_tyres
                self.pit_count += 1
                self.stop_lib['Stop' + str(self.pit_count)] = self.current_tyres

        elif not self.ir_connected:
            self.stop_lib['Initial'] = self.initial_tyres

        return self.stop_lib

    def lap_number(self):
        if self.ir_connected and self.ir['IsOnTrack']:
            self.completed_laps = self.ir['LapCompleted']

    def main_loop(self):
        self.check_iracing()
        if self.ir_connected:



