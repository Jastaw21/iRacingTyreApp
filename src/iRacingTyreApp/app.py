import time

import irsdk

import ir_vars


class StateVars:  # holds the data for
    def __init__(self):
        # general app data
        self.ir_connected = False
        self.ir_label = "iRacing Disconnected"

        # session info
        self.session_time = None
        self.track_tempVar = None
        self.track_number = None
        self.track_short = None

        # lap info
        self.last_lap_time = None
        self.completed_laps = 0
        self.started_laps = 0
        self.lap_dict = {}

        # tyre info
        self.corners = ["LF", "RF", "LR", "RR"]
        self.full = [100, 100, 100]
        self.initial_tyres = {corn: self.full for corn in self.corners}
        self.current_tyres = self.initial_tyres

        # pitstop info
        self.stop_lib = dict(Initial={"wear": self.initial_tyres, "length": 0})
        self.pit_count = 0
        self.last_stop_lap = 0

    def s_shutdown(self):
        self.ir_connected = False
        self.ir_label = "iRacing Disconnected"
        self.session_time = None
        self.track_tempVar = None
        self.last_lap_time = None
        self.completed_laps = 0
        self.lap_dict = {}
        self.corners = ["LF", "RF", "LR", "RR"]
        self.full = [100, 100, 100]
        self.initial_tyres = {corn: self.full for corn in self.corners}
        self.current_tyres = self.initial_tyres
        self.stop_lib = dict(Initial={"wear": self.initial_tyres, "length": 0})


class Driver(StateVars):  # main class to be called from UI
    def __init__(self):
        super().__init__()

        # populate a list of the tyre wear variables
        self.tyre_variables = ir_vars.tyre_wear()

        # initialise the SDK connection and the state variables
        self.ir = irsdk.IRSDK()

    def internal_shutdown(self):
        self.s_shutdown()
        self.ir.shutdown()

    # checks if IR connected - to be called every loop
    def check_iracing(self):
        if self.ir_connected and not (self.ir.is_initialized and self.ir.is_connected):
            self.internal_shutdown()
            self.ir_connected = False
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
        elif self.ir_connected and self.ir.is_initialized and self.ir.is_connected:
            return True
        else:
            return False

    # checks if we're in the box - use this to decide whether to bother grabbing tyre info
    def check_in_box(self):
        if self.ir["PlayerCarInPitStall"] and self.ir["IsOnTrack"]:
            return True
        else:
            return False

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
        if (
                self.check_in_box() or self.ir["OnPitRoad"]
        ):  # if we're not in the box, don't do anything

            # get the tyre info
            local_tyre_state = self.get_tyres_state()

            # if they've changed - set our local variable to the new ones and call stop dict builder
            if local_tyre_state != self.current_tyres:
                self.build_stop_library()
                self.current_tyres = local_tyre_state

            else:
                pass
        else:
            pass

    def build_stop_library(self):
        self.pit_count += 1
        self.stop_lib["Stop" + str(self.pit_count)] = {
            "wear": self.current_tyres,
            "length": (self.completed_laps - self.last_stop_lap),
        }
        self.last_stop_lap = self.completed_laps

    def lap_number(self):
        if self.ir_connected and self.ir["IsOnTrack"]:
            self.completed_laps = self.ir["LapCompleted"]
            self.started_laps = self.ir["Lap"]

    def set_session_time(self):
        time_in_secs = self.ir["SessionTimeOfDay"]
        self.session_time = time.strftime("%H:%M:%S", time.gmtime(time_in_secs))

    def lap_time(self): # in loop
        if self.completed_laps > 0:
            self.last_lap_time = self.ir["LapLastLapTime"]
            self.lap_dict[self.completed_laps] = {
                "lap_time": self.last_lap_time,
                "track_temp": self.track_temp,
            }

    def track_temp(self): # in lop
        track_temp_raw = self.ir["TrackTempCrew"]
        self.track_tempVar = round(track_temp_raw,2)

    def track_ID(self): # in loop
        self.track_number = self.ir["WeekendInfo"]["TrackID"]
        self.track_short = self.ir["WeekendInfo"]["TrackDisplayShortName"]

    # the main driver function - calls all the refreshing variables
    def main_loop(self):
        if self.check_iracing():
            self.set_session_time()
            self.update_tyre_state()
            self.track_temp()
            self.track_ID()
            self.lap_number()
            self.lap_time()


if __name__ == "__main__":
    d = Driver()
    while True:
        d.main_loop()
        time.sleep(1)
