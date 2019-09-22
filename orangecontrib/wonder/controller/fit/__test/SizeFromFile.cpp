#include "SizeFromFile.h"
#include <stdio.h>
#include <shlwapi.h>
#include <gsl/gsl_errno.h>
#include <gsl/gsl_math.h>
#include <gsl/gsl_sf_gamma.h>
#include <gsl/gsl_sf_erf.h>
#include <direct.h>

#define THRESH 1e-3

//#pragma comment(lib, "gsl.lib")
//////////////////////////////
/*
std::string findFileName(const char *path);
std::string findDirName(const char *path);
std::string findFileName(const char *path)
{
	return std::string(PathFindFileName(path));
}

std::string findDirName(const char *path)
{
	char buffer[MAX_PATH];
	strcpy_s(buffer, MAX_PATH, path);
	PathRemoveFileSpec(buffer);
	return std::string(buffer);
}
*/
struct DShape_s
{
	const char *str;
	DShape s;
} ds [] = 
{
	"delta", DSHAPE_DELTA,
	"lognormal", DSHAPE_LOGNORMAL,
	"york", DSHAPE_YORK,
	"gamma", DSHAPE_GAMMA,
	"generalised gamma", DSHAPE_GENGAMMA,
	NULL, DSHAPE_DELTA 
};

int fSizeFromFile(IParser *p)
{

	int totargs = p->getNrArgs();
	if(totargs != 5)
	{
		p->setError()->pushString("SizeFromFile: expected 5 parameters (filename,size)");
		return 1;
	}
	// first parameter: file name
	if(p->isStringError(0,"SizeFromFile arg 1: string (file containing parameteric shape data)")) return 1;
	const char *rdfilecos = p->toString(0);
	// second parameter: distribution shape
	if(p->isStringError(0,"SizeFromFile arg 2: string (distribution shape)")) return 1;
	const char *dShape	= p->toString(0);
	// match the distribution shape string
	int dsn = 0;
	for(dsn=0; ds[dsn].str != NULL; dsn++)
		if(_stricmp(ds[dsn].str, dShape) == 0) break;
	if(ds[dsn].str==NULL)
	{
		p->setError()->pushString("SizeDistribution arg 2: distribution shape not recognised");
		return 1;
	}	// first parameter: mean
	if(p->isParameterError(0,"SizeFromFile arg 3: parameter (mean)"))	return 1;
	// second parameter: variance
	if(p->isParameterError(1,"SizeFromFile arg 4: parameter (variance)"))	return 1;
	if(p->isParameterError(2,"SizeFromFile arg 5: truncation"))	return 1;
	
		// instantiate the function
	CSizeFromFile *fFF = (CSizeFromFile *) p->getCurr_f();

	// check existence of the fFF instance
	if(fFF == NULL)
	{
		printf("!?!??!?!??!");
		exit(1);
	}

   /*
   char* buffer;
   // Get the current working directory: 
   if( (buffer = _getcwd( NULL, 0 )) == NULL )
      perror( "_getcwd error" );
   else
   {
      printf( "%s \nLength: %d\n", buffer, strnlen(buffer,255) );
      free(buffer);
   }
*/
	// check for existence of description file
	
	FILE *f; errno_t err;
	if((err = fopen_s(&f,rdfilecos, "r") != 0))
	{
		p->setError()->pushString("SizeFromFile: Cos terms file not found.");
		return 1;
	}
	fclose(f);
	
	// file exist. Assign name
	fFF->readFileCos(rdfilecos);

	// push size parameters
	CParameter *level = p->toParameter(p->getNrArgs() - 1);
	CParameter *sigma = p->toParameter(p->getNrArgs() - 1);
	CParameter *mu	  = p->toParameter(p->getNrArgs() - 1);
	level->setStep(0.1);
	level->setHardwareMinMax(0.0,1.0);
	fFF->addParam(mu);
	fFF->addParam(sigma);
	fFF->addParam(level);
	// set distribution shape
	fFF->setDShape(ds[dsn].s);

	return 0;
}


void CSizeFromFile::readFileCos(const char *fn) 
{ 
	filecos = fn; 
	// get file size
//	struct stat filestatus;
//	stat( filecos.c_str(), &filestatus );
	// open file
	FILE *f;
	fopen_s(&f,filecos.c_str(), "r");
//	filecosdata = (char*)malloc(filestatus.st_size*sizeof(char));
//	fread(filecosdata, filestatus.st_size, 1, f);
//	fclose(f);
	struct SHn Hn;
	char buffer[4096];
	bool found = false;
	while (!feof(f)&&(!found))
	{
		fgets(buffer, 4096, f);
		// files contains
		// h k l level LD DO1[] xj DO2[] xl chi
		// level -> parametro di troncamento: 0 = ottaedro 1 = cubo 
		// xj intersezione due curve
		// xl intersezione con zero
		if (sscanf_s(buffer, "%lf %lf %lf %lf %lf %*lf %*lf %*lf %*lf %*lf %lf %lf %lf %lf %lf %lf %lf %lf %lf %lf %lf", 
			&Hn.h, &Hn.k, &Hn.l, &Hn.level, &Hn.LD, 
			&Hn.do1[0], &Hn.do1[1], &Hn.do1[2], &Hn.do1[3], &Hn.xj, 
			&Hn.do2[0], &Hn.do2[1], &Hn.do2[2], &Hn.do2[3], &Hn.xl, &Hn.chido)==16)
		{
			Hn.LD *= .01;
			Hn.Kc = 1./Hn.LD;
			Hn.norm = sqrt(Hn.h*Hn.h+Hn.k*Hn.k+Hn.l*Hn.l);
			Hcoeffs.push_back(Hn);
		}
	}
	fclose(f);

}

CSizeFromFile::~CSizeFromFile()
{
	printf("CSizeFromFile v.%i ",getVersion());
	Hcoeffs.clear();
	//delete [] v;
}

void CSizeFromFile::onInit()
{
	//enableCache(5);
	//setNrCacheParam(2);
	//v = new double[2];
	// check if files are present
	/*if (!filecos.empty())
	{
		int k = 0;
		double p1,p2;
		FILE *f; errno_t err;

		if((err = fopen_s(&f,filecos.c_str(), "r") != 0))
			exit(0);	// FIXME: file nn trovato.
		// scan the file to check number of points and 
		// presence of L - A(L) couples
		char buffer[4096];

		while (!feof(f))
		{
			fgets(buffer, 4096, f);
			if (sscanf_s(buffer, "%lf %lf", &p1, &p2)==2)
				++k;
		}
		printf("Cos terms file: found %d lines containing (L,A(L)) couples\n",k);
		setALN(k);
		fclose(f);
	}*/
}

void CSizeFromFile::onSetNrPoints(int np)
{
	nrPoints = np;
}

void CSizeFromFile::onSetCacheParams(double *&par)
{
	//v[0] = getParameter(0)->getValue();
	//v[1] = ((CWPPM*)F)->getCurrPhase()->a();
	//par = v;
	par = NULL;
}

double NRM(double K, double mu, double sigma)
// norm for cylinders, lognormal distribution
{
	double tmp = 3.*mu+9.*sigma*sigma/2.;
	if (tmp<-100)
		return 0.0;
	else
		return exp(tmp)*PI/(4.*K);
}

double FFourierLognormal(double myHn[4], double L, double Kc, double mu, double sigma2, double ssqrt2) 
{
	double val = 0.;
	for(int n=0; n<4; n++)
	{
		double Mnratio = n*(-mu+(n/2.0-3.0)*sigma2); // Mn(3-n,mu,sigma)/Mn(3,mu,sigma)
		if (Mnratio > -50.) {
			double YI = (log(L*Kc)-mu-(3.0-1.0*n)*sigma2)/ssqrt2;
			val += myHn[n]*gsl_sf_erfc(YI)*exp(Mnratio)*pow(L, n)/2.0;
		}
	}
	return val;
}


double FFourierGamma(double myHn[4], double L, double Kc, double mu, double sigma) 
{
	double val = 0.;
	for(int n=0; n<4; n++)
	{
		val += myHn[n]*pow(L*sigma/mu,n)*gsl_sf_gamma_inc(sigma+3-n,L*Kc*sigma/mu)/gsl_sf_gamma(sigma+3); 
	}
	return val;
}


void CSizeFromFile::onEval(CVectorCOW &A, CVectorCOW &B, CBrowser *data)
{
	double mu = fabs(getParameter(0)->getValue()),
		sigma = fabs(getParameter(1)->getValue()),	
		level = ceil(100.*fabs(getParameter(2)->getValue()));
	//printf("par 2 = %f, level = %f\n",getParameter(2)->getValue(),ceil(100.*fabs(getParameter(2)->getValue())));

	CPeak *p = ((CWPPM *) F)->getCurrPeak();

	double mnorm = sqrt(p->h()*p->h()+p->k()*p->k()+p->l()*p->l());
	double HH = fabs(p->h()/mnorm);
	double KK = fabs(p->k()/mnorm);
	double LL = fabs(p->l()/mnorm);
/*
		double HH  = getH(); double KK = getK(); double LL = getL();
		double PD = pha->cellVol()/sqrt((pha->getS11()*HH*HH+pha->getS22()*KK*KK+
				pha->getS33()*LL*LL+2.0*pha->getS12()*HH*KK+
				2.0*pha->getS23()*KK*LL+2.0*pha->getS13()*HH*LL));

		if ((fabs(PD-p->d())>1e-5)||(fabs(HH)!=fabs(p->h()))&&(fabs(HH)!=fabs(p->k()))&&(fabs(HH)!=fabs(p->l())))
*/
	int hj = 0;
	bool found = false;
	while (hj<(int)Hcoeffs.size())
	{
		if (Hcoeffs[hj].level==level) {
			if ((fabs(HH-Hcoeffs[hj].h/Hcoeffs[hj].norm)<THRESH)&&
				(fabs(KK-Hcoeffs[hj].k/Hcoeffs[hj].norm)<THRESH)&&
				(fabs(LL-Hcoeffs[hj].l/Hcoeffs[hj].norm)<THRESH)) {
					found = true;
					break;
			}
		}
		hj++;
	}

	if (found) 
	{
		struct SHn Hn = Hcoeffs[hj];
		double sigma2 = sigma*sigma;
		double ssqrt2 = sigma*sqrt(2.0);
		int cyc = 1, j = 0;
		while ((j<nrPoints) && (cyc == 1))
		{
			double L = data->getPoint(j)[0];
			A[j] = 0.0;
			if (L==0.) 
				A[j]=1.0;
			else
			{
				if(dShape == DSHAPE_LOGNORMAL)
				{
					if (fabs(Hn.xj-1.0)<THRESH) {
						double distr = FFourierLognormal(Hn.do1,L*Hn.Kc,1.,mu,sigma2,ssqrt2); ///pow(Hn.LD,k);
						if (distr>1e-20) A[j] += distr;
					} else {
						double distr  = FFourierLognormal(Hn.do2,L*Hn.Kc,1.      ,mu,sigma2,ssqrt2);
						double distr2 = FFourierLognormal(Hn.do1,L*Hn.Kc,1./Hn.xj,mu,sigma2,ssqrt2);
						double distr3 = FFourierLognormal(Hn.do2,L*Hn.Kc,1./Hn.xj,mu,sigma2,ssqrt2);
						if (distr>1e-20)  A[j] += distr; //integr(f2) on LK
						if (distr2>1e-20) A[j] += distr2; // (integr(f1)) on LKxj
						if (distr3>1e-20) A[j] -= distr3; // (integr(f2)) on LKxj
					}
				}
				else if(dShape == DSHAPE_YORK)
				{
					//double distr = gsl_sf_gamma_inc(sigma+(4.0-k),Hn.Kc*L*sigma/mu)/gsl_sf_gamma(sigma+4.0)*pow(sigma*L/mu, k);
					//if (distr>1e-20) A[j] += HHn[k]*distr;
				}
				else if(dShape == DSHAPE_GAMMA)
				{
					if (fabs(Hn.xj-1.0)<THRESH) {
						double distr = FFourierGamma(Hn.do1,L*Hn.Kc,1.,mu,sigma);
						if (distr>1e-20) A[j] += distr;
					} else {
						double distr  = FFourierGamma(Hn.do2,L*Hn.Kc,1.      ,mu,sigma);
						double distr2 = FFourierGamma(Hn.do1,L*Hn.Kc,1./Hn.xj,mu,sigma);
						double distr3 = FFourierGamma(Hn.do2,L*Hn.Kc,1./Hn.xj,mu,sigma);
						if (distr>1e-20)  A[j] += distr; //integr(f2) on LK
						if (distr2>1e-20) A[j] += distr2; // (integr(f1)) on LKxj
						if (distr3>1e-20) A[j] -= distr3; // (integr(f2)) on LKxj
					}
				}

				else if(dShape == DSHAPE_DELTA)
				{
					for(int k=0; k<4; k++)
					{
						double distr = pow(L/(mu*Hn.LD),k);
						if (fabs(Hn.xj-1.0)<THRESH) {
							A[j] += Hn.do1[k]*distr;
						} else {
							if (L < (mu*Hn.xj*Hn.LD)) {
								if (distr>1e-20) A[j] += Hn.do1[k]*distr;
							} else if (L < (mu*Hn.LD)) {
								if (distr>1e-20) A[j] += Hn.do2[k]*distr;
							} else {
								A[j] = 0.0;
								cyc = 0;
								break;							
							}
						}
					}
				}

				if ((A[j]<=0.0)||(A[j]>A[j-1])) {
					A[j] = 0.0; //for(;j<nrPoints; A[j++] = 0.0);
					cyc = 0;
					break;
				}
			}

			j++;

			/*
			if (dShape == DSHAPE_DELTA) {
				if (L >= (mu*Hn.xl*Hn.LD))
				{
					for(;j<nrPoints; A[j++] = 0.0);
					cyc = 0;
				}
				else j++;
			} else {
			// check where the Fourier coefficients are going to, and whether we 
			// should go on in L or truncate here
				if (A[j]<=0.0)
				{
					// and in case, cut them when they reach zero!
					for(;j<nrPoints; A[j++] = 0.0);
					cyc = 0;
				}
				else j++;
			}
			*/
		}
		for(;j<nrPoints; A[j++] = 0.0);

	}
	else 
	{
		for(int j=0;j<nrPoints;j++)  A[j] = 1.0;
	}
	
	B[0] = 0.0;
	memset(&B[0], 0, nrPoints * sizeof(double));
}


//---------------------------------------------------------------------
BEGIN_REGISTER_FUNCTION_DESC(1)
	ADD_FUNCTION_DESC(CSizeFromFile)
END_REGISTER_FUNCTION_DESC
//---------------------------------------------------------------------