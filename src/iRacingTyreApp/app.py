import irsdk
import ir_vars


# main class to be called from UI
class Driver:

    def __init__(self):
        # info to drive setup
        self.last_lap_time = None
        self.full = (100, 100, 100)
        self.corners = ['LF', 'RF', 'LR', 'RR']
        self.tyre_variables = ir_vars.tyre_wear()
        # state variables - initialise as None. These get refreshed with every loop
        self.lap_dict = {}
        self.started_laps = None
        self.current_tyres = None
        self.completed_laps = None
        self.actu_tyres = None
        self.ir_connected = False
        self.ir_label = 'iRacing Disconnected'
        self.in_box = 'Initialised'
        self.pit_count = 0

        self.lap_count = 0
        self.initial_tyres, self.current_tyres = {i: self.full for i in self.corners}, \
                                                 {i: self.full for i in self.corners}
        self.stop_lib = {'Initial': (self.initial_tyres, 0)}
        # initialise the SDK connection
        self.ir = irsdk.IRSDK()

    # function to reset all states - and shut the SDK
    def internal_shutdown(self):
        self.lap_dict = {}
        self.started_laps = None
        self.current_tyres = None
        self.completed_laps = None
        self.actu_tyres = None
        self.ir_connected = False
        self.ir_label = 'iRacing Disconnected'
        self.in_box = 'Initialised'
        self.pit_count = 0
        self.stop_lib = {}
        self.lap_count = 0
        self.initial_tyres, self.current_tyres = {i: self.full for i in self.corners}, \
                                                 {i: self.full for i in self.corners}
        self.ir.shutdown()

    # checks if IR connected - to be called every loop
    def check_iracing(self):
        if self.ir_connected and not (self.ir.is_initialized and self.ir.is_connected):
            self.internal_shutdown()
            return False
        elif not self.ir_connected and self.ir.startup() and self.ir.is_connected and self.ir.is_initialized:
            self.ir_connected = True
            self.ir_label = 'iRacing Connected'
            return True

    # checks if we're in the box - use this to decide whether to bother grabbing tyre info
    def check_in_box(self):
        if self.ir['PlayerCarInPitStall'] and self.ir['IsOnTrack']:
            self.in_box = True
            return self.in_box
        else:
            self.in_box = False
            return self.in_box

    # tyre state updater
    def tyre_state(self):
        # if we're not in the box, don't do anything
        if not self.check_in_box():
            pass

            # if we are - get the wear
        else:
            self.actu_tyres = {corner: [self.ir[self.tyre_variables[corner][ind]]
                                        for ind in range(0, 3)] for corner in self.corners}
            # if the wear hasn't changed, do nothing
            if self.actu_tyres == self.current_tyres:
                pass

            else:
                self.current_tyres = self.actu_tyres  # if they have changed, update the live tyre info
                self.pit_count += 1
                self.stop_lib['Stop' + str(self.pit_count)] = (self.current_tyres, self.completed_laps)
                # build our stop library



    def lap_number(self):
        if self.ir_connected and self.ir['IsOnTrack']:
            self.completed_laps = self.ir['LapCompleted']
            self.started_laps = self.ir['Lap']

    def lap_time(self):
        if self.completed_laps < 1:
            pass
        else:
            self.last_lap_time = self.ir['LapLastLapTime']
            self.lap_dict[self.completed_laps] = self.last_lap_time

    def main_loop(self):
        if self.check_iracing():
            self.lap_number()
            self.tyre_state()
