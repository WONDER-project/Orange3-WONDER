
from orangecontrib.wonder.controller.fit.fit_parameter import ParametersList

class Beampath:
    PRIMARY = 0
    SECONDARY = 1

    @classmethod
    def tuple(cls):
        return ["Primary", "Secondary"]

class LorentzFormula:
    S_Shkl = 0
    Shkl_Shkl = 1

    @classmethod
    def tuple(cls):
        return ["1/[s\u22c5s(hkl)]", "1/s(hkl)\u00b2"]

class ThermalPolarizationParameters(ParametersList):

    debye_waller_factor = None
    use_lorentz_factor = False
    lorentz_formula = LorentzFormula.Shkl_Shkl
    use_polarization_factor = False
    beampath = Beampath.PRIMARY
    degree_of_polarization = 0.5
    twotheta_mono = None

    def __init__(self,
                 debye_waller_factor = None,
                 use_lorentz_factor = False,
                 lorentz_formula = LorentzFormula.Shkl_Shkl,
                 use_polarization_factor=False,
                 beampath = Beampath.PRIMARY,
                 degree_of_polarization=0.0,
                 twotheta_mono=None):
        self.debye_waller_factor = debye_waller_factor
        self.use_lorentz_factor = use_lorentz_factor
        self.lorentz_formula = lorentz_formula
        self.use_polarization_factor = use_polarization_factor
        self.beampath = beampath
        self.degree_of_polarization = degree_of_polarization
        self.twotheta_mono = twotheta_mono

        if degree_of_polarization < 0: self.degree_of_polarization = 0.0
        elif degree_of_polarization> 1: self.degree_of_polarization = 1.0

    @classmethod
    def get_parameters_prefix(cls):
        return "tp_"
