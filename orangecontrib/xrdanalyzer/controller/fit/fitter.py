from orangecontrib.xrdanalyzer import Singleton, synchronized_method

@Singleton
class FitterListener():
    registered_fit_global_parameters = None
    space_parameters = None

    @synchronized_method
    def register_fit_global_parameters(self, fit_global_parameters = None):
        self.registered_fit_global_parameters = fit_global_parameters
        self.space_parameters = fit_global_parameters.space_parameters()

    def get_registered_fit_global_parameters(self):
        return self.registered_fit_global_parameters

    def get_registered_space_parameters(self):
        return self.space_parameters

class FitterInterface:

    def __init__(self):
        pass

    def init_fitter(self, fit_global_parameters=None):
        raise NotImplementedError("Abstract")

    def do_fit(self, fit_global_parameters=None, current_iteration=0):
        raise NotImplementedError("Abstract")









