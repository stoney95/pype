class PypelyTuple(tuple):
    
    def __new__(cls, *x):
        return super(PypelyTuple, cls).__new__(cls, x)