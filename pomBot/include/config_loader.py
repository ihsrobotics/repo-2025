import json

configs = {}

def load_configs():
    global configs
    with open('/home/kipr/Documents/IME_files/pomBot/include/config.json') as f:
        configs = json.load(f)

load_configs()


LEFT_WHEEL = configs["LEFT_WHEEL"]
RIGHT_WHEEL = configs["RIGHT_WHEEL"]
FRONT_TOPHAT = configs["FRONT_TOPHAT"]
BACK_TOPHAT = configs["BACK_TOPHAT"]
ET_SENSOR = configs["ET_SENSOR"]
FORWARD = configs["FORWARD"]
BACKWARD = configs["BACKWARD"]
BLACK = configs["BLACK"]
SWEEP_ARM = configs["SWEEP_ARM"]
CONVEYOR = configs["CONVEYOR"]
ARM_MAX = configs["ARM_MAX"]
ARM_MIN = configs["ARM_MIN"]
WHEEL = configs["WHEEL"]
