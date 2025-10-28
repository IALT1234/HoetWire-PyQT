from functions.motor_control import MotorConfig
from functions.hot_wire_script2 import RunTest
from functions.database import Database
from functions.csvWriter import Writer
from functions.spectra import Spectra
from functions.daq import Daq
import numpy as np

# Instantiate core objects
daqHat = Daq()
motors = MotorConfig()
database = Database()
csvWriter = Writer("", database)

# Global dictionaries
selection_option= {
    "gas": daqHat.gas,
    "selected_probes": [],
    "probe1_enabled": False,
    "probe2_enabled": False,
    "probe1_selected": False,  # for velocity calc
    "probe2_selected": False   # for velocity calc
}

mainTest = RunTest(daqHat, csvWriter, motors, database,selection_option)
spectra = Spectra(daqHat, csvWriter, selection_option)


data_acquisition = {
    "hw1": None,
    "hw2": None,
    "temp": None,
    "abs_pressure": None,
    "v1": None,
    "v2": None
}

distance = 1

###nice graphing colors###
bright_colors = [
    '#E6194B',  # Red
    '#3CB44B',  # Green
    '#0082C8',  # Blue
    '#F58231',  # Orange
    '#911EB4',  # Purple
    '#46F0F0',  # Cyan
    '#FABE28',  # Yellow
    '#000000',  # Black
    '#A9A9A9',  # Dark Gray
    '#FFD700',  # Gold
    '#FF69B4',  # Hot Pink
    '#7CFC00',  # Lawn Green
    '#40E0D0',  # Turquoise
    '#DC143C',  # Crimson
    '#00CED1',  # Dark Turquoise
    '#B22222',  # Firebrick
    '#00FF7F',  # Spring Green
    '#DA70D6',  # Orchid
    '#1E90FF',  # Dodger Blue
    '#FF8C00',  # Dark Orange
]

def get_shuffled_colors(seed=0):
    np.random.seed(seed)
    colors = bright_colors.copy()
    np.random.shuffle(colors)
    return colors
