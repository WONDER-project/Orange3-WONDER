import os, numpy
import orangecontrib.wonder.controller.fit.wppm_functions as wf

def run_gsas_ii():
    datadir = "/Users/lrebuffi/Documents/Workspace/Wonder/GSAS-TEST"
    cif_file = os.path.join(datadir,"LaB6_NISTSRM_660a.cif")

    datadir = "/Users/lrebuffi/Documents/Workspace/Wonder/Orange3-WONDER/Use_Cases/FeMoMCX"
    cif_file = os.path.join(datadir,"Fe-Iron-alpha.cif")

    reflections = wf.load_reflections(cif_file, 0.826, 5.0, 140.0)

    print(reflections.get_reflection(1, 1, 0))

    print ("h, k, l, 2th, mult, F2, int")

    reflections = reflections.get_reflections()

    tth = numpy.zeros(len(reflections))
    ints = numpy.zeros(len(reflections))

    i = 0
    for reflection in reflections:
        print(reflection.h, reflection.k, reflection.l, reflection.pos, reflection.multiplicity, reflection.F2, reflection.get_intensity_factor())
        tth[i] = reflection.pos
        ints[i] = reflection.get_intensity_factor()
        i += 1



    from matplotlib import pyplot as plt

    plt.bar(tth,ints)
    plt.show()


if __name__=="__main__":
    run_gsas_ii()
