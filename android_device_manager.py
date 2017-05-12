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
import tkFont
import subprocess
import inspect


def exit_if_fail(status, message):
    success = 0

    if status == success:
        return

    Message.show_error(message)
    sys.exit(1)


class Debug(object):
    DEBUG = True if '-d' in sys.argv[:] else False

    @staticmethod
    def debug(*args, **kwargs):
        use_print = True
        if "use_print" in kwargs:
            use_print = kwargs["use_print"]
            del kwargs["use_print"]

        message = "%s: %s: " % Debug._get_caller_name()
        message += " ".join(map(repr, *args))
        if not Debug.DEBUG:
            return

        if use_print:
            print message
        else:
            Message.show_info(title="debug", message=message)

    @staticmethod
    def _get_caller_name():
        """
        
        :return: Caller's caller, caller
        """
        stack = inspect.stack()
        caller_of_caller = stack[3][3]
        caller = stack[2][3]

        return caller_of_caller, caller


class Shell(object):
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


class FileDialog(object):
    @staticmethod
    def ask_open_filenames(*args, **kwargs):
        return tkFileDialog.askopenfilenames(*args, **kwargs)


class Message(object):
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


class ADBDeviceStatus(object):
    DEVICE = "device"
    OFFLINE = "offline"


class ADB(object):
    """
    A simple wrapper of adb commands
    """
    @staticmethod
    def get_device_dict():
        """
        Get devices as a dict
        Also updates it's own copy of device dict
        
        :return:  {"device0": "device", "device1", "offline"}
        """
        device_dict = {}

        ADB._start_server_exit_if_fail()

        """
        The output of "adb devices" would be: 
        List of devices attached
        device0\tdevice
        device1\toffline
        
        """
        adb_devices_output = Shell.execute_output("adb devices")
        device_list = adb_devices_output.splitlines()[1: -1]

        if len(device_list) > 0:
            for line in device_list:
                device, status = line.split('\t')
                device_dict[device] = status

        Debug.debug(device_dict)

        return device_dict

    @staticmethod
    def get_installed_package_list(device, third_party=True, search=""):
        """
        
        :param device:
        :param third_party: whether or not only includes third party apps
        :param search: filter result with " | grep search"
        :return: List of installed packages.
        """
        if ADB._check_status(device):
            return

        t = "-3" if third_party else ""
        search = " | grep %s" % search if search else ""

        command = "adb -s %s shell 'pm list packages %s'%s" % (device, t, search)
        Debug.debug(("command: ", command))
        packages_string = Shell.execute_output(command)
        """ The original output is in this form:
        package:com.chessking.android.learn.ctart4
        package:com.netease.cloudmusic
        package:tv.danmaku.bili
        """
        packages_string = packages_string.replace("package:", "")
        installed_package_list = packages_string.splitlines()

        return installed_package_list

    @staticmethod
    def install_packages(device, package_path_filename_list):
        """
        
        :return: 
        """
        if ADB._check_status(device):
            return

        if not package_path_filename_list:
            Message.show_warning("Cancelled!")
            return

        name_list = map(ADB._extract_filename, package_path_filename_list)
        package_name_list_string = "    ".join(name_list)

        if not Message.ask_ok_cancel("Install These Apps? %s" % package_name_list_string):
            Message.show_info("Installation Cancelled.")
            return

        status_dict = {}
        for path_name in package_path_filename_list:
            status_dict[path_name] = ADB._install_package(device, path_name)

        success_list = []
        failure_list = []

        for path_name, status in status_dict.iteritems():
            name = ADB._extract_filename(path_name)
            if status == Shell.SUCCESS:
                success_list.append(name)
            if status == Shell.FAILED:
                failure_list.append(name)

        success_list_string = " ".join(success_list)
        if success_list_string:
            Message.show_info("%s Installed!" % success_list_string)

        failure_list_string = " ".join(failure_list)
        if failure_list_string:
            Message.show_error("Installation Failed for These Apps: %s" % failure_list_string)

    @staticmethod
    def uninstall_packages(device, package_list):
        """
        
        :return: 
        """
        if ADB._check_status(device):
            return

        if len(package_list) == 0:
            Message.show_warning("Please Select at Least One Package to Uninstall!")
            return

        package_list_string = "    ".join(package_list)
        if not Message.ask_ok_cancel("Uninstall These Packages: %s?" % package_list_string):
            Message.show_info("Uninstallation Cancelled.")
            return

        status_dict = {}
        for package in package_list:
            status_dict[package] = ADB._uninstall_package(device, package)

        success_list = []
        failure_list = []

        for package, status in status_dict.iteritems():
            if status == Shell.SUCCESS:
                success_list.append(package)
            if status == Shell.FAILED:
                failure_list.append(package)

        success_list_string = " ".join(success_list)
        if success_list_string:
            Message.show_info("%s Uninstalled!" % success_list_string)

        failure_list_string = " ".join(failure_list)
        if failure_list_string:
            Message.show_error("Uninstallation Failed for These Packages: %s" % failure_list_string)

    @staticmethod
    def _check_status(device):
        """
        Check if device exists and whether is operable.
        :return: True if device doesn't exit or is inoperable.
        """
        if device is None:
            Message.show_error("No Device Selected.")
            return True

        device_dict = ADB.get_device_dict()
        if device not in device_dict:
            Message.show_error("Device %s Doesn't Exist." % device)
            return True

        status = device_dict[device]
        if status == ADBDeviceStatus.OFFLINE:
            Message.show_error("%s is Offline!" % device)
            return True

        return False

    @staticmethod
    def _start_server():
        return Shell.execute_status("adb start-server")

    @staticmethod
    def _start_server_exit_if_fail():
        exit_if_fail(ADB._start_server(), "Couldn't start adb server.")

    @staticmethod
    def _extract_filename(full_path_name):
        """
        Extract out the path of pathname
        :param full_path_name: 
        :return: google.apk with input /home/Download/google.apk
        """
        name = os.path.basename(full_path_name)
        return name

    @staticmethod
    def _install_package(device, full_path_name):
        """
        
        :param full_path_name: the full pathname of package to install: 
        :return: status of installation
        """
        replace_existing = "-r"
        command = "adb -s %s install %s %s" % (device, replace_existing, full_path_name)
        return Shell.execute_status(command)

    @staticmethod
    def _uninstall_package(device, package_name):
        """
        
        :param package_name: the package to uninstall.
        :return: 
        TODO: The return code for adb uninstall doesn't work the way this intends it to, adb uninstall returns 0 even 
              if the uninstallation fails.
        """
        command = "adb -s %s uninstall %s" % (device, package_name)
        Debug.debug((command,))
        return Shell.execute_status(command)


class UI(object):
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
        return UI.create(name, master, side=None, *args, **kwargs)

    @staticmethod
    def create_left(name, master, *args, **kwargs):
        side = UI.LEFT
        return UI.create(name, master, side=side, *args, **kwargs)

    @staticmethod
    def create(name, master, side=None, *args, **kwargs):
        factory = UI.get_factory(name)
        if factory is None:
            Debug.debug("factory is None")
            return None

        widget = factory(master, *args, **kwargs)

        if name not in [UI.TOPLEVEL]:    # toplevel widget doesn't have pack()
            widget.pack(side=side)

        return widget

    @staticmethod
    def get_factory(name):
        return {
            UI.FRAME:      UI.create_frame,
            UI.BUTTON:     UI.create_button,
            UI.LABEL:      UI.create_label,
            UI.MESSAGE:    UI.create_message,
            UI.LISTBOX:    UI.create_listbox,
            UI.ENTRY:      UI.create_entry,
            UI.TOPLEVEL:   UI.create_toplevel,
        }.get(name, None)

    @staticmethod
    def create_entry(master, *args, **kwargs):
        entry = tk.Entry(master, *args, **kwargs)

        return entry

    @staticmethod
    def create_message(master, *args, **kwargs):
        message = tk.Message(master, *args, **kwargs)
        return message

    @staticmethod
    def create_frame(master, *args, **kwargs):
        borderwidth = 3
        padx = 0
        pady = 0

        if "borderwidth" in kwargs:
            borderwidth = kwargs["borderwidth"]
            del kwargs["borderwidth"]
        if "padx" in kwargs:
            padx = kwargs["padx"]
            del kwargs["padx"]
        if "pady" in kwargs:
            pady = kwargs["pady"]
            del kwargs["pady"]

        frame = tk.Frame(master, borderwidth=borderwidth, padx=padx, pady=pady, *args, **kwargs)

        return frame

    @staticmethod
    def create_button(master, *args, **kwargs):
        text = ""
        command = None
        anchor = UI.E
        padx = 15
        pady = 6

        if "text" in kwargs:
            text = kwargs["text"]
            del kwargs["text"]
        if "command" in kwargs:
            command = kwargs["command"]
            del kwargs["command"]
        if "anchor" in kwargs:
            anchor = kwargs["anchor"]
            del kwargs["anchor"]
        if "padx" in kwargs:
            padx = kwargs["padx"]
            del kwargs["padx"]
        if "pady" in kwargs:
            pady = kwargs["pady"]
            del kwargs["pady"]

        button = tk.Button(master, text=text, command=command, anchor=anchor, padx=padx, pady=pady, *args, **kwargs)
        button.pack(fill=UI.BOTH)

        return button

    @staticmethod
    def create_label(master, *args, **kwargs):
        text = ""
        anchor = UI.W

        if "text" in kwargs:
            text = kwargs["text"]
            del kwargs["text"]
        if "anchor" in kwargs:
            anchor = kwargs["anchor"]
            del kwargs["anchor"]

        label = tk.Label(master, text=text, anchor=anchor, *args, **kwargs)
        label.pack(fill=UI.BOTH)

        return label

    @staticmethod
    def create_listbox(master, *args, **kwargs):
        selectmode = ListBox.SINGLE
        width = 25
        if "selectmode" in kwargs:
            selectmode = kwargs["selectmode"]
            del kwargs["selectmode"]
        if "width" in kwargs:
            width = kwargs["width"]
            del kwargs["width"]

        listbox = ListBox(master, *args, selectmode=selectmode, width=width, **kwargs)

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


class ListBox(tk.Listbox):
    SINGLE = tk.SINGLE
    MULTIPLE = tk.MULTIPLE

    def __init__(self, master, selectmode, *args, **kwargs):
        tk.Listbox.__init__(self, master, selectmode=selectmode, *args, **kwargs)
        self._selectmode = selectmode

    def update_options(self, options):
        self._delete_all_options()
        self._insert_options(options)
        # self._select_default()

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
        assert self._selectmode == ListBox.SINGLE

        selection = self.get_selections()
        if not selection:
            return None

        return selection[0]

    def select_default(self):
        self.select_set(0)

    def _insert_options(self, options):
        if not options:
            return

        for i in options:
            self.insert(tk.END, i)

    def _delete_all_options(self):
        self.delete(0, tk.END)


class DisableEnableWidget(object):
    """
    Records the callback to disable and enable a widget
    """
    def __init__(self):
        self._disable = None


class App(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)

        self.resizable(False, False)
        self.tk_setPalette("#ececec")

        x = (self.winfo_screenwidth() - self.winfo_reqwidth()) / 3
        y = (self.winfo_screenheight() - self.winfo_reqheight()) / 3

        default_font = tkFont.nametofont("TkDefaultFont")
        default_font.configure(size=13)

        self.geometry("+{}+{}".format(x, y))
        self.title("Android Device Manager")

        # Models
        self._adb = ADB()       # model for both device selection and package management
        self._device_administrator = DeviceAdministrator()
        # Views
        self._frame = MainFrame(self)
        # Controllers
        self._device_selection_manager = DeviceSelectionManager(self._adb, self._frame.device_selection_frame)
        self._device_manager = \
            DeviceAdministrationManager(self._device_administrator, self._frame.device_administration_frame)

    def run(self):
        self.mainloop()


class Frame(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        borderwidth = 3
        padx = 5
        pady = 5

        if "borderwidth" in kwargs:
            borderwith = kwargs["borderwidth"]
            del kwargs["borderwidth"]
        if "padx" in kwargs:
            padx = kwargs["padx"]
            del kwargs["padx"]
        if "pady" in kwargs:
            pady = kwargs["pady"]

        tk.Frame.__init__(self, master, borderwidth=borderwidth, padx=padx, pady=pady, *args, **kwargs)
        self.pack()


class FrameLeft(Frame):
    def __init__(self, master, *args, **kwargs):
        Frame.__init__(self, master, *args, **kwargs)
        self.pack(side=tk.LEFT)


class DeviceAdministrationFrame(FrameLeft):
    def __init__(self, master, *args, **kwargs):
        FrameLeft.__init__(self, master, *args, **kwargs)

        UI.create(UI.LABEL, self, text="Device Management")
        UI.create(UI.LABEL, self)
        self.create_template_button = UI.create(UI.BUTTON, self, text="Create Template")
        self.run_template_button = UI.create(UI.BUTTON, self, text="Run template")
        self.reboot_device_button = UI.create(UI.BUTTON, self, text="Reboot device")


class FileUtils(object):
    @staticmethod
    def create_file_close(name, data):
        with open(name, "w") as r:
            r.write(data)


class DeviceAdministrator(object):
    """
    The device administration model.
    """
    CONFIG_FILE = "VMMANAGER.CONF"

    CREATE_TEMPLATE = "0xA1"
    RUN_TEMPLATE = "0xA2"

    REBOOT_DEVICE = "0xAF"

    @staticmethod
    def create_template():
        DeviceAdministrator._do(DeviceAdministrator.CREATE_TEMPLATE)

    @staticmethod
    def run_template():
        DeviceAdministrator._do(DeviceAdministrator.RUN_TEMPLATE)

    @staticmethod
    def reboot_device():
        DeviceAdministrator._do(DeviceAdministrator.REBOOT_DEVICE)

    @staticmethod
    def _do(command):
        command += '\n'
        FileUtils.create_file_close(DeviceAdministrator.CONFIG_FILE, command)


class DeviceAdministrationManager(object):
    def __init__(self, device_administrator, device_administration_frame):
        self._model = device_administrator
        self._view = device_administration_frame

        self._set_commands()

    def _set_commands(self):
        self._view.create_template_button.config(command=self.create_template)
        self._view.run_template_button.config(command=self.run_template)
        self._view.reboot_device_button.config(command=self.reboot_device)

    def create_template(self):
        self._model.create_template()
        Message.show_info("Done!")

    def run_template(self):
        self._model.run_template()
        Message.show_info("Done!")

    def reboot_device(self):
        self._model.reboot_device()
        Message.show_info("Done!")


class DeviceSelectionManager(object):
    def __init__(self, adb, device_selection_frame):
        self._adb = adb
        self._view = device_selection_frame

        self._set_commands()
        self._refresh_device_list()

        # Solve the lost selection problem when focus gets lost
        self._view.device_listbox.config(exportselection=False)

    def refresh_device_list(self):
        self._refresh_device_list()
        Message.show_info("Device List Refreshed!")

    def _set_commands(self):
        self._view.refresh_button.config(command=self.refresh_device_list)
        self._view.select_button.config(command=self.create_package_management_frame)

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
            Message.show_error("Please Select a Device!")
            return

        frame = PackageManagementFrame(self._view)

        PackageManager(self._adb, frame, device)

    def _refresh_device_list(self):
        """
        We don't want the device refreshed message when this app starts up.
        :return: 
        """
        device_dict = self._adb.get_device_dict()

        options = []

        for device, status in device_dict.iteritems():
            options.append("{}    {}".format(device, status))

        Debug.debug(("options: ", options))

        self._view.device_listbox.update_options(options)

        self._view.device_listbox.select_default()

    def _get_selected_device(self):
        selection = self._view.device_listbox.get_selection()

        if not selection:
            Message.show_warning("Please Select a Device")
            return None

        device, _ = selection.split()

        Debug.debug(("device: ", device))

        return device


class DeviceSelectionFrame(FrameLeft):
    def __init__(self, master, *args, **kwargs):
        FrameLeft.__init__(self, master, *args, **kwargs)

        master = UI.create(UI.FRAME, self)

        UI.create(UI.LABEL, master, text="Package Management")
        UI.create(UI.LABEL, master)
        UI.create(UI.LABEL, master, text="List of Devices", anchor=None)
        UI.create(UI.LABEL, master, text="Devices     Status    ")
        UI.create(UI.LABEL, master)
        self.device_listbox = UI.create(UI.LISTBOX, master)

        master = UI.create(UI.FRAME, self)
        self.select_button = UI.create_left(UI.BUTTON, master, text="Select")
        self.refresh_button = UI.create_left(UI.BUTTON, master, text="Refresh")


class Toplevel(tk.Toplevel):
    def __init__(self, master, *args, **kwargs):
        tk.Toplevel.__init__(self, master, *args, **kwargs)


class PackageManagementFrame(Toplevel):
    def __init__(self, parent=None, *args, **kwargs):
        Toplevel.__init__(self, None, *args, **kwargs)

        self._parent = parent

        self.title("Package Manager")

        master = UI.create(UI.FRAME, self)

        self.installed_package_listbox = UI.create(UI.LISTBOX, master, selectmode=ListBox.MULTIPLE, width=50)

        master = UI.create(UI.FRAME, self)

        self.search_box = UI.create_left(UI.ENTRY, master)
        self.search_button = UI.create_left(UI.BUTTON, master, text="Search")

        master = UI.create(UI.FRAME, self)
        self.refresh_button = UI.create_left(UI.BUTTON, master, text="Refresh Installed Package List")
        self.install_button = UI.create_left(UI.BUTTON, master, text="Install")
        self.uninstall_button = UI.create_left(UI.BUTTON, master, text="Uninstall")


class PackageManager(object):
    def __init__(self, adb, package_management_frame, device):
        self._device = device

        self._model = adb
        self._view = package_management_frame
        self._set_commands()

        self._refresh_installed_package_list()

        self._view.search_box.focus_set()
        self._view.search_box.bind("<Return>", self.search)
        # self.bind("<Return>", self.search)      # TODO: figure out why this doesn't work

    def _set_commands(self):
        self._view.refresh_button.config(command=self.refresh_installed_package_list)
        self._view.install_button.config(command=self.install_packages)
        self._view.uninstall_button.config(command=self.uninstall_packages)
        self._view.search_button.config(command=self.search)

    def search(self, event=None):       # Tkinter pass event by default when calling callbacks
        search_phrase = self._view.search_box.get()
        if not search_phrase:
            return

        self._refresh_installed_package_list(search=search_phrase)

        return "break"

    def uninstall_packages(self):
        device = self._device

        if not device:
            return

        package_list = self._view.installed_package_listbox.get_selections()

        self._model.uninstall_packages(device, package_list)

    def install_packages(self):
        initialdir = "netdisk/app-files"
        device = self._device

        if not device:
            return

        package_path_filename_list = FileDialog.ask_open_filenames(initialdir=initialdir)
        self._model.install_packages(device, package_path_filename_list)

    def refresh_installed_package_list(self):
        if not self._device:
            return

        self._refresh_installed_package_list()
        Message.show_info("Installed Package List Refreshed!")

    def _refresh_installed_package_list(self, third_party=True, search=""):
        if not self._device:
            return

        installed_package_list = self._model.get_installed_package_list(self._device, third_party, search)
        Debug.debug(("installed_package_list[0: 3]: ", installed_package_list[0: 3]))

        self._view.installed_package_listbox.update_options(installed_package_list)


class MainFrame(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)

        self.device_administration_frame = DeviceAdministrationFrame(self)
        self.device_selection_frame = DeviceSelectionFrame(self)

        self.debug_button = None

        self._init_debug_frame()

    def _init_debug_frame(self):
        if not Debug.DEBUG:
            return

        def __debug():
            pass

        debug_frame = UI.create_left(UI.FRAME, self._frame)
        self.debug_button = UI.create(UI.BUTTON, debug_frame, text="Debug", command=__debug)


def main():
    app = App()
    app.run()

if __name__ == "__main__":
    main()
