import pickle

####################################################################
# Test data loader
####################################################################

class ResultStore:
    """
    Ghetto implementation of betamax/VCR for static data
    """
    def __init__(self, record_mode, data_dir):
        assert isinstance(record_mode, bool)
        assert isinstance(data_dir, str)

        self.record_mode = record_mode
        self.data_dir = data_dir

    def check(self, name, value):
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

        fname = '{}.pickle'.format(name)
        fpath = os.path.join(self.data_dir, fname)

        if not os.path.exists(fpath):
            if self.record_mode is False:
                raise Exception("Result missing and record mode disabled")

            with open(fpath, 'wb') as fh:
                pickle.dump(value, fh)
                return value
        else:
            with open(fpath, 'rb') as fh:
                return pickle.load(fh)


