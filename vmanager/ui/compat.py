""" python2 python3 compatibility layer.
"""


from ..compat import is_py2, is_py3


if is_py2:
    import Tkinter as tk
    import tkFont
    import ttk
    import tkMessageBox as MessageBox

elif is_py3:
    import tkinter as tk
    from tkinter import ttk
    from tkinter import font as tkFont
    from tkinter import messagebox as MessageBox
