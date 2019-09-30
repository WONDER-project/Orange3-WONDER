import numpy

from orangecontrib.wonder.controller.fit.wppm_functions import WulffCubeFace, WulffSolidDataRow, \
    wulff_solids_data_triangular, wulff_solids_data_hexagonal, \
    lognormal_distribution

def __point_in_between(y1, y2, x):
    return y1 + x*(y2 - y1)

def __get_Hj_coefficients(h, k, l, truncation, face=WulffCubeFace.TRIANGULAR): # N.B. L, truncation >= 0!
    divisor = numpy.gcd.reduce([h, k, l])

    truncation_on_file = 100*truncation

    if truncation_on_file.is_integer():
        if face == WulffCubeFace.TRIANGULAR:
            wulff_solid_data_row = wulff_solids_data_triangular[WulffSolidDataRow.get_key(h/divisor, k/divisor, l/divisor, truncation_on_file)]
        else:
            wulff_solid_data_row = wulff_solids_data_hexagonal[WulffSolidDataRow.get_key(h/divisor, k/divisor, l/divisor, truncation_on_file)]

        return wulff_solid_data_row
    else:
        x = truncation % 1 # decimal part

        if face == WulffCubeFace.TRIANGULAR:
            coefficients_bottom = wulff_solids_data_triangular[WulffSolidDataRow.get_key(h/divisor, k/divisor, l/divisor, int(truncation_on_file))]
            coefficients_top    = wulff_solids_data_triangular[WulffSolidDataRow.get_key(h/divisor, k/divisor, l/divisor, min(100, 1 + int(truncation_on_file)))]
        else:
            coefficients_bottom = wulff_solids_data_hexagonal[WulffSolidDataRow.get_key(h/divisor, k/divisor, l/divisor, int(truncation_on_file))]
            coefficients_top    = wulff_solids_data_hexagonal[WulffSolidDataRow.get_key(h/divisor, k/divisor, l/divisor, min(100, 1 + int(truncation_on_file)))]

        return  WulffSolidDataRow(h,
                                  k,
                                  l,
                                  truncation_on_file,
                                  __point_in_between(coefficients_top.limit_dist  , coefficients_bottom.limit_dist  , x),
                                  __point_in_between(coefficients_top.aa          , coefficients_bottom.aa          , x),
                                  __point_in_between(coefficients_top.bb          , coefficients_bottom.bb          , x),
                                  __point_in_between(coefficients_top.cc          , coefficients_bottom.cc          , x),
                                  __point_in_between(coefficients_top.dd          , coefficients_bottom.dd          , x),
                                  __point_in_between(coefficients_top.chi_square_1, coefficients_bottom.chi_square_1, x),
                                  __point_in_between(coefficients_top.a0          , coefficients_bottom.a0          , x),
                                  __point_in_between(coefficients_top.b0          , coefficients_bottom.b0          , x),
                                  __point_in_between(coefficients_top.c0          , coefficients_bottom.c0          , x),
                                  __point_in_between(coefficients_top.d0          , coefficients_bottom.d0          , x),
                                  __point_in_between(coefficients_top.xj          , coefficients_bottom.xj          , x),
                                  __point_in_between(coefficients_top.a1          , coefficients_bottom.a1          , x),
                                  __point_in_between(coefficients_top.b1          , coefficients_bottom.b1          , x),
                                  __point_in_between(coefficients_top.c1          , coefficients_bottom.c1          , x),
                                  __point_in_between(coefficients_top.d1          , coefficients_bottom.d1          , x),
                                  __point_in_between(coefficients_top.xl          , coefficients_bottom.xl          , x),
                                  __point_in_between(coefficients_top.chi_square_2, coefficients_bottom.chi_square_2, x))

#########################################################

def A_c(D, L, h, k, l, truncation):
    coefficients = __get_Hj_coefficients(h, k, l, truncation)

def g(mu, sigma, D):
    return lognormal_distribution(mu, sigma, D)

def Vc(D, truncation):
    return D**3

if __name__=="__main__":
    coefficients = __get_Hj_coefficients(4, 4, 0, 0.3)

    print(coefficients)
