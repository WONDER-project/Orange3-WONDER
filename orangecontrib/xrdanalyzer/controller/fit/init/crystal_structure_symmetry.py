class Symmetry:
    FCC = "fcc"
    BCC = "bcc"
    SIMPLE_CUBIC = "sc"

    @classmethod
    def tuple(cls):
        return [cls.SIMPLE_CUBIC, cls.BCC, cls.FCC]
