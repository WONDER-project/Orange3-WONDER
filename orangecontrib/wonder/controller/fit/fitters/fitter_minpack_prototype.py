from orangecontrib.wonder.controller.fit.fitter import FitterInterface

from orangecontrib.wonder.model.diffraction_pattern import DiffractionPattern, DiffractionPoint
from orangecontrib.wonder.controller.fit.fit_parameter import PARAM_ERR
from orangecontrib.wonder.controller.fit.fitters.fitter_minpack_util import *
from orangecontrib.wonder.controller.fit.wppm_functions import fit_function_direct
from orangecontrib.wonder.controller.fit.fit_global_parameters import FitGlobalParameters

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

class FitterMinpackPrototype(FitterInterface):

    def __init__(self):
        super().__init__()

    def init_fitter(self, fit_global_parameters):
        print("Initializing Fitter...")

        self.fit_global_parameters = fit_global_parameters
        self.fit_global_parameters_aux = fit_global_parameters.duplicate()

        self.totalWeight = 0.0

        self._lambda	= .001
        self._lmin	= 1E20
        self._totIter	= 0
        self._nincr = 0
        self._phi = 1.2 # relaxation factor

        self.currpar = CVector()
        self.initialpar = CVector()

        # INITIALIZATION OF FUNCTION VALUES

        self.fit_global_parameters.evaluate_functions()

        self.parameters = self.fit_global_parameters.get_parameters()

        self.has_functions = FitGlobalParameters.parameters_have_functions(self.parameters)

        self.diffraction_patterns_number = self.fit_global_parameters.fit_initialization.get_diffraction_patterns_number()

        self.twotheta_experimental_list = numpy.array([None]*self.diffraction_patterns_number)
        self.intensity_experimental_list = numpy.array([None]*self.diffraction_patterns_number)
        self.error_experimental_list = numpy.array([None]*self.diffraction_patterns_number)

        for index in range(self.diffraction_patterns_number):
            twotheta_experimental, intensity_experimental, error_experimental, s_experimental = self.fit_global_parameters.fit_initialization.diffraction_patterns[index].tuples()

            self.twotheta_experimental_list[index] = numpy.array(twotheta_experimental)
            self.intensity_experimental_list[index] = numpy.array(intensity_experimental)
            self.error_experimental_list[index] = numpy.array(error_experimental)

        self.nr_points = self.getNrPoints()

        self.nprm = len(self.parameters)
        self.nfit = self.getNrParamToFit()
        self.nobs = self.nr_points
        self.dof = self.nobs - self.nfit

        self.a = CTriMatrix(_n=self.nfit)
        self.c = CTriMatrix(_n=self.nfit)
        self.g = CVector(_n=self.nfit)
        self.grad = CVector(_n=self.nfit)
        self.currpar = CVector(_n=self.nfit)
        self.initialpar = CVector(_n=self.nfit)

        self.mighell = False

        self.nincr	= 0 # number of increments in lambda
        self.wss = self.getWSSQ()
        self.oldwss  = self.wss

        self.fit_data = MinpackData(wss=self.wss,
                                    dof=self.dof,
                                    nobs=self.nobs,
                                    nprm=self.nprm,
                                    nfit=self.nfit)

        self.conver = False
        self.exitflag  = False

        j = 0
        for  i in range (0, self.nprm):
            parameter = self.parameters[i]

            if parameter.is_variable():
                j += 1
                self.initialpar.setitem(j, parameter.value)

        print("Fitter Initialization done.")

    def do_fit(self, current_fit_global_parameters, current_iteration, compute_pattern, compute_errors):
        print("Fitter - Begin iteration nr. " + str(current_iteration))

        self.fit_global_parameters = current_fit_global_parameters.duplicate()

        if current_iteration <= current_fit_global_parameters.get_n_max_iterations() and not self.conver:
            # check values of lambda for large number of iterations
            if (self._totIter > 4 and self._lambda < self._lmin): self._lmin = self._lambda

            #update total number of iterations
            self._totIter += 1

            #decrease lambda using golden section 0.31622777=1/(sqrt(10.0))
            self._lambda *= 0.31622777

            #number of increments in lambda
            self._nincr = 0

            #zero the working arrays
            self.a.zero()
            self.grad.zero()

            self.set()

            self.c.assign(self.a) #save the matrix A and the current value of the parameters

            j = 0
            for i in range(0, self.nprm):
                if self.parameters[i].is_variable():
                    j += 1
                    self.initialpar.setitem(j, self.parameters[i].value)
                    self.currpar.setitem(j, self.initialpar.getitem(j))

            # emulate C++ do ... while cycle
            do_cycle = True

            print("Begin Minization using LAMBDA: ", self._lambda)

            while do_cycle:
                self.exitflag = False
                self.conver = False

                #set the diagonal of A to be A*(1+lambda)+phi*lambda
                da = self._phi*self._lambda

                for jj in range(1, self.nfit+1):
                    self.g.setitem(jj, -self.grad.getitem(jj))
                    l = int(jj*(jj+1)/2)
                    self.a.setitem(l, self.c.getitem(l)*(1.0 + self._lambda) + da)
                    if jj > 1:
                        for i in range (1, jj):
                            self.a.setitem(l-i, self.c.getitem(l-i))

                if self.a.chodec() == 0: # Cholesky decomposition
                    # the matrix is inverted, so calculate g (change in the
                    # parameters) by back substitution

                    self.a.choback(self.g)

                    prevwss = self.oldwss
                    recycle = 1

                    # Update the parameters: param = old param + g
                    # n0 counts the number of zero elements in g
                    do_cycle_2 = True
                    while do_cycle_2:
                        recyc = False
                        n0 = 0
                        i = 0
                        for j in range(0, self.nprm):
                            if self.parameters[j].is_variable():
                                i += 1

                                # update value of parameter
                                #  apply the required constraints (min/max)
                                self.parameters[j].set_value(self.currpar.getitem(i) + recycle*self.g.getitem(i))

                                # check number of parameters reaching convergence
                                if (abs(self.g.getitem(i))<=abs(PRCSN*self.currpar.getitem(i))): n0 += 1

                        # calculate functions
                        if self.has_functions:
                            FitGlobalParameters.compute_functions(self.parameters,
                                                                  current_fit_global_parameters.free_input_parameters,
                                                                  current_fit_global_parameters.free_output_parameters)

                        if (n0==self.nfit):
                            self.conver = True

                        # update the wss
                        self.wss = self.getWSSQ()

                        if self.wss < prevwss:
                            prevwss = self.wss
                            recyc = True
                            recycle += 1

                        # last line of while loop
                        do_cycle_2 = recyc and recycle<10

                    if recycle > 1:

                        # restore parameters to best value
                        recycle -= 1

                        i = 0
                        for j in range(0, self.nprm):
                            if self.parameters[j].is_variable():
                                i += 1
                                # update value of parameter
                                #  apply the required constraints (min/max)
                                self.parameters[j].set_value(self.currpar.getitem(i) + recycle*self.g.getitem(i))

                        # calculate functions
                        if self.has_functions:
                            FitGlobalParameters.compute_functions(self.parameters,
                                                                  current_fit_global_parameters.free_input_parameters,
                                                                  current_fit_global_parameters.free_output_parameters)

                        # update the wss
                        self.wss = self.getWSSQ()

                    # if all parameters reached convergence then it's time to quit

                    if self.wss < self.oldwss:
                        self.oldwss     = self.wss
                        self.exitflag   = True

                        ii = 0
                        for j in range(0, self.nprm):
                            if self.parameters[j].is_variable():
                                ii += 1

                                # update value of parameter
                                self.initialpar.setitem(ii, self.currpar.getitem(ii) + recycle*self.g.getitem(ii))


                    y_list = [None]*self.diffraction_patterns_number
                    
                    for index in range(self.diffraction_patterns_number):
                        y_list[index] = fit_function_direct(self.twotheta_experimental_list[index],
                                                            self.fit_global_parameters_aux.from_fitted_parameters(self.parameters),
                                                            index)

                    self.build_minpack_data(y_list=y_list)

                    print(self.fit_data.to_text())
                else:
                    if self.has_functions:
                        FitGlobalParameters.compute_functions(self.parameters,
                                                              current_fit_global_parameters.free_input_parameters,
                                                              current_fit_global_parameters.free_output_parameters)

                    print("Chlolesky decomposition failed!")

                if not self.exitflag  and not self.conver:
                    if self._lambda<PRCSN: self._lambda = PRCSN
                    self._nincr += 1
                    self._lambda *= 10.0
                    if self._lambda>(1E5*self._lmin): self.conver = True

                # last line of the while loop
                do_cycle =  not self.exitflag and not self.conver

            j = 0
            for i in range(0, self.nprm):
                if self.parameters[i].is_variable():
                    j += 1
                    self.parameters[i].set_value(self.initialpar.getitem(j))

            if self.has_functions:
                FitGlobalParameters.compute_functions(self.parameters,
                                                      current_fit_global_parameters.free_input_parameters,
                                                      current_fit_global_parameters.free_output_parameters)

        fit_global_parameters_out = self.fit_global_parameters_aux.from_fitted_parameters(self.parameters).duplicate()
        fit_global_parameters_out.set_convergence_reached(self.conver)

        fitted_patterns = self.build_fitted_diffraction_pattern(fit_global_parameters=fit_global_parameters_out)

        self.conver = False

        errors = [0] * len(self.parameters)

        self.a.zero()
        self.grad.zero()
        self.set()

        if self.a.chodec() == 0: # Cholesky decomposition
            k = 0
            for i in range (0, self.nprm):
                if self.parameters[i].is_variable():

                    self.g.zero()
                    self.g[k] = 1.0
                    self.a.choback(self.g)
                    errors[i] = numpy.sqrt(numpy.abs(self.g[k]))
                    k += 1
        else:
            print("Errors not calculated: chodec != 0")

        fit_global_parameters_out.from_fitted_errors(errors=errors)

        return fitted_patterns, fit_global_parameters_out, self.fit_data

    def set(self):
        fmm = self.getWeightedDelta()
        deriv = self.getDerivative()

        for index in range(self.diffraction_patterns_number):
            deriv_i = deriv[index]
            fmm_i = fmm[index]

            for i in range(1, self.getNrPoints(index) + 1):
                for jj in range(1, self.nfit + 1):

                    l = int(jj * (jj - 1) / 2)
                    self.grad.setitem(jj, self.grad.getitem(jj) + deriv_i.getitem(jj, i) * fmm_i[i - 1])

                    for k in range(1, jj + 1):
                        self.a.setitem(l + k, self.a.getitem(l + k) + deriv_i.getitem(jj, i) * deriv_i.getitem(k, i))

    def finalize_fit(self):
        pass



    def build_fitted_diffraction_pattern(self, fit_global_parameters):

        fitted_patterns = []

        for index in range(len(fit_global_parameters.fit_initialization.diffraction_patterns)):
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
            fitted_patterns.append(fitted_pattern)

        return fitted_patterns


    def build_minpack_data(self, y_list=None):
        self.wss = self.getWSSQ(y_list=y_list)

        self.fit_data.wss = self.wss
        self.fit_data.ss = self.getSSQFromData(y_list=y_list)
        self.fit_data.wsq = self.getWSQFromData(y_list=y_list)
        self.fit_data.calc_lambda = self._lambda
        self.fit_data.calculate()


    ###############################################
    #
    # METODI minObj
    #
    ###############################################

    def getNrPoints(self, diffraction_patterns_index=None):
        if diffraction_patterns_index is None:
            nr_points = 0
            for list in self.twotheta_experimental_list: nr_points += len(list)
    
            return nr_points
        else:
            return len(self.twotheta_experimental_list[diffraction_patterns_index])

    def getNrParamToFit(self):
        nfit = 0
        for parameter in self.parameters:
            if parameter.is_variable():
                nfit += 1
        return nfit

    def getWeightedDelta(self):
        fmm = []

        for index in range(self.diffraction_patterns_number):
            twotheta_experimental = self.twotheta_experimental_list[index]
            intensity_experimental = self.intensity_experimental_list[index]
            error_experimental = self.error_experimental_list[index]

            y = fit_function_direct(twotheta_experimental,
                                    self.fit_global_parameters_aux.from_fitted_parameters(self.parameters),
                                    diffraction_pattern_index=index)

            fmm_i = [0]*self.getNrPoints(index)

            for i in range (0, self.getNrPoints(index)):
                if error_experimental[i] == 0:
                    fmm_i[i] = 0
                else:
                    fmm_i[i] = (y[i] - intensity_experimental[i])/error_experimental[i]

            fmm.append(fmm_i)

        return fmm

    def getDerivative(self):
        deriv = []

        for index in range(self.diffraction_patterns_number):
            twotheta_experimental = self.twotheta_experimental_list[index]
            error_experimental = self.error_experimental_list[index]

            y = fit_function_direct(twotheta_experimental,
                                    self.fit_global_parameters_aux.from_fitted_parameters(self.parameters),
                                    diffraction_pattern_index=index)

            nr_points_i = self.getNrPoints(index)
            deriv_i = CMatrix(self.getNrParamToFit(), nr_points_i)

            jj = 0
            for k in range (0, self.nprm):
                parameter = self.parameters[k]

                if parameter.is_variable():
                    pk = parameter.value
                    if parameter.step == PARAM_ERR: step = 0.001
                    else: step = parameter.step

                    if abs(pk) > PRCSN:
                        d = pk*step
                        parameter.value = pk * (1.0 + step)
                        parameter.check_value()

                        deriv_i[jj] = fit_function_direct(twotheta_experimental,
                                                          self.fit_global_parameters_aux.from_fitted_parameters(self.parameters),
                                                          diffraction_pattern_index=index)
                    else:
                        d = step
                        parameter.value = pk + d
                        parameter.check_value()

                        deriv_i[jj] = fit_function_direct(twotheta_experimental,
                                                          self.fit_global_parameters_aux.from_fitted_parameters(self.parameters),
                                                          diffraction_pattern_index=index)

                    parameter.value = pk
                    parameter.check_value()

                    for i in range(0, nr_points_i):
                        if error_experimental[i] == 0:
                            deriv_i[jj][i] = 0.0
                        else:
                            deriv_i[jj][i] = (deriv_i[jj][i] - y[i]) / (d * error_experimental[i])
                    jj += 1

            deriv.append(deriv_i)

        return deriv

    def getWSSQ(self, y_list=None):
        if y_list is None: 
            y_list = [None]*self.diffraction_patterns_number
            
            for index in range(self.diffraction_patterns_number):
                y_list[index] = fit_function_direct(self.twotheta_experimental_list[index],
                                                    self.fit_global_parameters_aux.from_fitted_parameters(self.parameters),
                                                    index)

        wssqlow = 0.0
        wssq = 0.0

        for index in range(self.diffraction_patterns_number):
            y = y_list[index]
            intensity_experimental = self.intensity_experimental_list[index]
            error_experimental = self.error_experimental_list[index]
            
            if self.mighell:
                for i in range(0, self.getNrPoints(index)):
                    yv = y[i] - (intensity_experimental[i] + (intensity_experimental[i] if intensity_experimental[i] < 1 else 1.0))

                    wssqtmp = (yv**2)/(error_experimental[i]**2+1.0)
    
                    if (wssqtmp<1E-2):
                        wssqlow += wssqtmp
                    else:
                        wssq    += wssqtmp
            else:
                for i in range(0, self.getNrPoints(index)):    
                    if error_experimental[i] == 0.0:
                        yv = 0.0
                    else:
                        yv = (y[i] - intensity_experimental[i])/error_experimental[i]
    
                    wssqtmp = (yv**2)

                    if (wssqtmp<1E-2):
                        wssqlow += wssqtmp
                    else:
                        wssq    += wssqtmp

        return wssq + wssqlow


    def getWSQFromData(self, y_list=None):
        if y_list is None: 
            y_list = [None]*self.diffraction_patterns_number
            
            for index in range(self.diffraction_patterns_number):
                y_list[index] = fit_function_direct(self.twotheta_experimental_list[index],
                                                    self.fit_global_parameters_aux.from_fitted_parameters(self.parameters),
                                                    index)

        wssq = 0.0

        for index in range(self.diffraction_patterns_number):
            y = y_list[index]
            intensity_experimental = self.intensity_experimental_list[index]
            error_experimental = self.error_experimental_list[index]
            
            for i in range(0, self.getNrPoints(index)):
                if not self.mighell:
                    if error_experimental[i] == 0.0:
                        yv = 0.0
                    else:
                        yv = (y[i] - intensity_experimental[i])/error_experimental[i]
    
                    wssq += (yv**2)
                else:
                    if intensity_experimental[i] < 1:
                        yv = y[i] - 2*intensity_experimental[i]
                    else:
                        yv = y[i] - (intensity_experimental[i] + 1.0)
    
                    wssq += (yv**2)/(error_experimental[i]**2+1.0)

        return wssq

    def getSSQFromData(self, y_list=None):
        if y_list is None: 
            y_list = [None]*self.diffraction_patterns_number
            
            for index in range(self.diffraction_patterns_number):
                y_list[index] = fit_function_direct(self.twotheta_experimental_list[index],
                                                    self.fit_global_parameters_aux.from_fitted_parameters(self.parameters),
                                                    index)

        ss = 0.0

        for index in range(self.diffraction_patterns_number):
            y = y_list[index]
            intensity_experimental = self.intensity_experimental_list[index]

            for i in range(0, self.getNrPoints(index)):
                if self.mighell:
                    yv = y[i] - (intensity_experimental[i] + (intensity_experimental[i] if intensity_experimental[i] < 1 else 1.0))
                else:
                    yv = (y[i] - intensity_experimental[i])

                ss += yv**2

        return ss


