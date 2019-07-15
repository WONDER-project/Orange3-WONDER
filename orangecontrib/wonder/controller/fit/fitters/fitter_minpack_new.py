from orangecontrib.wonder.controller.fit.fitter import FitterInterface

from orangecontrib.wonder.model.diffraction_pattern import DiffractionPattern, DiffractionPoint
from orangecontrib.wonder.controller.fit.fit_parameter import PARAM_ERR
from orangecontrib.wonder.controller.fit.fitters.fitter_minpack_util_new import *
from orangecontrib.wonder.controller.fit.wppm_functions import fit_function_direct
from orangecontrib.wonder.controller.fit.wppm_functions_multipool import fit_function_direct_multipool
from orangecontrib.wonder.controller.fit.fit_global_parameters import FitGlobalParameters

import time

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

    def to_text(self):
        text = "\nCurrent fit results:\n\n"
        text += "  total parameters   (nprm): " + str(self.nprm) + "\n"
        text += "  parameters to fit  (nfit): " + str(self.nfit) + "\n"
        text += "  nr. of observables (nobs): " + str(self.nobs) + "\n"
        text += "  dof (nobs - nfit)        : " + str(self.dof)  + "\n"
        text += "  LAMBDA: " + str(self.calc_lambda)+ "\n"
        text += "  wss: " + str(self.wss) + "\n"
        text += "  ss : " + str(self.ss) + "\n"
        text += "  wsq: " + str(self.wsq) + "\n"
        text += "  gof: " + str(self.gof())+ "\n"

        return text

class FitterMinpackNew(FitterInterface):

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

        self.a = CTriMatrix(_n=self.nr_parameters_to_fit)
        self.c = CTriMatrix(_n=self.nr_parameters_to_fit)

        #self.g = CVector(_n=self.nr_parameters_to_fit)
        #self.grad = CVector(_n=self.nr_parameters_to_fit)
        #self.current_pararameters = CVector(_n=self.nr_parameters_to_fit)
        #self.initial_parameters = CVector(_n=self.nr_parameters_to_fit)

        self.g                    = numpy.zeros(self.nr_parameters_to_fit)
        self.grad                 = numpy.zeros(self.nr_parameters_to_fit)
        self.current_pararameters = numpy.zeros(self.nr_parameters_to_fit)
        self.initial_parameters   = numpy.zeros(self.nr_parameters_to_fit)

        self.mighell = False

        self.wss      = self.__get_wssq()
        self.old_wss  = self.wss

        self.fit_data = MinpackData(wss=self.wss,
                                    dof=self.degrees_of_freedom,
                                    nobs=self.nr_observables,
                                    nprm=self.nr_parameters,
                                    nfit=self.nr_parameters_to_fit)

        self.converged = False
        self.exit_flag  = False

        self.__populate_variables()

        print("Fitter Initialization done.")

    def do_fit(self, current_fit_global_parameters, current_iteration, compute_pattern):
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

            start_time = time.clock()

            #zero the working arrays
            self.a.zero()
            self.grad = numpy.zeros(self.nr_parameters_to_fit)

            self.set()

            self.c.assign(self.a) #save the matrix A and the current value of the parameters

            self.__populate_variables()
            self.current_pararameters = copy.deepcopy(self.initial_parameters)

            # emulate C++ do ... while cycle
            do_cycle = True

            print("Begin Minization using LAMBDA: ", self._lambda)

            while do_cycle:
                self.exit_flag = False
                self.converged = False

                #set the diagonal of A to be A*(1+lambda)+phi*lambda
                self.__set_A_diagonal()

                if self.a.chodec() == 0: # Cholesky decomposition
                    # the matrix is inverted, so calculate g (change in the
                    # parameters) by back substitution

                    self.a.choback(self.g)

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
                            if (abs(self.g[i])<=abs(PRCSN*self.current_pararameters[i])): nr_0_elements_in_g += 1
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

                    print(self.fit_data.to_text())
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

        fit_global_parameters_out = self.fit_global_parameters.from_fitted_parameters(self.parameters).duplicate()
        fit_global_parameters_out.set_convergence_reached(self.converged)

        if compute_pattern:
            fitted_patterns = self.build_fitted_diffraction_pattern(fit_global_parameters=fit_global_parameters_out)
        else:
            fitted_patterns = None

        self.converged = False

        errors = numpy.zeros(self.nr_parameters)

        self.a.zero()
        self.grad = numpy.zeros(self.nr_parameters_to_fit)
        self.set()

        if self.a.chodec() == 0: # Cholesky decomposition
            k = 0
            for i in self.variable_indexes:
                self.g = numpy.zeros(self.nr_parameters_to_fit)
                self.g[k] = 1.0
                self.a.choback(self.g)
                errors[i] = numpy.sqrt(numpy.abs(self.g[k]))
                k += 1
        else:
            print("Errors not calculated: chodec != 0")

        fit_global_parameters_out.from_fitted_errors(errors=errors)

        return fitted_patterns, fit_global_parameters_out, self.fit_data

    def get_fitted_values_list(self):
        fitted_values_list = numpy.full(self.diffraction_patterns_number, None)
        
        for index in range(self.diffraction_patterns_number):
            fitted_values_list[index] = fit_function_direct(self.twotheta_experimental_list[index],
                                                            self.fit_global_parameters.from_fitted_parameters(self.parameters),
                                                            index)
        return fitted_values_list

    def set(self):
        fitted_values_list = self.get_fitted_values_list()

        weighted_delta = self.get_weighted_delta(fitted_values_list)
        derivative     = self.get_derivative(fitted_values_list)

        for index in range(self.diffraction_patterns_number):
            derivative_i = derivative[index]
            weighted_delta_i = weighted_delta[index]

            for i in range(1, self.nr_points_list[index] + 1):
                for j in range(1, self.nr_parameters_to_fit + 1):

                    l = int(j * (j - 1) / 2)
                    self.grad[j-1] = self.grad[j-1] + derivative_i.getitem(j, i) * weighted_delta_i[i - 1]

                    for k in range(1, j + 1):
                        self.a.setitem(l + k, self.a.getitem(l + k) + derivative_i.getitem(j, i) * derivative_i.getitem(k, i))

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

    def get_weighted_delta(self, fitted_values_list=None):
        if fitted_values_list is None: fitted_values_list = self.get_fitted_values_list()

        fmm = numpy.full(self.diffraction_patterns_number, None)

        for index in range(self.diffraction_patterns_number):
            intensity_experimental = self.intensity_experimental_list[index]
            error_experimental = self.error_experimental_list[index]
            fitted_values = fitted_values_list[index]

            cursor = numpy.where(error_experimental!=0.0)

            fmm[index]         = numpy.zeros(self.nr_points_list[index])
            fmm[index][cursor] = (fitted_values[cursor] - intensity_experimental[cursor])/error_experimental[cursor]

        return fmm

    def get_derivative(self, fitted_values_list=None):
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

                for i in range(0, nr_points_i):
                    if error_experimental[i] == 0:
                        derivative_i[j, i] = 0.0
                    else:
                        derivative_i[j, i] = (derivative_i[j, i] - fitted_values[i]) / (d * error_experimental[i])
                j += 1

            derivative[index] = CMatrix()
            derivative[index].set_attributes(derivative_i)

        return derivative

    def __get_wssq(self, fitted_values_list=None):
        if fitted_values_list is None: fitted_values_list = self.get_fitted_values_list()

        wssq = 0.0

        for index in range(self.diffraction_patterns_number):
            fitted_values = fitted_values_list[index]
            intensity_experimental = self.intensity_experimental_list[index]
            error_experimental = self.error_experimental_list[index]

            wssq += get_wssq(fitted_values, intensity_experimental, error_experimental, self.nr_points_list[index], self.mighell)

        return wssq

    def __get_wssq_from_data(self, fitted_values_list=None):
        if fitted_values_list is None: fitted_values_list = self.get_fitted_values_list()

        wssq = 0.0

        for index in range(self.diffraction_patterns_number):
            fitted_values = fitted_values_list[index]
            intensity_experimental = self.intensity_experimental_list[index]
            error_experimental = self.error_experimental_list[index]

            wssq += get_wssq_from_data(fitted_values , intensity_experimental, error_experimental, self.nr_points_list[index], self.mighell)

        return wssq

    def __get_ssq_from_data(self, fitted_values_list=None):
        if fitted_values_list is None: fitted_values_list = self.get_fitted_values_list()

        ssq = 0.0

        for index in range(self.diffraction_patterns_number):
            ssq += get_ssq_from_data(fitted_values_list[index], self.intensity_experimental_list[index], self.nr_points_list[index], self.mighell)

        return ssq

    def __set_A_diagonal(self):
        set_A_diagonal(self.g,
                       self.grad,
                       self.a.get_attributes(),
                       self.c.get_attributes(),
                       self.nr_parameters_to_fit,
                       self._lambda,
                       self._phi)

    def __populate_variables(self):
        populate_variables(self.parameters, self.variable_indexes, self.initial_parameters)

# performance improvement
from numba import jit

@jit
def populate_variables(parameters, variable_indexes, initial_parameters):
    j = 0
    for i in variable_indexes:
        initial_parameters[j] = parameters[i].value
        j += 1

@jit(nopython=True)
def set_A_diagonal(data_g, data_grad, data_a, data_c, n, _lambda, _phi):
    da = _lambda*_phi

    for j in range(1, n+1):
        data_g[j-1] = -data_grad[j-1]
        #setitem_cvector(data_g, n, j, -getitem_cvector(data_grad, n, j))

        l = int(j*(j+1)/2)

        setitem_ctrimatrix(data_a, n, l, getitem_ctrimatrix(data_c, n, l)*(1.0 + _lambda) + da)
        if j > 1:
            for i in range (1, j):
                setitem_ctrimatrix(data_a, n, l-i, getitem_ctrimatrix(data_c, n, l-i))

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

