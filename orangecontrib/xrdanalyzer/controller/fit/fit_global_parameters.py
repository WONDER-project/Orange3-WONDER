import numpy

from orangecontrib.xrdanalyzer.controller.fit.fit_parameter import FitParametersList

class FitGlobalParameters(FitParametersList):

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

    def __init__(self,
                 fit_initialization = None,
                 background_parameters = {},
                 instrumental_parameters = None,
                 shift_parameters = {},
                 size_parameters = None,
                 strain_parameters = None):
        super().__init__()

        self.fit_initialization = fit_initialization
        self.background_parameters = background_parameters
        self.instrumental_parameters = instrumental_parameters
        self.shift_parameters = shift_parameters
        self.size_parameters = size_parameters
        self.strain_parameters = strain_parameters
        self.free_input_parameters = FreeInputParameters()
        self.free_output_parameters = FreeOutputParameters()

        self.n_max_iterations = 10
        self.convergence_reached = False

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


    def get_parameters(self):
        parameters = []

        if not self.fit_initialization is None:
            parameters.extend(self.fit_initialization.get_parameters())

        if not self.background_parameters is None:
            for key in self.background_parameters.keys():
                for background_parameters in self.background_parameters[key]:
                    parameters.extend(background_parameters.get_parameters())

        if not self.instrumental_parameters is None:
            for instrumental_parameters in self.instrumental_parameters:
                parameters.extend(instrumental_parameters.get_parameters())

        if not self.shift_parameters is None:
            for key in self.shift_parameters.keys():
                for shift_parameters in self.shift_parameters[key]:
                    parameters.extend(shift_parameters.get_parameters())

        if not self.size_parameters is None:
            for size_parameters in self.size_parameters:
                parameters.extend(size_parameters.get_parameters())

        if not self.strain_parameters is None:
            for strain_parameters in self.strain_parameters:
                parameters.extend(strain_parameters.get_parameters())

        return numpy.array(parameters)

    def tuple(self):
        tuple = []

        if not self.fit_initialization is None:
            tuple.extend(self.fit_initialization.tuple())

        if not self.background_parameters is None:
            for key in self.background_parameters.keys():
                for background_parameters in self.background_parameters[key]:
                    tuple.extend(background_parameters.tuple())

        if not self.instrumental_parameters is None:
            for instrumental_parameters in self.instrumental_parameters:
                tuple.extend(instrumental_parameters.tuple())

        if not self.shift_parameters is None:
            for key in self.shift_parameters.keys():
                for shift_parameters in self.shift_parameters[key]:
                    tuple.extend(shift_parameters.tuple())

        if not self.size_parameters is None:
            for size_parameters in self.size_parameters:
                tuple.extend(size_parameters.tuple())

        if not self.strain_parameters is None:
            for strain_parameters in self.strain_parameters:
                tuple.extend(strain_parameters.tuple())

        return tuple

    def append_to_tuple(self, parameters, boundaries):

        if not self.fit_initialization is None:
            parameters, boundaries = self.fit_initialization.append_to_tuple(parameters, boundaries)

        if not self.background_parameters is None:
            for key in self.background_parameters.keys():
                for background_parameters in self.background_parameters[key]:
                    parameters, boundaries = background_parameters.append_to_tuple(parameters, boundaries)

        if not self.instrumental_parameters is None:
            for instrumental_parameters in self.instrumental_parameters:
                parameters, boundaries = instrumental_parameters.append_to_tuple(parameters, boundaries)

        if not self.shift_parameters is None:
            for key in self.shift_parameters.keys():
                for shift_parameters in self.shift_parameters[key]:
                    parameters, boundaries = shift_parameters.append_to_tuple(parameters, boundaries)

        if not self.size_parameters is None:
            for size_parameters in self.size_parameters:
                parameters, boundaries = size_parameters.append_to_tuple(parameters, boundaries)

        if not self.strain_parameters is None:
            for strain_parameters in self.strain_parameters:
                parameters, boundaries = strain_parameters.append_to_tuple(parameters, boundaries)

        return parameters, boundaries

    def to_text(self):
        
        text = "FIT GLOBAL PARAMETERS\n"
        text += "###################################\n\n"

        text += self.free_input_parameters.to_text()

        if not self.fit_initialization is None:
            text += self.fit_initialization.to_text()

        if not self.background_parameters is None:
            for key in self.background_parameters.keys():
                for background_parameters in self.background_parameters[key]:
                    text += background_parameters.to_text()
            
        if not self.instrumental_parameters is None:
            for instrumental_parameters in self.instrumental_parameters:
                text += instrumental_parameters.to_text()
            
        if not self.shift_parameters is None:
            for key in self.shift_parameters.keys():
                for shift_parameters in self.shift_parameters[key]:
                    text += shift_parameters.to_text()

        if not self.size_parameters is None:
            for size_parameters in self.size_parameters:
                text += size_parameters.to_text()

        if not self.strain_parameters is None:
            for strain_parameters in self.strain_parameters:
                text += strain_parameters.to_text()
        
        text += self.free_output_parameters.to_text()

        text += "\n###################################\n"

        return text

    def evaluate_functions(self):
        if self.has_functions() or self.free_output_parameters.get_parameters_count() > 0:
            python_code = "import numpy\nfrom numpy import *\n\n"

            python_code += self.free_input_parameters.to_python_code()

            python_code += self.get_available_parameters()

            parameters_dictionary_fit, code_fit = self.get_functions_data()
            parameters_dictionary_out, code_out = self.free_output_parameters.get_functions_data()

            python_code += code_fit
            python_code += code_out

            parameters_dictionary = {}
            parameters_dictionary.update(parameters_dictionary_fit)
            parameters_dictionary.update(parameters_dictionary_out)

            exec(python_code, parameters_dictionary)

            self.set_functions_values(parameters_dictionary)
            self.free_output_parameters.set_functions_values(parameters_dictionary)

    def duplicate(self):
        self.evaluate_functions()

        fit_initialization = None if self.fit_initialization is None else self.fit_initialization.duplicate()

        if self.background_parameters is None:
            background_parameters = None
        else:
            background_parameters = {}
            for key in self.background_parameters.keys():
                background_parameters_list = self.get_background_parameters(key)

                if background_parameters_list is None: background_parameters[key] = None
                else:
                    dimension = len(background_parameters_list)
                    background_parameters[key] = [None]*dimension
                    for index in range(dimension):
                        background_parameters[key][index]= background_parameters_list[index].duplicate()
        
        if self.instrumental_parameters is None: instrumental_parameters = None
        else:
            dimension = len(self.instrumental_parameters)
            instrumental_parameters = [None]*dimension
            for index in range(dimension):
                instrumental_parameters[index] = self.instrumental_parameters[index].duplicate()
        
        if self.shift_parameters is None:
            shift_parameters = None
        else:
            shift_parameters = {}
            for key in self.shift_parameters.keys():
                shift_parameters_list = self.get_shift_parameters(key)

                if shift_parameters_list is None: shift_parameters[key] = None
                else:
                    dimension = len(shift_parameters_list)
                    shift_parameters[key] = [None]*dimension
                    for index in range(dimension):
                        shift_parameters[key][index]= shift_parameters_list[index].duplicate() 

        if self.size_parameters is None: size_parameters = None
        else:
            dimension = len(self.size_parameters)
            size_parameters = [None]*dimension
            for index in range(dimension):
                size_parameters[index] = self.size_parameters[index].duplicate()

        if self.strain_parameters is None: strain_parameters = None
        else:
            dimension = len(self.strain_parameters)
            strain_parameters = [None]*dimension
            for index in range(dimension):
                strain_parameters[index] = self.strain_parameters[index].duplicate()


        fit_global_parameters = FitGlobalParameters(fit_initialization=fit_initialization,
                                                    background_parameters=background_parameters,
                                                    instrumental_parameters=instrumental_parameters,
                                                    shift_parameters=shift_parameters,
                                                    size_parameters=size_parameters,
                                                    strain_parameters=strain_parameters)

        fit_global_parameters.free_input_parameters = self.free_input_parameters.duplicate()
        fit_global_parameters.free_output_parameters = self.free_output_parameters.duplicate()

        return fit_global_parameters

    def is_compatibile(self, other_fit_global_parameters):
        if other_fit_global_parameters is None: return False

        parameters = self.get_parameters()
        other_parameters = other_fit_global_parameters.get_parameters()

        if len(parameters) != len(other_parameters): return False

        for index in range(0, len(parameters)):
            if parameters[index].parameter_name != other_parameters[index].parameter_name: return False

        return True

class FitSpaceParameters:
    def __init__(self, fit_global_parameters):
        s_max   = fit_global_parameters.fit_initialization.fft_parameters.s_max
        n_steps = fit_global_parameters.fit_initialization.fft_parameters.n_step

        self.ds = s_max/(n_steps - 1)
        self.dL = 1 / (2 * s_max)

        self.L_max = (n_steps - 1) * self.dL
        self.L = numpy.linspace(self.dL, self.L_max + self.dL, n_steps)


######################################################################################################
######################################################################################################
######################################################################################################
######################################################################################################


from orangecontrib.xrdanalyzer.controller.fit.fit_parameter import FitParameter, FreeInputParameters, FreeOutputParameters, Boundary
from orangecontrib.xrdanalyzer.controller.fit.init.fit_initialization import FitInitialization
from orangecontrib.xrdanalyzer.controller.fit.init.crystal_structure import CrystalStructure, Reflection
from orangecontrib.xrdanalyzer.controller.fit.init.fft_parameters import FFTInitParameters
from orangecontrib.xrdanalyzer.controller.fit.instrument.background_parameters import ChebyshevBackground
from orangecontrib.xrdanalyzer.controller.fit.instrument.instrumental_parameters import Caglioti, Lab6TanCorrection
from orangecontrib.xrdanalyzer.controller.fit.microstructure.size import SizeParameters, Distribution, Shape
from orangecontrib.xrdanalyzer.controller.fit.microstructure.strain import InvariantPAHLaueGroup14, InvariantPAH

if __name__ == "__main__":

    fit_global_parameters = FitGlobalParameters()

    fit_global_parameters.free_input_parameters.set_parameter("A", 10)
    fit_global_parameters.free_input_parameters.set_parameter("C", 20)

    parameter_prefix = Caglioti.get_parameters_prefix()
    fit_global_parameters.instrumental_parameters = Caglioti(a=FitParameter(parameter_name=parameter_prefix + "a", value=0.5, boundary=Boundary(min_value=-10, max_value=10)),
                                                             b=FitParameter(parameter_name=parameter_prefix + "b", value=0.001, boundary=Boundary(min_value=0, max_value=10)),
                                                             c=FitParameter(parameter_name=parameter_prefix + "c", function=True, function_value="numpy.exp(A +C)"),
                                                             U=FitParameter(parameter_name=parameter_prefix + "U", function=True, function_value="numpy.exp(-(A +C))"),
                                                             V=FitParameter(parameter_name=parameter_prefix + "V", value=0.001, fixed=True),
                                                             W=FitParameter(parameter_name=parameter_prefix + "W", value=-0.001, fixed=True))

    parameter_prefix = InvariantPAH.get_parameters_prefix()
    fit_global_parameters.strain_parameters = InvariantPAHLaueGroup14(aa=FitParameter(parameter_name=parameter_prefix + "aa", value=2.0, boundary=Boundary(min_value=0, max_value=10)),
                                                                      bb=FitParameter(parameter_name=parameter_prefix + "bb", value=3.0, boundary=Boundary(min_value=0, max_value=10)),
                                                                      e1=FitParameter(parameter_name=parameter_prefix + "e1", function=True, function_value=parameter_prefix + "aa + " + parameter_prefix + "bb"),
                                                                      e4=FitParameter(parameter_name=parameter_prefix + "e4", function=True, function_value=parameter_prefix + "aa**2 + " + parameter_prefix + "bb**2"))


    fit_global_parameters.free_output_parameters.set_formula("out1 = caglioti_U + numpy.abs(caglioti_W)")

    fit_global_parameters.evaluate_functions()

    print(fit_global_parameters.to_text())

    '''
    free_p = FreeInputParameters()

    free_p.set_parameter("A", 10)
    free_p.set_parameter("C", 20)

    free_parameters_python_text = free_p.to_python_code()


    parameter = FitParameter(parameter_name="param1", function=True, function_value="numpy.exp(A +C)")

    out = {parameter.parameter_name : numpy.nan}

    exec("import numpy\n\n" + free_parameters_python_text + parameter.to_python_code(), out)

    parameter.set_value(float(out[parameter.parameter_name]))

    print("OUTPUT", parameter.value)
    '''
