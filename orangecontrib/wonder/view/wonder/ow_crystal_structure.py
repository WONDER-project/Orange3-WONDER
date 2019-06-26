import sys, numpy, copy

from PyQt5.QtWidgets import QMessageBox, QScrollArea, QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDoubleValidator

from Orange.widgets.settings import Setting
from Orange.widgets import gui as orangegui

from orangecontrib.wonder.util.widgets.ow_generic_widget import OWGenericWidget
from orangecontrib.wonder.util.gui.gui_utility import gui, ConfirmDialog, ConfirmTextDialog, ShowTextDialog

from orangecontrib.wonder.util import congruence
from orangecontrib.wonder.controller.fit.util.fit_utilities import Utilities, list_of_s_bragg, Symmetry
from orangecontrib.wonder.controller.fit.fit_global_parameters import FitGlobalParameters
from orangecontrib.wonder.controller.fit.fit_parameter import FitParameter, Boundary
from orangecontrib.wonder.controller.fit.init.crystal_structure import CrystalStructure, Reflection

class OWCrystalStructure(OWGenericWidget):

    name = "Crystal Structure"
    description = "Define Crystal Structure"
    icon = "icons/crystal_structure.png"
    priority = 3

    want_main_area = False

    a                                     = Setting([0.0])
    a_fixed                               = Setting([0])
    a_has_min                             = Setting([0])
    a_min                                 = Setting([0.0])
    a_has_max                             = Setting([0])
    a_max                                 = Setting([0.0])
    a_function                            = Setting([0])
    a_function_value                      = Setting([""])
    symmetry                              = Setting([2])
    use_structure                         = Setting([0])
    formula                               = Setting([""])
    intensity_scale_factor                = Setting([1.0])
    intensity_scale_factor_fixed          = Setting([0])
    intensity_scale_factor_has_min        = Setting([0])
    intensity_scale_factor_min            = Setting([0.0])
    intensity_scale_factor_has_max        = Setting([0])
    intensity_scale_factor_max            = Setting([0.0])
    intensity_scale_factor_function       = Setting([0])
    intensity_scale_factor_function_value = Setting([""])
    reflections                           = Setting([""])
    limit                                 = Setting([0.0])
    limit_type                            = Setting([0])

    inputs = [("Fit Global Parameters", FitGlobalParameters, 'set_data')]
    outputs = [("Fit Global Parameters", FitGlobalParameters)]

    # TO PRESERVE RETRO-COMPATIBILITY
    def fix_input(self, emergency=False):
        if not isinstance(self.a                                    , list): self.a                                     = [self.a                                    ]
        if not isinstance(self.a_fixed                              , list): self.a_fixed                               = [self.a_fixed                              ]
        if not isinstance(self.a_has_min                            , list): self.a_has_min                             = [self.a_has_min                            ]
        if not isinstance(self.a_min                                , list): self.a_min                                 = [self.a_min                                ]
        if not isinstance(self.a_has_max                            , list): self.a_has_max                             = [self.a_has_max                            ]
        if not isinstance(self.a_max                                , list): self.a_max                                 = [self.a_max                                ]
        if not isinstance(self.a_function                           , list): self.a_function                            = [self.a_function                           ]
        if not isinstance(self.a_function_value                     , list): self.a_function_value                      = [self.a_function_value                     ]
        if not isinstance(self.symmetry                             , list): self.symmetry                              = [self.symmetry                             ]
        if not isinstance(self.use_structure                        , list): self.use_structure                         = [self.use_structure                        ]
        if not isinstance(self.formula                              , list): self.formula                               = [self.formula                              ]
        if not isinstance(self.intensity_scale_factor               , list): self.intensity_scale_factor                = [self.intensity_scale_factor               ]
        if not isinstance(self.intensity_scale_factor_fixed         , list): self.intensity_scale_factor_fixed          = [self.intensity_scale_factor_fixed         ]
        if not isinstance(self.intensity_scale_factor_has_min       , list): self.intensity_scale_factor_has_min        = [self.intensity_scale_factor_has_min       ]
        if not isinstance(self.intensity_scale_factor_min           , list): self.intensity_scale_factor_min            = [self.intensity_scale_factor_min           ]
        if not isinstance(self.intensity_scale_factor_has_max       , list): self.intensity_scale_factor_has_max        = [self.intensity_scale_factor_has_max       ]
        if not isinstance(self.intensity_scale_factor_max           , list): self.intensity_scale_factor_max            = [self.intensity_scale_factor_max           ]
        if not isinstance(self.intensity_scale_factor_function      , list): self.intensity_scale_factor_function       = [self.intensity_scale_factor_function      ]
        if not isinstance(self.intensity_scale_factor_function_value, list): self.intensity_scale_factor_function_value = [self.intensity_scale_factor_function_value]
        if not isinstance(self.reflections                          , list): self.reflections                           = [self.reflections                          ]
        if not isinstance(self.limit                                , list): self.limit                                 = [self.limit                                ]
        if not isinstance(self.limit_type                           , list): self.limit_type                            = [self.limit_type                           ]

        if len(self.symmetry) < len(self.a):
            self.symmetry.extend([2]*(len(self.a)-len(self.symmetry)))
        elif len(self.symmetry) > len(self.a):
            self.symmetry = self.symmetry[:len(self.a)]

        if emergency:
            self.a                                     = [0.0]
            self.a_fixed                               = [0]
            self.a_has_min                             = [0]
            self.a_min                                 = [0.0]
            self.a_has_max                             = [0]
            self.a_max                                 = [0.0]
            self.a_function                            = [0]
            self.a_function_value                      = [""]
            self.symmetry                              = [2]
            self.use_structure                         = [0]
            self.formula                               = [""]
            self.intensity_scale_factor                = [1.0]
            self.intensity_scale_factor_fixed          = [0]
            self.intensity_scale_factor_has_min        = [0]
            self.intensity_scale_factor_min            = [0.0]
            self.intensity_scale_factor_has_max        = [0]
            self.intensity_scale_factor_max            = [0.0]
            self.intensity_scale_factor_function       = [0]
            self.intensity_scale_factor_function_value = [""]
            self.reflections                           = [""]
            self.limit                                 = [""]
            self.limit_type                            = [""]
        else:
            if len(self.a                                    ) == 0: self.a                                     = [0.0]
            if len(self.a_fixed                              ) == 0: self.a_fixed                               = [0]
            if len(self.a_has_min                            ) == 0: self.a_has_min                             = [0]
            if len(self.a_min                                ) == 0: self.a_min                                 = [0.0]
            if len(self.a_has_max                            ) == 0: self.a_has_max                             = [0]
            if len(self.a_max                                ) == 0: self.a_max                                 = [0.0]
            if len(self.a_function                           ) == 0: self.a_function                            = [0]
            if len(self.a_function_value                     ) == 0: self.a_function_value                      = [""]
            if len(self.symmetry                             ) == 0: self.symmetry                              = [2]
            if len(self.use_structure                        ) == 0: self.use_structure                         = [0]
            if len(self.formula                              ) == 0: self.formula                               = [""]
            if len(self.intensity_scale_factor               ) == 0: self.intensity_scale_factor                = [1.0]
            if len(self.intensity_scale_factor_fixed         ) == 0: self.intensity_scale_factor_fixed          = [0]
            if len(self.intensity_scale_factor_has_min       ) == 0: self.intensity_scale_factor_has_min        = [0]
            if len(self.intensity_scale_factor_min           ) == 0: self.intensity_scale_factor_min            = [0.0]
            if len(self.intensity_scale_factor_has_max       ) == 0: self.intensity_scale_factor_has_max        = [0]
            if len(self.intensity_scale_factor_max           ) == 0: self.intensity_scale_factor_max            = [0.0]
            if len(self.intensity_scale_factor_function      ) == 0: self.intensity_scale_factor_function       = [0]
            if len(self.intensity_scale_factor_function_value) == 0: self.intensity_scale_factor_function_value = [""]
            if len(self.reflections                          ) == 0: self.reflections                           = [""]
            if len(self.limit                                ) == 0: self.limit                                 = [""]
            if len(self.limit_type                           ) == 0: self.limit_type                            = [""]


    def __init__(self):
        super().__init__(show_automatic_box=True)
        
        if self.IS_FIX: self.fix_input()
        
        crystal_box = gui.widgetBox(self.controlArea,
                                 "Crystal Structure", orientation="vertical",
                                 width=self.CONTROL_AREA_WIDTH - 10, height=600)


        button_box = gui.widgetBox(crystal_box,
                                   "", orientation="horizontal",
                                   width=self.CONTROL_AREA_WIDTH-25)

        gui.button(button_box,  self, "Send Crystal Structure", height=50, callback=self.send_fit_initialization)

        self.crystal_structure_tabs = gui.tabWidget(crystal_box)
        self.crystal_structure_box_array = []

        for index in range(len(self.a)):
            crystal_structure_tab = gui.createTabPage(self.crystal_structure_tabs, "Diff. Patt. " + str(index + 1))

            crystal_structure_box = CrystalStructureBox(widget=self,
                                                        parent=crystal_structure_tab,
                                                        index = index,
                                                        a                                    = self.a[index],
                                                        a_fixed                              = self.a_fixed[index],
                                                        a_has_min                            = self.a_has_min[index],
                                                        a_min                                = self.a_min[index],
                                                        a_has_max                            = self.a_has_max[index],
                                                        a_max                                = self.a_max[index],
                                                        a_function                           = self.a_function[index],
                                                        a_function_value                     = self.a_function_value[index],
                                                        symmetry                             = self.symmetry[index],
                                                        use_structure                        = self.use_structure[index],
                                                        formula                              = self.formula[index],
                                                        intensity_scale_factor               = self.intensity_scale_factor[index],
                                                        intensity_scale_factor_fixed         = self.intensity_scale_factor_fixed[index],
                                                        intensity_scale_factor_has_min       = self.intensity_scale_factor_has_min[index],
                                                        intensity_scale_factor_min           = self.intensity_scale_factor_min[index],
                                                        intensity_scale_factor_has_max       = self.intensity_scale_factor_has_max[index],
                                                        intensity_scale_factor_max           = self.intensity_scale_factor_max[index],
                                                        intensity_scale_factor_function      = self.intensity_scale_factor_function[index],
                                                        intensity_scale_factor_function_value= self.intensity_scale_factor_function_value[index],
                                                        reflections                          = self.reflections[index],
                                                        limit                                = self.limit[index],
                                                        limit_type                           = self.limit_type[index])

            self.crystal_structure_box_array.append(crystal_structure_box)

    def send_fit_initialization(self):
        try:
            if not self.fit_global_parameters is None:
                self.dumpSettings()

                self.check_congruence()

                self.fit_global_parameters.fit_initialization.crystal_structures = []
                for index in range(len(self.crystal_structure_box_array)):
                    self.crystal_structure_box_array[index].append_fit_initialization()

                self.fit_global_parameters.regenerate_parameters()

                self.send("Fit Global Parameters", self.fit_global_parameters)

        except Exception as e:
            QMessageBox.critical(self, "Error",
                                 str(e),
                                 QMessageBox.Ok)

            if self.IS_DEVELOP: raise e

    def check_congruence(self):
        use_structure_first = self.crystal_structure_box_array[0].use_structure

        for index in range(1, len(self.crystal_structure_box_array)):
            if use_structure_first != self.crystal_structure_box_array[index].use_structure:
                raise Exception("Incongruity: all the Crystal Structures must have the same setup of the structural model")


    def set_data(self, data):
        if not data is None:
            try:
                self.fit_global_parameters = data.duplicate()

                diffraction_patterns = self.fit_global_parameters.fit_initialization.diffraction_patterns
                crystal_structures = self.fit_global_parameters.fit_initialization.crystal_structures

                if diffraction_patterns is None: raise ValueError("No Diffraction Pattern in input data!")

                if len(diffraction_patterns) != len(self.crystal_structure_box_array):
                    recycle = ConfirmDialog.confirmed(message="Number of Diffraction Patterns changed:\ndo you want to use the existing structures where possible?\n\nIf yes, check for possible incongruences",
                                                      title="Warning")

                    self.crystal_structure_tabs.clear()
                    self.crystal_structure_box_array = []

                    for index in range(len(diffraction_patterns)):
                        crystal_structure_tab = gui.createTabPage(self.crystal_structure_tabs, "Diff. Patt. " + str(index + 1))

                        if recycle and index < len(self.a): #keep the existing
                            crystal_structure_box = CrystalStructureBox(widget=self,
                                                                        parent=crystal_structure_tab,
                                                                        index = index,
                                                                        a                                    = self.a[index],
                                                                        a_fixed                              = self.a_fixed[index],
                                                                        a_has_min                            = self.a_has_min[index],
                                                                        a_min                                = self.a_min[index],
                                                                        a_has_max                            = self.a_has_max[index],
                                                                        a_max                                = self.a_max[index],
                                                                        a_function                           = self.a_function[index],
                                                                        a_function_value                     = self.a_function_value[index],
                                                                        symmetry                             = self.symmetry[index],
                                                                        use_structure                        = self.use_structure[index],
                                                                        formula                              = self.formula[index],
                                                                        intensity_scale_factor               = self.intensity_scale_factor[index],
                                                                        intensity_scale_factor_fixed         = self.intensity_scale_factor_fixed[index],
                                                                        intensity_scale_factor_has_min       = self.intensity_scale_factor_has_min[index],
                                                                        intensity_scale_factor_min           = self.intensity_scale_factor_min[index],
                                                                        intensity_scale_factor_has_max       = self.intensity_scale_factor_has_max[index],
                                                                        intensity_scale_factor_max           = self.intensity_scale_factor_max[index],
                                                                        intensity_scale_factor_function      = self.intensity_scale_factor_function[index],
                                                                        intensity_scale_factor_function_value= self.intensity_scale_factor_function_value[index],
                                                                        reflections                          = self.reflections[index],
                                                                        limit                                = self.limit[index],
                                                                        limit_type                           = self.limit_type[index])
                        else:
                            crystal_structure_box = CrystalStructureBox(widget=self, parent=crystal_structure_tab, index = index)

                        self.crystal_structure_box_array.append(crystal_structure_box)

                elif not crystal_structures is None:
                    for index in range(len(crystal_structures)):
                        self.crystal_structure_box_array[index].set_data(crystal_structures[index])

                self.dumpSettings()

                if self.is_automatic_run:
                    self.send_fit_initialization()

            except Exception as e:
                QMessageBox.critical(self, "Error",
                                     str(e),
                                     QMessageBox.Ok)

                if self.IS_DEVELOP: raise e


    ##############################
    # SINGLE FIELDS SIGNALS
    ##############################


    def dumpSettings(self):
        self.dump_a()
        self.dump_symmetry()
        self.dump_use_structure()
        self.dump_formula()
        self.dump_intensity_scale_factor()
        self.dump_reflections()
        self.dump_limit()
        self.dump_limit_type()

    def dump_a(self):
        bkp_a                = copy.deepcopy(self.a               )
        bkp_a_fixed          = copy.deepcopy(self.a_fixed         )
        bkp_a_has_min        = copy.deepcopy(self.a_has_min       )
        bkp_a_min            = copy.deepcopy(self.a_min           )
        bkp_a_has_max        = copy.deepcopy(self.a_has_max       )
        bkp_a_max            = copy.deepcopy(self.a_max           )
        bkp_a_function       = copy.deepcopy(self.a_function      )
        bkp_a_function_value = copy.deepcopy(self.a_function_value)
        
        try:
            self.a                = []
            self.a_fixed          = []
            self.a_has_min        = []
            self.a_min            = []
            self.a_has_max        = []
            self.a_max            = []
            self.a_function       = []
            self.a_function_value = []    
        
            for index in range(len(self.crystal_structure_box_array)):
                self.a.append(self.crystal_structure_box_array[index].a)
                self.a_fixed.append(self.crystal_structure_box_array[index].a_fixed)
                self.a_has_min.append(self.crystal_structure_box_array[index].a_has_min)
                self.a_min.append(self.crystal_structure_box_array[index].a_min)
                self.a_has_max.append(self.crystal_structure_box_array[index].a_has_max)
                self.a_max.append(self.crystal_structure_box_array[index].a_max)
                self.a_function.append(self.crystal_structure_box_array[index].a_function)
                self.a_function_value.append(self.crystal_structure_box_array[index].a_function_value)
        except:
            self.a                = copy.deepcopy(bkp_a               )
            self.a_fixed          = copy.deepcopy(bkp_a_fixed         )
            self.a_has_min        = copy.deepcopy(bkp_a_has_min       )
            self.a_min            = copy.deepcopy(bkp_a_min           )
            self.a_has_max        = copy.deepcopy(bkp_a_has_max       )
            self.a_max            = copy.deepcopy(bkp_a_max           )
            self.a_function       = copy.deepcopy(bkp_a_function      )
            self.a_function_value = copy.deepcopy(bkp_a_function_value)
 
    def dump_symmetry(self):
        bkp_symmetry = copy.deepcopy(self.symmetry)

        try:
            self.symmetry = []

            for index in range(len(self.crystal_structure_box_array)):
                self.symmetry.append(self.crystal_structure_box_array[index].symmetry)
        except:
            self.symmetry = copy.deepcopy(bkp_symmetry)

    def dump_use_structure(self):
        bkp_use_structure = copy.deepcopy(self.use_structure)

        try:
            self.use_structure = []

            for index in range(len(self.crystal_structure_box_array)):
                self.use_structure.append(self.crystal_structure_box_array[index].use_structure)
        except:
            self.use_structure = copy.deepcopy(bkp_use_structure)

    def dump_formula(self):
        bkp_formula = copy.deepcopy(self.formula)

        try:
            self.formula = []

            for index in range(len(self.crystal_structure_box_array)):
                self.formula.append(self.crystal_structure_box_array[index].formula)
        except:
            self.formula = copy.deepcopy(bkp_formula)

    def dump_intensity_scale_factor(self):
        bkp_intensity_scale_factor                = copy.deepcopy(self.intensity_scale_factor               )
        bkp_intensity_scale_factor_fixed          = copy.deepcopy(self.intensity_scale_factor_fixed         )
        bkp_intensity_scale_factor_has_min        = copy.deepcopy(self.intensity_scale_factor_has_min       )
        bkp_intensity_scale_factor_min            = copy.deepcopy(self.intensity_scale_factor_min           )
        bkp_intensity_scale_factor_has_max        = copy.deepcopy(self.intensity_scale_factor_has_max       )
        bkp_intensity_scale_factor_max            = copy.deepcopy(self.intensity_scale_factor_max           )
        bkp_intensity_scale_factor_function       = copy.deepcopy(self.intensity_scale_factor_function      )
        bkp_intensity_scale_factor_function_value = copy.deepcopy(self.intensity_scale_factor_function_value)
        
        try:
            self.intensity_scale_factor                = []
            self.intensity_scale_factor_fixed          = []
            self.intensity_scale_factor_has_min        = []
            self.intensity_scale_factor_min            = []
            self.intensity_scale_factor_has_max        = []
            self.intensity_scale_factor_max            = []
            self.intensity_scale_factor_function       = []
            self.intensity_scale_factor_function_value = []    
        
            for index in range(len(self.crystal_structure_box_array)):
                self.intensity_scale_factor.append(self.crystal_structure_box_array[index].intensity_scale_factor)
                self.intensity_scale_factor_fixed.append(self.crystal_structure_box_array[index].intensity_scale_factor_fixed)
                self.intensity_scale_factor_has_min.append(self.crystal_structure_box_array[index].intensity_scale_factor_has_min)
                self.intensity_scale_factor_min.append(self.crystal_structure_box_array[index].intensity_scale_factor_min)
                self.intensity_scale_factor_has_max.append(self.crystal_structure_box_array[index].intensity_scale_factor_has_max)
                self.intensity_scale_factor_max.append(self.crystal_structure_box_array[index].intensity_scale_factor_max)
                self.intensity_scale_factor_function.append(self.crystal_structure_box_array[index].intensity_scale_factor_function)
                self.intensity_scale_factor_function_value.append(self.crystal_structure_box_array[index].intensity_scale_factor_function_value)
        except:
            self.intensity_scale_factor                = copy.deepcopy(bkp_intensity_scale_factor               )
            self.intensity_scale_factor_fixed          = copy.deepcopy(bkp_intensity_scale_factor_fixed         )
            self.intensity_scale_factor_has_min        = copy.deepcopy(bkp_intensity_scale_factor_has_min       )
            self.intensity_scale_factor_min            = copy.deepcopy(bkp_intensity_scale_factor_min           )
            self.intensity_scale_factor_has_max        = copy.deepcopy(bkp_intensity_scale_factor_has_max       )
            self.intensity_scale_factor_max            = copy.deepcopy(bkp_intensity_scale_factor_max           )
            self.intensity_scale_factor_function       = copy.deepcopy(bkp_intensity_scale_factor_function      )
            self.intensity_scale_factor_function_value = copy.deepcopy(bkp_intensity_scale_factor_function_value)

    def dump_reflections(self):
        bkp_reflections = copy.deepcopy(self.reflections)

        try:
            self.reflections = []

            for index in range(len(self.crystal_structure_box_array)):
                self.reflections.append(self.crystal_structure_box_array[index].reflections)
        except:
            self.reflections = copy.deepcopy(bkp_reflections)

    def dump_limit(self):
        bkp_limit = copy.deepcopy(self.limit)

        try:
            self.limit = []

            for index in range(len(self.crystal_structure_box_array)):
                self.limit.append(self.crystal_structure_box_array[index].limit)
        except:
            self.limit = copy.deepcopy(bkp_limit)

    def dump_limit_type(self):
        bkp_limit_type = copy.deepcopy(self.limit_type)

        try:
            self.limit_type = []

            for index in range(len(self.crystal_structure_box_array)):
                self.limit_type.append(self.crystal_structure_box_array[index].limit_type)
        except:
            self.limit_type = copy.deepcopy(bkp_limit_type)


from Orange.widgets.gui import OWComponent
from PyQt5 import QtWidgets

class CrystalStructureBox(QtWidgets.QWidget, OWComponent):

    a                                     = 0.0
    a_fixed                               = 0
    a_has_min                             = 0
    a_min                                 = 0.0
    a_has_max                             = 0
    a_max                                 = 0.0
    a_function                            = 0
    a_function_value                      = ""
    symmetry                              = 2
    use_structure                         = 0
    formula                               = ""
    intensity_scale_factor                = 1.0
    intensity_scale_factor_fixed          = 0
    intensity_scale_factor_has_min        = 0
    intensity_scale_factor_min            = 0.0
    intensity_scale_factor_has_max        = 0
    intensity_scale_factor_max            = 0.0
    intensity_scale_factor_function       = 0
    intensity_scale_factor_function_value = ""
    reflections                           = ""
    limit                                 = 0.0
    limit_type                            = 0

    widget = None
    is_on_init = True

    parameter_functions = {}

    crystal_structure = None

    index = 0

    def __init__(self,
                 widget=None,
                 parent=None,
                 index = 0,
                 a                                     = 0.0,
                 a_fixed                               = 0,
                 a_has_min                             = 0,
                 a_min                                 = 0.0,
                 a_has_max                             = 0,
                 a_max                                 = 0.0,
                 a_function                            = 0,
                 a_function_value                      = "",
                 symmetry                              = 2,
                 use_structure                         = 0,
                 formula                               = "",
                 intensity_scale_factor                = 1.0,
                 intensity_scale_factor_fixed          = 0,
                 intensity_scale_factor_has_min        = 0,
                 intensity_scale_factor_min            = 0.0,
                 intensity_scale_factor_has_max        = 0,
                 intensity_scale_factor_max            = 0.0,
                 intensity_scale_factor_function       = 0,
                 intensity_scale_factor_function_value = "",
                 reflections                           = "",
                 limit                                 = 0.0,
                 limit_type                            = 0):
        super(CrystalStructureBox, self).__init__(parent)
        OWComponent.__init__(self)

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)
        self.setFixedWidth(widget.CONTROL_AREA_WIDTH - 35)
        self.setFixedHeight(500)

        self.widget = widget
        self.index = index
        
        self.a                                     = a
        self.a_fixed                               = a_fixed
        self.a_has_min                             = a_has_min
        self.a_min                                 = a_min
        self.a_has_max                             = a_has_max
        self.a_max                                 = a_max
        self.a_function                            = a_function
        self.a_function_value                      = a_function_value
        self.symmetry                              = symmetry
        self.use_structure                         = use_structure
        self.formula                               = formula
        self.intensity_scale_factor                = intensity_scale_factor
        self.intensity_scale_factor_fixed          = intensity_scale_factor_fixed
        self.intensity_scale_factor_has_min        = intensity_scale_factor_has_min
        self.intensity_scale_factor_min            = intensity_scale_factor_min
        self.intensity_scale_factor_has_max        = intensity_scale_factor_has_max
        self.intensity_scale_factor_max            = intensity_scale_factor_max
        self.intensity_scale_factor_function       = intensity_scale_factor_function
        self.intensity_scale_factor_function_value = intensity_scale_factor_function_value
        self.reflections                           = reflections
        self.limit                                 = limit
        self.limit_type                            = limit_type

        self.CONTROL_AREA_WIDTH = widget.CONTROL_AREA_WIDTH

        container = gui.widgetBox(parent, "", orientation="vertical", width=self.CONTROL_AREA_WIDTH-45)


        self.cb_symmetry = orangegui.comboBox(container, self, "symmetry", label="Symmetry", items=Symmetry.tuple(), callback=self.set_symmetry, orientation="horizontal")

        widget.create_box_in_widget(self, container, "a", "a [nm]", add_callback=True)

        orangegui.separator(container)

        structure_box = gui.widgetBox(container,
                                       "", orientation="vertical",
                                       width=self.CONTROL_AREA_WIDTH - 45)

        orangegui.comboBox(structure_box, self, "use_structure", label="Use Structural Model", items=["No", "Yes"],
                           callback=self.set_structure, labelWidth=350, orientation="horizontal")


        self.structure_box_1 = gui.widgetBox(structure_box,
                                       "", orientation="vertical",
                                       width=self.CONTROL_AREA_WIDTH - 50, height=60)

        gui.lineEdit(self.structure_box_1, self, "formula", "Chemical Formula", labelWidth=90, valueType=str, callback=widget.dump_formula)
        widget.create_box_in_widget(self, self.structure_box_1, "intensity_scale_factor", "I0", add_callback=True)

        self.structure_box_2 = gui.widgetBox(structure_box,
                                       "", orientation="vertical",
                                       width=self.CONTROL_AREA_WIDTH - 50, height=60)

        orangegui.separator(container)

        gen_box = gui.widgetBox(container, "Generate Reflections", orientation="horizontal")

        le_limit = gui.lineEdit(gen_box, self, "limit", "Limit", labelWidth=90, valueType=float, validator=QDoubleValidator(), callback=widget.dump_limit)
        cb_limit = orangegui.comboBox(gen_box, self, "limit_type", label="Kind", items=["None", "Nr. Peaks", "2Theta Max"], orientation="horizontal")

        def set_limit(limit_type):
            if limit_type == 0:
                le_limit.setText("-1")
                le_limit.setEnabled(False)
            else:
                le_limit.setEnabled(True)

            if not self.is_on_init:
                widget.dump_limit()
                widget.dump_limit_type()

        cb_limit.currentIndexChanged.connect(set_limit)
        set_limit(self.limit_type)

        gui.button(gen_box, self, "Generate Reflections", callback=self.generate_reflections)

        self.set_structure()

        reflection_box = gui.widgetBox(container,
                                       "Reflections", orientation="vertical",
                                       width=self.CONTROL_AREA_WIDTH - 50)

        orangegui.label(reflection_box, self, "h, k, l, <intensity_name> int <, min value, max value>")

        scrollarea = QScrollArea(reflection_box)
        scrollarea.setMaximumWidth(self.CONTROL_AREA_WIDTH - 85)
        scrollarea.setMinimumWidth(self.CONTROL_AREA_WIDTH - 85)

        def write_text():
            self.reflections = self.text_area.toPlainText()
            if not self.is_on_init: widget.dump_reflections()

        self.text_area = gui.textArea(height=500, width=1000, readOnly=False)
        self.text_area.setText(self.reflections)
        self.text_area.setStyleSheet("font-family: Courier, monospace;")
        self.text_area.textChanged.connect(write_text)

        scrollarea.setWidget(self.text_area)
        scrollarea.setWidgetResizable(1)

        reflection_box.layout().addWidget(scrollarea, alignment=Qt.AlignHCenter)

        self.is_on_init = False

    def after_change_workspace_units(self):
        pass

    def set_index(self, index):
        self.index = index

    def set_structure(self):
        self.structure_box_1.setVisible(self.use_structure==1)
        self.structure_box_2.setVisible(self.use_structure==0)

        if not self.is_on_init: self.widget.dump_use_structure()

    def set_symmetry(self):
        if not CrystalStructure.is_cube(self.cb_symmetry.currentText()):
            QMessageBox.critical(self, "Error",
                                 "Only Cubic Systems are supported",
                                 QMessageBox.Ok)

            self.symmetry = 2

        if not self.is_on_init: self.widget.dump_symmetry()

    def generate_reflections(self):
        if self.widget.populate_parameter_in_widget(self, "a", "").function:
            QMessageBox.critical(self,
                                 "Error",
                                 "a0 value is a function, generation is not possibile",
                                 QMessageBox.Ok)
            return

        if not self.reflections is None and not self.reflections.strip() == "":
            if not ConfirmDialog.confirmed(self, "Confirm overwriting of exisiting reflections?"):
                return

        if self.limit_type == 0:
            list = list_of_s_bragg(self.a,
                                   symmetry=self.cb_symmetry.currentText())
        elif self.limit_type == 1:
            list = list_of_s_bragg(self.a,
                                   symmetry=self.cb_symmetry.currentText(),
                                   n_peaks=int(self.limit))
        elif self.limit_type == 2:
            if not self.widget.fit_global_parameters is None \
               and not self.widget.fit_global_parameters.fit_initialization is None \
               and not self.widget.fit_global_parameters.fit_initialization.diffraction_patterns is None \
               and not self.widget.fit_global_parameters.fit_initialization.diffraction_patterns[self.index].wavelength.function:
                wavelength = self.widget.fit_global_parameters.fit_initialization.diffraction_patterns[self.index].wavelength.value

                list = list_of_s_bragg(self.a,
                                       symmetry=self.cb_symmetry.currentText(),
                                       s_max=Utilities.s(numpy.radians(self.limit/2), wavelength))
            else:
                QMessageBox.critical(self,
                                     "Error",
                                     "No wavelenght is available, 2theta limit is not possibile",
                                     QMessageBox.Ok)
                return

        text = ""

        for index in range(0, len(list)):
            h = list[index][0][0]
            k = list[index][0][1]
            l = list[index][0][2]

            text += Reflection(h, k, l, FitParameter(parameter_name="I" + str(h) + str(k) + str(l), value=1000, boundary=Boundary(min_value=0.0))).to_text() + "\n"

        self.text_area.setText(text)


    def callback_a(self):
        if not self.is_on_init: self.widget.dump_a()

    def callback_intensity_scale_factor(self):
        if not self.is_on_init: self.widget.dump_intensity_scale_factor()

    def get_parameters_prefix(self):
        return CrystalStructure.get_parameters_prefix() + self.get_parameter_progressive()

    def get_parameter_progressive(self):
        return str(self.index+1) + "_"

    def set_data(self, crystal_structure):
        self.widget.populate_fields_in_widget(self, "a", crystal_structure.a)
        self.use_structure = 1 if crystal_structure.use_structure else 0

        if self.use_structure == 0:
            existing_crystal_structure = CrystalStructure.init_cube(a0=self.widget.populate_parameter_in_widget(self, "a", self.get_parameters_prefix()),
                                                                    symmetry=self.cb_symmetry.currentText(),
                                                                    progressive=self.get_parameter_progressive())

        elif self.use_structure == 1:
            self.widget.populate_fields_in_widget(self, "intensity_scale_factor", crystal_structure.intensity_scale_factor)

            existing_crystal_structure = CrystalStructure.init_cube(a0=self.widget.populate_parameter_in_widget(self, "a", self.get_parameters_prefix()),
                                                                    symmetry=self.cb_symmetry.currentText(),
                                                                    use_structure=True,
                                                                    formula=congruence.checkEmptyString(self.formula, "Chemical Formula"),
                                                                    intensity_scale_factor=self.widget.populate_parameter_in_widget(self, "intensity_scale_factor", self.get_parameters_prefix()),
                                                                    progressive=self.get_parameter_progressive())


        if not self.text_area.toPlainText().strip() == "":
            existing_crystal_structure.parse_reflections(self.text_area.toPlainText(), progressive=self.get_parameter_progressive())

        simmetries = Symmetry.tuple()
        for index in range(0, len(simmetries)):
            if simmetries[index] == crystal_structure.symmetry:
                self.symmetry = index

        for reflection in crystal_structure.get_reflections():
            existing_reflection = existing_crystal_structure.existing_reflection(reflection.h, reflection.k, reflection.l)

            if existing_reflection is None:
                existing_crystal_structure.add_reflection(reflection)
            else:
                existing_reflection.intensity.value = reflection.intensity.value

        text = ""

        for reflection in existing_crystal_structure.get_reflections():
            text += reflection.to_row() + "\n"

        self.text_area.setText(text)


    def append_fit_initialization(self):
        if self.use_structure == 0:
            crystal_structure = CrystalStructure.init_cube(a0=self.widget.populate_parameter_in_widget(self, "a", self.get_parameters_prefix()),
                                                           symmetry=self.cb_symmetry.currentText(),
                                                           progressive=self.get_parameter_progressive())

            self.widget.fit_global_parameters.fit_initialization.crystal_structures.append(crystal_structure)
            self.widget.fit_global_parameters.evaluate_functions() # in case that a is a function of other parameters

            crystal_structure.parse_reflections(self.reflections, progressive=self.get_parameter_progressive())

        elif self.use_structure == 1:
            crystal_structure = CrystalStructure.init_cube(a0=self.widget.populate_parameter_in_widget(self, "a", self.get_parameters_prefix()),
                                                           symmetry=self.cb_symmetry.currentText(),
                                                           use_structure=True,
                                                           formula=congruence.checkEmptyString(self.formula, "Chemical Formula"),
                                                           intensity_scale_factor=self.widget.populate_parameter_in_widget(self, "intensity_scale_factor", self.get_parameters_prefix()),
                                                           progressive=self.get_parameter_progressive())

            self.widget.fit_global_parameters.fit_initialization.crystal_structures.append(crystal_structure)
            self.widget.fit_global_parameters.evaluate_functions() # in case that a is a function of other parameters

            crystal_structure.parse_reflections(self.reflections, progressive=self.get_parameter_progressive())

            #intensities will be ignored
            for reflection in crystal_structure.get_reflections():
                reflection.intensity.fixed = True

        if not self.widget.fit_global_parameters.fit_initialization is None \
           and not self.widget.fit_global_parameters.fit_initialization.diffraction_patterns is None:

            diffraction_pattern = self.widget.fit_global_parameters.fit_initialization.diffraction_patterns[self.index]

            if not diffraction_pattern.wavelength.function:
                wavelength = diffraction_pattern.wavelength.value
                s_min = diffraction_pattern.get_diffraction_point(0).s
                s_max = diffraction_pattern.get_diffraction_point(-1).s

                excluded_reflections = crystal_structure.get_congruence_check(wavelength=wavelength,
                                                                              min_value=s_min,
                                                                              max_value=s_max)

                if not excluded_reflections is None:
                    text_before = "The following reflections lie outside the diffraction pattern nr " + str(self.index+1) + ":"

                    text = ""
                    for reflection in excluded_reflections:
                        text += "[" + str(reflection.h) + ", " + str(reflection.k) + ", " + str(reflection.l) +"]\n"

                    text_after = "Proceed anyway?"

                    if not ConfirmTextDialog.confirm_text("Confirm Structure", text,
                                                          text_after=text_after, text_before=text_before,
                                                          width=350, parent=self): return

        return crystal_structure


if __name__ == "__main__":
    a = QApplication(sys.argv)
    ow = OWCrystalStructure()
    ow.show()
    a.exec_()
    ow.saveSettings()
