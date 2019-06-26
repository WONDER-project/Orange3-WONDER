import orangecontrib.wonder.util.congruence as congruence
from orangecontrib.wonder.controller.fit.fitters.fitter_minpack import FitterMinpack

class FitterName:
    MINPACK  = "minpack"

    @classmethod
    def tuple(cls):
        return [cls.MINPACK]

class FitterFactory():

    @classmethod
    def create_fitter(cls, fitter_name=FitterName.MINPACK, additional_data=None):
        congruence.checkEmptyString(fitter_name, "Fitter Name")

        if fitter_name == FitterName.MINPACK:
            return FitterMinpack()
        else:
            raise ValueError("Fitter name <" + fitter_name +"> not recognized")
