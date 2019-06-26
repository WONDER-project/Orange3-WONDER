import os, sys, numpy

from PyQt5.QtWidgets import QMessageBox, QApplication

from Orange.widgets.settings import Setting

from orangecontrib.wonder.util.widgets.ow_generic_widget import OWGenericWidget
from orangecontrib.wonder.util.gui.gui_utility import gui
from orangecontrib.wonder.controller.fit.fit_global_parameters import FitGlobalParameters
from orangecontrib.wonder.controller.fit.instrument.instrumental_parameters import ZeroError

class OWZeroErrorPeakShift(OWGenericWidget):

    name = "Zero Error Peak Shift"
    description = "Zero Error Peak Shift"
    icon = "icons/zero_error_peak_shift.png"
    priority = 14

    want_main_area = False

    shift = Setting(0.0)
    shift_fixed = Setting(0)
    shift_has_min = Setting(0)
    shift_min = Setting(0.0)
    shift_has_max = Setting(0)
    shift_max = Setting(0.0)
    shift_function = Setting(0)
    shift_function_value = Setting("")

    inputs = [("Fit Global Parameters", FitGlobalParameters, 'set_data')]
    outputs = [("Fit Global Parameters", FitGlobalParameters)]

    def __init__(self):
        super().__init__(show_automatic_box=True)

        main_box = gui.widgetBox(self.controlArea,
                                 "Peak Shift", orientation="vertical",
                                 width=self.CONTROL_AREA_WIDTH - 10, height=300)


        button_box = gui.widgetBox(main_box,
                                   "", orientation="horizontal",
                                   width=self.CONTROL_AREA_WIDTH-25)

        gui.button(button_box, self, "Send Peak Shift", height=50, callback=self.send_peak_shift)

        zero_error_box = gui.widgetBox(main_box,
                                    "Zero Error", orientation="vertical",
                                    width=self.CONTROL_AREA_WIDTH - 30)

        self.create_box(zero_error_box, "shift", label="\u0394(2\u03b8) [deg]")

    def send_peak_shift(self):
        try:
            if not self.fit_global_parameters is None:

                self.fit_global_parameters.set_shift_parameters([ZeroError(shift=self.populate_parameter("shift", ZeroError.get_parameters_prefix()))])
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
                shift_parameters = self.fit_global_parameters.get_shift_parameters(ZeroError.__name__)

                if not shift_parameters is None:
                    self.populate_fields("shift", shift_parameters[0].shift)

            if self.is_automatic_run:
                self.send_peak_shift()



if __name__ == "__main__":
    a = QApplication(sys.argv)
    ow = OWZeroErrorPeakShift()
    ow.show()
    a.exec_()
    ow.saveSettings()
