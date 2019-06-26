import os, sys, numpy

from PyQt5.QtWidgets import QMessageBox, QApplication

from Orange.widgets.settings import Setting

from orangecontrib.wonder.util.widgets.ow_generic_widget import OWGenericWidget
from orangecontrib.wonder.util.gui.gui_utility import gui
from orangecontrib.wonder.controller.fit.fit_global_parameters import FitGlobalParameters
from orangecontrib.wonder.controller.fit.instrument.instrumental_parameters import Caglioti

class OWInstrumentalProfile(OWGenericWidget):

    name = "Instrumental Profile"
    description = "Define Instrumental Profile Parameters"
    icon = "icons/instrumental_profile.png"
    priority = 12

    want_main_area = False

    U = Setting(0.0)
    V = Setting(0.0)
    W = Setting(0.0)

    U_fixed = Setting(0)
    V_fixed = Setting(0)
    W_fixed = Setting(0)

    U_has_min = Setting(0)
    V_has_min = Setting(0)
    W_has_min = Setting(0)

    U_min = Setting(0.0)
    V_min = Setting(0.0)
    W_min = Setting(0.0)

    U_has_max = Setting(0)
    V_has_max = Setting(0)
    W_has_max = Setting(0)

    U_max = Setting(0.0)
    V_max = Setting(0.0)
    W_max = Setting(0.0)

    U_function = Setting(0)
    V_function = Setting(0)
    W_function = Setting(0)

    U_function_value = Setting("")
    V_function_value = Setting("")
    W_function_value = Setting("")

    a = Setting(0.0)
    b = Setting(0.0)
    c = Setting(0.0)

    a_fixed = Setting(0)
    b_fixed = Setting(0)
    c_fixed = Setting(0)

    a_has_min = Setting(0)
    b_has_min = Setting(0)
    c_has_min = Setting(0)

    a_min = Setting(0.0)
    b_min = Setting(0.0)
    c_min = Setting(0.0)

    a_has_max = Setting(0)
    b_has_max = Setting(0)
    c_has_max = Setting(0)

    a_max = Setting(0.0)
    b_max = Setting(0.0)
    c_max = Setting(0.0)

    a_function = Setting(0)
    b_function = Setting(0)
    c_function = Setting(0)

    a_function_value = Setting("")
    b_function_value = Setting("")
    c_function_value = Setting("")

    inputs = [("Fit Global Parameters", FitGlobalParameters, 'set_data')]
    outputs = [("Fit Global Parameters", FitGlobalParameters)]

    def __init__(self):
        super().__init__(show_automatic_box=True)

        main_box = gui.widgetBox(self.controlArea,
                                 "Instrumental Profile", orientation="vertical",
                                 width=self.CONTROL_AREA_WIDTH - 10, height=300)


        button_box = gui.widgetBox(main_box,
                                   "", orientation="horizontal",
                                   width=self.CONTROL_AREA_WIDTH-25)

        gui.button(button_box,  self, "Send Instrumental Profile", height=50, callback=self.send_intrumental_profile)

        caglioti_box_1 = gui.widgetBox(main_box,
                                 "Caglioti's FWHM", orientation="vertical",
                                 width=self.CONTROL_AREA_WIDTH - 30)
        
        caglioti_box_2 = gui.widgetBox(main_box,
                                 "Caglioti's \u03b7", orientation="vertical",
                                 width=self.CONTROL_AREA_WIDTH - 30)

        self.create_box(caglioti_box_1, "U")
        self.create_box(caglioti_box_1, "V")
        self.create_box(caglioti_box_1, "W")
        self.create_box(caglioti_box_2, "a")
        self.create_box(caglioti_box_2, "b")
        self.create_box(caglioti_box_2, "c")


    def send_intrumental_profile(self):
        try:
            if not self.fit_global_parameters is None:

                self.fit_global_parameters.instrumental_parameters = [Caglioti(U=self.populate_parameter("U", Caglioti.get_parameters_prefix()),
                                                                               V=self.populate_parameter("V", Caglioti.get_parameters_prefix()),
                                                                               W=self.populate_parameter("W", Caglioti.get_parameters_prefix()),
                                                                               a=self.populate_parameter("a", Caglioti.get_parameters_prefix()),
                                                                               b=self.populate_parameter("b", Caglioti.get_parameters_prefix()),
                                                                               c=self.populate_parameter("c", Caglioti.get_parameters_prefix()))]
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

            if not self.fit_global_parameters.instrumental_parameters is None:
                self.populate_fields("U", self.fit_global_parameters.instrumental_parameters[0].U)
                self.populate_fields("V", self.fit_global_parameters.instrumental_parameters[0].V)
                self.populate_fields("W", self.fit_global_parameters.instrumental_parameters[0].W)
                self.populate_fields("a", self.fit_global_parameters.instrumental_parameters[0].a)
                self.populate_fields("b", self.fit_global_parameters.instrumental_parameters[0].b)
                self.populate_fields("c", self.fit_global_parameters.instrumental_parameters[0].c)

            if self.is_automatic_run:
                self.send_intrumental_profile()



if __name__ == "__main__":
    a = QApplication(sys.argv)
    ow = OWInstrumentalProfile()
    ow.show()
    a.exec_()
    ow.saveSettings()
