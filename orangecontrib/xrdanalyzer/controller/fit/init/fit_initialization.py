from orangecontrib.xrdanalyzer.controller.fit.fit_parameter import FitParametersList

class FitInitialization(FitParametersList):

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

    def get_parameters(self):
        parameters = []

        if not self.diffraction_patterns is None:
            for diffraction_pattern in self.diffraction_patterns:
                parameters.extend(diffraction_pattern.get_parameters())

        if not self.crystal_structures is None:
            for crystal_structure in self.crystal_structures:
                parameters.extend(crystal_structure.get_parameters())

        if not self.thermal_polarization_parameters is None:
            for thermal_polarization_parameters in self.thermal_polarization_parameters:
                parameters.extend(thermal_polarization_parameters.get_parameters())

        return parameters

    def tuple(self):
        tuple = []

        if not self.diffraction_patterns is None:
            for diffraction_pattern in self.diffraction_patterns:
                tuple.extend(diffraction_pattern.tuple())

        if not self.crystal_structure is None:
            for crystal_structure in self.crystal_structures:
                tuple.extend(crystal_structure.tuple())

        if not self.thermal_polarization_parameters is None:
            for thermal_polarization_parameters in self.thermal_polarization_parameters:
                tuple.extend(thermal_polarization_parameters.tuple())

        return tuple

    def append_to_tuple(self, parameters, boundaries):

        if not self.diffraction_patterns is None:
            for diffraction_pattern in self.diffraction_patterns:
                parameters, boundaries = diffraction_pattern.append_to_tuple(parameters, boundaries)

        if not self.crystal_structure is None:
            for crystal_structure in self.crystal_structures:
                parameters, boundaries = crystal_structure.append_to_tuple(parameters, boundaries)

        if not self.thermal_polarization_parameters is None:
            for thermal_polarization_parameters in self.thermal_polarization_parameters:
                parameters, boundaries = thermal_polarization_parameters.append_to_tuple(parameters, boundaries)

        return parameters, boundaries

    def to_text(self):
        text = "FIT INITIALIZATION\n\n"
        text += "***********************************\n\n"

        if not self.diffraction_patterns is None:
            for diffraction_pattern in self.diffraction_patterns:
                text += diffraction_pattern.to_text()

        if not self.fft_parameters is None:
            text += self.fft_parameters.to_text()

        if not self.crystal_structures is None:
            for crystal_structure in self.crystal_structures:
                text += crystal_structure.to_text()

        if not self.thermal_polarization_parameters is None:
            for thermal_polarization_parameters in self.thermal_polarization_parameters:
                text += thermal_polarization_parameters.to_text()


        text += "\n***********************************\n"

        return text


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
    
