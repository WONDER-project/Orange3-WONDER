import numpy, copy

from orangecontrib.wonder.controller.fit.fit_parameter import ParametersList
from orangecontrib.wonder.controller.fit.fit_parameter import FreeInputParameters, FreeOutputParameters
from orangecontrib.wonder.controller.fit.instrument.background_parameters import ChebyshevBackground, ExpDecayBackground
from orangecontrib.wonder.controller.fit.instrument.instrumental_parameters import Lab6TanCorrection, ZeroError, SpecimenDisplacement
from orangecontrib.wonder.controller.fit.microstructure.strain import InvariantPAH, KrivoglazWilkensModel, WarrenModel
from orangecontrib.wonder.controller.fit.wppm.wppm_functions import Distribution, Shape

class FitGlobalParameters(ParametersList):

    fit_initialization = None
    background_parameters = None
    instrumental_parameters = None
    shift_parameters = None
    size_parameters = None
    strain_parameters = None
    free_input_parameters = None
    free_output_parameters = None

    n_max_iterations = 10
    convergence_reached = False

    __parameters = numpy.full(10000, None)

    def __init__(self,
                 fit_initialization = None,
                 background_parameters = {},
                 instrumental_parameters = None,
                 shift_parameters = {},
                 size_parameters = None,
                 strain_parameters = None,
                 free_input_parameters = FreeInputParameters(),
                 free_output_parameters = FreeOutputParameters()):
        super().__init__()

        self.fit_initialization = fit_initialization
        self.background_parameters = background_parameters
        self.instrumental_parameters = instrumental_parameters
        self.shift_parameters = shift_parameters
        self.size_parameters = size_parameters
        self.strain_parameters = strain_parameters
        self.free_input_parameters = free_input_parameters
        self.free_output_parameters = free_output_parameters

        self.n_max_iterations = 10
        self.convergence_reached = False

    def get_parameters_count(self):
        return len(self.__parameters[numpy.where(self.__parameters != None)])

    def get_parameters(self, good_only=True):
        if not good_only: return self.__parameters
        else: return self.__parameters[numpy.where(self.__parameters != None)]

    def clear_parameters(self):
        self.__parameters = numpy.full(10000, None)

    def replace_parameters(self, parameters):
        self.__parameters = parameters

    def get_available_parameters(self):
        text = ""

        for parameter in self.__parameters[numpy.where(self.__parameters != None)]:
            if not parameter.function: text += parameter.to_parameter_text() + "\n"

        return text

    def get_functions_data(self):
        parameters_dictionary = {}
        python_code = ""

        for parameter in self.__parameters[numpy.where(self.__parameters != None)]:
            if parameter.function:
                parameters_dictionary[parameter.parameter_name] = numpy.nan
                python_code += parameter.to_python_code() + "\n"

        return parameters_dictionary, python_code


    def set_n_max_iterations(self, value=10):
        self.n_max_iterations = value

    def get_n_max_iterations(self):
        return self.n_max_iterations

    def set_convergence_reached(self, value=True):
        self.convergence_reached = value

    def is_convergence_reached(self):
        return self.convergence_reached == True

    def space_parameters(self):
        return FitSpaceParameters(self)

    def get_background_parameters(self, key):
        try:
            return self.background_parameters[key]
        except:
            return None

    def set_background_parameters(self, background_parameters):
        if self.background_parameters is None:
            self.background_parameters = {}

        if not background_parameters is None:
            key = background_parameters[0].__class__.__name__
            self.background_parameters[key] = background_parameters

    def get_shift_parameters(self, key):
        try:
            return self.shift_parameters[key]
        except:
            return None

    def set_shift_parameters(self, shift_parameters):
        if self.shift_parameters is None:
            self.shift_parameters = {}

        if not shift_parameters is None:
            key = shift_parameters[0].__class__.__name__
            self.shift_parameters[key] = shift_parameters

    def evaluate_functions(self):
        FitGlobalParameters.compute_functions(self.get_parameters(), self.free_input_parameters, self.free_output_parameters)

    def regenerate_parameters(self):
        self.clear_parameters()

        parameters = self.get_parameters(good_only=False)

        last_index = -1

        if not self.fit_initialization.incident_radiations is None:
            for index in range(len(self.fit_initialization.incident_radiations)):
                incident_radiation = self.fit_initialization.incident_radiations[index]
                parameters[last_index + 1] = incident_radiation.wavelength
                last_index += 1

                if not incident_radiation.is_single_wavelength:
                    for secondary_wavelength, secondary_wavelength_weigth in zip(incident_radiation.secondary_wavelengths,
                                                                                 incident_radiation.secondary_wavelengths_weights):
                        parameters[last_index + 1] = secondary_wavelength
                        parameters[last_index + 2] = secondary_wavelength_weigth
                        last_index += 2

        if not self.fit_initialization.crystal_structures is None:
            for index in range(len(self.fit_initialization.crystal_structures)):
                crystal_structure = self.fit_initialization.crystal_structures[index]

                parameters[last_index + 1] = crystal_structure.a
                parameters[last_index + 2] = crystal_structure.b
                parameters[last_index + 3] = crystal_structure.c
                parameters[last_index + 4] = crystal_structure.alpha
                parameters[last_index + 5] = crystal_structure.beta
                parameters[last_index + 6] = crystal_structure.gamma

                if crystal_structure.use_structure:
                    parameters[last_index + 7] = crystal_structure.intensity_scale_factor
                    last_index += 7
                else:
                    last_index += 6

                for reflection_index in range(crystal_structure.get_reflections_count()):
                    parameters[last_index + 1 + reflection_index] = crystal_structure.get_reflection(reflection_index).intensity

                last_index += crystal_structure.get_reflections_count()

        if not self.fit_initialization.thermal_polarization_parameters is None:
            for thermal_polarization_parameters in self.fit_initialization.thermal_polarization_parameters:
                if not thermal_polarization_parameters.debye_waller_factor is None:
                    parameters[last_index + 1] = thermal_polarization_parameters.debye_waller_factor
                    last_index += 1

        if not self.background_parameters is None:
            for key in self.background_parameters.keys():
                background_parameters_list = self.get_background_parameters(key)

                if not background_parameters_list is None:
                    for background_parameters in background_parameters_list:
                        if key == ChebyshevBackground.__name__:
                            parameters[last_index + 1]  = background_parameters.c0
                            parameters[last_index + 2]  = background_parameters.c1
                            parameters[last_index + 3]  = background_parameters.c2
                            parameters[last_index + 4]  = background_parameters.c3
                            parameters[last_index + 5]  = background_parameters.c4
                            parameters[last_index + 6]  = background_parameters.c5
                            parameters[last_index + 7]  = background_parameters.c6
                            parameters[last_index + 8]  = background_parameters.c7
                            parameters[last_index + 9]  = background_parameters.c8
                            parameters[last_index + 10] = background_parameters.c9
                            last_index += 10
                        elif key == ExpDecayBackground.__name__:
                            parameters[last_index + 1] = background_parameters.a0
                            parameters[last_index + 2] = background_parameters.b0
                            parameters[last_index + 3] = background_parameters.a1
                            parameters[last_index + 4] = background_parameters.b1
                            parameters[last_index + 5] = background_parameters.a2
                            parameters[last_index + 6] = background_parameters.b2
                            last_index += 6

        if not self.instrumental_parameters is None:
            for instrumental_parameters in self.instrumental_parameters:
                parameters[last_index + 1] = instrumental_parameters.U
                parameters[last_index + 2] = instrumental_parameters.V
                parameters[last_index + 3] = instrumental_parameters.W
                parameters[last_index + 4] = instrumental_parameters.a
                parameters[last_index + 5] = instrumental_parameters.b
                parameters[last_index + 6] = instrumental_parameters.c
                last_index += 6

        if not self.shift_parameters is None:
            for key in self.shift_parameters.keys():
                shift_parameters_list = self.get_shift_parameters(key)

                if not shift_parameters_list is None:
                    for shift_parameters in shift_parameters_list:
                        if key == Lab6TanCorrection.__name__:
                            parameters[last_index + 1] = shift_parameters.ax
                            parameters[last_index + 2] = shift_parameters.bx
                            parameters[last_index + 3] = shift_parameters.cx
                            parameters[last_index + 4] = shift_parameters.dx
                            parameters[last_index + 5] = shift_parameters.ex
                            last_index += 5
                        elif key == ZeroError.__name__:
                            parameters[last_index + 1] = shift_parameters.shift
                            last_index += 1
                        elif key == SpecimenDisplacement.__name__:
                            parameters[last_index + 1] = shift_parameters.displacement
                            last_index += 1

        if not self.size_parameters is None:
            for size_parameters in self.size_parameters:
                parameters[last_index + 1] = size_parameters.mu
                if size_parameters.distribution == Distribution.DELTA:
                    last_index += 1
                else:
                    parameters[last_index + 2] = size_parameters.sigma
                    if size_parameters.shape == Shape.WULFF:
                        parameters[last_index + 3] = size_parameters.truncation
                        last_index += 3
                    else:
                        last_index += 2

        if not self.strain_parameters is None:
            for strain_parameters in self.strain_parameters:
                if isinstance(strain_parameters, InvariantPAH):
                    parameters[last_index + 1] = strain_parameters.aa
                    parameters[last_index + 2] = strain_parameters.bb
                    parameters[last_index + 3] = strain_parameters.e1 # in realtà è E1 dell'invariante PAH
                    parameters[last_index + 4] = strain_parameters.e2 # in realtà è E1 dell'invariante PAH
                    parameters[last_index + 5] = strain_parameters.e3 # in realtà è E1 dell'invariante PAH
                    parameters[last_index + 6] = strain_parameters.e4 # in realtà è E4 dell'invariante PAH
                    parameters[last_index + 7] = strain_parameters.e5 # in realtà è E4 dell'invariante PAH
                    parameters[last_index + 8] = strain_parameters.e6 # in realtà è E4 dell'invariante PAH
                    last_index += 8
                elif isinstance(strain_parameters, KrivoglazWilkensModel):
                    parameters[last_index + 1] = strain_parameters.rho
                    parameters[last_index + 2] = strain_parameters.Re
                    parameters[last_index + 3] = strain_parameters.Ae
                    parameters[last_index + 4] = strain_parameters.Be
                    parameters[last_index + 5] = strain_parameters.As
                    parameters[last_index + 6] = strain_parameters.Bs
                    parameters[last_index + 7] = strain_parameters.mix
                    parameters[last_index + 8] = strain_parameters.b
                    last_index += 8
                elif isinstance(strain_parameters, WarrenModel):
                    parameters[last_index + 1] = strain_parameters.average_cell_parameter
                    last_index += 1

        self.evaluate_functions()

    def from_fitted_parameters(self, fitted_parameters):
        last_index = -1

        if not self.fit_initialization.incident_radiations is None:
            for index in range(len(self.fit_initialization.incident_radiations)):
                incident_radiation = self.fit_initialization.incident_radiations[index]
                incident_radiation.wavelength.set_value(fitted_parameters[last_index + 1].value)

                last_index += 1

                if not incident_radiation.is_single_wavelength:
                    for secondary_wavelength, secondary_wavelength_weigth in zip(incident_radiation.secondary_wavelengths,
                                                                                 incident_radiation.secondary_wavelengths_weights):
                        secondary_wavelength.set_value(fitted_parameters[last_index + 1].value)
                        secondary_wavelength_weigth.set_value(fitted_parameters[last_index + 2].value)
                        last_index += 2

        if not self.fit_initialization.crystal_structures is None:
            for index in range(len(self.fit_initialization.crystal_structures)):
                crystal_structure = self.fit_initialization.crystal_structures[index]

                crystal_structure.a.set_value(fitted_parameters[last_index + 1].value)
                crystal_structure.b.set_value(fitted_parameters[last_index + 2].value)
                crystal_structure.c.set_value(fitted_parameters[last_index + 3].value)
                crystal_structure.alpha.set_value(fitted_parameters[last_index + 4].value)
                crystal_structure.beta.set_value(fitted_parameters[last_index + 5].value)
                crystal_structure.gamma.set_value(fitted_parameters[last_index + 6].value)

                if crystal_structure.use_structure:
                    crystal_structure.intensity_scale_factor.set_value(fitted_parameters[last_index + 7].value)
                    last_index += 7
                else:
                    last_index += 6

                for reflection_index in range(crystal_structure.get_reflections_count()):
                    crystal_structure.get_reflection(reflection_index).intensity.set_value(fitted_parameters[last_index + 1 + reflection_index].value)

                last_index += crystal_structure.get_reflections_count()

        if not self.fit_initialization.thermal_polarization_parameters is None:
            for thermal_polarization_parameters in self.fit_initialization.thermal_polarization_parameters:
                if not thermal_polarization_parameters.debye_waller_factor is None:
                    thermal_polarization_parameters.debye_waller_factor.set_value(fitted_parameters[last_index + 1].value)
                    last_index += 1

        if not self.background_parameters is None:
            for key in self.background_parameters.keys():
                background_parameters_list = self.get_background_parameters(key)

                if not background_parameters_list is None:
                    for background_parameters in background_parameters_list:
                        if key == ChebyshevBackground.__name__:
                            background_parameters.c0.set_value(fitted_parameters[last_index + 1].value)
                            background_parameters.c1.set_value(fitted_parameters[last_index + 2].value)
                            background_parameters.c2.set_value(fitted_parameters[last_index + 3].value)
                            background_parameters.c3.set_value(fitted_parameters[last_index + 4].value)
                            background_parameters.c4.set_value(fitted_parameters[last_index + 5].value)
                            background_parameters.c5.set_value(fitted_parameters[last_index + 6].value)
                            background_parameters.c6.set_value(fitted_parameters[last_index + 7].value)
                            background_parameters.c7.set_value(fitted_parameters[last_index + 8].value)
                            background_parameters.c8.set_value(fitted_parameters[last_index + 9].value)
                            background_parameters.c9.set_value(fitted_parameters[last_index + 10].value)
                            last_index += 10
                        elif key == ExpDecayBackground.__name__:
                            background_parameters.a0.set_value(fitted_parameters[last_index + 1].value)
                            background_parameters.b0.set_value(fitted_parameters[last_index + 2].value)
                            background_parameters.a1.set_value(fitted_parameters[last_index + 3].value)
                            background_parameters.b1.set_value(fitted_parameters[last_index + 4].value)
                            background_parameters.a2.set_value(fitted_parameters[last_index + 5].value)
                            background_parameters.b2.set_value(fitted_parameters[last_index + 6].value)
                            last_index += 6

        if not self.instrumental_parameters is None:
            for instrumental_parameters in self.instrumental_parameters:
                instrumental_parameters.U.set_value(fitted_parameters[last_index + 1].value)
                instrumental_parameters.V.set_value(fitted_parameters[last_index + 2].value)
                instrumental_parameters.W.set_value(fitted_parameters[last_index + 3].value)
                instrumental_parameters.a.set_value(fitted_parameters[last_index + 4].value)
                instrumental_parameters.b.set_value(fitted_parameters[last_index + 5].value)
                instrumental_parameters.c.set_value(fitted_parameters[last_index + 6].value)
                last_index += 6

        if not self.shift_parameters is None:
            for key in self.shift_parameters.keys():
                shift_parameters_list = self.get_shift_parameters(key)

                if not shift_parameters_list is None:
                    for shift_parameters in shift_parameters_list:
                        if key == Lab6TanCorrection.__name__:
                            shift_parameters.ax.set_value(fitted_parameters[last_index + 1].value)
                            shift_parameters.bx.set_value(fitted_parameters[last_index + 2].value)
                            shift_parameters.cx.set_value(fitted_parameters[last_index + 3].value)
                            shift_parameters.dx.set_value(fitted_parameters[last_index + 4].value)
                            shift_parameters.ex.set_value(fitted_parameters[last_index + 5].value)
                            last_index += 5
                        elif key == ZeroError.__name__:
                            shift_parameters.shift.set_value(fitted_parameters[last_index + 1].value)
                            last_index += 1
                        elif key == SpecimenDisplacement.__name__:
                            shift_parameters.displacement.set_value(fitted_parameters[last_index + 1].value)
                            last_index += 1

        if not self.size_parameters is None:
            for size_parameters in self.size_parameters:
                size_parameters.mu.set_value(fitted_parameters[last_index + 1].value)
                if size_parameters.distribution == Distribution.DELTA:
                    last_index += 1
                else:
                    size_parameters.sigma.set_value(fitted_parameters[last_index + 2].value)
                    if size_parameters.shape == Shape.WULFF:
                        size_parameters.truncation.set_value(fitted_parameters[last_index + 3].value)
                        last_index += 3
                    else:
                        last_index += 2

        if not self.strain_parameters is None:
            for strain_parameters in self.strain_parameters:
                if isinstance(strain_parameters, InvariantPAH):
                    strain_parameters.aa.set_value(fitted_parameters[last_index + 1].value)
                    strain_parameters.bb.set_value(fitted_parameters[last_index + 2].value)
                    strain_parameters.e1.set_value(fitted_parameters[last_index + 3].value) # in realtà è E1 dell'invariante PAH
                    strain_parameters.e2.set_value(fitted_parameters[last_index + 4].value) # in realtà è E1 dell'invariante PAH
                    strain_parameters.e3.set_value(fitted_parameters[last_index + 5].value) # in realtà è E1 dell'invariante PAH
                    strain_parameters.e4.set_value(fitted_parameters[last_index + 6].value) # in realtà è E4 dell'invariante PAH
                    strain_parameters.e5.set_value(fitted_parameters[last_index + 7].value) # in realtà è E4 dell'invariante PAH
                    strain_parameters.e6.set_value(fitted_parameters[last_index + 8].value) # in realtà è E4 dell'invariante PAH
                    last_index += 8
                elif isinstance(strain_parameters, KrivoglazWilkensModel):
                    strain_parameters.rho.set_value(fitted_parameters[last_index + 1].value)
                    strain_parameters.Re.set_value(fitted_parameters[last_index + 2].value)
                    strain_parameters.Ae.set_value(fitted_parameters[last_index + 3].value)
                    strain_parameters.Be.set_value(fitted_parameters[last_index + 4].value)
                    strain_parameters.As.set_value(fitted_parameters[last_index + 5].value)
                    strain_parameters.Bs.set_value(fitted_parameters[last_index + 6].value)
                    strain_parameters.mix.set_value(fitted_parameters[last_index + 7].value)
                    strain_parameters.b.set_value(fitted_parameters[last_index + 8].value)
                    last_index += 8
                elif isinstance(strain_parameters, WarrenModel):
                    strain_parameters.average_cell_parameter.set_value(fitted_parameters[last_index + 1].value)
                    last_index += 1

        self.replace_parameters(fitted_parameters)
        self.evaluate_functions()

        return self
    
    def from_fitted_errors(self, errors):
        last_index = -1

        if not self.fit_initialization.incident_radiations is None:
            for index in range(len(self.fit_initialization.incident_radiations)):
                incident_radiation = self.fit_initialization.incident_radiations[index]
                incident_radiation.wavelength.error = errors[last_index + 1]

                last_index += 1

                if not incident_radiation.is_single_wavelength:

                    for secondary_wavelength, secondary_wavelength_weigth in zip(incident_radiation.secondary_wavelengths,
                                                                                 incident_radiation.secondary_wavelengths_weights):
                        secondary_wavelength.error = errors[last_index + 1]
                        secondary_wavelength_weigth.error = errors[last_index + 2]
                        last_index += 2

        if not self.fit_initialization.crystal_structures is None:
            for index in range(len(self.fit_initialization.crystal_structures)):
                crystal_structure = self.fit_initialization.crystal_structures[index]

                crystal_structure.a.error = errors[last_index + 1]
                crystal_structure.b.error = errors[last_index + 2]
                crystal_structure.c.error = errors[last_index + 3]
                crystal_structure.alpha.error = errors[last_index + 4]
                crystal_structure.beta.error = errors[last_index + 5]
                crystal_structure.gamma.error = errors[last_index + 6]

                if crystal_structure.use_structure:
                    crystal_structure.intensity_scale_factor.error = errors[last_index + 7]
                    last_index += 7
                else:
                    last_index += 6

                for reflection_index in range(crystal_structure.get_reflections_count()):
                    crystal_structure.get_reflection(reflection_index).intensity.error = errors[last_index+reflection_index]

                last_index += crystal_structure.get_reflections_count()

        if not self.fit_initialization.thermal_polarization_parameters is None:
            for thermal_polarization_parameters in self.fit_initialization.thermal_polarization_parameters:
                if not thermal_polarization_parameters.debye_waller_factor is None:
                    thermal_polarization_parameters.debye_waller_factor.error = errors[last_index + 1]
                    last_index += 1

        if not self.background_parameters is None:
            for key in self.background_parameters.keys():
                background_parameters_list = self.get_background_parameters(key)

                if not background_parameters_list is None:
                    for background_parameters in background_parameters_list:
                        if key == ChebyshevBackground.__name__:
                            background_parameters.c0.error = errors[last_index + 1]
                            background_parameters.c1.error = errors[last_index + 2]
                            background_parameters.c2.error = errors[last_index + 3]
                            background_parameters.c3.error = errors[last_index + 4]
                            background_parameters.c4.error = errors[last_index + 5]
                            background_parameters.c5.error = errors[last_index + 6]
                            background_parameters.c6.error = errors[last_index + 7]
                            background_parameters.c7.error = errors[last_index + 8]
                            background_parameters.c8.error = errors[last_index + 9]
                            background_parameters.c9.error = errors[last_index + 10]
                            last_index += 10
                        elif key == ExpDecayBackground.__name__:
                            background_parameters.a0.error = errors[last_index + 1]
                            background_parameters.b0.error = errors[last_index + 2]
                            background_parameters.a1.error = errors[last_index + 3]
                            background_parameters.b1.error = errors[last_index + 4]
                            background_parameters.a2.error = errors[last_index + 5]
                            background_parameters.b2.error = errors[last_index + 6]
                            last_index += 6

        if not self.instrumental_parameters is None:
            for instrumental_parameters in self.instrumental_parameters:
                instrumental_parameters.U.error = errors[last_index + 1]
                instrumental_parameters.V.error = errors[last_index + 2]
                instrumental_parameters.W.error = errors[last_index + 3]
                instrumental_parameters.a.error = errors[last_index + 4]
                instrumental_parameters.b.error = errors[last_index + 5]
                instrumental_parameters.c.error = errors[last_index + 6]
                last_index += 6

        if not self.shift_parameters is None:
            for key in self.shift_parameters.keys():
                shift_parameters_list = self.get_shift_parameters(key)

                if not shift_parameters_list is None:
                    for shift_parameters in shift_parameters_list:
                        if key == Lab6TanCorrection.__name__:
                            shift_parameters.ax.error = errors[last_index + 1]
                            shift_parameters.bx.error = errors[last_index + 2]
                            shift_parameters.cx.error = errors[last_index + 3]
                            shift_parameters.dx.error = errors[last_index + 4]
                            shift_parameters.ex.error = errors[last_index + 5]
                            last_index += 5
                        elif key == ZeroError.__name__:
                            shift_parameters.shift.error = errors[last_index + 1]
                            last_index += 1
                        elif key == SpecimenDisplacement.__name__:
                            shift_parameters.displacement.error = errors[last_index + 1]
                            last_index += 1

        if not self.size_parameters is None:
            for size_parameters in self.size_parameters:
                size_parameters.mu.error    = errors[last_index + 1]
                if size_parameters.distribution == Distribution.DELTA:
                    last_index += 1
                else:
                    size_parameters.sigma.error = errors[last_index + 2]
                    if size_parameters.shape == Shape.WULFF:
                        size_parameters.truncation.error = errors[last_index + 3]
                        last_index += 3
                    else:
                        last_index += 2

        if not self.strain_parameters is None:
            for strain_parameters in self.strain_parameters:
                if isinstance(strain_parameters, InvariantPAH):
                    strain_parameters.aa.error = errors[last_index + 1]
                    strain_parameters.bb.error = errors[last_index + 2]
                    strain_parameters.e1.error = errors[last_index + 3] # in realtà è E1 dell'invariante PAH
                    strain_parameters.e2.error = errors[last_index + 4] # in realtà è E1 dell'invariante PAH
                    strain_parameters.e3.error = errors[last_index + 5] # in realtà è E1 dell'invariante PAH
                    strain_parameters.e4.error = errors[last_index + 6] # in realtà è E4 dell'invariante PAH
                    strain_parameters.e5.error = errors[last_index + 7] # in realtà è E4 dell'invariante PAH
                    strain_parameters.e6.error = errors[last_index + 8] # in realtà è E4 dell'invariante PAH
                    last_index += 8
                elif isinstance(strain_parameters, KrivoglazWilkensModel):
                    strain_parameters.rho.error = errors[last_index + 1]
                    strain_parameters.Re.error = errors[last_index + 2]
                    strain_parameters.Ae.error = errors[last_index + 3]
                    strain_parameters.Be.error = errors[last_index + 4]
                    strain_parameters.As.error = errors[last_index + 5]
                    strain_parameters.Bs.error = errors[last_index + 6]
                    strain_parameters.mix.error = errors[last_index + 7]
                    strain_parameters.b.error = errors[last_index + 8]
                    last_index += 8
                elif isinstance(strain_parameters, WarrenModel):
                    strain_parameters.average_cell_parameter.error = errors[last_index + 1]
                    last_index += 1

    def from_fitted_parameters_and_errors(self, fitted_parameters, errors):
        last_index = -1

        if not self.fit_initialization.incident_radiations is None:
            for index in range(len(self.fit_initialization.incident_radiations)):
                incident_radiation = self.fit_initialization.incident_radiations[index]
                incident_radiation.wavelength.set_value(fitted_parameters[last_index + 1].value)
                incident_radiation.wavelength.error = errors[last_index + 1]

                last_index += 1

                if not incident_radiation.is_single_wavelength:
                    for secondary_wavelength, secondary_wavelength_weigth in zip(incident_radiation.secondary_wavelengths,
                                                                                 incident_radiation.secondary_wavelengths_weights):
                        secondary_wavelength.set_value(fitted_parameters[last_index + 1].value)
                        secondary_wavelength_weigth.set_value(fitted_parameters[last_index + 2].value)
                        secondary_wavelength.error = errors[last_index + 1]
                        secondary_wavelength_weigth.error = errors[last_index + 2]
                        last_index += 2

        if not self.fit_initialization.crystal_structures is None:
            for index in range(len(self.fit_initialization.crystal_structures)):
                crystal_structure = self.fit_initialization.crystal_structures[index]

                crystal_structure.a.set_value(fitted_parameters[last_index + 1].value)
                crystal_structure.b.set_value(fitted_parameters[last_index + 2].value)
                crystal_structure.c.set_value(fitted_parameters[last_index + 3].value)
                crystal_structure.alpha.set_value(fitted_parameters[last_index + 4].value)
                crystal_structure.beta.set_value(fitted_parameters[last_index + 5].value)
                crystal_structure.gamma.set_value(fitted_parameters[last_index + 6].value)
                crystal_structure.a.error = errors[last_index + 1]
                crystal_structure.b.error = errors[last_index + 2]
                crystal_structure.c.error = errors[last_index + 3]
                crystal_structure.alpha.error = errors[last_index + 4]
                crystal_structure.beta.error = errors[last_index + 5]
                crystal_structure.gamma.error = errors[last_index + 6]

                if crystal_structure.use_structure:
                    crystal_structure.intensity_scale_factor.set_value(fitted_parameters[last_index + 7].value)
                    crystal_structure.intensity_scale_factor.error = errors[last_index + 7]
                    last_index += 7
                else:
                    last_index += 6

                for reflection_index in range(crystal_structure.get_reflections_count()):
                    intensity = crystal_structure.get_reflection(reflection_index).intensity
                    intensity.set_value(fitted_parameters[last_index + 1 + reflection_index].value)
                    intensity.error = errors[last_index+reflection_index]

                last_index += crystal_structure.get_reflections_count()

        if not self.fit_initialization.thermal_polarization_parameters is None:
            for thermal_polarization_parameters in self.fit_initialization.thermal_polarization_parameters:
                if not thermal_polarization_parameters.debye_waller_factor is None:
                    thermal_polarization_parameters.debye_waller_factor.set_value(fitted_parameters[last_index + 1].value)
                    thermal_polarization_parameters.debye_waller_factor.error = errors[last_index + 1]
                    last_index += 1

        if not self.background_parameters is None:
            for key in self.background_parameters.keys():
                background_parameters_list = self.get_background_parameters(key)

                if not background_parameters_list is None:
                    for background_parameters in background_parameters_list:
                        if key == ChebyshevBackground.__name__:
                            background_parameters.c0.set_value(fitted_parameters[last_index + 1].value)
                            background_parameters.c1.set_value(fitted_parameters[last_index + 2].value)
                            background_parameters.c2.set_value(fitted_parameters[last_index + 3].value)
                            background_parameters.c3.set_value(fitted_parameters[last_index + 4].value)
                            background_parameters.c4.set_value(fitted_parameters[last_index + 5].value)
                            background_parameters.c5.set_value(fitted_parameters[last_index + 6].value)
                            background_parameters.c6.set_value(fitted_parameters[last_index + 7].value)
                            background_parameters.c7.set_value(fitted_parameters[last_index + 8].value)
                            background_parameters.c8.set_value(fitted_parameters[last_index + 9].value)
                            background_parameters.c9.set_value(fitted_parameters[last_index + 10].value)
                            background_parameters.c0.error = errors[last_index + 1]
                            background_parameters.c1.error = errors[last_index + 2]
                            background_parameters.c2.error = errors[last_index + 3]
                            background_parameters.c3.error = errors[last_index + 4]
                            background_parameters.c4.error = errors[last_index + 5]
                            background_parameters.c5.error = errors[last_index + 6]
                            background_parameters.c6.error = errors[last_index + 7]
                            background_parameters.c7.error = errors[last_index + 8]
                            background_parameters.c8.error = errors[last_index + 9]
                            background_parameters.c9.error = errors[last_index + 10]
                            last_index += 10
                        elif key == ExpDecayBackground.__name__:
                            background_parameters.a0.set_value(fitted_parameters[last_index + 1].value)
                            background_parameters.b0.set_value(fitted_parameters[last_index + 2].value)
                            background_parameters.a1.set_value(fitted_parameters[last_index + 3].value)
                            background_parameters.b1.set_value(fitted_parameters[last_index + 4].value)
                            background_parameters.a2.set_value(fitted_parameters[last_index + 5].value)
                            background_parameters.b2.set_value(fitted_parameters[last_index + 6].value)
                            background_parameters.a0.error = errors[last_index + 1]
                            background_parameters.b0.error = errors[last_index + 2]
                            background_parameters.a1.error = errors[last_index + 3]
                            background_parameters.b1.error = errors[last_index + 4]
                            background_parameters.a2.error = errors[last_index + 5]
                            background_parameters.b2.error = errors[last_index + 6]
                            last_index += 6

        if not self.instrumental_parameters is None:
            for instrumental_parameters in self.instrumental_parameters:
                instrumental_parameters.U.set_value(fitted_parameters[last_index + 1].value)
                instrumental_parameters.V.set_value(fitted_parameters[last_index + 2].value)
                instrumental_parameters.W.set_value(fitted_parameters[last_index + 3].value)
                instrumental_parameters.a.set_value(fitted_parameters[last_index + 4].value)
                instrumental_parameters.b.set_value(fitted_parameters[last_index + 5].value)
                instrumental_parameters.c.set_value(fitted_parameters[last_index + 6].value)
                instrumental_parameters.U.error = errors[last_index + 1]
                instrumental_parameters.V.error = errors[last_index + 2]
                instrumental_parameters.W.error = errors[last_index + 3]
                instrumental_parameters.a.error = errors[last_index + 4]
                instrumental_parameters.b.error = errors[last_index + 5]
                instrumental_parameters.c.error = errors[last_index + 6]
                last_index += 6

        if not self.shift_parameters is None:
            for key in self.shift_parameters.keys():
                shift_parameters_list = self.get_shift_parameters(key)

                if not shift_parameters_list is None:
                    for shift_parameters in shift_parameters_list:
                        if key == Lab6TanCorrection.__name__:
                            shift_parameters.ax.set_value(fitted_parameters[last_index + 1].value)
                            shift_parameters.bx.set_value(fitted_parameters[last_index + 2].value)
                            shift_parameters.cx.set_value(fitted_parameters[last_index + 3].value)
                            shift_parameters.dx.set_value(fitted_parameters[last_index + 4].value)
                            shift_parameters.ex.set_value(fitted_parameters[last_index + 5].value)
                            shift_parameters.ax.error = errors[last_index + 1]
                            shift_parameters.bx.error = errors[last_index + 2]
                            shift_parameters.cx.error = errors[last_index + 3]
                            shift_parameters.dx.error = errors[last_index + 4]
                            shift_parameters.ex.error = errors[last_index + 5]
                            last_index += 5
                        elif key == ZeroError.__name__:
                            shift_parameters.shift.set_value(fitted_parameters[last_index + 1].value)
                            shift_parameters.shift.error = errors[last_index + 1]
                            last_index += 1
                        elif key == SpecimenDisplacement.__name__:
                            shift_parameters.displacement.set_value(fitted_parameters[last_index + 1].value)
                            shift_parameters.displacement.error = errors[last_index + 1]
                            last_index += 1

        if not self.size_parameters is None:
            for size_parameters in self.size_parameters:
                size_parameters.mu.set_value(fitted_parameters[last_index + 1].value)
                size_parameters.mu.error    = errors[last_index + 1]
                if size_parameters.distribution == Distribution.DELTA:
                    last_index += 1
                else:
                    size_parameters.sigma.set_value(fitted_parameters[last_index + 2].value)
                    size_parameters.sigma.error = errors[last_index + 2]
                    if size_parameters.shape == Shape.WULFF:
                        size_parameters.truncation.set_value(fitted_parameters[last_index + 3].value)
                        size_parameters.truncation.error = errors[last_index + 3]
                        last_index += 3
                    else:
                        last_index += 2

        if not self.strain_parameters is None:
            for strain_parameters in self.strain_parameters:
                if isinstance(strain_parameters, InvariantPAH):
                    strain_parameters.aa.set_value(fitted_parameters[last_index + 1].value)
                    strain_parameters.bb.set_value(fitted_parameters[last_index + 2].value)
                    strain_parameters.e1.set_value(fitted_parameters[last_index + 3].value) # in realtà è E1 dell'invariante PAH
                    strain_parameters.e2.set_value(fitted_parameters[last_index + 4].value) # in realtà è E1 dell'invariante PAH
                    strain_parameters.e3.set_value(fitted_parameters[last_index + 5].value) # in realtà è E1 dell'invariante PAH
                    strain_parameters.e4.set_value(fitted_parameters[last_index + 6].value) # in realtà è E4 dell'invariante PAH
                    strain_parameters.e5.set_value(fitted_parameters[last_index + 7].value) # in realtà è E4 dell'invariante PAH
                    strain_parameters.e6.set_value(fitted_parameters[last_index + 8].value) # in realtà è E4 dell'invariante PAH
                    strain_parameters.aa.error = errors[last_index + 1]
                    strain_parameters.bb.error = errors[last_index + 2]
                    strain_parameters.e1.error = errors[last_index + 3] # in realtà è E1 dell'invariante PAH
                    strain_parameters.e2.error = errors[last_index + 4] # in realtà è E1 dell'invariante PAH
                    strain_parameters.e3.error = errors[last_index + 5] # in realtà è E1 dell'invariante PAH
                    strain_parameters.e4.error = errors[last_index + 6] # in realtà è E4 dell'invariante PAH
                    strain_parameters.e5.error = errors[last_index + 7] # in realtà è E4 dell'invariante PAH
                    strain_parameters.e6.error = errors[last_index + 8] # in realtà è E4 dell'invariante PAH
                    last_index += 8
                elif isinstance(strain_parameters, KrivoglazWilkensModel):
                    strain_parameters.rho.set_value(fitted_parameters[last_index + 1].value)
                    strain_parameters.Re.set_value(fitted_parameters[last_index + 2].value)
                    strain_parameters.Ae.set_value(fitted_parameters[last_index + 3].value)
                    strain_parameters.Be.set_value(fitted_parameters[last_index + 4].value)
                    strain_parameters.As.set_value(fitted_parameters[last_index + 5].value)
                    strain_parameters.Bs.set_value(fitted_parameters[last_index + 6].value)
                    strain_parameters.mix.set_value(fitted_parameters[last_index + 7].value)
                    strain_parameters.b.set_value(fitted_parameters[last_index + 8].value)
                    strain_parameters.rho.error = errors[last_index + 1]
                    strain_parameters.Re.error = errors[last_index + 2]
                    strain_parameters.Ae.error = errors[last_index + 3]
                    strain_parameters.Be.error = errors[last_index + 4]
                    strain_parameters.As.error = errors[last_index + 5]
                    strain_parameters.Bs.error = errors[last_index + 6]
                    strain_parameters.mix.error = errors[last_index + 7]
                    strain_parameters.b.error = errors[last_index + 8]
                    last_index += 8
                elif isinstance(strain_parameters, WarrenModel):
                    strain_parameters.average_cell_parameter.set_value(fitted_parameters[last_index + 1].value)
                    strain_parameters.average_cell_parameter.error = errors[last_index + 1]
                    last_index += 1

        self.replace_parameters(fitted_parameters)
        self.evaluate_functions()

        return self

    def is_compatibile(self, other_fit_global_parameters):
        if other_fit_global_parameters is None: return False

        parameters = self.get_parameters()
        other_parameters = other_fit_global_parameters.get_parameters()

        if len(parameters) != len(other_parameters): return False

        for index in range(0, len(parameters)):
            if parameters[index].parameter_name != other_parameters[index].parameter_name: return False

        return True

    @classmethod
    def parameters_have_functions(cls, parameters):
        for parameter in parameters:
            if parameter.function: return True
        return False

    @classmethod
    def compute_functions(cls, parameters, free_input_parameters, free_output_parameters):

        if cls.parameters_have_functions(parameters) or free_output_parameters.get_parameters_count() > 0:
            python_code = "import numpy\nfrom numpy import *\n\n"
            python_code += free_input_parameters.to_python_code()

            parameters_dictionary_fit = {}

            for parameter in parameters:
                if not parameter.function:
                    python_code += parameter.to_parameter_text() + "\n"
                else:
                    parameters_dictionary_fit[parameter.parameter_name] = numpy.nan
                    python_code += parameter.to_python_code() + "\n"

            parameters_dictionary_out, code_out = free_output_parameters.get_functions_data()

            python_code += code_out

            parameters_dictionary = {}
            parameters_dictionary.update(parameters_dictionary_fit)
            parameters_dictionary.update(parameters_dictionary_out)

            exec(python_code, parameters_dictionary)

            for parameter in parameters:
                if parameter.function:
                    parameter.value = float(parameters_dictionary[parameter.parameter_name])

            free_output_parameters.set_functions_values(parameters_dictionary)

    def __str__(self):
        parameters = self.get_parameters(good_only=True)
        text = ""

        for parameter in parameters:
            text += str(parameter) + "\n"

        return text

class FitSpaceParameters:
    def __init__(self, fit_global_parameters):
        s_max   = fit_global_parameters.fit_initialization.fft_parameters.s_max
        n_steps = fit_global_parameters.fit_initialization.fft_parameters.n_step

        self.ds = s_max/(n_steps - 1)
        self.dL = 1 / (2 * s_max)

        self.L_max = (n_steps - 1) * self.dL
        self.L = numpy.linspace(self.dL, self.L_max + self.dL, n_steps)
