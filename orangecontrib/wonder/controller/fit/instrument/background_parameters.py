from orangecontrib.wonder.controller.fit.fit_parameter import ParametersList

class ChebyshevBackground(ParametersList):
    c0 = None
    c1 = None
    c2 = None
    c3 = None
    c4 = None
    c5 = None
    c6 = None
    c7 = None
    c8 = None
    c9 = None

    @classmethod
    def get_parameters_prefix(cls):
        return "chebyshev_"

    def __init__(self, c0, c1, c2, c3, c4, c5, c6, c7, c8, c9):
        super(ChebyshevBackground, self).__init__()

        self.c0 = c0
        self.c1 = c1
        self.c2 = c2
        self.c3 = c3
        self.c4 = c4
        self.c5 = c5
        self.c6 = c6
        self.c7 = c7
        self.c8 = c8
        self.c9 = c9

class ExpDecayBackground(ParametersList):
    a0 = None
    b0 = None
    a1 = None
    b1 = None
    a2 = None
    b2 = None

    @classmethod
    def get_parameters_prefix(cls):
        return "expdecay_"

    def __init__(self, a0, b0, a1, b1, a2, b2):
        super(ExpDecayBackground, self).__init__()

        self.a0 = a0
        self.b0 = b0
        self.a1 = a1
        self.b1 = b1
        self.a2 = a2
        self.b2 = b2
