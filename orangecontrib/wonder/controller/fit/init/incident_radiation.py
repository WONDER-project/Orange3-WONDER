from orangecontrib.wonder.controller.fit.fit_parameter import ParametersList

class IncidentRadiation(ParametersList):

    @classmethod
    def get_parameters_prefix(cls):
        return "incident_radiation_"

    wavelength = None
    is_single_wavelength = True
    xray_tube_key = None
    secondary_wavelengths = []
    secondary_wavelengths_weights = []
    principal_wavelength_weight = None

    def __init__(self, wavelength = None):
        self.wavelength = wavelength
        self.is_single_wavelength = True

    def set_multiple_wavelengths(self, xray_tube_key=None, secondary_wavelengths = [], secondary_wavelengths_weights = [], recalculate=True):
        self.is_single_wavelength = False
        self.xray_tube_key=xray_tube_key
        self.secondary_wavelengths = secondary_wavelengths
        self.secondary_wavelengths_weights = secondary_wavelengths_weights
        self.principal_wavelength_weight = self.get_principal_wavelenght_weight(recalculate=recalculate)

    def set_single_wavelength(self, wavelength=None, recalculate=True):
        self.is_single_wavelength = True
        self.wavelength = wavelength
        self.xray_tube_key=None
        self.secondary_wavelengths = []
        self.secondary_wavelengths_weights = []
        self.principal_wavelength_weight = self.get_principal_wavelenght_weight(recalculate=recalculate)

    def get_principal_wavelenght_weight(self, recalculate=False): # recalculate is to improve efficiency
        if not recalculate:
            return self.principal_wavelength_weight
        else:
            if not self.is_single_wavelength:
                total_weight = 0.0

                for weight in self.secondary_wavelengths_weights:
                    total_weight += weight.value

                if total_weight >= 1.0: raise ValueError("Weight of principal wavelength is <= 0")

                return 1.0 - total_weight

            else: return 1.0
