from ..compat import is_py2, is_py3


if is_py2:
    import Tkinter as tk
    import tkFont
    import ttk

elif is_py3:
    import tkinter as tk
    from tkinter import ttk
    from tkinter import font as tkFont
