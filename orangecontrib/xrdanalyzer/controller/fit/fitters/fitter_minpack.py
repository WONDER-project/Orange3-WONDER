from orangecontrib.xrdanalyzer.controller.fit.fitter import FitterInterface

from orangecontrib.xrdanalyzer.model.diffraction_pattern import DiffractionPattern, DiffractionPoint
from orangecontrib.xrdanalyzer.controller.fit.fit_parameter import PARAM_ERR
from orangecontrib.xrdanalyzer.controller.fit.instrument.instrumental_parameters import Lab6TanCorrection, ZeroError, SpecimenDisplacement
from orangecontrib.xrdanalyzer.controller.fit.instrument.background_parameters import ChebyshevBackground, ExpDecayBackground
from orangecontrib.xrdanalyzer.controller.fit.microstructure.size import Distribution
from orangecontrib.xrdanalyzer.controller.fit.microstructure.strain import InvariantPAH, WarrenModel, KrivoglazWilkensModel
from orangecontrib.xrdanalyzer.controller.fit.fitters.fitter_minpack_util import *
from orangecontrib.xrdanalyzer.controller.fit.wppm_functions import fit_function_direct

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

class FitterMinpack(FitterInterface):

    def __init__(self):
        super().__init__()

    def init_fitter(self, fit_global_parameters):
        print("Initializing Fitter...")

        self.fit_global_parameters = fit_global_parameters

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

    def do_fit(self, current_fit_global_parameters, current_iteration):
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

                        self.parameters = self.build_fit_global_parameters_out(self.parameters).get_parameters()

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
                        self.parameters = self.build_fit_global_parameters_out(self.parameters).get_parameters()

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
                                                            self.build_fit_global_parameters_out(self.parameters),
                                                            index)

                    self.build_minpack_data(y_list=y_list)

                    print(self.fit_data.to_text())
                else:
                    self.parameters = self.build_fit_global_parameters_out(self.parameters).get_parameters()

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

            self.parameters = self.build_fit_global_parameters_out(self.parameters).get_parameters()

        fitted_parameters = self.parameters

        fit_global_parameters_out = self.build_fit_global_parameters_out(fitted_parameters)
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

        fit_global_parameters_out = self.build_fit_global_parameters_out_errors(errors=errors)

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


    def build_fit_global_parameters_out(self, fitted_parameters):
        fit_global_parameters = self.fit_global_parameters

        last_index = -1

        for index in range(len(fit_global_parameters.fit_initialization.diffraction_patterns)):
            diffraction_pattern = fit_global_parameters.fit_initialization.diffraction_patterns[index]
            diffraction_pattern.wavelength.set_value(fitted_parameters[last_index + 1].value)

            last_index += 1

            if not diffraction_pattern.is_single_wavelength:
                for secondary_wavelength, secondary_wavelength_weigth in zip(diffraction_pattern.secondary_wavelengths,
                                                                             diffraction_pattern.secondary_wavelengths_weights):
                    secondary_wavelength.set_value(fitted_parameters[last_index + 1].value)
                    secondary_wavelength_weigth.set_value(fitted_parameters[last_index + 2].value)
                    last_index += 2

        #if last_index < 0: last_index = len(fit_global_parameters.fit_initialization.diffraction_patterns) - 1

        for index in range(len(fit_global_parameters.fit_initialization.crystal_structures)):
            crystal_structure = fit_global_parameters.fit_initialization.crystal_structures[index]

            crystal_structure.a.set_value(fitted_parameters[last_index + 1].value)
            crystal_structure.b.set_value(fitted_parameters[last_index + 2].value)
            crystal_structure.c.set_value(fitted_parameters[last_index + 3].value)
            crystal_structure.alpha.set_value(fitted_parameters[last_index + 4].value)
            crystal_structure.beta.set_value(fitted_parameters[last_index + 5].value)
            crystal_structure.gamma.set_value(fitted_parameters[last_index + 6].value)

            if crystal_structure.use_structure:
                crystal_structure.intensity_scale_factor.set_value(fitted_parameters[last_index + 7].value)
                last_index += 7
            else:
                last_index += 6

            for reflection_index in range(crystal_structure.get_reflections_count()):
                crystal_structure.get_reflection(reflection_index).intensity.set_value(fitted_parameters[last_index + 1 + reflection_index].value)

            last_index += crystal_structure.get_reflections_count()

        if not fit_global_parameters.fit_initialization.thermal_polarization_parameters is None:
            for thermal_polarization_parameters in fit_global_parameters.fit_initialization.thermal_polarization_parameters:
                if not thermal_polarization_parameters.debye_waller_factor is None:
                    thermal_polarization_parameters.debye_waller_factor.set_value(fitted_parameters[last_index + 1].value)

                    last_index += thermal_polarization_parameters.get_parameters_count()

        if not fit_global_parameters.background_parameters is None:
            for key in fit_global_parameters.background_parameters.keys():
                background_parameters_list = fit_global_parameters.get_background_parameters(key)

                if not background_parameters_list is None:
                    for background_parameters in background_parameters_list:
                        if key == ChebyshevBackground.__name__:
                            background_parameters.c0.set_value(fitted_parameters[last_index + 1].value)
                            background_parameters.c1.set_value(fitted_parameters[last_index + 2].value)
                            background_parameters.c2.set_value(fitted_parameters[last_index + 3].value)
                            background_parameters.c3.set_value(fitted_parameters[last_index + 4].value)
                            background_parameters.c4.set_value(fitted_parameters[last_index + 5].value)
                            background_parameters.c5.set_value(fitted_parameters[last_index + 6].value)
                            background_parameters.c6.set_value(fitted_parameters[last_index + 7].value)
                            background_parameters.c7.set_value(fitted_parameters[last_index + 8].value)
                            background_parameters.c8.set_value(fitted_parameters[last_index + 9].value)
                            background_parameters.c9.set_value(fitted_parameters[last_index + 10].value)
                        elif key == ExpDecayBackground.__name__:
                            background_parameters.a0.set_value(fitted_parameters[last_index + 1].value)
                            background_parameters.b0.set_value(fitted_parameters[last_index + 2].value)
                            background_parameters.a1.set_value(fitted_parameters[last_index + 3].value)
                            background_parameters.b1.set_value(fitted_parameters[last_index + 4].value)
                            background_parameters.a2.set_value(fitted_parameters[last_index + 5].value)
                            background_parameters.b2.set_value(fitted_parameters[last_index + 6].value)

                        last_index += background_parameters.get_parameters_count()

        if not fit_global_parameters.instrumental_parameters is None:
            for instrumental_parameters in fit_global_parameters.instrumental_parameters:
                instrumental_parameters.U.set_value(fitted_parameters[last_index + 1].value)
                instrumental_parameters.V.set_value(fitted_parameters[last_index + 2].value)
                instrumental_parameters.W.set_value(fitted_parameters[last_index + 3].value)
                instrumental_parameters.a.set_value(fitted_parameters[last_index + 4].value)
                instrumental_parameters.b.set_value(fitted_parameters[last_index + 5].value)
                instrumental_parameters.c.set_value(fitted_parameters[last_index + 6].value)

                last_index += instrumental_parameters.get_parameters_count()

        if not fit_global_parameters.shift_parameters is None:
            for key in fit_global_parameters.shift_parameters.keys():
                shift_parameters_list = fit_global_parameters.get_shift_parameters(key)

                if not shift_parameters_list is None:
                    for shift_parameters in shift_parameters_list:
                        if key == Lab6TanCorrection.__name__:
                            shift_parameters.ax.set_value(fitted_parameters[last_index + 1].value)
                            shift_parameters.bx.set_value(fitted_parameters[last_index + 2].value)
                            shift_parameters.cx.set_value(fitted_parameters[last_index + 3].value)
                            shift_parameters.dx.set_value(fitted_parameters[last_index + 4].value)
                            shift_parameters.ex.set_value(fitted_parameters[last_index + 5].value)
                        elif key == ZeroError.__name__:
                            shift_parameters.shift.set_value(fitted_parameters[last_index + 1].value)
                        elif key == SpecimenDisplacement.__name__:
                            shift_parameters.displacement.set_value(fitted_parameters[last_index + 1].value)

                    last_index += shift_parameters.get_parameters_count()

        if not fit_global_parameters.size_parameters is None:
            for size_parameters in fit_global_parameters.size_parameters:
                size_parameters.mu.set_value(fitted_parameters[last_index + 1].value)
                if size_parameters.distribution == Distribution.LOGNORMAL: size_parameters.sigma.set_value(fitted_parameters[last_index + 2].value)

                last_index += size_parameters.get_parameters_count()

        if not fit_global_parameters.strain_parameters is None:
            for strain_parameters in fit_global_parameters.strain_parameters:
                if isinstance(strain_parameters, InvariantPAH):
                    strain_parameters.aa.set_value(fitted_parameters[last_index + 1].value)
                    strain_parameters.bb.set_value(fitted_parameters[last_index + 2].value)
                    strain_parameters.e1.set_value(fitted_parameters[last_index + 3].value) # in realtà è E1 dell'invariante PAH
                    strain_parameters.e2.set_value(fitted_parameters[last_index + 4].value) # in realtà è E1 dell'invariante PAH
                    strain_parameters.e3.set_value(fitted_parameters[last_index + 5].value) # in realtà è E1 dell'invariante PAH
                    strain_parameters.e4.set_value(fitted_parameters[last_index + 6].value) # in realtà è E4 dell'invariante PAH
                    strain_parameters.e5.set_value(fitted_parameters[last_index + 7].value) # in realtà è E4 dell'invariante PAH
                    strain_parameters.e6.set_value(fitted_parameters[last_index + 8].value) # in realtà è E4 dell'invariante PAH
                elif isinstance(strain_parameters, KrivoglazWilkensModel):
                    strain_parameters.rho.set_value(fitted_parameters[last_index + 1].value)
                    strain_parameters.Re.set_value(fitted_parameters[last_index + 2].value)
                    strain_parameters.Ae.set_value(fitted_parameters[last_index + 3].value)
                    strain_parameters.Be.set_value(fitted_parameters[last_index + 4].value)
                    strain_parameters.As.set_value(fitted_parameters[last_index + 5].value)
                    strain_parameters.Bs.set_value(fitted_parameters[last_index + 6].value)
                    strain_parameters.mix.set_value(fitted_parameters[last_index + 7].value)
                    strain_parameters.b.set_value(fitted_parameters[last_index + 8].value)
                elif isinstance(strain_parameters, WarrenModel):
                    strain_parameters.average_cell_parameter.set_value(fitted_parameters[last_index + 1].value)

                last_index += strain_parameters.get_parameters_count()

        if fit_global_parameters.has_functions(): fit_global_parameters.evaluate_functions()

        return fit_global_parameters

    def build_fit_global_parameters_out_errors(self, errors):
        fit_global_parameters = self.fit_global_parameters

        last_index = -1

        for index in range(len(fit_global_parameters.fit_initialization.diffraction_patterns)):
            diffraction_pattern = fit_global_parameters.fit_initialization.diffraction_patterns[index]
            diffraction_pattern.wavelength.error = errors[(0 if last_index < 0 else last_index) + index]


            if not diffraction_pattern.is_single_wavelength:
                last_index += 1

                for secondary_wavelength, secondary_wavelength_weigth in zip(diffraction_pattern.secondary_wavelengths,
                                                                             diffraction_pattern.secondary_wavelengths_weights):
                    secondary_wavelength.error = errors[last_index + 1]
                    secondary_wavelength_weigth.error = errors[last_index + 2]
                    last_index += 2

        if last_index < 0: last_index = len(fit_global_parameters.fit_initialization.diffraction_patterns) - 1

        for index in range(len(fit_global_parameters.fit_initialization.crystal_structures)):
            crystal_structure = fit_global_parameters.fit_initialization.crystal_structures[index]

            crystal_structure.a.error = errors[last_index + 1]
            crystal_structure.b.error = errors[last_index + 2]
            crystal_structure.c.error = errors[last_index + 3]
            crystal_structure.alpha.error = errors[last_index + 4]
            crystal_structure.beta.error = errors[last_index + 5]
            crystal_structure.gamma.error = errors[last_index + 6]

            if crystal_structure.use_structure:
                crystal_structure.intensity_scale_factor.error = errors[last_index + 7]
                last_index += 7
            else:
                last_index += 6

            for reflection_index in range(crystal_structure.get_reflections_count()):
                crystal_structure.get_reflection(reflection_index).intensity.error = errors[last_index+reflection_index]

            last_index += crystal_structure.get_reflections_count()

        if not fit_global_parameters.fit_initialization.thermal_polarization_parameters is None:
            for thermal_polarization_parameters in fit_global_parameters.fit_initialization.thermal_polarization_parameters:
                if not thermal_polarization_parameters.debye_waller_factor is None:
                    thermal_polarization_parameters.debye_waller_factor.error = errors[last_index + 1]

                    last_index += thermal_polarization_parameters.get_parameters_count()

        if not fit_global_parameters.background_parameters is None:
            for key in fit_global_parameters.background_parameters.keys():
                background_parameters_list = fit_global_parameters.get_background_parameters(key)

                if not background_parameters_list is None:
                    for background_parameters in background_parameters_list:
                        if key == ChebyshevBackground.__name__:
                            background_parameters.c0.error = errors[last_index + 1]
                            background_parameters.c1.error = errors[last_index + 2]
                            background_parameters.c2.error = errors[last_index + 3]
                            background_parameters.c3.error = errors[last_index + 4]
                            background_parameters.c4.error = errors[last_index + 5]
                            background_parameters.c5.error = errors[last_index + 6]
                            background_parameters.c6.error = errors[last_index + 7]
                            background_parameters.c7.error = errors[last_index + 8]
                            background_parameters.c8.error = errors[last_index + 9]
                            background_parameters.c9.error = errors[last_index + 10]
                        elif key == ExpDecayBackground.__name__:
                            background_parameters.a0.error = errors[last_index + 1]
                            background_parameters.b0.error = errors[last_index + 2]
                            background_parameters.a1.error = errors[last_index + 3]
                            background_parameters.b1.error = errors[last_index + 4]
                            background_parameters.a2.error = errors[last_index + 5]
                            background_parameters.b2.error = errors[last_index + 6]

                        last_index += background_parameters.get_parameters_count()

        if not fit_global_parameters.instrumental_parameters is None:
            for instrumental_parameters in fit_global_parameters.instrumental_parameters:
                instrumental_parameters.U.error = errors[last_index + 1]
                instrumental_parameters.V.error = errors[last_index + 2]
                instrumental_parameters.W.error = errors[last_index + 3]
                instrumental_parameters.a.error = errors[last_index + 4]
                instrumental_parameters.b.error = errors[last_index + 5]
                instrumental_parameters.c.error = errors[last_index + 6]

                last_index += instrumental_parameters.get_parameters_count()

        if not fit_global_parameters.shift_parameters is None:
            for key in fit_global_parameters.shift_parameters.keys():
                shift_parameters_list = fit_global_parameters.get_shift_parameters(key)

                if not shift_parameters_list is None:
                    for shift_parameters in shift_parameters_list:
                        if key == Lab6TanCorrection.__name__:
                            shift_parameters.ax.error = errors[last_index + 1]
                            shift_parameters.bx.error = errors[last_index + 2]
                            shift_parameters.cx.error = errors[last_index + 3]
                            shift_parameters.dx.error = errors[last_index + 4]
                            shift_parameters.ex.error = errors[last_index + 5]
                        elif key == ZeroError.__name__:
                            shift_parameters.shift.error = errors[last_index + 1]
                        elif key == SpecimenDisplacement.__name__:
                            shift_parameters.displacement.error = errors[last_index + 1]

                        last_index += shift_parameters.get_parameters_count()

        if not fit_global_parameters.size_parameters is None:
            for size_parameters in fit_global_parameters.size_parameters:
                size_parameters.mu.error    = errors[last_index + 1]
                if size_parameters.distribution == Distribution.LOGNORMAL: size_parameters.sigma.error = errors[last_index + 2]

                last_index += size_parameters.get_parameters_count()

        if not fit_global_parameters.strain_parameters is None:
            for strain_parameters in fit_global_parameters.strain_parameters:
                if isinstance(strain_parameters, InvariantPAH):
                    strain_parameters.aa.error = errors[last_index + 1]
                    strain_parameters.bb.error = errors[last_index + 2]
                    strain_parameters.e1.error = errors[last_index + 3] # in realtà è E1 dell'invariante PAH
                    strain_parameters.e2.error = errors[last_index + 4] # in realtà è E1 dell'invariante PAH
                    strain_parameters.e3.error = errors[last_index + 5] # in realtà è E1 dell'invariante PAH
                    strain_parameters.e4.error = errors[last_index + 6] # in realtà è E4 dell'invariante PAH
                    strain_parameters.e5.error = errors[last_index + 7] # in realtà è E4 dell'invariante PAH
                    strain_parameters.e6.error = errors[last_index + 8] # in realtà è E4 dell'invariante PAH
                elif isinstance(strain_parameters, KrivoglazWilkensModel):
                    strain_parameters.rho.error = errors[last_index + 1]
                    strain_parameters.Re.error = errors[last_index + 2]
                    strain_parameters.Ae.error = errors[last_index + 3]
                    strain_parameters.Be.error = errors[last_index + 4]
                    strain_parameters.As.error = errors[last_index + 5]
                    strain_parameters.Bs.error = errors[last_index + 6]
                    strain_parameters.mix.error = errors[last_index + 7]
                    strain_parameters.b.error = errors[last_index + 8]
                elif isinstance(strain_parameters, WarrenModel):
                    strain_parameters.average_cell_parameter.error = errors[last_index + 1]

                last_index += strain_parameters.get_parameters_count()

        return fit_global_parameters

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
                                    self.build_fit_global_parameters_out(self.parameters),
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
                                    self.build_fit_global_parameters_out(self.parameters),
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
                                                          self.build_fit_global_parameters_out(self.parameters),
                                                          diffraction_pattern_index=index)
                    else:
                        d = step
                        parameter.value = pk + d
                        parameter.check_value()

                        deriv_i[jj] = fit_function_direct(twotheta_experimental,
                                                          self.build_fit_global_parameters_out(self.parameters),
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
                                                    self.build_fit_global_parameters_out(self.parameters),
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
                                                    self.build_fit_global_parameters_out(self.parameters),
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
                                                    self.build_fit_global_parameters_out(self.parameters),
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


