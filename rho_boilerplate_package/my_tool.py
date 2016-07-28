import logging

logger = logging.getLogger(__name__)


class MyClass(object):
    """ Boilerplate class
    """
    def __init__(self):
        super(MyClass, self).__init__()

    def start(self):
        return 'Foo Bar'
