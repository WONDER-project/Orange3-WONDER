import numpy

from orangecontrib.wonder.controller.fit.fit_parameter import ParametersList
from orangecontrib.wonder.controller.fit.wppm.wppm_functions import \
    Normalization, Distribution, Shape, WulffCubeFace, \
    lognormal_distribution, delta_distribution, gamma_distribution, york_distribution, \
    lognormal_average, lognormal_average_surface_weigthed, lognormal_average_volume_weigthed, lognormal_standard_deviation


class SizeDistribution:
    D                      = None
    frequency              = None
    D_min                  = None
    D_max                  = None
    D_avg                  = None
    D_avg_surface_weighted = None
    D_avg_volume_weighted  = None
    standard_deviation     = None


class SizeParameters(ParametersList):

    shape = Shape.SPHERE
    distribution = Distribution.LOGNORMAL
    mu = None
    sigma = None
    truncation = None
    cube_face = WulffCubeFace.HEXAGONAL
    add_saxs = False
    normalize_to = Normalization.NORMALIZE_TO_N

    @classmethod
    def get_parameters_prefix(cls):
        return "size_"

    def __init__(self, shape, distribution, mu, sigma, truncation=0.0, cube_face = WulffCubeFace.HEXAGONAL, add_saxs=False, normalize_to=Normalization.NORMALIZE_TO_N):
        super(SizeParameters, self).__init__()

        self.shape = shape
        self.distribution = distribution
        self.mu = mu
        self.sigma = sigma
        self.truncation = truncation
        self.cube_face = cube_face
        self.add_saxs = add_saxs
        self.normalize_to = normalize_to

    def get_distribution(self, auto=True, D_min=0, D_max=1000):
        if auto:
            D_min = 0
            D_max = 1000

        distribution       = SizeDistribution()
        distribution.D_min = D_min
        distribution.D_max = D_max
        distribution.x     = numpy.arange(start=D_min, stop=D_max, step=(D_max-D_min)/1000)

        self.__populate_stats_on_ditribution(distribution)

        try:
            distribution.y = self.__get_distribution_frequency_values(distribution.x)

            if auto:
                D_min, D_max = self.__get_auto_limits(distribution.x, distribution.y)

                distribution = self.get_distribution(auto=False, D_min=D_min, D_max=D_max)
        except:
            pass

        return distribution

    def __populate_stats_on_ditribution(self, distribution):
        if self.distribution == Distribution.LOGNORMAL:
            distribution.D_avg = lognormal_average(self.mu.value, self.sigma.value)
            distribution.D_avg_surface_weighted = lognormal_average_surface_weigthed(self.mu.value, self.sigma.value)
            distribution.D_avg_volume_weighted = lognormal_average_volume_weigthed(self.mu.value, self.sigma.value)
            distribution.standard_deviation = lognormal_standard_deviation(self.mu.value, self.sigma.value)
        elif self.distribution == Distribution.GAMMA or self.distribution == Distribution.YORK:
            distribution.D_avg = self.mu.value
            distribution.D_avg_surface_weighted = None
            distribution.D_avg_volume_weighted = None
            distribution.standard_deviation = None
        else:
            distribution.D_avg = None
            distribution.D_avg_surface_weighted = None
            distribution.D_avg_volume_weighted = None
            distribution.standard_deviation = None


    def __get_distribution_frequency_values(self, x):
        if self.distribution == Distribution.LOGNORMAL:
            y = lognormal_distribution(self.mu.value, self.sigma.value, x)
        elif self.distribution == Distribution.GAMMA:
            y = gamma_distribution(self.mu.value, self.sigma.value, x)
        elif self.distribution == Distribution.YORK:
            y = york_distribution(self.mu.value, self.sigma.value, x)
        elif self.distribution == Distribution.DELTA:
            y = delta_distribution(self.mu.value, x)
        else:
            y = numpy.zeros(len(x))

        y[numpy.where(numpy.logical_or(numpy.isnan(y), numpy.isinf(y)))] = 0.0

        return y

    def __get_auto_limits(self, x, y):
        good = x[numpy.where(y > 1e-5)]

        D_min = good[0]
        D_max = good[-1]

        if D_min == D_max: D_min = x[0]
        if D_min < 5: D_min = 0.0

        return D_min, D_max
