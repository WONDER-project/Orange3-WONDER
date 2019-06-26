import numpy
import inspect
import copy

from orangecontrib.wonder.util import congruence
from orangecontrib.wonder.controller.fit.util.fit_utilities import Utilities
from orangecontrib.wonder.controller.fit.fit_parameter import ParametersList


#---------------------------------------
# DATA STRUCTURES
#---------------------------------------
class DiffractionPoint:
    twotheta = None
    intensity = None
    error = None
    s = None

    def __init__ (self,
                  twotheta = None,
                  intensity = None,
                  error = None,
                  s = None,
                  wavelength = None):
        self.intensity = intensity
        self.error = error

        if not wavelength is None:
            if twotheta is None:
                self.s = s
                self.twotheta = self._get_twotheta_from_s(s, wavelength)
            elif s is None:
                self.twotheta = twotheta
                self.s = self._get_s_from_twotheta(twotheta, wavelength)
        else:
            self.twotheta = twotheta
            self.s = s

        self._check_attributes_congruence()

    def get_array (self):
        return numpy.array([self.twotheta, self.intensity, self.error, self.s])

    @classmethod
    def _get_s_from_twotheta(cls, twotheta, wavelength):
        if twotheta is None: return None

        return Utilities.s(theta=numpy.radians(twotheta/2),
                           wavelength=wavelength.value)

    @classmethod
    def _get_twotheta_from_s(cls, s, wavelength):
        if s is None: return None

        return numpy.degrees(2*Utilities.theta(s=s,
                                               wavelength=wavelength.value))

    def _check_attributes_congruence(self):
        if self.s is None:
            congruence.checkPositiveNumber(self.twotheta, "twotheta")
        if self.twotheta is None:
            congruence.checkPositiveNumber(self.s, "s")

class DiffractionPattern(ParametersList):

    diffraction_pattern = None
    wavelength = None
    is_single_wavelength = True
    secondary_wavelengths = []
    secondary_wavelengths_weights = []
    principal_wavelength_weight = None

    @classmethod
    def get_parameters_prefix(cls):
        return "diffraction_pattern_"

    def __init__(self, n_points = 0, wavelength = None):
        if n_points > 0:
            self.diffraction_pattern = numpy.array([None]*n_points)
        else:
            self.diffraction_pattern = None

        self.wavelength = wavelength
        self.is_single_wavelength = True

    def set_multiple_wavelengths(self, secondary_wavelengths = [], secondary_wavelengths_weights = [], recalculate=True):
        self.is_single_wavelength = False
        self.secondary_wavelengths = secondary_wavelengths
        self.secondary_wavelengths_weights = secondary_wavelengths_weights
        self.principal_wavelength_weight = self.get_principal_wavelenght_weight(recalculate=recalculate)

    def set_single_wavelength(self, wavelength=None, recalculate=True):
        self.is_single_wavelength = True
        self.wavelength = wavelength
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

    def add_diffraction_point (self, diffraction_point):
        if diffraction_point is None: raise ValueError ("Diffraction Point is None")
        if not isinstance(diffraction_point, DiffractionPoint): raise ValueError ("diffraction point should be of type Diffraction Point")

        if self.diffraction_pattern is None:
            self.diffraction_pattern = numpy.array([self.__check_diffraction_point(diffraction_point)])
        else:
            self.diffraction_pattern = numpy.append(self.diffraction_pattern, self.__check_diffraction_point(diffraction_point))

    def set_diffraction_point(self, index, diffraction_point):
        self.__check_diffraction_pattern()
        self.diffraction_pattern[index] = self.__check_diffraction_point(diffraction_point)

    def diffraction_points_count(self):
        return 0 if self.diffraction_pattern is None else len(self.diffraction_pattern)

    def get_diffraction_point(self, index):#
        self.__check_diffraction_pattern()

        return self.diffraction_pattern[index]

    def duplicate(self):
        self.__check_diffraction_pattern()

        return super(DiffractionPattern, self).duplicate()

    def tuples(self):
        data = [[diffraction_point.twotheta, diffraction_point.intensity,diffraction_point.error, diffraction_point.s] for diffraction_point in self.diffraction_pattern]
        data = numpy.array(data)

        return data[:, 0], data[:, 1], data[:, 2], data[:, 3]

    # "PRIVATE METHODS"
    def __check_diffraction_pattern(self):
        if self.diffraction_pattern is None:
            raise AttributeError("diffraction pattern is "
                                 "not initialized")

    def __check_diffraction_point(self, diffraction_point):
        if not self.wavelength is None:
            if diffraction_point.s is None or diffraction_point.twotheta is None:
                diffraction_point = DiffractionPoint(twotheta=diffraction_point.twotheta,
                                                     intensity=diffraction_point.intensity,
                                                     error=diffraction_point.error,
                                                     s=diffraction_point.s,
                                                     wavelength=self.wavelength)
        return diffraction_point


# ----------------------------------------------------
#  FACTORY METHOD
# ----------------------------------------------------

class DiffractionPatternLimits:
    def __init__(self, twotheta_min = -numpy.inf, twotheta_max = numpy.inf):
        self.twotheta_max = twotheta_max
        self.twotheta_min = twotheta_min


class DiffractionPatternFactory:
    @classmethod
    def create_diffraction_pattern_from_file(clscls, file_name, wavelength=None, limits=None):
        return DiffractionPatternFactoryChain.Instance().create_diffraction_pattern_from_file(file_name, wavelength, limits)

import os

# ----------------------------------------------------
#  CHAIN OF RESPONSABILITY
# ----------------------------------------------------

class DiffractionPatternFactoryInterface():
    def create_diffraction_pattern_from_file(self, file_name, wavelength=None, limits=None):
        raise NotImplementedError ("Method is Abstract")

    def _get_extension(self, file_name):
        filename, file_extension = os.path.splitext(file_name)
        return file_extension

from orangecontrib.wonder import Singleton
import sys

def predicate(class_name):
    return inspect.isclass(class_name) and issubclass(class_name, DiffractionPatternFactoryHandler)

@Singleton
class DiffractionPatternFactoryChain(DiffractionPatternFactoryInterface):
    _chain_of_handlers = []

    def __init__(self):
        self.initialize_chain()

    def initialize_chain(self):
        self._chain_of_handlers = []

        for handler in self._get_handlers_list():
            self._chain_of_handlers.append((globals()[handler])())

    def append_handler(self, handler = None):
        if self._chain_of_handlers is None: self.initialize_chain()

        if handler is None:
            raise ValueError ("Handler is None")

        if not isinstance(handler, DiffractionPatternFactoryHandler):
            raise ValueError("Handler Type not correct")

        self._chain_of_handlers.append(handler)

    def create_diffraction_pattern_from_file(self, file_name, wavelength=None, limits=None):
        file_extension = self._get_extension(file_name)

        for handler in self._chain_of_handlers:
            if handler.is_handler(file_extension):
                return handler.create_diffraction_pattern_from_file(file_name, wavelength, limits)

        raise ValueError ("File Extension not recognized")

    def _get_handlers_list(self):
        classes = numpy.array([m[0] for m in inspect.getmembers(sys.modules[__name__], predicate)])

        return numpy.asarray(classes[numpy.where(classes != "DiffractionPatternFactoryHandler")])

# ---------------------------------------------------
# HANDLERS INTERFACE
# ---------------------------------------------------

class DiffractionPatternFactoryHandler(DiffractionPatternFactoryInterface):

    def _get_handled_extension(self):
        raise NotImplementedError()

    def is_handler(self, file_extension):
        return file_extension == self._get_handled_extension()

# ---------------------------------------------------
# HANDLERS
# ---------------------------------------------------

class DiffractionPatternXyeFactoryHandler(DiffractionPatternFactoryHandler):

    def _get_handled_extension(self):
        return ".xye"

    def create_diffraction_pattern_from_file(self, file_name, wavelength=None, limits=None):
        return DiffractionPatternXye(file_name = file_name, wavelength=wavelength, limits=limits)

class DiffractionPatterXyFactoryHandler(DiffractionPatternXyeFactoryHandler):

    def _get_handled_extension(self):
        return ".xy"

class DiffractionPatternRawFactoryHandler(DiffractionPatternFactoryHandler):

    def _get_handled_extension(self):
        return ".raw"

    def create_diffraction_pattern_from_file(self, file_name, wavelength=None, limits=None):
        return DiffractionPatternRaw(file_name= file_name, wavelength=wavelength, limits=limits)


# ----------------------------------------------------
# PERSISTENCY MANAGAMENT
# ----------------------------------------------------

class DiffractionPatternXye(DiffractionPattern):
    def __init__(self, file_name= "", wavelength=None, limits=None):
        super(DiffractionPatternXye, self).__init__(n_points=0, wavelength=wavelength)

        self.__initialize_from_file(file_name, limits)

    def __initialize_from_file(self, file_name, limits):
        #method supposes only 2 rows of header are present
        #can be changed. Right now I want to finish
        with open(file_name, 'r') as xyefile : lines = xyefile.readlines()
        n_points = len(lines) - 2
        if n_points > 0:
            if len(lines) < 3: raise Exception("Number of lines in file < 3: wrong file format")
            if limits is None: self.diffraction_pattern = numpy.array([None] *n_points)

            for i in numpy.arange(2, n_points+2):
                line = lines[i].split()

                if len(line) < 2 : raise  Exception("Number of columns in line " + str(i) + " < 2: wrong file format")

                twotheta = float(line[0])
                intensity = float(line[1])

                if len(line) >= 3:
                    error = float(line[2])
                else:
                    error = numpy.sqrt(intensity)

                if limits is None:
                    self.set_diffraction_point(index=i-2,
                                               diffraction_point=DiffractionPoint(twotheta=twotheta,
                                                                                  intensity=intensity,
                                                                                  error=error,
                                                                                  wavelength=self.wavelength))
                elif  limits.twotheta_min <= twotheta <= limits.twotheta_max:
                    self.add_diffraction_point(diffraction_point=DiffractionPoint(twotheta=twotheta,
                                                                                  intensity=intensity,
                                                                                  error=error,
                                                                                  wavelength=self.wavelength))

class DiffractionPatternRaw(DiffractionPattern):
    def __init__(self, file_name= "", wavelength=None, limits=None):
        super(DiffractionPatternRaw, self).__init__(n_points = 0, wavelength=wavelength)

        self.__initialize_from_file(file_name, limits)

    def __initialize_from_file(self, file_name, limits):
        #method supposes only 1 rows of header is present
        #can be changed.
        with open(file_name, 'r') as rawfile : lines = rawfile.readlines()

        splitted_row = lines[1].split(sep=',')

        if not len(splitted_row) == 5:
            splitted_row = numpy.array(lines[1].split(sep=' '))
            splitted_row = splitted_row[numpy.where(splitted_row != '')]

        n_points = int(splitted_row[0])
        step = float(splitted_row[1])
        starting_theta = float(splitted_row[2])

        self.wavelength.set_value(float(splitted_row[3])/10)

        if limits is None: self.diffraction_pattern = numpy.array([None] *n_points)

        for i in numpy.arange(2, n_points+2):
            index = i-2
            line = lines[i]

            intensity = float(line)
            error = numpy.sqrt(intensity)

            if limits is None:
                self.set_diffraction_point(index,
                                           diffraction_point= DiffractionPoint(twotheta=starting_theta + step*index,
                                                                               intensity=intensity,
                                                                               error=error,
                                                                               wavelength=self.wavelength))
            else:
                twotheta = starting_theta + step*index

                if  limits.twotheta_min <= twotheta <= limits.twotheta_max:
                    self.add_diffraction_point(diffraction_point=DiffractionPoint(twotheta=twotheta,
                                                                                  intensity=intensity,
                                                                                  error=error,
                                                                                  wavelength=self.wavelength))
