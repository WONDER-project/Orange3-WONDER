import numpy
import scipy.special
import matplotlib.pyplot as plt

# Leonardi's common volume
# Python parser for Leonardi's cfv for truncated cubes


def load_cvf_data(filename):
    return numpy.loadtxt(filename, skiprows=2)


def load_cvf_dictionary(cvf_data, direction, truncation):
    truncation_1 = int(truncation//1)
    coefficients = dict()
    for col in cvf_data:
        if list(col[:3]) == direction:
            if col[3] == truncation_1:
                coefficients['limit_dist'] = col[4]
                coefficients['xj'] = col[14]
                coefficients['a0'] = col[10]
                coefficients['b0'] = col[11]
                coefficients['c0'] = col[12]
                coefficients['d0'] = col[13]
                coefficients['a1'] = col[15]
                coefficients['b1'] = col[16]
                coefficients['c1'] = col[17]
                coefficients['d1'] = col[18]
    return coefficients
	
def FFourierLognormal(myHn, L, Kc, mu, sigma2, ssqrt2): #from PM2K
    val = 0
    for n in range(0, 3, 1):
        Mnratio = n*(-mu+(n/2.0-3.0)*sigma2) #Mn(3-n,mu,sigma)/Mn(3,mu,sigma)
        if (Mnratio > -50.):
            YI = (numpy.log(L*Kc)-mu-(3.0-1.0*n)*sigma2)/ssqrt2
            val = val + myHn[n]*scipy.special.erfc(YI)*numpy.exp(Mnratio)*(L**n)/2.0
    return val

def main():
    dShape = 'DSHAPE_LOGNORMAL'
    THRESH = 0.001
    sigma = 0.02
    sigma2 = sigma*sigma
    ssqrt2 = sigma*numpy.sqrt(2.0)
    mu = 1
    direction = [1,1,0]
    truncation_level = 0
    L =  numpy.arange(0,3.2,0.01)

    import os
    from orangecontrib.wonder.controller.fit import wppm_functions
    wulff_data_path = os.path.join(os.path.dirname(wppm_functions.__file__), "data")
    wulff_data_path = os.path.join(wulff_data_path, "wulff_solids")

    input_file = os.path.join(wulff_data_path, 'Cube_TruncatedCubeHexagonalFace_L_FIT.data') #name of the file where the coefficients are stored
    cvf_data = load_cvf_data(input_file)
    dic = load_cvf_dictionary(cvf_data,direction, truncation_level)
    print(dic)
#--------------From PM2K-----------------------------------------------------------
    Hn_do1 = numpy.array([dic['a0'], dic['b0'], dic['c0'], dic['d0']])
    Hn_do2 = numpy.array([dic['a1'], dic['b1'], dic['c1'], dic['d1']])
    Hn_LD = dic['limit_dist'] * 0.01
    Hn_Kc = 1/Hn_LD
    Hn_xj = dic['xj']
    A=[0]
    if dShape == 'DSHAPE_LOGNORMAL':
        if numpy.abs(Hn_xj-1.0)<THRESH:
            distr = FFourierLognormal(Hn_do1,L*Hn_Kc,1.,mu,sigma2,ssqrt2) #pow(Hn.LD,k)
            if distr.all()>10**(-20): A += distr
        else:
            distr  = FFourierLognormal(Hn_do2,L*Hn_Kc,1,mu,sigma2,ssqrt2)
            distr2 = FFourierLognormal(Hn_do1,L*Hn_Kc,1/Hn_xj,mu,sigma2,ssqrt2)
            distr3 = FFourierLognormal(Hn_do2,L*Hn_Kc,1/Hn_xj,mu,sigma2,ssqrt2)
            if distr.all()>10**(-20):  A += distr #integr(f2) on LK
            if distr2.all()>10**(-20): A += distr2 #(integr(f1)) on LKxj
            if distr3.all()>10**(-20): A -= distr3 #(integr(f2)) on LKxj
#----------------------------------------------------------------------------------------------------------------------
    A = numpy.asarray(A)
    for j in range(0,len(A)):
        if L[j]==0: A[j]=1
        if A[j]>1: A[j]=1
    for j in range(1,len(A)): #control statements from PM2K
        if A[j]<0: A[j]=0
        if A[j]>A[j-1]: A[j]=0

    plt.plot(L,A)

#---- Testing against analytical expression, not part of routine ------------------------------------------
    analytical100 = numpy.where((L >= 0) & (L < dic['limit_dist']), 1 - L/2.7, 0)
    analytical110 = numpy.where((L >= 0) & (L < dic['limit_dist']), 1 - 2*L/3.8 + (L/3.8)**2, 0)
    analytical111 = numpy.where((L >= 0) & (L < dic['limit_dist']), 1 - numpy.sqrt(3)*L/2.8 +(L/2.8)**2
                                - (1/(numpy.sqrt(3))**3)*(L/2.8)**3, 0)
    #plt.plot(L,analytical100)
    plt.plot(L,analytical110)
    #plt.plot(L,analytical111)
#------------------------------------------------------------------------------------------------------------------
    plt.show()
    return

main()
