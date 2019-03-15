from orangecontrib.xrdanalyzer.controller.fit.fit_parameter import Boundary, FitParameter, FitParametersList

class Caglioti(FitParametersList):
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

    def to_text(self):
        text = "INSTRUMENTAL PARAMETERS\n"
        text += "-----------------------------------\n"

        text += self.U.to_text() + "\n"
        text += self.V.to_text() + "\n"
        text += self.W.to_text() + "\n"
        text += self.a.to_text() + "\n"
        text += self.b.to_text() + "\n"
        text += self.c.to_text() + "\n"

        text += "-----------------------------------\n"

        return text

    def duplicate(self):
        return Caglioti(U=None if self.U is None else self.U.duplicate(),
                        V=None if self.V is None else self.V.duplicate(),
                        W=None if self.W is None else self.W.duplicate(),
                        a=None if self.a is None else self.a.duplicate(),
                        b=None if self.b is None else self.b.duplicate(),
                        c=None if self.c is None else self.c.duplicate())

class Lab6TanCorrection(FitParametersList):
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

    def to_text(self):
        text = "LAB6 TAN-CORRECTION\n"
        text += "-----------------------------------\n"

        text += self.ax.to_text() + "\n"
        text += self.bx.to_text() + "\n"
        text += self.cx.to_text() + "\n"
        text += self.dx.to_text() + "\n"
        text += self.ex.to_text() + "\n"

        text += "-----------------------------------\n"

        return text

    def duplicate(self):
        return Lab6TanCorrection(ax=None if self.ax is None else self.ax.duplicate(),
                                 bx=None if self.bx is None else self.bx.duplicate(),
                                 cx=None if self.cx is None else self.cx.duplicate(),
                                 dx=None if self.dx is None else self.dx.duplicate(),
                                 ex=None if self.ex is None else self.ex.duplicate())


class ZeroError(FitParametersList):
    shift = None

    @classmethod
    def get_parameters_prefix(cls):
        return "zero_error_"

    def __init__(self, shift):
        super(ZeroError, self).__init__()

        self.shift = shift

    def to_text(self):
        text = "ZERO ERROR\n"
        text += "-----------------------------------\n"

        text += self.shift.to_text() + "\n"

        text += "-----------------------------------\n"

        return text

    def duplicate(self):
        return ZeroError(shift=None if self.shift is None else self.shift.duplicate())


class SpecimenDisplacement(FitParametersList):
    goniometer_radius = 1.0
    displacement = None

    @classmethod
    def get_parameters_prefix(cls):
        return "sd_"

    def __init__(self, goniometer_radius=1.0, displacement=None):
        super(SpecimenDisplacement, self).__init__()

        self.goniometer_radius = goniometer_radius
        self.displacement = displacement

    def to_text(self):
        text = "SPECIMEN DISPLACEMENT\n"
        text += "-----------------------------------\n"

        text += "Goniometer Radius: " + str(self.goniometer_radius) + "\n"
        text += self.displacement.to_text() + "\n"

        text += "-----------------------------------\n"

        return text

    def duplicate(self):
        return SpecimenDisplacement(goniometer_radius=self.goniometer_radius,
                                    displacement=None if self.displacement is None else self.displacement.duplicate())


if __name__=="__main__":
    test = Caglioti(U=FitParameter(parameter_name="U", value=1.0, fixed=True),
                    V=FitParameter(parameter_name="V", value=2.0, boundary=Boundary(max_value=10.0)),
                    W=FitParameter(parameter_name="W", value=3.0, boundary=Boundary(min_value=-10.0)),
                    a=FitParameter(parameter_name="a", value=4.0, fixed=True),
                    b=FitParameter(parameter_name="b", value=5.0, boundary=Boundary(min_value=-10.0, max_value=10.0)),
                    c=FitParameter(parameter_name="c", value=6.0, boundary=Boundary(min_value=-10.0, max_value=10.0)))

    print(test.tuple())
    print("\n")
    print(test.to_text())
