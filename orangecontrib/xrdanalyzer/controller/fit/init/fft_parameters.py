from orangecontrib.xrdanalyzer.util import congruence
from orangecontrib.xrdanalyzer.controller.fit.fit_parameter import FitParametersList

class FFTTypes:
    REAL_ONLY = 0
    FULL = 1

    @classmethod
    def tuple(cls):
        return ["Real Only", "Full"]

class FFTInitParameters(FitParametersList):

    s_max = 9.0
    n_step = 4096
    fft_type = FFTTypes.REAL_ONLY

    def __init__(self, s_max = 9.0, n_step = 4096, fft_type=FFTTypes.REAL_ONLY):
        congruence.checkStrictlyPositiveNumber(s_max, "S_max")
        congruence.checkStrictlyPositiveNumber(n_step, "N_step")

        n_step = int(n_step)

        if not ((n_step & (n_step - 1)) == 0): raise ValueError("N_step should be a power of 2")
        if not (fft_type == FFTTypes.REAL_ONLY or fft_type == FFTTypes.FULL): raise ValueError("FFT type not recognized")

        self.s_max = s_max
        self.n_step = n_step
        self.fft_type = fft_type

        # THESE PARAMETERS ARE FIXED BY DEFAULT, THEY ARE NOT PASSED TO THE LIST

    def duplicate(self):
        return FFTInitParameters(s_max=self.s_max, n_step=self.n_step, fft_type=self.fft_type)

    def to_text(self):
        text = "FFT PARAMETERS\n"
        text += "-----------------------------------\n"
        text += "fft steps: " + str(self.n_step) + "\n"
        text += "s max    : "  + str(self.s_max) + "\n"
        text += "FFT Type : "  + FFTTypes.tuple()[self.fft_type] + "\n"
        text += "-----------------------------------\n"

        return text
