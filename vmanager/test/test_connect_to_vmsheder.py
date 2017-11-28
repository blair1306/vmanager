from vmanager.app.connect_to_vmsheder import connect_to_vmsheder_window
from vmanager.ui import mainloop


def test_window():
    window = connect_to_vmsheder_window()
    mainloop()