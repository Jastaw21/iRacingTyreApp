import time
import irsdk


class StateVars:  # holds the data for
    def __init__(self):
        # general app data

        self.ir_connected = False
        self.ir_label = "iRacing Disconnected"
        self.stop_inhibit = False

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
        self.full = ["100%", "100%", "100%"]
        self.warmup = ["44C", "44C", "44C"]
        self.initial_tyres = {corn: self.full for corn in self.corners}
        self.current_tyres = self.initial_tyres
        self.initial_temps = {corn: self.warmup for corn in self.corners}
        self.current_temps = self.initial_temps

        # pitstop info
        self.stop_lib = dict(
            Initial={
                "wear": self.initial_tyres,
                "length": 0,
                "temps": self.initial_temps,
            }
        )
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
        self.stop_lib = dict(
            Initial={
                "wear": self.initial_tyres,
                "length": 0,
                "temps": self.initial_temps,
            }
        )


class Driver(StateVars):  # main class to be called from UI
    def __init__(self):
        super().__init__()

        # populate a list of the tyre wear variables

        self.stop_ready_flag = None
        self.tyre_wear_variables = {
            "LF": ["LFwearL", "LFwearM", "LFwearR"],
            "RF": ["RFwearL", "RFwearM", "RFwearR"],
            "LR": ["LRwearL", "LRwearM", "LRwearR"],
            "RR": ["RRwearL", "RRwearM", "RRwearR"],
        }

        self.tyre_temp_variables = {
            "LF": ["LFtempCL", "LFtempCM", "LFtempCR"],
            "RF": ["RFtempCL", "RFtempCM", "RFtempCR"],
            "LR": ["LRtempCL", "LRtempCM", "LRtempCR"],
            "RR": ["RRtempCL", "RRtempCM", "RRtempCR"],
        }

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
        if not self.ir["OnPitRoad"]:
            self.stop_inhibit = False
            return False
        elif self.ir["OnPitRoad"]:
            return True

    # this polls the SDK for the wear, and returns it in format of {LF:[100,95,84].... etc
    def get_tyres_state(self):
        tyre_wear = {}
        for corner in self.corners:
            working_list = []
            for ind in range(0, 3):
                raw_wear = self.ir[self.tyre_wear_variables[corner][ind]]
                wear = round(raw_wear * 100, 2)
                working_list.append(str(wear) + "%")
            tyre_wear[corner] = working_list
        return tyre_wear

    def get_tyre_temps(self):
        tyre_temp = {}
        for corner in self.corners:
            working_list = []
            for ind in range(0, 3):
                raw_temp = self.ir[self.tyre_temp_variables[corner][ind]]
                temp = round(raw_temp, 1)
                working_list.append(str(temp) + "C")
            tyre_temp[corner] = working_list
        return tyre_temp

    def update_tyre_state(self):
        if self.check_in_box() and not self.stop_inhibit:
            self.stop_ready_flag = True  # if we're in the pitlane - keep sampling the tyres until we see the change
            local_tyre_state = self.get_tyres_state()
            local_tyre_temp = self.get_tyre_temps()
            # if they've changed - set our local variable to the new ones and call stop dict builder
            if local_tyre_state != self.current_tyres:
                self.current_tyres = local_tyre_state
                self.current_temps = local_tyre_temp
                self.stop_inhibit = True
                self.build_stop_library()

    def build_stop_library(self):
        self.pit_count += 1
        self.stop_lib["Stop" + str(self.pit_count)] = {
            "wear": self.current_tyres,
            "temps": self.current_temps,
            "length": (self.completed_laps - self.last_stop_lap),
        }
        self.last_stop_lap = self.completed_laps

    def lap_number(self):
        if self.ir["IsOnTrack"]:
            self.completed_laps = self.ir["LapCompleted"]
            self.started_laps = self.ir["Lap"]

    def set_session_time(self):
        time_in_secs = self.ir["SessionTimeOfDay"]
        self.session_time = time.strftime("%H:%M:%S", time.gmtime(time_in_secs))

    def lap_time(self):  # in loop
        if self.completed_laps > 0:
            self.last_lap_time = self.ir["LapLastLapTime"]
            self.lap_dict[self.completed_laps] = dict(
                lap_time=self.last_lap_time, track_temp=self.track_temp
            )

    def track_temp(self):  # in loop
        track_temp_raw = self.ir["TrackTempCrew"]
        self.track_tempVar = round(track_temp_raw, 2)

    def track_ID(self):  # in loop
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
