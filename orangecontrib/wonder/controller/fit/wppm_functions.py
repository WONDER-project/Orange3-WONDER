
from orangecontrib.wonder.controller.fit.init.crystal_structure import CrystalStructure
from orangecontrib.wonder.controller.fit.init.fft_parameters import FFTTypes
from orangecontrib.wonder.controller.fit.init.thermal_polarization_parameters import Beampath, LorentzFormula
from orangecontrib.wonder.controller.fit.instrument.instrumental_parameters import Lab6TanCorrection, ZeroError, SpecimenDisplacement
from orangecontrib.wonder.controller.fit.instrument.background_parameters import ChebyshevBackground, ExpDecayBackground
from orangecontrib.wonder.controller.fit.microstructure.strain import InvariantPAH, WarrenModel, KrivoglazWilkensModel
from orangecontrib.wonder.controller.fit.util.fit_utilities import Utilities, Symmetry
from orangecontrib.wonder.util.general_functions import ChemicalFormulaParser


#########################################################################
# MAIN FUNCTION

#################################################
#
# FIT FUNCTION
#
#################################################

class Distribution:
    DELTA = "delta"
    LOGNORMAL = "lognormal"
    GAMMA = "gamma"
    YORK = "york"

    @classmethod
    def tuple(cls):
        return [cls.DELTA, cls.LOGNORMAL, cls.GAMMA, cls.YORK]

class Normalization:
    NORMALIZE_TO_N = 0
    NORMALIZE_TO_N2 = 1

    @classmethod
    def tuple(cls):
        return ["to N", "to N\u00b2"]

def _wrapper_fit_function_direct(parameters):
	twotheta, fit_global_parameters, diffraction_pattern_index = parameters

	return fit_function_direct(twotheta, fit_global_parameters, diffraction_pattern_index)

def fit_function_direct(twotheta, fit_global_parameters, diffraction_pattern_index = 0):
    wavelength = fit_global_parameters.fit_initialization.diffraction_patterns[diffraction_pattern_index].wavelength.value

    I = fit_function_reciprocal(Utilities.s(0.5*numpy.radians(twotheta), wavelength),
                                fit_global_parameters,
                                diffraction_pattern_index)


    # POLARIZATION FACTOR --------------------------------------------------------------------------------------

    if not fit_global_parameters.fit_initialization.thermal_polarization_parameters is None:
        thermal_polarization_parameters = fit_global_parameters.fit_initialization.thermal_polarization_parameters[0 if len(fit_global_parameters.fit_initialization.thermal_polarization_parameters) == 1 else diffraction_pattern_index]

        if thermal_polarization_parameters.use_polarization_factor:
            twotheta_mono = thermal_polarization_parameters.twotheta_mono

            I *= polarization_factor(numpy.radians(twotheta),
                                     None if twotheta_mono is None else numpy.radians(twotheta_mono),
                                     thermal_polarization_parameters.degree_of_polarization,
                                     thermal_polarization_parameters.beampath)

    # ADD BACKGROUNDS  ---------------------------------------------------------------------------------------------

    if not fit_global_parameters.background_parameters is None:
        for key in fit_global_parameters.background_parameters.keys():
            background_parameters_list = fit_global_parameters.get_background_parameters(key)

            if not background_parameters_list is None:
                background_parameters = background_parameters_list[0 if len(background_parameters_list) == 1 else diffraction_pattern_index]

                if key == ChebyshevBackground.__name__:
                    parameters=[background_parameters.c0.value,
                                background_parameters.c1.value,
                                background_parameters.c2.value,
                                background_parameters.c3.value,
                                background_parameters.c4.value,
                                background_parameters.c5.value,
                                background_parameters.c6.value,
                                background_parameters.c7.value,
                                background_parameters.c8.value,
                                background_parameters.c9.value]

                    add_chebyshev_background(twotheta, I, parameters)

                elif key == ExpDecayBackground.__name__:
                    add_expdecay_background(twotheta,
                                            I,
                                            parameters=[background_parameters.a0.value,
                                                        background_parameters.b0.value,
                                                        background_parameters.a1.value,
                                                        background_parameters.b1.value,
                                                        background_parameters.a2.value,
                                                        background_parameters.b2.value])

    return I

def fit_function_reciprocal(s, fit_global_parameters, diffraction_pattern_index = 0):
    crystal_structure = fit_global_parameters.fit_initialization.crystal_structures[diffraction_pattern_index]

    if CrystalStructure.is_cube(crystal_structure.symmetry):

        # CONSTRUCTION OF EACH SEPARATE PEAK ---------------------------------------------------------------------------

        separated_peaks_functions = []

        for reflection_index in range(crystal_structure.get_reflections_count()):
            sanalitycal, Ianalitycal = create_one_peak(reflection_index, fit_global_parameters, diffraction_pattern_index)

            separated_peaks_functions.append([sanalitycal, Ianalitycal])

        # INTERPOLATION ONTO ORIGINAL S VALUES -------------------------------------------------------------------------

        I = Utilities.merge_functions(separated_peaks_functions, s)

        # ADD SAXS

        if not fit_global_parameters.size_parameters is None:
            size_parameters = fit_global_parameters.size_parameters[0 if len(fit_global_parameters.size_parameters) == 1 else diffraction_pattern_index]

            if size_parameters.distribution == Distribution.DELTA and size_parameters.add_saxs:
                if not crystal_structure.use_structure: NotImplementedError("SAXS is available when the structural model is active")

                I += saxs(s,
                          size_parameters.mu.value,
                          crystal_structure.a.value,
                          crystal_structure.formula,
                          crystal_structure.symmetry,
                          size_parameters.normalize_to)

        # ADD DEBYE-WALLER FACTOR --------------------------------------------------------------------------------------

        if not fit_global_parameters.fit_initialization.thermal_polarization_parameters is None:
            thermal_polarization_parameters = fit_global_parameters.fit_initialization.thermal_polarization_parameters[0 if len(fit_global_parameters.fit_initialization.thermal_polarization_parameters) == 1 else diffraction_pattern_index]

            if not thermal_polarization_parameters.debye_waller_factor is None:
                I *= debye_waller(s, thermal_polarization_parameters.debye_waller_factor.value)

        diffraction_pattern = fit_global_parameters.fit_initialization.diffraction_patterns[diffraction_pattern_index]

        if not diffraction_pattern.is_single_wavelength:
            principal_wavelength = diffraction_pattern.wavelength
            I_scaled = I*diffraction_pattern.get_principal_wavelenght_weight()

            for secondary_wavelength, secondary_wavelength_weigth in zip(diffraction_pattern.secondary_wavelengths,
                                                                         diffraction_pattern.secondary_wavelengths_weights):
                s_secondary = s * secondary_wavelength.value/principal_wavelength.value
                I_scaled += Utilities.merge_functions([[s_secondary, I*secondary_wavelength_weigth.value]], s)

            I = I_scaled

        return I
    else:
        raise NotImplementedError("Only Cubic structures are supported by fit")


#################################################
# FOURIER FUNCTIONS
#################################################


class FourierTranformFactory:
    @classmethod
    def get_fourier_transform(cls, type=FFTTypes.REAL_ONLY):
        if type == FFTTypes.REAL_ONLY:
            return FourierTransformRealOnly
        elif type == FFTTypes.FULL:
            return FourierTransformFull
        else:
            raise ValueError("Type not recognized")

class FourierTransform:
    @classmethod
    def fft(cls, f, n_steps, dL):
        raise NotImplementedError()

    @classmethod
    def get_empty_fft(cls, n_steps, dL):
        s = numpy.fft.fftfreq(n_steps, dL)
        s = numpy.fft.fftshift(s)

        I = numpy.zeros(len(s))
        I[int(len(s)/2)] = 1.0

        return s, I


class FourierTransformRealOnly(FourierTransform):

    @classmethod
    def _real_absolute_fourier(cls, y):
        return numpy.fft.fftshift(numpy.abs(numpy.real(numpy.fft.fft(y))))

    @classmethod
    def _fft_normalized(cls, y_fft, n_steps, dL):
        s = numpy.fft.fftfreq(n_steps, dL)
        s = numpy.fft.fftshift(s)

        integral = numpy.trapz(y_fft, s)

        return s, y_fft / integral

    @classmethod
    def fft(cls, f, n_steps, dL):
        return cls._fft_normalized(cls._real_absolute_fourier(f), n_steps, dL)

from scipy.integrate import simps

class FourierTransformFull(FourierTransform):
    @classmethod
    def _full_fourier(cls, y):
        return numpy.fft.fftshift(numpy.fft.fft(y))

    @classmethod
    def _fft_shifted(cls, y_fft, n_steps, dL):
        s = numpy.fft.fftfreq(n_steps, dL)
        s = numpy.fft.fftshift(s)

        y_fft -= y_fft[0]

        return s, y_fft

    @classmethod
    def _fft_real(cls, f, n_steps, dL):
        return cls._fft_shifted(numpy.real(cls._full_fourier(f)), n_steps, dL)

    @classmethod
    def _fft_imag(cls, f, n_steps, dL):
        return cls._fft_shifted(numpy.imag(cls._full_fourier(f)), n_steps, dL)

    @classmethod
    def _normalize(cls, s, i):
        return s, i/simps(i, s)

    @classmethod
    def fft(cls, f, n_steps, dL):
        sr, fft_real = cls._fft_real(numpy.real(f), n_steps, dL)
        si, fft_imag = cls._fft_imag(numpy.imag(f), n_steps, dL)

        return cls._normalize(sr, fft_real - fft_imag)

#################################################
# CALCOLO DI UN SINGOLO PICCO
#################################################

def create_one_peak(reflection_index, fit_global_parameters, diffraction_pattern_index=0):
    fft_type = fit_global_parameters.fit_initialization.fft_parameters.fft_type
    fit_space_parameters = fit_global_parameters.space_parameters()
    crystal_structure = fit_global_parameters.fit_initialization.crystal_structures[diffraction_pattern_index]
    reflection = crystal_structure.get_reflection(reflection_index)

    wavelength = fit_global_parameters.fit_initialization.diffraction_patterns[diffraction_pattern_index].wavelength.value
    lattice_parameter = crystal_structure.a.value

    fourier_amplitudes = None

    # INSTRUMENTAL PROFILE ---------------------------------------------------------------------------------------------

    if not fit_global_parameters.instrumental_parameters is None:
        instrumental_parameters = fit_global_parameters.instrumental_parameters[0 if len(fit_global_parameters.instrumental_parameters) == 1 else diffraction_pattern_index]
            
        if fourier_amplitudes is None:
            fourier_amplitudes = instrumental_function(fit_space_parameters.L,
                                                       reflection.h,
                                                       reflection.k,
                                                       reflection.l,
                                                       lattice_parameter,
                                                       wavelength,
                                                       instrumental_parameters.U.value,
                                                       instrumental_parameters.V.value,
                                                       instrumental_parameters.W.value,
                                                       instrumental_parameters.a.value,
                                                       instrumental_parameters.b.value,
                                                       instrumental_parameters.c.value)
        else:
            fourier_amplitudes *= instrumental_function(fit_space_parameters.L,
                                                        reflection.h,
                                                        reflection.k,
                                                        reflection.l,
                                                        lattice_parameter,
                                                        wavelength,
                                                        instrumental_parameters.U.value,
                                                        instrumental_parameters.V.value,
                                                        instrumental_parameters.W.value,
                                                        instrumental_parameters.a.value,
                                                        instrumental_parameters.b.value,
                                                        instrumental_parameters.c.value)

    # SIZE -------------------------------------------------------------------------------------------------------------

    if not fit_global_parameters.size_parameters is None:
        size_parameters = fit_global_parameters.size_parameters[0 if len(fit_global_parameters.size_parameters) == 1 else diffraction_pattern_index]

        if size_parameters.distribution == Distribution.LOGNORMAL:
            if fourier_amplitudes is None:
                fourier_amplitudes = size_function_lognormal(fit_space_parameters.L,
                                                             size_parameters.sigma.value,
                                                             size_parameters.mu.value)
            else:
                fourier_amplitudes *= size_function_lognormal(fit_space_parameters.L,
                                                              size_parameters.sigma.value,
                                                              size_parameters.mu.value)
        elif size_parameters.distribution == Distribution.DELTA:
            if fourier_amplitudes is None:
                fourier_amplitudes = size_function_delta(fit_space_parameters.L,
                                                         size_parameters.mu.value)
            else:
                fourier_amplitudes *= size_function_delta(fit_space_parameters.L,
                                                          size_parameters.mu.value)

    # STRAIN -----------------------------------------------------------------------------------------------------------

    if not fit_global_parameters.strain_parameters is None:
        strain_parameters = fit_global_parameters.strain_parameters[0 if len(fit_global_parameters.strain_parameters) == 1 else diffraction_pattern_index]

        if isinstance(strain_parameters, InvariantPAH): # INVARIANT PAH
            if fourier_amplitudes is None:
                fourier_amplitudes = strain_invariant_function_pah(fit_space_parameters.L,
                                                                   reflection.h,
                                                                   reflection.k,
                                                                   reflection.l,
                                                                   lattice_parameter,
                                                                   strain_parameters.aa.value,
                                                                   strain_parameters.bb.value,
                                                                   strain_parameters.get_invariant(reflection.h,
                                                                                                   reflection.k,
                                                                                                   reflection.l))
            else:
                fourier_amplitudes *= strain_invariant_function_pah(fit_space_parameters.L,
                                                                    reflection.h,
                                                                    reflection.k,
                                                                    reflection.l,
                                                                    lattice_parameter,
                                                                    strain_parameters.aa.value,
                                                                    strain_parameters.bb.value,
                                                                    strain_parameters.get_invariant(reflection.h,
                                                                                                    reflection.k,
                                                                                                    reflection.l))

        elif isinstance(strain_parameters, KrivoglazWilkensModel): # KRIVOGLAZ-WILKENS
            if fourier_amplitudes is None:
                fourier_amplitudes = strain_krivoglaz_wilkens(fit_space_parameters.L,
                                                              reflection.h,
                                                              reflection.k,
                                                              reflection.l,
                                                              lattice_parameter,
                                                              strain_parameters.rho.value,
                                                              strain_parameters.Re.value,
                                                              strain_parameters.Ae.value,
                                                              strain_parameters.Be.value,
                                                              strain_parameters.As.value,
                                                              strain_parameters.Bs.value,
                                                              strain_parameters.mix.value,
                                                              strain_parameters.b.value)

            else:
                fourier_amplitudes *= strain_krivoglaz_wilkens(fit_space_parameters.L,
                                                               reflection.h,
                                                               reflection.k,
                                                               reflection.l,
                                                               lattice_parameter,
                                                               strain_parameters.rho.value,
                                                               strain_parameters.Re.value,
                                                               strain_parameters.Ae.value,
                                                               strain_parameters.Be.value,
                                                               strain_parameters.As.value,
                                                               strain_parameters.Bs.value,
                                                               strain_parameters.mix.value,
                                                               strain_parameters.b.value)

        elif isinstance(strain_parameters, WarrenModel): # WARREN
            fourier_amplitudes_re, fourier_amplitudes_im = strain_warren_function(fit_space_parameters.L,
                                                                                  reflection.h,
                                                                                  reflection.k,
                                                                                  reflection.l,
                                                                                  lattice_parameter,
                                                                                  strain_parameters.average_cell_parameter.value)
            if fft_type == FFTTypes.FULL:
                if fourier_amplitudes is None:
                    fourier_amplitudes = fourier_amplitudes_re + 1j*fourier_amplitudes_im
                else:
                    fourier_amplitudes = (fourier_amplitudes*fourier_amplitudes_re) + 1j*(fourier_amplitudes*fourier_amplitudes_im)
            elif fft_type == FFTTypes.REAL_ONLY:
                if fourier_amplitudes is None:
                    fourier_amplitudes = fourier_amplitudes_re
                else:
                    fourier_amplitudes *= fourier_amplitudes_re

    # FFT -----------------------------------------------------------------------------------------------------------
    if not fourier_amplitudes is None:
        s, I = FourierTranformFactory.get_fourier_transform(fft_type).fft(fourier_amplitudes,
                                                                          n_steps=fit_global_parameters.fit_initialization.fft_parameters.n_step,
                                                                          dL=fit_space_parameters.dL)
    else:
        s, I = FourierTransform.get_empty_fft(n_steps=fit_global_parameters.fit_initialization.fft_parameters.n_step,
                                              dL=fit_space_parameters.dL)

    s_hkl = Utilities.s_hkl(lattice_parameter, reflection.h, reflection.k, reflection.l)

    s += s_hkl

    # INTENSITY MODULATION: STRUCTURAL MODEL YES/NO --------------------------------------------------------------------

    if crystal_structure.use_structure:
        I *= crystal_structure.intensity_scale_factor.value
        I *= multiplicity_cubic(reflection.h, reflection.k, reflection.l)
        I *= squared_modulus_structure_factor(s_hkl,
                                              crystal_structure.formula,
                                              reflection.h,
                                              reflection.k,
                                              reflection.l,
                                              crystal_structure.symmetry)
    else:
        I *= reflection.intensity.value

    #TODO: AGGIUNGERE GESTIONE TDS con strutture dati + widget ad hoc

    # PEAK SHIFTS  -----------------------------------------------------------------------------------------------------

    if not fit_global_parameters.shift_parameters is None:
        theta = Utilities.theta(s, wavelength)

        for key in fit_global_parameters.shift_parameters.keys():
            shift_parameters = fit_global_parameters.get_shift_parameters(key)[0 if len(fit_global_parameters.get_shift_parameters(key)) == 1 else diffraction_pattern_index]

            if not shift_parameters is None:
                if key == Lab6TanCorrection.__name__:
                    s += lab6_tan_correction(theta, wavelength,
                                             shift_parameters.ax.value,
                                             shift_parameters.bx.value,
                                             shift_parameters.cx.value,
                                             shift_parameters.dx.value,
                                             shift_parameters.ex.value)
                elif key == ZeroError.__name__:
                    s += Utilities.s(shift_parameters.shift.value/2, wavelength)
                elif key == SpecimenDisplacement.__name__:
                    s += specimen_displacement(theta, wavelength, shift_parameters.goniometer_radius, shift_parameters.displacement.value)

    # LORENTZ FACTOR --------------------------------------------------------------------------------------

    if not fit_global_parameters.fit_initialization.thermal_polarization_parameters is None:
        thermal_polarization_parameters = fit_global_parameters.fit_initialization.thermal_polarization_parameters[0 if len(fit_global_parameters.fit_initialization.thermal_polarization_parameters) == 1 else diffraction_pattern_index]

        if thermal_polarization_parameters.use_lorentz_factor:
            if thermal_polarization_parameters.lorentz_formula == LorentzFormula.Shkl_Shkl:
                I *= lorentz_factor_simplified_normalized(s_hkl, wavelength)
            elif thermal_polarization_parameters.lorentz_formula == LorentzFormula.S_Shkl:
                I *= lorentz_factor_normalized(s, s_hkl, wavelength)

    return s, I


######################################################################
# FUNZIONI WPPM
######################################################################

import numpy
from scipy.special import erfc
import os

######################################################################
# THERMAL AND POLARIZATION
######################################################################

def debye_waller(s, B):
    return numpy.exp(-0.5*B*(s**2)) # it's the exp(-2M) = exp(-Bs^2/2)

def lorentz_factor(s, s_hkl):
    return 1/(s*s_hkl)

def lorentz_factor_normalized(s, s_hkl, wavelength):
    return lorentz_factor(s, s_hkl)/numpy.sqrt(1 - (s*wavelength/2)**2)

def lorentz_factor_simplified(s_hkl):
    return 1/(s_hkl**2)

def lorentz_factor_simplified_normalized(s_hkl, wavelength):
    return lorentz_factor_simplified(s_hkl)/numpy.sqrt(1 - (s_hkl*wavelength/2)**2)

def polarization_factor(twotheta, twotheta_mono, degree_of_polarization, beampath):
    Q = degree_of_polarization

    if twotheta_mono is None or twotheta_mono == 0.0:
        return ((1+Q) + (1-Q)*(numpy.cos(twotheta)**2))/2
    else:
        if beampath == Beampath.PRIMARY:
            return ((1+Q) + (1-Q)*(numpy.cos(twotheta_mono)**2)*(numpy.cos(twotheta)**2))/(1 + (numpy.cos(twotheta_mono)**2))
        elif beampath == Beampath.SECONDARY:
            return ((1+Q) + (1-Q)*(numpy.cos(twotheta_mono)**2)*(numpy.cos(twotheta)**2))/2

######################################################################
# SIZE
######################################################################

def size_function_delta(L, D):
    LfracD = L/D

    return 1 - 1.5*LfracD + 0.5*LfracD**3

def size_function_lognormal(L, sigma, mu):
    modL = numpy.abs(L)
    lnModL = numpy.log(modL)
    sqrt2 = numpy.sqrt(2)

    a = 0.5*erfc((lnModL - mu -3*sigma**2)/(sigma*sqrt2))
    b = -0.75*modL*erfc((lnModL - mu -2*sigma**2)/(sigma*sqrt2))\
                *numpy.exp(-mu - 2.5*sigma**2)
    c = 0.25*(L**3)*erfc((lnModL - mu)/(sigma*sqrt2)) \
                *numpy.exp(-3*mu - 4.5*sigma**2)

    return  a + b + c

def lognormal_distribution(mu, sigma, x):
        return numpy.exp(-0.5*((numpy.log(x) - mu)/(sigma))**2)/(x*sigma*numpy.sqrt(2*numpy.pi))

######################################################################
# STRAIN
######################################################################

# INVARIANT PAH --------------------------------

def strain_invariant_function_pah(L, h, k, l, lattice_parameter, a, b, C_hkl):
    s_hkl = Utilities.s_hkl(lattice_parameter, h, k, l)

    return numpy.exp(-((2*numpy.pi**2)/((s_hkl**2)*(lattice_parameter**4))) * C_hkl * (a*L + b*(L**2)))

def displacement_invariant_pah(L, h, k, l, a, b, C_hkl):
    return numpy.sqrt((C_hkl*(a*L + b*(L**2)))/((h**2+k**2+l**2)**2))


# Krivoglaz-Wilkens  --------------------------------

from scipy import integrate
from numpy import pi, log, sqrt, arcsin, sin, cos # TO SHORTEN FORMULAS

def clausen_integral_inner_function(t):
    return log(2*sin(t/2))

def clausen_integral(x=0.0):
    _v_integrate_quad = numpy.vectorize(integrate.quad)

    return -1*(_v_integrate_quad(lambda t: clausen_integral_inner_function(t), 0.0, x)[0])

def f_star(eta, use_simplified_calculation=True):
    result = numpy.zeros(len(eta))
    eta = numpy.array(eta)

    cursor_1 = numpy.where(eta >= 1)
    cursor_2 = numpy.where(eta < 1)

    eta1 = eta[cursor_1]
    eta2 = eta[cursor_2]

    result[cursor_1] = (256/(45*pi*eta1)) - ((11/24) + (log(2) - log(eta1))/4)/(eta1**2)

    if use_simplified_calculation:
        result[cursor_2] = (7/4) - log(2) - log(eta2) + ((eta2**2)/6) - (32*(eta2**3))/(225*pi)
    else:
        result[cursor_2] = (256/(45*pi*eta2))
        result[cursor_2] += ((eta2**2)/6) - log(2) - log(eta2)
        result[cursor_2] += -eta2*sqrt(1-(eta2**2))*(769 + 4*(eta2**2)*(20.5 + (eta2**2)))/(180*pi*(eta2**2))
        result[cursor_2] += -((45 - 180*eta2**2)*clausen_integral(2*arcsin(eta2)) +
                             (15*arcsin(eta2)*(11 + 4*(eta2**2)*(10.5 + (eta2**2)) + (6 - 24*(eta2**2))*(log(2) + log(eta2)))))/(180*pi*(eta2**2))

    return result


def C_hkl_krivoglaz_wilkens(h, k, l, Ae, Be, As, Bs, mix):
    H = Utilities.Hinvariant(h, k, l)

    C_hkl_edge  = Ae + Be*H**2
    C_hkl_screw = As + Bs*H**2

    return mix*C_hkl_edge + (1-mix)*C_hkl_screw

def strain_krivoglaz_wilkens(L, h, k, l, lattice_parameter, rho, Re, Ae, Be, As, Bs, mix, b):
    s_hkl = Utilities.s_hkl(lattice_parameter, h, k, l)
    C_hkl = C_hkl_krivoglaz_wilkens(h, k, l, Ae, Be, As, Bs, mix)

    return numpy.exp(-(0.5*pi*(s_hkl**2)*(b**2)*rho*C_hkl*(L**2)*f_star(L/Re)))

def displacement_krivoglaz_wilkens(L, h, k, l, rho, Re, Ae, Be, As, Bs, mix, b):
    C_hkl = C_hkl_krivoglaz_wilkens(h, k, l, Ae, Be, As, Bs, mix)

    return numpy.sqrt(rho*C_hkl*(b**2)*(L**2)*f_star(L/Re)/(4*numpy.pi))


# WARREN MODEL --------------------------------

def load_warren_files():
    delta_l_dict = {}
    delta_l2_dict = {}

    path = os.path.join(os.path.dirname(__file__), "data")
    path = os.path.join(path, "delta_l_files")

    filenames = os.listdir(path)

    for filename in filenames:
        if filename.endswith('FTinfo'):
            hkl = filename[0:3]
            name =  os.path.join(path, filename)
            data = numpy.loadtxt(name)
            L = data[:,0]

            delta_l_dict[hkl] = [L, data[:, 1]] # deltal_fun
            delta_l2_dict[hkl] = [L, data[:,2]] # deltal2_fun

    return delta_l_dict, delta_l2_dict

delta_l_dict, delta_l2_dict = load_warren_files()

def modify_delta_l(l, delta_l, lattice_parameter, average_lattice_parameter):
    return delta_l - (average_lattice_parameter/lattice_parameter -1)*l

def modify_delta_l2(l, delta_l, delta_l2, lattice_parameter, average_lattice_parameter):
    return delta_l2 - 2*delta_l*(average_lattice_parameter/lattice_parameter -1)*l \
               + ((average_lattice_parameter/lattice_parameter -1)*l)**2

def re_warren_strain(s_hkl, delta_l2):
    return numpy.exp(-0.5*((s_hkl*2*numpy.pi)**2)*delta_l2)

def im_warren_strain(s_hkl, delta_l):
    return (s_hkl*2*numpy.pi)*delta_l

def strain_warren_function(L, h, k, l, lattice_parameter, average_lattice_parameter):
    hkl = str(h) + str(k) + str(l)
    
    if hkl not in delta_l_dict.keys():
        return numpy.ones(len(L)), numpy.zeros(len(L))
    
    delta_l_entry = delta_l_dict[hkl]
    delta_l2_entry = delta_l2_dict[hkl]

    l_local  = delta_l_entry[0]
    delta_l  = delta_l_entry[1]
    delta_l2 = delta_l2_entry[1]

    new_delta_l  = modify_delta_l(l_local, delta_l, lattice_parameter, average_lattice_parameter)
    new_delta_l2 = modify_delta_l2(l_local, delta_l, delta_l2, lattice_parameter, average_lattice_parameter)

    new_delta_l  = numpy.interp(L, l_local, new_delta_l)
    new_delta_l2 = numpy.interp(L, l_local, new_delta_l2)

    s_hkl = Utilities.s_hkl(average_lattice_parameter, h, k, l)

    return re_warren_strain(s_hkl, new_delta_l2), im_warren_strain(s_hkl, new_delta_l)

######################################################################
# STRUCTURE
######################################################################

def load_atomic_scattering_factor_coefficients():
    atomic_scattering_factor_coefficients = {}

    path = os.path.join(os.path.dirname(__file__), "data")
    file_name = os.path.join(path, "atomic_scattering_factor_coefficients.dat")

    file = open(file_name, "r")
    rows = file.readlines()
    for row in rows:
        tokens = numpy.array(row.strip().split(sep=" "))
        tokens = tokens[numpy.where(tokens != '')]

        if not tokens is None and len(tokens) == 10:
            element = tokens[0].strip()

            coefficients =[[[float(tokens[1].strip()), float(tokens[2].strip())],
                            [float(tokens[3].strip()), float(tokens[4].strip())],
                            [float(tokens[5].strip()), float(tokens[6].strip())],
                            [float(tokens[7].strip()), float(tokens[8].strip())]],
                           float(tokens[9].strip())]

            atomic_scattering_factor_coefficients[element] = coefficients

    file.close()

    return atomic_scattering_factor_coefficients

atomic_scattering_factor_coefficients = load_atomic_scattering_factor_coefficients()

def multiplicity_cubic(h, k, l):
    p = [6, 12, 24, 8, 24, 48]
    hkl = sorted([h, k, l], reverse=True)
    h, k, l = hkl[0], hkl[1], hkl[2]

    if (h != 0 and k == 0 and l ==0):
        return p[0]
    elif (h == k and l == 0):
        return p[1]
    elif ((h == k and l != h and l != k) or (k==l and h != k and h != l)):
        return p[2]
    elif (h == k and k == l):
        return p[3]
    elif (h != k and l == 0):
        return p[4]
    elif (h != k and k != l and h!=l):
        return p[5]

def atomic_scattering_factor(s, element):
    coefficients = atomic_scattering_factor_coefficients[str(element).upper()]
    ab = coefficients[0]
    c = coefficients[1]

    f_s = numpy.zeros(numpy.size(s))
    s_angstrom = s/10 # to angstrom-1
    for index in range(0, len(ab)):
        a = ab[index][0]
        b = ab[index][1]

        f_s += a*numpy.exp(-b*((0.5*s_angstrom)**2))

    # TODO: AGGIUNGERE DFi e DFii

    return f_s + c

def structure_factor(s, formula, h, k, l, symmetry=Symmetry.FCC):
    elements = ChemicalFormulaParser.parse_formula(formula)

    if len(elements) == 1: #TODO: this is valid for Cubic materials only
        if symmetry == Symmetry.FCC:
            return 4*atomic_scattering_factor(s, elements[0]._element)
        elif symmetry == Symmetry.BCC:
            return 2*atomic_scattering_factor(s, elements[0]._element)
        elif symmetry == Symmetry.SIMPLE_CUBIC:
            return atomic_scattering_factor(s, elements[0]._element)
    else:
        total_weight = 0.0
        total_structure_factor = 0.0
        cell = get_cell(symmetry)

        for element in elements:
            weight = element._n_atoms

            element_structure_factor = 0.0

            for atom in cell:
                element_structure_factor += atomic_scattering_factor(s, element._element) * numpy.exp(2 * numpy.pi * 1j * (numpy.dot(atom, [h, k ,l])))
            element_structure_factor *= weight

            total_weight += weight
            total_structure_factor += element_structure_factor

        total_structure_factor /= total_weight

        return total_structure_factor

def get_cell(symmetry=Symmetry.FCC):
    if symmetry == Symmetry.SIMPLE_CUBIC:
        return [[0, 0, 0]]
    elif symmetry == Symmetry.BCC:
        return [[0, 0, 0], [0.5, 0.5, 0.5]]
    elif symmetry == Symmetry.FCC:
        return [[0, 0, 0], [0.5, 0.5, 0], [0.5, 0, 0.5], [0, 0.5, 0.5]]

def squared_modulus_structure_factor(s, formula, h, k, l, symmetry=Symmetry.FCC):
    return numpy.absolute(structure_factor(s, formula, h, k, l, symmetry))**2

def saxs(s, D, a0, formula, symmetry, normalize_to):
    f = atomic_scattering_factor(s, ChemicalFormulaParser.parse_formula(formula)[0]._element)
    Z = 4 if symmetry == Symmetry.FCC else 2 if symmetry == Symmetry.BCC else 1
    N = (Z*pi*(D**3))/(6*(a0**3))

    if normalize_to == Normalization.NORMALIZE_TO_N:
        normalization = N*(numpy.absolute(f)**2)
    elif normalize_to == Normalization.NORMALIZE_TO_N2:
        normalization = (N*numpy.absolute(f))**2

    x = pi*D*s

    saxs = normalization*(3*(sin(x)-x*cos(x))/(x**3))**2
    saxs[numpy.where(numpy.isnan(saxs))] = 1.0

    return saxs

######################################################################
# INSTRUMENTAL
######################################################################

def caglioti_eta(a, b, c, theta): # input: radians
    eta = a + b * theta + c * theta**2

    if isinstance(eta, numpy.float64):
        eta = 0 if eta < 0 else 1 if eta > 1 else eta
    else:
        eta[numpy.where(eta < 0)] = 0
        eta[numpy.where(eta > 1)] = 1

    return eta

def caglioti_fwhm(U, V, W, theta): # input: radians, output: degrees
    return numpy.sqrt(W +  V * numpy.tan(theta) + U * (numpy.tan(theta)**2))

def delta_two_theta_lab6(ax, bx, cx, dx, ex, theta): # input: radians
    tan_theta = numpy.tan(theta)

    delta_twotheta = numpy.radians(ax*(1/tan_theta) + bx + cx*tan_theta + dx*tan_theta**2 + ex*tan_theta**3)
    delta_twotheta[numpy.where(numpy.isnan(delta_twotheta))] = 0.0
    delta_twotheta[numpy.where(numpy.isinf(delta_twotheta))] = 0.0

    return delta_twotheta

def delta_two_theta_specimen_displacement(goniometer_radius, displacement, theta):
    return -(2*displacement/goniometer_radius)*cos(theta)


def lab6_tan_correction(theta, wavelength, ax, bx, cx, dx, ex):
    delta_twotheta = delta_two_theta_lab6(ax, bx, cx, dx, ex, theta)

    return delta_twotheta*numpy.cos(theta)/wavelength

def specimen_displacement(theta, wavelength, goniometer_radius, displacement): # input radians
    delta_twotheta = delta_two_theta_specimen_displacement(goniometer_radius, displacement, theta)

    return delta_twotheta*numpy.cos(theta)/wavelength

def instrumental_function (L, h, k, l, lattice_parameter, wavelength, U, V, W, a, b, c):
    theta = Utilities.theta_hkl(lattice_parameter, h, k, l, wavelength)
    theta_deg = numpy.degrees(theta)

    eta = caglioti_eta(a, b, c, theta_deg)

    k = eta * numpy.sqrt(numpy.pi*numpy.log(2))
    k /= k + (1-eta)

    sigma = numpy.radians(caglioti_fwhm(U, V, W, theta))*0.5*(numpy.cos(theta)/wavelength)
    exp1 = numpy.pi * sigma * L

    return k*numpy.exp(-2.0*exp1) + (1-k)*numpy.exp(-(exp1**2)/numpy.log(2))

######################################################################
# BACKGROUND
######################################################################

def add_chebyshev_background(x, I, parameters=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0]):
    degree = len(parameters)
    bkg = numpy.zeros(len(x))
    T = numpy.zeros((len(x), degree))

    for j in range(degree):
        if j==0:
            T[:, j] = 1
        elif j==1:
            T[:, j] = x
        else:
            T[:, j] = 2*x*T[:, j-1] - T[:, j-2]

        bkg += parameters[j]*T[:, j]

    I += bkg

def add_polynomial_background(x, I, parameters=[0, 0, 0, 0, 0, 0]):
    degree = len(parameters)
    bkg = numpy.zeros(len(x))

    for j in range(0, degree):
        I += parameters[j]*numpy.pow(x, j)

def add_polynomial_N_background(x, I, parameters=[0, 0, 0, 0, 0, 0]):
    degree = len(parameters)
    bkg = numpy.zeros(len(x))

    for j in range(0, int(degree/2 - 1)):
        a_i = parameters[2*j]
        b_i = parameters[2*j+1]

        bkg += a_i*numpy.pow(x, b_i)

    I += bkg

def add_polynomial_0N_background(x, I, parameters=[0, 0, 0, 0, 0, 0]):
    degree = len(parameters)
    bkg = numpy.zeros(len(x))
    x0 = parameters[0]

    for j in range(0, int(degree/2 - 1)):
        a_i = parameters[1 + 2*j]
        b_i = parameters[1 + 2*j+1]

        bkg += a_i*numpy.pow((x-x0), b_i)

    I += bkg

def add_expdecay_background(x, I, parameters=[0, 0, 0, 0, 0, 0]):
    degree = len(parameters)
    bkg = numpy.zeros(len(x))

    for j in range(0, int(degree/2 - 1)):
        a_i = parameters[2*j]
        b_i = parameters[2*j+1]

        bkg += a_i*numpy.exp(-numpy.abs(x)*b_i)

    I += bkg

def add_expdecay_0_background(x, I, parameters=[0, 0, 0, 0, 0, 0]):
    degree = len(parameters)
    bkg = numpy.zeros(len(x))
    x0 = parameters[0]

    for j in range(0, int(degree/2 - 1)):
        a_i = parameters[1 + 2*j]
        b_i = parameters[1 + 2*j+1]

        bkg += a_i*numpy.exp(-numpy.abs(x-x0)*b_i)

    I += bkg
