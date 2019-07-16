import orangecontrib.wonder.util.congruence as congruence
from orangecontrib.wonder.controller.fit.fitters.fitter_minpack import FitterMinpack
from orangecontrib.wonder.controller.fit.fitters.fitter_minpack_prototype import FitterMinpackPrototype

class FitterName:
    MINPACK_PROTOTYPE = "minpack (prototype)"
    MINPACK           = "minpack (optimized)"

    @classmethod
    def tuple(cls):
        return [cls.MINPACK_PROTOTYPE, cls.MINPACK]

class FitterFactory():

    @classmethod
    def create_fitter(cls, fitter_name=FitterName.MINPACK_PROTOTYPE, additional_data=None):
        congruence.checkEmptyString(fitter_name, "Fitter Name")

        if fitter_name == FitterName.MINPACK_PROTOTYPE:
            return FitterMinpackPrototype()
        elif fitter_name == FitterName.MINPACK:
            return FitterMinpack()
        else:
            raise ValueError("Fitter name <" + fitter_name +"> not recognized")
