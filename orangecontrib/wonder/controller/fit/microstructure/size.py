import numpy

from orangecontrib.wonder.controller.fit.fit_parameter import ParametersList
from orangecontrib.wonder.controller.fit.wppm_functions import Normalization, Distribution, lognormal_distribution

class Shape:
    NONE = "none"
    SPHERE = "sphere"
    CUBE = "cube"
    TETRAHEDRON = "tetrahedron"
    OCTAHEDRON = "octahedron"
    CYLINDER = "cylinder"

    @classmethod
    def tuple(cls):
        return [cls.NONE, cls.SPHERE, cls.CUBE, cls.TETRAHEDRON, cls.OCTAHEDRON, cls.CYLINDER]


class SizeParameters(ParametersList):

    shape = Shape.SPHERE
    distribution = Distribution.LOGNORMAL
    mu = None
    sigma = None
    add_saxs = False
    normalize_to = Normalization.NORMALIZE_TO_N

    @classmethod
    def get_parameters_prefix(cls):
        return "size_"

    def __init__(self, shape, distribution, mu, sigma, add_saxs=False, normalize_to=Normalization.NORMALIZE_TO_N):
        super(SizeParameters, self).__init__()

        self.shape = shape
        self.distribution = distribution
        self.mu = mu
        self.sigma = sigma
        self.add_saxs = add_saxs
        self.normalize_to = normalize_to

    def get_distribution(self, auto=True, D_min=None, D_max=None):
        if auto:
            D_min = 0
            D_max = 1000

        step = (D_max-D_min)/1000

        x = numpy.arange(start=D_min, stop=D_max, step=step)

        try:
            if self.distribution == Distribution.LOGNORMAL:
                y = lognormal_distribution(self.mu.value, self.sigma.value, x)
            else:
                y = numpy.zeros(len(x))

            if auto:
                D_min = 0.0
                D_max = x[numpy.where(y > 1e-5)][-1]
                if D_min == D_max: D_min==x[0]

                x, y, D_min, D_max = self.get_distribution(auto=False, D_min=D_min, D_max=D_max)
        except:
            pass

        return x, y, D_min, D_max

