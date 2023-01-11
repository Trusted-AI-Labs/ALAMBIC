from accelerate import Accelerator

class OneAccelerator(Accelerator):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(OneAccelerator, cls).__new__(cls)
        return cls.instance