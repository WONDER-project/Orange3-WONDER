import numpy
from numba import jit

NONE = numpy.inf

########################################
#
# DATA STRUCTURES
#
########################################

class CVector:

    def __init__(self, _n=0):
        self.__create_attributes(_n)

    def setSize(self, _n):
        if self.__n != _n:
            self.__create_attributes(_n)

    def __create_attributes(self, _n):
        self.__n = _n

        if self.__n > 0:
            self.__data = numpy.zeros(self.__n)
        else:
            self.__data = None

    def getSize(self):
        return self.__n

    def set_attributes(self, data):
        self.__data = copy.deepcopy(data)

    def get_attributes(self):
        return self.__data

    #inline double &operator [] (int i) const { assert(i<n); return data[i]; }
    def __getitem__(self, index):
        return self.__data[index]

    def __setitem__(self, index, value):
        self.__data[index] = value

    #inline double &operator () (int i) const { assert(i<=n); return data[i-1]; }
    def getitem(self, i):
        return getitem_cvector(self.__data, self.__n, i)

    def setitem(self, i, value):
        setitem_cvector(self.__data, self.__n, i, value)

    #CVector &operator - ()
	#{
	#	for(int i=0; i<n; ++i)
	#		data[i] = -data[i];
	#	return *this;
	#}
    def __neg__(self):
        self.__data = -1*self.__data

        return self;

    def zero(self):
        self.__init__(self.__n)

    def __str__(self):
        str = ""
        if not self.__data is None:
            for item in self.__data:
                str += "%4.4f\n"%item
        return str




class CMatrix:

    def __init__(self, _n=0, _m=0):
        self.__n = _n
        self.__m = _m

        if self.__n > 0 and self.__m > 0:
            self.__data = numpy.zeros(self.__n * self.__m).reshape((self.__n, self.__m))
        else:
            self.__data = None

    def setSize(self, _n, _m):
        if (self.__n == _n) and (self.__m == _m):
            return

        if self.__n*self.__m != _n*_m:
            self.__data = numpy.zeros(_n * _m).reshape((_n, _m))

        self.__n = _n
        self.__m = _m

    def get_attributes(self):
        return self.__data

    #inline double *operator [] (int i)		  const { assert(i<n);  return idx[i]; }
    def __getitem__(self, index):
        return self.__data[index, :]

    def __setitem__(self, index, value):
        self.__data[index, :] = value

    #inline double &operator () (int i, int j) const	{ assert(j<=m); return idx[--i][--j]; }
	#inline double *operator () (int i)		  const	{ assert(i<=n); return idx[--i]; }
    def getitem(self, i, j=None):
        if j is None:
            return self.__data[i - 1, :]
        else:
            assert  j <= self.__m

            return self.__data[i - 1, j - 1]

    def setitem(self, i, j, value):
        self.__data[i - 1, j - 1] = value

    def zero(self):
        self.__init__(self.__n, self.__m)

    def getSize(self):
        return self.__n * self.__m

    def __str__(self):
        str = ""
        if not self.__data is None:
            for j in range(0, self.__m):
                for i in range(0, self.__n):
                    str += "%4.4f\t"%self.__data[i, j]
                str += "\n"
        return str

import copy

class CTriMatrix:

    def __init__(self, _n=0, other=None):
        if other is None:
            self._create_attributes(_n)
        else:
            self.__n = other.getSize()
            self.__data = copy.deepcopy(other.__data)

    def _create_attributes(self, _n):
        self.__n = _n

        if self.__n > 0:
            self.__data = numpy.zeros(int(self.__n * (self.__n + 1) / 2))
        else:
            self.__data = None

    def getSize(self):
        return self.__n

    def setSize(self, _n):
        if self.__n != _n:
            self._create_attributes(_n)

    def get_attributes(self):
        return self.__data

    #	inline const CTriMatrix &operator =(CTriMatrix &m)
	#{
	#	assert(m.n == n);
	#	memcpy((void*)data, (void*)m.data, sizeof(double) * (n*(n+1)/2));
	#	return *this;
	#}
    def assign(self, other):
        self.__init__(other=other)

    #inline double &operator [] (int i) const { assert(i<n); return data[i]; }
    def __getitem__(self, index):
        return self.__data[index]

    def __setitem__(self, index, value):
        self.__data[index] = value

    #inline double &operator () (int i, int j) const
	#{
	#	assert(i<=n);
	#	assert(j<=n);
	#	if(--i<--j) swap(i,j);
	#	int l = i*(i+1)/2;
	#	return data[l+j];
	#}
	#inline double &operator () (int i) const { assert(i<=n*(n+1)/2); return data[i-1]; }
    def getitem(self, i, j=None):
        if j is None: return getitem_ctrimatrix(self.__data, self.__n, i)
        else: return getitem_ij_ctrimatrix(self.__data, self.__n, i, j)

    def setitem(self, i, value):
        setitem_ctrimatrix(self.__data, self.__n, i, value)

    def chodec(self):
        return _chodec_ctrimatrix(self.__data, self.__n)

    def choback(self, g=CVector()):
        _choback_ctrimatrix(self.__data, self.__n, g.get_attributes())

    def zero(self):
        self.__init__(self.__n)

    def __str__(self):
        str = ""
        if not self.__data is None:
            for i in range(1, self.__n + 1):
                for j in range(1, i+1):
                    str += "%4.4f\t"%self.getitem(i,j)
                str += "\n"
        return str

    def swap(self, i, j):
        return swap_ctrimatrix(i, j)

    def equals(self, other):
        if not self.__data is None:
            for i in range(1, self.__n + 1):
                for j in range(1, self.__n + 1):
                    if self.getitem(i,j) != other.getitem(i,j): return False
        else:
            return False

        return True

# CVector

@jit(nopython=True)
def getitem_cvector(data, n, i):
    return data[int(i-1)]

@jit(nopython=True)
def setitem_cvector(data, n, i, value):
    data[int(i-1)]=value


# CTriMatrix

@jit(nopython=True)
def swap_ctrimatrix(i, j):
    t = i
    i = j
    j = t

    return i, j

@jit(nopython=True)
def getitem_ij_ctrimatrix(data, n, i, j):
    i -=1
    j -=1

    if i < j : i, j = swap_ctrimatrix(i, j)
    l = int(i*(i+1)/2)

    return data[int(l+j)]

@jit(nopython=True)
def getitem_ctrimatrix(data, n, i):
    return data[int(i-1)]

@jit(nopython=True)
def setitem_ctrimatrix(data, n, i, value):
    data[int(i-1)]=value

@jit(nopython=True)
def _chodec_ctrimatrix(data, n):
    for j in range(1, n+1):
        l = int(j*(j+1)/2)

        if j>1:
            for i in range(j, n+1):
                k1 = int(i * (i - 1)/2 + j)
                f  = getitem_ctrimatrix(data, n, k1)
                k2 = j - 1
                for k in range(1, k2+1):
                    f -= getitem_ctrimatrix(data, n, k1 - k) * getitem_ctrimatrix(data, n, l - k)
                setitem_ctrimatrix(data, n, k1, f)

        if getitem_ctrimatrix(data, n, l) > 0:
            f = numpy.sqrt(getitem_ctrimatrix(data, n, l))

            for i in range(j, n+1):
                k2 = int(i*(i-1)/2+j)
                setitem_ctrimatrix(data, n, k2, getitem_ctrimatrix(data, n, k2) / f)
        else:
            return -1 # negative diagonal

    return 0

@jit(nopython=True)
def _choback_ctrimatrix(data, n, data_g):
    setitem_ctrimatrix(data_g, n, 1, value=getitem_ctrimatrix(data_g, n, 1) / getitem_ctrimatrix(data, n, 1))

    if n > 1:
        l=1
        for i in range(2, n + 1):
            k=i-1
            for j in range(1, k+1):
                l += 1
                setitem_ctrimatrix(data_g, n, i, getitem_ctrimatrix(data_g, n, i) - getitem_ctrimatrix(data, n, l) * getitem_ctrimatrix(data_g, n, j))
            l += 1
            setitem_ctrimatrix(data_g, n, i, getitem_ctrimatrix(data_g, n, i) / getitem_ctrimatrix(data, n, l))

    mdi = n * (n + 1) / 2

    setitem_ctrimatrix(data_g, n, n, getitem_ctrimatrix(data_g, n, n) / getitem_ctrimatrix(data, n, mdi))

    if n > 1:
        for k1 in range(2, n + 1):
            i = n + 2 - k1
            k = i-1
            l = int(i*k/2)

            for j in range (1, k+1):
                setitem_ctrimatrix(data_g, n, j, getitem_ctrimatrix(data_g, n, j) - getitem_ctrimatrix(data_g, n, i) * getitem_ctrimatrix(data, n, l + j))
            setitem_ctrimatrix(data_g, n, k, getitem_ctrimatrix(data_g, n, k) / getitem_ctrimatrix(data, n, l))
