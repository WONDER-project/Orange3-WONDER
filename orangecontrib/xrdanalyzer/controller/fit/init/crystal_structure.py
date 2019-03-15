import numpy

import orangecontrib.xrdanalyzer.util.congruence as congruence
from orangecontrib.xrdanalyzer.controller.fit.fit_parameter import FitParametersList, FitParameter, Boundary, PARAM_HWMAX, PARAM_HWMIN
from orangecontrib.xrdanalyzer.controller.fit.util.fit_utilities import Utilities
from orangecontrib.xrdanalyzer.controller.fit.init.crystal_structure_symmetry import Symmetry

class Reflection():

    h = 0
    k = 0
    l = 0

    d_spacing = 0.0

    intensity = None

    def __init__(self, h, k, l, intensity):
        self.h = h
        self.k = k
        self.l = l

        self.intensity = intensity

    def to_text(self):
        return str(self.h) + ", " + str(self.k) + ", " + str(self.l) + ", "  + self.intensity.to_text()

    def to_row(self):
        text = str(self.h) + ", " + str(self.k) + ", " + str(self.l) + ", " + self.intensity.parameter_name + " "

        if self.intensity.function:
            text += ":= " + str(self.intensity.function_value)
        else:
            text += str(self.intensity.value)

            if self.intensity.fixed:
                text += "fixed"
            elif not self.intensity.boundary is None:
                if not self.intensity.boundary.min_value == PARAM_HWMIN:
                    text += ", min " + str(self.intensity.boundary.min_value)

                if not self.intensity.boundary.max_value == PARAM_HWMAX:
                    text += ", max " + str(self.intensity.boundary.max_value)

        return text

    def get_theta_hkl(self, wavelength):
        return numpy.degrees(numpy.asin(2*self.d_spacing/wavelength))

    def get_q_hkl(self, wavelength):
        return 8*numpy.pi*self.d_spacing/(wavelength**2)

    def get_s_hkl(self, wavelength):
        return self.get_q_hkl(wavelength)/(2*numpy.pi)

class CrystalStructure(FitParametersList):

    a = None
    b = None
    c = None

    alpha = None
    beta = None
    gamma = None

    symmetry = Symmetry.SIMPLE_CUBIC

    use_structure = False
    formula = None
    intensity_scale_factor = None

    reflections = []

    @classmethod
    def get_parameters_prefix(cls):
        return "crystal_structure_"


    def __init__(self, a, b, c, alpha, beta, gamma, symmetry=Symmetry.SIMPLE_CUBIC, use_structure=False, formula=None, intensity_scale_factor=None):
        super(CrystalStructure, self).__init__()

        self.a = a
        self.b = b
        self.c = c
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.symmetry = symmetry
        self.use_structure = use_structure
        self.formula = None if formula is None else formula.strip()
        self.intensity_scale_factor = intensity_scale_factor

        self.reflections = []

    @classmethod
    def is_cube(cls, symmetry):
        return symmetry in (Symmetry.BCC, Symmetry.FCC, Symmetry.SIMPLE_CUBIC)

    @classmethod
    def init_cube(cls, a0, symmetry=Symmetry.FCC, use_structure=False, formula=None, intensity_scale_factor=None, progressive = ""):
        if not cls.is_cube(symmetry): raise ValueError("Symmetry doesn't belong to a cubic crystal cell")

        if a0.fixed:
            a = FitParameter(parameter_name=CrystalStructure.get_parameters_prefix() + progressive + "a", value=a0.value, fixed=a0.fixed, boundary=a0.boundary)
            b = FitParameter(parameter_name=CrystalStructure.get_parameters_prefix() + progressive + "b", value=a0.value, fixed=a0.fixed, boundary=a0.boundary)
            c = FitParameter(parameter_name=CrystalStructure.get_parameters_prefix() + progressive + "c", value=a0.value, fixed=a0.fixed, boundary=a0.boundary)
        else:
            a = a0
            b = FitParameter(parameter_name=CrystalStructure.get_parameters_prefix() + progressive + "b", function=True, function_value=CrystalStructure.get_parameters_prefix() + progressive + "a")
            c = FitParameter(parameter_name=CrystalStructure.get_parameters_prefix() + progressive + "c", function=True, function_value=CrystalStructure.get_parameters_prefix() + progressive + "a" )

        alpha = FitParameter(parameter_name=CrystalStructure.get_parameters_prefix() + progressive + "alpha", value=90, fixed=True)
        beta  = FitParameter(parameter_name=CrystalStructure.get_parameters_prefix() + progressive + "beta",  value=90, fixed=True)
        gamma = FitParameter(parameter_name=CrystalStructure.get_parameters_prefix() + progressive + "gamma", value=90, fixed=True)

        return CrystalStructure(a,
                                b,
                                c,
                                alpha,
                                beta,
                                gamma,
                                symmetry,
                                use_structure,
                                formula,
                                intensity_scale_factor)

    def add_reflection(self, reflection):
        self.reflections.append(reflection)

        self.update_reflection(-1)

    def set_reflection(self, index, reflection):
        self.reflections[index] = reflection

        self.update_reflection(index)

    def get_reflections_count(self):
        return len(self.reflections)

    def get_reflection(self, index):
        return self.reflections[index]

    def get_reflections(self):
        return numpy.array(self.reflections)

    def update_reflection(self, index):
        reflection = self.reflections[index]
        reflection.d_spacing = self.get_d_spacing(reflection.h, reflection.k, reflection.l)

    def update_reflections(self):
        for index in range(self.get_reflections_count()): self.update_reflection(index)

    def existing_reflection(self, h, k, l):
        for reflection in self.reflections:
            if reflection.h == h and reflection.k == k and reflection.l == l:
                return reflection

        return None

    def get_d_spacing(self, h, k, l):
        if self.is_cube(self.symmetry):
            if self.a.value is None:
                return 0
            else:
                return 1/Utilities.s_hkl(self.a.value, h, k, l)
        #elif self.symmetry == Symmetry.HCP:
        #    return 1/numpy.sqrt((4/3)*((h**2 + h*k + k**2)/ self.a.value**2  + (l/self.c.value)**2))
        else:
            NotImplementedError("Only Cubic supported: TODO!!!!!!")

    def parse_reflections(self, text, progressive=""):
        congruence.checkEmptyString(text, "Reflections")

        lines = text.splitlines()

        reflections = []

        for i in range(len(lines)):
            congruence.checkEmptyString(lines[i], "Reflections: line " + str(i+1))

            if not lines[i].strip().startswith("#"):
                data = lines[i].strip().split(",")

                if len(data) < 4: raise ValueError("Reflections, malformed line: " + str(i+1))

                h = int(data[0].strip())
                k = int(data[1].strip())
                l = int(data[2].strip())

                if ":=" in data[3].strip():
                    intensity_data = data[3].strip().split(":=")

                    if len(intensity_data) == 2:
                        intensity_name = intensity_data[0].strip()
                        function_value = intensity_data[1].strip()
                    else:
                        intensity_name = None
                        function_value = data[3].strip()

                    if intensity_name is None:
                        intensity_name = CrystalStructure.get_parameters_prefix() + progressive + "I" + str(h) + str(k) + str(l)
                    elif not intensity_name.startswith(CrystalStructure.get_parameters_prefix()):
                        intensity_name = CrystalStructure.get_parameters_prefix() + progressive + intensity_name

                    reflection = Reflection(h, k, l, intensity=FitParameter(parameter_name=intensity_name,
                                                                            function=True,
                                                                            function_value=function_value))
                else:

                    intensity_data = data[3].strip().split()

                    if len(intensity_data) == 2:
                        intensity_name = intensity_data[0].strip()
                        intensity_value = float(intensity_data[1])
                    else:
                        intensity_name = None
                        intensity_value = float(data[3])

                    boundary = None
                    fixed = False

                    if len(data) > 4:
                        min_value = PARAM_HWMIN
                        max_value = PARAM_HWMAX

                        for j in range(4, len(data)):
                            boundary_data = data[j].strip().split()

                            if boundary_data[0] == "min": min_value = float(boundary_data[1].strip())
                            elif boundary_data[0] == "max": max_value = float(boundary_data[1].strip())
                            elif boundary_data[0] == "fixed": fixed = True

                        if not fixed:
                            if min_value != PARAM_HWMIN or max_value != PARAM_HWMAX:
                                boundary = Boundary(min_value=min_value, max_value=max_value)
                            else:
                                boundary = Boundary()

                    if intensity_name is None:
                        intensity_name = CrystalStructure.get_parameters_prefix() + progressive + "I" + str(h) + str(k) + str(l)
                    elif not intensity_name.startswith(CrystalStructure.get_parameters_prefix()):
                        intensity_name = CrystalStructure.get_parameters_prefix() + progressive + intensity_name

                    reflection = Reflection(h, k, l, intensity=FitParameter(parameter_name=intensity_name,
                                                                            value=intensity_value,
                                                                            fixed=fixed,
                                                                            boundary=boundary))
                reflections.append(reflection)

        self.reflections = reflections
        self.update_reflections()

    def get_congruence_check(self, wavelength, min_value, max_value, limit_is_s=True):
        if wavelength <= 0: raise ValueError("Wavelenght should be a positive number")
        if max_value <= 0: raise ValueError("Max Value should be a positive number")

        if not limit_is_s:
            s_min = Utilities.s(numpy.radians(min_value/2), wavelength) # 2THETA MIN VALUE!
            s_max = Utilities.s(numpy.radians(max_value/2), wavelength) # 2THETA MAX VALUE!
        else:
            s_min = min_value
            s_max = max_value

        excluded_reflection = []

        for reflection in self.reflections:
            s_hkl = Utilities.s_hkl(self.a.value, reflection.h, reflection.k, reflection.l)

            if s_hkl < s_min or s_hkl > s_max: excluded_reflection.append(reflection)

        if len(excluded_reflection) == 0: excluded_reflection = None

        return excluded_reflection

    def duplicate(self):
        crystal_structure = CrystalStructure(a=None if self.a is None else self.a.duplicate(),
                                             b=None if self.b is None else self.b.duplicate(),
                                             c=None if self.c is None else self.c.duplicate(),
                                             alpha=None if self.alpha is None else self.alpha.duplicate(),
                                             beta=None if self.beta is None else self.beta.duplicate(),
                                             gamma=None if self.gamma is None else self.gamma.duplicate(),
                                             symmetry=self.symmetry,
                                             use_structure=self.use_structure,
                                             formula=self.formula,
                                             intensity_scale_factor=None if self.intensity_scale_factor is None else self.intensity_scale_factor.duplicate())

        for reflection in self.reflections:
            reflection_copy = Reflection(h=reflection.h, k=reflection.k, l=reflection.l, intensity=None if reflection.intensity is None else reflection.intensity.duplicate())
            reflection_copy.d_spacing = reflection.d_spacing

            crystal_structure.add_reflection(reflection_copy)

        return crystal_structure

    def to_text(self):
        text = "CRYSTAL STRUCTURE\n"
        text += "-----------------------------------\n"

        text += self.a.to_text() + "\n"
        text += self.b.to_text() + "\n"
        text += self.c.to_text() + "\n"
        text += self.alpha.to_text() + "\n"
        text += self.beta.to_text() + "\n"
        text += self.gamma.to_text() + "\n"
        text += "Symmetry: " + self.symmetry + "\n"
        text += "Use Strucuture: " + str(self.use_structure) + "\n"
        text += "Chemical Formula: " + str(self.formula) + "\n"
        text += ("" if self.intensity_scale_factor is None else self.intensity_scale_factor.to_text()) + "\n"

        text += "\nREFLECTIONS\n"
        text += "h, k, l, intensity:\n"

        for reflection in self.reflections:
            text += reflection.to_text() + "\n"

        text += "-----------------------------------\n"

        return text

    def get_parameters(self):
        parameters = super().get_parameters()

        for reflection in self.reflections:
            parameters.append(reflection.intensity)

        return parameters

if __name__=="__main__":
    test = CrystalStructure.init_cube(a0=FitParameter(value=0.55, fixed=True), symmetry=Symmetry.BCC)

    test = CrystalStructure(a=FitParameter(parameter_name="a", value=0.55), b=FitParameter(parameter_name="b", value=0.66), c=FitParameter(parameter_name="c", value=0.77),
                            alpha=FitParameter(value=10), beta=FitParameter(value=20), gamma=FitParameter(value=30),
                            symmetry=Symmetry.NONE)

    test.add_reflection(Reflection(1, 0, 3, intensity=FitParameter(value=200, boundary=Boundary(min_value=10, max_value=100000))))
    test.add_reflection(Reflection(2, 0, 0, intensity=FitParameter(value=300, boundary=Boundary(min_value=10, max_value=100000))))
    test.add_reflection(Reflection(2, 1, 1, intensity=FitParameter(value=400)))

    text = "1, 1, 0, I110 := crystal_structure_I200\n" + \
           "2, 0, 0, crystal_structure_I200 2000, min 20, max 10000\n"  + \
           "2, 1, 0, crystal_structure_I210 3000, max 30000\n"  + \
           "3, 0, 0, crystal_structure_I300 4000\n"  + \
           "3, 1, 0, crystal_structure_4100\n"  + \
           "4, 4, 1, crystal_structure_I441 5000\n"

    test.parse_reflections(text)

    print(test.to_text())
