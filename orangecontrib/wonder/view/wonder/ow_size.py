import os, sys, numpy

from PyQt5.QtWidgets import QMessageBox, QScrollArea, QTableWidget, QApplication

from Orange.widgets.settings import Setting
from Orange.widgets import gui as orangegui

from orangecontrib.wonder.util.widgets.ow_generic_widget import OWGenericWidget
from orangecontrib.wonder.util.gui.gui_utility import gui, ShowTextDialog
from orangecontrib.wonder.util import congruence
from orangecontrib.wonder.controller.fit.fit_global_parameters import FitGlobalParameters
from orangecontrib.wonder.controller.fit.microstructure.size import SizeParameters
from orangecontrib.wonder.controller.fit.wppm_functions import Distribution, Normalization, Shape, WulffCubeFace

class OWSize(OWGenericWidget):

    name = "Size"
    description = "Define Size"
    icon = "icons/size.png"
    priority = 16

    want_main_area =  False

    shape = Setting(1)
    distribution = Setting(1)

    mu = Setting(4.0)
    mu_fixed = Setting(0)
    mu_has_min = Setting(1)
    mu_min = Setting(0.01)
    mu_has_max = Setting(0)
    mu_max = Setting(0.0)
    mu_function = Setting(0)
    mu_function_value = Setting("")

    sigma = Setting(0.5)
    sigma_fixed = Setting(0)
    sigma_has_min = Setting(1)
    sigma_min = Setting(0.01)
    sigma_has_max = Setting(1)
    sigma_max = Setting(1.0)
    sigma_function = Setting(0)
    sigma_function_value = Setting("")

    truncation = Setting(0.5)
    truncation_fixed = Setting(0)
    truncation_has_min = Setting(1)
    truncation_min = Setting(0.01)
    truncation_has_max = Setting(1)
    truncation_max = Setting(1.0)
    truncation_function = Setting(0)
    truncation_function_value = Setting("")

    cube_face = Setting(1)

    add_saxs = Setting(False)
    normalize_to = Setting(0)

    inputs = [("Fit Global Parameters", FitGlobalParameters, 'set_data')]
    outputs = [("Fit Global Parameters", FitGlobalParameters)]

    def __init__(self):
        super().__init__(show_automatic_box=True)

        main_box = gui.widgetBox(self.controlArea,
                                 "Size", orientation="vertical",
                                 width=self.CONTROL_AREA_WIDTH - 10, height=600)

        button_box = gui.widgetBox(main_box,
                                   "", orientation="horizontal",
                                   width=self.CONTROL_AREA_WIDTH-25)

        gui.button(button_box,  self, "Send Size", height=50, callback=self.send_size)

        self.cb_shape = orangegui.comboBox(main_box, self, "shape", label="Shape", items=Shape.tuple(), callback=self.set_shape, orientation="horizontal")
        self.cb_distribution = orangegui.comboBox(main_box, self, "distribution", label="Distribution", items=Distribution.tuple(), callback=self.set_distribution, orientation="horizontal")


        size_box = gui.widgetBox(main_box, "Size Parameters", orientation="vertical", width=self.CONTROL_AREA_WIDTH - 30)

        self.create_box(size_box, "mu", label="\u03bc or D", min_value=0.0, min_accepted=False)

        self.sigma_box = gui.widgetBox(size_box, "", orientation="vertical")

        self.create_box(self.sigma_box, "sigma", label="\u03c3", min_value=0.0, min_accepted=False)

        self.truncation_box = gui.widgetBox(size_box, "", orientation="vertical")

        self.create_box(self.truncation_box, "truncation", label="trunc.", min_value=0.0, min_accepted=True, max_value=1.0, max_accepted=True)

        self.cb_cube_face = orangegui.comboBox(self.truncation_box, self, "cube_face", label="Cube Face", items=WulffCubeFace.tuple(), labelWidth=300, orientation="horizontal")

        self.saxs_box = gui.widgetBox(size_box, "", orientation="vertical")

        orangegui.comboBox(self.saxs_box, self, "add_saxs", label="Add SAXS", items=["No", "Yes"], labelWidth=300, orientation="horizontal",
                           callback=self.set_add_saxs)

        self.normalize_box = gui.widgetBox(self.saxs_box, "", orientation="vertical")

        orangegui.comboBox(self.normalize_box, self, "normalize_to", label="Normalize to", items=Normalization.tuple(), labelWidth=300, orientation="horizontal")

        self.set_shape(is_init=True)

    def set_shape(self, is_init=False):
        if self.cb_distribution.currentText() == Distribution.LOGNORMAL:
            if not (self.cb_shape.currentText() == Shape.SPHERE or self.cb_shape.currentText() == Shape.WULFF):
                QMessageBox.critical(self, "Error",
                                     "Only Sphere/Wulff Solid shape is supported",
                                     QMessageBox.Ok)

                self.shape = 1
        else:
            if not self.cb_shape.currentText() == Shape.SPHERE:
                QMessageBox.critical(self, "Error",
                                     "Only Sphere shape is supported",
                                     QMessageBox.Ok)

                self.shape = 1

        self.set_distribution(is_init)

    def set_add_saxs(self):
        self.normalize_box.setVisible(self.add_saxs==1)

    def set_distribution(self, is_init=False):
        if not (self.cb_distribution.currentText() == Distribution.LOGNORMAL or \
                #self.cb_distribution.currentText() == Distribution.GAMMA or \
                self.cb_distribution.currentText() == Distribution.DELTA):
            if not is_init:
                QMessageBox.critical(self, "Error",
                                     #"Only Lognormal, Gamma and Delta distributions are supported",
                                     "Only Lognormal and Delta distributions are supported",
                                     QMessageBox.Ok)

                self.distribution = 1
        else:
            self.sigma_box.setVisible(self.cb_distribution.currentText() != Distribution.DELTA)
            self.saxs_box.setVisible(self.cb_distribution.currentText() == Distribution.DELTA)
            if self.cb_distribution.currentText() == Distribution.DELTA: self.set_add_saxs()
            self.truncation_box.setVisible(self.cb_distribution.currentText() == Distribution.LOGNORMAL and self.cb_shape.currentText() == Shape.WULFF)

    def send_size(self):
        try:
            if not self.fit_global_parameters is None:
                if not self.mu_function==1: congruence.checkStrictlyPositiveNumber(self.mu, "\u03bc or D")
                if self.cb_distribution.currentText() != Distribution.DELTA and not self.sigma_function==1:
                    congruence.checkStrictlyPositiveNumber(self.sigma, "\u03c3")
                if self.cb_distribution.currentText() == Distribution.DELTA and not self.fit_global_parameters.fit_initialization.crystal_structures[0].use_structure:
                        raise Exception("Delta Distribution cannot be used when the structural model is not activated")

                self.fit_global_parameters.size_parameters = [SizeParameters(shape=self.cb_shape.currentText(),
                                                                             distribution=self.cb_distribution.currentText(),
                                                                             mu=self.populate_parameter("mu", SizeParameters.get_parameters_prefix()),
                                                                             sigma=None if self.cb_distribution.currentText() == Distribution.DELTA else self.populate_parameter("sigma", SizeParameters.get_parameters_prefix()),
                                                                             truncation=self.populate_parameter("truncation", SizeParameters.get_parameters_prefix()) if (self.cb_distribution.currentText() == Distribution.LOGNORMAL and self.cb_shape.currentText() == Shape.WULFF) else None,
                                                                             cube_face=self.cb_cube_face.currentText() if (self.cb_distribution.currentText() == Distribution.LOGNORMAL and self.cb_shape.currentText() == Shape.WULFF) else None,
                                                                             add_saxs=self.add_saxs if self.cb_distribution.currentText() == Distribution.DELTA else False,
                                                                             normalize_to=self.normalize_to if self.cb_distribution.currentText() == Distribution.DELTA else None)]
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

            if not self.fit_global_parameters.size_parameters is None:
                size_parameters = self.fit_global_parameters.size_parameters[0]

                self.populate_fields("mu",    size_parameters.mu)
                self.populate_fields("sigma", size_parameters.sigma)

                if size_parameters.shape == Shape.WULFF:
                    self.populate_fields("truncation", size_parameters.truncation)
                    self.cb_cube_face.setCurrentText(size_parameters.cube_face)

                self.add_saxs = size_parameters.add_saxs

                if size_parameters.add_saxs:
                    self.normalize_to = size_parameters.normalize_to

                self.set_shape()
                self.set_distribution()

            if self.is_automatic_run:
                self.send_size()





if __name__ == "__main__":
    a =  QApplication(sys.argv)
    ow = OWSize()
    ow.show()
    a.exec_()
    ow.saveSettings()
