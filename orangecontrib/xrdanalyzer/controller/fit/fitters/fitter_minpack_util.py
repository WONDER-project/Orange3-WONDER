import numpy

########################################
#
# DATA STRUCTURES
#
########################################

class CVector:

    def __init__(self, _n=0):
        self._create_attributes(_n)

    def setSize(self, _n):
        if self.n != _n:
            self._create_attributes(_n)

    def _create_attributes(self, _n):
        self.n = _n

        if self.n > 0:
            self.data = numpy.zeros(self.n)
        else:
            self.data = None

    def getSize(self):
        return self.n

    #inline double &operator [] (int i) const { assert(i<n); return data[i]; }
    def __getitem__(self, index):
        assert index < self.n

        return self.data[index]

    def __setitem__(self, index, value):
        assert index < self.n

        self.data[index] = value

    #inline double &operator () (int i) const { assert(i<=n); return data[i-1]; }
    def getitem(self, i):
        assert i <= self.n

        return self.data[i-1]

    def setitem(self, i, value):
        assert i <= self.n

        self.data[i-1]=value

    #CVector &operator - ()
	#{
	#	for(int i=0; i<n; ++i)
	#		data[i] = -data[i];
	#	return *this;
	#}
    def __neg__(self):
        for i in range(0, self.n):
            self.data[i] = -self.data[i]

        return self;

    def zero(self):
        self.__init__(self.n)

    def __str__(self):
        str = ""
        if not self.data is None:
            for item in self.data:
                str += "%4.4f\n"%item
        return str

class CMatrix:

    def __init__(self, _n=0, _m=0):
        self.n = _n
        self.m = _m

        if self.n > 0 and self.m > 0:
            self.data = numpy.zeros(self.n*self.m).reshape((self.n, self.m))
        else:
            self.data = None

    def setSize(self, _n, _m):
        if (self.n == _n) and (self.m == _m):
            return

        if self.n*self.m != _n*_m:
            self.data = numpy.zeros(_n*_m).reshape((_n, _m))

        self.n = _n
        self.m = _m

    #inline double *operator [] (int i)		  const { assert(i<n);  return idx[i]; }
    def __getitem__(self, index):
        assert index < self.n

        return self.data[index, :]

    def __setitem__(self, index, value):
        assert index < self.n

        self.data[index, :] = value


    #inline double &operator () (int i, int j) const	{ assert(j<=m); return idx[--i][--j]; }
	#inline double *operator () (int i)		  const	{ assert(i<=n); return idx[--i]; }
    def getitem(self, i, j=None):
        assert i <= self.n

        if j is None:
            return self.data[i-1, :]
        else:
            assert j <= self.m

            return self.data[i-1, j-1]

    def setitem(self, i, j, value):
        assert j <= self.m

        self.data[i-1, j-1] = value

    def zero(self):
        self.__init__(self.n, self.m)

    def getSize(self):
        return self.n*self.m

    def __str__(self):
        str = ""
        if not self.data is None:
            for j in range(0, self.m):
                for i in range(0, self.n):
                    str += "%4.4f\t"%self.data[i, j]
                str += "\n"
        return str

import copy

class CTriMatrix:

    def __init__(self, _n=0, other=None):
        if other is None:
            self._create_attributes(_n)
        else:
            self.n = other.getSize()
            self.data = copy.deepcopy(other.data)

    def _create_attributes(self, _n):
        self.n = _n

        if self.n > 0:
            self.data = numpy.zeros(int(self.n*(self.n + 1)/2))
        else:
            self.data = None

    def getSize(self):
        return self.n

    def setSize(self, _n):
        if self.n != _n:
            self._create_attributes(_n)

    #	inline const CTriMatrix &operator =(CTriMatrix &m)
	#{
	#	assert(m.n == n);
	#	memcpy((void*)data, (void*)m.data, sizeof(double) * (n*(n+1)/2));
	#	return *this;
	#}
    def assign(self, other):
        assert other.n == self.n
        self.__init__(other=other)


    #inline double &operator [] (int i) const { assert(i<n); return data[i]; }
    def __getitem__(self, index):
        assert index < self.n

        return self.data[index]

    def __setitem__(self, index, value):
        assert index < self.n

        self.data[index] = value

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
        if j is None:
            assert i <= self.n*(self.n + 1)/2
            return self.data[int(i-1)]
        else:
            assert i <= self.n
            assert j <= self.n

            i -=1
            j -=1

            if i < j : i, j = self.swap(i, j)
            l = int(i*(i+1)/2)

            return self.data[l+j]

    def setitem(self, i, value):
        assert i <= self.n*(self.n + 1)/2

        self.data[int(i-1)]=value

    def chodec(self):
        for j in range(1, self.n+1):
            l = int(j*(j+1)/2)

            if j>1:
                for i in range(j, self.n+1):
                    k1 = int(i * (i - 1)/2 + j)
                    f  = self.getitem(k1)
                    k2 = j - 1
                    for k in range(1, k2+1):
                        f -= self.getitem(k1-k)*self.getitem(l-k)
                    self.setitem(k1, f)

            if self.getitem(l) > 0:
                f = numpy.sqrt(self.getitem(l))

                for i in range(j, self.n+1):
                    k2 = int(i*(i-1)/2+j)
                    self.setitem(k2, self.getitem(k2)/f)
            else:
                return -1; # negative diagonal

        return 0

    def choback(self, g=CVector()):
        g.setitem(1, value=g.getitem(1)/self.getitem(1))

        if self.n > 1:
            l=1
            for i in range(2, self.n+1):
                k=i-1
                for j in range(1, k+1):
                    l += 1
                    g.setitem(i, g.getitem(i) - self.getitem(l)*g.getitem(j))
                l += 1
                g.setitem(i, g.getitem(i) / self.getitem(l))

        mdi = self.n*(self.n+1)/2

        g.setitem(self.n, g.getitem(self.n) / self.getitem(mdi))

        if self.n > 1:
            for k1 in range(2, self.n + 1):

                i = self.n+2-k1
                k = i-1
                l = int(i*k/2)

                for j in range (1, k+1):
                    g.setitem(j, g.getitem(j) - g.getitem(i)*self.getitem(l+j))
                g.setitem(k, g.getitem(k) / self.getitem(l))

    def zero(self):
        self.__init__(self.n)

    def __str__(self):
        str = ""
        if not self.data is None:
            for i in range(1, self.n+1):
                for j in range(1, i+1):
                    str += "%4.4f\t"%self.getitem(i,j)
                str += "\n"
        return str

    def swap(self, i, j):
        t = i
        i = j
        j = t

        return i, j

    def equals(self, other):
        if not self.data is None:
            for i in range(1, self.n+1):
                for j in range(1, self.n+1):
                    if self.getitem(i,j) != other.getitem(i,j): return False
        else:
            return False

        return True




if __name__=="__main__":

    vector = CVector(10)

    vector[2] = 1.4
    vector.setitem(4, 25)

    print(vector[2])
    print(vector[3])
    print(vector.getitem(4))
    print(vector)
    print(-vector)