import numpy
import copy

from orangecontrib.wonder.util import congruence

PARAM_FIX		= 1 << 0
PARAM_SYS		= 1 << 1
PARAM_REF		= 1 << 2
PARAM_HWMIN		= -numpy.finfo('d').max
PARAM_HWMAX		= numpy.finfo('d').max
PARAM_ERR		= numpy.finfo('d').max

class Boundary:
    def __init__(self, min_value = PARAM_HWMIN, max_value = PARAM_HWMAX):
        congruence.checkGreaterOrEqualThan(max_value, min_value, "Max Value", "Min Value")

        self.min_value = min_value
        self.max_value = max_value

class FitParameter:
    def __init__(self,
                 value=None,
                 parameter_name="",
                 boundary=None,
                 fixed=False,
                 function = False,
                 function_value = "",
                 step=PARAM_ERR,
                 error=None,
                 input_parameter = False,
                 output_parameter = False):
        self.parameter_name = parameter_name
        self.value = value
        self.fixed = fixed
        self.function = function
        self.function_value = function_value
        self.error = error

        if self.function:
            if self.function_value is None: raise ValueError("Function Value cannot be None")
            if self.function_value.strip() == "": raise ValueError("Function Value cannot be an empty string")

            self.fixed = False
            self.boundary = None

        if self.fixed:
            self.boundary = Boundary(min_value=self.value, max_value=self.value + 1e-12) # just a trick, to be done in a better way
        else:
            if boundary is None: self.boundary = Boundary()
            else: self.boundary = boundary

        if step is None:
            self.step = PARAM_ERR
        else:
            self.step = step

        self.input_parameter = input_parameter
        self.output_parameter = output_parameter

    def set_value(self, value):
        self.value = value
        self.check_value()

    def rescale(self, scaling_factor = 100):
        if not self.value is None: self.value *= scaling_factor
        if not self.boundary is None:
            if self.boundary.min_value != PARAM_HWMIN: self.boundary.min_value *= scaling_factor
            if self.boundary.max_value != PARAM_HWMAX: self.boundary.max_value *= scaling_factor

    def check_value(self):
        if self.value is None: raise ValueError("Parameter Value cannot be None")
        if self.function:
            if self.function_value is None: raise ValueError("Function Value cannot be None")
            if self.function_value.strip() == "": raise ValueError("Function Value cannot be an empty string")
        else:
            if not self.fixed:
                if self.boundary is None: self.boundary = Boundary()

                if self.boundary.min_value != PARAM_HWMIN:
                    if self.value < self.boundary.min_value:
                        self.value = self.boundary.min_value + (self.boundary.min_value - self.value)/2

                if self.boundary.max_value != PARAM_HWMAX:
                    if self.value > self.boundary.max_value:
                        self.value = max(self.boundary.min_value,
                                         self.boundary.max_value - (self.value - self.boundary.max_value)/2)
            else:
                if self.boundary is None: self.boundary = Boundary(min_value=self.value, max_value=self.value + 1e-12)

    def __str__(self):
        if self.function:
            text = self.to_python_code() + " = " + str(self.value)
        else:
            text = self.parameter_name + " " + str(self.value)

            if self.fixed:
                text += ", fixed"
            else:
                if not self.boundary is None:

                    if not self.boundary.min_value == PARAM_HWMIN:
                        text += ", min " + str(self.boundary.min_value)

                    if not self.boundary.max_value == PARAM_HWMAX:
                        text += ", max " + str(self.boundary.max_value)

        if self.is_variable() and not self.error is None:
            text += ", sd = \u00B1 " + str(self.error)

        return text

    def to_parameter_text(self):
        return self.parameter_name + " = " + str(self.value)

    def to_python_code(self):
        if not self.function:
            raise ValueError("Fit parameter " + self.parameter_name + "is not a function")

        return self.parameter_name + " = " + self.function_value

    def duplicate(self):
        return copy.deepcopy(self)

    def is_variable(self):
        return not self.fixed and not self.function


class ParametersList:
    @classmethod
    def get_parameters_prefix(cls):
        return ""

    def duplicate(self):
        return copy.deepcopy(self)

class FreeInputParameters(ParametersList):
    def __init__(self):
        self.parameters_dictionary = {}
    
    def _check_dictionary(self):
        if not hasattr(self, "parameters_dictionary"):
            self.parameters_dictionary = {}

    def get_parameters_names(self):
        self._check_dictionary()
        return self.parameters_dictionary.keys()

    def get_parameters_count(self):
        self._check_dictionary()
        return len(self.parameters_dictionary)

    def set_parameter(self, name, value):
        self._check_dictionary()
        self.parameters_dictionary[name] = value

    def get_parameter(self, name):
        self._check_dictionary()
        return self.parameters_dictionary[name]

    def append(self,parameters_dictionary):
        if not parameters_dictionary is None:
            for name in parameters_dictionary.keys():
                self.set_parameter(name, parameters_dictionary[name])

    def to_text(self):
        text = "FREE INPUT PARAMETERS\n"
        text += "-----------------------------------\n"

        if not self.parameters_dictionary is None:
            for name in self.parameters_dictionary.keys():
                text += name + " = " + str(self.get_parameter(name)) + "\n"

        text += "-----------------------------------\n"

        return text

    def as_parameters(self):
        parameters = []

        if not self.parameters_dictionary is None:
            for name in self.parameters_dictionary.keys():
                fit_parameter = FitParameter(value=self.parameters_dictionary[name],
                                             parameter_name=name,
                                             fixed=True,
                                             input_parameter=True)

                parameters.append(fit_parameter)

        return parameters

    def parse_values(self, text):
        self.parameters_dictionary.clear()

        is_empty = False

        try:
            congruence.checkEmptyString(text, "")
        except:
            is_empty = True

        if not is_empty:
            lines = text.splitlines()

            for i in range(len(lines)):
                is_line_empty = False
                try:
                    congruence.checkEmptyString(lines[i], "")
                except:
                    is_line_empty = True

                if not is_line_empty:
                    data = lines[i].strip().split("=")

                    if len(data) != 2: raise ValueError("Free Output Parameters, malformed line:" + str(i+1))

                    name  = data[0].strip()
                    value = float(data[1].strip())

                    self.set_parameter(name, value)

    def to_python_code(self):
        python_text = ""

        for name in self.parameters_dictionary.keys():
            python_text += name + " = " + str(self.get_parameter(name)) + "\n"

        return python_text


class FreeOutputParameter:
    def __init__(self, expression=None, value=None):
        self.expression = expression
        self.value = value
    
    def duplicate(self):
        return copy.deepcopy(self)

        return FreeOutputParameter(expression=self.expression, value=self.value)
    
class FreeOutputParameters(ParametersList):
    def __init__(self):
        self.parameters_dictionary = {}

    def _check_dictionary(self):
        if not hasattr(self, "parameters_dictionary"):
            self.parameters_dictionary = {}

    def get_parameters_count(self):
        self._check_dictionary()
        return len(self.parameters_dictionary)

    def set_parameter(self, name, parameter=FreeOutputParameter()):
        self._check_dictionary()
        if parameter is None:
            raise ValueError("Parameter object cannot be None")

        self.parameters_dictionary[name] = parameter

    def set_parameter_expression(self, name, expression):
        self._check_dictionary()
        try:
            self.parameters_dictionary[name].expression = expression
        except:
            self.parameters_dictionary[name] = FreeOutputParameter(expression=expression)

    def set_parameter_value(self, name, value):
        self._check_dictionary()
        try:
            self.parameters_dictionary[name].value = value
        except:
            self.parameters_dictionary[name] = FreeOutputParameter(value=value)

    def get_parameter_expression(self, name):
        self._check_dictionary()
        try:
            return self.parameters_dictionary[name].expression
        except:
            raise ValueError("Key " + name + " not found")

    def get_parameter_value(self, name):
        self._check_dictionary()
        try:
            return self.parameters_dictionary[name].value
        except:
            raise ValueError("Key " + name + " not found")

    def get_parameter_formula(self, name):
        self._check_dictionary()
        try:
            return name + " = " + self.parameters_dictionary[name].expression
        except:
            raise ValueError("Key " + name + " not found")

    def get_parameter_full_text(self, name):
        self._check_dictionary()
        try:
            return name + " = " + self.parameters_dictionary[name].expression + " = " + str(self.parameters_dictionary[name].value)
        except:
            raise ValueError("Key " + name + " not found")

    def set_formula(self, formula):
        self._check_dictionary()
        tokens = formula.split("=")
        if len(tokens) != 2: raise ValueError("Formula format not recognized: <name> = <expression>")

        self.set_parameter(name=tokens[0].strip(),
                           parameter=FreeOutputParameter(expression=tokens[1].strip()))

    def append(self, free_output_parameters):
        if not free_output_parameters is None and not free_output_parameters.parameters_dictionary is None:
            for name in free_output_parameters.parameters_dictionary.keys():
                self.set_parameter(name, free_output_parameters.parameters_dictionary[name])

    def parse_formulas(self, text):
        self.parameters_dictionary.clear()

        is_empty = False

        try:
            congruence.checkEmptyString(text, "")
        except:
            is_empty = True

        if not is_empty:
            lines = text.splitlines()

            for i in range(len(lines)):
                is_line_empty = False
                try:
                    congruence.checkEmptyString(lines[i], "")
                except:
                    is_line_empty = True

                if not is_line_empty:
                    data = lines[i].strip().split("=")

                    if len(data) != 2: raise ValueError("Free Output Parameters, malformed line:" + str(i+1))

                    name       = data[0].strip()
                    expression = data[1].strip()

                    self.set_parameter_expression(name, expression)

    def to_python_code(self):
        text = ""

        if not self.parameters_dictionary is None:
            for name in self.parameters_dictionary.keys():
                text += self.get_parameter_formula(name) + "\n"

        return text


    def to_text(self):
        text = "FREE OUTPUT PARAMETERS\n"
        text += "-----------------------------------\n"

        if not self.parameters_dictionary is None:
            for name in self.parameters_dictionary.keys():
                text += self.get_parameter_full_text(name) + "\n"

        text += "-----------------------------------\n"

        return text

    def as_parameters(self):
        if not self.parameters_dictionary is None:
            keys = self.parameters_dictionary.keys()
            parameters = numpy.full(len(keys), None)

            i = 0
            for name in keys:
                parameter = self.parameters_dictionary[name]

                parameters[i] = FitParameter(value=parameter.value,
                                             parameter_name=name,
                                             function=True,
                                             function_value=parameter.expression,
                                             output_parameter=True)
                i += 1

            return parameters
        else:
            return []

    def get_functions_data(self):
        self._check_dictionary()

        parameters_dictionary = {}
        python_code = ""

        for parameter_name in self.parameters_dictionary.keys():
            parameters_dictionary[parameter_name] = numpy.nan
            python_code += self.get_parameter_formula(parameter_name) + "\n"

        return parameters_dictionary, python_code

    def set_functions_values(self, parameters_dictionary):
        for parameter_name in self.parameters_dictionary.keys():
           self.set_parameter_value(parameter_name, float(parameters_dictionary[parameter_name]))
