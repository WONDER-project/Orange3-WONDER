from orangecontrib.wonder.controller.fit.fit_parameter import Boundary, FitParameter, ParametersList

class Caglioti(ParametersList):
    U = None
    V = None
    W = None
    a = None
    b = None
    c = None

    @classmethod
    def get_parameters_prefix(cls):
        return "caglioti_"

    def __init__(self, U, V, W, a, b, c):
        super(Caglioti, self).__init__()

        self.U = U
        self.V = V
        self.W = W
        self.a = a
        self.b = b
        self.c = c

class Lab6TanCorrection(ParametersList):
    ax = None
    bx = None
    cx = None
    dx = None
    ex = None

    @classmethod
    def get_parameters_prefix(cls):
        return "lab6_tancorrection_"

    def __init__(self, ax, bx, cx, dx, ex):
        super(Lab6TanCorrection, self).__init__()

        self.ax = ax
        self.bx = bx
        self.cx = cx
        self.dx = dx
        self.ex = ex

class ZeroError(ParametersList):
    shift = None

    @classmethod
    def get_parameters_prefix(cls):
        return "zero_error_"

    def __init__(self, shift):
        super(ZeroError, self).__init__()

        self.shift = shift

class SpecimenDisplacement(ParametersList):
    goniometer_radius = 1.0
    displacement = None

    @classmethod
    def get_parameters_prefix(cls):
        return "sd_"

    def __init__(self, goniometer_radius=1.0, displacement=None):
        super(SpecimenDisplacement, self).__init__()

        self.goniometer_radius = goniometer_radius
        self.displacement = displacement
