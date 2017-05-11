#!/usr/bin/python
#
#
#
import sys


if sys.version_info >= (3, 0):
    print("Please Use Python 2")
    exit(0)

import os
import Tkinter as tk
import tkMessageBox
import tkFileDialog
import subprocess
import inspect


def exit_if_fail(status, message):
    if status == 0:
        return

    _Message.show_error(message)
    sys.exit(1)


class _Debug(object):
    DEBUG = True if '-d' in sys.argv[:] else False

    @staticmethod
    def debug(*args, **kwargs):
        use_print = True
        if "use_print" in kwargs:
            use_print = kwargs["use_print"]
            del kwargs["use_print"]

        message = "%s: %s: " % _Debug._get_caller_name()
        message += " ".join(map(repr, *args))
        if not _Debug.DEBUG:
            return

        if use_print:
            print message
        else:
            _Message.show_info(title="debug", message=message)

    @staticmethod
    def _get_caller_name():
        """
        
        :return: Caller's caller, caller
        """
        stack = inspect.stack()
        caller_of_caller = stack[3][3]
        caller = stack[2][3]

        return caller_of_caller, caller


class _Shell(object):
    SUCCESS = 0
    FAILED = 1

    @staticmethod
    def execute_status(command):
        """
        Execute a command and return the return status
        :param command: "ls -l"
        :return: return status
        """
        params = command.split()
        status = subprocess.call(params)
        return status

    @staticmethod
    def execute_output(command):
        """
        Execute a command and return it's output
        :param command: "ls -l"
        :return:  the output of the shell command
        """
        output = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE).stdout.read()
        return output


class _FileDialog(object):
    @staticmethod
    def ask_open_filenames(*args, **kwargs):
        return tkFileDialog.askopenfilenames(*args, **kwargs)


class _Message(object):
    @staticmethod
    def show_warning(message):
        tkMessageBox.showwarning(message=message)

    @staticmethod
    def show_error(message):
        tkMessageBox.showerror(message=message)

    @staticmethod
    def show_info(message, *args, **kwargs):
        tkMessageBox.showinfo(message=message, *args, **kwargs)

    @staticmethod
    def ask_ok_cancel(message):
        return tkMessageBox.askokcancel(message=message)


class _ADBDeviceStatus(object):
    DEVICE = "device"
    OFFLINE = "offline"


class _ADB(object):
    @staticmethod
    def get_device_dict():
        """
        Get devices as a dict
        Also updates it's own copy of device dict
        
        :return:  {"device0": "device", "device1", "offline"}
        """
        device_dict = {}

        _ADB._start_server_exit_if_fail()

        """
        The output of "adb devices" would be: 
        List of devices attached
        device0\tdevice
        device1\toffline
        
        """
        adb_devices_output = _Shell.execute_output("adb devices")
        device_list = adb_devices_output.splitlines()[1: -1]

        if len(device_list) > 0:
            for line in device_list:
                device, status = line.split('\t')
                device_dict[device] = status

        _Debug.debug(device_dict)

        return device_dict

    @staticmethod
    def get_installed_packages(device, third_party=True, search=""):
        """
        
        :param device:
        :param third_party: 
        :param search: 
        :return: List of installed packages.
        """
        if _ADB._check_status(device):
            return

        t = "-3" if third_party else ""
        search = " | grep %s" % search if search else ""

        command = "adb -s %s shell 'pm list packages %s'%s" % (device, t, search)
        _Debug.debug(("command: ", command))
        packages_string = _Shell.execute_output(command)
        installed_packages = packages_string.splitlines()

        return installed_packages

    @staticmethod
    def install_packages(device, package_path_filename_list):
        """
        
        :return: 
        """
        if _ADB._check_status(device):
            return

        if not package_path_filename_list:
            _Message.show_warning("Cancelled!")
            return

        name_list = map(_ADB._extract_filename, package_path_filename_list)
        package_name_list_string = "    ".join(name_list)

        if not _Message.ask_ok_cancel("Install These Apps? %s" % package_name_list_string):
            _Message.show_info("Installation Cancelled.")
            return

        status_dict = {}
        for path_name in package_path_filename_list:
            status_dict[path_name] = _ADB._install_package(device, path_name)

        for path_name, status in status_dict.iteritems():
            name = _ADB._extract_filename(path_name)
            if status == _Shell.SUCCESS:
                _Message.show_info("%s Installed!" % name)
            if status == _Shell.FAILED:
                _Message.show_error("Installation failed: %s." % name)

    @staticmethod
    def uninstall_packages(device, package_list):
        """
        
        :return: 
        """
        if _ADB._check_status(device):
            return

        if len(package_list) == 0:
            _Message.show_warning("Please Select at Least One Package to Uninstall!")
            return

        package_list_string = "    ".join(package_list)
        if not _Message.ask_ok_cancel("Uninstall These Packages: %s?" % package_list_string):
            _Message.show_info("Uninstallation Cancelled.")
            return

        status_dict = {}
        for package in package_list:
            status_dict[package] = _ADB._uninstall_package(device, package)

        for package, status in status_dict.iteritems():
            if status == _Shell.SUCCESS:
                _Message.show_info("%s Uninstalled!" % package)
            if status == _Shell.FAILED:
                _Message.show_error("Uninstallation failed for %s!" % package)

    @staticmethod
    def _check_status(device):
        """
        Check if there is a device that _ADB holds as default transport.
        :return: True if device doesn't exit or is inoperable.
        """
        if device is None:
            _Message.show_error("Please Select One Device.")
            return True

        device_dict = _ADB.get_device_dict()
        if device not in device_dict:
            _Message.show_error("Device %s Doesn't Exist." % device)
            return True

        status = device_dict[device]
        if status == _ADBDeviceStatus.OFFLINE:
            _Message.show_error("%s is Offline!" % device)
            return True

        return False

    @staticmethod
    def _start_server():
        return _Shell.execute_status("adb start-server")

    @staticmethod
    def _start_server_exit_if_fail():
        exit_if_fail(_ADB._start_server(), "Couldn't start adb server.")

    @staticmethod
    def _extract_filename(full_path_name):
        _, name = os.path.split(full_path_name)
        return name

    @staticmethod
    def _install_package(device, full_path_name):
        """
        
        :param full_path_name: the full pathname of package to install: 
        :return: status of installation
        """
        replace_existing_package = "-r"
        command = "adb -s %s install %s %s" % (device, replace_existing_package, full_path_name)
        return _Shell.execute_status(command)

    @staticmethod
    def _uninstall_package(device, package_name):
        """
        
        :param package_name: the package to uninstall.
        :return: 
        TODO: The return code for adb uninstall doesn't work the way this intends it to, adb uninstall returns 0 even 
              if the uninstallation fails.
        """
        command = "adb -s %s uninstall %s" % (device, package_name)
        _Debug.debug((command, ))
        return _Shell.execute_status(command)


class _UI(object):
    LEFT = tk.LEFT
    BOTH = tk.BOTH

    W = tk.W
    E = tk.E

    FRAME = "frame"
    BUTTON = "button"
    LABEL = "label"
    MESSAGE = "message"
    LISTBOX = "listbox"
    ENTRY = "entry"
    TOPLEVEL = "toplevel"

    @staticmethod
    def create_below(name, master, *args, **kwargs):
        return _UI.create(name, master, side=None, *args, **kwargs)

    @staticmethod
    def create_left(name, master, *args, **kwargs):
        side = _UI.LEFT
        return _UI.create(name, master, side=side, *args, **kwargs)

    @staticmethod
    def create(name, master, side=None, *args, **kwargs):
        factory = _UI.get_factory(name)
        if factory is None:
            _Debug.debug("factory is None")
            return None

        widget = factory(master, *args, **kwargs)

        if name not in [_UI.TOPLEVEL]:    # toplevel widget doesn't have pack()
            widget.pack(side=side)

        return widget

    @staticmethod
    def get_factory(name):
        return {
            _UI.FRAME:      _UI.create_frame,
            _UI.BUTTON:     _UI.create_button,
            _UI.LABEL:      _UI.create_label,
            _UI.MESSAGE:    _UI.create_message,
            _UI.LISTBOX:    _UI.create_listbox,
            _UI.ENTRY:      _UI.create_entry,
            _UI.TOPLEVEL:   _UI.create_toplevel,
        }.get(name, None)

    @staticmethod
    def create_entry(master, *args, **kwargs):
        entry = tk.Entry(master, *args, **kwargs)

        return entry

    @staticmethod
    def create_message(master, *args, **kwargs):
        # text = ""
        # if "text" in kwargs:
        #     text = kwargs["text"]
        #     del kwargs["text"]

        message = tk.Message(master, *args, **kwargs)
        return message

    @staticmethod
    def create_frame(master, *args, **kwargs):
        frame = tk.Frame(master, borderwidth=3, padx=15, pady=15, *args, **kwargs)

        return frame

    @staticmethod
    def create_button(master, *args, **kwargs):
        text = ""
        command = None
        anchor = _UI.E

        if "text" in kwargs:
            text = kwargs["text"]
            del kwargs["text"]
        if "command" in kwargs:
            command = kwargs["command"]
            del kwargs["command"]
        if "anchor" in kwargs:
            anchor = kwargs["anchor"]
            del kwargs["anchor"]

        button = tk.Button(master, text=text, command=command, anchor=anchor, *args, **kwargs)
        button.pack(fill=_UI.BOTH)

        return button

    @staticmethod
    def create_label(master, *args, **kwargs):
        text = ""
        anchor = _UI.W

        if "text" in kwargs:
            text = kwargs["text"]
            del kwargs["text"]
        if "anchor" in kwargs:
            anchor = kwargs["anchor"]
            del kwargs["anchor"]

        label = tk.Label(master, text=text, anchor=anchor, *args, **kwargs)
        label.pack(fill=_UI.BOTH)

        return label

    @staticmethod
    def create_listbox(master, *args, **kwargs):
        selectmode = _ListBox.SINGLE
        width = 25
        if "selectmode" in kwargs:
            selectmode = kwargs["selectmode"]
            del kwargs["selectmode"]
        if "width" in kwargs:
            width = kwargs["width"]
            del kwargs["width"]

        listbox = _ListBox(master, *args, selectmode=selectmode, width=width, **kwargs)

        return listbox

    @staticmethod
    def create_toplevel(master, *args, **kwargs):
        title = ""
        if "title" in kwargs:
            title = kwargs["title"]
            del kwargs["title"]

        toplevel = tk.Toplevel(master, *args, **kwargs)
        toplevel.title(title)

        return toplevel


class _ListBox(tk.Listbox):
    SINGLE = tk.SINGLE
    MULTIPLE = tk.MULTIPLE

    def __init__(self, master, selectmode, *args, **kwargs):
        tk.Listbox.__init__(self, master, selectmode=selectmode, *args, **kwargs)
        self._selectmode = selectmode

    def update_options(self, options):
        self._delete_all_options()
        self._insert_options(options)
        self._select_default()

    def get_selections(self):
        """
        :return: a list of currently selected options
        """
        indices = self.curselection()
        if not indices:
            return []

        selections = [self.get(i) for i in indices]

        return selections

    def get_selection(self):
        assert self._selectmode == _ListBox.SINGLE

        selection = self.get_selections()
        if not selection:
            return None

        return selection[0]

    def _select_default(self):
        self.select_set(0)

    def _insert_options(self, options):
        if not options:
            return

        for i in options:
            self.insert(tk.END, i)

    def _delete_all_options(self):
        self.delete(0, tk.END)


class App(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)

        self.resizable(False, False)
        self.tk_setPalette("#ececec")

        x = (self.winfo_screenwidth() - self.winfo_reqwidth()) / 3
        y = (self.winfo_screenheight() - self.winfo_reqheight()) / 3

        self.geometry("+{}+{}".format(x, y))
        self.title("Android Device Manager")

        self._adb = _ADB()
        self._main_frame = _MainFrame(self)
        self._device_selection_manager = _DeviceSelectionManager(self._adb, self._main_frame.device_selection_frame)
        self._device_manager = _DeviceManager(self._main_frame.device_management_frame)

    def run(self):
        self.mainloop()


class _DeviceSelectionManager(object):
    def __init__(self, adb, device_selection_frame):
        self._adb = adb
        self._frame = device_selection_frame

        self._set_commands()
        self._refresh_device_list()

        # Solve the lost selection problem.
        self._frame.device_listbox.config(exportselection=False)

    def refresh_device_list(self):
        self._refresh_device_list()
        _Message.show_info("Device List Refreshed!")

    def _set_commands(self):
        self._frame.refresh_button.config(command=self.refresh_device_list)
        self._frame.select_button.config(command=self.create_package_management_frame)

    def create_package_management_frame(self):
        """
        Create package management frame if there is a device currently under selection.
        
        :return: 
        """
        device = self._get_selected_device()
        if not device:
            return

        self._create_package_management_frame(device)

    def _create_package_management_frame(self, device):
        if not device:
            return

        # TODO:
        frame = _PackageManagementFrame()
        packagemanager = _PackageManager(self._adb, frame, device)

    def _refresh_device_list(self):
        """
        We don't want the device refreshed message when this app starts up.
        :return: 
        """
        device_dict = self._adb.get_device_dict()

        options = []

        for device in device_dict:
            status = device_dict[device]
            options.append("{}    {}".format(device, status))

        _Debug.debug(("options: ", options))

        self._frame.device_listbox.update_options(options)

    def _get_selected_device(self):
        selection = self._frame.device_listbox.get_selection()

        if not selection:
            _Message.show_warning("Please Select a Device")
            _Debug.debug(("no selection",))
            return None

        device, _ = selection.split()

        _Debug.debug(("device: ", device))

        return device


class _Frame(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        tk.Frame.__init__(self, master, borderwidth=3, padx=15, pady=15, *args, **kwargs)
        self.pack()


class _FrameLeft(_Frame):
    def __init__(self, master, *args, **kwargs):
        _Frame.__init__(self, master, *args, **kwargs)
        self.pack(side=tk.LEFT)


class _DeviceManagementFrame(_FrameLeft):
    def __init__(self, master, *args, **kwargs):
        _FrameLeft.__init__(self, master, *args, **kwargs)
        _UI.create(_UI.LABEL, self, text="Device Management")
        _UI.create(_UI.LABEL, self)
        self.create_template_button = _UI.create(_UI.BUTTON, self, text="Create Template")
        self.run_template_button = _UI.create(_UI.BUTTON, self, text="Run template")
        self.reboot_device_button = _UI.create(_UI.BUTTON, self, text="Reboot device")


class _DeviceManager(object):
    CONFIG_FILE = "VMMANAGER.CONF"

    CREATE_TEMPLATE = "0xA1\n"
    RUN_TEMPLATE = "0xA2\n"

    REBOOT_DEVICE = "0xAF\n"

    def __init__(self, device_management_frame):
        self._frame = device_management_frame

        self._set_commands()

    def _set_commands(self):
        self._frame.create_template_button.config(command=self.create_template)
        self._frame.run_template_button.config(command=self.run_template)
        self._frame.reboot_device_button.config(command=self.reboot_device)

    @staticmethod
    def _open_and_write(name, data):
        r = open(name, "w")
        r.write(data)
        r.close()

    def create_template(self):
        self._open_and_write(_DeviceManager.CONFIG_FILE, _DeviceManager.CREATE_TEMPLATE)

    def run_template(self):
        self._open_and_write(_DeviceManager.CONFIG_FILE, _DeviceManager.RUN_TEMPLATE)

    def reboot_device(self):
        self._open_and_write(_DeviceManager.CONFIG_FILE, _DeviceManager.REBOOT_DEVICE)


class _DeviceSelectionFrame(_FrameLeft):
    def __init__(self, master, *args, **kwargs):
        _FrameLeft.__init__(self, master, *args, **kwargs)

        master = _UI.create(_UI.FRAME, self)
        _UI.create(_UI.LABEL, master, text="Package Management")
        _UI.create(_UI.LABEL, master)

        _UI.create(_UI.LABEL, master, text="List of Devices", anchor=None)
        _UI.create(_UI.LABEL, master, text="Devices     Status    ")
        self.device_listbox = _UI.create(_UI.LISTBOX, master)

        master = _UI.create(_UI.FRAME, self)
        self.select_button = _UI.create_left(_UI.BUTTON, master, text="Select")
        self.refresh_button = _UI.create_left(_UI.BUTTON, master, text="Refresh")


class _Toplevel(tk.Toplevel):
    def __init__(self, master, *args, **kwargs):
        tk.Toplevel.__init__(self, master, *args, **kwargs)


class _PackageManagementFrame(_Toplevel):
    def __init__(self, *args, **kwargs):
        _Toplevel.__init__(self, None, *args, **kwargs)
        self.title("Package Manager")

        master = _UI.create(_UI.FRAME, self)
        self.installed_package_listbox = _UI.create(_UI.LISTBOX, master, selectmode=_ListBox.MULTIPLE, width=50)

        master = _UI.create(_UI.FRAME, self)
        self.search_box = _UI.create_left(_UI.ENTRY, master)
        self.search_button = _UI.create_left(_UI.BUTTON, master, text="Search")

        master = _UI.create(_UI.FRAME, self)
        self.refresh_button = _UI.create_left(_UI.BUTTON, master, text="Refresh Installed Package List")
        self.install_button = _UI.create_left(_UI.BUTTON, master, text="Install")
        self.uninstall_button = _UI.create_left(_UI.BUTTON, master, text="Uninstall")


class _PackageManager(object):
    def __init__(self, adb, package_management_frame, device):
        self._adb = adb
        self._frame = package_management_frame
        self._device = device

        self._set_commands()

        self._refresh_installed_package_list()

        self._frame.search_box.focus_set()
        self._frame.search_button.bind("<Return>", self.search)

    def _set_commands(self):
        self._frame.refresh_button.config(command=self.refresh_installed_package_list)
        self._frame.install_button.config(command=self.install_packages)
        self._frame.uninstall_button.config(command=self.uninstall_packages)
        self._frame.search_button.config(command=self.search)

    def search(self):
        search_phrase = self._frame.search_box.get()
        if not search_phrase:
            return

        self._refresh_installed_package_list(True, search_phrase)

    def uninstall_packages(self):
        device = self._device

        if not device:
            return

        package_list = self._frame.installed_package_listbox.get_selections()

        self._adb.uninstall_packages(device, package_list)

    def install_packages(self):
        initialdir = "netdisk/app-files"
        device = self._device

        if not device:
            return

        package_path_filename_list = _FileDialog.ask_open_filenames(initialdir=initialdir)
        self._adb.install_packages(device, package_path_filename_list)

    def refresh_installed_package_list(self):
        if not self._device:
            return
        self._refresh_installed_package_list()
        _Message.show_info("Installed Package List Refreshed!")

    def _refresh_installed_package_list(self, third_party=True, search=""):
        if not self._device:
            return

        installed_package_list = self._adb.get_installed_packages(self._device, third_party, search)
        _Debug.debug(("installed_package_list[0: 3]: ", installed_package_list[0: 3]))

        self._frame.installed_package_listbox.update_options(installed_package_list)


class _MainFrame(object):
    def __init__(self, master):

        self._frame = _UI.create(_UI.FRAME, master)

        self.device_management_frame = _DeviceManagementFrame(self._frame)
        self.device_selection_frame = _DeviceSelectionFrame(self._frame)

        self.debug_button = None

        self._init_frames()

    def _init_frames(self):
        self._init_debug_frame()

    def _init_debug_frame(self):
        if not _Debug.DEBUG:
            return

        def __debug():
            pass

        debug_frame = _UI.create_left(_UI.FRAME, self._frame)
        self.debug_button = _UI.create(_UI.BUTTON, debug_frame, text="Debug", command=__debug)


def main():
    app = App()
    app.run()

if __name__ == "__main__":
    main()
