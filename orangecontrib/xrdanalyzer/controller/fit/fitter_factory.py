import orangecontrib.xrdanalyzer.util.congruence as congruence
from orangecontrib.xrdanalyzer.controller.fit.fitters.fitter_minpack import FitterMinpack
from orangecontrib.xrdanalyzer.controller.fit.fitters.fitter_minpack_2 import FitterMinpack2

class FitterName:
    MINPACK  = "minpack"
    MINPACK2  = "minpack2"

    @classmethod
    def tuple(cls):
        return [cls.MINPACK, cls.MINPACK2]

class FitterFactory():

    @classmethod
    def create_fitter(cls, fitter_name=FitterName.MINPACK, additional_data=None):
        congruence.checkEmptyString(fitter_name, "Fitter Name")

        if fitter_name == FitterName.MINPACK:
            return FitterMinpack()
        elif fitter_name == FitterName.MINPACK2:
            return FitterMinpack2()
        else:
            raise ValueError("Fitter name <" + fitter_name +"> not recognized")
