import os, sys, numpy, copy

from PyQt5.QtWidgets import QMessageBox, QScrollArea, QTableWidget, QHeaderView, QAbstractItemView, QTableWidgetItem, QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDoubleValidator

from silx.gui.plot.PlotWindow import PlotWindow

from Orange.widgets.settings import Setting
from Orange.widgets import gui as orangegui

from orangecontrib.wonder.util.widgets.ow_generic_widget import OWGenericWidget
from orangecontrib.wonder.util.gui.gui_utility import gui, ConfirmDialog
from orangecontrib.wonder.util import congruence
from orangecontrib.wonder.model.diffraction_pattern import DiffractionPattern, DiffractionPatternFactory, DiffractionPatternLimits
from orangecontrib.wonder.controller.fit.fit_global_parameters import FitGlobalParameters
from orangecontrib.wonder.controller.fit.init.fit_initialization import FitInitialization
from orangecontrib.wonder.controller.fit.fit_parameter import FitParameter

class Wavelenght:
    wavelength = 0.0
    weight = 0.0

    def __init__(self, wavelength, weight):
        self.wavelength = wavelength
        self.weight = weight
        self.is_principal = False

wavelengths_data = {}

def load_data_files():
    directory_files = os.path.join(os.path.dirname(__file__), "data")

    try:
        for path, dirs, files in os.walk(directory_files):

            for file_name in files:
                file = open(os.path.join(path, file_name), "r")

                rows = file.readlines()

                key = rows[0].strip()
                wavelengths = [None]*(len(rows)-1)
                highest_weight = 0.0
                for index in range(1, len(rows)):
                    data = rows[index].split()
                    wavelength = round(float(data[0].strip())/10, 8) # nm!
                    weight = round(float(data[1].strip()), 6)
                    highest_weight = highest_weight if weight <= highest_weight else weight

                    wavelengths[index-1] = Wavelenght(wavelength, weight)

                for wavelength in wavelengths:
                    if wavelength.weight == highest_weight:
                        wavelength.is_principal = True

                wavelengths_data[key] = wavelengths

    except Exception as err:
        raise Exception("Problems reading X-ray Tubes Wavelengths Configuration file: {0}".format(err))
    except:
        raise Exception("Unexpected error while reading X-ray Tubes Wavelengths Configuration file: ", sys.exc_info()[0])

load_data_files()

'''
for key in wavelengths_data.keys():
    print(key)
    wavelengths = wavelengths_data[key]
    for wavelength in wavelengths: print(wavelength.wavelength, wavelength.weight, wavelength.is_principal)
'''

class OWDiffractionPattern(OWGenericWidget):

    name = "Load Diffraction Pattern"
    description = "Loads diffraction pattern " \
                  "points from most common file formats"
    icon = "icons/diffraction_pattern.png"
    priority = 1

    want_main_area = True

    filename = Setting(["<input file>"])

    is_multiple_wavelength = Setting([0])
    
    wavelength = Setting([0.0826])
    wavelength_fixed = Setting([0])
    wavelength_has_min = Setting([0])
    wavelength_min = Setting([0.0])
    wavelength_has_max = Setting([0])
    wavelength_max = Setting([0.0])
    wavelength_function = Setting([0])
    wavelength_function_value = Setting([""])
    
    xray_tube_key = Setting(["CuKa2"])

    wavelength_2 = Setting([0])
    wavelength_2_fixed = Setting([1])
    wavelength_2_has_min = Setting([0])
    wavelength_2_min = Setting([0.0])
    wavelength_2_has_max = Setting([0])
    wavelength_2_max = Setting([0.0])
    wavelength_2_function = Setting([0])
    wavelength_2_function_value = Setting([""])

    wavelength_3 = Setting([0])
    wavelength_3_fixed = Setting([1])
    wavelength_3_has_min = Setting([0])
    wavelength_3_min = Setting([0.0])
    wavelength_3_has_max = Setting([0])
    wavelength_3_max = Setting([0.0])
    wavelength_3_function = Setting([0])
    wavelength_3_function_value = Setting([""])

    wavelength_4 = Setting([0])
    wavelength_4_fixed = Setting([1])
    wavelength_4_has_min = Setting([0])
    wavelength_4_min = Setting([0.0])
    wavelength_4_has_max = Setting([0])
    wavelength_4_max = Setting([0.0])
    wavelength_4_function = Setting([0])
    wavelength_4_function_value = Setting([""])

    wavelength_5 = Setting([0])
    wavelength_5_fixed = Setting([1])
    wavelength_5_has_min = Setting([0])
    wavelength_5_min = Setting([0.0])
    wavelength_5_has_max = Setting([0])
    wavelength_5_max = Setting([0.0])
    wavelength_5_function = Setting([0])
    wavelength_5_function_value = Setting([""])

    weight_2 = Setting([0])
    weight_2_fixed = Setting([1])
    weight_2_has_min = Setting([0])
    weight_2_min = Setting([0.0])
    weight_2_has_max = Setting([0])
    weight_2_max = Setting([0.0])
    weight_2_function = Setting([0])
    weight_2_function_value = Setting([""])

    weight_3 = Setting([0])
    weight_3_fixed = Setting([1])
    weight_3_has_min = Setting([0])
    weight_3_min = Setting([0.0])
    weight_3_has_max = Setting([0])
    weight_3_max = Setting([0.0])
    weight_3_function = Setting([0])
    weight_3_function_value = Setting([""])

    weight_4 = Setting([0])
    weight_4_fixed = Setting([1])
    weight_4_has_min = Setting([0])
    weight_4_min = Setting([0.0])
    weight_4_has_max = Setting([0])
    weight_4_max = Setting([0.0])
    weight_4_function = Setting([0])
    weight_4_function_value = Setting([""])

    weight_5 = Setting([0])
    weight_5_fixed = Setting([1])
    weight_5_has_min = Setting([0])
    weight_5_min = Setting([0.0])
    weight_5_has_max = Setting([0])
    weight_5_max = Setting([0.0])
    weight_5_function = Setting([0])
    weight_5_function_value = Setting([""])

    twotheta_min = Setting([0.0])
    twotheta_has_min = Setting([0])
    twotheta_max = Setting([0.0])
    twotheta_has_max = Setting([0])

    horizontal_headers = ["2Theta [deg]", "s [nm^-1]", "Intensity", "Error"]

    outputs = [("Fit Global Parameters", FitGlobalParameters)]

    diffraction_patterns = None

    # TO PRESERVE RETRO-COMPATIBILITY
    def fix_input(self, emergency=False):
        if not isinstance(self.filename                   , list): self.filename                    = [self.filename                   ]
        if not isinstance(self.is_multiple_wavelength     , list): self.is_multiple_wavelength      = [self.is_multiple_wavelength     ]
        if not isinstance(self.wavelength                 , list): self.wavelength                  = [self.wavelength                 ]
        if not isinstance(self.wavelength_fixed           , list): self.wavelength_fixed            = [self.wavelength_fixed           ]
        if not isinstance(self.wavelength_has_min         , list): self.wavelength_has_min          = [self.wavelength_has_min         ]
        if not isinstance(self.wavelength_min             , list): self.wavelength_min              = [self.wavelength_min             ]
        if not isinstance(self.wavelength_has_max         , list): self.wavelength_has_max          = [self.wavelength_has_max         ]
        if not isinstance(self.wavelength_max             , list): self.wavelength_max              = [self.wavelength_max             ]
        if not isinstance(self.wavelength_function        , list): self.wavelength_function         = [self.wavelength_function        ]
        if not isinstance(self.wavelength_function_value  , list): self.wavelength_function_value   = [self.wavelength_function_value  ]
        if not isinstance(self.xray_tube_key              , list): self.xray_tube_key               = [self.xray_tube_key              ]
        if not isinstance(self.wavelength_2               , list): self.wavelength_2                = [self.wavelength_2               ]
        if not isinstance(self.wavelength_2_fixed         , list): self.wavelength_2_fixed          = [self.wavelength_2_fixed         ]
        if not isinstance(self.wavelength_2_has_min       , list): self.wavelength_2_has_min        = [self.wavelength_2_has_min       ]
        if not isinstance(self.wavelength_2_min           , list): self.wavelength_2_min            = [self.wavelength_2_min           ]
        if not isinstance(self.wavelength_2_has_max       , list): self.wavelength_2_has_max        = [self.wavelength_2_has_max       ]
        if not isinstance(self.wavelength_2_max           , list): self.wavelength_2_max            = [self.wavelength_2_max           ]
        if not isinstance(self.wavelength_2_function      , list): self.wavelength_2_function       = [self.wavelength_2_function      ]
        if not isinstance(self.wavelength_2_function_value, list): self.wavelength_2_function_value = [self.wavelength_2_function_value]
        if not isinstance(self.wavelength_3               , list): self.wavelength_3                = [self.wavelength_3               ]
        if not isinstance(self.wavelength_3_fixed         , list): self.wavelength_3_fixed          = [self.wavelength_3_fixed         ]
        if not isinstance(self.wavelength_3_has_min       , list): self.wavelength_3_has_min        = [self.wavelength_3_has_min       ]
        if not isinstance(self.wavelength_3_min           , list): self.wavelength_3_min            = [self.wavelength_3_min           ]
        if not isinstance(self.wavelength_3_has_max       , list): self.wavelength_3_has_max        = [self.wavelength_3_has_max       ]
        if not isinstance(self.wavelength_3_max           , list): self.wavelength_3_max            = [self.wavelength_3_max           ]
        if not isinstance(self.wavelength_3_function      , list): self.wavelength_3_function       = [self.wavelength_3_function      ]
        if not isinstance(self.wavelength_3_function_value, list): self.wavelength_3_function_value = [self.wavelength_3_function_value]
        if not isinstance(self.wavelength_4               , list): self.wavelength_4                = [self.wavelength_4               ]
        if not isinstance(self.wavelength_4_fixed         , list): self.wavelength_4_fixed          = [self.wavelength_4_fixed         ]
        if not isinstance(self.wavelength_4_has_min       , list): self.wavelength_4_has_min        = [self.wavelength_4_has_min       ]
        if not isinstance(self.wavelength_4_min           , list): self.wavelength_4_min            = [self.wavelength_4_min           ]
        if not isinstance(self.wavelength_4_has_max       , list): self.wavelength_4_has_max        = [self.wavelength_4_has_max       ]
        if not isinstance(self.wavelength_4_max           , list): self.wavelength_4_max            = [self.wavelength_4_max           ]
        if not isinstance(self.wavelength_4_function      , list): self.wavelength_4_function       = [self.wavelength_4_function      ]
        if not isinstance(self.wavelength_4_function_value, list): self.wavelength_4_function_value = [self.wavelength_4_function_value]
        if not isinstance(self.wavelength_5               , list): self.wavelength_5                = [self.wavelength_5               ]
        if not isinstance(self.wavelength_5_fixed         , list): self.wavelength_5_fixed          = [self.wavelength_5_fixed         ]
        if not isinstance(self.wavelength_5_has_min       , list): self.wavelength_5_has_min        = [self.wavelength_5_has_min       ]
        if not isinstance(self.wavelength_5_min           , list): self.wavelength_5_min            = [self.wavelength_5_min           ]
        if not isinstance(self.wavelength_5_has_max       , list): self.wavelength_5_has_max        = [self.wavelength_5_has_max       ]
        if not isinstance(self.wavelength_5_max           , list): self.wavelength_5_max            = [self.wavelength_5_max           ]
        if not isinstance(self.wavelength_5_function      , list): self.wavelength_5_function       = [self.wavelength_5_function      ]
        if not isinstance(self.wavelength_5_function_value, list): self.wavelength_5_function_value = [self.wavelength_5_function_value]
        if not isinstance(self.weight_2                   , list): self.weight_2                    = [self.weight_2                   ]
        if not isinstance(self.weight_2_fixed             , list): self.weight_2_fixed              = [self.weight_2_fixed             ]
        if not isinstance(self.weight_2_has_min           , list): self.weight_2_has_min            = [self.weight_2_has_min           ]
        if not isinstance(self.weight_2_min               , list): self.weight_2_min                = [self.weight_2_min               ]
        if not isinstance(self.weight_2_has_max           , list): self.weight_2_has_max            = [self.weight_2_has_max           ]
        if not isinstance(self.weight_2_max               , list): self.weight_2_max                = [self.weight_2_max               ]
        if not isinstance(self.weight_2_function          , list): self.weight_2_function           = [self.weight_2_function          ]
        if not isinstance(self.weight_2_function_value    , list): self.weight_2_function_value     = [self.weight_2_function_value    ]
        if not isinstance(self.weight_3                   , list): self.weight_3                    = [self.weight_3                   ]
        if not isinstance(self.weight_3_fixed             , list): self.weight_3_fixed              = [self.weight_3_fixed             ]
        if not isinstance(self.weight_3_has_min           , list): self.weight_3_has_min            = [self.weight_3_has_min           ]
        if not isinstance(self.weight_3_min               , list): self.weight_3_min                = [self.weight_3_min               ]
        if not isinstance(self.weight_3_has_max           , list): self.weight_3_has_max            = [self.weight_3_has_max           ]
        if not isinstance(self.weight_3_max               , list): self.weight_3_max                = [self.weight_3_max               ]
        if not isinstance(self.weight_3_function          , list): self.weight_3_function           = [self.weight_3_function          ]
        if not isinstance(self.weight_3_function_value    , list): self.weight_3_function_value     = [self.weight_3_function_value    ]
        if not isinstance(self.weight_4                   , list): self.weight_4                    = [self.weight_4                   ]
        if not isinstance(self.weight_4_fixed             , list): self.weight_4_fixed              = [self.weight_4_fixed             ]
        if not isinstance(self.weight_4_has_min           , list): self.weight_4_has_min            = [self.weight_4_has_min           ]
        if not isinstance(self.weight_4_min               , list): self.weight_4_min                = [self.weight_4_min               ]
        if not isinstance(self.weight_4_has_max           , list): self.weight_4_has_max            = [self.weight_4_has_max           ]
        if not isinstance(self.weight_4_max               , list): self.weight_4_max                = [self.weight_4_max               ]
        if not isinstance(self.weight_4_function          , list): self.weight_4_function           = [self.weight_4_function          ]
        if not isinstance(self.weight_4_function_value    , list): self.weight_4_function_value     = [self.weight_4_function_value    ]
        if not isinstance(self.weight_5                   , list): self.weight_5                    = [self.weight_5                   ]
        if not isinstance(self.weight_5_fixed             , list): self.weight_5_fixed              = [self.weight_5_fixed             ]
        if not isinstance(self.weight_5_has_min           , list): self.weight_5_has_min            = [self.weight_5_has_min           ]
        if not isinstance(self.weight_5_min               , list): self.weight_5_min                = [self.weight_5_min               ]
        if not isinstance(self.weight_5_has_max           , list): self.weight_5_has_max            = [self.weight_5_has_max           ]
        if not isinstance(self.weight_5_max               , list): self.weight_5_max                = [self.weight_5_max               ]
        if not isinstance(self.weight_5_function          , list): self.weight_5_function           = [self.weight_5_function          ]
        if not isinstance(self.weight_5_function_value    , list): self.weight_5_function_value     = [self.weight_5_function_value    ]
        if not isinstance(self.twotheta_min               , list): self.twotheta_min                = [self.twotheta_min               ]
        if not isinstance(self.twotheta_has_min           , list): self.twotheta_has_min            = [self.twotheta_has_min           ]
        if not isinstance(self.twotheta_max               , list): self.twotheta_max                = [self.twotheta_max               ]
        if not isinstance(self.twotheta_has_max           , list): self.twotheta_has_max            = [self.twotheta_has_max           ]

        if emergency:
            self.filename                    = ["<input file>"]
            self.is_multiple_wavelength      = [0]
            self.wavelength                  = [0.0826]
            self.wavelength_fixed            = [0]
            self.wavelength_has_min          = [0]
            self.wavelength_min              = [0.0]
            self.wavelength_has_max          = [0]
            self.wavelength_max              = [0.0]
            self.wavelength_function         = [0]
            self.wavelength_function_value   = [""]
            self.xray_tube_key               = ["CuKa2"]
            self.wavelength_2                = [0]
            self.wavelength_2_fixed          = [1]
            self.wavelength_2_has_min        = [0]
            self.wavelength_2_min            = [0.0]
            self.wavelength_2_has_max        = [0]
            self.wavelength_2_max            = [0.0]
            self.wavelength_2_function       = [0]
            self.wavelength_2_function_value = [""]
            self.wavelength_3                = [0]
            self.wavelength_3_fixed          = [1]
            self.wavelength_3_has_min        = [0]
            self.wavelength_3_min            = [0.0]
            self.wavelength_3_has_max        = [0]
            self.wavelength_3_max            = [0.0]
            self.wavelength_3_function       = [0]
            self.wavelength_3_function_value = [""]
            self.wavelength_4                = [0]
            self.wavelength_4_fixed          = [1]
            self.wavelength_4_has_min        = [0]
            self.wavelength_4_min            = [0.0]
            self.wavelength_4_has_max        = [0]
            self.wavelength_4_max            = [0.0]
            self.wavelength_4_function       = [0]
            self.wavelength_4_function_value = [""]
            self.wavelength_5                = [0]
            self.wavelength_5_fixed          = [1]
            self.wavelength_5_has_min        = [0]
            self.wavelength_5_min            = [0.0]
            self.wavelength_5_has_max        = [0]
            self.wavelength_5_max            = [0.0]
            self.wavelength_5_function       = [0]
            self.wavelength_5_function_value = [""]
            self.weight_2                    = [0]
            self.weight_2_fixed              = [1]
            self.weight_2_has_min            = [0]
            self.weight_2_min                = [0.0]
            self.weight_2_has_max            = [0]
            self.weight_2_max                = [0.0]
            self.weight_2_function           = [0]
            self.weight_2_function_value     = [""]
            self.weight_3                    = [0]
            self.weight_3_fixed              = [1]
            self.weight_3_has_min            = [0]
            self.weight_3_min                = [0.0]
            self.weight_3_has_max            = [0]
            self.weight_3_max                = [0.0]
            self.weight_3_function           = [0]
            self.weight_3_function_value     = [""]
            self.weight_4                    = [0]
            self.weight_4_fixed              = [1]
            self.weight_4_has_min            = [0]
            self.weight_4_min                = [0.0]
            self.weight_4_has_max            = [0]
            self.weight_4_max                = [0.0]
            self.weight_4_function           = [0]
            self.weight_4_function_value     = [""]
            self.weight_5                    = [0]
            self.weight_5_fixed              = [1]
            self.weight_5_has_min            = [0]
            self.weight_5_min                = [0.0]
            self.weight_5_has_max            = [0]
            self.weight_5_max                = [0.0]
            self.weight_5_function           = [0]
            self.weight_5_function_value     = [""]
            self.twotheta_min                = [0.0]
            self.twotheta_has_min            = [0]
            self.twotheta_max                = [0.0]
            self.twotheta_has_max            = [0]
        else:
            if len(self.filename                   ) == 0: self.filename                    = ["<input file>"]
            if len(self.is_multiple_wavelength     ) == 0: self.is_multiple_wavelength      = [0]
            if len(self.wavelength                 ) == 0: self.wavelength                  = [0.0826]
            if len(self.wavelength_fixed           ) == 0: self.wavelength_fixed            = [0]
            if len(self.wavelength_has_min         ) == 0: self.wavelength_has_min          = [0]
            if len(self.wavelength_min             ) == 0: self.wavelength_min              = [0.0]
            if len(self.wavelength_has_max         ) == 0: self.wavelength_has_max          = [0]
            if len(self.wavelength_max             ) == 0: self.wavelength_max              = [0.0]
            if len(self.wavelength_function        ) == 0: self.wavelength_function         = [0]
            if len(self.wavelength_function_value  ) == 0: self.wavelength_function_value   = [""]
            if len(self.xray_tube_key              ) == 0: self.xray_tube_key               = ["CuKa2"]
            if len(self.wavelength_2               ) == 0: self.wavelength_2                = [0]
            if len(self.wavelength_2_fixed         ) == 0: self.wavelength_2_fixed          = [1]
            if len(self.wavelength_2_has_min       ) == 0: self.wavelength_2_has_min        = [0]
            if len(self.wavelength_2_min           ) == 0: self.wavelength_2_min            = [0.0]
            if len(self.wavelength_2_has_max       ) == 0: self.wavelength_2_has_max        = [0]
            if len(self.wavelength_2_max           ) == 0: self.wavelength_2_max            = [0.0]
            if len(self.wavelength_2_function      ) == 0: self.wavelength_2_function       = [0]
            if len(self.wavelength_2_function_value) == 0: self.wavelength_2_function_value = [""]
            if len(self.wavelength_3               ) == 0: self.wavelength_3                = [0]
            if len(self.wavelength_3_fixed         ) == 0: self.wavelength_3_fixed          = [1]
            if len(self.wavelength_3_has_min       ) == 0: self.wavelength_3_has_min        = [0]
            if len(self.wavelength_3_min           ) == 0: self.wavelength_3_min            = [0.0]
            if len(self.wavelength_3_has_max       ) == 0: self.wavelength_3_has_max        = [0]
            if len(self.wavelength_3_max           ) == 0: self.wavelength_3_max            = [0.0]
            if len(self.wavelength_3_function      ) == 0: self.wavelength_3_function       = [0]
            if len(self.wavelength_3_function_value) == 0: self.wavelength_3_function_value = [""]
            if len(self.wavelength_4               ) == 0: self.wavelength_4                = [0]
            if len(self.wavelength_4_fixed         ) == 0: self.wavelength_4_fixed          = [1]
            if len(self.wavelength_4_has_min       ) == 0: self.wavelength_4_has_min        = [0]
            if len(self.wavelength_4_min           ) == 0: self.wavelength_4_min            = [0.0]
            if len(self.wavelength_4_has_max       ) == 0: self.wavelength_4_has_max        = [0]
            if len(self.wavelength_4_max           ) == 0: self.wavelength_4_max            = [0.0]
            if len(self.wavelength_4_function      ) == 0: self.wavelength_4_function       = [0]
            if len(self.wavelength_4_function_value) == 0: self.wavelength_4_function_value = [""]
            if len(self.wavelength_5               ) == 0: self.wavelength_5                = [0]
            if len(self.wavelength_5_fixed         ) == 0: self.wavelength_5_fixed          = [1]
            if len(self.wavelength_5_has_min       ) == 0: self.wavelength_5_has_min        = [0]
            if len(self.wavelength_5_min           ) == 0: self.wavelength_5_min            = [0.0]
            if len(self.wavelength_5_has_max       ) == 0: self.wavelength_5_has_max        = [0]
            if len(self.wavelength_5_max           ) == 0: self.wavelength_5_max            = [0.0]
            if len(self.wavelength_5_function      ) == 0: self.wavelength_5_function       = [0]
            if len(self.wavelength_5_function_value) == 0: self.wavelength_5_function_value = [""]
            if len(self.weight_2                   ) == 0: self.weight_2                    = [0]
            if len(self.weight_2_fixed             ) == 0: self.weight_2_fixed              = [1]
            if len(self.weight_2_has_min           ) == 0: self.weight_2_has_min            = [0]
            if len(self.weight_2_min               ) == 0: self.weight_2_min                = [0.0]
            if len(self.weight_2_has_max           ) == 0: self.weight_2_has_max            = [0]
            if len(self.weight_2_max               ) == 0: self.weight_2_max                = [0.0]
            if len(self.weight_2_function          ) == 0: self.weight_2_function           = [0]
            if len(self.weight_2_function_value    ) == 0: self.weight_2_function_value     = [""]
            if len(self.weight_3                   ) == 0: self.weight_3                    = [0]
            if len(self.weight_3_fixed             ) == 0: self.weight_3_fixed              = [1]
            if len(self.weight_3_has_min           ) == 0: self.weight_3_has_min            = [0]
            if len(self.weight_3_min               ) == 0: self.weight_3_min                = [0.0]
            if len(self.weight_3_has_max           ) == 0: self.weight_3_has_max            = [0]
            if len(self.weight_3_max               ) == 0: self.weight_3_max                = [0.0]
            if len(self.weight_3_function          ) == 0: self.weight_3_function           = [0]
            if len(self.weight_3_function_value    ) == 0: self.weight_3_function_value     = [""]
            if len(self.weight_4                   ) == 0: self.weight_4                    = [0]
            if len(self.weight_4_fixed             ) == 0: self.weight_4_fixed              = [1]
            if len(self.weight_4_has_min           ) == 0: self.weight_4_has_min            = [0]
            if len(self.weight_4_min               ) == 0: self.weight_4_min                = [0.0]
            if len(self.weight_4_has_max           ) == 0: self.weight_4_has_max            = [0]
            if len(self.weight_4_max               ) == 0: self.weight_4_max                = [0.0]
            if len(self.weight_4_function          ) == 0: self.weight_4_function           = [0]
            if len(self.weight_4_function_value    ) == 0: self.weight_4_function_value     = [""]
            if len(self.weight_5                   ) == 0: self.weight_5                    = [0]
            if len(self.weight_5_fixed             ) == 0: self.weight_5_fixed              = [1]
            if len(self.weight_5_has_min           ) == 0: self.weight_5_has_min            = [0]
            if len(self.weight_5_min               ) == 0: self.weight_5_min                = [0.0]
            if len(self.weight_5_has_max           ) == 0: self.weight_5_has_max            = [0]
            if len(self.weight_5_max               ) == 0: self.weight_5_max                = [0.0]
            if len(self.weight_5_function          ) == 0: self.weight_5_function           = [0]
            if len(self.weight_5_function_value    ) == 0: self.weight_5_function_value     = [""]
            if len(self.twotheta_min               ) == 0: self.twotheta_min                = [0.0]
            if len(self.twotheta_has_min           ) == 0: self.twotheta_has_min            = [0]
            if len(self.twotheta_max               ) == 0: self.twotheta_max                = [0.0]
            if len(self.twotheta_has_max           ) == 0: self.twotheta_has_max            = [0]

    def __init__(self):
        super().__init__(show_automatic_box=False)

        if self.IS_FIX: self.fix_input(False)

        main_box = gui.widgetBox(self.controlArea,
                                 "Load Diffraction Pattern", orientation="vertical",
                                 width=self.CONTROL_AREA_WIDTH - 5, height=600)


        button_box = gui.widgetBox(main_box,
                                   "", orientation="horizontal",
                                   width=self.CONTROL_AREA_WIDTH-25)

        gui.button(button_box, self, "Load Data", height=50, callback=self.load_diffraction_patterns)

        tabs_button_box = gui.widgetBox(main_box, "", addSpace=False, orientation="horizontal")

        btns = [gui.button(tabs_button_box, self, "Insert Pattern Before", callback=self.insert_before),
                gui.button(tabs_button_box, self, "Insert Pattern After", callback=self.insert_after),
                gui.button(tabs_button_box, self, "Remove Pattern", callback=self.remove)]

        for btn in btns:
            btn.setFixedHeight(40)

        self.diffraction_pattern_tabs = gui.tabWidget(main_box)
        self.diffraction_pattern_box_array = []

        for index in range(len(self.filename)):
            diffraction_pattern_tab = gui.createTabPage(self.diffraction_pattern_tabs, "Diff. Patt. " + str(index + 1))

            diffraction_pattern_box = DiffractionPatternBox(widget=self,
                                                            parent=diffraction_pattern_tab,
                                                            index = index,
                                                            filename                    = self.filename[index],
                                                            is_multiple_wavelength        = self.is_multiple_wavelength[index],
                                                            wavelength                  = self.wavelength[index],
                                                            wavelength_fixed            = self.wavelength_fixed[index],
                                                            wavelength_has_min          = self.wavelength_has_min[index],
                                                            wavelength_min              = self.wavelength_min[index],
                                                            wavelength_has_max          = self.wavelength_has_max[index],
                                                            wavelength_max              = self.wavelength_max[index],
                                                            wavelength_function         = self.wavelength_function[index],
                                                            wavelength_function_value   = self.wavelength_function_value[index],
                                                            xray_tube_key               = self.xray_tube_key[index],
                                                            wavelength_2                = self.wavelength_2[index],
                                                            wavelength_2_fixed          = self.wavelength_2_fixed[index],
                                                            wavelength_2_has_min        = self.wavelength_2_has_min[index],
                                                            wavelength_2_min            = self.wavelength_2_min[index],
                                                            wavelength_2_has_max        = self.wavelength_2_has_max[index],
                                                            wavelength_2_max            = self.wavelength_2_max[index],
                                                            wavelength_2_function       = self.wavelength_2_function[index],
                                                            wavelength_2_function_value = self.wavelength_2_function_value[index],
                                                            wavelength_3                = self.wavelength_3[index],
                                                            wavelength_3_fixed          = self.wavelength_3_fixed[index],
                                                            wavelength_3_has_min        = self.wavelength_3_has_min[index],
                                                            wavelength_3_min            = self.wavelength_3_min[index],
                                                            wavelength_3_has_max        = self.wavelength_3_has_max[index],
                                                            wavelength_3_max            = self.wavelength_3_max[index],
                                                            wavelength_3_function       = self.wavelength_3_function[index],
                                                            wavelength_3_function_value = self.wavelength_3_function_value[index],
                                                            wavelength_4                = self.wavelength_4[index],
                                                            wavelength_4_fixed          = self.wavelength_4_fixed[index],
                                                            wavelength_4_has_min        = self.wavelength_4_has_min[index],
                                                            wavelength_4_min            = self.wavelength_4_min[index],
                                                            wavelength_4_has_max        = self.wavelength_4_has_max[index],
                                                            wavelength_4_max            = self.wavelength_4_max[index],
                                                            wavelength_4_function       = self.wavelength_4_function[index],
                                                            wavelength_4_function_value = self.wavelength_4_function_value[index],
                                                            wavelength_5                = self.wavelength_5[index],
                                                            wavelength_5_fixed          = self.wavelength_5_fixed[index],
                                                            wavelength_5_has_min        = self.wavelength_5_has_min[index],
                                                            wavelength_5_min            = self.wavelength_5_min[index],
                                                            wavelength_5_has_max        = self.wavelength_5_has_max[index],
                                                            wavelength_5_max            = self.wavelength_5_max[index],
                                                            wavelength_5_function       = self.wavelength_5_function[index],
                                                            wavelength_5_function_value = self.wavelength_5_function_value[index],
                                                            weight_2                    = self.weight_2[index],
                                                            weight_2_fixed              = self.weight_2_fixed[index],
                                                            weight_2_has_min            = self.weight_2_has_min[index],
                                                            weight_2_min                = self.weight_2_min[index],
                                                            weight_2_has_max            = self.weight_2_has_max[index],
                                                            weight_2_max                = self.weight_2_max[index],
                                                            weight_2_function           = self.weight_2_function[index],
                                                            weight_2_function_value     = self.weight_2_function_value[index],
                                                            weight_3                    = self.weight_3[index],
                                                            weight_3_fixed              = self.weight_3_fixed[index],
                                                            weight_3_has_min            = self.weight_3_has_min[index],
                                                            weight_3_min                = self.weight_3_min[index],
                                                            weight_3_has_max            = self.weight_3_has_max[index],
                                                            weight_3_max                = self.weight_3_max[index],
                                                            weight_3_function           = self.weight_3_function[index],
                                                            weight_3_function_value     = self.weight_3_function_value[index],
                                                            weight_4                    = self.weight_4[index],
                                                            weight_4_fixed              = self.weight_4_fixed[index],
                                                            weight_4_has_min            = self.weight_4_has_min[index],
                                                            weight_4_min                = self.weight_4_min[index],
                                                            weight_4_has_max            = self.weight_4_has_max[index],
                                                            weight_4_max                = self.weight_4_max[index],
                                                            weight_4_function           = self.weight_4_function[index],
                                                            weight_4_function_value     = self.weight_4_function_value[index],
                                                            weight_5                    = self.weight_5[index],
                                                            weight_5_fixed              = self.weight_5_fixed[index],
                                                            weight_5_has_min            = self.weight_5_has_min[index],
                                                            weight_5_min                = self.weight_5_min[index],
                                                            weight_5_has_max            = self.weight_5_has_max[index],
                                                            weight_5_max                = self.weight_5_max[index],
                                                            weight_5_function           = self.weight_5_function[index],
                                                            weight_5_function_value     = self.weight_5_function_value[index],
                                                            twotheta_min                = self.twotheta_min[index],
                                                            twotheta_has_min            = self.twotheta_has_min[index],
                                                            twotheta_max                = self.twotheta_max[index],
                                                            twotheta_has_max            = self.twotheta_has_max[index]
                                                            )

            self.diffraction_pattern_box_array.append(diffraction_pattern_box)

        self.tabs = gui.tabWidget(self.mainArea)
        self.tab_diff = []
        self.tabs_data_plot = []
        self.tab_data = []
        self.tab_plot = []
        self.plot = []
        self.table_data = []

        for index in range(len(self.filename)):
            self.tab_diff.append(gui.createTabPage(self.tabs, "Diff. Patt. " + str(index+1)))
            self.tabs_data_plot.append(gui.tabWidget(self.tab_diff[index]))
            self.tab_data.append(gui.createTabPage(self.tabs_data_plot[index], "Data"))
            self.tab_plot.append(gui.createTabPage(self.tabs_data_plot[index], "Plot"))

            self.plot.append(PlotWindow())
            self.plot[index].setDefaultPlotLines(True)
            self.plot[index].setActiveCurveColor(color="#00008B")
            self.plot[index].setGraphXLabel(r"2$\theta$")
            self.plot[index].setGraphYLabel("Intensity")

            self.tab_plot[index].layout().addWidget(self.plot[index])

            table_widget = self.create_table_widget()

            self.table_data.append(table_widget)

            self.tab_data[index].layout().addWidget(table_widget, alignment=Qt.AlignHCenter)


    def insert_before(self):
        current_index = self.diffraction_pattern_tabs.currentIndex()

        if ConfirmDialog.confirmed(parent=self, message="Confirm Insertion of a new element before " + self.diffraction_pattern_tabs.tabText(current_index) + "?"):
            diffraction_pattern_tab = gui.widgetBox(self.diffraction_pattern_tabs, addToLayout=0, margin=4)
            diffraction_pattern_box = DiffractionPatternBox(widget=self, parent=diffraction_pattern_tab, index=current_index)
            diffraction_pattern_box.after_change_workspace_units()

            self.diffraction_pattern_tabs.insertTab(current_index, diffraction_pattern_tab, "TEMP")
            self.diffraction_pattern_box_array.insert(current_index, diffraction_pattern_box)

            diffraction_pattern_pd_tab = gui.widgetBox(self.tabs, addToLayout=0, margin=4)
            self.tabs.insertTab(current_index, diffraction_pattern_pd_tab, "TEMP")
            self.tab_diff.insert(current_index, diffraction_pattern_pd_tab)

            self.tabs_data_plot.insert(current_index, gui.tabWidget(self.tab_diff[current_index]))
            self.tab_data.insert(current_index, gui.createTabPage(self.tabs_data_plot[current_index], "Data"))
            self.tab_plot.insert(current_index, gui.createTabPage(self.tabs_data_plot[current_index], "Plot"))

            self.plot.insert(current_index, PlotWindow())
            self.plot[current_index].setDefaultPlotLines(True)
            self.plot[current_index].setActiveCurveColor(color="#00008B")
            self.plot[current_index].setGraphXLabel(r"2$\theta$")
            self.plot[current_index].setGraphYLabel("Intensity")

            self.tab_plot[current_index].layout().addWidget(self.plot[current_index])

            scrollarea = QScrollArea(self.tab_data[current_index])
            scrollarea.setMinimumWidth(805)
            scrollarea.setMinimumHeight(605)

            self.table_data.insert(current_index, self.create_table_widget())

            scrollarea.setWidget(self.table_data[current_index])
            scrollarea.setWidgetResizable(1)

            self.tab_data[current_index].layout().addWidget(scrollarea, alignment=Qt.AlignHCenter)

            for index in range(current_index, self.diffraction_pattern_tabs.count()):
                self.diffraction_pattern_tabs.setTabText(index, "Diff. Patt." + str(index + 1))
                self.diffraction_pattern_box_array[index].index = index
                self.tabs.setTabText(index, "Diff. Patt." + str(index + 1))

            self.dumpSettings()
            self.diffraction_pattern_tabs.setCurrentIndex(current_index)
            self.tabs.setCurrentIndex(current_index)

    def insert_after(self):
        current_index = self.diffraction_pattern_tabs.currentIndex()

        if ConfirmDialog.confirmed(parent=self, message="Confirm Insertion of a new element after " + self.diffraction_pattern_tabs.tabText(current_index) + "?"):
            diffraction_pattern_tab = gui.widgetBox(self.diffraction_pattern_tabs, addToLayout=0, margin=4)
            diffraction_pattern_box = DiffractionPatternBox(widget=self, parent=diffraction_pattern_tab, index=current_index+1)
            diffraction_pattern_box.after_change_workspace_units()

            diffraction_pattern_pd_tab = gui.widgetBox(self.tabs, addToLayout=0, margin=4)

            if current_index == self.diffraction_pattern_tabs.count() - 1:  # LAST
                self.diffraction_pattern_tabs.addTab(diffraction_pattern_tab, "TEMP")
                self.diffraction_pattern_box_array.append(diffraction_pattern_box)
                
                self.tabs.addTab(diffraction_pattern_pd_tab, "TEMP")
                self.tab_diff.append(diffraction_pattern_pd_tab)
    
                self.tabs_data_plot.append(gui.tabWidget(self.tab_diff[current_index + 1]))
                self.tab_data.append(gui.createTabPage(self.tabs_data_plot[current_index + 1], "Data"))
                self.tab_plot.append(gui.createTabPage(self.tabs_data_plot[current_index + 1], "Plot"))
    
                self.plot.append(PlotWindow())
                self.plot[current_index + 1].setDefaultPlotLines(True)
                self.plot[current_index + 1].setActiveCurveColor(color="#00008B")
                self.plot[current_index + 1].setGraphXLabel(r"2$\theta$")
                self.plot[current_index + 1].setGraphYLabel("Intensity")
    
                self.tab_plot[current_index + 1].layout().addWidget(self.plot[current_index + 1])
    
                scrollarea = QScrollArea(self.tab_data[current_index])
                scrollarea.setMinimumWidth(805)
                scrollarea.setMinimumHeight(605)
    
                self.table_data.append(self.create_table_widget())
    
                scrollarea.setWidget(self.table_data[current_index + 1])
                scrollarea.setWidgetResizable(1)
    
                self.tab_data[current_index + 1].layout().addWidget(scrollarea, alignment=Qt.AlignHCenter)
            else:
                self.diffraction_pattern_tabs.insertTab(current_index + 1, diffraction_pattern_tab, "TEMP")
                self.diffraction_pattern_box_array.insert(current_index + 1, diffraction_pattern_box)
                
                self.tabs.insertTab(current_index + 1, diffraction_pattern_pd_tab, "TEMP")
                self.tab_diff.insert(current_index + 1, diffraction_pattern_pd_tab)
    
                self.tabs_data_plot.insert(current_index + 1, gui.tabWidget(self.tab_diff[current_index + 1]))
                self.tab_data.insert(current_index + 1, gui.createTabPage(self.tabs_data_plot[current_index + 1], "Data"))
                self.tab_plot.insert(current_index + 1, gui.createTabPage(self.tabs_data_plot[current_index + 1], "Plot"))
    
                self.plot.insert(current_index + 1, PlotWindow())
                self.plot[current_index + 1].setDefaultPlotLines(True)
                self.plot[current_index + 1].setActiveCurveColor(color="#00008B")
                self.plot[current_index + 1].setGraphXLabel(r"2$\theta$")
                self.plot[current_index + 1].setGraphYLabel("Intensity")
    
                self.tab_plot[current_index + 1].layout().addWidget(self.plot[current_index + 1])
    
                scrollarea = QScrollArea(self.tab_data[current_index + 1])
                scrollarea.setMinimumWidth(805)
                scrollarea.setMinimumHeight(605)
    
                self.table_data.insert(current_index + 1, self.create_table_widget())
    
                scrollarea.setWidget(self.table_data[current_index + 1])
                scrollarea.setWidgetResizable(1)
    
                self.tab_data[current_index + 1].layout().addWidget(scrollarea, alignment=Qt.AlignHCenter)

            for index in range(current_index, self.diffraction_pattern_tabs.count()):
                self.diffraction_pattern_tabs.setTabText(index, "Diff. Patt." + str(index + 1))
                self.diffraction_pattern_box_array[index].index = index
                self.tabs.setTabText(index, "Diff. Patt." + str(index + 1))

            self.dumpSettings()
            self.diffraction_pattern_tabs.setCurrentIndex(current_index + 1)
            self.tabs.setCurrentIndex(current_index + 1)

    def remove(self):
        if self.diffraction_pattern_tabs.count() <= 1:
            QtWidgets.QMessageBox.critical(self, "Error",
                                       "Remove not possible, Fit process needs at least 1 element",
                                       QtWidgets.QMessageBox.Ok)
        else:
            current_index = self.diffraction_pattern_tabs.currentIndex()

            if ConfirmDialog.confirmed(parent=self, message="Confirm Removal of " + self.diffraction_pattern_tabs.tabText(current_index) + "?"):
                self.diffraction_pattern_tabs.removeTab(current_index)
                self.diffraction_pattern_box_array.pop(current_index)

                self.tabs.removeTab(current_index)
                self.tab_diff.pop(current_index)
                self.tabs_data_plot.pop(current_index)
                self.tab_data.pop(current_index)
                self.tab_plot.pop(current_index)
                self.plot.pop(current_index)
                self.table_data.pop(current_index)

                for index in range(current_index, self.diffraction_pattern_tabs.count()):
                    self.diffraction_pattern_tabs.setTabText(index, "Diff. Patt." + str(index + 1))
                    self.diffraction_pattern_box_array[index].index = index
                    self.tabs.setTabText(index, "Diff. Patt." + str(index + 1))

                self.dumpSettings()
                self.diffraction_pattern_tabs.setCurrentIndex(current_index)
                self.tabs.setCurrentIndex(current_index)

    def load_diffraction_patterns(self):
        try:
            self.dumpSettings()

            self.diffraction_patterns = []
            for index in range(len(self.filename)):
                self.diffraction_pattern_box_array[index].load_diffraction_pattern()
                self.diffraction_patterns.append(self.diffraction_pattern_box_array[index].diffraction_pattern)

                self.show_data(index)

            self.tabs.setCurrentIndex(self.diffraction_pattern_tabs.currentIndex())
            self.tabs_data_plot[self.diffraction_pattern_tabs.currentIndex()].setCurrentIndex(1)

            fit_global_parameters = FitGlobalParameters(fit_initialization=FitInitialization(diffraction_patterns=self.diffraction_patterns))
            fit_global_parameters.regenerate_parameters()

            self.send("Fit Global Parameters", fit_global_parameters)

        except Exception as e:
            QMessageBox.critical(self, "Error during load",
                                 str(e),
                                 QMessageBox.Ok)

            if self.IS_DEVELOP: raise e

    def show_data(self, diffraction_pattern_index=0):
        diffraction_pattern = self.diffraction_patterns[diffraction_pattern_index]

        x = []
        y = []

        for index in range(0, diffraction_pattern.diffraction_points_count()):
            x.append(diffraction_pattern.get_diffraction_point(index).twotheta)
            y.append(diffraction_pattern.get_diffraction_point(index).intensity)

        self.plot[diffraction_pattern_index].addCurve(x, y, linewidth=2, color="#0B0B61")

        self.populate_table(self.table_data[diffraction_pattern_index], diffraction_pattern)


    def create_table_widget(self):
        table = QTableWidget(1, 4)
        table.setMinimumWidth(750)
        table.setAlternatingRowColors(True)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        table.verticalHeader().setVisible(False)
        table.setHorizontalHeaderLabels(self.horizontal_headers)
        table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)

        return table

    def populate_table(self, table_widget, diffraction_pattern):
        table_widget.clear()

        row_count = table_widget.rowCount()
        for n in range(0, row_count):
            table_widget.removeRow(0)

        for index in range(0, diffraction_pattern.diffraction_points_count()):
            table_widget.insertRow(0)

        for index in range(0, diffraction_pattern.diffraction_points_count()):

            table_item = QTableWidgetItem(str(round(diffraction_pattern.get_diffraction_point(index).twotheta, 6)))
            table_item.setTextAlignment(Qt.AlignRight)
            table_widget.setItem(index, 0, table_item)

            table_item = QTableWidgetItem(str(round(diffraction_pattern.get_diffraction_point(index).s, 6)))
            table_item.setTextAlignment(Qt.AlignRight)
            table_widget.setItem(index, 1, table_item)

            table_item = QTableWidgetItem(str(round(diffraction_pattern.get_diffraction_point(index).intensity, 6)))
            table_item.setTextAlignment(Qt.AlignRight)
            table_widget.setItem(index, 2, table_item)

            table_item = QTableWidgetItem(str(round(0.0 if diffraction_pattern.get_diffraction_point(index).error is None else diffraction_pattern.get_diffraction_point(index).error, 6)))
            table_item.setTextAlignment(Qt.AlignRight)
            table_widget.setItem(index, 3, table_item)

        table_widget.setHorizontalHeaderLabels(self.horizontal_headers)
        table_widget.resizeRowsToContents()
        table_widget.setSelectionBehavior(QAbstractItemView.SelectRows)
        table_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)


    ##############################
    # SINGLE FIELDS SIGNALS
    ##############################

    def dumpSettings(self):
        self.dump_filename()
        self.dump_is_multiple_wavelength()
        self.dump_wavelength()
        self.dump_xray_tube_key()
        self.dump_wavelength_2()
        self.dump_wavelength_3()
        self.dump_wavelength_4()
        self.dump_wavelength_5()
        self.dump_weight_2()
        self.dump_weight_3()
        self.dump_weight_4()
        self.dump_weight_5()
        self.dump_twotheta_has_min()
        self.dump_twotheta_min()
        self.dump_twotheta_has_max()
        self.dump_twotheta_max()

    def dump_filename(self):
        bkp_filename = copy.deepcopy(self.filename)

        try:
            self.filename = []

            for index in range(len(self.diffraction_pattern_box_array)):
                self.filename.append(self.diffraction_pattern_box_array[index].filename)
        except:
            self.filename = copy.deepcopy(bkp_filename)

    def dump_is_multiple_wavelength(self):
        bkp_is_multiple_wavelength = copy.deepcopy(self.is_multiple_wavelength)

        try:
            self.is_multiple_wavelength = []

            for index in range(len(self.diffraction_pattern_box_array)):
                self.is_multiple_wavelength.append(self.diffraction_pattern_box_array[index].is_multiple_wavelength)
        except:
            self.is_multiple_wavelength = copy.deepcopy(bkp_is_multiple_wavelength)

    def dump_xray_tube_key(self):
        bkp_xray_tube_key = copy.deepcopy(self.xray_tube_key)

        try:
            self.xray_tube_key = []

            for index in range(len(self.diffraction_pattern_box_array)):
                self.xray_tube_key.append(self.diffraction_pattern_box_array[index].xray_tube_key)
        except:
            self.xray_tube_key = copy.deepcopy(bkp_xray_tube_key)

    def dump_twotheta_min(self):
        bkp_twotheta_min = copy.deepcopy(self.twotheta_min)

        try:
            self.twotheta_min = []

            for index in range(len(self.diffraction_pattern_box_array)):
                self.twotheta_min.append(self.diffraction_pattern_box_array[index].twotheta_min)
        except:
            self.twotheta_min = copy.deepcopy(bkp_twotheta_min)

    def dump_twotheta_has_min(self):
        bkp_twotheta_has_min = copy.deepcopy(self.twotheta_has_min)

        try:
            self.twotheta_has_min = []

            for index in range(len(self.diffraction_pattern_box_array)):
                self.twotheta_has_min.append(self.diffraction_pattern_box_array[index].twotheta_has_min)
        except:
            self.twotheta_has_min = copy.deepcopy(bkp_twotheta_has_min)

    def dump_twotheta_max(self):
        bkp_twotheta_max = copy.deepcopy(self.twotheta_max)

        try:
            self.twotheta_max = []

            for index in range(len(self.diffraction_pattern_box_array)):
                self.twotheta_max.append(self.diffraction_pattern_box_array[index].twotheta_max)
        except:
            self.twotheta_max = copy.deepcopy(bkp_twotheta_max)

    def dump_twotheta_has_max(self):
        bkp_twotheta_has_max = copy.deepcopy(self.twotheta_has_max)

        try:
            self.twotheta_has_max = []

            for index in range(len(self.diffraction_pattern_box_array)):
                self.twotheta_has_max.append(self.diffraction_pattern_box_array[index].twotheta_has_max)
        except:
            self.twotheta_has_max = copy.deepcopy(bkp_twotheta_has_max)


    def dump_wavelength(self):
        bkp_wavelength                = copy.deepcopy(self.wavelength               )
        bkp_wavelength_fixed          = copy.deepcopy(self.wavelength_fixed         )
        bkp_wavelength_has_min        = copy.deepcopy(self.wavelength_has_min       )
        bkp_wavelength_min            = copy.deepcopy(self.wavelength_min           )
        bkp_wavelength_has_max        = copy.deepcopy(self.wavelength_has_max       )
        bkp_wavelength_max            = copy.deepcopy(self.wavelength_max           )
        bkp_wavelength_function       = copy.deepcopy(self.wavelength_function      )
        bkp_wavelength_function_value = copy.deepcopy(self.wavelength_function_value)
        
        try:
            self.wavelength                = []
            self.wavelength_fixed          = []
            self.wavelength_has_min        = []
            self.wavelength_min            = []
            self.wavelength_has_max        = []
            self.wavelength_max            = []
            self.wavelength_function       = []
            self.wavelength_function_value = []    
        
            for index in range(len(self.diffraction_pattern_box_array)):
                self.wavelength.append(self.diffraction_pattern_box_array[index].wavelength)
                self.wavelength_fixed.append(self.diffraction_pattern_box_array[index].wavelength_fixed)
                self.wavelength_has_min.append(self.diffraction_pattern_box_array[index].wavelength_has_min)
                self.wavelength_min.append(self.diffraction_pattern_box_array[index].wavelength_min)
                self.wavelength_has_max.append(self.diffraction_pattern_box_array[index].wavelength_has_max)
                self.wavelength_max.append(self.diffraction_pattern_box_array[index].wavelength_max)
                self.wavelength_function.append(self.diffraction_pattern_box_array[index].wavelength_function)
                self.wavelength_function_value.append(self.diffraction_pattern_box_array[index].wavelength_function_value)
        except:
            self.wavelength                = copy.deepcopy(bkp_wavelength               )
            self.wavelength_fixed          = copy.deepcopy(bkp_wavelength_fixed         )
            self.wavelength_has_min        = copy.deepcopy(bkp_wavelength_has_min       )
            self.wavelength_min            = copy.deepcopy(bkp_wavelength_min           )
            self.wavelength_has_max        = copy.deepcopy(bkp_wavelength_has_max       )
            self.wavelength_max            = copy.deepcopy(bkp_wavelength_max           )
            self.wavelength_function       = copy.deepcopy(bkp_wavelength_function      )
            self.wavelength_function_value = copy.deepcopy(bkp_wavelength_function_value)
    
    def dump_wavelength_2(self):
        bkp_wavelength_2                = copy.deepcopy(self.wavelength_2               )
        bkp_wavelength_2_fixed          = copy.deepcopy(self.wavelength_2_fixed         )
        bkp_wavelength_2_has_min        = copy.deepcopy(self.wavelength_2_has_min       )
        bkp_wavelength_2_min            = copy.deepcopy(self.wavelength_2_min           )
        bkp_wavelength_2_has_max        = copy.deepcopy(self.wavelength_2_has_max       )
        bkp_wavelength_2_max            = copy.deepcopy(self.wavelength_2_max           )
        bkp_wavelength_2_function       = copy.deepcopy(self.wavelength_2_function      )
        bkp_wavelength_2_function_value = copy.deepcopy(self.wavelength_2_function_value)
        
        try:
            self.wavelength_2                = []
            self.wavelength_2_fixed          = []
            self.wavelength_2_has_min        = []
            self.wavelength_2_min            = []
            self.wavelength_2_has_max        = []
            self.wavelength_2_max            = []
            self.wavelength_2_function       = []
            self.wavelength_2_function_value = []    
        
            for index in range(len(self.diffraction_pattern_box_array)):
                self.wavelength_2.append(self.diffraction_pattern_box_array[index].wavelength_2)
                self.wavelength_2_fixed.append(self.diffraction_pattern_box_array[index].wavelength_2_fixed)
                self.wavelength_2_has_min.append(self.diffraction_pattern_box_array[index].wavelength_2_has_min)
                self.wavelength_2_min.append(self.diffraction_pattern_box_array[index].wavelength_2_min)
                self.wavelength_2_has_max.append(self.diffraction_pattern_box_array[index].wavelength_2_has_max)
                self.wavelength_2_max.append(self.diffraction_pattern_box_array[index].wavelength_2_max)
                self.wavelength_2_function.append(self.diffraction_pattern_box_array[index].wavelength_2_function)
                self.wavelength_2_function_value.append(self.diffraction_pattern_box_array[index].wavelength_2_function_value)
        except:
            self.wavelength_2                = copy.deepcopy(bkp_wavelength_2               )
            self.wavelength_2_fixed          = copy.deepcopy(bkp_wavelength_2_fixed         )
            self.wavelength_2_has_min        = copy.deepcopy(bkp_wavelength_2_has_min       )
            self.wavelength_2_min            = copy.deepcopy(bkp_wavelength_2_min           )
            self.wavelength_2_has_max        = copy.deepcopy(bkp_wavelength_2_has_max       )
            self.wavelength_2_max            = copy.deepcopy(bkp_wavelength_2_max           )
            self.wavelength_2_function       = copy.deepcopy(bkp_wavelength_2_function      )
            self.wavelength_2_function_value = copy.deepcopy(bkp_wavelength_2_function_value)

    def dump_wavelength_3(self):
        bkp_wavelength_3                = copy.deepcopy(self.wavelength_3               )
        bkp_wavelength_3_fixed          = copy.deepcopy(self.wavelength_3_fixed         )
        bkp_wavelength_3_has_min        = copy.deepcopy(self.wavelength_3_has_min       )
        bkp_wavelength_3_min            = copy.deepcopy(self.wavelength_3_min           )
        bkp_wavelength_3_has_max        = copy.deepcopy(self.wavelength_3_has_max       )
        bkp_wavelength_3_max            = copy.deepcopy(self.wavelength_3_max           )
        bkp_wavelength_3_function       = copy.deepcopy(self.wavelength_3_function      )
        bkp_wavelength_3_function_value = copy.deepcopy(self.wavelength_3_function_value)
        
        try:
            self.wavelength_3                = []
            self.wavelength_3_fixed          = []
            self.wavelength_3_has_min        = []
            self.wavelength_3_min            = []
            self.wavelength_3_has_max        = []
            self.wavelength_3_max            = []
            self.wavelength_3_function       = []
            self.wavelength_3_function_value = []    
        
            for index in range(len(self.diffraction_pattern_box_array)):
                self.wavelength_3.append(self.diffraction_pattern_box_array[index].wavelength_3)
                self.wavelength_3_fixed.append(self.diffraction_pattern_box_array[index].wavelength_3_fixed)
                self.wavelength_3_has_min.append(self.diffraction_pattern_box_array[index].wavelength_3_has_min)
                self.wavelength_3_min.append(self.diffraction_pattern_box_array[index].wavelength_3_min)
                self.wavelength_3_has_max.append(self.diffraction_pattern_box_array[index].wavelength_3_has_max)
                self.wavelength_3_max.append(self.diffraction_pattern_box_array[index].wavelength_3_max)
                self.wavelength_3_function.append(self.diffraction_pattern_box_array[index].wavelength_3_function)
                self.wavelength_3_function_value.append(self.diffraction_pattern_box_array[index].wavelength_3_function_value)
        except:
            self.wavelength_3                = copy.deepcopy(bkp_wavelength_3               )
            self.wavelength_3_fixed          = copy.deepcopy(bkp_wavelength_3_fixed         )
            self.wavelength_3_has_min        = copy.deepcopy(bkp_wavelength_3_has_min       )
            self.wavelength_3_min            = copy.deepcopy(bkp_wavelength_3_min           )
            self.wavelength_3_has_max        = copy.deepcopy(bkp_wavelength_3_has_max       )
            self.wavelength_3_max            = copy.deepcopy(bkp_wavelength_3_max           )
            self.wavelength_3_function       = copy.deepcopy(bkp_wavelength_3_function      )
            self.wavelength_3_function_value = copy.deepcopy(bkp_wavelength_3_function_value)

    def dump_wavelength_4(self):
        bkp_wavelength_4                = copy.deepcopy(self.wavelength_4               )
        bkp_wavelength_4_fixed          = copy.deepcopy(self.wavelength_4_fixed         )
        bkp_wavelength_4_has_min        = copy.deepcopy(self.wavelength_4_has_min       )
        bkp_wavelength_4_min            = copy.deepcopy(self.wavelength_4_min           )
        bkp_wavelength_4_has_max        = copy.deepcopy(self.wavelength_4_has_max       )
        bkp_wavelength_4_max            = copy.deepcopy(self.wavelength_4_max           )
        bkp_wavelength_4_function       = copy.deepcopy(self.wavelength_4_function      )
        bkp_wavelength_4_function_value = copy.deepcopy(self.wavelength_4_function_value)
        
        try:
            self.wavelength_4                = []
            self.wavelength_4_fixed          = []
            self.wavelength_4_has_min        = []
            self.wavelength_4_min            = []
            self.wavelength_4_has_max        = []
            self.wavelength_4_max            = []
            self.wavelength_4_function       = []
            self.wavelength_4_function_value = []    
        
            for index in range(len(self.diffraction_pattern_box_array)):
                self.wavelength_4.append(self.diffraction_pattern_box_array[index].wavelength_4)
                self.wavelength_4_fixed.append(self.diffraction_pattern_box_array[index].wavelength_4_fixed)
                self.wavelength_4_has_min.append(self.diffraction_pattern_box_array[index].wavelength_4_has_min)
                self.wavelength_4_min.append(self.diffraction_pattern_box_array[index].wavelength_4_min)
                self.wavelength_4_has_max.append(self.diffraction_pattern_box_array[index].wavelength_4_has_max)
                self.wavelength_4_max.append(self.diffraction_pattern_box_array[index].wavelength_4_max)
                self.wavelength_4_function.append(self.diffraction_pattern_box_array[index].wavelength_4_function)
                self.wavelength_4_function_value.append(self.diffraction_pattern_box_array[index].wavelength_4_function_value)
        except:
            self.wavelength_4                = copy.deepcopy(bkp_wavelength_4               )
            self.wavelength_4_fixed          = copy.deepcopy(bkp_wavelength_4_fixed         )
            self.wavelength_4_has_min        = copy.deepcopy(bkp_wavelength_4_has_min       )
            self.wavelength_4_min            = copy.deepcopy(bkp_wavelength_4_min           )
            self.wavelength_4_has_max        = copy.deepcopy(bkp_wavelength_4_has_max       )
            self.wavelength_4_max            = copy.deepcopy(bkp_wavelength_4_max           )
            self.wavelength_4_function       = copy.deepcopy(bkp_wavelength_4_function      )
            self.wavelength_4_function_value = copy.deepcopy(bkp_wavelength_4_function_value)

    def dump_wavelength_5(self):
        bkp_wavelength_5                = copy.deepcopy(self.wavelength_5               )
        bkp_wavelength_5_fixed          = copy.deepcopy(self.wavelength_5_fixed         )
        bkp_wavelength_5_has_min        = copy.deepcopy(self.wavelength_5_has_min       )
        bkp_wavelength_5_min            = copy.deepcopy(self.wavelength_5_min           )
        bkp_wavelength_5_has_max        = copy.deepcopy(self.wavelength_5_has_max       )
        bkp_wavelength_5_max            = copy.deepcopy(self.wavelength_5_max           )
        bkp_wavelength_5_function       = copy.deepcopy(self.wavelength_5_function      )
        bkp_wavelength_5_function_value = copy.deepcopy(self.wavelength_5_function_value)
        
        try:
            self.wavelength_5                = []
            self.wavelength_5_fixed          = []
            self.wavelength_5_has_min        = []
            self.wavelength_5_min            = []
            self.wavelength_5_has_max        = []
            self.wavelength_5_max            = []
            self.wavelength_5_function       = []
            self.wavelength_5_function_value = []    
        
            for index in range(len(self.diffraction_pattern_box_array)):
                self.wavelength_5.append(self.diffraction_pattern_box_array[index].wavelength_5)
                self.wavelength_5_fixed.append(self.diffraction_pattern_box_array[index].wavelength_5_fixed)
                self.wavelength_5_has_min.append(self.diffraction_pattern_box_array[index].wavelength_5_has_min)
                self.wavelength_5_min.append(self.diffraction_pattern_box_array[index].wavelength_5_min)
                self.wavelength_5_has_max.append(self.diffraction_pattern_box_array[index].wavelength_5_has_max)
                self.wavelength_5_max.append(self.diffraction_pattern_box_array[index].wavelength_5_max)
                self.wavelength_5_function.append(self.diffraction_pattern_box_array[index].wavelength_5_function)
                self.wavelength_5_function_value.append(self.diffraction_pattern_box_array[index].wavelength_5_function_value)
        except:
            self.wavelength_5                = copy.deepcopy(bkp_wavelength_5               )
            self.wavelength_5_fixed          = copy.deepcopy(bkp_wavelength_5_fixed         )
            self.wavelength_5_has_min        = copy.deepcopy(bkp_wavelength_5_has_min       )
            self.wavelength_5_min            = copy.deepcopy(bkp_wavelength_5_min           )
            self.wavelength_5_has_max        = copy.deepcopy(bkp_wavelength_5_has_max       )
            self.wavelength_5_max            = copy.deepcopy(bkp_wavelength_5_max           )
            self.wavelength_5_function       = copy.deepcopy(bkp_wavelength_5_function      )
            self.wavelength_5_function_value = copy.deepcopy(bkp_wavelength_5_function_value)

    def dump_weight_2(self):
        bkp_weight_2                = copy.deepcopy(self.weight_2               )
        bkp_weight_2_fixed          = copy.deepcopy(self.weight_2_fixed         )
        bkp_weight_2_has_min        = copy.deepcopy(self.weight_2_has_min       )
        bkp_weight_2_min            = copy.deepcopy(self.weight_2_min           )
        bkp_weight_2_has_max        = copy.deepcopy(self.weight_2_has_max       )
        bkp_weight_2_max            = copy.deepcopy(self.weight_2_max           )
        bkp_weight_2_function       = copy.deepcopy(self.weight_2_function      )
        bkp_weight_2_function_value = copy.deepcopy(self.weight_2_function_value)
        
        try:
            self.weight_2                = []
            self.weight_2_fixed          = []
            self.weight_2_has_min        = []
            self.weight_2_min            = []
            self.weight_2_has_max        = []
            self.weight_2_max            = []
            self.weight_2_function       = []
            self.weight_2_function_value = []    
        
            for index in range(len(self.diffraction_pattern_box_array)):
                self.weight_2.append(self.diffraction_pattern_box_array[index].weight_2)
                self.weight_2_fixed.append(self.diffraction_pattern_box_array[index].weight_2_fixed)
                self.weight_2_has_min.append(self.diffraction_pattern_box_array[index].weight_2_has_min)
                self.weight_2_min.append(self.diffraction_pattern_box_array[index].weight_2_min)
                self.weight_2_has_max.append(self.diffraction_pattern_box_array[index].weight_2_has_max)
                self.weight_2_max.append(self.diffraction_pattern_box_array[index].weight_2_max)
                self.weight_2_function.append(self.diffraction_pattern_box_array[index].weight_2_function)
                self.weight_2_function_value.append(self.diffraction_pattern_box_array[index].weight_2_function_value)
        except:
            self.weight_2                = copy.deepcopy(bkp_weight_2               )
            self.weight_2_fixed          = copy.deepcopy(bkp_weight_2_fixed         )
            self.weight_2_has_min        = copy.deepcopy(bkp_weight_2_has_min       )
            self.weight_2_min            = copy.deepcopy(bkp_weight_2_min           )
            self.weight_2_has_max        = copy.deepcopy(bkp_weight_2_has_max       )
            self.weight_2_max            = copy.deepcopy(bkp_weight_2_max           )
            self.weight_2_function       = copy.deepcopy(bkp_weight_2_function      )
            self.weight_2_function_value = copy.deepcopy(bkp_weight_2_function_value)

    def dump_weight_3(self):
        bkp_weight_3                = copy.deepcopy(self.weight_3               )
        bkp_weight_3_fixed          = copy.deepcopy(self.weight_3_fixed         )
        bkp_weight_3_has_min        = copy.deepcopy(self.weight_3_has_min       )
        bkp_weight_3_min            = copy.deepcopy(self.weight_3_min           )
        bkp_weight_3_has_max        = copy.deepcopy(self.weight_3_has_max       )
        bkp_weight_3_max            = copy.deepcopy(self.weight_3_max           )
        bkp_weight_3_function       = copy.deepcopy(self.weight_3_function      )
        bkp_weight_3_function_value = copy.deepcopy(self.weight_3_function_value)
        
        try:
            self.weight_3                = []
            self.weight_3_fixed          = []
            self.weight_3_has_min        = []
            self.weight_3_min            = []
            self.weight_3_has_max        = []
            self.weight_3_max            = []
            self.weight_3_function       = []
            self.weight_3_function_value = []    
        
            for index in range(len(self.diffraction_pattern_box_array)):
                self.weight_3.append(self.diffraction_pattern_box_array[index].weight_3)
                self.weight_3_fixed.append(self.diffraction_pattern_box_array[index].weight_3_fixed)
                self.weight_3_has_min.append(self.diffraction_pattern_box_array[index].weight_3_has_min)
                self.weight_3_min.append(self.diffraction_pattern_box_array[index].weight_3_min)
                self.weight_3_has_max.append(self.diffraction_pattern_box_array[index].weight_3_has_max)
                self.weight_3_max.append(self.diffraction_pattern_box_array[index].weight_3_max)
                self.weight_3_function.append(self.diffraction_pattern_box_array[index].weight_3_function)
                self.weight_3_function_value.append(self.diffraction_pattern_box_array[index].weight_3_function_value)
        except:
            self.weight_3                = copy.deepcopy(bkp_weight_3               )
            self.weight_3_fixed          = copy.deepcopy(bkp_weight_3_fixed         )
            self.weight_3_has_min        = copy.deepcopy(bkp_weight_3_has_min       )
            self.weight_3_min            = copy.deepcopy(bkp_weight_3_min           )
            self.weight_3_has_max        = copy.deepcopy(bkp_weight_3_has_max       )
            self.weight_3_max            = copy.deepcopy(bkp_weight_3_max           )
            self.weight_3_function       = copy.deepcopy(bkp_weight_3_function      )
            self.weight_3_function_value = copy.deepcopy(bkp_weight_3_function_value)

    def dump_weight_4(self):
        bkp_weight_4                = copy.deepcopy(self.weight_4               )
        bkp_weight_4_fixed          = copy.deepcopy(self.weight_4_fixed         )
        bkp_weight_4_has_min        = copy.deepcopy(self.weight_4_has_min       )
        bkp_weight_4_min            = copy.deepcopy(self.weight_4_min           )
        bkp_weight_4_has_max        = copy.deepcopy(self.weight_4_has_max       )
        bkp_weight_4_max            = copy.deepcopy(self.weight_4_max           )
        bkp_weight_4_function       = copy.deepcopy(self.weight_4_function      )
        bkp_weight_4_function_value = copy.deepcopy(self.weight_4_function_value)
        
        try:
            self.weight_4                = []
            self.weight_4_fixed          = []
            self.weight_4_has_min        = []
            self.weight_4_min            = []
            self.weight_4_has_max        = []
            self.weight_4_max            = []
            self.weight_4_function       = []
            self.weight_4_function_value = []    
        
            for index in range(len(self.diffraction_pattern_box_array)):
                self.weight_4.append(self.diffraction_pattern_box_array[index].weight_4)
                self.weight_4_fixed.append(self.diffraction_pattern_box_array[index].weight_4_fixed)
                self.weight_4_has_min.append(self.diffraction_pattern_box_array[index].weight_4_has_min)
                self.weight_4_min.append(self.diffraction_pattern_box_array[index].weight_4_min)
                self.weight_4_has_max.append(self.diffraction_pattern_box_array[index].weight_4_has_max)
                self.weight_4_max.append(self.diffraction_pattern_box_array[index].weight_4_max)
                self.weight_4_function.append(self.diffraction_pattern_box_array[index].weight_4_function)
                self.weight_4_function_value.append(self.diffraction_pattern_box_array[index].weight_4_function_value)
        except:
            self.weight_4                = copy.deepcopy(bkp_weight_4               )
            self.weight_4_fixed          = copy.deepcopy(bkp_weight_4_fixed         )
            self.weight_4_has_min        = copy.deepcopy(bkp_weight_4_has_min       )
            self.weight_4_min            = copy.deepcopy(bkp_weight_4_min           )
            self.weight_4_has_max        = copy.deepcopy(bkp_weight_4_has_max       )
            self.weight_4_max            = copy.deepcopy(bkp_weight_4_max           )
            self.weight_4_function       = copy.deepcopy(bkp_weight_4_function      )
            self.weight_4_function_value = copy.deepcopy(bkp_weight_4_function_value)

    def dump_weight_5(self):
        bkp_weight_5                = copy.deepcopy(self.weight_5               )
        bkp_weight_5_fixed          = copy.deepcopy(self.weight_5_fixed         )
        bkp_weight_5_has_min        = copy.deepcopy(self.weight_5_has_min       )
        bkp_weight_5_min            = copy.deepcopy(self.weight_5_min           )
        bkp_weight_5_has_max        = copy.deepcopy(self.weight_5_has_max       )
        bkp_weight_5_max            = copy.deepcopy(self.weight_5_max           )
        bkp_weight_5_function       = copy.deepcopy(self.weight_5_function      )
        bkp_weight_5_function_value = copy.deepcopy(self.weight_5_function_value)
        
        try:
            self.weight_5                = []
            self.weight_5_fixed          = []
            self.weight_5_has_min        = []
            self.weight_5_min            = []
            self.weight_5_has_max        = []
            self.weight_5_max            = []
            self.weight_5_function       = []
            self.weight_5_function_value = []    
        
            for index in range(len(self.diffraction_pattern_box_array)):
                self.weight_5.append(self.diffraction_pattern_box_array[index].weight_5)
                self.weight_5_fixed.append(self.diffraction_pattern_box_array[index].weight_5_fixed)
                self.weight_5_has_min.append(self.diffraction_pattern_box_array[index].weight_5_has_min)
                self.weight_5_min.append(self.diffraction_pattern_box_array[index].weight_5_min)
                self.weight_5_has_max.append(self.diffraction_pattern_box_array[index].weight_5_has_max)
                self.weight_5_max.append(self.diffraction_pattern_box_array[index].weight_5_max)
                self.weight_5_function.append(self.diffraction_pattern_box_array[index].weight_5_function)
                self.weight_5_function_value.append(self.diffraction_pattern_box_array[index].weight_5_function_value)
        except:
            self.weight_5                = copy.deepcopy(bkp_weight_5               )
            self.weight_5_fixed          = copy.deepcopy(bkp_weight_5_fixed         )
            self.weight_5_has_min        = copy.deepcopy(bkp_weight_5_has_min       )
            self.weight_5_min            = copy.deepcopy(bkp_weight_5_min           )
            self.weight_5_has_max        = copy.deepcopy(bkp_weight_5_has_max       )
            self.weight_5_max            = copy.deepcopy(bkp_weight_5_max           )
            self.weight_5_function       = copy.deepcopy(bkp_weight_5_function      )
            self.weight_5_function_value = copy.deepcopy(bkp_weight_5_function_value)

from Orange.widgets.gui import OWComponent
from PyQt5 import QtWidgets

class DiffractionPatternBox(QtWidgets.QWidget, OWComponent):

    filename = "<input file>"
    is_multiple_wavelength = 0
    wavelength = 0.0826
    wavelength_fixed = 0
    wavelength_has_min = 0
    wavelength_min = 0.0
    wavelength_has_max = 0
    wavelength_max = 0.0
    wavelength_function = 0
    wavelength_function_value = ""
    xray_tube_key = "CuKa2"
    wavelength_2 = 0
    wavelength_2_fixed = 1
    wavelength_2_has_min = 0
    wavelength_2_min = 0.0
    wavelength_2_has_max = 0
    wavelength_2_max = 0.0
    wavelength_2_function = 0
    wavelength_2_function_value = ""
    wavelength_3 = 0
    wavelength_3_fixed = 1
    wavelength_3_has_min = 0
    wavelength_3_min = 0.0
    wavelength_3_has_max = 0
    wavelength_3_max = 0.0
    wavelength_3_function = 0
    wavelength_3_function_value = ""
    wavelength_4 = 0
    wavelength_4_fixed = 1
    wavelength_4_has_min = 0
    wavelength_4_min = 0.0
    wavelength_4_has_max = 0
    wavelength_4_max = 0.0
    wavelength_4_function = 0
    wavelength_4_function_value = ""
    wavelength_5 = 0
    wavelength_5_fixed = 1
    wavelength_5_has_min = 0
    wavelength_5_min = 0.0
    wavelength_5_has_max = 0
    wavelength_5_max = 0.0
    wavelength_5_function = 0
    wavelength_5_function_value = ""
    weight_2 = 0
    weight_2_fixed = 1
    weight_2_has_min = 0
    weight_2_min = 0.0
    weight_2_has_max = 0
    weight_2_max = 0.0
    weight_2_function = 0
    weight_2_function_value = ""
    weight_3 = 0
    weight_3_fixed = 1
    weight_3_has_min = 0
    weight_3_min = 0.0
    weight_3_has_max = 0
    weight_3_max = 0.0
    weight_3_function = 0
    weight_3_function_value = ""
    weight_4 = 0
    weight_4_fixed = 1
    weight_4_has_min = 0
    weight_4_min = 0.0
    weight_4_has_max = 0
    weight_4_max = 0.0
    weight_4_function = 0
    weight_4_function_value = ""
    weight_5 = 0
    weight_5_fixed = 1
    weight_5_has_min = 0
    weight_5_min = 0.0
    weight_5_has_max = 0
    weight_5_max = 0.0
    weight_5_function = 0
    weight_5_function_value = ""
    twotheta_min = 0.0
    twotheta_has_min = 0
    twotheta_max = 0.0
    twotheta_has_max = 0

    widget = None
    is_on_init = True

    parameter_functions = {}

    diffraction_pattern = None

    index = 0

    def __init__(self,
                 widget=None,
                 parent=None,
                 index = 0,
                 filename = "<input file>",
                 is_multiple_wavelength = 0,
                 wavelength = 0.0826,
                 wavelength_fixed = 0,
                 wavelength_has_min = 0,
                 wavelength_min = 0.0,
                 wavelength_has_max = 0,
                 wavelength_max = 0.0,
                 wavelength_function = 0,
                 wavelength_function_value = "",
                 xray_tube_key = "CuKa2",
                 wavelength_2 = 0,
                 wavelength_2_fixed = 1,
                 wavelength_2_has_min = 0,
                 wavelength_2_min = 0.0,
                 wavelength_2_has_max = 0,
                 wavelength_2_max = 0.0,
                 wavelength_2_function = 0,
                 wavelength_2_function_value = "",
                 wavelength_3 = 0,
                 wavelength_3_fixed = 1,
                 wavelength_3_has_min = 0,
                 wavelength_3_min = 0.0,
                 wavelength_3_has_max = 0,
                 wavelength_3_max = 0.0,
                 wavelength_3_function = 0,
                 wavelength_3_function_value = "",
                 wavelength_4 = 0,
                 wavelength_4_fixed = 1,
                 wavelength_4_has_min = 0,
                 wavelength_4_min = 0.0,
                 wavelength_4_has_max = 0,
                 wavelength_4_max = 0.0,
                 wavelength_4_function = 0,
                 wavelength_4_function_value = "",
                 wavelength_5 = 0,
                 wavelength_5_fixed = 1,
                 wavelength_5_has_min = 0,
                 wavelength_5_min = 0.0,
                 wavelength_5_has_max = 0,
                 wavelength_5_max = 0.0,
                 wavelength_5_function = 0,
                 wavelength_5_function_value = "",
                 weight_2 = 0,
                 weight_2_fixed = 1,
                 weight_2_has_min = 0,
                 weight_2_min = 0.0,
                 weight_2_has_max = 0,
                 weight_2_max = 0.0,
                 weight_2_function = 0,
                 weight_2_function_value = "",
                 weight_3 = 0,
                 weight_3_fixed = 1,
                 weight_3_has_min = 0,
                 weight_3_min = 0.0,
                 weight_3_has_max = 0,
                 weight_3_max = 0.0,
                 weight_3_function = 0,
                 weight_3_function_value = "",
                 weight_4 = 0,
                 weight_4_fixed = 1,
                 weight_4_has_min = 0,
                 weight_4_min = 0.0,
                 weight_4_has_max = 0,
                 weight_4_max = 0.0,
                 weight_4_function = 0,
                 weight_4_function_value = "",
                 weight_5 = 0,
                 weight_5_fixed = 1,
                 weight_5_has_min = 0,
                 weight_5_min = 0.0,
                 weight_5_has_max = 0,
                 weight_5_max = 0.0,
                 weight_5_function = 0,
                 weight_5_function_value = "",
                 twotheta_min = 0.0,
                 twotheta_has_min = 0,
                 twotheta_max = 0.0,
                 twotheta_has_max = 0):
        super(DiffractionPatternBox, self).__init__(parent)
        OWComponent.__init__(self)

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)
        self.setFixedWidth(widget.CONTROL_AREA_WIDTH - 35)
        self.setFixedHeight(500)

        self.widget = widget
        self.index = index
        
        self.filename                    = filename
        self.is_multiple_wavelength        = is_multiple_wavelength
        self.wavelength                  = wavelength
        self.wavelength_fixed            = wavelength_fixed
        self.wavelength_has_min          = wavelength_has_min
        self.wavelength_min              = wavelength_min
        self.wavelength_has_max          = wavelength_has_max
        self.wavelength_max              = wavelength_max
        self.wavelength_function         = wavelength_function
        self.wavelength_function_value   = wavelength_function_value
        self.xray_tube_key               = xray_tube_key
        self.wavelength_2                = wavelength_2
        self.wavelength_2_fixed          = wavelength_2_fixed
        self.wavelength_2_has_min        = wavelength_2_has_min
        self.wavelength_2_min            = wavelength_2_min
        self.wavelength_2_has_max        = wavelength_2_has_max
        self.wavelength_2_max            = wavelength_2_max
        self.wavelength_2_function       = wavelength_2_function
        self.wavelength_2_function_value = wavelength_2_function_value
        self.wavelength_3                = wavelength_3
        self.wavelength_3_fixed          = wavelength_3_fixed
        self.wavelength_3_has_min        = wavelength_3_has_min
        self.wavelength_3_min            = wavelength_3_min
        self.wavelength_3_has_max        = wavelength_3_has_max
        self.wavelength_3_max            = wavelength_3_max
        self.wavelength_3_function       = wavelength_3_function
        self.wavelength_3_function_value = wavelength_3_function_value
        self.wavelength_4                = wavelength_4
        self.wavelength_4_fixed          = wavelength_4_fixed
        self.wavelength_4_has_min        = wavelength_4_has_min
        self.wavelength_4_min            = wavelength_4_min
        self.wavelength_4_has_max        = wavelength_4_has_max
        self.wavelength_4_max            = wavelength_4_max
        self.wavelength_4_function       = wavelength_4_function
        self.wavelength_4_function_value = wavelength_4_function_value
        self.wavelength_5                = wavelength_5
        self.wavelength_5_fixed          = wavelength_5_fixed
        self.wavelength_5_has_min        = wavelength_5_has_min
        self.wavelength_5_min            = wavelength_5_min
        self.wavelength_5_has_max        = wavelength_5_has_max
        self.wavelength_5_max            = wavelength_5_max
        self.wavelength_5_function       = wavelength_5_function
        self.wavelength_5_function_value = wavelength_5_function_value
        self.weight_2                    = weight_2
        self.weight_2_fixed              = weight_2_fixed
        self.weight_2_has_min            = weight_2_has_min
        self.weight_2_min                = weight_2_min
        self.weight_2_has_max            = weight_2_has_max
        self.weight_2_max                = weight_2_max
        self.weight_2_function           = weight_2_function
        self.weight_2_function_value     = weight_2_function_value
        self.weight_3                    = weight_3
        self.weight_3_fixed              = weight_3_fixed
        self.weight_3_has_min            = weight_3_has_min
        self.weight_3_min                = weight_3_min
        self.weight_3_has_max            = weight_3_has_max
        self.weight_3_max                = weight_3_max
        self.weight_3_function           = weight_3_function
        self.weight_3_function_value     = weight_3_function_value
        self.weight_4                    = weight_4
        self.weight_4_fixed              = weight_4_fixed
        self.weight_4_has_min            = weight_4_has_min
        self.weight_4_min                = weight_4_min
        self.weight_4_has_max            = weight_4_has_max
        self.weight_4_max                = weight_4_max
        self.weight_4_function           = weight_4_function
        self.weight_4_function_value     = weight_4_function_value
        self.weight_5                    = weight_5
        self.weight_5_fixed              = weight_5_fixed
        self.weight_5_has_min            = weight_5_has_min
        self.weight_5_min                = weight_5_min
        self.weight_5_has_max            = weight_5_has_max
        self.weight_5_max                = weight_5_max
        self.weight_5_function           = weight_5_function
        self.weight_5_function_value     = weight_5_function_value
        self.twotheta_min                = twotheta_min
        self.twotheta_has_min            = twotheta_has_min
        self.twotheta_max                = twotheta_max
        self.twotheta_has_max            = twotheta_has_max

        self.CONTROL_AREA_WIDTH = widget.CONTROL_AREA_WIDTH

        container = gui.widgetBox(parent, "", orientation="vertical", width=self.CONTROL_AREA_WIDTH-35)

        file_box = gui.widgetBox(container, "", orientation="horizontal", width=self.CONTROL_AREA_WIDTH-35)

        self.le_filename = gui.lineEdit(file_box, self, value="filename", valueType=str, label="File", labelWidth=50,
                                        callback=widget.dump_filename)

        orangegui.button(file_box, self, "...", callback=self.open_folders)

        box = gui.widgetBox(container, "", orientation="horizontal", width=self.CONTROL_AREA_WIDTH - 35, spacing=0)

        orangegui.checkBox(box, self, "twotheta_has_min", "2\u03b8 min [deg]", labelWidth=350, callback=widget.dump_twotheta_has_min)
        gui.lineEdit(box, self, "twotheta_min", "", labelWidth=5, valueType=float, validator=QDoubleValidator(), callback=self.set_twotheta_min)

        box = gui.widgetBox(container, "", orientation="horizontal", width=self.CONTROL_AREA_WIDTH - 35, spacing=0)

        orangegui.checkBox(box, self, "twotheta_has_max", "2\u03b8 max [deg]", labelWidth=350, callback=widget.dump_twotheta_has_max)
        gui.lineEdit(box, self, "twotheta_max", "", labelWidth=5, valueType=float, validator=QDoubleValidator(), callback=self.set_twotheta_max)

        orangegui.separator(container)

        orangegui.comboBox(container, self, "is_multiple_wavelength", label="Incident Radiation", items=["Single Wavelenght", "X-ray Tube"], orientation="horizontal", callback=self.set_is_multiple_wavelength)

        self.secondary_box = gui.widgetBox(container, "", orientation="vertical", width=self.CONTROL_AREA_WIDTH - 35, spacing=0)

        orangegui.comboBox(self.secondary_box, self, "xray_tube_key", label="X-ray Tube Dataset", items=self.get_xray_tube_keys(),
                           sendSelectedValue=True, orientation="horizontal", callback=self.set_xray_tube_key)

        self.secondary_box_empty = gui.widgetBox(container, "", orientation="vertical", width=self.CONTROL_AREA_WIDTH - 35, spacing=0)

        widget.create_box_in_widget(self, container,  "wavelength", label="\u03BB  [nm]", disable_function=True, add_callback=True)

        self.secondary_box_2 = gui.widgetBox(container, "", orientation="vertical", width=self.CONTROL_AREA_WIDTH - 35, )
        self.secondary_box_2_empty = gui.widgetBox(container, "", orientation="vertical", width=self.CONTROL_AREA_WIDTH - 35)

        self.create_wavelength_boxes()

        self.set_is_multiple_wavelength()

        self.is_on_init = False

    def get_xray_tube_keys(self):
        items = []

        for key in wavelengths_data.keys():
            items.append(key)

        return items

    def create_wavelength_boxes(self):
        self.secondary_wavelengths_boxes = {}

        for key in wavelengths_data.keys():
            self.secondary_wavelengths_boxes[key] = gui.widgetBox(self.secondary_box_2, key + " Secondary Wavelengths", orientation="vertical", width=self.CONTROL_AREA_WIDTH - 40, height=230)

            secondary_index = 2
            for wavelenght in wavelengths_data[key]:
                if not wavelenght.is_principal:
                    var_wl = "wavelength_" + str(secondary_index)
                    var_we = "weight_" + str(secondary_index)
                    label_wl = "\u03BB" + " " + str(secondary_index) + "  [nm]"
                    label_we = "weight " + str(secondary_index)

                    self.widget.create_box_in_widget(self, self.secondary_wavelengths_boxes[key],  var_wl, label=label_wl, label_width=55, add_callback=True)
                    self.widget.create_box_in_widget(self, self.secondary_wavelengths_boxes[key],  var_we, label=label_we, label_width=55, add_callback=True)

                    secondary_index += 1

            self.secondary_wavelengths_boxes[key].setVisible(False)

    def set_xray_tube_key(self):
        if not self.is_on_init and self.xray_tube_key in wavelengths_data.keys():
            secondary_index = 2
            for wavelength in wavelengths_data[self.xray_tube_key]:
                if not wavelength.is_principal:
                    var_wl = "wavelength_" + str(secondary_index)
                    var_we = "weight_" + str(secondary_index)

                    self.widget.populate_fields_in_widget(self, var_wl, FitParameter(value=wavelength.wavelength, fixed=True), value_only=False)
                    self.widget.populate_fields_in_widget(self, var_we, FitParameter(value=wavelength.weight, fixed=True), value_only=False)

                    secondary_index += 1
                else:
                    self.widget.populate_fields_in_widget(self, "wavelength", FitParameter(value=wavelength.wavelength, fixed=True), value_only=False)

        for key in self.secondary_wavelengths_boxes.keys():
            if key==self.xray_tube_key:
                self.secondary_box_2.layout().removeWidget(self.secondary_wavelengths_boxes[key])
                self.secondary_box_2.layout().insertWidget(0, self.secondary_wavelengths_boxes[key])
                self.secondary_wavelengths_boxes[key].setVisible(True)
            else:
                self.secondary_wavelengths_boxes[key].setVisible(False)

        if not self.is_on_init:
            self.widget.dump_xray_tube_key()
            self.widget.dump_wavelength_2()
            self.widget.dump_wavelength_3()
            self.widget.dump_wavelength_4()
            self.widget.dump_wavelength_5()
            self.widget.dump_weight_2()
            self.widget.dump_weight_3()
            self.widget.dump_weight_4()
            self.widget.dump_weight_5()
        
    def set_is_multiple_wavelength(self):
        if self.is_multiple_wavelength == 0:
            self.secondary_box.setVisible(False)
            self.secondary_box_2.setVisible(False)
            self.secondary_box_empty.setVisible(True)
            self.secondary_box_2_empty.setVisible(True)
            self.widget.populate_fields_in_widget(self, "wavelength_2", FitParameter(value=0.0, fixed=True), value_only=False)
            self.widget.populate_fields_in_widget(self, "weight_2", FitParameter(value=0.0, fixed=True), value_only=False)
            self.widget.populate_fields_in_widget(self, "wavelength_3", FitParameter(value=0.0, fixed=True), value_only=False)
            self.widget.populate_fields_in_widget(self, "weight_3", FitParameter(value=0.0, fixed=True), value_only=False)
            self.widget.populate_fields_in_widget(self, "wavelength_4", FitParameter(value=0.0, fixed=True), value_only=False)
            self.widget.populate_fields_in_widget(self, "weight_4", FitParameter(value=0.0, fixed=True), value_only=False)
            self.widget.populate_fields_in_widget(self, "wavelength_5", FitParameter(value=0.0, fixed=True), value_only=False)
            self.widget.populate_fields_in_widget(self, "weight_5", FitParameter(value=0.0, fixed=True), value_only=False)
        else:
            self.secondary_box.setVisible(True)
            self.secondary_box_empty.setVisible(False)
            self.secondary_box_2.setVisible(True)
            self.secondary_box_2_empty.setVisible(False)

            self.set_xray_tube_key()
        
        if not self.is_on_init:
            self.widget.dump_is_multiple_wavelength()

    def set_twotheta_min(self):
        self.twotheta_has_min = 1
        if not self.is_on_init:
            self.widget.dump_twotheta_min()
            self.widget.dump_twotheta_has_min()

    def set_twotheta_max(self):
        self.twotheta_has_max = 1
        if not self.is_on_init:
            self.widget.dump_twotheta_max()
            self.widget.dump_twotheta_has_max()

    def callback_wavelength(self):
        if not self.is_on_init: self.widget.dump_wavelength()
        
    def callback_wavelength_2(self):
        if not self.is_on_init: self.widget.dump_wavelength_2()
        
    def callback_wavelength_3(self):
        if not self.is_on_init: self.widget.dump_wavelength_3()
        
    def callback_wavelength_4(self):
        if not self.is_on_init: self.widget.dump_wavelength_4()
        
    def callback_wavelength_5(self):
        if not self.is_on_init: self.widget.dump_wavelength_5()
        
    def callback_weight_2(self):
        if not self.is_on_init: self.widget.dump_weight_2()
        
    def callback_weight_3(self):
        if not self.is_on_init: self.widget.dump_weight_3()
        
    def callback_weight_4(self):
        if not self.is_on_init: self.widget.dump_weight_4()
        
    def callback_weight_5(self):
        if not self.is_on_init: self.widget.dump_weight_5()

    def open_folders(self):
        self.filename=gui.selectFileFromDialog(self,
                                               self.filename,
                                               start_directory=os.curdir)

        self.le_filename.setText(self.filename)

    def after_change_workspace_units(self):
        pass

    def set_index(self, index):
        self.index = index

    def load_diffraction_pattern(self):
        congruence.checkFile(self.filename)

        if self.twotheta_has_min == 1 or self.twotheta_has_max == 1:
            limits = DiffractionPatternLimits(twotheta_min=self.twotheta_min if self.twotheta_has_min==1 else -numpy.inf,
                                              twotheta_max=self.twotheta_max if self.twotheta_has_max==1 else numpy.inf)
        else:
            limits=None

        self.diffraction_pattern = DiffractionPatternFactory.create_diffraction_pattern_from_file(self.filename,
                                                                                                  self.widget.populate_parameter_in_widget(self,
                                                                                                                                           "wavelength",
                                                                                                                                           DiffractionPattern.get_parameters_prefix() + str(self.index+1) + "_"),
                                                                                                  limits)
        if self.is_multiple_wavelength == 1:
            secondary_wavelengths = []
            secondary_wavelengths_weights = []

            secondary_index = 2
            for wavelenght in wavelengths_data[self.xray_tube_key]:
                if not wavelenght.is_principal:
                    var_wl = "wavelength_" + str(secondary_index)
                    var_we = "weight_" + str(secondary_index)

                    secondary_wavelengths.append(self.widget.populate_parameter_in_widget(self,
                                                                                          var_wl,
                                                                                          DiffractionPattern.get_parameters_prefix() + str(self.index+1) + "_"))
                    secondary_wavelengths_weights.append(self.widget.populate_parameter_in_widget(self,
                                                                                                  var_we,
                                                                                                  DiffractionPattern.get_parameters_prefix() + str(self.index+1) + "_"))
                    secondary_index += 1

            self.diffraction_pattern.set_multiple_wavelengths(secondary_wavelengths, secondary_wavelengths_weights, recalculate=False)

if __name__ == "__main__":
    a = QApplication(sys.argv)
    ow = OWDiffractionPattern()
    ow.show()
    a.exec_()
    ow.saveSettings()
