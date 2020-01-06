class ImproperlyConfigured(Exception):

    def __init__(self, msg):
        super(ImproperlyConfigured, self).__init__()
        self.msg = msg

    def __repr__(self):
        return self.msg

    def __str__(self):
        return self.__repr__()
