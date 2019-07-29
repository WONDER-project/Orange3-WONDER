import os
import orangecontrib.wonder.util.congruence as congruence
from orangecontrib.wonder.controller.fit.fitters.fitter_minpack import FitterMinpack
from orangecontrib.wonder.controller.fit.fitters.fitter_minpack_prototype import FitterMinpackPrototype
from orangecontrib.wonder.util.gui.gui_utility import OW_IS_DEVELOP

class FitterName:
    MINPACK_PROTOTYPE = "minpack (prototype)"
    if OW_IS_DEVELOP:
       MINPACK           = "minpack (optimized)"
    else:
       MINPACK           = "minpack"

    @classmethod
    def tuple(cls):
        if OW_IS_DEVELOP:
            return [cls.MINPACK_PROTOTYPE, cls.MINPACK]
        else:
            return [cls.MINPACK]

class FitterFactory():

    @classmethod
    def create_fitter(cls, fitter_name=FitterName.MINPACK, additional_data=None):
        congruence.checkEmptyString(fitter_name, "Fitter Name")

        if fitter_name == FitterName.MINPACK_PROTOTYPE:
            return FitterMinpackPrototype()
        elif fitter_name == FitterName.MINPACK:
            return FitterMinpack()
        else:
            raise ValueError("Fitter name <" + fitter_name +"> not recognized")
