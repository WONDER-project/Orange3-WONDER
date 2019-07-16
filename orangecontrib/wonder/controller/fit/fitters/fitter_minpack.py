from orangecontrib.wonder.controller.fit.fitter import FitterInterface

from orangecontrib.wonder.model.diffraction_pattern import DiffractionPattern, DiffractionPoint
from orangecontrib.wonder.controller.fit.fit_parameter import PARAM_ERR
from orangecontrib.wonder.controller.fit.wppm_functions import fit_function_direct
#from orangecontrib.wonder.controller.fit.wppm_functions_multipool import fit_function_direct_multipool
from orangecontrib.wonder.controller.fit.fit_global_parameters import FitGlobalParameters

import numpy
import time
import copy

PRCSN = 2.5E-7

class MinpackData:
    def __init__(self,
                 dof = 0.0,
                 wss = 0.0,
                 ss = 0.0,
                 wsq = 0.0,
                 nobs = 0.0,
                 nprm = 0.0,
                 nfit = 0.0,
                 calc_lambda = 0.0,
                 calculate = True):
        self.dof = dof
        self.wss = wss
        self.ss = ss
        self.wsq = wsq
        self.nprm = nprm
        self.nfit = nfit
        self.nobs = nobs
        self.calc_lambda = calc_lambda

        if calculate: self.calculate()

    def calculate(self):
        try:
            self.rwp  = numpy.sqrt(self.wss / self.wsq)
        except:
            self.rwp = 0.0

        try:
            self.rexp = numpy.sqrt(self.dof / self.wsq)
        except:
            self.rexp = 0.0

    def gof(self):
        return self.rwp / self.rexp

    def print_init_data(self):
        print("Current Fit data:\n",
              "  total parameters   (nprm): %d \n" % self.nprm,
              "  parameters to fit  (nfit): %d \n" % self.nfit,
              "  nr. of observables (nobs): %d \n" % self.nobs,
              "  dof (nobs - nfit)        : %d \n" % self.dof)

    def print_fit_data(self):
        print("\nCurrent fit results:\n\n",
              "  LAMBDA: %d \n" % self.calc_lambda,
              "  wss: %d \n" % self.wss,
              "  ss : %d \n" % self.ss,
              "  wsq: %d \n" % self.wsq,
              "  gof: %d \n" % self.gof())

class FitterMinpack(FitterInterface):

    def __init__(self):
        super().__init__()

    def init_fitter(self, fit_global_parameters):
        print("Initializing Fitter...")

        self.fit_global_parameters = fit_global_parameters.duplicate()
        self.fit_global_parameters.evaluate_functions()

        self._lambda = .001
        self._lmin   = 1E20
        self._phi    = 1.2 # relaxation factor

        self.total_iterations	= 0
        self.nr_increments = 0

         # INITIALIZATION OF FUNCTION VALUES

        self.parameters    = self.fit_global_parameters.get_parameters()
        self.has_functions = FitGlobalParameters.parameters_have_functions(self.parameters)

        self.diffraction_patterns_number = self.fit_global_parameters.fit_initialization.get_diffraction_patterns_number()

        self.twotheta_experimental_list = numpy.full(self.diffraction_patterns_number, None)
        self.intensity_experimental_list = numpy.full(self.diffraction_patterns_number, None)
        self.error_experimental_list = numpy.full(self.diffraction_patterns_number, None)

        for index in range(self.diffraction_patterns_number):
            twotheta_experimental, intensity_experimental, error_experimental, _ = self.fit_global_parameters.fit_initialization.diffraction_patterns[index].tuples()

            self.twotheta_experimental_list[index] = twotheta_experimental
            self.intensity_experimental_list[index] = intensity_experimental
            self.error_experimental_list[index] = error_experimental

        self.nr_points_list = self.get_nr_points_list()

        self.nr_parameters = len(self.parameters)
        self.nr_parameters_to_fit = self.get_nr_parameters_to_fit()
        self.nr_observables = numpy.sum(self.nr_points_list)
        self.degrees_of_freedom = self.nr_observables - self.nr_parameters_to_fit

        self.variable_indexes = []
        for i in range (0, self.nr_parameters):
            if self.parameters[i].is_variable():
                self.variable_indexes.append(i)

        self.a = self.__get_zero_trimatrix() #CTriMatrix(_n=self.nr_parameters_to_fit)
        self.c = self.__get_zero_trimatrix() #CTriMatrix(_n=self.nr_parameters_to_fit)

        self.g                    = self.__get_zero_vector()
        self.gradient             = self.__get_zero_vector()
        self.current_pararameters = self.__get_zero_vector()
        self.initial_parameters   = self.__get_zero_vector()

        self.mighell = False

        self.wss      = self.__get_wssq()
        self.old_wss  = self.wss

        self.fit_data = MinpackData(wss=self.wss,
                                    dof=self.degrees_of_freedom,
                                    nobs=self.nr_observables,
                                    nprm=self.nr_parameters,
                                    nfit=self.nr_parameters_to_fit)

        self.fit_data.print_init_data()

        self.converged = False
        self.exit_flag  = False

        self.__populate_variables()

        print("Fitter Initialization done.")


    def do_fit(self, current_fit_global_parameters, current_iteration, compute_pattern, compute_errors):
        print("Fitter - Begin iteration nr. " + str(current_iteration))

        if current_iteration <= current_fit_global_parameters.get_n_max_iterations() and not self.converged:
            # check values of lambda for large number of iterations
            if (self.total_iterations > 4 and self._lambda < self._lmin): self._lmin = self._lambda

            #update total number of iterations
            self.total_iterations += 1

            #decrease lambda using golden section 0.31622777=1/(sqrt(10.0))
            self._lambda *= 0.31622777

            #number of increments in lambda
            self.nr_increments = 0

            #start_time = time.clock()

            #zero the working arrays
            self.__initialize_a_and_gradient()

            self.c = copy.deepcopy(self.a) #save the matrix A and the current value of the parameters

            self.__populate_variables()
            self.current_pararameters = copy.deepcopy(self.initial_parameters)

            # emulate C++ do ... while cycle
            do_cycle = True

            print("Begin Minization using LAMBDA: ", self._lambda)

            while do_cycle:
                self.exit_flag = False
                self.converged = False

                #set the diagonal of A to be A*(1+lambda)+phi*lambda
                self.__set_a_diagonal()

                if self.__cholesky_decomposition_a() == 0: # Cholesky decomposition
                    # the matrix is inverted, so calculate g (change in the
                    # parameters) by back substitution

                    self.__cholesky_back_substitution_a()

                    previous_wss = self.old_wss
                    nr_cycles = 1

                    # Update the parameters: param = old param + g
                    # n0 counts the number of zero elements in g
                    do_inner_cycle = True
                    while do_inner_cycle:
                        keep_cycling = False
                        
                        nr_0_elements_in_g = 0
                        i = 0
                        for j in self.variable_indexes:
                            self.parameters[j].set_value(self.current_pararameters[i] + nr_cycles * self.g[i])
                            # check number of parameters reaching convergence
                            if (abs(self.g[i]) <= abs(PRCSN*self.current_pararameters[i])): nr_0_elements_in_g += 1
                            i += 1

                        # calculate functions
                        if self.has_functions:
                            FitGlobalParameters.compute_functions(self.parameters,
                                                                  current_fit_global_parameters.free_input_parameters,
                                                                  current_fit_global_parameters.free_output_parameters)

                        if (nr_0_elements_in_g==self.nr_parameters_to_fit):
                            self.converged = True

                        # update the wss
                        self.wss = self.__get_wssq()

                        if self.wss < previous_wss:
                            previous_wss = self.wss
                            keep_cycling = True
                            nr_cycles += 1

                        # last line of while loop
                        do_inner_cycle = keep_cycling and nr_cycles<10

                    if nr_cycles > 1:

                        # restore parameters to best value
                        nr_cycles -= 1

                        i = 0
                        for j in self.variable_indexes:
                            # update value of parameter
                            #  apply the required constraints (min/max)
                            self.parameters[j].set_value(self.current_pararameters[i] + nr_cycles * self.g[i])
                            i += 1

                        # calculate functions
                        if self.has_functions:
                            FitGlobalParameters.compute_functions(self.parameters,
                                                                  current_fit_global_parameters.free_input_parameters,
                                                                  current_fit_global_parameters.free_output_parameters)

                        # update the wss
                        self.wss = self.__get_wssq()

                    # if all parameters reached convergence then it's time to quit

                    if self.wss < self.old_wss:
                        self.old_wss     = self.wss
                        self.exit_flag   = True

                        for i in range(self.nr_parameters_to_fit):
                            self.initial_parameters[i] = self.current_pararameters[i] + nr_cycles * self.g[i]

                    self.build_minpack_data()

                    self.fit_data.print_fit_data()
                else:
                    if self.has_functions:
                        FitGlobalParameters.compute_functions(self.parameters,
                                                              current_fit_global_parameters.free_input_parameters,
                                                              current_fit_global_parameters.free_output_parameters)

                    print("Chlolesky decomposition failed!")

                if not self.exit_flag and not self.converged:
                    if self._lambda<PRCSN: self._lambda = PRCSN
                    self.nr_increments += 1
                    self._lambda *= 10.0
                    if self._lambda>(1E5*self._lmin): self.converged = True

                # last line of the while loop
                do_cycle = not self.exit_flag and not self.converged

            j = -1
            for i in self.variable_indexes:
                j += 1
                self.parameters[i].set_value(self.initial_parameters[j])

            if self.has_functions:
                FitGlobalParameters.compute_functions(self.parameters,
                                                      current_fit_global_parameters.free_input_parameters,
                                                      current_fit_global_parameters.free_output_parameters)

        if compute_errors:
            errors = numpy.zeros(self.nr_parameters)

            self.__initialize_a_and_gradient()

            if self.__cholesky_decomposition_a() == 0:
                k = 0
                for i in self.variable_indexes:
                    self.g = numpy.zeros(self.nr_parameters_to_fit)
                    self.g[k] = 1.0
                    self.__cholesky_back_substitution_a()
                    errors[i] = numpy.sqrt(numpy.abs(self.g[k]))
                    k += 1
            else:
                print("Errors not calculated: cholesky decomposition != 0")

            fit_global_parameters_out = self.fit_global_parameters.from_fitted_parameters_and_errors(self.parameters, errors).duplicate()
        else:
            fit_global_parameters_out = self.fit_global_parameters.from_fitted_parameters(self.parameters).duplicate()

        fit_global_parameters_out.set_convergence_reached(self.converged)

        if compute_pattern:
            fitted_patterns = self.build_fitted_diffraction_pattern(fit_global_parameters=fit_global_parameters_out)
        else:
            fitted_patterns = None

        self.converged = False

        return fitted_patterns, fit_global_parameters_out, self.fit_data

    def get_fitted_values_list(self):
        fitted_values_list = numpy.full(self.diffraction_patterns_number, None)
        
        for index in range(self.diffraction_patterns_number):
            fitted_values_list[index] = fit_function_direct(self.twotheta_experimental_list[index],
                                                            self.fit_global_parameters.from_fitted_parameters(self.parameters),
                                                            index)
        return fitted_values_list

    def __initialize_a_and_gradient(self):
        self.a        = self.__get_zero_trimatrix()
        self.gradient = self.__get_zero_vector()

        fitted_values_list = self.get_fitted_values_list()

        weighted_delta = self.__get_weighted_delta(fitted_values_list)
        derivative     = self.__get_derivative(fitted_values_list)

        for index in range(self.diffraction_patterns_number):
            derivative_i = derivative[index]
            weighted_delta_i = weighted_delta[index]

            for i in range(self.nr_points_list[index]):
                for j in range(self.nr_parameters_to_fit):
                    l = int(j * (j + 1) / 2)

                    self.gradient[j] += derivative_i[j, i] * weighted_delta_i[i]

                    for k in range(j+1):
                        self.a[l+k] += derivative_i[j, i] * derivative_i[k, i]

    def finalize_fit(self):
        pass

    def build_fitted_diffraction_pattern(self, fit_global_parameters):

        fitted_patterns = numpy.full(self.diffraction_patterns_number, None)

        for index in range(self.diffraction_patterns_number):
            wavelength = fit_global_parameters.fit_initialization.diffraction_patterns[index].wavelength

            fitted_pattern = DiffractionPattern(wavelength=wavelength)

            fitted_intensity = fit_function_direct(self.twotheta_experimental_list[index],
                                                   fit_global_parameters,
                                                   diffraction_pattern_index=index)
            fitted_residual = self.intensity_experimental_list[index] - fitted_intensity

            for i in range(0, len(fitted_intensity)):
                fitted_pattern.add_diffraction_point(diffraction_point=DiffractionPoint(twotheta=self.twotheta_experimental_list[index][i],
                                                                                        intensity=fitted_intensity[i],
                                                                                        error=fitted_residual[i]))
            fitted_patterns[index] = fitted_pattern

        return fitted_patterns


    def build_minpack_data(self, fitted_values_list=None):
        if fitted_values_list is None: fitted_values_list = self.get_fitted_values_list()

        self.wss = self.__get_wssq(fitted_values_list=fitted_values_list)

        self.fit_data.wss = self.wss
        self.fit_data.ss = self.__get_ssq_from_data(fitted_values_list=fitted_values_list)
        self.fit_data.wsq = self.__get_wssq_from_data(fitted_values_list=fitted_values_list)
        self.fit_data.calc_lambda = self._lambda
        self.fit_data.calculate()


    ###############################################
    #
    # METODI minObj
    #
    ###############################################

    def get_nr_points_list(self):
        return numpy.array([len(list) for list in self.twotheta_experimental_list])
        
    def get_nr_parameters_to_fit(self):
        nr_parameters_to_fit = 0

        for parameter in self.parameters:
            if parameter.is_variable(): nr_parameters_to_fit += 1

        return nr_parameters_to_fit

    def __get_weighted_delta(self, fitted_values_list=None):
        if fitted_values_list is None: fitted_values_list = self.get_fitted_values_list()

        weighted_delta = numpy.full(self.diffraction_patterns_number, None)

        for index in range(self.diffraction_patterns_number):
            weighted_delta[index] = get_weighted_delta(fitted_values_list[index],
                                                       self.intensity_experimental_list[index],
                                                       self.error_experimental_list[index],
                                                       self.nr_points_list[index])

        return weighted_delta

    def __get_derivative(self, fitted_values_list=None):
        if fitted_values_list is None: fitted_values_list = self.get_fitted_values_list()

        derivative = numpy.full(self.diffraction_patterns_number, None)

        for index in range(self.diffraction_patterns_number):
            twotheta_experimental = self.twotheta_experimental_list[index]
            error_experimental = self.error_experimental_list[index]
            fitted_values = fitted_values_list[index]

            nr_points_i  = self.nr_points_list[index]
            derivative_i = numpy.zeros((self.nr_parameters_to_fit, nr_points_i))

            j = 0
            for k in self.variable_indexes:
                parameter = self.parameters[k]

                pk = parameter.value
                if parameter.step == PARAM_ERR: step = 0.001
                else: step = parameter.step

                if abs(pk) > PRCSN:
                    d = pk*step
                    parameter.set_value(pk * (1.0 + step))

                    derivative_i[j, :] = fit_function_direct(twotheta_experimental,
                                                             self.fit_global_parameters.from_fitted_parameters(self.parameters),
                                                             diffraction_pattern_index=index)
                else:
                    d = step
                    parameter.set_value(pk + d)

                    derivative_i[j, :] = fit_function_direct(twotheta_experimental,
                                                             self.fit_global_parameters.from_fitted_parameters(self.parameters),
                                                             diffraction_pattern_index=index)

                parameter.set_value(pk)

                set_derivative(derivative_i, fitted_values, error_experimental, nr_points_i, d, j)

                j += 1

            derivative[index] = derivative_i

        return derivative

    def __get_wssq(self, fitted_values_list=None):
        if fitted_values_list is None: fitted_values_list = self.get_fitted_values_list()

        wssq = 0.0

        for index in range(self.diffraction_patterns_number):
            wssq += get_wssq(fitted_values_list[index],
                             self.intensity_experimental_list[index],
                             self.error_experimental_list[index],
                             self.nr_points_list[index],
                             self.mighell)

        return wssq

    def __get_wssq_from_data(self, fitted_values_list=None):
        if fitted_values_list is None: fitted_values_list = self.get_fitted_values_list()

        wssq = 0.0

        for index in range(self.diffraction_patterns_number):
            wssq += get_wssq_from_data(fitted_values_list[index],
                                       self.intensity_experimental_list[index],
                                       self.error_experimental_list[index],
                                       self.nr_points_list[index],
                                       self.mighell)

        return wssq

    def __get_ssq_from_data(self, fitted_values_list=None):
        if fitted_values_list is None: fitted_values_list = self.get_fitted_values_list()

        ssq = 0.0

        for index in range(self.diffraction_patterns_number):
            ssq += get_ssq_from_data(fitted_values_list[index],
                                     self.intensity_experimental_list[index],
                                     self.nr_points_list[index],
                                     self.mighell)

        return ssq

    def __set_a_diagonal(self):
        set_a_diagonal(self.g,
                       self.gradient,
                       self.a,
                       self.c,
                       self.nr_parameters_to_fit,
                       self._lambda,
                       self._phi)

    def __cholesky_decomposition_a(self):
        return cholesky_decomposition_a(self.a, self.nr_parameters_to_fit)

    def __cholesky_back_substitution_a(self):
        cholesky_back_substitution_a(self.a, self.nr_parameters_to_fit, self.g)

    def __populate_variables(self):
        self.initial_parameters[:] = [parameter.value for parameter in self.parameters[self.variable_indexes]]

    def __get_zero_vector(self):
        return numpy.zeros(self.nr_parameters_to_fit)

    def __get_zero_trimatrix(self):
        return numpy.zeros(int(self.nr_parameters_to_fit * (self.nr_parameters_to_fit + 1) / 2))


# performance improvement
from numba import jit

@jit(nopython=True)
def set_a_diagonal(g, grad, a, c, n, _lambda, _phi):
    da = _lambda*_phi
    for j in range(1, n+1):
        g[j-1] = -grad[j-1]
        l = int(j*(j+1)/2)-1
        a[l] = c[l] *(1.0 + _lambda) + da
        if j > 1:
            for i in range(1, j):
                a[l-i] = c[l-i]

@jit(nopython=True)
def cholesky_decomposition_a(a, n):
    for j in range(1, n+1):
        l = int(j*(j+1)/2) - 1

        if j>1:
            for i in range(j, n+1):
                k1 = int(i*(i-1)/2+j) - 1
                f = a[k1]
                for k in range(1, j): f -= a[k1-k]*a[l-k]
                a[k1] = f

        if a[l] > 0:
            f = numpy.sqrt(a[l])
            for i in range(j, n+1):
                a[int(i*(i-1)/2+j) - 1] /= f
        else:
            return -1 # negative diagonal

    return 0

@jit(nopython=True)
def cholesky_back_substitution_a(a, n, g):
    g[0] /= a[0]

    if n > 1:
        l=0
        for i in range(1, n):
            k=i
            for j in range(k):
                l += 1
                g[i] -= a[l]*g[j]
            l += 1
            g[i] /= a[l]

    g[int(n-1)] /= a[int(n*(n+1)/2)-1]

    if n > 1:
        for k1 in range(2, n + 1):
            i = n + 2 - k1
            k = i-1
            l = int(i*k/2)

            for j in range(k):
                g[j] -= g[k]*a[l+j]

            g[k-1] /= a[l-1]

@jit(nopython=True)
def get_weighted_delta(fitted_values, intensity_experimental, error_experimental, nr_points):
    weighted_delta_i = numpy.zeros(nr_points)

    for i in range(nr_points):
        if error_experimental[i] != 0.0:
            weighted_delta_i[i] = (fitted_values[i] - intensity_experimental[i])/error_experimental[i]

    return weighted_delta_i

@jit(nopython=True)
def set_derivative(derivative, fitted_values, error_experimental, nr_points, d, j):
    for i in range(0, nr_points):
        if error_experimental[i] == 0:
            derivative[j, i] = 0.0
        else:
            derivative[j, i] = (derivative[j, i] - fitted_values[i]) / (d * error_experimental[i])

@jit(nopython=True)
def get_wssq(fitted_values, intensity_experimental, error_experimental, nr_points, mighell):
    wssqlow = 0.0
    wssq = 0.0

    if mighell:
        for i in range(nr_points):
            yv = fitted_values[i] - (intensity_experimental[i] + (intensity_experimental[i] if intensity_experimental[i] < 1 else 1.0))

            wssqtmp = (yv**2)/(error_experimental[i]**2+1.0)

            if (wssqtmp<1E-2):
                wssqlow += wssqtmp
            else:
                wssq    += wssqtmp
    else:
        for i in range(nr_points):
            if error_experimental[i] == 0.0:
                yv = 0.0
            else:
                yv = (fitted_values[i] - intensity_experimental[i]) / error_experimental[i]

            wssqtmp = (yv**2)

            if (wssqtmp<1E-2):
                wssqlow += wssqtmp
            else:
                wssq    += wssqtmp

    return wssq + wssqlow

@jit(nopython=True)
def get_wssq_from_data(fitted_values, intensity_experimental, error_experimental, nr_points, mighell):
    wssq = 0.0

    for i in range(nr_points):
        if not mighell:
            if error_experimental[i] == 0.0:
                yv = 0.0
            else:
                yv = (fitted_values[i] - intensity_experimental[i]) / error_experimental[i]

            wssq += (yv**2)
        else:
            if intensity_experimental[i] < 1:
                yv = fitted_values[i] - 2 * intensity_experimental[i]
            else:
                yv = fitted_values[i] - (intensity_experimental[i] + 1.0)

            wssq += (yv**2)/(error_experimental[i]**2+1.0)

    return wssq

@jit(nopython=True)
def get_ssq_from_data(fitted_values, intensity_experimental, nr_points, mighell):
    ssq = 0.0

    for i in range(0, nr_points):
        if mighell:
            yv = fitted_values[i] - (intensity_experimental[i] + (intensity_experimental[i] if intensity_experimental[i] < 1 else 1.0))
        else:
            yv = (fitted_values[i] - intensity_experimental[i])

        ssq += yv**2

    return ssq

