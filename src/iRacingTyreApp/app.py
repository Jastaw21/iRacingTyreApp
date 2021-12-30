import time

import irsdk
import ir_vars


# main class to be called from UI
class Driver:
    def __init__(self):
        # info to drive setup
        self.external_tyres = None
        self.track_temp = None
        self.last_lap_time = None
        self.full = [100, 100, 100]
        self.corners = ["LF", "RF", "LR", "RR"]
        self.tyre_variables = ir_vars.tyre_wear()
        # state variables - initialise as None. These get refreshed with every loop
        self.lap_dict = {}
        self.started_laps = 0
        self.completed_laps = 0
        self.actu_tyres = None
        self.ir_connected = False
        self.ir_label = "iRacing Disconnected"
        self.in_box = "Initialised"
        self.pit_count = 0
        self.lap_count = 0
        self.initial_tyres, self.current_tyres = {i: self.full for i in self.corners}
        self.stop_lib = {"Initial": {'wear': self.initial_tyres, 'length': 0}}
        # initialise the SDK connection
        self.ir = irsdk.IRSDK()

    '''These next three funtions are my utilities - reset states, check connection etc'''

    def internal_shutdown(self):
        self.lap_dict = {}
        self.started_laps = None
        self.current_tyres = None
        self.completed_laps = None
        self.actu_tyres = None
        self.ir_connected = False
        self.ir_label = "iRacing Disconnected"
        self.in_box = "Initialised"
        self.pit_count = 0
        self.stop_lib = {}
        self.lap_count = 0
        self.initial_tyres, self.current_tyres = {i: self.full for i in self.corners}, {
            i: self.full for i in self.corners
        }
        self.ir.shutdown()

    # checks if IR connected - to be called every loop
    def check_iracing(self):
        if self.ir_connected and not (self.ir.is_initialized and self.ir.is_connected):
            self.internal_shutdown()
            return False
        elif (
                not self.ir_connected
                and self.ir.startup()
                and self.ir.is_connected
                and self.ir.is_initialized
        ):
            self.ir_connected = True
            self.ir_label = "iRacing Connected"
            return True

    # checks if we're in the box - use this to decide whether to bother grabbing tyre info
    def check_in_box(self):
        if self.ir["PlayerCarInPitStall"] and self.ir["IsOnTrack"]:
            self.in_box = True
            return self.in_box
        else:
            self.in_box = False
            return self.in_box

    '''End Utilities. The below grab the info from the SDK and do stuff with it'''

    # this polls the SDK for the wear, and returns it in format of {LF:[100,95,84].... etc
    def get_tyres_state(self):
        tyre_wear = {}
        for corner in self.corners:
            working_list = []
            for ind in range(0, 3):
                raw_wear = self.ir[self.tyre_variables[corner][ind]]
                wear = round(raw_wear * 100, 2)
                working_list.append(wear)
            tyre_wear[corner] = working_list
        return tyre_wear

    # this updates our tyre wear variables, and if they've changed, i.e we've done a pitstop, add to stop dict
    def update_tyre_state(self):
        # if we're not in the box, don't do anything
        if self.check_in_box():

            # refresh the tyres
            local_tyre_state = self.get_tyres_state()

            # if they've changed - set our local variable to the new ones and call stop dict builder
            if local_tyre_state != self.current_tyres:
                self.current_tyres = local_tyre_state
                self.build_stop_library()

    def build_stop_library(self):
        self.pit_count += 1
        self.stop_lib["Stop" + str(self.pit_count)] = {
            "wear": self.current_tyres,
            "length": self.completed_laps,
        }

    def lap_number(self):
        if self.ir_connected and self.ir["IsOnTrack"]:
            self.completed_laps = self.ir["LapCompleted"]
            self.started_laps = self.ir["Lap"]

    def lap_time(self):
        if self.completed_laps > 0:
            self.last_lap_time = self.ir["LapLastLapTime"]
            self.track_temp = self.ir["TrackTempCrew"]
            self.lap_dict[self.completed_laps] = {
                "lap_time": self.last_lap_time,
                "track_temp": self.track_temp,
            }

    # the main driver function - calls all the refreshing variables
    def main_loop(self):
        if self.check_iracing():
            self.lap_number()
            self.update_tyre_state()
            self.lap_time()


if __name__ == '__main__':
    d = Driver()
    while True:
        d.main_loop()
        time.sleep(5)
