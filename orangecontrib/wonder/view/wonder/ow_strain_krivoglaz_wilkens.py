import os, sys, numpy

from PyQt5.QtWidgets import QMessageBox, QApplication

from Orange.widgets.settings import Setting

from orangecontrib.wonder.util.widgets.ow_generic_widget import OWGenericWidget
from orangecontrib.wonder.util.gui.gui_utility import gui
from orangecontrib.wonder.util import congruence
from orangecontrib.wonder.controller.fit.fit_global_parameters import FitGlobalParameters
from orangecontrib.wonder.controller.fit.microstructure.strain import KrivoglazWilkensModel

class OWStrainKW(OWGenericWidget):

    name = "Krivoglaz-Wilkens Strain"
    description = "Define Krivoglaz-Wilkens Strain"
    icon = "icons/strain.png"
    priority = 19

    want_main_area =  False

    rho = Setting(0.0)
    Re = Setting(0.0)

    rho_fixed = Setting(0)
    Re_fixed = Setting(0)

    rho_has_min = Setting(1)
    Re_has_min = Setting(1)

    rho_min = Setting(0.0)
    Re_min = Setting(0.0)

    rho_has_max = Setting(0)
    Re_has_max = Setting(0)

    rho_max = Setting(0.0)
    Re_max = Setting(0.0)

    rho_function = Setting(0)
    Re_function = Setting(0)

    rho_function_value = Setting("")
    Re_function_value = Setting("")

    Ae = Setting(0.0)
    Be = Setting(0.0)

    Ae_fixed = Setting(1)
    Be_fixed = Setting(1)

    Ae_has_min = Setting(0)
    Be_has_min = Setting(0)

    Ae_min = Setting(0.0)
    Be_min = Setting(0.0)

    Ae_has_max = Setting(0)
    Be_has_max = Setting(0)

    Ae_max = Setting(0.0)
    Be_max = Setting(0.0)

    Ae_function = Setting(0)
    Be_function = Setting(0)

    Ae_function_value = Setting("")
    Be_function_value = Setting("")

    As = Setting(0.0)
    Bs = Setting(0.0)

    As_fixed = Setting(1)
    Bs_fixed = Setting(1)

    As_has_min = Setting(0)
    Bs_has_min = Setting(0)

    As_min = Setting(0.0)
    Bs_min = Setting(0.0)

    As_has_max = Setting(0)
    Bs_has_max = Setting(0)

    As_max = Setting(0.0)
    Bs_max = Setting(0.0)

    As_function = Setting(0)
    Bs_function = Setting(0)

    As_function_value = Setting("")
    Bs_function_value = Setting("")

    mix = Setting(0.5)
    b = Setting(0.0)

    mix_fixed = Setting(0)
    b_fixed = Setting(0)

    mix_has_min = Setting(1)
    b_has_min = Setting(0)

    mix_min = Setting(0.0)
    b_min = Setting(0.0)

    mix_has_max = Setting(1)
    b_has_max = Setting(0)

    mix_max = Setting(1.0)
    b_max = Setting(0.0)

    mix_function = Setting(0)
    b_function = Setting(1)

    mix_function_value = Setting("")
    b_function_value = Setting("crystal_structure_a*sqrt(3)/2")

    inputs = [("Fit Global Parameters", FitGlobalParameters, 'set_data')]
    outputs = [("Fit Global Parameters", FitGlobalParameters)]

    def __init__(self):
        super().__init__(show_automatic_box=True)

        main_box = gui.widgetBox(self.controlArea,
                                 "Strain", orientation="vertical",
                                 width=self.CONTROL_AREA_WIDTH - 10, height=600)

        button_box = gui.widgetBox(main_box,
                                   "", orientation="horizontal",
                                   width=self.CONTROL_AREA_WIDTH-25)

        gui.button(button_box,  self, "Send Strain", height=50, callback=self.send_strain)

        self.create_box(main_box, "rho", label="\u03c1")
        self.create_box(main_box, "Re")
        self.create_box(main_box, "Ae")
        self.create_box(main_box, "Be")
        self.create_box(main_box, "As")
        self.create_box(main_box, "Bs")
        self.create_box(main_box, "mix")
        self.create_box(main_box, "b")


    def send_strain(self):
        try:
            if not self.fit_global_parameters is None:
                if not self.rho_function==1: congruence.checkStrictlyPositiveNumber(self.rho, "\u03c1")
                if not self.Re_function==1: congruence.checkStrictlyPositiveNumber(self.Re, "Re")
                if not self.mix_function==1: congruence.checkPositiveNumber(self.mix, "mix")
                if not self.b_function==1: congruence.checkStrictlyPositiveNumber(self.b, "b")

                self.fit_global_parameters.strain_parameters = [KrivoglazWilkensModel(rho=self.populate_parameter("rho", KrivoglazWilkensModel.get_parameters_prefix()),
                                                                                      Re=self.populate_parameter("Re", KrivoglazWilkensModel.get_parameters_prefix()),
                                                                                      Ae=self.populate_parameter("Ae", KrivoglazWilkensModel.get_parameters_prefix()),
                                                                                      Be=self.populate_parameter("Be", KrivoglazWilkensModel.get_parameters_prefix()),
                                                                                      As=self.populate_parameter("As", KrivoglazWilkensModel.get_parameters_prefix()),
                                                                                      Bs=self.populate_parameter("Bs", KrivoglazWilkensModel.get_parameters_prefix()),
                                                                                      mix=self.populate_parameter("mix", KrivoglazWilkensModel.get_parameters_prefix()),
                                                                                      b=self.populate_parameter("b", KrivoglazWilkensModel.get_parameters_prefix()))]
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
                if not isinstance(self.fit_global_parameters.strain_parameters[0], KrivoglazWilkensModel):
                    raise Exception("Only 1 Strain Model is allowed in a line of fit: it should be branched before")

                if self.fit_global_parameters.strain_parameters[0].rho is None and \
                   self.fit_global_parameters.strain_parameters[0].Re is None and \
                   self.fit_global_parameters.strain_parameters[0].mix is None and \
                   self.fit_global_parameters.strain_parameters[0].mix is None:
                    self.populate_fields("Ae",  self.fit_global_parameters.strain_parameters[0].Ae, value_only=False)
                    self.populate_fields("Be",  self.fit_global_parameters.strain_parameters[0].Be, value_only=False)
                    self.populate_fields("As",  self.fit_global_parameters.strain_parameters[0].As, value_only=False)
                    self.populate_fields("Bs",  self.fit_global_parameters.strain_parameters[0].Bs, value_only=False)
                else:
                    self.populate_fields("rho", self.fit_global_parameters.strain_parameters[0].rho)
                    self.populate_fields("Re",  self.fit_global_parameters.strain_parameters[0].Re)
                    self.populate_fields("Ae",  self.fit_global_parameters.strain_parameters[0].Ae)
                    self.populate_fields("Be",  self.fit_global_parameters.strain_parameters[0].Be)
                    self.populate_fields("As",  self.fit_global_parameters.strain_parameters[0].As)
                    self.populate_fields("Bs",  self.fit_global_parameters.strain_parameters[0].Bs)
                    self.populate_fields("mix", self.fit_global_parameters.strain_parameters[0].mix)
                    self.populate_fields("b",   self.fit_global_parameters.strain_parameters[0].b)

            if self.is_automatic_run:
                self.send_strain()


if __name__ == "__main__":
    a =  QApplication(sys.argv)
    ow = OWStrainKW()
    ow.show()
    a.exec_()
    ow.saveSettings()
