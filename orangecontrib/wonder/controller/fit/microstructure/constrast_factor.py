import numpy
import scipy.interpolate
import matplotlib.pyplot as plt

#========================================================#

def zener(c11,c12,c44): # definition of the Zener ratio
    return 2*c44/(c11-c12)

def c_(c12,c44): # definition of the ratio c_12/c_44
    return c12/c44

def param_eqn(a,b,c,d,c11,c12,c44): # parametrization equation
    return a*(1-numpy.exp(-zener(c11,c12,c44)/b)) + c*zener(c11,c12,c44) + d


#--- A parameters, low Zener ratio ----------------------#

def A_lowZen_screw_FCC(c11,c12,c44): # calculation of parameter A for Zener ratio <=0.5 for screw dislocation
                                     # in FCC <110>{111} slip system
    a = 0.0454
    b = 0.1704
    c = 0.1056
    d = 0.0221
    value = param_eqn(a,b,c,d,c11,c12,c44)
    return value

def A_lowZen_edge_FCC(c11,c12,c44): # calculation of parameter A for Zener ratio <=0.5 for edge dislocation
                                    # in FCC <110>{111} slip system
    if (c12/c44 > 3 or c12/c44 < 0.5):
        value = 0
    else:
        a05 = 0.0737 # parameters for c_12/c_44 = 0.5
        b05 = 0.1712
        c05 = 0.0901
        d05 = 0.0275
        a1 = 0.0659 # parameters for c_12/c_44 = 1
        b1 = 0.1551
        c1 = 0.0930
        d1 = 0.0274
        a2 = 0.0552 # parameters for c_12/c_44 = 2
        b2 = 0.1411
        c2 = 0.1057
        d2 = 0.0279
        a3 = 0.0493 # parameters for c_12/c_44 = 3
        b3 = 0.1399
        c3 = 0.1179
        d3 = 0.0286
        x = numpy.array([0.5,1,2,3])
        y = numpy.array([param_eqn(a05,b05,c05,d05,c11,c12,c44),param_eqn(a1,b1,c1,d1,c11,c12,c44),
                         param_eqn(a2,b2,c2,d2,c11,c12,c44),param_eqn(a3,b3,c3,d3,c11,c12,c44)])
        y_interp = scipy.interpolate.interp1d(x, y)
        value = y_interp(c_(c12, c44))
    return value

def A_lowZen_screw_BCC(c11,c12,c44): # calculation of parameter A for Zener ratio <=0.5 for screw dislocation in
                                     # BCC <111>{110} slip system
    if (c12/c44 > 5 or c12/c44 < 0.5):
        value = 0
    else:
        a05 = 0.0736 # parameters for c_12/c_44 = 0.5
        b05 = 0.2822
        c05 = 0.1342
        d05 = 0.0264
        a1 = 0.0624 # parameters for c_12/c_44 = 1
        b1 = 0.2236
        c1 = 0.1532
        d1 = 0.024
        a2 = 0.1264 # parameters for c_12/c_44 = 2
        b2 = 0.385
        c2 = 0.0845
        d2 = 0.0249
        a3 = 0.1271 # parameters for c_12/c_44 = 3
        b3 = 0.3591
        c3 = 0.0842
        d3 = 0.0233
        a5 = 0.1321 # parameters for c_12/c_44 = 5
        b5 = 0.3334
        c5 = 0.0783
        d5 = 0.0216
        x = numpy.array([0.5,1,2,3,5])
        y = numpy.array([param_eqn(a05,b05,c05,d05,c11,c12,c44),param_eqn(a1,b1,c1,d1,c11,c12,c44),
                         param_eqn(a2,b2,c2,d2,c11,c12,c44),param_eqn(a3,b3,c3,d3,c11,c12,c44),
                         param_eqn(a5,b5,c5,d5,c11,c12,c44)])
        y_interp = scipy.interpolate.interp1d(x, y)
        value = y_interp(c_(c12,c44))
    return value

def A_lowZen_edge_BCC(c11,c12,c44): # calculation of parameter A for Zener ratio <=0.5 for edge dislocation in
                                    # BCC <111>{110} slip system
    if (c12/c44 > 5 or c12/c44 < 0.5):
        value = 0
    else:
        a05 = 0.0565 # parameters for c_12/c_44 = 0.5
        b05 = 0.1548
        c05 = 0.0821
        d05 = 0.02432
        a1 = 0.04901 # parameters for c_12/c_44 = 1
        b1 = 0.1327
        c1 = 0.08528
        d1 = 0.02382
        a2 = 0.03768 # parameters for c_12/c_44 = 2
        b2 = 0.10732
        c2 = 0.10115
        d2 = 0.02373
        a3 = 0.03181 # parameters for c_12/c_44 = 3
        b3 = 0.09116
        c3 = 0.11696
        d3 = 0.02269
        a5 = 0.02702 # parameters for c_12/c_44 = 5
        b5 = 0.07624
        c5 = 0.14048
        d5 = 0.02075
        x = numpy.array([0.5,1,2,3,5])
        y = numpy.array([param_eqn(a05,b05,c05,d05,c11,c12,c44),param_eqn(a1,b1,c1,d1,c11,c12,c44),
                         param_eqn(a2,b2,c2,d2,c11,c12,c44),param_eqn(a3,b3,c3,d3,c11,c12,c44),
                         param_eqn(a5,b5,c5,d5,c11,c12,c44)])
        y_interp = scipy.interpolate.interp1d(x, y)
        value = y_interp(c_(c12,c44))
    return value

#--- B parameters, low Zener ratio ----------------------#

def B_lowZen_screw_FCC(c11,c12,c44): # calculation of parameter B for Zener ratio <=0.5 for screw dislocation
                                     # in FCC <110>{111} slip system
    a = 48.5946
    b = 0.0713
    c = 10.3165
    d = -54.6536
    value = -param_eqn(a,b,c,d,c11,c12,c44) * A_lowZen_screw_FCC(c11,c12,c44)
    return value

def B_lowZen_edge_FCC(c11,c12,c44): # calculation of parameter B for Zener ratio <=0.5 for edge dislocation
                                    # in FCC <110>{111} slip system
    if (c12/c44 > 3 or c12/c44 < 0.5):
        value = 0
    else:
        a05 = 43.4223 # parameters for c_12/c_44 = 0.5
        b05 = 0.0739
        c05 = 6.9926
        d05 = -48.3544
        a1 = 43.4100 # parameters for c_12/c_44 = 1
        b1 = 0.0744
        c1 = 7.6463
        d1 = -48.9061
        a2 = 43.3221 # parameters for c_12/c_44 = 2
        b2 = 0.07568
        c2 = 8.6402
        d2 = -49.6478
        a3 = 43.3401 # parameters for c_12/c_44 = 3
        b3 = 0.0771
        c3 = 9.2576
        d3 = -50.1819
        x = numpy.array([0.5,1,2,3])
        y = numpy.array([param_eqn(a05,b05,c05,d05,c11,c12,c44),param_eqn(a1,b1,c1,d1,c11,c12,c44),
                         param_eqn(a2,b2,c2,d2,c11,c12,c44),param_eqn(a3,b3,c3,d3,c11,c12,c44)])
        y_interp = scipy.interpolate.interp1d(x, y)
        value = -y_interp(c_(c12,c44)) * A_lowZen_edge_FCC(c11,c12,c44)
    return value

def B_lowZen_screw_BCC(c11,c12,c44): # calculation of parameter B for Zener ratio <=0.5 for screw dislocation
                                     # in BCC <111>{110} slip system
    a = 54.1422
    b = 0.0731
    c = 9.7907
    d = -58.552
    value = -param_eqn(a, b, c, d, c11,c12,c44) * A_lowZen_screw_BCC(c11,c12,c44)
    return value

def B_lowZen_edge_BCC(c11,c12,c44): # calculation of parameter B for Zener ratio <=0.5 for edge dislocation
                                    # in BCC <111>{110} slip system
    if (c12/c44 > 5 or c12/c44 < 0.5):
        value = 0
    else:
        a05 = 45.89136 # parameters for c_12/c_44 = 0.5
        b05 = 0.0691
        c05 = 9.09972
        d05 = -53.08442
        a1 = 45.86721 # parameters for c_12/c_44 = 1
        b1 = 0.06885
        c1 = 10.20281
        d1 = -53.96221
        a2 = 44.80338 # parameters for c_12/c_44 = 2
        b2 = 0.07067
        c2 = 11.87255
        d2 = -54.17248
        a3 = 45.14885 # parameters for c_12/c_44 = 3
        b3 = 0.07123
        c3 = 13.46823
        d3 = -55.52068
        a5 = 46.18657 # parameters for c_12/c_44 = 5
        b5 = 0.0732
        c5 = 15.16578
        d5 = -57.58587
        x = numpy.array([0.5,1,2,3,5])
        y = numpy.array([param_eqn(a05,b05,c05,d05,c11,c12,c44),param_eqn(a1,b1,c1,d1,c11,c12,c44),
                         param_eqn(a2,b2,c2,d2,c11,c12,c44),param_eqn(a3,b3,c3,d3,c11,c12,c44),
                         param_eqn(a5,b5,c5,d5,c11,c12,c44)])
        y_interp = scipy.interpolate.interp1d(x, y)
        value = -y_interp(c_(c12,c44)) * A_lowZen_edge_BCC(c11,c12,c44)
    return value

#--- A parameters, high Zener ratio ----------------------#

def A_highZen_screw_FCC(c11,c12,c44): # calculation of parameter A for Zener ratio > 0.5 for screw dislocation
                                      # in FCC <110>{111} slip system
    a = 0.1740
    b = 1.9522
    c = 0.0293
    d = 0.0662
    value = param_eqn(a,b,c,d,c11,c12,c44)
    return value

def A_highZen_edge_FCC(c11,c12,c44): # calculation of parameter A for Zener ratio > 0.5 for edge dislocation
                                     # in FCC <110>{111} slip system
    if (c12/c44 > 3 or c12/c44 < 0.5):
        value = 0
    else:
        a05 = 0.1312 # parameters for c_12/c_44 = 0.5
        b05 = 1.4284
        c05 = 0.0201
        d05 = 0.0954
        a1 = 0.1687 # parameters for c_12/c_44 = 1
        b1 = 2.0400
        c1 = 0.0194
        d1 = 0.0926
        a2 = 0.2438 # parameters for c_12/c_44 = 2
        b2 = 2.4243
        c2 = 0.0172
        d2 = 0.0816
        a3 = 0.2635 # parameters for c_12/c_44 = 3
        b3 = 2.1880
        c3 = 0.0186
        d3 = 0.0731
        x = numpy.array([0.5,1,2,3])
        y = numpy.array([param_eqn(a05, b05, c05, d05, c11, c12, c44),param_eqn(a1, b1, c1, d1, c11, c12, c44),
                         param_eqn(a2, b2, c2, d2, c11, c12, c44),param_eqn(a3, b3, c3, d3, c11, c12, c44)])
        y_interp = scipy.interpolate.interp1d(x, y)
        value = y_interp(c_(c12,c44))
    return value

def A_highZen_screw_BCC(c11,c12,c44): # calculation of parameter A for Zener ratio > 0.5 for screw dislocation
                                      # in BCC <111>{110} slip system
    a = 0.1740
    b = 1.9522
    c = 0.0293
    d = 0.0662
    value = param_eqn(a,b,c,d,c11,c12,c44)
    return value

def A_highZen_edge_BCC(c11,c12,c44): # calculation of parameter A for Zener ratio > 0.5 for edge dislocation
                                     # in BCC <111>{110} slip system
    if (c12/c44 > 2 or c12/c44 < 0.5):
        value = 0
    else:
        a05 = 1.4948 # parameters for c_12/c_44 = 0.5
        b05 = 25.671
        c05 = 0.0
        d05 = 0.0966
        a1 = 1.6690 # parameters for c_12/c_44 = 1
        b1 = 21.124
        c1 = 0.0
        d1 = 0.0757
        a2 = 1.4023 # parameters for c_12/c_44 = 2
        b2 = 12.739
        c2 = 0.0
        d2 = 0.0563
        x = numpy.array([0.5,1,2])
        y = numpy.array([param_eqn(a05,b05,c05,d05,c11,c12,c44),param_eqn(a1,b1,c1,d1,c11,c12,c44),
                         param_eqn(a2,b2,c2,d2,c11,c12,c44)])
        y_interp = scipy.interpolate.interp1d(x, y)
        value = y_interp(c_(c12,c44))
    return value

#--- B parameters, high Zener ratio ----------------------#

def B_highZen_screw_FCC(c11,c12,c44): # calculation of parameter B for Zener ratio > 0.5 for screw dislocation
                                      # in FCC <110>{111} slip system
    a = 5.4252
    b = 0.7196
    c = 0.0690
    d = -3.1970
    value = -param_eqn(a,b,c,d,c11,c12,c44) * A_lowZen_screw_FCC(c11,c12,c44)
    return value

def B_highZen_edge_FCC(c11,c12,c44): # calculation of parameter B for Zener ratio > 0.5 for edge dislocation
                                     # in FCC <110>{111} slip system
    if (c12/c44 > 3 or c12/c44 < 0.5):
        value = 0
    else:
        a05 = 4.0327 # parameters for c_12/c_44 = 0.5
        b05 = 0.8846
        c05 = 0.0986
        d05 = -2.8225
        a1 = 4.8608 # parameters for c_12/c_44 = 1
        b1 = 0.8687
        c1 = 0.0896
        d1 = -3.4280
        a2 = 5.8282 # parameters for c_12/c_44 = 2
        b2 = 0.8098
        c2 = 0.0828
        d2 = -4.297
        a3 = 6.3398 # parameters for c_12/c_44 = 3
        b3 = 0.7751
        c3 = 0.0813
        d3 = -4.8129
        x = numpy.array([0.5,1,2,3])
        y = numpy.array([param_eqn(a05,b05,c05,d05,c11,c12,c44),param_eqn(a1,b1,c1,d1,c11,c12,c44),
                         param_eqn(a2,b2,c2,d2,c11,c12,c44),param_eqn(a3,b3,c3,d3,c11,c12,c44)])
        y_interp = scipy.interpolate.interp1d(x, y)
        value = -y_interp(c_(c12,c44)) * A_highZen_edge_FCC(c11,c12,c44)
    return value

def B_highZen_screw_BCC(c11,c12,c44): # calculation of parameter B for Zener ratio > 0.5 for screw dislocation
                                      # in BCC <111>{110} slip system
    if (c12/c44 > 2 or c12/c44 < 0.5):
        print('c12/c44 out of range. A_screw and B_screw set to 0.')
        value = 0
    else:
        a05 = 7.5149 # parameters for c_12/c_44 = 0.5
        b05 = 0.3818
        c05 = 0.0478
        d05 = -4.9826
        a1 = 8.6590 # parameters for c_12/c_44 = 1
        b1 = 0.3730
        c1 = 0.0424
        d1 = -6.074
        a2 = 6.0725 # parameters for c_12/c_44 = 2
        b2 = 0.4338
        c2 = 0.0415
        d2 = -3.5021
        x = numpy.array([0.5,1,2])
        y = numpy.array([param_eqn(a05,b05,c05,d05,c11,c12,c44),param_eqn(a1,b1,c1,d1,c11,c12,c44),
                         param_eqn(a2,b2,c2,d2,c11,c12,c44)])
        y_interp = scipy.interpolate.interp1d(x, y)
        value = -y_interp(c_(c12,c44)) * A_highZen_screw_BCC(c11,c12,c44)
    return value

def B_highZen_edge_BCC(c11,c12,c44): # calculation of parameter B for Zener ratio > 0.5 for edge dislocation
                                     # in BCC <111>{110} slip system
    if (c12/c44 > 2 or c12/c44 < 0.5):
        value = 0
    else:
        a05 = 5.3020 # parameters for c_12/c_44 = 0.5
        b05 = 1.0945
        c05 = 0.1540
        d05 = -4.1841
        a1 = 7.2361 # parameters for c_12/c_44 = 1
        b1 = 0.9285
        c1 = 0.1359
        d1 = -5.7484
        a2 = 8.8331 # parameters for c_12/c_44 = 2
        b2 = 0.8241
        c2 =  0.1078
        d2 = -7.0570
        x = numpy.array([0.5,1,2])
        y = numpy.array([param_eqn(a05,b05,c05,d05,c11,c12,c44),param_eqn(a1,b1,c1,d1,c11,c12,c44),
                         param_eqn(a2,b2,c2,d2,c11,c12,c44)])
        y_interp = scipy.interpolate.interp1d(x, y)
        value = -y_interp(c_(c12,c44)) * A_highZen_edge_BCC(c11,c12,c44)
    return value


from orangecontrib.wonder.controller.fit.util.fit_utilities import Symmetry

def calculate_A_B_coefficients(c11, c12, c44, symmetry=Symmetry.FCC):
    zener_ratio = zener(c11, c12, c44)
    
    if zener_ratio <= 0.53:
        if symmetry == Symmetry.BCC:
            A_edge = A_lowZen_edge_BCC(c11, c12, c44)
            B_edge = B_lowZen_edge_BCC(c11, c12, c44)
            A_screw = A_lowZen_screw_BCC(c11, c12, c44)
            B_screw = B_lowZen_screw_BCC(c11, c12, c44)
        elif symmetry == Symmetry.FCC:
            A_edge = A_lowZen_edge_FCC(c11, c12, c44)
            B_edge = B_lowZen_edge_FCC(c11, c12, c44)
            A_screw = A_lowZen_screw_FCC(c11, c12, c44)
            B_screw = B_lowZen_screw_FCC(c11, c12, c44)
        else:
            ValueError("Unsupported symmetry")
    elif (zener_ratio > 0.53) & (zener_ratio <= 8):
        if symmetry == Symmetry.BCC:
            A_edge = A_highZen_edge_BCC(c11, c12, c44)
            B_edge = B_highZen_edge_BCC(c11, c12, c44)
            A_screw = A_highZen_screw_BCC(c11, c12, c44)
            B_screw = B_highZen_screw_BCC(c11, c12, c44)
        elif symmetry == Symmetry.FCC:
            A_edge = A_highZen_edge_FCC(c11, c12, c44)
            B_edge = B_highZen_edge_FCC(c11, c12, c44)
            A_screw = A_highZen_screw_FCC(c11, c12, c44)
            B_screw = B_highZen_screw_FCC(c11, c12, c44)
        else:
            ValueError("Unsupported symmetry")
    else:
        raise ValueError("Invalid range for Zener ratio")

    return float(A_edge), float(B_edge), float(A_screw), float(B_screw)


############################################################################################
#
# FOR TEST PURPOSES
#
#--------CALCULATION OF CONTRAST FACTORS----------------------------------------------------------#

def s(h,k,l):
    s_list =[]
    for i in range(0,len(h)):
        s_list.append((h[i]**2 + k[i]**2 + l[i]**2))
    return numpy.asarray(s_list)

def H(h,k,l):
    H_list = []
    for i in range(0,len(h)):
        H_list.append(((h[i]**2)*(k[i]**2) + (h[i]**2)*(l[i]**2) + (k[i]**2)*(l[i]**2))/(h[i]**2 + k[i]**2 + l[i]**2)**2)
    return numpy.asarray(H_list)

#----ZENER RATIO <= 0.5 ------------------------------------#

def C_lowZen_screw_BCC(c11,c12,c44,h,k,l):
    C_list = []
    if (A_lowZen_screw_BCC(c11, c12, c44) == 0):
        print('c12/c44 out of range. A_screw and B_screw set to 0.')
    print('A_screw = ' + str(A_lowZen_screw_BCC(c11, c12, c44)))
    print('B_screw = ' + str(B_lowZen_screw_BCC(c11, c12, c44)))
    for i in range(0,len(h)):
        C_list.append(A_lowZen_screw_BCC(c11,c12,c44) + B_lowZen_screw_BCC(c11,c12,c44) * ((h[i]**2)*(k[i]**2) +\
                                            (h[i]**2)*(l[i]**2) + (k[i]**2)*(l[i]**2))/(h[i]**2 + k[i]**2 + l[i]**2)**2)
    return numpy.asarray(C_list)

def C_lowZen_edge_BCC(c11,c12,c44,h,k,l):
    C_list = []
    if (A_lowZen_edge_BCC(c11, c12, c44) == 0):
        print('c12/c44 out of range. A_edge and B_edge set to 0.')
    print('A_edge = ' + str(A_lowZen_edge_BCC(c11, c12, c44)))
    print('B_edge = ' + str(B_lowZen_edge_BCC(c11, c12, c44)))
    for i in range(0,len(h)):
        C_list.append(A_lowZen_edge_BCC(c11,c12,c44) + B_lowZen_edge_BCC(c11,c12,c44) * ((h[i]**2)*(k[i]**2) +\
                                            (h[i]**2)*(l[i]**2) + (k[i]**2)*(l[i]**2))/(h[i]**2 + k[i]**2 + l[i]**2)**2)
    return numpy.asarray(C_list)

def C_lowZen_screw_FCC(c11,c12,c44,h,k,l):
    C_list = []
    if (A_lowZen_screw_FCC(c11, c12, c44) == 0):
        print('c12/c44 out of range. A_screw and B_screw set to 0.')
    print('A_screw = ' + str(A_lowZen_screw_FCC(c11, c12, c44)))
    print('B_screw = ' + str(B_lowZen_screw_FCC(c11, c12, c44)))
    for i in range(0,len(h)):
        C_list.append(A_lowZen_screw_FCC(c11,c12,c44) + B_lowZen_screw_FCC(c11,c12,c44) * ((h[i]**2)*(k[i]**2) +\
                                            (h[i]**2)*(l[i]**2) + (k[i]**2)*(l[i]**2))/(h[i]**2 + k[i]**2 + l[i]**2)**2)
    return numpy.asarray(C_list)

def C_lowZen_edge_FCC(c11,c12,c44,h,k,l):
    C_list = []
    if (A_lowZen_edge_FCC(c11, c12, c44) == 0):
        print('c12/c44 out of range. A_edge and B_edge set to 0.')
    print('A_edge = ' + str(A_lowZen_edge_FCC(c11, c12, c44)))
    print('B_edge = ' + str(B_lowZen_edge_FCC(c11, c12, c44)))
    for i in range(0,len(h)):
        C_list.append(A_lowZen_edge_FCC(c11,c12,c44) + B_lowZen_edge_FCC(c11,c12,c44) * ((h[i]**2)*(k[i]**2) +\
                                            (h[i]**2)*(l[i]**2) + (k[i]**2)*(l[i]**2))/(h[i]**2 + k[i]**2 + l[i]**2)**2)
    return numpy.asarray(C_list)

#----0.5 < ZENER RATIO <= 8 ------------------------------------#

def C_highZen_screw_BCC(c11,c12,c44,h,k,l):
    C_list = []
    if (A_highZen_screw_BCC(c11, c12, c44) == 0):
        print('c12/c44 out of range. A_screw and B_screw set to 0.')
    print('A_screw = ' + str(A_highZen_screw_BCC(c11, c12, c44)))
    print('B_screw = ' + str(B_highZen_screw_BCC(c11, c12, c44)))
    for i in range(0,len(h)):
        C_list.append(A_highZen_screw_BCC(c11,c12,c44) + B_highZen_screw_BCC(c11,c12,c44) * ((h[i]**2)*(k[i]**2) +\
                                            (h[i]**2)*(l[i]**2) + (k[i]**2)*(l[i]**2))/(h[i]**2 + k[i]**2 + l[i]**2)**2)
    return numpy.asarray(C_list)

def C_highZen_edge_BCC(c11,c12,c44,h,k,l):
    C_list = []
    if (A_highZen_edge_BCC(c11, c12, c44) == 0):
        print('c12/c44 out of range. A_edge and B_edge set to 0.')
    print('A_edge = ' + str(A_highZen_edge_BCC(c11, c12, c44)))
    print('B_edge = ' + str(B_highZen_edge_BCC(c11, c12, c44)))
    for i in range(0,len(h)):
        C_list.append(A_highZen_edge_BCC(c11,c12,c44) + B_highZen_edge_BCC(c11,c12,c44) * ((h[i]**2)*(k[i]**2) +\
                                            (h[i]**2)*(l[i]**2) + (k[i]**2)*(l[i]**2))/(h[i]**2 + k[i]**2 + l[i]**2)**2)

    return numpy.asarray(C_list)

def C_highZen_screw_FCC(c11,c12,c44,h,k,l):
    C_list = []
    if (A_highZen_screw_FCC(c11, c12, c44) == 0):
        print('c12/c44 out of range. A_screw and B_screw set to 0.')
    print('A_screw = ' + str(A_highZen_screw_FCC(c11, c12, c44)))
    print('B_screw = ' + str(B_highZen_screw_FCC(c11, c12, c44)))
    for i in range(0,len(h)):
        C_list.append(A_highZen_screw_FCC(c11,c12,c44) + B_highZen_screw_FCC(c11,c12,c44) * ((h[i]**2)*(k[i]**2) +\
                                            (h[i]**2)*(l[i]**2) + (k[i]**2)*(l[i]**2))/(h[i]**2 + k[i]**2 + l[i]**2)**2)
    return numpy.asarray(C_list)

def C_highZen_edge_FCC(c11,c12,c44,h,k,l):
    C_list = []
    if (A_highZen_edge_FCC(c11, c12, c44) == 0):
        print('c12/c44 out of range. A_edge and B_edge set to 0.')
    print('A_edge = ' + str(A_highZen_edge_FCC(c11, c12, c44)))
    print('B_edge = ' + str(B_highZen_edge_FCC(c11, c12, c44)))
    for i in range(0,len(h)):
        C_list.append(A_highZen_edge_FCC(c11,c12,c44) + B_highZen_edge_FCC(c11,c12,c44) * ((h[i]**2)*(k[i]**2) +\
                                            (h[i]**2)*(l[i]**2) + (k[i]**2)*(l[i]**2))/(h[i]**2 + k[i]**2 + l[i]**2)**2)
    return numpy.asarray(C_list)

#---PLOTTING FUNCTIONS------------------------------------------------------------#

def s_vs_C(h,k,l,C_avg):
    plt.scatter(s(h,k,l),C_avg)
    plt.show()
    return

def H_vs_C(h,k,l,C_avg):
    plt.scatter(H(h, k, l), C_avg)
    plt.show()
    return

#===================================================#

def main():
#--- User inputs -----------------------#
    c11 = 24.65
    c12 = 13.45
    c44 = 2.87
    crystal_type = 'FCC'
    screw_fraction = 0.5
    edge_fraction = 1 - screw_fraction

    file_name = "/Users/labx/Documents/workspace/Scardi-XRD/Orange3-WONDER/Examples/hkl.txt"
#---------------------------------------#
    zener_ratio = zener(c11,c12,c44)
    print('Zener ratio = ' + str(zener_ratio))
    print('c_12/c44 = ' + str(c_(c12,c44)))
    hkl = open(file_name).readlines()
    h = []
    k = []
    l = []
    for i in range(0, len(hkl)):
        row = (hkl[i].split(" "))
        h.append(int(row[0]))
        k.append(int(row[1]))
        l.append(int(row[2]))

    hkl = numpy.loadtxt(file_name)


    if zener_ratio <= 0.53:
        if crystal_type == 'BCC':
            C_screw = C_lowZen_screw_BCC(c11,c12,c44,h,k,l)
            C_edge = C_lowZen_edge_BCC(c11,c12,c44,h,k,l)
        elif crystal_type == 'FCC':
            C_screw = C_lowZen_screw_FCC(c11,c12,c44,h,k,l)
            C_edge = C_lowZen_edge_FCC(c11,c12,c44,h,k,l)
        else: print ('Unsupported crystal type')
    elif (zener_ratio > 0.53) & (zener_ratio <= 8):
        if crystal_type == 'BCC':
            C_screw = C_highZen_screw_BCC(c11,c12,c44,h,k,l)
            C_edge = C_highZen_edge_BCC(c11,c12,c44,h,k,l)
        elif crystal_type == 'FCC':
            C_screw = C_highZen_screw_FCC(c11,c12,c44,h,k,l)
            C_edge = C_highZen_edge_FCC(c11,c12,c44,h,k,l)
        else: print('Unsupported crystal type')
    else:
        C_screw = 0
        C_edge = 0
        print('Invalid range for Zener ratio. C_screw and C_edge set to 0.')
    C_avg = (screw_fraction * C_screw + edge_fraction * C_edge)/2
    H(h, k, l)
    print('H = ' + str(H(h,k,l)))
    s(h, k, l)
    print('s = ' + str(s(h,k,l)))
    print('C_avg = ' + str(C_avg))
    s_vs_C(h,k,l,C_avg)
    H_vs_C(h,k,l,C_avg)
    return

if __name__ == "__main__":
    main()
