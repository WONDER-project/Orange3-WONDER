import os, sys, numpy, copy

from PyQt5.QtWidgets import QMessageBox, QApplication


from Orange.widgets.settings import Setting
from Orange.widgets import gui as orangegui

from orangecontrib.wonder.util.widgets.ow_generic_widget import OWGenericWidget
from orangecontrib.wonder.util.gui.gui_utility import gui, ConfirmDialog

from orangecontrib.wonder.util import congruence
from orangecontrib.wonder.controller.fit.fit_global_parameters import FitGlobalParameters
from orangecontrib.wonder.controller.fit.instrument.background_parameters import ChebyshevBackground

class OWChebyshevBackground(OWGenericWidget):

    name = "Chebyshev Background"
    description = "Define Chebyshev background"
    icon = "icons/chebyshev_background.png"
    priority = 10

    want_main_area =  False

    use_single_parameter_set = Setting(0)

    c0                = Setting([0.0])
    c1                = Setting([0.0])
    c2                = Setting([0.0])
    c3                = Setting([0.0])
    c4                = Setting([0.0])
    c5                = Setting([0.0])
    c6                = Setting([0.0])
    c7                = Setting([0.0])
    c8                = Setting([0.0])
    c9                = Setting([0.0])
    c0_fixed          = Setting([0])
    c1_fixed          = Setting([0])
    c2_fixed          = Setting([0])
    c3_fixed          = Setting([0])
    c4_fixed          = Setting([0])
    c5_fixed          = Setting([0])
    c6_fixed          = Setting([1])
    c7_fixed          = Setting([1])
    c8_fixed          = Setting([1])
    c9_fixed          = Setting([1])
    c0_has_min        = Setting([0])
    c1_has_min        = Setting([0])
    c2_has_min        = Setting([0])
    c3_has_min        = Setting([0])
    c4_has_min        = Setting([0])
    c5_has_min        = Setting([0])
    c6_has_min        = Setting([0])
    c7_has_min        = Setting([0])
    c8_has_min        = Setting([0])
    c9_has_min        = Setting([0])
    c0_min            = Setting([0.0])
    c1_min            = Setting([0.0])
    c2_min            = Setting([0.0])
    c3_min            = Setting([0.0])
    c4_min            = Setting([0.0])
    c5_min            = Setting([0.0])
    c6_min            = Setting([0.0])
    c7_min            = Setting([0.0])
    c8_min            = Setting([0.0])
    c9_min            = Setting([0.0])
    c0_has_max        = Setting([0])
    c1_has_max        = Setting([0])
    c2_has_max        = Setting([0])
    c3_has_max        = Setting([0])
    c4_has_max        = Setting([0])
    c5_has_max        = Setting([0])
    c6_has_max        = Setting([0])
    c7_has_max        = Setting([0])
    c8_has_max        = Setting([0])
    c9_has_max        = Setting([0])
    c0_max            = Setting([0.0])
    c1_max            = Setting([0.0])
    c2_max            = Setting([0.0])
    c3_max            = Setting([0.0])
    c4_max            = Setting([0.0])
    c5_max            = Setting([0.0])
    c6_max            = Setting([0.0])
    c7_max            = Setting([0.0])
    c8_max            = Setting([0.0])
    c9_max            = Setting([0.0])
    c0_function       = Setting([0])
    c1_function       = Setting([0])
    c2_function       = Setting([0])
    c3_function       = Setting([0])
    c4_function       = Setting([0])
    c5_function       = Setting([0])
    c6_function       = Setting([0])
    c7_function       = Setting([0])
    c8_function       = Setting([0])
    c9_function       = Setting([0])
    c0_function_value = Setting([""])
    c1_function_value = Setting([""])
    c2_function_value = Setting([""])
    c3_function_value = Setting([""])
    c4_function_value = Setting([""])
    c5_function_value = Setting([""])
    c6_function_value = Setting([""])
    c7_function_value = Setting([""])
    c8_function_value = Setting([""])
    c9_function_value = Setting([""])

    inputs = [("Fit Global Parameters", FitGlobalParameters, 'set_data')]
    outputs = [("Fit Global Parameters", FitGlobalParameters)]

    # TO PRESERVE RETRO-COMPATIBILITY
    def fix_input(self, emergency=False):
        if not isinstance(self.c0               , list): self.c0                = [self.c0               ]
        if not isinstance(self.c1               , list): self.c1                = [self.c1               ]
        if not isinstance(self.c2               , list): self.c2                = [self.c2               ]
        if not isinstance(self.c3               , list): self.c3                = [self.c3               ]
        if not isinstance(self.c4               , list): self.c4                = [self.c4               ]
        if not isinstance(self.c5               , list): self.c5                = [self.c5               ]
        if not isinstance(self.c6               , list): self.c6                = [self.c6               ]
        if not isinstance(self.c7               , list): self.c7                = [self.c7               ]
        if not isinstance(self.c8               , list): self.c8                = [self.c8               ]
        if not isinstance(self.c9               , list): self.c9                = [self.c9               ]
        if not isinstance(self.c0_fixed         , list): self.c0_fixed          = [self.c0_fixed         ]
        if not isinstance(self.c1_fixed         , list): self.c1_fixed          = [self.c1_fixed         ]
        if not isinstance(self.c2_fixed         , list): self.c2_fixed          = [self.c2_fixed         ]
        if not isinstance(self.c3_fixed         , list): self.c3_fixed          = [self.c3_fixed         ]
        if not isinstance(self.c4_fixed         , list): self.c4_fixed          = [self.c4_fixed         ]
        if not isinstance(self.c5_fixed         , list): self.c5_fixed          = [self.c5_fixed         ]
        if not isinstance(self.c6_fixed         , list): self.c6_fixed          = [self.c6_fixed         ]
        if not isinstance(self.c7_fixed         , list): self.c7_fixed          = [self.c7_fixed         ]
        if not isinstance(self.c8_fixed         , list): self.c8_fixed          = [self.c8_fixed         ]
        if not isinstance(self.c9_fixed         , list): self.c9_fixed          = [self.c9_fixed         ]
        if not isinstance(self.c0_has_min       , list): self.c0_has_min        = [self.c0_has_min       ]
        if not isinstance(self.c1_has_min       , list): self.c1_has_min        = [self.c1_has_min       ]
        if not isinstance(self.c2_has_min       , list): self.c2_has_min        = [self.c2_has_min       ]
        if not isinstance(self.c3_has_min       , list): self.c3_has_min        = [self.c3_has_min       ]
        if not isinstance(self.c4_has_min       , list): self.c4_has_min        = [self.c4_has_min       ]
        if not isinstance(self.c5_has_min       , list): self.c5_has_min        = [self.c5_has_min       ]
        if not isinstance(self.c6_has_min       , list): self.c6_has_min        = [self.c6_has_min       ]
        if not isinstance(self.c7_has_min       , list): self.c7_has_min        = [self.c7_has_min       ]
        if not isinstance(self.c8_has_min       , list): self.c8_has_min        = [self.c8_has_min       ]
        if not isinstance(self.c9_has_min       , list): self.c9_has_min        = [self.c9_has_min       ]
        if not isinstance(self.c0_min           , list): self.c0_min            = [self.c0_min           ]
        if not isinstance(self.c1_min           , list): self.c1_min            = [self.c1_min           ]
        if not isinstance(self.c2_min           , list): self.c2_min            = [self.c2_min           ]
        if not isinstance(self.c3_min           , list): self.c3_min            = [self.c3_min           ]
        if not isinstance(self.c4_min           , list): self.c4_min            = [self.c4_min           ]
        if not isinstance(self.c5_min           , list): self.c5_min            = [self.c5_min           ]
        if not isinstance(self.c6_min           , list): self.c6_min            = [self.c6_min           ]
        if not isinstance(self.c7_min           , list): self.c7_min            = [self.c7_min           ]
        if not isinstance(self.c8_min           , list): self.c8_min            = [self.c8_min           ]
        if not isinstance(self.c9_min           , list): self.c9_min            = [self.c9_min           ]
        if not isinstance(self.c0_has_max       , list): self.c0_has_max        = [self.c0_has_max       ]
        if not isinstance(self.c1_has_max       , list): self.c1_has_max        = [self.c1_has_max       ]
        if not isinstance(self.c2_has_max       , list): self.c2_has_max        = [self.c2_has_max       ]
        if not isinstance(self.c3_has_max       , list): self.c3_has_max        = [self.c3_has_max       ]
        if not isinstance(self.c4_has_max       , list): self.c4_has_max        = [self.c4_has_max       ]
        if not isinstance(self.c5_has_max       , list): self.c5_has_max        = [self.c5_has_max       ]
        if not isinstance(self.c6_has_max       , list): self.c6_has_max        = [self.c6_has_max       ]
        if not isinstance(self.c7_has_max       , list): self.c7_has_max        = [self.c7_has_max       ]
        if not isinstance(self.c8_has_max       , list): self.c8_has_max        = [self.c8_has_max       ]
        if not isinstance(self.c9_has_max       , list): self.c9_has_max        = [self.c9_has_max       ]
        if not isinstance(self.c0_max           , list): self.c0_max            = [self.c0_max           ]
        if not isinstance(self.c1_max           , list): self.c1_max            = [self.c1_max           ]
        if not isinstance(self.c2_max           , list): self.c2_max            = [self.c2_max           ]
        if not isinstance(self.c3_max           , list): self.c3_max            = [self.c3_max           ]
        if not isinstance(self.c4_max           , list): self.c4_max            = [self.c4_max           ]
        if not isinstance(self.c5_max           , list): self.c5_max            = [self.c5_max           ]
        if not isinstance(self.c6_max           , list): self.c6_max            = [self.c6_max           ]
        if not isinstance(self.c7_max           , list): self.c7_max            = [self.c7_max           ]
        if not isinstance(self.c8_max           , list): self.c8_max            = [self.c8_max           ]
        if not isinstance(self.c9_max           , list): self.c9_max            = [self.c9_max           ]
        if not isinstance(self.c0_function      , list): self.c0_function       = [self.c0_function      ]
        if not isinstance(self.c1_function      , list): self.c1_function       = [self.c1_function      ]
        if not isinstance(self.c2_function      , list): self.c2_function       = [self.c2_function      ]
        if not isinstance(self.c3_function      , list): self.c3_function       = [self.c3_function      ]
        if not isinstance(self.c4_function      , list): self.c4_function       = [self.c4_function      ]
        if not isinstance(self.c5_function      , list): self.c5_function       = [self.c5_function      ]
        if not isinstance(self.c6_function      , list): self.c6_function       = [self.c6_function      ]
        if not isinstance(self.c7_function      , list): self.c7_function       = [self.c7_function      ]
        if not isinstance(self.c8_function      , list): self.c8_function       = [self.c8_function      ]
        if not isinstance(self.c9_function      , list): self.c9_function       = [self.c9_function      ]
        if not isinstance(self.c0_function_value, list): self.c0_function_value = [self.c0_function_value]
        if not isinstance(self.c1_function_value, list): self.c1_function_value = [self.c1_function_value]
        if not isinstance(self.c2_function_value, list): self.c2_function_value = [self.c2_function_value]
        if not isinstance(self.c3_function_value, list): self.c3_function_value = [self.c3_function_value]
        if not isinstance(self.c4_function_value, list): self.c4_function_value = [self.c4_function_value]
        if not isinstance(self.c5_function_value, list): self.c5_function_value = [self.c5_function_value]
        if not isinstance(self.c6_function_value, list): self.c6_function_value = [self.c6_function_value]
        if not isinstance(self.c7_function_value, list): self.c7_function_value = [self.c7_function_value]
        if not isinstance(self.c8_function_value, list): self.c8_function_value = [self.c8_function_value]
        if not isinstance(self.c9_function_value, list): self.c9_function_value = [self.c9_function_value]

        if emergency:
            self.c0                = [0.0]
            self.c1                = [0.0]
            self.c2                = [0.0]
            self.c3                = [0.0]
            self.c4                = [0.0]
            self.c5                = [0.0]
            self.c6                = [0.0]
            self.c7                = [0.0]
            self.c8                = [0.0]
            self.c9                = [0.0]
            self.c0_fixed          = [0]
            self.c1_fixed          = [0]
            self.c2_fixed          = [0]
            self.c3_fixed          = [0]
            self.c4_fixed          = [0]
            self.c5_fixed          = [0]
            self.c6_fixed          = [1]
            self.c7_fixed          = [1]
            self.c8_fixed          = [1]
            self.c9_fixed          = [1]
            self.c0_has_min        = [0]
            self.c1_has_min        = [0]
            self.c2_has_min        = [0]
            self.c3_has_min        = [0]
            self.c4_has_min        = [0]
            self.c5_has_min        = [0]
            self.c6_has_min        = [0]
            self.c7_has_min        = [0]
            self.c8_has_min        = [0]
            self.c9_has_min        = [0]
            self.c0_min            = [0.0]
            self.c1_min            = [0.0]
            self.c2_min            = [0.0]
            self.c3_min            = [0.0]
            self.c4_min            = [0.0]
            self.c5_min            = [0.0]
            self.c6_min            = [0.0]
            self.c7_min            = [0.0]
            self.c8_min            = [0.0]
            self.c9_min            = [0.0]
            self.c0_has_max        = [0]
            self.c1_has_max        = [0]
            self.c2_has_max        = [0]
            self.c3_has_max        = [0]
            self.c4_has_max        = [0]
            self.c5_has_max        = [0]
            self.c6_has_max        = [0]
            self.c7_has_max        = [0]
            self.c8_has_max        = [0]
            self.c9_has_max        = [0]
            self.c0_max            = [0.0]
            self.c1_max            = [0.0]
            self.c2_max            = [0.0]
            self.c3_max            = [0.0]
            self.c4_max            = [0.0]
            self.c5_max            = [0.0]
            self.c6_max            = [0.0]
            self.c7_max            = [0.0]
            self.c8_max            = [0.0]
            self.c9_max            = [0.0]
            self.c0_function       = [0]
            self.c1_function       = [0]
            self.c2_function       = [0]
            self.c3_function       = [0]
            self.c4_function       = [0]
            self.c5_function       = [0]
            self.c6_function       = [0]
            self.c7_function       = [0]
            self.c8_function       = [0]
            self.c9_function       = [0]
            self.c0_function_value = [""]
            self.c1_function_value = [""]
            self.c2_function_value = [""]
            self.c3_function_value = [""]
            self.c4_function_value = [""]
            self.c5_function_value = [""]
            self.c6_function_value = [""]
            self.c7_function_value = [""]
            self.c8_function_value = [""]
            self.c9_function_value = [""]
        else:
            if len(self.c0               ) == 0: self.c0                = [0.0]
            if len(self.c1               ) == 0: self.c1                = [0.0]
            if len(self.c2               ) == 0: self.c2                = [0.0]
            if len(self.c3               ) == 0: self.c3                = [0.0]
            if len(self.c4               ) == 0: self.c4                = [0.0]
            if len(self.c5               ) == 0: self.c5                = [0.0]
            if len(self.c6               ) == 0: self.c6                = [0.0]
            if len(self.c7               ) == 0: self.c7                = [0.0]
            if len(self.c8               ) == 0: self.c8                = [0.0]
            if len(self.c9               ) == 0: self.c9                = [0.0]
            if len(self.c0_fixed         ) == 0: self.c0_fixed          = [0]
            if len(self.c1_fixed         ) == 0: self.c1_fixed          = [0]
            if len(self.c2_fixed         ) == 0: self.c2_fixed          = [0]
            if len(self.c3_fixed         ) == 0: self.c3_fixed          = [0]
            if len(self.c4_fixed         ) == 0: self.c4_fixed          = [0]
            if len(self.c5_fixed         ) == 0: self.c5_fixed          = [0]
            if len(self.c6_fixed         ) == 0: self.c6_fixed          = [1]
            if len(self.c7_fixed         ) == 0: self.c7_fixed          = [1]
            if len(self.c8_fixed         ) == 0: self.c8_fixed          = [1]
            if len(self.c9_fixed         ) == 0: self.c9_fixed          = [1]
            if len(self.c0_has_min       ) == 0: self.c0_has_min        = [0]
            if len(self.c1_has_min       ) == 0: self.c1_has_min        = [0]
            if len(self.c2_has_min       ) == 0: self.c2_has_min        = [0]
            if len(self.c3_has_min       ) == 0: self.c3_has_min        = [0]
            if len(self.c4_has_min       ) == 0: self.c4_has_min        = [0]
            if len(self.c5_has_min       ) == 0: self.c5_has_min        = [0]
            if len(self.c6_has_min       ) == 0: self.c6_has_min        = [0]
            if len(self.c7_has_min       ) == 0: self.c7_has_min        = [0]
            if len(self.c8_has_min       ) == 0: self.c8_has_min        = [0]
            if len(self.c9_has_min       ) == 0: self.c9_has_min        = [0]
            if len(self.c0_min           ) == 0: self.c0_min            = [0.0]
            if len(self.c1_min           ) == 0: self.c1_min            = [0.0]
            if len(self.c2_min           ) == 0: self.c2_min            = [0.0]
            if len(self.c3_min           ) == 0: self.c3_min            = [0.0]
            if len(self.c4_min           ) == 0: self.c4_min            = [0.0]
            if len(self.c5_min           ) == 0: self.c5_min            = [0.0]
            if len(self.c6_min           ) == 0: self.c6_min            = [0.0]
            if len(self.c7_min           ) == 0: self.c7_min            = [0.0]
            if len(self.c8_min           ) == 0: self.c8_min            = [0.0]
            if len(self.c9_min           ) == 0: self.c9_min            = [0.0]
            if len(self.c0_has_max       ) == 0: self.c0_has_max        = [0]
            if len(self.c1_has_max       ) == 0: self.c1_has_max        = [0]
            if len(self.c2_has_max       ) == 0: self.c2_has_max        = [0]
            if len(self.c3_has_max       ) == 0: self.c3_has_max        = [0]
            if len(self.c4_has_max       ) == 0: self.c4_has_max        = [0]
            if len(self.c5_has_max       ) == 0: self.c5_has_max        = [0]
            if len(self.c6_has_max       ) == 0: self.c6_has_max        = [0]
            if len(self.c7_has_max       ) == 0: self.c7_has_max        = [0]
            if len(self.c8_has_max       ) == 0: self.c8_has_max        = [0]
            if len(self.c9_has_max       ) == 0: self.c9_has_max        = [0]
            if len(self.c0_max           ) == 0: self.c0_max            = [0.0]
            if len(self.c1_max           ) == 0: self.c1_max            = [0.0]
            if len(self.c2_max           ) == 0: self.c2_max            = [0.0]
            if len(self.c3_max           ) == 0: self.c3_max            = [0.0]
            if len(self.c4_max           ) == 0: self.c4_max            = [0.0]
            if len(self.c5_max           ) == 0: self.c5_max            = [0.0]
            if len(self.c6_max           ) == 0: self.c6_max            = [0.0]
            if len(self.c7_max           ) == 0: self.c7_max            = [0.0]
            if len(self.c8_max           ) == 0: self.c8_max            = [0.0]
            if len(self.c9_max           ) == 0: self.c9_max            = [0.0]
            if len(self.c0_function      ) == 0: self.c0_function       = [0]
            if len(self.c1_function      ) == 0: self.c1_function       = [0]
            if len(self.c2_function      ) == 0: self.c2_function       = [0]
            if len(self.c3_function      ) == 0: self.c3_function       = [0]
            if len(self.c4_function      ) == 0: self.c4_function       = [0]
            if len(self.c5_function      ) == 0: self.c5_function       = [0]
            if len(self.c6_function      ) == 0: self.c6_function       = [0]
            if len(self.c7_function      ) == 0: self.c7_function       = [0]
            if len(self.c8_function      ) == 0: self.c8_function       = [0]
            if len(self.c9_function      ) == 0: self.c9_function       = [0]
            if len(self.c0_function_value) == 0: self.c0_function_value = [""]
            if len(self.c1_function_value) == 0: self.c1_function_value = [""]
            if len(self.c2_function_value) == 0: self.c2_function_value = [""]
            if len(self.c3_function_value) == 0: self.c3_function_value = [""]
            if len(self.c4_function_value) == 0: self.c4_function_value = [""]
            if len(self.c5_function_value) == 0: self.c5_function_value = [""]
            if len(self.c6_function_value) == 0: self.c6_function_value = [""]
            if len(self.c7_function_value) == 0: self.c7_function_value = [""]
            if len(self.c8_function_value) == 0: self.c8_function_value = [""]
            if len(self.c9_function_value) == 0: self.c9_function_value = [""]



    def __init__(self):
        super().__init__(show_automatic_box=True)

        if self.IS_FIX: self.fix_input()

        main_box = gui.widgetBox(self.controlArea,
                                 "Chebyshev Parameters", orientation="vertical",
                                 width=self.CONTROL_AREA_WIDTH - 10, height=600)


        button_box = gui.widgetBox(main_box,
                                   "", orientation="horizontal",
                                   width=self.CONTROL_AREA_WIDTH-25)

        gui.button(button_box,  self, "Send Background", height=50, callback=self.send_background)

        orangegui.comboBox(main_box, self, "use_single_parameter_set", label="Use single set of Parameters", labelWidth=350, orientation="horizontal",
                           items=["No", "Yes"], callback=self.set_use_single_parameter_set, sendSelectedValue=False)

        orangegui.separator(main_box)

        self.chebyshev_tabs = gui.tabWidget(main_box)

        self.set_use_single_parameter_set(on_init=True)


    def set_use_single_parameter_set(self, on_init=False):
        if on_init:
            confirmed = True
        else:
            confirmed = True

        if confirmed:
            self.chebyshev_tabs.clear()
            self.chebyshev_box_array = []

            dimension = len(self.c0) if self.fit_global_parameters is None else len(self.fit_global_parameters.fit_initialization.diffraction_patterns)

            for index in range(1 if self.use_single_parameter_set == 1 else dimension):
                chebyshev_tab = gui.createTabPage(self.chebyshev_tabs, "Diff. Patt. " + str(index + 1))

                if index < len(self.c0): #keep the existing
                    chebyshev_box = ChebyshevBackgroundBox(widget=self,
                                                                parent=chebyshev_tab,
                                                                index = index,
                                                                c0                = self.c0[index],
                                                                c1                = self.c1[index],
                                                                c2                = self.c2[index],
                                                                c3                = self.c3[index],
                                                                c4                = self.c4[index],
                                                                c5                = self.c5[index],
                                                                c6                = self.c6[index],
                                                                c7                = self.c7[index],
                                                                c8                = self.c8[index],
                                                                c9                = self.c9[index],
                                                                c0_fixed          = self.c0_fixed[index],
                                                                c1_fixed          = self.c1_fixed[index],
                                                                c2_fixed          = self.c2_fixed[index],
                                                                c3_fixed          = self.c3_fixed[index],
                                                                c4_fixed          = self.c4_fixed[index],
                                                                c5_fixed          = self.c5_fixed[index],
                                                                c6_fixed          = self.c6_fixed[index],
                                                                c7_fixed          = self.c7_fixed[index],
                                                                c8_fixed          = self.c8_fixed[index],
                                                                c9_fixed          = self.c9_fixed[index],
                                                                c0_has_min        = self.c0_has_min[index],
                                                                c1_has_min        = self.c1_has_min[index],
                                                                c2_has_min        = self.c2_has_min[index],
                                                                c3_has_min        = self.c3_has_min[index],
                                                                c4_has_min        = self.c4_has_min[index],
                                                                c5_has_min        = self.c5_has_min[index],
                                                                c6_has_min        = self.c6_has_min[index],
                                                                c7_has_min        = self.c7_has_min[index],
                                                                c8_has_min        = self.c8_has_min[index],
                                                                c9_has_min        = self.c9_has_min[index],
                                                                c0_min            = self.c0_min[index],
                                                                c1_min            = self.c1_min[index],
                                                                c2_min            = self.c2_min[index],
                                                                c3_min            = self.c3_min[index],
                                                                c4_min            = self.c4_min[index],
                                                                c5_min            = self.c5_min[index],
                                                                c6_min            = self.c6_min[index],
                                                                c7_min            = self.c7_min[index],
                                                                c8_min            = self.c8_min[index],
                                                                c9_min            = self.c9_min[index],
                                                                c0_has_max        = self.c0_has_max[index],
                                                                c1_has_max        = self.c1_has_max[index],
                                                                c2_has_max        = self.c2_has_max[index],
                                                                c3_has_max        = self.c3_has_max[index],
                                                                c4_has_max        = self.c4_has_max[index],
                                                                c5_has_max        = self.c5_has_max[index],
                                                                c6_has_max        = self.c6_has_max[index],
                                                                c7_has_max        = self.c7_has_max[index],
                                                                c8_has_max        = self.c8_has_max[index],
                                                                c9_has_max        = self.c9_has_max[index],
                                                                c0_max            = self.c0_max[index],
                                                                c1_max            = self.c1_max[index],
                                                                c2_max            = self.c2_max[index],
                                                                c3_max            = self.c3_max[index],
                                                                c4_max            = self.c4_max[index],
                                                                c5_max            = self.c5_max[index],
                                                                c6_max            = self.c6_max[index],
                                                                c7_max            = self.c7_max[index],
                                                                c8_max            = self.c8_max[index],
                                                                c9_max            = self.c9_max[index],
                                                                c0_function       = self.c0_function[index],
                                                                c1_function       = self.c1_function[index],
                                                                c2_function       = self.c2_function[index],
                                                                c3_function       = self.c3_function[index],
                                                                c4_function       = self.c4_function[index],
                                                                c5_function       = self.c5_function[index],
                                                                c6_function       = self.c6_function[index],
                                                                c7_function       = self.c7_function[index],
                                                                c8_function       = self.c8_function[index],
                                                                c9_function       = self.c9_function[index],
                                                                c0_function_value = self.c0_function_value[index],
                                                                c1_function_value = self.c1_function_value[index],
                                                                c2_function_value = self.c2_function_value[index],
                                                                c3_function_value = self.c3_function_value[index],
                                                                c4_function_value = self.c4_function_value[index],
                                                                c5_function_value = self.c5_function_value[index],
                                                                c6_function_value = self.c6_function_value[index],
                                                                c7_function_value = self.c7_function_value[index],
                                                                c8_function_value = self.c8_function_value[index],
                                                                c9_function_value = self.c9_function_value[index])
                else:
                    chebyshev_box = ChebyshevBackgroundBox(widget=self, parent=chebyshev_tab, index = index)

                self.chebyshev_box_array.append(chebyshev_box)

            if not on_init: self.dumpSettings()
            
    def send_background(self):
        try:
            if not self.fit_global_parameters is None:
                self.dumpSettings()

                background_parameters = []
                for index in range(len(self.c0)):
                    background_parameters.append(self.chebyshev_box_array[index].send_background())

                self.fit_global_parameters.set_background_parameters(background_parameters)
                self.fit_global_parameters.regenerate_parameters()

                self.send("Fit Global Parameters", self.fit_global_parameters)

        except Exception as e:
            QMessageBox.critical(self, "Error",
                                 str(e),
                                 QMessageBox.Ok)

            if self.IS_DEVELOP: raise e

    def set_data(self, data):
        if not data is None:
            try:
                self.fit_global_parameters = data.duplicate()

                diffraction_patterns = self.fit_global_parameters.fit_initialization.diffraction_patterns

                if diffraction_patterns is None: raise ValueError("No Diffraction Pattern in input data!")

                background_parameters = self.fit_global_parameters.get_background_parameters(ChebyshevBackground.__name__)

                if len(diffraction_patterns) != len(self.chebyshev_box_array):
                    if ConfirmDialog.confirmed(message="Number of Diffraction Patterns changed:\ndo you want to use the existing structures where possible?\n\nIf yes, check for possible incongruences", title="Warning"):
                        self.set_use_single_parameter_set()
                elif not background_parameters is None:
                        for index in range(1 if self.use_single_parameter_set == 0 else len(background_parameters)):
                            self.chebyshev_box_array[index].set_data(background_parameters[index])

                self.dumpSettings()

                if self.is_automatic_run:
                    self.send_background()

            except Exception as e:
                QMessageBox.critical(self, "Error",
                                     str(e),
                                     QMessageBox.Ok)

                if self.IS_DEVELOP: raise e

    def dumpSettings(self):
        self.dump_c0()
        self.dump_c1()
        self.dump_c2()
        self.dump_c3()
        self.dump_c4()
        self.dump_c5()
        self.dump_c6()
        self.dump_c7()
        self.dump_c8()
        self.dump_c9()

    def dump_c0(self):
        bkp_c0                = copy.deepcopy(self.c0               )
        bkp_c0_fixed          = copy.deepcopy(self.c0_fixed         )
        bkp_c0_has_min        = copy.deepcopy(self.c0_has_min       )
        bkp_c0_min            = copy.deepcopy(self.c0_min           )
        bkp_c0_has_max        = copy.deepcopy(self.c0_has_max       )
        bkp_c0_max            = copy.deepcopy(self.c0_max           )
        bkp_c0_function       = copy.deepcopy(self.c0_function      )
        bkp_c0_function_value = copy.deepcopy(self.c0_function_value)
        
        try:
            self.c0                = []
            self.c0_fixed          = []
            self.c0_has_min        = []
            self.c0_min            = []
            self.c0_has_max        = []
            self.c0_max            = []
            self.c0_function       = []
            self.c0_function_value = []    
        
            for index in range(len(self.chebyshev_box_array)):
                self.c0.append(self.chebyshev_box_array[index].c0)
                self.c0_fixed.append(self.chebyshev_box_array[index].c0_fixed)
                self.c0_has_min.append(self.chebyshev_box_array[index].c0_has_min)
                self.c0_min.append(self.chebyshev_box_array[index].c0_min)
                self.c0_has_max.append(self.chebyshev_box_array[index].c0_has_max)
                self.c0_max.append(self.chebyshev_box_array[index].c0_max)
                self.c0_function.append(self.chebyshev_box_array[index].c0_function)
                self.c0_function_value.append(self.chebyshev_box_array[index].c0_function_value)
        except:
            self.c0                = copy.deepcopy(bkp_c0               )
            self.c0_fixed          = copy.deepcopy(bkp_c0_fixed         )
            self.c0_has_min        = copy.deepcopy(bkp_c0_has_min       )
            self.c0_min            = copy.deepcopy(bkp_c0_min           )
            self.c0_has_max        = copy.deepcopy(bkp_c0_has_max       )
            self.c0_max            = copy.deepcopy(bkp_c0_max           )
            self.c0_function       = copy.deepcopy(bkp_c0_function      )
            self.c0_function_value = copy.deepcopy(bkp_c0_function_value)

    def dump_c1(self):
        bkp_c1                = copy.deepcopy(self.c1               )
        bkp_c1_fixed          = copy.deepcopy(self.c1_fixed         )
        bkp_c1_has_min        = copy.deepcopy(self.c1_has_min       )
        bkp_c1_min            = copy.deepcopy(self.c1_min           )
        bkp_c1_has_max        = copy.deepcopy(self.c1_has_max       )
        bkp_c1_max            = copy.deepcopy(self.c1_max           )
        bkp_c1_function       = copy.deepcopy(self.c1_function      )
        bkp_c1_function_value = copy.deepcopy(self.c1_function_value)
        
        try:
            self.c1                = []
            self.c1_fixed          = []
            self.c1_has_min        = []
            self.c1_min            = []
            self.c1_has_max        = []
            self.c1_max            = []
            self.c1_function       = []
            self.c1_function_value = []    
        
            for index in range(len(self.chebyshev_box_array)):
                self.c1.append(self.chebyshev_box_array[index].c1)
                self.c1_fixed.append(self.chebyshev_box_array[index].c1_fixed)
                self.c1_has_min.append(self.chebyshev_box_array[index].c1_has_min)
                self.c1_min.append(self.chebyshev_box_array[index].c1_min)
                self.c1_has_max.append(self.chebyshev_box_array[index].c1_has_max)
                self.c1_max.append(self.chebyshev_box_array[index].c1_max)
                self.c1_function.append(self.chebyshev_box_array[index].c1_function)
                self.c1_function_value.append(self.chebyshev_box_array[index].c1_function_value)
        except:
            self.c1                = copy.deepcopy(bkp_c1               )
            self.c1_fixed          = copy.deepcopy(bkp_c1_fixed         )
            self.c1_has_min        = copy.deepcopy(bkp_c1_has_min       )
            self.c1_min            = copy.deepcopy(bkp_c1_min           )
            self.c1_has_max        = copy.deepcopy(bkp_c1_has_max       )
            self.c1_max            = copy.deepcopy(bkp_c1_max           )
            self.c1_function       = copy.deepcopy(bkp_c1_function      )
            self.c1_function_value = copy.deepcopy(bkp_c1_function_value)

    def dump_c2(self):
        bkp_c2                = copy.deepcopy(self.c2               )
        bkp_c2_fixed          = copy.deepcopy(self.c2_fixed         )
        bkp_c2_has_min        = copy.deepcopy(self.c2_has_min       )
        bkp_c2_min            = copy.deepcopy(self.c2_min           )
        bkp_c2_has_max        = copy.deepcopy(self.c2_has_max       )
        bkp_c2_max            = copy.deepcopy(self.c2_max           )
        bkp_c2_function       = copy.deepcopy(self.c2_function      )
        bkp_c2_function_value = copy.deepcopy(self.c2_function_value)
        
        try:
            self.c2                = []
            self.c2_fixed          = []
            self.c2_has_min        = []
            self.c2_min            = []
            self.c2_has_max        = []
            self.c2_max            = []
            self.c2_function       = []
            self.c2_function_value = []    
        
            for index in range(len(self.chebyshev_box_array)):
                self.c2.append(self.chebyshev_box_array[index].c2)
                self.c2_fixed.append(self.chebyshev_box_array[index].c2_fixed)
                self.c2_has_min.append(self.chebyshev_box_array[index].c2_has_min)
                self.c2_min.append(self.chebyshev_box_array[index].c2_min)
                self.c2_has_max.append(self.chebyshev_box_array[index].c2_has_max)
                self.c2_max.append(self.chebyshev_box_array[index].c2_max)
                self.c2_function.append(self.chebyshev_box_array[index].c2_function)
                self.c2_function_value.append(self.chebyshev_box_array[index].c2_function_value)
        except:
            self.c2                = copy.deepcopy(bkp_c2               )
            self.c2_fixed          = copy.deepcopy(bkp_c2_fixed         )
            self.c2_has_min        = copy.deepcopy(bkp_c2_has_min       )
            self.c2_min            = copy.deepcopy(bkp_c2_min           )
            self.c2_has_max        = copy.deepcopy(bkp_c2_has_max       )
            self.c2_max            = copy.deepcopy(bkp_c2_max           )
            self.c2_function       = copy.deepcopy(bkp_c2_function      )
            self.c2_function_value = copy.deepcopy(bkp_c2_function_value)

    def dump_c3(self):
        bkp_c3                = copy.deepcopy(self.c3               )
        bkp_c3_fixed          = copy.deepcopy(self.c3_fixed         )
        bkp_c3_has_min        = copy.deepcopy(self.c3_has_min       )
        bkp_c3_min            = copy.deepcopy(self.c3_min           )
        bkp_c3_has_max        = copy.deepcopy(self.c3_has_max       )
        bkp_c3_max            = copy.deepcopy(self.c3_max           )
        bkp_c3_function       = copy.deepcopy(self.c3_function      )
        bkp_c3_function_value = copy.deepcopy(self.c3_function_value)
        
        try:
            self.c3                = []
            self.c3_fixed          = []
            self.c3_has_min        = []
            self.c3_min            = []
            self.c3_has_max        = []
            self.c3_max            = []
            self.c3_function       = []
            self.c3_function_value = []    
        
            for index in range(len(self.chebyshev_box_array)):
                self.c3.append(self.chebyshev_box_array[index].c3)
                self.c3_fixed.append(self.chebyshev_box_array[index].c3_fixed)
                self.c3_has_min.append(self.chebyshev_box_array[index].c3_has_min)
                self.c3_min.append(self.chebyshev_box_array[index].c3_min)
                self.c3_has_max.append(self.chebyshev_box_array[index].c3_has_max)
                self.c3_max.append(self.chebyshev_box_array[index].c3_max)
                self.c3_function.append(self.chebyshev_box_array[index].c3_function)
                self.c3_function_value.append(self.chebyshev_box_array[index].c3_function_value)
        except:
            self.c3                = copy.deepcopy(bkp_c3               )
            self.c3_fixed          = copy.deepcopy(bkp_c3_fixed         )
            self.c3_has_min        = copy.deepcopy(bkp_c3_has_min       )
            self.c3_min            = copy.deepcopy(bkp_c3_min           )
            self.c3_has_max        = copy.deepcopy(bkp_c3_has_max       )
            self.c3_max            = copy.deepcopy(bkp_c3_max           )
            self.c3_function       = copy.deepcopy(bkp_c3_function      )
            self.c3_function_value = copy.deepcopy(bkp_c3_function_value)

    def dump_c4(self):
        bkp_c4                = copy.deepcopy(self.c4               )
        bkp_c4_fixed          = copy.deepcopy(self.c4_fixed         )
        bkp_c4_has_min        = copy.deepcopy(self.c4_has_min       )
        bkp_c4_min            = copy.deepcopy(self.c4_min           )
        bkp_c4_has_max        = copy.deepcopy(self.c4_has_max       )
        bkp_c4_max            = copy.deepcopy(self.c4_max           )
        bkp_c4_function       = copy.deepcopy(self.c4_function      )
        bkp_c4_function_value = copy.deepcopy(self.c4_function_value)
        
        try:
            self.c4                = []
            self.c4_fixed          = []
            self.c4_has_min        = []
            self.c4_min            = []
            self.c4_has_max        = []
            self.c4_max            = []
            self.c4_function       = []
            self.c4_function_value = []    
        
            for index in range(len(self.chebyshev_box_array)):
                self.c4.append(self.chebyshev_box_array[index].c4)
                self.c4_fixed.append(self.chebyshev_box_array[index].c4_fixed)
                self.c4_has_min.append(self.chebyshev_box_array[index].c4_has_min)
                self.c4_min.append(self.chebyshev_box_array[index].c4_min)
                self.c4_has_max.append(self.chebyshev_box_array[index].c4_has_max)
                self.c4_max.append(self.chebyshev_box_array[index].c4_max)
                self.c4_function.append(self.chebyshev_box_array[index].c4_function)
                self.c4_function_value.append(self.chebyshev_box_array[index].c4_function_value)
        except:
            self.c4                = copy.deepcopy(bkp_c4               )
            self.c4_fixed          = copy.deepcopy(bkp_c4_fixed         )
            self.c4_has_min        = copy.deepcopy(bkp_c4_has_min       )
            self.c4_min            = copy.deepcopy(bkp_c4_min           )
            self.c4_has_max        = copy.deepcopy(bkp_c4_has_max       )
            self.c4_max            = copy.deepcopy(bkp_c4_max           )
            self.c4_function       = copy.deepcopy(bkp_c4_function      )
            self.c4_function_value = copy.deepcopy(bkp_c4_function_value)

    def dump_c5(self):
        bkp_c5                = copy.deepcopy(self.c5               )
        bkp_c5_fixed          = copy.deepcopy(self.c5_fixed         )
        bkp_c5_has_min        = copy.deepcopy(self.c5_has_min       )
        bkp_c5_min            = copy.deepcopy(self.c5_min           )
        bkp_c5_has_max        = copy.deepcopy(self.c5_has_max       )
        bkp_c5_max            = copy.deepcopy(self.c5_max           )
        bkp_c5_function       = copy.deepcopy(self.c5_function      )
        bkp_c5_function_value = copy.deepcopy(self.c5_function_value)
        
        try:
            self.c5                = []
            self.c5_fixed          = []
            self.c5_has_min        = []
            self.c5_min            = []
            self.c5_has_max        = []
            self.c5_max            = []
            self.c5_function       = []
            self.c5_function_value = []    
        
            for index in range(len(self.chebyshev_box_array)):
                self.c5.append(self.chebyshev_box_array[index].c5)
                self.c5_fixed.append(self.chebyshev_box_array[index].c5_fixed)
                self.c5_has_min.append(self.chebyshev_box_array[index].c5_has_min)
                self.c5_min.append(self.chebyshev_box_array[index].c5_min)
                self.c5_has_max.append(self.chebyshev_box_array[index].c5_has_max)
                self.c5_max.append(self.chebyshev_box_array[index].c5_max)
                self.c5_function.append(self.chebyshev_box_array[index].c5_function)
                self.c5_function_value.append(self.chebyshev_box_array[index].c5_function_value)
        except:
            self.c5                = copy.deepcopy(bkp_c5               )
            self.c5_fixed          = copy.deepcopy(bkp_c5_fixed         )
            self.c5_has_min        = copy.deepcopy(bkp_c5_has_min       )
            self.c5_min            = copy.deepcopy(bkp_c5_min           )
            self.c5_has_max        = copy.deepcopy(bkp_c5_has_max       )
            self.c5_max            = copy.deepcopy(bkp_c5_max           )
            self.c5_function       = copy.deepcopy(bkp_c5_function      )
            self.c5_function_value = copy.deepcopy(bkp_c5_function_value)

    def dump_c6(self):
        bkp_c6                = copy.deepcopy(self.c6               )
        bkp_c6_fixed          = copy.deepcopy(self.c6_fixed         )
        bkp_c6_has_min        = copy.deepcopy(self.c6_has_min       )
        bkp_c6_min            = copy.deepcopy(self.c6_min           )
        bkp_c6_has_max        = copy.deepcopy(self.c6_has_max       )
        bkp_c6_max            = copy.deepcopy(self.c6_max           )
        bkp_c6_function       = copy.deepcopy(self.c6_function      )
        bkp_c6_function_value = copy.deepcopy(self.c6_function_value)
        
        try:
            self.c6                = []
            self.c6_fixed          = []
            self.c6_has_min        = []
            self.c6_min            = []
            self.c6_has_max        = []
            self.c6_max            = []
            self.c6_function       = []
            self.c6_function_value = []    
        
            for index in range(len(self.chebyshev_box_array)):
                self.c6.append(self.chebyshev_box_array[index].c6)
                self.c6_fixed.append(self.chebyshev_box_array[index].c6_fixed)
                self.c6_has_min.append(self.chebyshev_box_array[index].c6_has_min)
                self.c6_min.append(self.chebyshev_box_array[index].c6_min)
                self.c6_has_max.append(self.chebyshev_box_array[index].c6_has_max)
                self.c6_max.append(self.chebyshev_box_array[index].c6_max)
                self.c6_function.append(self.chebyshev_box_array[index].c6_function)
                self.c6_function_value.append(self.chebyshev_box_array[index].c6_function_value)
        except:
            self.c6                = copy.deepcopy(bkp_c6               )
            self.c6_fixed          = copy.deepcopy(bkp_c6_fixed         )
            self.c6_has_min        = copy.deepcopy(bkp_c6_has_min       )
            self.c6_min            = copy.deepcopy(bkp_c6_min           )
            self.c6_has_max        = copy.deepcopy(bkp_c6_has_max       )
            self.c6_max            = copy.deepcopy(bkp_c6_max           )
            self.c6_function       = copy.deepcopy(bkp_c6_function      )
            self.c6_function_value = copy.deepcopy(bkp_c6_function_value)

    def dump_c7(self):
        bkp_c7                = copy.deepcopy(self.c7               )
        bkp_c7_fixed          = copy.deepcopy(self.c7_fixed         )
        bkp_c7_has_min        = copy.deepcopy(self.c7_has_min       )
        bkp_c7_min            = copy.deepcopy(self.c7_min           )
        bkp_c7_has_max        = copy.deepcopy(self.c7_has_max       )
        bkp_c7_max            = copy.deepcopy(self.c7_max           )
        bkp_c7_function       = copy.deepcopy(self.c7_function      )
        bkp_c7_function_value = copy.deepcopy(self.c7_function_value)
        
        try:
            self.c7                = []
            self.c7_fixed          = []
            self.c7_has_min        = []
            self.c7_min            = []
            self.c7_has_max        = []
            self.c7_max            = []
            self.c7_function       = []
            self.c7_function_value = []    
        
            for index in range(len(self.chebyshev_box_array)):
                self.c7.append(self.chebyshev_box_array[index].c7)
                self.c7_fixed.append(self.chebyshev_box_array[index].c7_fixed)
                self.c7_has_min.append(self.chebyshev_box_array[index].c7_has_min)
                self.c7_min.append(self.chebyshev_box_array[index].c7_min)
                self.c7_has_max.append(self.chebyshev_box_array[index].c7_has_max)
                self.c7_max.append(self.chebyshev_box_array[index].c7_max)
                self.c7_function.append(self.chebyshev_box_array[index].c7_function)
                self.c7_function_value.append(self.chebyshev_box_array[index].c7_function_value)
        except:
            self.c7                = copy.deepcopy(bkp_c7               )
            self.c7_fixed          = copy.deepcopy(bkp_c7_fixed         )
            self.c7_has_min        = copy.deepcopy(bkp_c7_has_min       )
            self.c7_min            = copy.deepcopy(bkp_c7_min           )
            self.c7_has_max        = copy.deepcopy(bkp_c7_has_max       )
            self.c7_max            = copy.deepcopy(bkp_c7_max           )
            self.c7_function       = copy.deepcopy(bkp_c7_function      )
            self.c7_function_value = copy.deepcopy(bkp_c7_function_value)

    def dump_c8(self):
        bkp_c8                = copy.deepcopy(self.c8               )
        bkp_c8_fixed          = copy.deepcopy(self.c8_fixed         )
        bkp_c8_has_min        = copy.deepcopy(self.c8_has_min       )
        bkp_c8_min            = copy.deepcopy(self.c8_min           )
        bkp_c8_has_max        = copy.deepcopy(self.c8_has_max       )
        bkp_c8_max            = copy.deepcopy(self.c8_max           )
        bkp_c8_function       = copy.deepcopy(self.c8_function      )
        bkp_c8_function_value = copy.deepcopy(self.c8_function_value)
        
        try:
            self.c8                = []
            self.c8_fixed          = []
            self.c8_has_min        = []
            self.c8_min            = []
            self.c8_has_max        = []
            self.c8_max            = []
            self.c8_function       = []
            self.c8_function_value = []    
        
            for index in range(len(self.chebyshev_box_array)):
                self.c8.append(self.chebyshev_box_array[index].c8)
                self.c8_fixed.append(self.chebyshev_box_array[index].c8_fixed)
                self.c8_has_min.append(self.chebyshev_box_array[index].c8_has_min)
                self.c8_min.append(self.chebyshev_box_array[index].c8_min)
                self.c8_has_max.append(self.chebyshev_box_array[index].c8_has_max)
                self.c8_max.append(self.chebyshev_box_array[index].c8_max)
                self.c8_function.append(self.chebyshev_box_array[index].c8_function)
                self.c8_function_value.append(self.chebyshev_box_array[index].c8_function_value)
        except:
            self.c8                = copy.deepcopy(bkp_c8               )
            self.c8_fixed          = copy.deepcopy(bkp_c8_fixed         )
            self.c8_has_min        = copy.deepcopy(bkp_c8_has_min       )
            self.c8_min            = copy.deepcopy(bkp_c8_min           )
            self.c8_has_max        = copy.deepcopy(bkp_c8_has_max       )
            self.c8_max            = copy.deepcopy(bkp_c8_max           )
            self.c8_function       = copy.deepcopy(bkp_c8_function      )
            self.c8_function_value = copy.deepcopy(bkp_c8_function_value)

    def dump_c9(self):
        bkp_c9                = copy.deepcopy(self.c9               )
        bkp_c9_fixed          = copy.deepcopy(self.c9_fixed         )
        bkp_c9_has_min        = copy.deepcopy(self.c9_has_min       )
        bkp_c9_min            = copy.deepcopy(self.c9_min           )
        bkp_c9_has_max        = copy.deepcopy(self.c9_has_max       )
        bkp_c9_max            = copy.deepcopy(self.c9_max           )
        bkp_c9_function       = copy.deepcopy(self.c9_function      )
        bkp_c9_function_value = copy.deepcopy(self.c9_function_value)
        
        try:
            self.c9                = []
            self.c9_fixed          = []
            self.c9_has_min        = []
            self.c9_min            = []
            self.c9_has_max        = []
            self.c9_max            = []
            self.c9_function       = []
            self.c9_function_value = []    
        
            for index in range(len(self.chebyshev_box_array)):
                self.c9.append(self.chebyshev_box_array[index].c9)
                self.c9_fixed.append(self.chebyshev_box_array[index].c9_fixed)
                self.c9_has_min.append(self.chebyshev_box_array[index].c9_has_min)
                self.c9_min.append(self.chebyshev_box_array[index].c9_min)
                self.c9_has_max.append(self.chebyshev_box_array[index].c9_has_max)
                self.c9_max.append(self.chebyshev_box_array[index].c9_max)
                self.c9_function.append(self.chebyshev_box_array[index].c9_function)
                self.c9_function_value.append(self.chebyshev_box_array[index].c9_function_value)
        except:
            self.c9                = copy.deepcopy(bkp_c9               )
            self.c9_fixed          = copy.deepcopy(bkp_c9_fixed         )
            self.c9_has_min        = copy.deepcopy(bkp_c9_has_min       )
            self.c9_min            = copy.deepcopy(bkp_c9_min           )
            self.c9_has_max        = copy.deepcopy(bkp_c9_has_max       )
            self.c9_max            = copy.deepcopy(bkp_c9_max           )
            self.c9_function       = copy.deepcopy(bkp_c9_function      )
            self.c9_function_value = copy.deepcopy(bkp_c9_function_value)




from Orange.widgets.gui import OWComponent
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt

class ChebyshevBackgroundBox(QtWidgets.QWidget, OWComponent):

    c0                = 0.0
    c1                = 0.0
    c2                = 0.0
    c3                = 0.0
    c4                = 0.0
    c5                = 0.0
    c6                = 0.0
    c7                = 0.0
    c8                = 0.0
    c9                = 0.0
    c0_fixed          = 0
    c1_fixed          = 0
    c2_fixed          = 0
    c3_fixed          = 0
    c4_fixed          = 0
    c5_fixed          = 0
    c6_fixed          = 1
    c7_fixed          = 1
    c8_fixed          = 1
    c9_fixed          = 1
    c0_has_min        = 0
    c1_has_min        = 0
    c2_has_min        = 0
    c3_has_min        = 0
    c4_has_min        = 0
    c5_has_min        = 0
    c6_has_min        = 0
    c7_has_min        = 0
    c8_has_min        = 0
    c9_has_min        = 0
    c0_min            = 0.0
    c1_min            = 0.0
    c2_min            = 0.0
    c3_min            = 0.0
    c4_min            = 0.0
    c5_min            = 0.0
    c6_min            = 0.0
    c7_min            = 0.0
    c8_min            = 0.0
    c9_min            = 0.0
    c0_has_max        = 0
    c1_has_max        = 0
    c2_has_max        = 0
    c3_has_max        = 0
    c4_has_max        = 0
    c5_has_max        = 0
    c6_has_max        = 0
    c7_has_max        = 0
    c8_has_max        = 0
    c9_has_max        = 0
    c0_max            = 0.0
    c1_max            = 0.0
    c2_max            = 0.0
    c3_max            = 0.0
    c4_max            = 0.0
    c5_max            = 0.0
    c6_max            = 0.0
    c7_max            = 0.0
    c8_max            = 0.0
    c9_max            = 0.0
    c0_function       = 0
    c1_function       = 0
    c2_function       = 0
    c3_function       = 0
    c4_function       = 0
    c5_function       = 0
    c6_function       = 0
    c7_function       = 0
    c8_function       = 0
    c9_function       = 0
    c0_function_value = ""
    c1_function_value = ""
    c2_function_value = ""
    c3_function_value = ""
    c4_function_value = ""
    c5_function_value = ""
    c6_function_value = ""
    c7_function_value = ""
    c8_function_value = ""
    c9_function_value = ""

    widget = None
    is_on_init = True

    parameter_functions = {}

    crystal_structure = None

    index = 0

    def __init__(self,
                 widget=None,
                 parent=None,
                 index = 0,
                 c0                = 0.0,
                 c1                = 0.0,
                 c2                = 0.0,
                 c3                = 0.0,
                 c4                = 0.0,
                 c5                = 0.0,
                 c6                = 0.0,
                 c7                = 0.0,
                 c8                = 0.0,
                 c9                = 0.0,
                 c0_fixed          = 0,
                 c1_fixed          = 0,
                 c2_fixed          = 0,
                 c3_fixed          = 0,
                 c4_fixed          = 0,
                 c5_fixed          = 0,
                 c6_fixed          = 1,
                 c7_fixed          = 1,
                 c8_fixed          = 1,
                 c9_fixed          = 1,
                 c0_has_min        = 0,
                 c1_has_min        = 0,
                 c2_has_min        = 0,
                 c3_has_min        = 0,
                 c4_has_min        = 0,
                 c5_has_min        = 0,
                 c6_has_min        = 0,
                 c7_has_min        = 0,
                 c8_has_min        = 0,
                 c9_has_min        = 0,
                 c0_min            = 0.0,
                 c1_min            = 0.0,
                 c2_min            = 0.0,
                 c3_min            = 0.0,
                 c4_min            = 0.0,
                 c5_min            = 0.0,
                 c6_min            = 0.0,
                 c7_min            = 0.0,
                 c8_min            = 0.0,
                 c9_min            = 0.0,
                 c0_has_max        = 0,
                 c1_has_max        = 0,
                 c2_has_max        = 0,
                 c3_has_max        = 0,
                 c4_has_max        = 0,
                 c5_has_max        = 0,
                 c6_has_max        = 0,
                 c7_has_max        = 0,
                 c8_has_max        = 0,
                 c9_has_max        = 0,
                 c0_max            = 0.0,
                 c1_max            = 0.0,
                 c2_max            = 0.0,
                 c3_max            = 0.0,
                 c4_max            = 0.0,
                 c5_max            = 0.0,
                 c6_max            = 0.0,
                 c7_max            = 0.0,
                 c8_max            = 0.0,
                 c9_max            = 0.0,
                 c0_function       = 0,
                 c1_function       = 0,
                 c2_function       = 0,
                 c3_function       = 0,
                 c4_function       = 0,
                 c5_function       = 0,
                 c6_function       = 0,
                 c7_function       = 0,
                 c8_function       = 0,
                 c9_function       = 0,
                 c0_function_value = "",
                 c1_function_value = "",
                 c2_function_value = "",
                 c3_function_value = "",
                 c4_function_value = "",
                 c5_function_value = "",
                 c6_function_value = "",
                 c7_function_value = "",
                 c8_function_value = "",
                 c9_function_value = ""):
        super(ChebyshevBackgroundBox, self).__init__(parent)
        OWComponent.__init__(self)

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)
        self.setFixedWidth(widget.CONTROL_AREA_WIDTH - 35)
        self.setFixedHeight(500)

        self.widget = widget
        self.index = index
        
        self.c0                = c0               
        self.c1                = c1               
        self.c2                = c2               
        self.c3                = c3               
        self.c4                = c4               
        self.c5                = c5               
        self.c6                = c6               
        self.c7                = c7               
        self.c8                = c8               
        self.c9                = c9               
        self.c0_fixed          = c0_fixed         
        self.c1_fixed          = c1_fixed         
        self.c2_fixed          = c2_fixed         
        self.c3_fixed          = c3_fixed         
        self.c4_fixed          = c4_fixed         
        self.c5_fixed          = c5_fixed         
        self.c6_fixed          = c6_fixed         
        self.c7_fixed          = c7_fixed         
        self.c8_fixed          = c8_fixed         
        self.c9_fixed          = c9_fixed         
        self.c0_has_min        = c0_has_min       
        self.c1_has_min        = c1_has_min       
        self.c2_has_min        = c2_has_min       
        self.c3_has_min        = c3_has_min       
        self.c4_has_min        = c4_has_min       
        self.c5_has_min        = c5_has_min       
        self.c6_has_min        = c6_has_min       
        self.c7_has_min        = c7_has_min       
        self.c8_has_min        = c8_has_min       
        self.c9_has_min        = c9_has_min       
        self.c0_min            = c0_min           
        self.c1_min            = c1_min           
        self.c2_min            = c2_min           
        self.c3_min            = c3_min           
        self.c4_min            = c4_min           
        self.c5_min            = c5_min           
        self.c6_min            = c6_min           
        self.c7_min            = c7_min           
        self.c8_min            = c8_min           
        self.c9_min            = c9_min           
        self.c0_has_max        = c0_has_max       
        self.c1_has_max        = c1_has_max       
        self.c2_has_max        = c2_has_max       
        self.c3_has_max        = c3_has_max       
        self.c4_has_max        = c4_has_max       
        self.c5_has_max        = c5_has_max       
        self.c6_has_max        = c6_has_max       
        self.c7_has_max        = c7_has_max       
        self.c8_has_max        = c8_has_max       
        self.c9_has_max        = c9_has_max       
        self.c0_max            = c0_max           
        self.c1_max            = c1_max           
        self.c2_max            = c2_max           
        self.c3_max            = c3_max           
        self.c4_max            = c4_max           
        self.c5_max            = c5_max           
        self.c6_max            = c6_max           
        self.c7_max            = c7_max           
        self.c8_max            = c8_max           
        self.c9_max            = c9_max           
        self.c0_function       = c0_function      
        self.c1_function       = c1_function      
        self.c2_function       = c2_function      
        self.c3_function       = c3_function      
        self.c4_function       = c4_function      
        self.c5_function       = c5_function      
        self.c6_function       = c6_function      
        self.c7_function       = c7_function      
        self.c8_function       = c8_function      
        self.c9_function       = c9_function      
        self.c0_function_value = c0_function_value
        self.c1_function_value = c1_function_value
        self.c2_function_value = c2_function_value
        self.c3_function_value = c3_function_value
        self.c4_function_value = c4_function_value
        self.c5_function_value = c5_function_value
        self.c6_function_value = c6_function_value
        self.c7_function_value = c7_function_value
        self.c8_function_value = c8_function_value
        self.c9_function_value = c9_function_value

        self.CONTROL_AREA_WIDTH = widget.CONTROL_AREA_WIDTH

        container = gui.widgetBox(parent, "", orientation="vertical", width=self.CONTROL_AREA_WIDTH-35)

        widget.create_box_in_widget(self, container, "c0", add_callback=True)
        widget.create_box_in_widget(self, container, "c1", add_callback=True)
        widget.create_box_in_widget(self, container, "c2", add_callback=True)
        widget.create_box_in_widget(self, container, "c3", add_callback=True)
        widget.create_box_in_widget(self, container, "c4", add_callback=True)
        widget.create_box_in_widget(self, container, "c5", add_callback=True)
        widget.create_box_in_widget(self, container, "c6", add_callback=True)
        widget.create_box_in_widget(self, container, "c7", add_callback=True)
        widget.create_box_in_widget(self, container, "c8", add_callback=True)
        widget.create_box_in_widget(self, container, "c9", add_callback=True)

        self.is_on_init = False

    def after_change_workspace_units(self):
        pass

    def set_index(self, index):
        self.index = index

    def callback_c0(self):
        if not self.is_on_init: self.widget.dump_c0()

    def callback_c1(self):
        if not self.is_on_init: self.widget.dump_c1()
        
    def callback_c2(self):
        if not self.is_on_init: self.widget.dump_c2()
        
    def callback_c3(self):
        if not self.is_on_init: self.widget.dump_c3()
        
    def callback_c4(self):
        if not self.is_on_init: self.widget.dump_c4()
        
    def callback_c5(self):
        if not self.is_on_init: self.widget.dump_c5()
        
    def callback_c6(self):
        if not self.is_on_init: self.widget.dump_c6()
        
    def callback_c7(self):
        if not self.is_on_init: self.widget.dump_c7()
        
    def callback_c8(self):
        if not self.is_on_init: self.widget.dump_c8()
        
    def callback_c9(self):
        if not self.is_on_init: self.widget.dump_c9()

    def after_change_workspace_units(self):
        pass

    def set_index(self, index):
        self.index = index

    def get_parameters_prefix(self):
        return ChebyshevBackground.get_parameters_prefix() + self.get_parameter_progressive()

    def get_parameter_progressive(self):
        return str(self.index+1) + "_"

    def set_data(self, background_parameters):
        self.widget.populate_fields_in_widget(self, "c0", background_parameters.c0)
        self.widget.populate_fields_in_widget(self, "c1", background_parameters.c1)
        self.widget.populate_fields_in_widget(self, "c2", background_parameters.c2)
        self.widget.populate_fields_in_widget(self, "c3", background_parameters.c3)
        self.widget.populate_fields_in_widget(self, "c4", background_parameters.c4)
        self.widget.populate_fields_in_widget(self, "c5", background_parameters.c5)
        self.widget.populate_fields_in_widget(self, "c6", background_parameters.c6)
        self.widget.populate_fields_in_widget(self, "c7", background_parameters.c7)
        self.widget.populate_fields_in_widget(self, "c8", background_parameters.c8)
        self.widget.populate_fields_in_widget(self, "c9", background_parameters.c9)

    def send_background(self):
        return ChebyshevBackground(c0=self.widget.populate_parameter_in_widget(self, "c0", self.get_parameters_prefix()),
                                   c1=self.widget.populate_parameter_in_widget(self, "c1", self.get_parameters_prefix()),
                                   c2=self.widget.populate_parameter_in_widget(self, "c2", self.get_parameters_prefix()),
                                   c3=self.widget.populate_parameter_in_widget(self, "c3", self.get_parameters_prefix()),
                                   c4=self.widget.populate_parameter_in_widget(self, "c4", self.get_parameters_prefix()),
                                   c5=self.widget.populate_parameter_in_widget(self, "c5", self.get_parameters_prefix()),
                                   c6=self.widget.populate_parameter_in_widget(self, "c6", self.get_parameters_prefix()),
                                   c7=self.widget.populate_parameter_in_widget(self, "c7", self.get_parameters_prefix()),
                                   c8=self.widget.populate_parameter_in_widget(self, "c8", self.get_parameters_prefix()),
                                   c9=self.widget.populate_parameter_in_widget(self, "c9", self.get_parameters_prefix()))


if __name__ == "__main__":
    a4 =  QApplication(sys.argv)
    ow = OWChebyshevBackground()
    ow.show()
    a.exec_()
    ow.saveSettings()
