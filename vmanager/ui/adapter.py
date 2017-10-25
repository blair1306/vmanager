# the ui node class is the base class for ui elements

class UINode(object):
    """
    """
    def __init__(self):
        self.children = []
        self.children_names = {}
        self.horizontal = True

    def add(self, child, name=None):
        if name:
            if name in self.children_names:
        pass

    def get(name):
        pass


_root = None


_INITED = '2a8b0f'
_LIST = _INITED + '_children_names'
_HORI = _INITED + '_horizontal'


def init(self, horizontal=True):
    """
    horizontal: either True or False. If true, elements that are added to this element will be added horizontally from left to right,
    or else will be added vertically.
    """
    if hasattr(self, INITED):
        raise

    setattr(self, LIST, {})
    setattr(self, HORI, horizontal)

    setattr(self, INITED, True)


def add(parent, t_child, args=(), kwargs={}, name=None, horizontal=True):
    """
    t_child: the type of child to add such as button, label etc.
    """
    assert __inited(parent)

    child = t_child(*args, **kwargs)


def get(parent, name):
    """
    """
    assert parent
    assert name

    try:
        return parent.children_names[name]
    except:
        return None

def __inited(self):
    return hasattr(self, INITED)


