

from .compat import tk, ttk

LEFT = tk.LEFT
BOTH = tk.BOTH
RIGHT = tk.RIGHT

W = tk.W
E = tk.E

Y = tk.Y

FRAME = "frame"
BUTTON = "button"
LABEL = "label"
MESSAGE = "message"
LISTBOX = "listbox"
ENTRY = "entry"
TOPLEVEL = "toplevel"
SCROLLBAR = "scrollbar"


def create_frame(master, *args, **kwargs):
    return TkinterAdapter.create(FRAME, master, *args, **kwargs)


def create_button(master, *args, **kwargs):
    return TkinterAdapter.create(BUTTON, master, *args, **kwargs)


def create_label(master, *args, **kwargs):
    return TkinterAdapter.create(LABEL, master, *args, **kwargs)


def create_message(master, *args, **kwargs):
    return TkinterAdapter.create(MESSAGE, master, *args, **kwargs)


def create_listbox(master, *args, **kwargs):
    return TkinterAdapter.create(LISTBOX, master, *args, **kwargs)


def create_entry(master, *args, **kwargs):
    return TkinterAdapter.create(ENTRY, master, *args, **kwargs)


def create_toplevel(master, *args, **kwargs):
    return TkinterAdapter.create(TOPLEVEL, master, *args, **kwargs)


def create_scrollbar(master, *args, **kwargs):
    return TkinterAdapter.create(SCROLLBAR, master, *args, **kwargs)


class TkinterAdapter(object):
    """
    Factory class used to give tkinter widgets default values .
    """
    @staticmethod
    def create(name, master, side=None, *args, **kwargs):
        factory = TkinterAdapter.get_factory(name)

        if factory is None:
            raise ValueError

        element = factory(master, *args, **kwargs)

        if name not in (TkinterAdapter.TOPLEVEL, ):     # toplevel doesn't have pack().
            element.pack(side=side)
        
        if name is UI.SCROLLBAR:
            element.pack(fill=UI.Y)

        if name is UI.BUTTON:
            element.pack(fill=UI.BOTH)

        return element

    @staticmethod
    def get_factory(name):
        factorys = {
            FRAME:       TkinterAdapter._frame,
            BUTTON:      TkinterAdapter._button,
            LABEL:       TkinterAdapter._label,
            MESSAGE:     TkinterAdapter._message,
            LISTBOX:     TkinterAdapter._listbox,
            ENTRY:       TkinterAdapter._entry,
            TOPLEVEL:    TkinterAdapter._toplevel,
            SCROLLBAR:   TkinterAdapter._scrollbar,
        }
        return factorys.get(name, None)

    @staticmethod
    def _frame(master, *args, **kwargs):
        borderwidth = 3

        if 'borderwidth' in kwargs:
            borderwidth = kwargs['borderwidth']
            del kwargs['borderwidth']

        frame = ttk.Frame(master, borderwidth=borderwidth, *args, **kwargs)

        return frame
    
    @staticmethod
    def _button(master, *args, **kwargs):
        text = ""
        command = None

        if 'text' in kwargs:
            text = kwargs['text']
            del kwargs['text']
        if 'command' in kwargs:
            command = kwargs['command']
            del kwargs['command']

        button = ttk.Button(master, text=text, command=command, *args, **kwargs)

        return button

    @staticmethod
    def _label(master, *args, **kwargs):
        text = ''
        anchor = UI.W

        if 'text' in kwargs:
            text = kwargs['text']
            del kwargs['text']
        if 'anchor' in kwargs:
            anchor = kwargs['anchor']
            del kwargs['anchor']

        label = ttk.Label(master, text=text, anchor=anchor, *args, **kwargs)

        return label

    @staticmethod
    def _messge(master, *args, **kwargs):
        message = tk.Message(master, *args, **kwargs)

        return message

    @staticmethod
    def _listbox(master, *args, **kwargs):
        selectmode = LISTBOX.SINGLE
        width = 25
        if 'selectmode' in kwargs:
            selectmode = kwargs['selectmode']
            del kwargs['selectmode']
        if 'width' in kwargs:
            width = kwargs['width']
            del kwargs['width']

        listbox = ListBox(master, selectmode=selectmode, width=width, *args, **kwargs)

        return listbox

    @staticmethod
    def _entry(master, *args, **kwargs):
        entry = ttk.Entry(master, *args, **kwargs)

        return entry

    @staticmethod
    def _toplevel(master, *args, **kwargs):
        title = ""
        if 'title' in kwargs:
            title = kwargs['title']
            del kwargs['title']

        toplevel = tk.Toplevel(master, *args, **kwargs)
        toplevel.title(title)

        return toplevel

    @staticmethod
    def _scrollbar(master, *args, **kwargs):
        scrollbar = ttk.Scrollbar(master, *args, **kwargs)

        return scrollbar


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
    assert horizontal in (True, False)

    if hasattr(self, _INITED):
        raise

    setattr(self, _LIST, {})
    setattr(self, _HORI, horizontal)

    setattr(self, _INITED, True)


def add_frame():
    pass


def add_button():
    pass


def add(parent, child_factory, name=None, horizontal=True, *args, **kwargs):
    """
    t_child: the type of child to add such as button, label etc.
    """
    assert __inited(parent)

    child = child_factory(parent, *args, **kwargs)
    __pack(child, )


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
    return hasattr(self, _INITED)

