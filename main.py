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


def _exit_if_fail(status, message):
    if status == 0:
        return

    _Message.show_error(message)
    exit(1)


class _Debug(object):
    DEBUG = True

    @staticmethod
    def debug(*args, **kwargs):
        use_print = True
        if "use_print" in kwargs:
            use_print = kwargs["use_print"]
            del kwargs["use_print"]

        message = "In %s : " % _Debug._get_caller_name()
        message += " ".join(map(repr, args))
        if not _Debug.DEBUG:
            return

        if use_print:
            print message
        else:
            _Message.show_info(title="debug", message=message)

    @staticmethod
    def _get_caller_name():
        return inspect.stack()[2][3]


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
        _exit_if_fail(_ADB._start_server(), "Couldn't start adb server.")

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

    def install_applications(self):
        """
        
        :return: 
        """
        initialdir = "netdisk/app-files"

        if self._check_status():
            return

        app_list = _FileDialog.ask_open_filenames(initialdir=initialdir)

        if len(app_list) == 0:
            _Message.show_warning("Please Select At Least One App to Install!")
            return

        name_list = map(_ADB._extract_name, app_list)
        app_name_list_string = "    ".join(name_list)

        if not _Message.ask_ok_cancel("Install These Apps? %s" % app_name_list_string):
            _Message.show_info("Installation Cancelled.")
            return

        status_dict = {}
        for path_name in app_list:
            status_dict[path_name] = self._install_application(path_name)

        for path_name, status in status_dict.iteritems():
            name = _ADB._extract_name(path_name)
            if status == _Shell.SUCCESS:
                _Message.show_info("%s Installed!" % name)
            if status == _Shell.FAILED:
                _Message.show_error("Installation failed: %s." % name)

    @staticmethod
    def _extract_name(full_path_name):
        _, name = os.path.split(full_path_name)
        return name

    def _install_application(self, full_path_name):
        """
        
        :param full_path_name: the full pathname of app to install: 
        :return: status of installation
        """
        replace_existing_app = "-r"
        command = "adb -s %s install %s %s" % (self._device, replace_existing_app, full_path_name)
        return _Shell.execute_status(command)

    def _uninstall_application(self, package_name):
        """
        
        :param package_name: the package to uninstall.
        :return: 
        TODO: The return code for adb uninstall doesn't work the way this intends it to, adb uninstall returns 0 even 
              if the uninstallation fails.
        """
        command = "adb -s %s uninstall %s" % (self._device, package_name)
        return _Shell.execute_status(command)

    def create_uninstallation_window(self):
        window = _UI.create(_UI.TOPLEVEL, None, title="Please Select Some Apps to Uninstall.")

        return window

    def uninstall_applications(self):
        """
        
        :return: 
        """
        if self._check_status():
            return

        uninstallation_window = self.create_uninstallation_window()

        app_list = ["qq", "wechat"]

        if len(app_list) == 0:
            _Message.show_warning("Please Select at Least One App to Uninstall!")
            return

        app_list_string = "    ".join(app_list)
        if not _Message.ask_ok_cancel("Uninstall These Apps: %s?" % app_list_string):
            _Message.show_info("Uninstallation Cancelled.")
            return

        status_dict = {}
        for app in app_list:
            status_dict[app] = self._uninstall_application(app)

        for app, status in status_dict.iteritems():
            if status == _Shell.SUCCESS:
                _Message.show_info("%s Uninstalled!" % app)
            if status == _Shell.FAILED:
                _Message.show_error("Uninstallation failed for %s!" % app)

    def set_device(self, device):
        if device is None:
            self._device = None
            return

        self.get_device_dict()
        if device in self._device_dict:
            self._device = device
            self._status = self._device_dict[device]

    def get_device(self):
        return self._device


class _UI(object):
    LEFT = tk.LEFT
    BOTH = tk.BOTH

    FRAME = "frame"
    BUTTON = "button"
    LABEL = "label"
    LISTBOX = "listbox"
    VM_LISTBOX = "vm_listbox"
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
            _UI.VM_LISTBOX: _UI.create_vm_listbox,
            _UI.TOPLEVEL:   _UI.create_toplevel,
        }.get(name, None)

    @staticmethod
    def create_frame(master, *args, **kwargs):
        frame = tk.Frame(master, borderwidth=3, padx=15, pady=15, *args, **kwargs)

        return frame

    @staticmethod
    def create_button(master, *args, **kwargs):
        text = ""
        command = None
        if "text" in kwargs:
            text = kwargs["text"]
            del kwargs["text"]
        if "command" in kwargs:
            command = kwargs["command"]
            del kwargs["command"]

        button = tk.Button(master, text=text, command=command, anchor='e', *args, **kwargs)
        button.pack(fill=_UI.BOTH)

        return button

    @staticmethod
    def create_label(master, *args, **kwargs):
        text = ""
        if "text" in kwargs:
            text = kwargs["text"]
            del kwargs["text"]

        label = tk.Label(master, text=text, *args, **kwargs)
        label.pack()

        return label

    @staticmethod
    def create_listbox(master):
        pass

    @staticmethod
    def create_toplevel(master, *args, **kwargs):
        title = ""
        if "title" in kwargs:
            title = kwargs["title"]
            del kwargs["title"]

        toplevel = tk.Toplevel(master, *args, **kwargs)
        toplevel.title(title)

        return toplevel

    @staticmethod
    def create_vm_listbox(master, *args, **kwargs):
        adb = None
        if "adb" in kwargs:
            adb = kwargs["adb"]
            del kwargs["adb"]
        vm_listbox = _VMListBox(master, adb=adb, *args, **kwargs)

        return vm_listbox


class _ListBox(tk.Listbox):
    SINGLE = tk.SINGLE
    MULTIPLE = tk.MULTIPLE

    def __init__(self, master, *args, **kwargs):
        tk.Listbox.__init__(self, master, *args, **kwargs)

    def _insert_options(self, options):
        if len(options) == 0:
            return

        for i in options:
            self.insert(tk.END, i)

    def update_options(self, options):
        self._delete_all_options()
        self._insert_options(options)

    def _delete_all_options(self):
        self.delete(0, tk.END)


class _VMListBox(_ListBox):
    def __init__(self, master, adb, selectmode=_ListBox.SINGLE, width=35):
        _ListBox.__init__(self, master=master, selectmode=selectmode)
        self.config(width=width)

        self._adb = adb

        self.update_device_list()
        self.pack()

    def get_selected_device(self):
        i = self.get(tk.ACTIVE)
        try:
            device, _ = i.split()
        except ValueError:
            device = None
        _Debug.debug(("device: ", device))
        return device

    def update_device_list(self):
        self._delete_all_options()
        device_dict = self._adb.get_device_dict()
        if len(device_dict) == 0:
            return

        options = []
        for device in device_dict:
            status = device_dict[device]
            options.append("{}    {}".format(device, status))

        _Debug.debug(("options: ", options))

        self._insert_options(options)


class _App(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)

        self.resizable(False, False)
        self.tk_setPalette("#ececec")

        x = (self.winfo_screenwidth() - self.winfo_reqwidth()) / 3
        y = (self.winfo_screenheight() - self.winfo_reqheight()) / 3

        self.geometry("+{}+{}".format(x, y))
        self.title("VM    Manager")

        self._main_controller = _ControllerADBMain()
        self._adb = _ADB()
        self._main_window = _MainWindow(self, self._adb)

    def run(self):
        self.mainloop()


class _ControllerADBMain(object):
    def __init__(self):
        pass


class _MainWindow(object):
    def __init__(self, master, adb):
        self._adb = adb

        self._main_frame = _UI.create(_UI.FRAME, master)

        self._button_frame = _UI.create_right(_UI.FRAME, self._main_frame)
        self._vm_list_frame = _UI.create_right(_UI.FRAME, self._main_frame, relief="sunken")
        self._vm_list_box = None
        self._uninstall_frame = None

        self.create_frames()

    def create_frames(self):
        self.create_button_frame()
        self.create_vm_list_frame()

    def create_button_frame(self):
        template = _UI.create(_UI.FRAME, self._button_frame)
        _UI.create(_UI.BUTTON, template, text="Create Template", command=self.create_template)
        _UI.create(_UI.BUTTON, template, text="Start Template", command=self.start_template)
        _UI.create(_UI.BUTTON, template, text="Reboot Virtual Machine(s)", command=self.reboot_vms)

        in_uninstall = _UI.create(_UI.FRAME, self._button_frame)
        _UI.create(_UI.BUTTON, in_uninstall, text="Install App(s)", command=self.install_applications)
        _UI.create(_UI.BUTTON, in_uninstall, text="Uninstall App(s)", command=self.uninstall_applications)

        refresh_device = _UI.create(_UI.FRAME, self._button_frame)
        _UI.create(_UI.BUTTON, refresh_device, text="Refresh Devices List", command=self.refresh_device_list)

    def create_vm_list_frame(self):
        _UI.create(_UI.LABEL, self._vm_list_frame, text="    List of VMs      ")
        _UI.create(_UI.LABEL, self._vm_list_frame, text="Devices            Status    ")
        self._vm_list_box = _UI.create(_UI.VM_LISTBOX, self._vm_list_frame, adb=self._adb)

    def create_template(self):
        pass

    def start_template(self):
        pass

    def reboot_vms(self):
        pass

    def install_applications(self):
        self._get_and_set_device()
        self._adb.install_applications()

    def uninstall_applications(self):
        self._get_and_set_device()
        self._adb.uninstall_applications()

    def refresh_device_list(self):
        self._vm_list_box.update_device_list()
        _Message.show_info("VM List Refreshed!")

    def _get_and_set_device(self):
        """
        Get the currently selected device from self._vm_list_box and
        call self._adb.set_device with it.
        :return:  None
        """
        device = self._vm_list_box.get_selected_device()
        self._adb.set_device(device)


if __name__ == "__main__":

    app = _App()
    app.run()
