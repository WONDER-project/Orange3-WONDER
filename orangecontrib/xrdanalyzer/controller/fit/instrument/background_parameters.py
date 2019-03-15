from orangecontrib.xrdanalyzer.controller.fit.fit_parameter import FitParametersList

class ChebyshevBackground(FitParametersList):
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

    def to_text(self):
        text = "BACKGROUND PARAMETERS\n"
        text += "-----------------------------------\n"

        text += self.c0.to_text() + "\n"
        text += self.c1.to_text() + "\n"
        text += self.c2.to_text() + "\n"
        text += self.c3.to_text() + "\n"
        text += self.c4.to_text() + "\n"
        text += self.c5.to_text() + "\n"
        text += self.c6.to_text() + "\n"
        text += self.c7.to_text() + "\n"
        text += self.c8.to_text() + "\n"
        text += self.c9.to_text() + "\n"

        text += "-----------------------------------\n"
        
        return text       

    def duplicate(self):
        return ChebyshevBackground(c0=None if self.c0 is None else self.c0.duplicate(),
                                   c1=None if self.c1 is None else self.c1.duplicate(),
                                   c2=None if self.c2 is None else self.c2.duplicate(),
                                   c3=None if self.c3 is None else self.c3.duplicate(),
                                   c4=None if self.c4 is None else self.c4.duplicate(),
                                   c5=None if self.c5 is None else self.c5.duplicate(),
                                   c6=None if self.c6 is None else self.c6.duplicate(),
                                   c7=None if self.c7 is None else self.c7.duplicate(),
                                   c8=None if self.c8 is None else self.c8.duplicate(),
                                   c9=None if self.c9 is None else self.c9.duplicate())

class ExpDecayBackground(FitParametersList):
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

    def to_text(self):
        text = "BACKGROUND PARAMETERS\n"
        text += "-----------------------------------\n"

        text += self.a0.to_text() + "\n"
        text += self.b0.to_text() + "\n"
        text += self.a1.to_text() + "\n"
        text += self.b1.to_text() + "\n"
        text += self.a2.to_text() + "\n"
        text += self.b2.to_text() + "\n"

        text += "-----------------------------------\n"

        return text

    def duplicate(self):
        return ExpDecayBackground(a0=None if self.a0 is None else self.a0.duplicate(),
                                  b0=None if self.b0 is None else self.b0.duplicate(),
                                  a1=None if self.a1 is None else self.a1.duplicate(),
                                  b1=None if self.b1 is None else self.b1.duplicate(),
                                  a2=None if self.a2 is None else self.a2.duplicate(),
                                  b2=None if self.b2 is None else self.b2.duplicate())
