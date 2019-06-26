import os, sys, numpy

from PyQt5.QtWidgets import QMessageBox, QApplication
from PyQt5.QtGui import QDoubleValidator

from Orange.widgets.settings import Setting
from Orange.widgets import gui as orangegui

from orangecontrib.wonder.util.widgets.ow_generic_widget import OWGenericWidget
from orangecontrib.wonder.util.gui.gui_utility import gui
from orangecontrib.wonder.util import congruence
from orangecontrib.wonder.controller.fit.fit_global_parameters import FitGlobalParameters
from orangecontrib.wonder.controller.fit.instrument.instrumental_parameters import SpecimenDisplacement

class OWSpecimenDisplacementPeakShift(OWGenericWidget):

    name = "Specimen Displacement Peak Shift"
    description = "Specimen Displacement Peak Shift"
    icon = "icons/specimen_displacement_peak_shift.png"
    priority = 15

    want_main_area = False

    displacement = Setting(0.0)
    displacement_fixed = Setting(0)
    displacement_has_min = Setting(0)
    displacement_min = Setting(0.0)
    displacement_has_max = Setting(0)
    displacement_max = Setting(0.0)
    displacement_function = Setting(0)
    displacement_function_value = Setting("")

    goniometer_radius = Setting(1.0)

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

        gui.button(button_box, self, "Send Peak Shift", height=50, callback=self.send_peak_displacement)

        specimen_displacement_box = gui.widgetBox(main_box,
                                    "Specimen Displacement", orientation="vertical",
                                    width=self.CONTROL_AREA_WIDTH - 30)

        gui.lineEdit(specimen_displacement_box, self, "goniometer_radius", "Goniometer Radius [m]", labelWidth=300, valueType=float, validator=QDoubleValidator())
        orangegui.separator(specimen_displacement_box)
        self.create_box(specimen_displacement_box, "displacement", label="\u03b4 [\u03bcm]")

    def send_peak_displacement(self):
        try:
            if not self.fit_global_parameters is None:
                congruence.checkStrictlyPositiveNumber(self.goniometer_radius, "Goniometer Radius")

                displacement = self.populate_parameter("displacement", SpecimenDisplacement.get_parameters_prefix())
                displacement.rescale(1e-6) # to m

                self.fit_global_parameters.set_shift_parameters([SpecimenDisplacement(goniometer_radius=self.goniometer_radius, displacement=displacement)])
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
                displacement_parameters = self.fit_global_parameters.get_shift_parameters(SpecimenDisplacement.__name__)

                if not displacement_parameters is None:
                    self.goniometer_radius = displacement_parameters.goniometer_radius

                    displacement = displacement_parameters[0].displacement.duplicate()
                    displacement.rescale(1e6) # to um

                    self.populate_fields("displacement", displacement)


            if self.is_automatic_run:
                self.send_peak_displacement()



if __name__ == "__main__":
    a = QApplication(sys.argv)
    ow = OWSpecimenDisplacementPeakShift()
    ow.show()
    a.exec_()
    ow.saveSettings()
