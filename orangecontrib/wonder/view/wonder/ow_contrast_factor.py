import os, sys, numpy

from PyQt5.QtWidgets import QMessageBox, QScrollArea, QTableWidget, QApplication


from Orange.widgets.settings import Setting
from Orange.widgets import gui as orangegui

from orangecontrib.wonder.util.widgets.ow_generic_widget import OWGenericWidget
from orangecontrib.wonder.util.gui.gui_utility import gui
from orangecontrib.wonder.util import congruence
from orangecontrib.wonder.controller.fit.fit_parameter import FitParameter
from orangecontrib.wonder.controller.fit.fit_global_parameters import FitGlobalParameters
from orangecontrib.wonder.controller.fit.microstructure.constrast_factor import calculate_A_B_coefficients
from orangecontrib.wonder.controller.fit.microstructure.strain import KrivoglazWilkensModel

class OWContrastFactor(OWGenericWidget):

    name = "Contrast Factor Calculator"
    description = "Contrast Factor Calculator"
    icon = "icons/contrast_factor.png"
    priority = 18

    want_main_area = False

    c11 = Setting(24.65)
    c12 = Setting(13.45)
    c44 = Setting(2.87)

    inputs = [("Fit Global Parameters", FitGlobalParameters, 'set_data')]
    outputs = [("Fit Global Parameters", FitGlobalParameters)]

    def __init__(self):
        super().__init__(show_automatic_box=True)

        main_box = gui.widgetBox(self.controlArea,
                                 "Constrast Factor Calculator Parameters", orientation="vertical",
                                 width=self.CONTROL_AREA_WIDTH - 10, height=600)

        button_box = gui.widgetBox(main_box,
                                   "", orientation="horizontal",
                                   width=self.CONTROL_AREA_WIDTH-25)

        gui.button(button_box, self, "Send Constrast Factor A/B Parameters", height=50, callback=self.send_contrast_factor_a_b)

        contrast_factor_box = gui.widgetBox(main_box, "Elastic Constants", orientation="vertical", height=300, width=self.CONTROL_AREA_WIDTH - 30)

        gui.lineEdit(contrast_factor_box, self, "c11", "c11", labelWidth=90, valueType=float)
        gui.lineEdit(contrast_factor_box, self, "c12", "c12", labelWidth=90, valueType=float)
        gui.lineEdit(contrast_factor_box, self, "c44", "c44", labelWidth=90, valueType=float)

        text_area_box = gui.widgetBox(contrast_factor_box, "Calculation Result", orientation="vertical",
                                      height=160, width=self.CONTROL_AREA_WIDTH - 50)

        self.text_area = gui.textArea(height=120, width=self.CONTROL_AREA_WIDTH - 70, readOnly=True)
        self.text_area.setText("")
        self.text_area.setStyleSheet("font-family: Courier, monospace;")

        text_area_box.layout().addWidget(self.text_area)

        orangegui.separator(main_box, height=280)

    def send_contrast_factor_a_b(self):
        try:
            if not self.fit_global_parameters is None:
                if self.fit_global_parameters.fit_initialization is None:
                    raise ValueError("Calculation is not possibile, Crystal Structure is missing")

                if self.fit_global_parameters.fit_initialization.crystal_structures is None:
                    raise ValueError("Calculation is not possibile, Crystal Structure is missing")

                congruence.checkStrictlyPositiveNumber(self.c11, "c11")
                congruence.checkStrictlyPositiveNumber(self.c12, "c12")
                congruence.checkStrictlyPositiveNumber(self.c44, "c44")

                symmetry = self.fit_global_parameters.fit_initialization.crystal_structures[0].symmetry

                Ae, Be, As, Bs = calculate_A_B_coefficients(self.c11, self.c12, self.c44, symmetry)

                text  = "Ae = " + str(Ae) + "\n"
                text += "Be = " + str(Be) + "\n"
                text += "As = " + str(As) + "\n"
                text += "Bs = " + str(Bs) + "\n"

                self.text_area.setText(text)

                self.fit_global_parameters.strain_parameters = [KrivoglazWilkensModel(Ae=FitParameter(parameter_name=KrivoglazWilkensModel.get_parameters_prefix() + "Ae", value=Ae, fixed=True),
                                                                                      Be=FitParameter(parameter_name=KrivoglazWilkensModel.get_parameters_prefix() + "Be", value=Be, fixed=True),
                                                                                      As=FitParameter(parameter_name=KrivoglazWilkensModel.get_parameters_prefix() + "As", value=As, fixed=True),
                                                                                      Bs=FitParameter(parameter_name=KrivoglazWilkensModel.get_parameters_prefix() + "Bs", value=Bs, fixed=True))]

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
                raise Exception("This widget should be put BEFORE the strain model widget")

            if self.is_automatic_run:
                self.send_contrast_factor_a_b()



if __name__ == "__main__":
    a = QApplication(sys.argv)
    ow = OWContrastFactor()
    ow.show()
    a.exec_()
    ow.saveSettings()
