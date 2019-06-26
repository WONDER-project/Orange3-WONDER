import operator
import itertools
import numpy

class Symmetry:
    FCC = "fcc"
    BCC = "bcc"
    SIMPLE_CUBIC = "sc"

    @classmethod
    def tuple(cls):
        return [cls.SIMPLE_CUBIC, cls.BCC, cls.FCC]

class Utilities:

    @classmethod
    def Hinvariant(cls, h, k, l):
        numerator = (h * h * k * k + k * k * l * l + l * l * h * h)
        denominator = (h**2 + k**2 + l**2)**2
        return numerator / denominator

    @classmethod
    def s_hkl(cls, a, h, k, l):
        return numpy.sqrt(h**2 + k**2 + l**2) / a

    @classmethod
    def theta(cls, s, wavelength):
        return numpy.arcsin (s * wavelength / 2)

    @classmethod
    def s(cls, theta, wavelength):
        return 2*numpy.sin(theta)/wavelength

    @classmethod
    def theta_hkl (cls, a, h, k, l , wavelength):
        return cls.theta(cls.s_hkl(a, h, k, l), wavelength)

    @classmethod
    def isolate_peak(cls, s, I, smin, smax):
        data = []
        N = numpy.size(s)
        for i in numpy.arange(0, N):
            if s[i] > smin and s[i] < smax:
                data.append([s[i], I[i]])
        output = numpy.asarray(data)
        return output[:, 0], output[:, 1]

    @classmethod
    def merge_functions(cls, list_of_pairs, s):
        # x step must be the same for all functions
        I = numpy.zeros(len(s))

        for pairs in list_of_pairs:
            I += numpy.interp(s, pairs[0], pairs[1])

        return I




def is_even(a):
    return a % 2 == 0

def is_odd(a):
    return a % 2 == 1

def is_fcc(h, k, l):
    if (is_even(h) and is_even(k) and is_even(l)):
        return True
    elif (is_odd(h) and is_odd(k) and is_odd(l)):
        return True
    else:
        return False

def is_bcc(h, k, l):
    if is_even(h+k+l):
        return True
    else:
        return False

def list_of_s_bragg(lattice_param, symmetry=Symmetry.FCC, n_peaks=numpy.inf, s_max=numpy.inf):

    s_list = []
    s_hkl_max = 0.0
    possible_indexes = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    for h, k, l in itertools.combinations_with_replacement(possible_indexes, 3):
        if (symmetry == Symmetry.FCC and is_fcc(h, k, l)) or \
           (symmetry == Symmetry.BCC and is_bcc(h, k, l)) or \
            symmetry == Symmetry.SIMPLE_CUBIC:
            s_hkl = Utilities.s_hkl(lattice_param, h, k, l)

            s_hkl_max = s_hkl if s_hkl > s_hkl_max else s_hkl_max

            s_list.append([[h, k, l], s_hkl])

    s_list = sorted(s_list, key=operator.itemgetter(1))

    if not len(s_list) <= n_peaks:
        s_list = s_list[:n_peaks+1]

    if not s_max > s_hkl_max:
        last_index = 0
        for item in s_list:
            if item[1] > s_max: break
            last_index +=1

        if last_index == 0:
            s_list = []
        else:
            s_list = s_list[:(last_index)]

    if not s_list == []:
        for temp_list in s_list:
            temp_list[0] = sorted(temp_list[0], reverse=True)

        s_list.pop(0)

    return s_list

if __name__=="__main__":
    list = list_of_s_bragg(0.2873, Symmetry.FCC)

    for item in list:
        print(item)
