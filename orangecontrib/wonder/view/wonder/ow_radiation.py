import os, sys, numpy, copy

from PyQt5.QtWidgets import QMessageBox, QApplication
from PyQt5.QtCore import Qt

from Orange.widgets.settings import Setting
from Orange.widgets import gui as orangegui

from orangecontrib.wonder.util.widgets.ow_generic_widget import OWGenericWidget
from orangecontrib.wonder.util.gui.gui_utility import gui, ConfirmDialog
from orangecontrib.wonder.util import congruence
from orangecontrib.wonder.model.diffraction_pattern import DiffractionPattern
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

class OWRadiation(OWGenericWidget):

    name = "Radiation"
    description = "Radiation of diffraction patterns"
    icon = "icons/lambda.png"
    priority = 1.1

    want_main_area = False

    is_multiple_wavelength = Setting([0])
    
    wavelength = Setting([0.0826])
    wavelength_fixed = Setting([0])
    wavelength_has_min = Setting([0])
    wavelength_min = Setting([0.0])
    wavelength_has_max = Setting([0])
    wavelength_max = Setting([0.0])
    wavelength_function = Setting([0])
    wavelength_function_value = Setting([""])
    
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

    inputs = [("Fit Global Parameters", FitGlobalParameters, 'set_data')]
    outputs = [("Fit Global Parameters", FitGlobalParameters)]

    fit_global_parameters = None

    def __init__(self):
        super().__init__(show_automatic_box=True)

        main_box = gui.widgetBox(self.controlArea,
                                 "Radiation", orientation="vertical",
                                 width=self.CONTROL_AREA_WIDTH - 5, height=600)


        button_box = gui.widgetBox(main_box,
                                   "", orientation="horizontal",
                                   width=self.CONTROL_AREA_WIDTH-25)

        gui.button(button_box, self, "Send Radiation", height=50, callback=self.send_radiation)

        self.radiation_tabs = gui.tabWidget(main_box)
        self.radiation_box_array = []

        for index in range(len(self.is_multiple_wavelength)):
            radiation_tab = gui.createTabPage(self.radiation_tabs, "Diff. Patt. " + str(index + 1))

            radiation_box = RadiationBox(widget=self,
                                         parent=radiation_tab,
                                         index = index,
                                         is_multiple_wavelength      = self.is_multiple_wavelength[index],
                                         wavelength                  = self.wavelength[index],
                                         wavelength_fixed            = self.wavelength_fixed[index],
                                         wavelength_has_min          = self.wavelength_has_min[index],
                                         wavelength_min              = self.wavelength_min[index],
                                         wavelength_has_max          = self.wavelength_has_max[index],
                                         wavelength_max              = self.wavelength_max[index],
                                         wavelength_function         = self.wavelength_function[index],
                                         wavelength_function_value   = self.wavelength_function_value[index],
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
                                         )

            self.radiation_box_array.append(radiation_box)

    def set_data(self, data):
        try:
            if not data is None:
                self.fit_global_parameters = data.duplicate()

                self.dumpSettings()

                # remove radiation boxes and regenerate

                self.radiation_box_array = []

                for index in range(self.radiation_tabs.count()):
                    self.radiation_tabs.removeTab(0)

                for index in range(self.fit_global_parameters.fit_initialization.get_diffraction_patterns_number()):
                    radiation_tab = gui.createTabPage(self.radiation_tabs, "Diff. Patt. " + str(index + 1))

                    radiation_box = RadiationBox(widget=self,
                                                 parent=radiation_tab,
                                                 index = index,
                                                 diffraction_pattern=self.fit_global_parameters.fit_initialization.diffraction_patterns[index],
                                                 is_multiple_wavelength      = self.is_multiple_wavelength[index],
                                                 wavelength                  = self.wavelength[index],
                                                 wavelength_fixed            = self.wavelength_fixed[index],
                                                 wavelength_has_min          = self.wavelength_has_min[index],
                                                 wavelength_min              = self.wavelength_min[index],
                                                 wavelength_has_max          = self.wavelength_has_max[index],
                                                 wavelength_max              = self.wavelength_max[index],
                                                 wavelength_function         = self.wavelength_function[index],
                                                 wavelength_function_value   = self.wavelength_function_value[index],
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
                                                 )

                    self.radiation_box_array.append(radiation_box)

                self.dumpSettings()

                if self.is_automatic_run:
                    self.send_radiation()

        except Exception as e:
            QMessageBox.critical(self, "Error during load",
                                 str(e),
                                 QMessageBox.Ok)

            if self.IS_DEVELOP: raise e

    def send_radiation(self):
        try:
            if not self.fit_global_parameters is None:
                diffraction_patterns = []

                for index in range(self.fit_global_parameters.fit_initialization.get_diffraction_patterns_number()):
                    diffraction_patterns.append(self.radiation_box_array[index].get_diffraction_pattern())

                self.fit_global_parameters.fit_initialization.diffraction_patterns = diffraction_patterns
                self.fit_global_parameters.regenerate_parameters()

                self.send("Fit Global Parameters", self.fit_global_parameters)
        except Exception as e:
            QMessageBox.critical(self, "Error",
                                 str(e),
                                 QMessageBox.Ok)

            if self.IS_DEVELOP: raise e

    ##############################
    # SINGLE FIELDS SIGNALS
    ##############################

    def dumpSettings(self):
        self.dump_is_multiple_wavelength()
        self.dump_wavelength()
        self.dump_wavelength_2()
        self.dump_wavelength_3()
        self.dump_wavelength_4()
        self.dump_wavelength_5()
        self.dump_weight_2()
        self.dump_weight_3()
        self.dump_weight_4()
        self.dump_weight_5()

    def dump_is_multiple_wavelength(self):
        bkp_is_multiple_wavelength = copy.deepcopy(self.is_multiple_wavelength)

        try:
            self.is_multiple_wavelength = []

            for index in range(len(self.radiation_box_array)):
                self.is_multiple_wavelength.append(self.radiation_box_array[index].is_multiple_wavelength)
        except:
            self.is_multiple_wavelength = copy.deepcopy(bkp_is_multiple_wavelength)

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
        
            for index in range(len(self.radiation_box_array)):
                self.wavelength.append(self.radiation_box_array[index].wavelength)
                self.wavelength_fixed.append(self.radiation_box_array[index].wavelength_fixed)
                self.wavelength_has_min.append(self.radiation_box_array[index].wavelength_has_min)
                self.wavelength_min.append(self.radiation_box_array[index].wavelength_min)
                self.wavelength_has_max.append(self.radiation_box_array[index].wavelength_has_max)
                self.wavelength_max.append(self.radiation_box_array[index].wavelength_max)
                self.wavelength_function.append(self.radiation_box_array[index].wavelength_function)
                self.wavelength_function_value.append(self.radiation_box_array[index].wavelength_function_value)
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
        
            for index in range(len(self.radiation_box_array)):
                self.wavelength_2.append(self.radiation_box_array[index].wavelength_2)
                self.wavelength_2_fixed.append(self.radiation_box_array[index].wavelength_2_fixed)
                self.wavelength_2_has_min.append(self.radiation_box_array[index].wavelength_2_has_min)
                self.wavelength_2_min.append(self.radiation_box_array[index].wavelength_2_min)
                self.wavelength_2_has_max.append(self.radiation_box_array[index].wavelength_2_has_max)
                self.wavelength_2_max.append(self.radiation_box_array[index].wavelength_2_max)
                self.wavelength_2_function.append(self.radiation_box_array[index].wavelength_2_function)
                self.wavelength_2_function_value.append(self.radiation_box_array[index].wavelength_2_function_value)
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
        
            for index in range(len(self.radiation_box_array)):
                self.wavelength_3.append(self.radiation_box_array[index].wavelength_3)
                self.wavelength_3_fixed.append(self.radiation_box_array[index].wavelength_3_fixed)
                self.wavelength_3_has_min.append(self.radiation_box_array[index].wavelength_3_has_min)
                self.wavelength_3_min.append(self.radiation_box_array[index].wavelength_3_min)
                self.wavelength_3_has_max.append(self.radiation_box_array[index].wavelength_3_has_max)
                self.wavelength_3_max.append(self.radiation_box_array[index].wavelength_3_max)
                self.wavelength_3_function.append(self.radiation_box_array[index].wavelength_3_function)
                self.wavelength_3_function_value.append(self.radiation_box_array[index].wavelength_3_function_value)
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
        
            for index in range(len(self.radiation_box_array)):
                self.wavelength_4.append(self.radiation_box_array[index].wavelength_4)
                self.wavelength_4_fixed.append(self.radiation_box_array[index].wavelength_4_fixed)
                self.wavelength_4_has_min.append(self.radiation_box_array[index].wavelength_4_has_min)
                self.wavelength_4_min.append(self.radiation_box_array[index].wavelength_4_min)
                self.wavelength_4_has_max.append(self.radiation_box_array[index].wavelength_4_has_max)
                self.wavelength_4_max.append(self.radiation_box_array[index].wavelength_4_max)
                self.wavelength_4_function.append(self.radiation_box_array[index].wavelength_4_function)
                self.wavelength_4_function_value.append(self.radiation_box_array[index].wavelength_4_function_value)
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
        
            for index in range(len(self.radiation_box_array)):
                self.wavelength_5.append(self.radiation_box_array[index].wavelength_5)
                self.wavelength_5_fixed.append(self.radiation_box_array[index].wavelength_5_fixed)
                self.wavelength_5_has_min.append(self.radiation_box_array[index].wavelength_5_has_min)
                self.wavelength_5_min.append(self.radiation_box_array[index].wavelength_5_min)
                self.wavelength_5_has_max.append(self.radiation_box_array[index].wavelength_5_has_max)
                self.wavelength_5_max.append(self.radiation_box_array[index].wavelength_5_max)
                self.wavelength_5_function.append(self.radiation_box_array[index].wavelength_5_function)
                self.wavelength_5_function_value.append(self.radiation_box_array[index].wavelength_5_function_value)
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
        
            for index in range(len(self.radiation_box_array)):
                self.weight_2.append(self.radiation_box_array[index].weight_2)
                self.weight_2_fixed.append(self.radiation_box_array[index].weight_2_fixed)
                self.weight_2_has_min.append(self.radiation_box_array[index].weight_2_has_min)
                self.weight_2_min.append(self.radiation_box_array[index].weight_2_min)
                self.weight_2_has_max.append(self.radiation_box_array[index].weight_2_has_max)
                self.weight_2_max.append(self.radiation_box_array[index].weight_2_max)
                self.weight_2_function.append(self.radiation_box_array[index].weight_2_function)
                self.weight_2_function_value.append(self.radiation_box_array[index].weight_2_function_value)
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
        
            for index in range(len(self.radiation_box_array)):
                self.weight_3.append(self.radiation_box_array[index].weight_3)
                self.weight_3_fixed.append(self.radiation_box_array[index].weight_3_fixed)
                self.weight_3_has_min.append(self.radiation_box_array[index].weight_3_has_min)
                self.weight_3_min.append(self.radiation_box_array[index].weight_3_min)
                self.weight_3_has_max.append(self.radiation_box_array[index].weight_3_has_max)
                self.weight_3_max.append(self.radiation_box_array[index].weight_3_max)
                self.weight_3_function.append(self.radiation_box_array[index].weight_3_function)
                self.weight_3_function_value.append(self.radiation_box_array[index].weight_3_function_value)
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
        
            for index in range(len(self.radiation_box_array)):
                self.weight_4.append(self.radiation_box_array[index].weight_4)
                self.weight_4_fixed.append(self.radiation_box_array[index].weight_4_fixed)
                self.weight_4_has_min.append(self.radiation_box_array[index].weight_4_has_min)
                self.weight_4_min.append(self.radiation_box_array[index].weight_4_min)
                self.weight_4_has_max.append(self.radiation_box_array[index].weight_4_has_max)
                self.weight_4_max.append(self.radiation_box_array[index].weight_4_max)
                self.weight_4_function.append(self.radiation_box_array[index].weight_4_function)
                self.weight_4_function_value.append(self.radiation_box_array[index].weight_4_function_value)
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
        
            for index in range(len(self.radiation_box_array)):
                self.weight_5.append(self.radiation_box_array[index].weight_5)
                self.weight_5_fixed.append(self.radiation_box_array[index].weight_5_fixed)
                self.weight_5_has_min.append(self.radiation_box_array[index].weight_5_has_min)
                self.weight_5_min.append(self.radiation_box_array[index].weight_5_min)
                self.weight_5_has_max.append(self.radiation_box_array[index].weight_5_has_max)
                self.weight_5_max.append(self.radiation_box_array[index].weight_5_max)
                self.weight_5_function.append(self.radiation_box_array[index].weight_5_function)
                self.weight_5_function_value.append(self.radiation_box_array[index].weight_5_function_value)
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

class RadiationBox(QtWidgets.QWidget, OWComponent):

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

    widget = None
    is_on_init = True

    parameter_functions = {}

    diffraction_pattern = None

    index = 0

    def __init__(self,
                 widget=None,
                 parent=None,
                 index = 0,
                 diffraction_pattern = None,
                 is_multiple_wavelength = 0,
                 wavelength = 0.0826,
                 wavelength_fixed = 0,
                 wavelength_has_min = 0,
                 wavelength_min = 0.0,
                 wavelength_has_max = 0,
                 wavelength_max = 0.0,
                 wavelength_function = 0,
                 wavelength_function_value = "",
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
                 weight_5_function_value = ""):
        super(RadiationBox, self).__init__(parent)
        OWComponent.__init__(self)

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)
        self.setFixedWidth(widget.CONTROL_AREA_WIDTH - 35)
        self.setFixedHeight(500)

        self.widget = widget
        self.index = index

        self.CONTROL_AREA_WIDTH = widget.CONTROL_AREA_WIDTH

        container = gui.widgetBox(parent, "", orientation="vertical", width=self.CONTROL_AREA_WIDTH-35)

        widget.create_box_in_widget(self, container,  "wavelength", label="\u03BB  [nm]", disable_function=True, add_callback=True)

        self.is_multiple_wavelength      = is_multiple_wavelength
        self.wavelength                  = wavelength
        self.wavelength_fixed            = wavelength_fixed
        self.wavelength_has_min          = wavelength_has_min
        self.wavelength_min              = wavelength_min
        self.wavelength_has_max          = wavelength_has_max
        self.wavelength_max              = wavelength_max
        self.wavelength_function         = wavelength_function
        self.wavelength_function_value   = wavelength_function_value
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

        if not diffraction_pattern is None:
            self.diffraction_pattern = diffraction_pattern

            OWGenericWidget.populate_fields_in_widget(self, "wavelength", self.diffraction_pattern.wavelength, value_only=True)
            self.is_multiple_wavelength = self.diffraction_pattern.is_single_wavelength == False

        self.secondary_box       = gui.widgetBox(container, "", orientation="vertical", width=self.CONTROL_AREA_WIDTH - 35, spacing=0)

        OWGenericWidget.create_box_in_widget(self, self.secondary_box,  "wavelength_2", label="\u03BB 2 [nm]", label_width=55, add_callback=True)
        OWGenericWidget.create_box_in_widget(self, self.secondary_box,  "weight_2", label="weight 2", label_width=55, add_callback=True)
        OWGenericWidget.create_box_in_widget(self, self.secondary_box,  "wavelength_3", label="\u03BB 3 [nm]", label_width=55, add_callback=True)
        OWGenericWidget.create_box_in_widget(self, self.secondary_box,  "weight_3", label="weight 3", label_width=55, add_callback=True)
        OWGenericWidget.create_box_in_widget(self, self.secondary_box,  "wavelength_4", label="\u03BB 4 [nm]", label_width=55, add_callback=True)
        OWGenericWidget.create_box_in_widget(self, self.secondary_box,  "weight_4", label="weight 4", label_width=55, add_callback=True)
        OWGenericWidget.create_box_in_widget(self, self.secondary_box,  "wavelength_5", label="\u03BB 5 [nm]", label_width=55, add_callback=True)
        OWGenericWidget.create_box_in_widget(self, self.secondary_box,  "weight_5", label="weight 5", label_width=55, add_callback=True)

        self.secondary_box_empty = gui.widgetBox(container, "", orientation="vertical", width=self.CONTROL_AREA_WIDTH - 35, spacing=0)

        self.set_is_multiple_wavelength()

        self.is_on_init = False

    def set_is_multiple_wavelength(self):
        if self.is_multiple_wavelength == 0:
            self.secondary_box.setVisible(False)
            self.secondary_box_empty.setVisible(True)
            OWGenericWidget.populate_fields_in_widget(self, "wavelength_2", FitParameter(value=0.0, fixed=True), value_only=False)
            OWGenericWidget.populate_fields_in_widget(self, "weight_2", FitParameter(value=0.0, fixed=True), value_only=False)
            OWGenericWidget.populate_fields_in_widget(self, "wavelength_3", FitParameter(value=0.0, fixed=True), value_only=False)
            OWGenericWidget.populate_fields_in_widget(self, "weight_3", FitParameter(value=0.0, fixed=True), value_only=False)
            OWGenericWidget.populate_fields_in_widget(self, "wavelength_4", FitParameter(value=0.0, fixed=True), value_only=False)
            OWGenericWidget.populate_fields_in_widget(self, "weight_4", FitParameter(value=0.0, fixed=True), value_only=False)
            OWGenericWidget.populate_fields_in_widget(self, "wavelength_5", FitParameter(value=0.0, fixed=True), value_only=False)
            OWGenericWidget.populate_fields_in_widget(self, "weight_5", FitParameter(value=0.0, fixed=True), value_only=False)
        else:
            self.secondary_box.setVisible(True)
            self.secondary_box_empty.setVisible(False)

            if self.is_on_init and not self.diffraction_pattern is None:
                nr_secondary_wavelengths = len(self.diffraction_pattern.secondary_wavelengths)

                for index in range(nr_secondary_wavelengths):
                    OWGenericWidget.populate_fields_in_widget(self, "wavelength_" + str(2 + index), self.diffraction_pattern.secondary_wavelengths[index], value_only=True)
                    OWGenericWidget.populate_fields_in_widget(self, "weight_" + str(2 + index), self.diffraction_pattern.secondary_wavelengths_weights[index], value_only=True)

                if nr_secondary_wavelengths < 4:
                    for index in range(nr_secondary_wavelengths+1, 6):
                        OWGenericWidget.populate_fields_in_widget(self, "wavelength_" + str(index), FitParameter(value=0.0, fixed=True), value_only=False)
                        OWGenericWidget.populate_fields_in_widget(self, "weight_" + str(index), FitParameter(value=0.0, fixed=True), value_only=False)

        if not self.is_on_init or (self.is_on_init and not self.diffraction_pattern is None):
            self.widget.dump_is_multiple_wavelength()
            self.widget.dump_wavelength_2()
            self.widget.dump_wavelength_3()
            self.widget.dump_wavelength_4()
            self.widget.dump_wavelength_5()
            self.widget.dump_weight_2()
            self.widget.dump_weight_3()
            self.widget.dump_weight_4()
            self.widget.dump_weight_5()

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

    def after_change_workspace_units(self):
        pass

    def get_diffraction_pattern(self):
        self.diffraction_pattern.wavelength = self.widget.populate_parameter_in_widget(self,
                                                                                       "wavelength",
                                                                                       DiffractionPattern.get_parameters_prefix() + str(self.index+1) + "_")
        if self.is_multiple_wavelength == 1:
            secondary_wavelengths = []
            secondary_wavelengths_weights = []

            secondary_index = 2
            for index in range(0, 4):
                var_wl = "wavelength_" + str(secondary_index + index)
                var_we = "weight_" + str(secondary_index + index)

                secondary_wavelength = self.widget.populate_parameter_in_widget(self,
                                                                                var_wl,
                                                                                DiffractionPattern.get_parameters_prefix() + str(self.index+1) + "_")
                secondary_wavelength_weight = self.widget.populate_parameter_in_widget(self,
                                                                                       var_we,
                                                                                       DiffractionPattern.get_parameters_prefix() + str(self.index+1) + "_")

                if secondary_wavelength.value > 0.0:
                    secondary_wavelengths.append(secondary_wavelength)
                    secondary_wavelengths_weights.append(secondary_wavelength_weight)

            self.diffraction_pattern.set_multiple_wavelengths(secondary_wavelengths, secondary_wavelengths_weights, recalculate=False)

        return self.diffraction_pattern

if __name__ == "__main__":
    a = QApplication(sys.argv)
    ow = OWRadiation()
    ow.show()
    a.exec_()
    ow.saveSettings()
