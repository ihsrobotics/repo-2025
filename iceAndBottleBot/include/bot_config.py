# Import
import json

# Bot Config
configs = {}

def load_configs():
    global configs
    with open("/home/pi/Documents/IME_files/iceAndBottleBot/include/config.json") as f:
        configs = json.load(f)

load_configs()

LEFT_WHEEL = configs["LEFT_WHEEL"]
RIGHT_WHEEL = configs["RIGHT_WHEEL"]
ARM = configs["ARM"]
LEFT_T_SENSOR = configs["LEFT_T_SENSOR"]
RIGHT_T_SENSOR = configs["RIGHT_T_SENSOR"]
ET_SENSOR = configs["ET_SENSOR"]
FORWARD = configs["FORWARD"]
BACKWARD = configs["BACKWARD"]
BOOM_STICK = configs["BOOM_STICK"]
WRIST = configs["WRIST"]
CLAW = configs["CLAW"]
