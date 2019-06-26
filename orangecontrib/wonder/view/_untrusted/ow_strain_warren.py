import os, sys, numpy

from PyQt5.QtWidgets import QMessageBox, QApplication

from Orange.widgets.settings import Setting

from orangecontrib.wonder.util.widgets.ow_generic_widget import OWGenericWidget
from orangecontrib.wonder.util.gui.gui_utility import gui

from orangecontrib.wonder.controller.fit.fit_global_parameters import FitGlobalParameters
from orangecontrib.wonder.controller.fit.microstructure.strain import WarrenModel

class OWStrainWarren(OWGenericWidget):

    name = "Warren Strain"
    description = "Define Strain"
    icon = "icons/strain.png"
    priority = 7

    want_main_area =  False

    average_cell_parameter = Setting(0.0)
    average_cell_parameter_fixed = Setting(0)
    average_cell_parameter_has_min = Setting(0)
    average_cell_parameter_min = Setting(0.0)
    average_cell_parameter_has_max = Setting(0)
    average_cell_parameter_max = Setting(0.0)
    average_cell_parameter_function = Setting(0)
    average_cell_parameter_function_value = Setting("")

    inputs = [("Fit Global Parameters", FitGlobalParameters, 'set_data')]
    outputs = [("Fit Global Parameters", FitGlobalParameters)]

    def __init__(self):
        super().__init__(show_automatic_box=True)

        main_box = gui.widgetBox(self.controlArea,
                                 "Warren Model Strain", orientation="vertical",
                                 width=self.CONTROL_AREA_WIDTH - 10, height=600)

        self.create_box(parent_box=main_box, var="average_cell_parameter", label="<a>")

        button_box = gui.widgetBox(main_box,
                                   "", orientation="horizontal",
                                   width=self.CONTROL_AREA_WIDTH-25)

        gui.button(button_box,  self, "Send Strain", height=50, callback=self.send_strain)


    def send_strain(self):
        try:
            if not self.fit_global_parameters is None:
                self.fit_global_parameters.strain_parameters = WarrenModel(average_cell_parameter=self.populate_parameter("average_cell_parameter", WarrenModel.get_parameters_prefix()))
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

            if not self.fit_global_parameters.strain_parameters is None:
                self.average_cell_parameter = self.fit_global_parameters.strain_parameters.average_cell_parameter.value

            if self.is_automatic_run:
                self.send_strain()


if __name__ == "__main__":
    a =  QApplication(sys.argv)
    ow = OWStrainWarren()
    ow.show()
    a.exec_()
    ow.saveSettings()
