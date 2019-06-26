import os, sys, numpy

from PyQt5.QtWidgets import QMessageBox, QScrollArea, QTableWidget, QApplication


from Orange.widgets.settings import Setting
from Orange.widgets import gui as orangegui

from orangecontrib.wonder.util.widgets.ow_generic_widget import OWGenericWidget
from orangecontrib.wonder.util.gui.gui_utility import gui
from orangecontrib.wonder.controller.fit.fit_global_parameters import FitGlobalParameters
from orangecontrib.wonder.controller.fit.instrument.background_parameters import ExpDecayBackground


class OWExpDecayBackground(OWGenericWidget):

    name = "ExpDecay Background"
    description = "Define ExpDecay background"
    icon = "icons/expdecay_background.png"
    priority = 11

    want_main_area =  False

    a0 = Setting(0.0)
    b0 = Setting(0.0)
    a1 = Setting(0.0)
    b1 =  Setting(0.0)
    a2 =  Setting(0.0)
    b2 =  Setting(0.0)

    a0_fixed = Setting(0)
    b0_fixed = Setting(0)
    a1_fixed = Setting(0)
    b1_fixed = Setting(0)
    a2_fixed = Setting(0)
    b2_fixed = Setting(0)

    a0_has_min = Setting(0)
    b0_has_min = Setting(0)
    a1_has_min = Setting(0)
    b1_has_min = Setting(0)
    a2_has_min = Setting(0)
    b2_has_min = Setting(0)

    a0_min = Setting(0.0)
    b0_min = Setting(0.0)
    a1_min = Setting(0.0)
    b1_min = Setting(0.0)
    a2_min = Setting(0.0)
    b2_min = Setting(0.0)

    a0_has_max = Setting(0)
    b0_has_max = Setting(0)
    a1_has_max = Setting(0)
    b1_has_max = Setting(0)
    a2_has_max = Setting(0)
    b2_has_max = Setting(0)

    a0_max = Setting(0.0)
    b0_max = Setting(0.0)
    a1_max = Setting(0.0)
    b1_max = Setting(0.0)
    a2_max = Setting(0.0)
    b2_max = Setting(0.0)

    a0_function = Setting(0)
    b0_function = Setting(0)
    a1_function = Setting(0)
    b1_function = Setting(0)
    a2_function = Setting(0)
    b2_function = Setting(0)

    a0_function_value = Setting("")
    b0_function_value = Setting("")
    a1_function_value = Setting("")
    b1_function_value = Setting("")
    a2_function_value = Setting("")
    b2_function_value = Setting("")

    inputs = [("Fit Global Parameters", FitGlobalParameters, 'set_data')]
    outputs = [("Fit Global Parameters", FitGlobalParameters)]

    def __init__(self):
        super().__init__(show_automatic_box=True)

        main_box = gui.widgetBox(self.controlArea,
                                 "Instrumental Profile", orientation="vertical",
                                 width=self.CONTROL_AREA_WIDTH - 10, height=600)


        button_box = gui.widgetBox(main_box,
                                   "", orientation="horizontal",
                                   width=self.CONTROL_AREA_WIDTH-25)

        gui.button(button_box,  self, "Send Background", height=50, callback=self.send_background)

        chebyshev_box = gui.widgetBox(main_box,
                                 "Chebyshev Parameters", orientation="vertical",
                                 width=self.CONTROL_AREA_WIDTH - 30)

        self.create_box(chebyshev_box, "a0")
        self.create_box(chebyshev_box, "b0")
        self.create_box(chebyshev_box, "a1")
        self.create_box(chebyshev_box, "b1")
        self.create_box(chebyshev_box, "a2")
        self.create_box(chebyshev_box, "b2")



    def send_background(self):
        try:
            if not self.fit_global_parameters is None:
                self.fit_global_parameters.set_background_parameters([ExpDecayBackground(a0=self.populate_parameter("a0", ExpDecayBackground.get_parameters_prefix()),
                                                                                        b0=self.populate_parameter("b0", ExpDecayBackground.get_parameters_prefix()),
                                                                                        a1=self.populate_parameter("a1", ExpDecayBackground.get_parameters_prefix()),
                                                                                        b1=self.populate_parameter("b1", ExpDecayBackground.get_parameters_prefix()),
                                                                                        a2=self.populate_parameter("a2", ExpDecayBackground.get_parameters_prefix()),
                                                                                        b2=self.populate_parameter("b2", ExpDecayBackground.get_parameters_prefix()))])
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

            if not self.fit_global_parameters.background_parameters is None:
                background_parameters = self.fit_global_parameters.get_background_parameters(ExpDecayBackground.__name__)

                if not background_parameters is None:
                    self.populate_fields("a0", background_parameters[0].a0)
                    self.populate_fields("b0", background_parameters[0].b0)
                    self.populate_fields("a1", background_parameters[0].a1)
                    self.populate_fields("b1", background_parameters[0].b1)
                    self.populate_fields("a2", background_parameters[0].a2)
                    self.populate_fields("b2", background_parameters[0].b2)

            if self.is_automatic_run:
                self.send_background()



if __name__ == "__main__":
    a4 =  QApplication(sys.argv)
    ow = OWExpDecayBackground()
    ow.show()
    a.exec_()
    ow.saveSettings()
