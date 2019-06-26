import os, sys, numpy

from PyQt5.QtWidgets import QMessageBox, QApplication

from Orange.widgets.settings import Setting

from orangecontrib.wonder.util.widgets.ow_generic_widget import OWGenericWidget
from orangecontrib.wonder.util.gui.gui_utility import gui
from orangecontrib.wonder.controller.fit.fit_global_parameters import FitGlobalParameters
from orangecontrib.wonder.controller.fit.instrument.instrumental_parameters import Lab6TanCorrection

class OWCalibrationPeakShift(OWGenericWidget):

    name = "Calibration Peak Shift"
    description = "Calibration Peak Shift"
    icon = "icons/calibration_peak_shift.png"
    priority = 13

    want_main_area = False

    ax = Setting(0.0)
    bx = Setting(0.0)
    cx = Setting(0.0)
    dx = Setting(0.0)
    ex = Setting(0.0)

    ax_fixed = Setting(0)
    bx_fixed = Setting(0)
    cx_fixed = Setting(0)
    dx_fixed = Setting(0)
    ex_fixed = Setting(0)

    ax_has_min = Setting(0)
    bx_has_min = Setting(0)
    cx_has_min = Setting(0)
    dx_has_min = Setting(0)
    ex_has_min = Setting(0)

    ax_min = Setting(0.0)
    bx_min = Setting(0.0)
    cx_min = Setting(0.0)
    dx_min = Setting(0.0)
    ex_min = Setting(0.0)

    ax_has_max = Setting(0)
    bx_has_max = Setting(0)
    cx_has_max = Setting(0)
    dx_has_max = Setting(0)
    ex_has_max = Setting(0)

    ax_max = Setting(0.0)
    bx_max = Setting(0.0)
    cx_max = Setting(0.0)
    dx_max = Setting(0.0)
    ex_max = Setting(0.0)

    ax_function = Setting(0)
    bx_function = Setting(0)
    cx_function = Setting(0)
    dx_function = Setting(0)
    ex_function = Setting(0)

    ax_function_value = Setting("")
    bx_function_value = Setting("")
    cx_function_value = Setting("")
    dx_function_value = Setting("")
    ex_function_value = Setting("")

    inputs = [("Fit Global Parameters", FitGlobalParameters, 'set_data')]
    outputs = [("Fit Global Parameters", FitGlobalParameters)]

    def __init__(self):
        super().__init__(show_automatic_box=True)

        main_box = gui.widgetBox(self.controlArea,
                                 "Calibration Peak Shift", orientation="vertical",
                                 width=self.CONTROL_AREA_WIDTH - 10, height=300)


        button_box = gui.widgetBox(main_box,
                                   "", orientation="horizontal",
                                   width=self.CONTROL_AREA_WIDTH-25)

        gui.button(button_box, self, "Send Peak Shift", height=50, callback=self.send_peak_shift)

        lab6_box = gui.widgetBox(main_box,
                                    "Lab6 Tan Correction", orientation="vertical",
                                    width=self.CONTROL_AREA_WIDTH - 30)

        self.create_box(lab6_box, "ax")
        self.create_box(lab6_box, "bx")
        self.create_box(lab6_box, "cx")
        self.create_box(lab6_box, "dx")
        self.create_box(lab6_box, "ex")


    def send_peak_shift(self):
        try:
            if not self.fit_global_parameters is None:

                self.fit_global_parameters.set_shift_parameters([Lab6TanCorrection(ax=self.populate_parameter("ax", Lab6TanCorrection.get_parameters_prefix()),
                                                                                   bx=self.populate_parameter("bx", Lab6TanCorrection.get_parameters_prefix()),
                                                                                   cx=self.populate_parameter("cx", Lab6TanCorrection.get_parameters_prefix()),
                                                                                   dx=self.populate_parameter("dx", Lab6TanCorrection.get_parameters_prefix()),
                                                                                   ex=self.populate_parameter("ex", Lab6TanCorrection.get_parameters_prefix()))])
                self.fit_global_parameters.regenerate_parameters()

                self.send("Fit Global Parameters", self.fit_global_parameters)

        except Exception as e:
            QMessageBox.critical(self, "Error",
                                 str(e),
                                 QMessageBox.Ok)

            if self.IS_DEVELOP: raise e


    def set_data(self, data):
        if not data is None:
            self.fit_global_parameters = data.duplicate()
            if not self.fit_global_parameters.shift_parameters is None:
                shift_parameters = self.fit_global_parameters.get_shift_parameters(Lab6TanCorrection.__name__)

                if not shift_parameters is None:
                    self.populate_fields("ax", shift_parameters[0].ax)
                    self.populate_fields("bx", shift_parameters[0].bx)
                    self.populate_fields("cx", shift_parameters[0].cx)
                    self.populate_fields("dx", shift_parameters[0].dx)
                    self.populate_fields("ex", shift_parameters[0].ex)

            if self.is_automatic_run:
                self.send_peak_shift()



if __name__ == "__main__":
    a = QApplication(sys.argv)
    ow = OWCalibrationPeakShift()
    ow.show()
    a.exec_()
    ow.saveSettings()
