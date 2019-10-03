######################################################################
# STRUCTURE - GSAS-II plugin
######################################################################
import sys, tempfile, site, os, subprocess, numpy, pickle, codecs

from orangecontrib.wonder.util.gui.gui_utility import OW_IS_DEVELOP

if OW_IS_DEVELOP:
    gsasii_dirname = os.environ.get("GSAS-II-DIR")
    gsasii_temp_dir = os.environ.get("GSAS-II-TEMP-DIR")
else:
    gsasii_dirname = os.path.join(site.getsitepackages()[0], "GSAS-II-WONDER")
    gsasii_temp_dir = tempfile.gettempdir()

sys.path.insert(0, gsasii_dirname)

project_file = os.path.join(gsasii_temp_dir, "temp.gpx")

GSASII_MODE_ONLINE = 1
GSASII_MODE_EXTERNAL = 2

if sys.platform == "darwin":
    GSASII_MODE = GSASII_MODE_EXTERNAL
else:
    GSASII_MODE = GSASII_MODE_ONLINE

try:
    import GSASIIscriptable as G2sc
    G2sc.SetPrintLevel("none")

    print("GSAS-II found in ", gsasii_dirname)
except:
    print("GSAS-II not available")

class GSASIIReflectionData:
    def __init__(self, h, k, l, pos, multiplicity, F2):
        self.h = int(h)
        self.k = int(k)
        self.l = int(l)
        self.pos = pos
        self.multiplicity = int(multiplicity)
        self.F2 = F2

    @classmethod
    def create_key(cls, h, k, l):
        return str(h) + str(k) + str(l)

    def get_key(self):
        return self.create_key(self.h, self.k, self.l)

    def get_intensity_factor(self):
        return self.F2*self.multiplicity

    def __str__(self):
        return str(self.h           ) + " "  + \
               str(self.k           ) + " "  + \
               str(self.l           ) + " "  + \
               str(self.pos         ) + " "  + \
               str(self.multiplicity) + " "  + \
               str(self.F2          ) + " "  + \
               str(self.get_intensity_factor())

class GSASIIReflections:
    def __init__(self, cif_file, wavelength, twotheta_min=0.0, twotheta_max=180.0):
        self.__data = {}

        if GSASII_MODE == GSASII_MODE_ONLINE:
            gpx = G2sc.G2Project(newgpx=project_file)
            gpx.add_phase(cif_file, phasename="wonder_phase", fmthint='CIF')

            prm_file = self.create_temp_prm_file(wavelength)

            hist1 = gpx.add_simulated_powder_histogram("wonder_histo", prm_file, twotheta_min, twotheta_max, 0.01, phases=gpx.phases())

            gpx.data['Controls']['data']['max cyc'] = 0 # refinement not needed
            gpx.do_refinements([{}])

            gsasii_data = hist1.reflections()["wonder_phase"]["RefList"]

            for item in gsasii_data:
                entry = GSASIIReflectionData(item[0], item[1], item[2], item[5], item[3], item[9])
                self.__data[entry.get_key()] = entry

        elif GSASII_MODE == GSASII_MODE_EXTERNAL:
            prm_file = self.create_temp_prm_file(wavelength)
            gsasii_data_file = os.path.join(gsasii_temp_dir, "gsasii_data.dat")
            python_script_file = self.create_python_script(gsasii_dirname, gsasii_temp_dir, gsasii_data_file, project_file, cif_file, prm_file, twotheta_min, twotheta_max)

            gsasii_data = pickle.loads(subprocess.check_output([sys.executable, python_script_file], timeout=10))

            for item in gsasii_data:
                entry = GSASIIReflectionData(item[0], item[1], item[2], item[5], item[3], item[9])
                self.__data[entry.get_key()] = entry

    def get_reflection(self, h, k, l):
        return self.__data[GSASIIReflectionData.create_key(h, k, l)]

    def get_reflections(self):
        return [self.__data[key] for key in self.__data.keys()]

    @classmethod
    def create_temp_prm_file(cls, wavelength):
        temp_file_name = os.path.join(gsasii_temp_dir, "temp.instprm")
        temp_file = open(temp_file_name, "w")

        text = "#GSAS-II instrument parameter file; do not add/delete items!\n" + \
               "Type: PXC" + "\n" + \
               "Bank: 1.0" + "\n" + \
               "Lam: " + "{:10.8f}".format(wavelength*10) + "\n" + \
               "Polariz.: 0.99" + "\n" + \
               "Azimuth: 0.0" + "\n" + \
               "Zero: 0.0" + "\n" + \
               "U: 1.163" + "\n" + \
               "V: -0.126" + "\n" + \
               "W: 0.063" + "\n" + \
               "X: 0.0" + "\n" + \
               "Y: 0.0" + "\n" + \
               "Z: 0.0" + "\n" + \
               "SH / L: 0.002"

        temp_file.write(text)
        temp_file.close()

        return temp_file_name

    def create_python_script(self, gsasii_dirname, gsasii_temp_dir, gsasii_data_file, project_file, cif_file, prm_file, twotheta_min, twotheta_max):
        python_script_file_name = os.path.join(gsasii_temp_dir, "temp.py")
        python_script =  open(python_script_file_name, "w")

        text =  "import sys, os, numpy, pickle, codecs\n\n"  + \
                "gsasii_dirname = '" + gsasii_dirname + "'\n" + \
                "gsasii_temp_dir = '" + gsasii_temp_dir + "'\n" + \
                "gsasii_data_file = '" + gsasii_data_file + "'\n" + \
                "project_file = '" + project_file + "'\n" + \
                "cif_file = '" + cif_file + "'\n" + \
                "prm_file = '" + prm_file + "'\n" + \
                "twotheta_min = " + str(twotheta_min) + "\n" + \
                "twotheta_max = " + str(twotheta_max) + "\n" + \
                "sys.path.insert(0, gsasii_dirname)\n\n" + \
                "try:" + "\n" + \
                "    import GSASIIscriptable as G2sc" + "\n" + \
                "    G2sc.SetPrintLevel('none')" + "\n" + \
                "except:" + "\n" + \
                "    raise ValueError('GSAS NOT FOUND!')" + "\n" + \
                "gpx = G2sc.G2Project(newgpx=project_file)" + "\n" + \
                "gpx.add_phase(cif_file, phasename='wonder_phase', fmthint='CIF')" + "\n" + \
                "hist1 = gpx.add_simulated_powder_histogram('wonder_histo', prm_file, twotheta_min, twotheta_max, 0.01, phases=gpx.phases())" + "\n" + \
                "gpx.data['Controls']['data']['max cyc'] = 0" + "\n" + \
                "gpx.do_refinements([{}])" + "\n" + \
                "gsasii_data = hist1.reflections()['wonder_phase']['RefList']" + "\n" + \
                "pickle.dump(gsasii_data, os.fdopen(sys.stdout.fileno(), 'wb'))"

        python_script.write(text)
        python_script.close()

        return python_script_file_name

def gsasii_load_reflections(cif_file, wavelength, twotheta_min=0.0, twotheta_max=180.0):
    return GSASIIReflections(cif_file, wavelength, twotheta_min, twotheta_max)

def gsasii_intensity_factor(h, k, l, reflections):
    return reflections.get_reflection(h, k, l).get_intensity_factor()

