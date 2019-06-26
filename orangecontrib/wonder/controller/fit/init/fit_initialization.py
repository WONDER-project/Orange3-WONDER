from orangecontrib.wonder.controller.fit.fit_parameter import ParametersList

class FitInitialization(ParametersList):
    diffraction_patterns = None
    crystal_structures = None
    fft_parameters = None
    thermal_polarization_parameters = None

    def __init__(self,
                 diffraction_patterns = None,
                 crystal_structures = None,
                 fft_parameters = None,
                 thermal_polarization_parameters = None):
        self.diffraction_patterns = diffraction_patterns
        self.crystal_structures = crystal_structures
        self.fft_parameters = fft_parameters
        self.thermal_polarization_parameters = thermal_polarization_parameters

    def get_diffraction_patterns_number(self):
        return 0 if self.diffraction_patterns is None else len(self.diffraction_patterns)

    def duplicate(self):
        if self.diffraction_patterns is None: diffraction_patterns = None
        else:
            dimension = len(self.diffraction_patterns)
            diffraction_patterns = [None]*dimension
            for index in range(dimension):
                diffraction_patterns[index] = self.diffraction_patterns[index].duplicate()

        if self.crystal_structures is None: crystal_structures = None
        else:
            dimension = len(self.crystal_structures)
            crystal_structures = [None]*dimension
            for index in range(dimension):
                crystal_structures[index] = self.crystal_structures[index].duplicate()

        fft_parameters = None if self.fft_parameters is None else self.fft_parameters.duplicate()

        if self.thermal_polarization_parameters is None: thermal_polarization_parameters = None
        else:
            dimension = len(self.thermal_polarization_parameters)
            thermal_polarization_parameters = [None]*dimension
            for index in range(dimension):
                thermal_polarization_parameters[index] = self.thermal_polarization_parameters[index].duplicate()

        return FitInitialization(diffraction_patterns=diffraction_patterns,
                                 crystal_structures=crystal_structures,
                                 fft_parameters=fft_parameters,
                                 thermal_polarization_parameters=thermal_polarization_parameters)
