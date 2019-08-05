import sys, numpy, os

from PyQt5.QtWidgets import QMessageBox, QScrollArea, QApplication, QTableWidget, QHeaderView, QAbstractItemView, QTableWidgetItem, QFileDialog
from PyQt5.QtCore import Qt, QMutex
from PyQt5.QtGui import QColor, QFont, QTextCursor, QIntValidator

from silx.gui.plot.PlotWindow import PlotWindow
from silx.gui.plot.LegendSelector import LegendsDockWidget
from silx.gui import qt

from Orange.widgets.settings import Setting
from Orange.widgets import gui as orangegui

from orangecontrib.wonder.util.widgets.ow_generic_widget import OWGenericWidget, OW_IS_DEVELOP
from orangecontrib.wonder.util.gui.gui_utility import gui, ConfirmDialog, EmittingStream


from orangecontrib.wonder.controller.fit.fitter_factory import FitterFactory, FitterName

from orangecontrib.wonder.util import congruence
from orangecontrib.wonder.controller.fit.fit_parameter import PARAM_HWMAX, PARAM_HWMIN
from orangecontrib.wonder.controller.fit.fit_global_parameters import FitGlobalParameters, FreeOutputParameters
from orangecontrib.wonder.controller.fit.init.thermal_polarization_parameters import ThermalPolarizationParameters
from orangecontrib.wonder.controller.fit.instrument.instrumental_parameters import SpecimenDisplacement
from orangecontrib.wonder.controller.fit.instrument.instrumental_parameters import Lab6TanCorrection
from orangecontrib.wonder.controller.fit.microstructure.strain import InvariantPAH, KrivoglazWilkensModel
from orangecontrib.wonder.controller.fit.microstructure.size import Distribution
from orangecontrib.wonder.controller.fit.wppm_functions import caglioti_fwhm, caglioti_eta, delta_two_theta_lab6, \
    integral_breadth_instrumental_function, integral_breadth_size_lognormal, integral_breadth_size_delta, \
    integral_breadth_strain_invariant_function_pah, integral_breadth_strain_krivoglaz_wilkens


class OWFitter(OWGenericWidget):
    name = "Fitter"
    description = "Fitter"
    icon = "icons/fit.png"
    priority = 60

    want_main_area = True
    standard_output = sys.stdout

    if OW_IS_DEVELOP:
        fitter_name = Setting(1)
    else:
        fitter_name = Setting(0)

    n_iterations = Setting(5)
    is_incremental = Setting(1)
    current_iteration = 0
    free_output_parameters_text = Setting("")
    save_file_name = Setting("fit_output.dat")

    is_interactive = Setting(1)

    show_wss_gof = Setting(1)
    show_ipf = Setting(1)
    show_shift = Setting(1)
    show_size = Setting(1)
    show_warren = Setting(1)
    show_integral_breadth = Setting(1)

    horizontal_headers = ["Name", "Value", "Min", "Max", "Fixed", "Function", "Expression", "e.s.d."]

    inputs = [("Fit Global Parameters", FitGlobalParameters, 'set_data')]
    outputs = [("Fit Global Parameters", FitGlobalParameters)]

    fit_global_parameters = None
    initial_fit_global_parameters = None
    fitted_fit_global_parameters = None
    current_wss = []
    current_gof = []

    stop_fit = False
    fit_running = False

    thread_exception = None

    twotheta_ipf = numpy.arange(0.5, 120.0, 0.5)
    theta_ipf_deg = 0.5*twotheta_ipf
    theta_ipf_radians = numpy.radians(theta_ipf_deg)

    fwhm_autoscale = Setting(1)
    fwhm_xmin = Setting(0.0)
    fwhm_xmax = Setting(150.0)
    fwhm_ymin = Setting(0.0)
    fwhm_ymax = Setting(1.0)

    eta_autoscale = Setting(1)
    eta_xmin = Setting(0.0)
    eta_xmax = Setting(150.0)
    eta_ymin = Setting(0.0)
    eta_ymax = Setting(1.0)

    lab6_autoscale = Setting(1)
    lab6_xmin = Setting(0.0)
    lab6_xmax = Setting(150.0)
    lab6_ymin = Setting(-1.0)
    lab6_ymax = Setting(1.0)

    # accessories

    text_size = None
    annotations_ib = None

    def __fix_flags(self):
        self.is_incremental = OWGenericWidget.fix_flag(self.is_incremental)
        self.is_interactive = OWGenericWidget.fix_flag(self.is_interactive)
        self.show_wss_gof = OWGenericWidget.fix_flag(self.show_wss_gof)
        self.show_ipf = OWGenericWidget.fix_flag(self.show_ipf)
        self.show_shift = OWGenericWidget.fix_flag(self.show_shift)
        self.show_size = OWGenericWidget.fix_flag(self.show_size)
        self.show_warren = OWGenericWidget.fix_flag(self.show_warren)
        self.show_integral_breadth = OWGenericWidget.fix_flag(self.show_integral_breadth)
        self.fwhm_autoscale = OWGenericWidget.fix_flag(self.fwhm_autoscale)
        self.eta_autoscale = OWGenericWidget.fix_flag(self.eta_autoscale)
        self.lab6_autoscale = OWGenericWidget.fix_flag(self.lab6_autoscale)

    def __init__(self):
        super().__init__(show_automatic_box=True)

        self.__fix_flags()

        main_box = gui.widgetBox(self.controlArea, "Fitter Setting", orientation="vertical", width=self.CONTROL_AREA_WIDTH)

        button_box = gui.widgetBox(main_box, "", orientation="vertical", width=self.CONTROL_AREA_WIDTH-15, height=70)

        button_box_1 = gui.widgetBox(button_box, "", orientation="horizontal")

        self.fit_button = gui.button(button_box_1,  self, "Fit", height=35, callback=self.do_fit)
        self.fit_button.setStyleSheet("color: #252468")
        font = QFont(self.fit_button.font())
        font.setBold(True)
        font.setPixelSize(18)
        self.fit_button.setFont(font)

        self.stop_fit_button = gui.button(button_box_1,  self, "STOP", height=35, callback=self.stop_fit)
        self.stop_fit_button.setStyleSheet("color: red")
        font = QFont(self.stop_fit_button.font())
        font.setBold(True)
        font.setItalic(True)
        self.stop_fit_button.setFont(font)

        button_box_2 = gui.widgetBox(button_box, "", orientation="horizontal")

        gui.button(button_box_2,  self, "Send Current Fit", height=35, callback=self.send_current_fit)
        gui.button(button_box_2,  self, "Save Data", height=35, callback=self.save_data)

        orangegui.separator(main_box)

        self.cb_fitter = orangegui.comboBox(main_box, self, "fitter_name", label="Fit algorithm", items=FitterName.tuple(), orientation="horizontal")

        iteration_box = gui.widgetBox(main_box, "", orientation="horizontal", width=250)

        gui.lineEdit(iteration_box, self, "n_iterations", "Nr. Iterations", labelWidth=80, valueType=int, validator=QIntValidator())
        orangegui.checkBox(iteration_box, self, "is_incremental", "Incremental", callback=self.set_incremental)

        self.was_incremental = self.is_incremental

        iteration_box = gui.widgetBox(main_box, "", orientation="vertical", width=250)

        self.le_current_iteration = gui.lineEdit(iteration_box, self, "current_iteration", "Current Iteration", labelWidth=120, valueType=int, orientation="horizontal")
        self.le_current_iteration.setReadOnly(True)
        self.le_current_iteration.setStyleSheet("background-color: #FAFAB0; color: #252468")
        font = QFont(self.le_current_iteration.font())
        font.setBold(True)
        self.le_current_iteration.setFont(font)

        orangegui.separator(main_box)

        self.plot_box = gui.widgetBox(main_box, "Plotting Options", orientation="vertical", width=self.CONTROL_AREA_WIDTH-20)

        self.cb_interactive = orangegui.checkBox(self.plot_box, self, "is_interactive", "Update plots while fitting:", callback=self.set_interactive)
        orangegui.separator(self.plot_box, height=8)

        self.cb_show_wss_gof           = orangegui.checkBox(self.plot_box, self, "show_wss_gof", "W.S.S. and G.o.F." )
        self.cb_show_ipf               = orangegui.checkBox(self.plot_box, self, "show_ipf", "Instrumental Profile")
        self.cb_show_shift             = orangegui.checkBox(self.plot_box, self, "show_shift", "Calibration Shift")
        self.cb_show_size              = orangegui.checkBox(self.plot_box, self, "show_size", "Size Distribution")
        self.cb_show_warren            = orangegui.checkBox(self.plot_box, self, "show_warren", "Warren's Plot")
        self.cb_show_integral_breadth  = orangegui.checkBox(self.plot_box, self, "show_integral_breadth", "Integral Breadth")

        self.set_interactive()

        tab_free_out = gui.widgetBox(main_box, "Free Output Parameters", orientation="vertical")

        self.scrollarea_free_out = QScrollArea(tab_free_out)
        self.scrollarea_free_out.setMinimumWidth(self.CONTROL_AREA_WIDTH-55)
        self.scrollarea_free_out.setMaximumHeight(170)

        def write_text():
            self.free_output_parameters_text = self.text_area_free_out.toPlainText()

        self.text_area_free_out = gui.textArea(height=1000, width=1000, readOnly=False)
        self.text_area_free_out.setText(self.free_output_parameters_text)
        self.text_area_free_out.textChanged.connect(write_text)

        self.scrollarea_free_out.setWidget(self.text_area_free_out)
        self.scrollarea_free_out.setWidgetResizable(1)

        tab_free_out.layout().addWidget(self.scrollarea_free_out, alignment=Qt.AlignHCenter)

        self.tabs = gui.tabWidget(self.mainArea)

        self.tab_fit_in  = gui.createTabPage(self.tabs, "Fit Input Parameters")
        self.tab_plot    = gui.createTabPage(self.tabs, "Plots")
        self.tab_fit_out = gui.createTabPage(self.tabs, "Fit Output Parameters")

        self.tabs_plot = gui.tabWidget(self.tab_plot)

        self.tab_plot_fit_data = gui.createTabPage(self.tabs_plot, "Fit")
        self.tab_plot_fit_wss  = gui.createTabPage(self.tabs_plot, "W.S.S.")
        self.tab_plot_fit_gof  = gui.createTabPage(self.tabs_plot, "G.o.F.")
        self.tab_plot_ipf   = gui.createTabPage(self.tabs_plot,  "Instrumental Profile")
        self.tab_plot_size   = gui.createTabPage(self.tabs_plot, "Size Distribution")
        self.tab_plot_strain = gui.createTabPage(self.tabs_plot, "Warren's Plot")
        self.tab_plot_integral_breadth = gui.createTabPage(self.tabs_plot, "Integral Breadth")

        self.std_output = gui.textArea(height=100, width=800)
        self.std_output.setStyleSheet("font-family: Courier, monospace;")

        out_box = gui.widgetBox(self.mainArea, "System Output", addSpace=False, orientation="horizontal")
        out_box.layout().addWidget(self.std_output)

        self.tabs_plot_fit_data = gui.tabWidget(self.tab_plot_fit_data)
        self.tabs_plot_ipf = gui.tabWidget(self.tab_plot_ipf)
        self.tab_plot_fwhm = gui.createTabPage(self.tabs_plot_ipf, "Caglioti's FWHM")
        self.tab_plot_eta  = gui.createTabPage(self.tabs_plot_ipf, "Caglioti's \u03b7")
        self.tab_plot_lab6 = gui.createTabPage(self.tabs_plot_ipf, "LaB6 Tan Correction")

        self.__build_plot_fit()

        self.plot_fit_wss = PlotWindow()
        self.plot_fit_wss.setDefaultPlotLines(True)
        self.plot_fit_wss.setActiveCurveColor(color="#00008B")
        self.plot_fit_wss.setGraphXLabel("Iteration")
        self.plot_fit_wss.setGraphYLabel("WSS")

        self.tab_plot_fit_wss.layout().addWidget(self.plot_fit_wss)

        self.plot_fit_gof = PlotWindow()
        self.plot_fit_gof.setDefaultPlotLines(True)
        self.plot_fit_gof.setActiveCurveColor(color="#00008B")
        self.plot_fit_gof.setGraphXLabel("Iteration")
        self.plot_fit_gof.setGraphYLabel("GOF")

        self.tab_plot_fit_gof.layout().addWidget(self.plot_fit_gof)

        self.plot_size = PlotWindow()
        self.plot_size.setDefaultPlotLines(True)
        self.plot_size.setActiveCurveColor(color="#00008B")
        self.plot_size.setGraphTitle("Crystalline Domains Size Distribution")
        self.plot_size.setGraphXLabel(r"D [nm]")
        self.plot_size.setGraphYLabel("Frequency")

        self.tab_plot_size.layout().addWidget(self.plot_size)

        self.plot_strain = PlotWindow(control=True)
        legends_dock_widget = LegendsDockWidget(plot=self.plot_strain)
        self.plot_strain._legendsDockWidget = legends_dock_widget
        self.plot_strain._dockWidgets.append(legends_dock_widget)
        self.plot_strain.addDockWidget(qt.Qt.RightDockWidgetArea, legends_dock_widget)
        self.plot_strain._legendsDockWidget.setFixedWidth(120)
        self.plot_strain.getLegendsDockWidget().show()

        self.plot_strain.setDefaultPlotLines(True)
        self.plot_strain.setActiveCurveColor(color="#00008B")
        self.plot_strain.setGraphTitle("Warren's plot")
        self.plot_strain.setGraphXLabel(r"L [nm]")
        self.plot_strain.setGraphYLabel("$\sqrt{<{\Delta}L^{2}>}$ [nm]")

        self.tab_plot_strain.layout().addWidget(self.plot_strain)

        self.tabs_plot_integral_breadth = gui.tabWidget(self.tab_plot_integral_breadth)

        self.__build_plot_integral_breadth()

        box = gui.widgetBox(self.tab_plot_fwhm, "", orientation="horizontal")

        boxl = gui.widgetBox(box, "", orientation="vertical")
        boxr = gui.widgetBox(box, "", orientation="vertical", width=150)

        def set_fwhm_autoscale():
            self.le_fwhm_xmin.setEnabled(self.fwhm_autoscale==0)
            self.le_fwhm_xmax.setEnabled(self.fwhm_autoscale==0)
            self.le_fwhm_ymin.setEnabled(self.fwhm_autoscale==0)
            self.le_fwhm_ymax.setEnabled(self.fwhm_autoscale==0)

        orangegui.checkBox(boxr, self, "fwhm_autoscale", "Autoscale", callback=set_fwhm_autoscale)

        def refresh_caglioti_fwhm():
            if not self.fitted_fit_global_parameters.instrumental_parameters is None:
                index = 0
                instrumental_parameters = self.fitted_fit_global_parameters.instrumental_parameters[index]
                self.__refresh_caglioti_fwhm(instrumental_parameters)

        self.le_fwhm_xmin = gui.lineEdit(boxr, self, "fwhm_xmin", "2\u03b8 min", labelWidth=70, valueType=float)
        self.le_fwhm_xmax = gui.lineEdit(boxr, self, "fwhm_xmax", "2\u03b8 max", labelWidth=70, valueType=float)
        self.le_fwhm_ymin = gui.lineEdit(boxr, self, "fwhm_ymin", "FWHM min", labelWidth=70, valueType=float)
        self.le_fwhm_ymax = gui.lineEdit(boxr, self, "fwhm_ymax", "FWHM max", labelWidth=70, valueType=float)
        gui.button(boxr, self, "Refresh", height=40, callback=refresh_caglioti_fwhm)

        set_fwhm_autoscale()

        self.plot_ipf_fwhm = PlotWindow()
        self.plot_ipf_fwhm.setDefaultPlotLines(True)
        self.plot_ipf_fwhm.setActiveCurveColor(color="#00008B")
        self.plot_ipf_fwhm.setGraphXLabel("2\u03b8 (deg)")
        self.plot_ipf_fwhm.setGraphYLabel("FWHM (deg)")

        boxl.layout().addWidget(self.plot_ipf_fwhm)

        box = gui.widgetBox(self.tab_plot_eta, "", orientation="horizontal")

        boxl = gui.widgetBox(box, "", orientation="vertical")
        boxr = gui.widgetBox(box, "", orientation="vertical", width=150)

        def set_eta_autoscale():
            self.le_eta_xmin.setEnabled(self.eta_autoscale==0)
            self.le_eta_xmax.setEnabled(self.eta_autoscale==0)
            self.le_eta_ymin.setEnabled(self.eta_autoscale==0)
            self.le_eta_ymax.setEnabled(self.eta_autoscale==0)

        orangegui.checkBox(boxr, self, "eta_autoscale", "Autoscale", callback=set_eta_autoscale)

        def refresh_caglioti_eta():
            if not self.fitted_fit_global_parameters.instrumental_parameters is None:
                index = 0
                instrumental_parameters = self.fitted_fit_global_parameters.instrumental_parameters[index]
                self.__refresh_caglioti_eta(instrumental_parameters)

        self.le_eta_xmin = gui.lineEdit(boxr, self, "eta_xmin", "2\u03b8 min", labelWidth=70, valueType=float)
        self.le_eta_xmax = gui.lineEdit(boxr, self, "eta_xmax", "2\u03b8 max", labelWidth=70, valueType=float)
        self.le_eta_ymin = gui.lineEdit(boxr, self, "eta_ymin", "\u03b7 min", labelWidth=70, valueType=float)
        self.le_eta_ymax = gui.lineEdit(boxr, self, "eta_ymax", "\u03b7 max", labelWidth=70, valueType=float)
        gui.button(boxr, self, "Refresh", height=40, callback=refresh_caglioti_eta)

        set_eta_autoscale()

        self.plot_ipf_eta = PlotWindow()
        self.plot_ipf_eta.setDefaultPlotLines(True)
        self.plot_ipf_eta.setActiveCurveColor(color="#00008B")
        self.plot_ipf_eta.setGraphXLabel("2\u03b8 (deg)")
        self.plot_ipf_eta.setGraphYLabel("\u03b7")

        boxl.layout().addWidget(self.plot_ipf_eta)

        box = gui.widgetBox(self.tab_plot_lab6, "", orientation="horizontal")

        boxl = gui.widgetBox(box, "", orientation="vertical")
        boxr = gui.widgetBox(box, "", orientation="vertical", width=150)

        def set_lab6_autoscale():
            self.le_lab6_xmin.setEnabled(self.lab6_autoscale==0)
            self.le_lab6_xmax.setEnabled(self.lab6_autoscale==0)
            self.le_lab6_ymin.setEnabled(self.lab6_autoscale==0)
            self.le_lab6_ymax.setEnabled(self.lab6_autoscale==0)

        orangegui.checkBox(boxr, self, "lab6_autoscale", "Autoscale", callback=set_lab6_autoscale)

        def refresh_lab6():
            shift_parameters = self.fitted_fit_global_parameters.get_shift_parameters(Lab6TanCorrection.__name__)

            if not shift_parameters is None: self.__refresh_lab6(shift_parameters)

        self.le_lab6_xmin = gui.lineEdit(boxr, self, "lab6_xmin", "2\u03b8 min", labelWidth=70, valueType=float)
        self.le_lab6_xmax = gui.lineEdit(boxr, self, "lab6_xmax", "2\u03b8 max", labelWidth=70, valueType=float)
        self.le_lab6_ymin = gui.lineEdit(boxr, self, "lab6_ymin", "\u0394(2\u03b8) min", labelWidth=70, valueType=float)
        self.le_lab6_ymax = gui.lineEdit(boxr, self, "lab6_ymax", "\u0394(2\u03b8) max", labelWidth=70, valueType=float)
        gui.button(boxr, self, "Refresh", height=40, callback=refresh_lab6)

        set_lab6_autoscale()

        self.plot_ipf_lab6 = PlotWindow()
        self.plot_ipf_lab6.setDefaultPlotLines(True)
        self.plot_ipf_lab6.setActiveCurveColor(color="#00008B")
        self.plot_ipf_lab6.setGraphXLabel("2\u03b8 (deg)")
        self.plot_ipf_lab6.setGraphYLabel("\u0394(2\u03b8) (deg)")

        boxl.layout().addWidget(self.plot_ipf_lab6)

        # -------------------

        self.table_fit_in = self.__create_table_widget(is_output=False)
        self.tab_fit_in.layout().addWidget(self.table_fit_in, alignment=Qt.AlignHCenter)

        # -------------------

        self.table_fit_out = self.__create_table_widget()
        self.tab_fit_out.layout().addWidget(self.table_fit_out, alignment=Qt.AlignHCenter)

    def write_stdout(self, text):
        cursor = self.std_output.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.std_output.setTextCursor(cursor)
        self.std_output.ensureCursorVisible()

    def set_incremental(self):
        if self.is_incremental == 0:
            if self.was_incremental == 1:
                answer = QMessageBox.question(self, 'Set Incremental', "Unchecking incremental mode will make the fit begin from initially received parameters, continue?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

                if (answer == QMessageBox.No):
                    self.is_incremental = 1

        self.was_incremental = self.is_incremental

    def set_interactive(self):
        self.cb_show_wss_gof.setEnabled(self.is_interactive==1)

        if not self.fit_global_parameters is None:
            if self.is_interactive == 1:
                self.cb_show_ipf.setEnabled(not self.fit_global_parameters.instrumental_parameters is None)
                self.cb_show_shift.setEnabled(not self.fit_global_parameters.get_shift_parameters(Lab6TanCorrection.__name__) is None)
                self.cb_show_size.setEnabled(not self.fit_global_parameters.size_parameters is None)
                self.cb_show_warren.setEnabled(not self.fit_global_parameters.strain_parameters is None)
                self.cb_show_integral_breadth.setEnabled(not (self.fit_global_parameters.strain_parameters is None and
                                                              self.fit_global_parameters.size_parameters is None and
                                                              self.fit_global_parameters.instrumental_parameters is None))
            else:
                self.cb_show_ipf.setEnabled(False)
                self.cb_show_shift.setEnabled(False)
                self.cb_show_size.setEnabled(False)
                self.cb_show_warren.setEnabled(False)
                self.cb_show_integral_breadth.setEnabled(False)
        else:
            self.cb_show_ipf.setEnabled(self.is_interactive==1)
            self.cb_show_shift.setEnabled(self.is_interactive==1)
            self.cb_show_size.setEnabled(self.is_interactive==1)
            self.cb_show_warren.setEnabled(self.is_interactive==1)
            self.cb_show_integral_breadth.setEnabled(self.is_interactive==1)

    def set_plot_options_enabled(self, enabled):
        self.fit_button.setEnabled(enabled)
        self.plot_box.setEnabled(enabled)
        self.plot_box.repaint()

    #####################################
    # INPUT
    #####################################

    def set_data(self, data):
        try:
            if not data is None:
                if self.fit_running: raise RuntimeError("Fit is Running: Input data are not accepted!")

                if self.is_incremental == 1 and not self.fit_global_parameters is None:
                    if not ConfirmDialog.confirmed(self, message="Warning: Fitter is in set in incremental mode, but received fit parameters will replace the already fitted ones. Do you accept them?"):
                        return

                self.current_iteration = 0

                self.fit_global_parameters = data.duplicate()
                self.initial_fit_global_parameters = data.duplicate()

                # keep existing text!
                received_free_output_parameters = self.fit_global_parameters.free_output_parameters.duplicate()

                existing_free_output_parameters = FreeOutputParameters()
                existing_free_output_parameters.parse_formulas(self.free_output_parameters_text)
                existing_free_output_parameters.append(received_free_output_parameters) # received overwrite parameters with same name

                self.text_area_free_out.setText(existing_free_output_parameters.to_python_code())

                parameters = self.fit_global_parameters.free_input_parameters.as_parameters()
                parameters.extend(self.fit_global_parameters.get_parameters())

                self.__populate_table(self.table_fit_in, parameters, is_output=False)

                self.tabs.setCurrentIndex(0)

                if self.fit_global_parameters.instrumental_parameters is None:
                    self.show_ipf = 0
                    self.cb_show_ipf.setEnabled(False)
                    self.tab_plot_ipf.setEnabled(False)
                else:
                    self.cb_show_ipf.setEnabled(True)
                    self.tab_plot_ipf.setEnabled(True)

                if self.fit_global_parameters.get_shift_parameters(Lab6TanCorrection.__name__) is None:
                    self.show_shift = 0
                    self.cb_show_shift.setEnabled(False)
                    self.tab_plot_lab6.setEnabled(False)
                else:
                    self.cb_show_shift.setEnabled(True)
                    self.tab_plot_lab6.setEnabled(True)

                if self.fit_global_parameters.size_parameters is None:
                    self.show_size = 0
                    self.cb_show_size.setEnabled(False)
                    self.tab_plot_size.setEnabled(False)
                else:
                    self.cb_show_size.setEnabled(True)
                    self.tab_plot_size.setEnabled(True)

                if self.fit_global_parameters.strain_parameters is None:
                    self.show_warren           = 0
                    self.cb_show_warren.setEnabled(False)
                    self.tab_plot_strain.setEnabled(False)
                else:
                    self.cb_show_warren.setEnabled(True)
                    self.tab_plot_strain.setEnabled(True)

                if self.fit_global_parameters.strain_parameters is None and \
                   self.fit_global_parameters.size_parameters is None and \
                   self.fit_global_parameters.instrumental_parameters is None:
                    self.show_integral_breadth = 0
                    self.cb_show_integral_breadth.setEnabled(False)
                    self.tab_plot_integral_breadth.setEnabled(False)
                else:
                    self.cb_show_integral_breadth.setEnabled(True)
                    self.tab_plot_integral_breadth.setEnabled(True)

                self.set_interactive()
                self.was_incremental = self.is_incremental
                self.__initialize_fit(is_init=True)
                self.__show_data(is_init=True)

                if self.is_automatic_run:
                    self.do_fit()
        except Exception as e:
            QMessageBox.critical(self, "Error during load",
                                 str(e),
                                 QMessageBox.Ok)

            if self.IS_DEVELOP: raise e

    def __create_table_widget(self, is_output=True):
        from PyQt5.QtWidgets import QAbstractItemView

        table_fit = QTableWidget(1, 8 if is_output else 7)
        table_fit.setMinimumWidth(780)
        table_fit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        table_fit.setAlternatingRowColors(True)
        table_fit.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        table_fit.verticalHeader().setVisible(False)
        table_fit.setHorizontalHeaderLabels(self.horizontal_headers if is_output else self.horizontal_headers[:-1])
        table_fit.setSelectionBehavior(QAbstractItemView.SelectRows)

        return table_fit

    def __add_table_item(self,
                         table_widget,
                         row_index,
                         column_index,
                         text="",
                         alignement=Qt.AlignLeft,
                         change_color=False,
                         color=QColor(255, 255, 255)):

            table_item = QTableWidgetItem(text)
            table_item.setTextAlignment(alignement)
            if change_color: table_item.setBackground(color)
            table_widget.setItem(row_index, column_index, table_item)

    def __analyze_parameter(self, parameter):
        if parameter.parameter_name == ThermalPolarizationParameters.get_parameters_prefix() + "debye_waller_factor":
            parameter = parameter.duplicate()
            parameter.rescale(100) # from nm-2 to A-2
        elif parameter.parameter_name == SpecimenDisplacement.get_parameters_prefix() + "displacement":
            parameter = parameter.duplicate()
            parameter.rescale(1e6) # from m to um

        return parameter

    def __populate_table(self, table_widget, parameters, is_output=True):
        table_widget.clear()

        row_count = table_widget.rowCount()
        for n in range(0, row_count):
            table_widget.removeRow(0)

        for index in range(0, len(parameters)):
            table_widget.insertRow(0)

        for index in range(0, len(parameters)):
            parameter = parameters[index]
            parameter = self.__analyze_parameter(parameter)
            change_color = not parameter.is_variable()

            if change_color:
                if parameter.input_parameter: color = QColor(213, 245, 227)
                elif parameter.fixed: color = QColor(190, 190, 190)
                elif parameter.output_parameter: color = QColor(242, 245, 169)
                else: color = QColor(169, 208, 245)
            else:
                color = None

            self.__add_table_item(table_widget, index, 0,
                                  parameter.parameter_name,
                                  Qt.AlignLeft, change_color, color)

            self.__add_table_item(table_widget, index, 1,
                                  str(round(0.0 if parameter.value is None else parameter.value, 6)),
                                  Qt.AlignRight, change_color, color)

            if (not parameter.is_variable()) or parameter.boundary is None: text_2 = text_3 = ""
            else:
                if parameter.boundary.min_value == PARAM_HWMIN: text_2 = ""
                else: text_2 = str(round(0.0 if parameter.boundary.min_value is None else parameter.boundary.min_value, 6))

                if parameter.boundary.max_value == PARAM_HWMAX: text_3 = ""
                else: text_3 = str(round(0.0 if parameter.boundary.max_value is None else parameter.boundary.max_value, 6))

            self.__add_table_item(table_widget, index, 2,
                                  text_2,
                                  Qt.AlignRight, change_color, color)
            self.__add_table_item(table_widget, index, 3,
                                  text_3,
                                  Qt.AlignRight, change_color, color)

            self.__add_table_item(table_widget, index, 4,
                                "" if not parameter.fixed else "\u2713",
                                  Qt.AlignCenter, change_color, color)
            self.__add_table_item(table_widget, index, 5,
                                "" if not parameter.function else "\u2713",
                                  Qt.AlignCenter, change_color, color)

            if parameter.function: text_6 = str(parameter.function_value)
            else: text_6 = ""

            self.__add_table_item(table_widget, index, 6,
                                  text_6,
                                  Qt.AlignLeft, change_color, color)

            if is_output: self.__add_table_item(table_widget, index, 7,
                                                str(round(0.0 if parameter.error is None else parameter.error, 6)),
                                                Qt.AlignRight, change_color, color)

        table_widget.setHorizontalHeaderLabels(self.horizontal_headers)
        table_widget.resizeRowsToContents()
        table_widget.setSelectionBehavior(QAbstractItemView.SelectRows)
        table_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)

    #####################################
    # FIT
    #####################################

    def do_fit(self):
        try:
            if not self.fit_global_parameters is None:
                self.set_plot_options_enabled(False)
                self.stop_fit = False

                congruence.checkStrictlyPositiveNumber(self.n_iterations, "Nr. Iterations")

                if self.fit_global_parameters.fit_initialization is None:
                    raise ValueError("Mandatory widgets (Load Data/Fit Initialization/Crystal Structure) are totally missing.")

                if self.fit_global_parameters.fit_initialization.fft_parameters is None:
                    raise ValueError("FFT parameters is missing: add the proper widget before the Fitter")

                if self.fit_global_parameters.fit_initialization.diffraction_patterns is None:
                    raise ValueError("Diffraction Pattern is missing: add the proper widget before the Fitter")

                if self.fit_global_parameters.fit_initialization.crystal_structures is None:
                    raise ValueError("Crystal Structure is missing: add the proper widget before the Fitter")

                self.__initialize_fit(is_init=False)

                initial_fit_global_parameters = self.fit_global_parameters.duplicate()

                if self.is_incremental == 1 and self.current_iteration > 0:
                    if len(initial_fit_global_parameters.get_parameters()) != len(self.fitter.fit_global_parameters.get_parameters()):
                        raise Exception("Incremental Fit is not possibile!\n\nParameters in the last fitting procedure are incompatible with the received ones")

                sys.stdout = EmittingStream(textWritten=self.write_stdout)

                self.fitted_fit_global_parameters = initial_fit_global_parameters
                self.current_running_iteration = 0

                try:
                    self.fit_thread = FitThread(self)
                    self.fit_thread.begin.connect(self.fit_begin)
                    self.fit_thread.update.connect(self.fit_update)
                    self.fit_thread.finished.connect(self.fit_completed)
                    self.fit_thread.error.connect(self.fit_error)
                    self.fit_thread.start()
                except Exception as e:
                    raise FitNotStartedException(str(e))

        except Exception as e:
            QMessageBox.critical(self, "Error",
                                 str(e),
                                 QMessageBox.Ok)

            self.set_plot_options_enabled(True)

            if self.IS_DEVELOP: raise e

        self.setStatusMessage("")
        self.progressBarFinished()

    def __initialize_fit(self, is_init=False):
        if self.is_incremental==0 or is_init:
            self.fit_global_parameters = self.initial_fit_global_parameters.duplicate()
            self.current_wss = []
            self.current_gof = []
            self.current_iteration = 0
            self.fit_data = None

        if not is_init:
            self.fit_global_parameters.set_n_max_iterations(self.n_iterations)
            self.fit_global_parameters.set_convergence_reached(False)
        else:
            sys.stdout = EmittingStream(textWritten=self.write_stdout)

            self.fitter = FitterFactory.create_fitter(fitter_name=self.cb_fitter.currentText())

        self.fit_global_parameters.free_output_parameters.parse_formulas(self.free_output_parameters_text)

        self.fitted_fit_global_parameters = self.fit_global_parameters.duplicate()
        self.fitted_fit_global_parameters.evaluate_functions()

        self.fitter.initialize(self.fitted_fit_global_parameters)

        self.fitted_patterns = self.fitter.build_fitted_diffraction_pattern(self.fitted_fit_global_parameters)

        self.tabs.setCurrentIndex(1)
        self.tabs_plot.setCurrentIndex(0)

    def stop_fit(self):
        if ConfirmDialog.confirmed(self, "Confirm STOP?"):
            self.stop_fit = True


    def send_current_fit(self):
        if not self.fit_global_parameters is None:
            self.fit_global_parameters.regenerate_parameters()
            self.send("Fit Global Parameters", self.fit_global_parameters.duplicate())

    def save_data(self):
        try:
            if hasattr(self, "fitted_patterns") and not self.fitted_patterns is None:
                file_path = QFileDialog.getSaveFileName(self, "Select File", os.path.dirname(self.save_file_name))[0]

                if not file_path is None and not file_path.strip() == "":
                    self.save_file_name=file_path

                    text = ""
                    for diffraction_pattern_index in range(len(self.fitted_patterns)):
                        fitted_pattern = self.fitted_patterns[diffraction_pattern_index]
                        diffraction_pattern = self.fit_global_parameters.fit_initialization.diffraction_patterns[diffraction_pattern_index]

                        text += "" if diffraction_pattern_index==0 else "\n"
                        text += "------------------------------------------------------------------------\n"
                        text +="DIFFRACTION PATTERN Nr. " + str(diffraction_pattern_index+1) + "\n\n"
                        text += "2Theta [deg], s [Å-1], Intensity, Fit, Residual\n"
                        text += "------------------------------------------------------------------------"

                        for index in range(0, fitted_pattern.diffraction_points_count()):
                            text += "\n" + str(fitted_pattern.get_diffraction_point(index).twotheta) + "  " + \
                                    str(fitted_pattern.get_diffraction_point(index).s) + " " + \
                                    str(diffraction_pattern.get_diffraction_point(index).intensity) + " " + \
                                    str(fitted_pattern.get_diffraction_point(index).intensity) + " " + \
                                    str(fitted_pattern.get_diffraction_point(index).error) + " "

                    file = open(self.save_file_name, "w")
                    file.write(text)
                    file.flush()
                    file.close()

                    QMessageBox.information(self,
                                            "Save Data",
                                            "Fitted data saved on file:\n" + self.save_file_name,
                                            QMessageBox.Ok)
        except Exception as e:
            QMessageBox.critical(self, "Error",
                                 str(e),
                                 QMessageBox.Ok)

            if self.IS_DEVELOP: raise e

    ##########################################
    # PLOTS
    ##########################################

    def __show_data(self, is_init=False):
        diffraction_pattern_number = self.fitted_fit_global_parameters.fit_initialization.get_diffraction_patterns_number()

        self.__refresh_fit(diffraction_pattern_number, is_init)
        self.__refresh_fit_data()
        self.__refresh_instrumental_function()
        self.__refresh_size(is_init)
        self.__refresh_strain()
        self.__refresh_integral_breadth(diffraction_pattern_number, is_init)

        self.set_interactive()

    # ------------------------------------------------------------------------

    def __refresh_fit(self, diffraction_pattern_number, is_init=False):
        if is_init:
            self.__build_plot_fit()

            self.x = numpy.full(diffraction_pattern_number, None)
            self.y = numpy.full(diffraction_pattern_number, None)

        for diffraction_pattern_index in range(diffraction_pattern_number):
            diffraction_pattern = self.fitted_fit_global_parameters.fit_initialization.diffraction_patterns[diffraction_pattern_index]
            fitted_pattern = self.fitted_patterns[diffraction_pattern_index]

            nr_points = fitted_pattern.diffraction_points_count()

            yf = numpy.zeros(nr_points)
            res = numpy.zeros(nr_points)

            if is_init:
                x = numpy.zeros(nr_points)
                y = numpy.zeros(nr_points)

                i = -1
                for point, fit in zip(diffraction_pattern.diffraction_pattern, fitted_pattern.diffraction_pattern):
                    i += 1
                    x[i]   = point.twotheta
                    y[i]   = point.intensity
                    yf[i]  = fit.intensity
                    res[i] = fit.error

                self.x[diffraction_pattern_index] = x
                self.y[diffraction_pattern_index] = y
            else:
                i = -1
                for fit in fitted_pattern.diffraction_pattern:
                    i += 1
                    yf[i]  = fit.intensity
                    res[i] = fit.error

            res = -10 + (res-numpy.max(res))

            if is_init: self.plot_fit[diffraction_pattern_index].addCurve(self.x[diffraction_pattern_index], self.y[diffraction_pattern_index], legend="data", linewidth=4, color="blue")
            self.plot_fit[diffraction_pattern_index].addCurve(self.x[diffraction_pattern_index], yf, legend="fit", color="red")
            self.plot_fit[diffraction_pattern_index].addCurve(self.x[diffraction_pattern_index], res, legend="residual", color="#2D811B")

    # ------------------------------------------------------------------------

    def __refresh_fit_data(self):
        if not self.fit_data is None and self.show_wss_gof==1:
            x = numpy.arange(1, self.current_iteration + 1)

            self.plot_fit_wss.addCurve(x, self.current_wss, legend="wss", symbol='o', color="blue")
            self.plot_fit_gof.addCurve(x, self.current_gof, legend="gof", symbol='o', color="red")


    # ------------------------------------------------------------------------

    def __refresh_instrumental_function(self, diffraction_pattern_index=0):
        if not self.fitted_fit_global_parameters.instrumental_parameters is None:
            instrumental_parameters = self.fitted_fit_global_parameters.instrumental_parameters[0 if len(self.fitted_fit_global_parameters.instrumental_parameters) == 1 else diffraction_pattern_index]

            self.__refresh_caglioti_fwhm(instrumental_parameters)
            self.__refresh_caglioti_eta(instrumental_parameters)

        shift_parameters = self.fitted_fit_global_parameters.get_shift_parameters(Lab6TanCorrection.__name__)

        if not shift_parameters is None: self.__refresh_lab6(shift_parameters)

    # ------------------------------------------------------------------------

    def __refresh_caglioti_fwhm(self, instrumental_parameters):
        if self.show_ipf==1:
            if self.fwhm_autoscale == 1:
                twotheta_fwhm = numpy.arange(0.0, 150.0, 0.5)
            else:
                twotheta_fwhm = numpy.arange(self.fwhm_xmin, self.fwhm_xmax, 0.5)

            theta_fwhm_radians = numpy.radians(0.5*twotheta_fwhm)

            y = caglioti_fwhm(instrumental_parameters.U.value,
                              instrumental_parameters.V.value,
                              instrumental_parameters.W.value,
                              theta_fwhm_radians)

            self.plot_ipf_fwhm.addCurve(twotheta_fwhm, y, legend="fwhm", color="blue")

            if self.fwhm_autoscale == 0 and self.fwhm_ymin < self.fwhm_xmax: self.plot_ipf_fwhm.setGraphYLimits(ymin=self.fwhm_ymin, ymax=self.fwhm_ymax)

    # ------------------------------------------------------------------------

    def __refresh_caglioti_eta(self, instrumental_parameters):
        if self.show_ipf==1:
            if self.eta_autoscale == 1:
                twotheta_eta = numpy.arange(0.0, 150.0, 0.5)
            else:
                twotheta_eta = numpy.arange(self.eta_xmin, self.eta_xmax, 0.5)

            theta_eta_radians = numpy.radians(0.5*twotheta_eta)

            y = caglioti_eta(instrumental_parameters.a.value,
                             instrumental_parameters.b.value,
                             instrumental_parameters.c.value,
                             theta_eta_radians)

            self.plot_ipf_eta.addCurve(twotheta_eta, y, legend="eta", color="blue")

            if self.eta_autoscale == 0 and self.eta_ymin < self.eta_xmax: self.plot_ipf_eta.setGraphYLimits(ymin=self.eta_ymin, ymax=self.eta_ymax)

    # ------------------------------------------------------------------------

    def __refresh_lab6(self, shift_parameters):
        if self.show_shift==1:
            if self.lab6_autoscale == 1:
                twotheta_lab6 = numpy.arange(0.0, 150.0, 0.5)
            else:
                twotheta_lab6 = numpy.arange(self.lab6_xmin, self.lab6_xmax, 0.5)

            theta_lab6_radians = numpy.radians(0.5*twotheta_lab6)

            y = delta_two_theta_lab6(shift_parameters[0].ax.value,
                                     shift_parameters[0].bx.value,
                                     shift_parameters[0].cx.value,
                                     shift_parameters[0].dx.value,
                                     shift_parameters[0].ex.value,
                                     theta_lab6_radians)

            self.plot_ipf_lab6.addCurve(twotheta_lab6, y, legend="lab6", color="blue")

            if self.lab6_autoscale == 0 and self.lab6_ymin < self.lab6_xmax: self.plot_ipf_lab6.setGraphYLimits(ymin=self.lab6_ymin, ymax=self.lab6_ymax)

    # ------------------------------------------------------------------------

    def __refresh_size(self, is_init=False):
        if not self.text_size is None: self.text_size.remove()

        if is_init:
            self.distribution = None

        if not self.fitted_fit_global_parameters.size_parameters is None and self.show_size==1:
            if self.current_iteration <= 1: #TO BE SURE...
                self.distribution = self.fitted_fit_global_parameters.size_parameters[0].get_distribution(auto=True)
            else:
                self.distribution = self.fitted_fit_global_parameters.size_parameters[0].get_distribution(auto=False, D_min=self.distribution.D_min, D_max=self.distribution.D_max)

            self.plot_size.addCurve(self.distribution.x, self.distribution.y, legend="distribution", color="blue")

            self.text_size = self.plot_size._backend.ax.text(numpy.max(self.distribution.x) * 0.65, numpy.max(self.distribution.y) * 0.7,
                                                             "<D>        = " + str(round(self.distribution.D_avg, 3)) + " nm\n" + \
                                                             "<D> s.w. = " + str(round(self.distribution.D_avg_surface_weighted, 3)) + " nm\n" + \
                                                             "<D> v.w. = " + str(round(self.distribution.D_avg_volume_weighted, 3)) + " nm\n" + \
                                                             "s.d.           = " + str(round(self.distribution.standard_deviation, 3)) + " nm", fontsize=12)

    # ------------------------------------------------------------------------

    def __refresh_strain(self):
        if not self.fitted_fit_global_parameters.strain_parameters is None and self.show_warren==1:
            if self.distribution is None: L_max = 20
            else: L_max = 2*self.distribution.D_avg

            x, y = self.fitted_fit_global_parameters.strain_parameters[0].get_warren_plot(1, 0, 0, L_max=L_max)
            self.plot_strain.addCurve(x, y, legend="h00", color='blue')
            _, y = self.fitted_fit_global_parameters.strain_parameters[0].get_warren_plot(1, 1, 1, L_max=L_max)
            self.plot_strain.addCurve(x, y, legend="hhh", color='red')
            _, y = self.fitted_fit_global_parameters.strain_parameters[0].get_warren_plot(1, 1, 0, L_max=L_max)
            self.plot_strain.addCurve(x, y, legend="hh0", color='green')

    # ------------------------------------------------------------------------

    def __refresh_integral_breadth(self, diffraction_pattern_number, is_init=False):
        if not self.annotations_ib is None:
            for annotations in self.annotations_ib:
                if not annotations is None:
                    for annotation in annotations: annotation.remove()

        if not (self.fitted_fit_global_parameters.strain_parameters is None and \
                self.fitted_fit_global_parameters.size_parameters is None and \
                self.fitted_fit_global_parameters.instrumental_parameters is None) and \
                self.show_integral_breadth==1:
            if is_init:
                self.__build_plot_integral_breadth()

            self.x_ib           = numpy.full(diffraction_pattern_number, None)
            self.labels_ib      = numpy.full(diffraction_pattern_number, None)
            self.annotations_ib = numpy.full(diffraction_pattern_number, None)

            for diffraction_pattern_index in range(diffraction_pattern_number):
                crystal_structure = self.fitted_fit_global_parameters.fit_initialization.crystal_structures[diffraction_pattern_index]
                incident_radiation = self.fitted_fit_global_parameters.fit_initialization.incident_radiations[0 if len(self.fitted_fit_global_parameters.fit_initialization.incident_radiations) == 1 else diffraction_pattern_index]

                wavelength = incident_radiation.wavelength.value
                lattice_parameter = crystal_structure.a.value

                nr_points = crystal_structure.get_reflections_count()

                self.x_ib[diffraction_pattern_index]      = crystal_structure.get_s_list()
                self.labels_ib[diffraction_pattern_index] = crystal_structure.get_hkl_list()

                size_parameters = None
                if not self.fitted_fit_global_parameters.size_parameters is None:
                    size_parameters = self.fitted_fit_global_parameters.size_parameters[0 if len(self.fitted_fit_global_parameters.size_parameters) == 1 else diffraction_pattern_index]

                instrumental_parameters = None
                if not self.fitted_fit_global_parameters.instrumental_parameters is None:
                    instrumental_parameters = self.fitted_fit_global_parameters.instrumental_parameters[0 if len(self.fitted_fit_global_parameters.instrumental_parameters) == 1 else diffraction_pattern_index]

                strain_parameters = None
                if not self.fitted_fit_global_parameters.strain_parameters is None:
                    strain_parameters = self.fitted_fit_global_parameters.strain_parameters[0 if len(self.fitted_fit_global_parameters.strain_parameters) == 1 else diffraction_pattern_index]

                plot_instr = not instrumental_parameters is None
                plot_size = not size_parameters is None
                plot_strain = not strain_parameters is None

                if not size_parameters is None:
                    if size_parameters.distribution == Distribution.LOGNORMAL:
                        y_ib_size = numpy.full(crystal_structure.get_reflections_count(), integral_breadth_size_lognormal(size_parameters.mu.value, size_parameters.sigma.value))
                    elif size_parameters.distribution == Distribution.DELTA:
                        y_ib_size = numpy.full(crystal_structure.get_reflections_count(), integral_breadth_size_delta(size_parameters.mu.value))
                else:
                    y_ib_size = numpy.zeros(nr_points)

                y_ib_strain = numpy.zeros(nr_points)
                y_ib_instr  = numpy.zeros(nr_points)

                i = -1
                for reflection in crystal_structure.get_reflections():
                    i += 1

                    if not strain_parameters is None:
                        if isinstance(strain_parameters, InvariantPAH):
                            y_ib_strain[i] = integral_breadth_strain_invariant_function_pah(reflection.h,
                                                                                            reflection.k,
                                                                                            reflection.l,
                                                                                            lattice_parameter,
                                                                                            strain_parameters.aa.value,
                                                                                            strain_parameters.bb.value,
                                                                                            strain_parameters.get_invariant(reflection.h,
                                                                                                                            reflection.k,
                                                                                                                            reflection.l))
                        elif isinstance(strain_parameters, KrivoglazWilkensModel):
                            y_ib_strain[i] = integral_breadth_strain_krivoglaz_wilkens(reflection.h,
                                                                                       reflection.k,
                                                                                       reflection.l,
                                                                                       lattice_parameter,
                                                                                       strain_parameters.rho.value,
                                                                                       strain_parameters.Re.value,
                                                                                       strain_parameters.Ae.value,
                                                                                       strain_parameters.Be.value,
                                                                                       strain_parameters.As.value,
                                                                                       strain_parameters.Bs.value,
                                                                                       strain_parameters.mix.value,
                                                                                       strain_parameters.b.value)

                    if not instrumental_parameters is None:
                        y_ib_instr[i] = integral_breadth_instrumental_function(reflection.h,
                                                                               reflection.k,
                                                                               reflection.l,
                                                                               lattice_parameter,
                                                                               wavelength,
                                                                               instrumental_parameters.U.value,
                                                                               instrumental_parameters.V.value,
                                                                               instrumental_parameters.W.value,
                                                                               instrumental_parameters.a.value,
                                                                               instrumental_parameters.b.value,
                                                                               instrumental_parameters.c.value)

                y_ib_total = y_ib_size + y_ib_strain + y_ib_instr

                x_ib = self.x_ib[diffraction_pattern_index]

                if plot_instr:  self.plot_integral_breadth[diffraction_pattern_index].addCurve(x_ib, y_ib_instr, legend="IPF", symbol='o', color="black")
                if plot_size:   self.plot_integral_breadth[diffraction_pattern_index].addCurve(x_ib, y_ib_size, legend="Size", symbol='o', color="red")
                if plot_strain: self.plot_integral_breadth[diffraction_pattern_index].addCurve(x_ib, y_ib_strain, legend="Strain", symbol='o', color="blue")
                self.plot_integral_breadth[diffraction_pattern_index].addCurve(x_ib, y_ib_total, legend="Total", symbol='o', color="#2D811B")
                self.plot_integral_breadth[diffraction_pattern_index].setGraphYLimits(-0.05,
                                                                                      numpy.max(y_ib_total)*1.2)
                self.plot_integral_breadth[diffraction_pattern_index].setGraphXLimits(x_ib[0] - abs(x_ib[0])*0.1,
                                                                                      x_ib[-1] + abs(x_ib[0])*0.1)

                ax          = self.plot_integral_breadth[diffraction_pattern_index]._backend.ax
                annotations = numpy.full(nr_points, None)
                labels      = self.labels_ib[diffraction_pattern_index]
                dy = (numpy.max(y_ib_total)-numpy.min(y_ib_instr))*0.125

                self.annotations_ib[diffraction_pattern_index] = annotations

                for i, hkl in enumerate(labels):
                    annotations[i] = ax.annotate(hkl, (x_ib[i], y_ib_total[i] + dy), rotation=90)

    # ------------------------------------------------------------------------

    def __build_plot_fit(self):
        fit_global_parameter = self.fit_global_parameters if self.fitted_fit_global_parameters is None else self.fitted_fit_global_parameters

        self.plot_fit = []
        self.tabs_plot_fit_data.clear()

        for index in range(1 if fit_global_parameter is None else len(fit_global_parameter.fit_initialization.diffraction_patterns)):
            tab_plot_fit_data = gui.createTabPage(self.tabs_plot_fit_data, "Diff. Patt. " + str(index+1))

            plot_fit = PlotWindow()
            plot_fit.setDefaultPlotLines(True)
            plot_fit.setActiveCurveColor(color="#00008B")
            plot_fit.setGraphXLabel(r"2$\theta$ (deg)")
            plot_fit.setGraphYLabel("Intensity")

            self.plot_fit.append(plot_fit)
            tab_plot_fit_data.layout().addWidget(plot_fit)

    # ------------------------------------------------------------------------

    def __build_plot_integral_breadth(self):
        fit_global_parameter = self.fit_global_parameters if self.fitted_fit_global_parameters is None else self.fitted_fit_global_parameters

        self.plot_integral_breadth = []
        self.tabs_plot_integral_breadth.clear()

        for index in range(1 if fit_global_parameter is None else fit_global_parameter.fit_initialization.get_diffraction_patterns_number()):
            tab_plot_integral_breadth = gui.createTabPage(self.tabs_plot_integral_breadth, "Diff. Patt. " + str(index+1))

            plot_integral_breadth = PlotWindow(control=True)
            legends_dock_widget = LegendsDockWidget(plot=plot_integral_breadth)
            plot_integral_breadth._legendsDockWidget = legends_dock_widget
            plot_integral_breadth._dockWidgets.append(legends_dock_widget)
            plot_integral_breadth.addDockWidget(qt.Qt.RightDockWidgetArea, legends_dock_widget)
            plot_integral_breadth._legendsDockWidget.setFixedWidth(130)
            plot_integral_breadth.getLegendsDockWidget().show()

            plot_integral_breadth.setDefaultPlotLines(True)
            plot_integral_breadth.setDefaultPlotPoints(True)
            plot_integral_breadth.setActiveCurveColor(color="#00008B")
            plot_integral_breadth.setGraphTitle("Integral Breadth plot")
            plot_integral_breadth.setGraphXLabel(r"s [$nm^{-1}$]")
            plot_integral_breadth.setGraphYLabel("${\\beta}(s)$ [$nm^{-1}$]")

            self.plot_integral_breadth.append(plot_integral_breadth)
            tab_plot_integral_breadth.layout().addWidget(plot_integral_breadth)

    ##########################################
    # THREADING
    ##########################################

    def fit_begin(self):
        self.fit_thread.mutex.tryLock()

        self.progressBarInit()
        self.setStatusMessage("Fitting procedure started")
        print("Fitting procedure started")
        self.fit_running = True

        self.fit_thread.mutex.unlock()

    def fit_update(self):
        self.fit_thread.mutex.tryLock()

        try:
            self.current_iteration += 1
            self.current_running_iteration += 1

            self.progressBarSet(int(self.current_running_iteration*100/self.n_iterations))
            self.setStatusMessage("Fit iteration nr. " + str(self.current_iteration) + "/" + str(self.n_iterations) + " completed")
            print("Fit iteration nr. " + str(self.current_iteration) + "/" + str(self.n_iterations) + " completed")

            if self.is_interactive == 1:
                self.__show_data()

                parameters = self.fitted_fit_global_parameters.free_input_parameters.as_parameters()
                parameters.extend(self.fitted_fit_global_parameters.get_parameters())
                parameters.extend(self.fitted_fit_global_parameters.free_output_parameters.as_parameters())

                self.__populate_table(self.table_fit_out, parameters)

                if self.current_iteration == 1:
                    self.tabs.setCurrentIndex(1)
                    self.tabs_plot.setCurrentIndex(0)

        except Exception as e:
            QMessageBox.critical(self, "Error",
                                 str(e),
                                 QMessageBox.Ok)

            if self.IS_DEVELOP: raise e

        self.fit_thread.mutex.unlock()

    def fit_completed(self):
        sys.stdout = self.standard_output

        self.setStatusMessage("Fitting procedure completed")
        print("Fitting procedure completed")

        self.fitted_fit_global_parameters.regenerate_parameters()

        self.fit_global_parameters = self.fitted_fit_global_parameters.duplicate()

        if self.is_incremental == 1:
            parameters = self.fit_global_parameters.free_input_parameters.as_parameters()
            parameters.extend(self.fit_global_parameters.get_parameters())

            self.__populate_table(self.table_fit_in, parameters, is_output=False)

        if self.is_interactive == 0:
            self.__show_data()

            parameters = self.fitted_fit_global_parameters.free_input_parameters.as_parameters()
            parameters.extend(self.fitted_fit_global_parameters.get_parameters())
            parameters.extend(self.fitted_fit_global_parameters.free_output_parameters.as_parameters())

            self.__populate_table(self.table_fit_out, parameters)

            if self.current_iteration == 1:
                self.tabs.setCurrentIndex(1)
                self.tabs_plot.setCurrentIndex(0)

        self.send("Fit Global Parameters", self.fitted_fit_global_parameters)

        self.fit_button.setEnabled(True)
        self.set_plot_options_enabled(True)
        self.fit_running = False
        self.stop_fit = False
        self.progressBarFinished()

    def fit_error(self):
        QMessageBox.critical(self, "Error",
                             "Fit Failed: " + str(self.thread_exception),
                             QMessageBox.Ok)

        self.fit_completed()

        if self.IS_DEVELOP: raise self.thread_exception


# ------------------------------------------------------------------------

from PyQt5.QtCore import QThread, pyqtSignal
import time

class FitThread(QThread):

    begin = pyqtSignal()
    update = pyqtSignal()
    error = pyqtSignal()
    mutex = QMutex()

    def __init__(self, fitter_widget):
        super(FitThread, self).__init__(fitter_widget)
        self.fitter_widget = fitter_widget

    def run(self):
        try:
            self.begin.emit()

            t0 = time.clock()

            for iteration in range(1, self.fitter_widget.n_iterations + 1):
                if self.fitter_widget.stop_fit: break

                self.fitter_widget.fitted_patterns, \
                self.fitter_widget.fitted_fit_global_parameters, \
                self.fitter_widget.fit_data = \
                    self.fitter_widget.fitter.do_fit(current_fit_global_parameters=self.fitter_widget.fitted_fit_global_parameters,
                                                     current_iteration=iteration,
                                                     compute_pattern=self.fitter_widget.is_interactive==1 or iteration==self.fitter_widget.n_iterations,
                                                     compute_errors=self.fitter_widget.is_interactive==1 or iteration==self.fitter_widget.n_iterations)

                self.fitter_widget.current_wss.append(self.fitter_widget.fit_data.wss)
                self.fitter_widget.current_gof.append(self.fitter_widget.fit_data.gof())

                self.update.emit()

                if self.fitter_widget.stop_fit:
                    if self.fitter_widget.is_interactive==0 and iteration<self.fitter_widget.n_iterations:
                        self.fitter_widget.fitted_patterns = \
                            self.fitter_widget.fitter.build_fitted_diffraction_pattern(fit_global_parameters=self.fitter_widget.fitted_fit_global_parameters)

                    break
                if self.fitter_widget.fitted_fit_global_parameters.is_convergence_reached(): break

            print("Fit duration: ", round(time.clock()-t0, 3), " seconds")

        except Exception as exception:
            self.fitter_widget.thread_exception = exception

            self.error.emit()

class FitNotStartedException(Exception):
    def __init__(self, *args, **kwargs): # real signature unknown
        super(FitNotStartedException, self).__init__(args, kwargs)

if __name__ == "__main__":
    a = QApplication(sys.argv)
    ow = OWFitter()
    ow.show()
    a.exec_()
    ow.saveSettings()
