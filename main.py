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
    def __init__(self):
        self._device_dict = {}
        self._device = None
        self._uninstallation_window = None

        self.get_device_dict()
        self._device, self._status = self._get_one_device_status()

    def get_device_dict(self):
        """
        Get devices as a dict
        Also updates it's own copy of device dict
        
        :return:  {"device0": "device", "device1", "offline"}
        """
        _ADB._start_server_exit_if_fail()

        adb_devices_output = _Shell.execute_output("adb devices")

        """
        The output of "adb devices" would be: 
        List of devices attached
        device0\tdevice
        device1\toffline
        
        """
        device_list = adb_devices_output.splitlines()[1: -1]

        self._device_dict = {}

        if len(device_list) > 0:
            for line in device_list:
                device, status = line.split('\t')
                self._device_dict[device] = status

        _Debug.debug(self._device_dict)

        return self._device_dict

    def get_installed_packages(self, third_party=True, search=""):
        """
        
        :param third_party: 
        :param search: 
        :return: List of installed packages.
        """
        if self._check_status():
            return

        t = "-3" if third_party else ""
        search = " | grep %s" % search if search else ""

        command = "adb -s %s shell 'pm list packages %s'%s" % (self._device, t, search)
        _Debug.debug(("command: ", command))
        packages_string = _Shell.execute_output(command)
        packages = packages_string.splitlines()

        return packages

    def install_packages(self, package_path_filename_list):
        """
        
        :return: 
        """
        if self._check_status():
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
            status_dict[path_name] = self._install_package(path_name)

        for path_name, status in status_dict.iteritems():
            name = _ADB._extract_filename(path_name)
            if status == _Shell.SUCCESS:
                _Message.show_info("%s Installed!" % name)
            if status == _Shell.FAILED:
                _Message.show_error("Installation failed: %s." % name)

    def uninstall_packages(self, package_list):
        """
        
        :return: 
        """
        if self._check_status():
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
            status_dict[package] = self._uninstall_package(package)

        for package, status in status_dict.iteritems():
            if status == _Shell.SUCCESS:
                _Message.show_info("%s Uninstalled!" % package)
            if status == _Shell.FAILED:
                _Message.show_error("Uninstallation failed for %s!" % package)

    def set_device(self, device):
        if device is None:
            self._device = None
            _Debug.debug(("device is None.",))
            return

        self.get_device_dict()
        if device in self._device_dict:
            self._device = device
            self._status = self._device_dict[device]
            _Debug.debug(("self._device, self._status = ", self._device, self._status))

    def _check_status(self):
        """
        Check if there is a device that _ADB holds as default transport.
        :return: True if device doesn't exit or is inoperable.
        """
        if self._device is None:
            _Message.show_error("Please Select One Device.")
            return True

        if self._device not in self._device_dict.keys():
            _Message.show_error("Device %s disconnected." % self._device)
            return True

        if self._device_dict[self._device] == _ADBDeviceStatus.OFFLINE:
            _Message.show_error("%s is Offline!" % self._device)
            return True

        return False

    @staticmethod
    def _start_server():
        return _Shell.execute_status("adb start-server")

    @staticmethod
    def _start_server_exit_if_fail():
        exit_if_fail(_ADB._start_server(), "Couldn't start adb server.")

    def _get_one_device_status(self):
        """
        Get the first device in the device list.
        :return: the first device, None if device list is empty
        """
        device_dict = self._device_dict
        if len(device_dict) == 0:
            return None, None

        device = device_dict.keys()[0]
        status = device_dict[device]

        return device, status

    @staticmethod
    def _extract_filename(full_path_name):
        _, name = os.path.split(full_path_name)
        return name

    def _install_package(self, full_path_name):
        """
        
        :param full_path_name: the full pathname of package to install: 
        :return: status of installation
        """
        replace_existing_package = "-r"
        command = "adb -s %s install %s %s" % (self._device, replace_existing_package, full_path_name)
        return _Shell.execute_status(command)

    def _uninstall_package(self, package_name):
        """
        
        :param package_name: the package to uninstall.
        :return: 
        TODO: The return code for adb uninstall doesn't work the way this intends it to, adb uninstall returns 0 even 
              if the uninstallation fails.
        """
        command = "adb -s %s uninstall %s" % (self._device, package_name)
        return _Shell.execute_status(command)


class _UI(object):
    LEFT = tk.LEFT
    BOTH = tk.BOTH

    W = tk.W
    E = tk.E

    FRAME = "frame"
    BUTTON = "button"
    LABEL = "label"
    LISTBOX = "listbox"
    ENTRY = "entry"
    TOPLEVEL = "toplevel"

    @staticmethod
    def create_below(name, master, *args, **kwargs):
        return _UI.create(name, master, side=None, *args, **kwargs)

    @staticmethod
    def create_right(name, master, *args, **kwargs):
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
            _UI.LISTBOX:    _UI.create_listbox,
            _UI.ENTRY:      _UI.create_entry,
            _UI.TOPLEVEL:   _UI.create_toplevel,
        }.get(name, None)

    @staticmethod
    def create_entry(master, *args, **kwargs):
        entry = tk.Entry(master, *args, **kwargs)

        return entry

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
            selectmode = kwargs["width"]
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
        self.title("Android Devices Manager")

        self._adb = _ADB()
        self._main_frame = _MainFrame(self)
        self._app_manager = _ApplicationManager(self._adb, self._main_frame)

    def run(self):
        self.mainloop()


class DeviceListBoxManager(object):
    def __init__(self, adb, device_listbox, refresh_button):
        self._adb = adb
        self._device_listbox = device_listbox
        self._refresh_button = refresh_button

        self._set_command()

    def selected_device(self):
        return None

    def _set_command(self):
        pass


class _ApplicationManager(object):
    def __init__(self, adb, mainwindow):
        self._adb = adb
        self._window = mainwindow

        self._set_commands()

        self._refresh_device_list()

    def install_packages(self):
        initialdir = "netdisk/app-files"
        self._get_and_set_device()
        package_path_filename_list = _FileDialog.ask_open_filenames(initialdir=initialdir)
        self._adb.install_packages(package_path_filename_list)

    def uninstall_packages(self):
        self._get_and_set_device()
        self._window.create_uninstallation_frame()
        self._window.uninstallation_frame.protocol('WM_DELETE_WINDOW', lambda: None)    # disable x button

        self._refresh_installed_package_list()

        self._set_uninstallation_commands()

        self._adb.uninstall_packages(["qq", "wechat"])
        self._window.uninstallation_frame = None

    def refresh_device_list(self):
        self._refresh_device_list()
        _Message.show_info("Device List Refreshed!")

    def refresh_installed_package_list(self):
        self._refresh_installed_package_list()
        _Message.show_info("Installed Package List Refreshed!")

    def _set_uninstallation_commands(self):
        self._window.refresh_installed_package_list_button.config(command=self.refresh_installed_package_list)

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

        self._window.device_listbox.update_options(options)

    def _refresh_installed_package_list(self):
        installed_package_list = self._adb.get_installed_packages()
        _Debug.debug(("installed_package_list[0: 3]: ", installed_package_list[0: 3]))

        self._window.installed_package_listbox.update_options(installed_package_list)

    def _set_commands(self):
        self._window.install_packages_button.config(command=self.install_packages)
        self._window.uninstall_packages_button.config(command=self.uninstall_packages)
        self._window.refresh_device_list_button.config(command=self.refresh_device_list)

    def _get_and_set_device(self):
        """
        Get the currently selected device from self._vm_list_box and
        call self._adb.set_device with it.
        :return:  None
        """
        device = self._get_selected_device()
        self._adb.set_device(device)

    def _get_selected_device(self):
        selection = self._window.device_listbox.get_selection()

        if not selection:
            _Debug.debug(("no selection",))
            return None

        device, _ = selection.split()

        _Debug.debug(("device: ", device))

        return device


class _MainFrame(object):
    def __init__(self, master):

        self._main_frame = _UI.create(_UI.FRAME, master)

        self.create_template_button = None
        self.run_template_button = None
        self.reboot_device_button = None

        self.install_packages_button = None
        self.uninstall_packages_button = None
        self.refresh_device_list_button = None
        self.device_listbox = None

        self.uninstallation_frame = None

        self.debug_button = None

        self._init_frames()

    def _init_frames(self):
        self._init_device_management_frame()
        self._init_package_management_frame()
        self._init_debug_frame()

    def _init_debug_frame(self):
        if not _Debug.DEBUG:
            return

        def __debug():
            print self.uninstallation_frame
            self.uninstallation_frame.destroy()
            print self.uninstallation_frame

        debug_frame = _UI.create_right(_UI.FRAME, self._main_frame)
        self.debug_button = _UI.create(_UI.BUTTON, debug_frame, text="Debug", command=__debug)

    def _init_device_management_frame(self):
        device_management_frame = _UI.create_right(_UI.FRAME, self._main_frame)
        master = device_management_frame

        _UI.create(_UI.LABEL, master, text="Device Management")
        _UI.create(_UI.LABEL, master)

        self.create_template_button = _UI.create(_UI.BUTTON, master, text="Create Template")
        self.run_template_button = _UI.create(_UI.BUTTON, master, text="Run Template")
        self.reboot_device_button = _UI.create(_UI.BUTTON, master, text="Reboot Device")

    def _init_package_management_frame(self):
        package_management_frame = _UI.create_right(_UI.FRAME, self._main_frame)

        button_frame = _UI.create_right(_UI.FRAME, package_management_frame)
        master = button_frame

        _UI.create(_UI.LABEL, master, text="Package Management")
        _UI.create(_UI.LABEL, master)

        self.install_packages_button = _UI.create(_UI.BUTTON, master, text="Install Packages")
        self.uninstall_packages_button = _UI.create(_UI.BUTTON, master, text="Uninstall Packages")

        self.refresh_device_list_button = _UI.create(_UI.BUTTON, master, text="Refresh Device List")

        device_list_frame = _UI.create_right(_UI.FRAME, package_management_frame)
        master = device_list_frame

        _UI.create(_UI.LABEL, master, text="List of Devices", anchor=None)
        _UI.create(_UI.LABEL, master, text="Devices     Status    ")
        self.device_listbox = _UI.create(_UI.LISTBOX, master)

    def create_uninstallation_frame(self):
        self.uninstallation_frame = _UI.create(_UI.TOPLEVEL, None, title="Please Select Some Packages to Uninstall.")

        search_frame = _UI.create(_UI.FRAME, self.uninstallation_frame)
        master = search_frame

        self.search_installed_package_input_box = _UI.create_right(_UI.ENTRY, master)
        self.search_installed_package_button = _UI.create_right(_UI.BUTTON, master, text="Search")

        installed_apps_frame = _UI.create(_UI.FRAME, self.uninstallation_frame)
        master = installed_apps_frame

        _UI.create(_UI.LABEL, master, text="Packages Installed: ")
        self.installed_package_listbox = _UI.create(_UI.LISTBOX, master, selectmode=_ListBox.MULTIPLE)

        buttons_frame = _UI.create(_UI.FRAME, self.uninstallation_frame)
        master = buttons_frame

        self.confirm_uninstallation_button = _UI.create_right(_UI.BUTTON, master, text="Confirm")
        self.refresh_installed_package_list_button = _UI.create_right(_UI.BUTTON, master, text="Refresh")
        self.exit_uninstallation_frame_button =    _UI.create_right(_UI.BUTTON, master, text="Exit", command=self.uninstallation_frame.destroy)


def main():
    app = App()
    app.run()

if __name__ == "__main__":
    main()
