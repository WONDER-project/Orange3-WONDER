import orangecontrib.wonder.util.congruence as congruence
from orangecontrib.wonder.controller.fit.fitters.fitter_minpack import FitterMinpack
from orangecontrib.wonder.controller.fit.fitters.fitter_minpack_new import FitterMinpackNew

class FitterName:
    MINPACK   = "minpack (prototype)"
    MINPACK2  = "minpack (optimized)"

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
            return FitterMinpackNew()
        else:
            raise ValueError("Fitter name <" + fitter_name +"> not recognized")
