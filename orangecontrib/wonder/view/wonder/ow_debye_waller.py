import sys

from PyQt5.QtWidgets import QMessageBox, QApplication

from Orange.widgets.settings import Setting
from Orange.widgets import gui as orangegui

from orangecontrib.wonder.util.widgets.ow_generic_widget import OWGenericWidget
from orangecontrib.wonder.util.gui.gui_utility import ConfirmDialog, gui
from orangecontrib.wonder.util import congruence
from orangecontrib.wonder.controller.fit.fit_global_parameters import FitGlobalParameters
from orangecontrib.wonder.controller.fit.init.thermal_polarization_parameters import ThermalPolarizationParameters

class OWDebyeWaller(OWGenericWidget):

    name = "Debye-Waller Factor"
    description = "Define Debye-Waller Factor"
    icon = "icons/debye_waller.png"
    priority = 5

    want_main_area = False

    use_debye_waller_factor = Setting(1)

    debye_waller_factor = Setting(0.0)
    debye_waller_factor_fixed = Setting(0)
    debye_waller_factor_has_min = Setting(0)
    debye_waller_factor_min = Setting(0.0)
    debye_waller_factor_has_max = Setting(0)
    debye_waller_factor_max = Setting(0.0)
    debye_waller_factor_function = Setting(0)
    debye_waller_factor_function_value = Setting("")

    inputs = [("Fit Global Parameters", FitGlobalParameters, 'set_data')]
    outputs = [("Fit Global Parameters", FitGlobalParameters)]

    def __init__(self):
        super().__init__(show_automatic_box=True)

        main_box = gui.widgetBox(self.controlArea,
                                 "Thermal Properties Setting", orientation="vertical",
                                 width=self.CONTROL_AREA_WIDTH - 10, height=300)


        button_box = gui.widgetBox(main_box,
                                   "", orientation="horizontal",
                                   width=self.CONTROL_AREA_WIDTH-25)

        gui.button(button_box, self, "Send Debye-Waller Parameters", height=50, callback=self.send_debye_waller)

        box = gui.widgetBox(main_box,
                            "Debye-Waller Factor", orientation="vertical",
                            width=self.CONTROL_AREA_WIDTH - 30)

        orangegui.comboBox(box, self, "use_debye_waller_factor", label="Calculate", items=["No", "Yes"], labelWidth=250, orientation="horizontal", callback=self.set_dw)

        self.box_dw       = gui.widgetBox(box, "", orientation="vertical", width=self.CONTROL_AREA_WIDTH - 30, height=30)
        self.box_dw_empty = gui.widgetBox(box, "", orientation="vertical", width=self.CONTROL_AREA_WIDTH - 30, height=30)

        self.create_box(self.box_dw, "debye_waller_factor", "B [Å-2]")

        self.set_dw()


    def set_dw(self):
        self.box_dw.setVisible(self.use_debye_waller_factor==1)
        self.box_dw_empty.setVisible(self.use_debye_waller_factor==0)

    def send_debye_waller(self):
        try:
            if not self.fit_global_parameters is None:
                send_data = True

                if self.use_debye_waller_factor == 1 and not self.debye_waller_factor_function==1:
                    congruence.checkStrictlyPositiveNumber(self.debye_waller_factor, "B")

                    if self.fit_global_parameters.fit_initialization.crystal_structures is None:
                        raise ValueError("Add Crystal Structure(s) before this widget")

                    if not self.fit_global_parameters.fit_initialization.crystal_structures[0].use_structure:
                        send_data = ConfirmDialog.confirmed(parent=self, message="Debye-Waller factor is better refined when the structural model is activated.\nProceed anyway?")

                if send_data:
                    debye_waller_factor  = None if self.use_debye_waller_factor==0 else self.populate_parameter("debye_waller_factor", ThermalPolarizationParameters.get_parameters_prefix())
                    if not debye_waller_factor is None: debye_waller_factor.rescale(0.01) # CONVERSIONE from A-2 to nm-2

                    if self.fit_global_parameters.fit_initialization.thermal_polarization_parameters is None:
                        self.fit_global_parameters.fit_initialization.thermal_polarization_parameters = [ThermalPolarizationParameters(debye_waller_factor=debye_waller_factor)]
                    else:
                        self.fit_global_parameters.fit_initialization.thermal_polarization_parameters[0].debye_waller_factor = debye_waller_factor

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

            if not self.fit_global_parameters.fit_initialization.thermal_polarization_parameters is None:
                if not self.fit_global_parameters.fit_initialization.thermal_polarization_parameters[0].debye_waller_factor is None:

                    self.use_debye_waller_factor = 1

                    debye_waller_factor = self.fit_global_parameters.fit_initialization.thermal_polarization_parameters[0].debye_waller_factor.duplicate()
                    debye_waller_factor.rescale(100) # CONVERSIONE from nm-2 to A-2

                    self.populate_fields("debye_waller_factor", debye_waller_factor)

            self.set_dw()

            if self.is_automatic_run:
                self.send_debye_waller()



if __name__ == "__main__":
    a = QApplication(sys.argv)
    ow = OWDebyeWaller()
    ow.show()
    a.exec_()
    ow.saveSettings()
