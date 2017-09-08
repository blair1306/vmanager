#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#
#
import sys


if sys.version_info >= (3, 0):
    print("Please Use Python 2")
    exit(0)

import os
import Tkinter as tk
import ttk
import tkMessageBox
import tkFileDialog
import tkFont
import subprocess
import inspect
import socket
import ssl
import errno


PROTOCOL_VERSION = "0.1"


class Debug(object):
    DEBUG = True if '-d' in sys.argv[:] else False

    @staticmethod
    def debug(*args, **kwargs):
        if not Debug.DEBUG:
            return

        use_print = True
        if "use_print" in kwargs:
            use_print = kwargs["use_print"]
            del kwargs["use_print"]

        message = "%s: %s: " % Debug._get_caller_name()
        message += " ".join(map(repr, *args))

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


client = None


class Shell(object):
    """ Both client and server use this class as a shell wrapper.
    on server side, this is just a simple shell wrapper, whereas
    on client side, this sets up a tcp connection and run the shell command on the server side.
    """
    SUCCESS = 0
    FAILED = 1

    @staticmethod
    def execute_status(command):
        """
        Execute a command and return the return status
        :param command: "ls -l"
        :return: return status
        """
        global client
        if client:
            return client.execute_status(command)

        params = command.split()
        try:
            return subprocess.check_call(params)
        except:
            return Shell.FAILED

    @staticmethod
    def execute_output(command):
        """
        Execute a command and return it's output
        :param command: "ls -l"
        :return:  the output of the shell command
        """
        global client
        if client:
            return client.execute_output(command)

        try:
            output = subprocess.check_output(command, shell=True)
        except subprocess.CalledProcessError:
            output = ""

        return output


class FileDialog(object):
    @staticmethod
    def ask_open_filenames(*args, **kwargs):
        return tkFileDialog.askopenfilenames(*args, **kwargs)

    @staticmethod
    def ask_open_apkfilenames(**kwargs):
        return tkFileDialog.askopenfilenames(
            filetypes=[
                ('Apk files', '.apk'),
                ('All Files', '.*'),
            ],
            **kwargs
        )


class Message(object):
    """ Use to show a pop-up message
    *Don't use this on the server side*
    """
    @staticmethod
    def show_warning(message, *args, **kwargs):
        tkMessageBox.showwarning(message=message, *args, **kwargs)

    @staticmethod
    def show_error(message, *args, **kwargs):
        tkMessageBox.showerror(message=message, *args, **kwargs)

    @staticmethod
    def show_info(message, *args, **kwargs):
        tkMessageBox.showinfo(message=message, *args, **kwargs)

    @staticmethod
    def ask_ok_cancel(message, *args, **kwargs):
        return tkMessageBox.askokcancel(message=message, *args, **kwargs)


class ADBDeviceStatus(object):
    DEVICE = "device"
    OFFLINE = "offline"


class ADBException(Exception):
    pass


class ADBServerError(ADBException):
    pass


class ADB(object):
    """
    A simple wrapper of adb commands
    """
    @staticmethod
    def get_device_dict():
        """
        Get devices as a dict

        :return:  {"device0": "device", "device1", "offline"}
        """
        ADB._start_server_raise_exception()

        device_dict = {}

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
            return None

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
    def _check_status(device):
        """
        check to see if device exists and device if online. display error messages.
        :param device:
        :return: true if device doesn't exist or is offline.
        """
        assert device

        status = ADB._get_status(device)

        if status and status != ADBDeviceStatus.OFFLINE:
            return False

        if not status:
            Message.show_error("Coundn't find device: %s" % device)

        if status == ADBDeviceStatus.OFFLINE:
            Message.show_error("Device: %s is offline" % device)

        return True

    @staticmethod
    def install_packages(device, package_path_filename_list):
        """

        :return: Installation Status List
        """
        assert device
        assert package_path_filename_list

        if ADB._check_status(device):
            return None

        install_status_list = []
        for path_name in package_path_filename_list:
            status = ADB._install_package(device, path_name)
            install_status_list.append(status)

        return install_status_list

    @staticmethod
    def uninstall_packages(device, package_list):
        """

        :return: list of uninstallation status
        """
        assert device
        assert package_list

        if ADB._check_status(device):
            return None

        uninstall_status_list = []
        for package in package_list:
            # status_dict[package] = ADB._uninstall_package(device, package)
            status = ADB._uninstall_package(device, package)
            uninstall_status_list.append(status)

        return uninstall_status_list

    @staticmethod
    def _get_status(device):
        """
        Check if device exists and whether is operable.
        """
        assert device

        device_dict = ADB.get_device_dict()
        if not device_dict:
            return None

        status = device_dict[device]
        return status

    @staticmethod
    def _start_server():
        return Shell.execute_status("adb start-server")

    @staticmethod
    def _start_server_raise_exception():
        if (Shell.FAILED == ADB._start_server()) and (Shell.FAILED == ADB._start_server()):
            raise ADBServerError("Couldn't Start ADB Server.")

    @staticmethod
    def _install_package(device, full_path_name):
        """

        :param full_path_name: the full pathname of package to install:
        :return: Installation status
        """
        replace_existing = "-r"
        command = "adb -s %s install %s %s" % (device, replace_existing, full_path_name)
        return Shell.execute_status(command)

    @staticmethod
    def _uninstall_package(device, package_name):
        """

        :param package_name: the package to uninstall.
        :return: Uninstallation status
        TODO: The return code for adb uninstall doesn't work the way this intends it to, adb uninstall returns 0 even
              if the uninstallation fails.
        """
        command = "adb -s %s uninstall %s" % (device, package_name)
        Debug.debug((command,))
        return Shell.execute_status(command)


class UI(object):
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

    @staticmethod
    def create_below(name, master, *args, **kwargs):
        return UI.create(name, master, side=None, *args, **kwargs)

    @staticmethod
    def create_left(name, master, *args, **kwargs):
        side = UI.LEFT
        return UI.create(name, master, side=side, *args, **kwargs)

    @staticmethod
    def create_right(name, master, *args, **kwargs):
        side = UI.RIGHT
        return UI.create(name, master, side=side, *args, **kwargs)

    @staticmethod
    def create(name, master, side=None, *args, **kwargs):
        factory = UI.get_factory(name)
        if factory is None:
            raise ValueError

        widget = factory(master, *args, **kwargs)

        if name not in [UI.TOPLEVEL]:    # toplevel widget doesn't have pack()
            widget.pack(side=side)

        if name is UI.SCROLLBAR:
            widget.pack(fill=UI.Y)

        if name is UI.BUTTON:
            widget.pack(fill=UI.BOTH)

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
            UI.SCROLLBAR:  UI.create_scrollbar,
        }.get(name, None)

    @staticmethod
    def create_scrollbar(master, *args, **kwargs):
        scrollbar = ttk.Scrollbar(master, *args, **kwargs)

        return scrollbar

    @staticmethod
    def create_entry(master, *args, **kwargs):
        entry = ttk.Entry(master, *args, **kwargs)

        return entry

    @staticmethod
    def create_message(master, *args, **kwargs):
        message = tk.Message(master, *args, **kwargs)
        return message

    @staticmethod
    def create_frame(master, *args, **kwargs):
        borderwidth = 3

        if "borderwidth" in kwargs:
            borderwidth = kwargs["borderwidth"]
            del kwargs["borderwidth"]

        frame = ttk.Frame(master, borderwidth=borderwidth, *args, **kwargs)

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

        button = ttk.Button(master, text=text, command=command, *args, **kwargs)

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

        label = ttk.Label(master, text=text, anchor=anchor, *args, **kwargs)

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
        self._append_options(options)

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

    def _append_options(self, options):
        if not options:
            return

        for i in options:
            self.insert(tk.END, i)

    def _delete_all_options(self):
        self.delete(0, tk.END)


class App(tk.Tk):
    def __init__(self, lan):
        tk.Tk.__init__(self)

        self.resizable(False, False)
        # self.tk_setPalette("#ececec")

        x = (self.winfo_screenwidth() - self.winfo_reqwidth()) / 3
        y = (self.winfo_screenheight() - self.winfo_reqheight()) / 3

        default_font = tkFont.nametofont("TkDefaultFont")
        # default_font = tkFont.nametofont("Courier")
        default_font.configure(size=13)

        # reposition the window
        self.geometry("+{}+{}".format(x, y))
        self.title("Android Device Manager")

        # Use ttk style
        self.style = ttk.Style()
        classic = 'classic'
        self.style.theme_use(classic)

        self._lan = lan

        # Models
        self._adb = ADB()       # model for both device selection and package management
        self._device_administrator = DeviceAdministrator()
        # Views
        self._frame = MainFrame(self, self._lan)
        # Controllers
        self._device_selection_manager = DeviceSelectionManager(self._adb, self._frame.device_selection_frame, self._lan)
        self._device_manager = \
            DeviceAdministrationManager(self._device_administrator, self._frame.device_administration_frame, self._lan)

    def run(self):
        self.mainloop()


class Frame(ttk.Frame):
    def __init__(self, master, *args, **kwargs):
        borderwidth = 3

        if "borderwidth" in kwargs:
            borderwidth = kwargs["borderwidth"]
            del kwargs["borderwidth"]

        # ttk.Frame.__init__(self, master, borderwidth=borderwidth, padx=padx, pady=pady, *args, **kwargs)
        ttk.Frame.__init__(self, master, borderwidth=borderwidth, *args, **kwargs)
        self.pack()


class FrameLeft(Frame):
    def __init__(self, master, *args, **kwargs):
        Frame.__init__(self, master, *args, **kwargs)
        self.pack(side=tk.LEFT)


class AskOpenFilenamesFrame(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)

        master = UI.create_left(UI.FRAME, self)
        self.file_listbox_banner = UI.create(UI.LABEL, master)
        self.file_listbox = UI.create(UI.LISTBOX, master, selectmode=ListBox.MULTIPLE)

        master = UI.create_left(UI.FRAME, self)
        self.confirm_button = UI.create(UI.BUTTON, master)


class DirectoryUtils(object):
    @staticmethod
    def list_directory_content(path=None):
        path = path if path else "."    # default path is the current directory.
        return os.listdir(path)


class AskOpenFilenamesManager(object):
    def __init__(self, directory_utils, askopenfiles_frame, multi_lingual, initial_dir=None):
        self._controller = directory_utils
        self._view = askopenfiles_frame
        self._multi_lingual = multi_lingual
        self._initial_dir = initial_dir

        self._set_texts()
        self._list_files()
        self._set_commands()

        self.selections = tk.StringVar()       # Ordinary data will be destroyed once the window is destroyed.

    def _set_texts(self):
        self._view.file_listbox_banner.config(text=self._multi_lingual.get_text(MultiLingual.LIST_OF_FILE))
        self._view.confirm_button.config(text=self._multi_lingual.get_text(MultiLingual.SELECT))

    def _list_files(self):
        dir = self._initial_dir if self._initial_dir else "."
        file_list = self._controller.list_directory_content(dir)
        self._view.file_listbox.update_options(file_list)

    def _set_commands(self):
        self._view.confirm_button.config(command=self._on_ok)

    def _on_ok(self, event=None):
        s = self._view.file_listbox.get_selections()
        selections = "\n".join(s)

        self.selections.set(selections)

        self._view.master.destroy()

    def show(self):
        self._view.master.wm_deiconify()
        self._view.file_listbox.focus_set()
        self._view.master.wait_window()

        return self.selections.get()


class DeviceAdministrationFrame(FrameLeft):
    def __init__(self, master, lan, *args, **kwargs):
        FrameLeft.__init__(self, master, *args, **kwargs)

        self.lan = lan

        self.title = UI.create(UI.LABEL, self)
        UI.create(UI.LABEL, self)
        self.create_template_button = UI.create(UI.BUTTON, self)
        self.run_template_button = UI.create(UI.BUTTON, self)
        self.reboot_device_button = UI.create(UI.BUTTON, self)

        self._set_text()

    def _set_text(self):
        self.title.config(text=self.lan.get_text(MultiLingual.DEVICE_ADMINISTRATION))
        self.create_template_button.config(text=self.lan.get_text(MultiLingual.CREATE_TEMPLATE))
        self.run_template_button.config(text=self.lan.get_text(MultiLingual.RUN_TEMPLATE))
        self.reboot_device_button.config(text=self.lan.get_text(MultiLingual.REBOOT_DEVICE))


class FileUtils(object):
    @staticmethod
    def create_file_close(name, data):
        with open(name, "w") as r:
            r.write(data)

    @staticmethod
    def extract_filename(full_path_name):
        """
        Extract out the path of pathname
        :param full_path_name:
        :return: google.apk with /home/Download/google.apk as input
        """
        name = os.path.basename(full_path_name)
        return name


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
    def __init__(self, device_administrator, device_administration_frame, multi_lingual):
        self._model = device_administrator
        self._view = device_administration_frame
        self._multi_lingual = multi_lingual

        self._set_commands()

    def _set_commands(self):
        self._view.create_template_button.config(command=self.create_template)
        self._view.run_template_button.config(command=self.run_template)
        self._view.reboot_device_button.config(command=self.reboot_device)

    def create_template(self):
        self._model.create_template()
        Message.show_info(self._multi_lingual.get_text(MultiLingual.DONE))

    def run_template(self):
        self._model.run_template()
        Message.show_info(self._multi_lingual.get_text(MultiLingual.DONE))

    def reboot_device(self):
        self._model.reboot_device()
        Message.show_info(self._multi_lingual.get_text(MultiLingual.DONE))


class DeviceSelectionManager(object):
    def __init__(self, adb, device_selection_frame, multi_lingual):
        self._adb = adb
        self._view = device_selection_frame
        self._multi_lingual = multi_lingual

        self._set_commands()
        self._refresh_device_list()

        # Bind double click event to listbox
        self._view.device_listbox.bind('<Double-Button-1>', self.create_package_management_frame)

        # Solve the lost selection problem when focus gets lost
        self._view.device_listbox.config(exportselection=False)

    def refresh_device_list(self):
        self._refresh_device_list()
        Message.show_info(self._multi_lingual.get_text(MultiLingual.DONE))

    def _set_commands(self):
        self._view.refresh_button.config(command=self.refresh_device_list)
        self._view.select_button.config(command=self.create_package_management_frame)

    def create_package_management_frame(self, event=None):
        """
        Create package management frame if there is a device currently under selection.

        :return:
        """
        device = self._get_selected_device()
        if not device:
            Message.show_warning(self._multi_lingual.get_text(MultiLingual.PLEASE_SELECT_A_DEVICE))
            return

        self._create_package_management_frame(device)

    def _create_package_management_frame(self, device):
        toplevel = Toplevel()

        frame = PackageManagementFrame(toplevel)

        PackageManager(self._adb, frame, device, self._multi_lingual)

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
            return None

        device, _ = selection.split()

        Debug.debug(("device: ", device))

        return device


class DeviceSelectionFrame(FrameLeft):
    def __init__(self, master, lan, *args, **kwargs):
        FrameLeft.__init__(self, master, *args, **kwargs)

        master = UI.create(UI.FRAME, self)
        self.lan = lan

        self.title = UI.create(UI.LABEL, master)
        UI.create(UI.LABEL, master)
        self.banner = UI.create(UI.LABEL, master, anchor=None)
        self.device_listbox = UI.create(UI.LISTBOX, master)

        master = UI.create(UI.FRAME, self)
        self.select_button = UI.create_left(UI.BUTTON, master)
        self.refresh_button = UI.create_left(UI.BUTTON, master)

        self._set_text()

    def _set_text(self):
        self.title.config(text=self.lan.get_text(MultiLingual.PACKAGE_MANAGEMENT))
        self.banner.config(text=self.lan.get_text(MultiLingual.LIST_OF_DEVICES))
        self.select_button.config(text=self.lan.get_text(MultiLingual.SELECT))
        self.refresh_button.config(text=self.lan.get_text(MultiLingual.REFRESH))


class Toplevel(tk.Toplevel):
    def __init__(self, master=None, *args, **kwargs):
        tk.Toplevel.__init__(self, master, *args, **kwargs)


class PackageManagementFrame(Frame):
    def __init__(self, master, *args, **kwargs):
        Frame.__init__(self, master, *args, **kwargs)

        self.master.resizable(False, False)

        self.device_info = tk.StringVar()
        self.device_info.set("No Device is Selected")
        UI.create(UI.LABEL, self, textvariable=self.device_info, anchor='center')

        master = UI.create(UI.FRAME, self)

        self.installed_package_listbox = UI.create_left(UI.LISTBOX, master, selectmode=ListBox.MULTIPLE, width=50)
        self.scrollbar = UI.create_right(UI.SCROLLBAR, master)

        master = UI.create(UI.FRAME, self)

        self.search_box = UI.create_left(UI.ENTRY, master)
        self.search_button = UI.create_left(UI.BUTTON, master)

        master = UI.create(UI.FRAME, self)
        self.refresh_button = UI.create_left(UI.BUTTON, master)
        self.install_button = UI.create_left(UI.BUTTON, master)
        self.uninstall_button = UI.create_left(UI.BUTTON, master)

        self._init_installed_package_list_scrollbar()

    def _init_installed_package_list_scrollbar(self):
        listbox = self.installed_package_listbox
        scrollbar = self.scrollbar

        listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=listbox.yview)


class PackageManager(object):
    def __init__(self, adb, package_management_frame, device, multi_lingual):
        assert device

        self._device = device
        self._multi_lingual = multi_lingual

        self._model = adb
        self._view = package_management_frame
        self._set_commands()

        self._set_device_info()

        self._refresh_installed_package_list()

        self._view.search_box.focus_set()
        self._view.search_box.bind("<Return>", self.search)
        # self.bind("<Return>", self.search)      # TODO: figure out why this doesn't work

        self._set_texts()

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

        package_list = self._view.installed_package_listbox.get_selections()

        if not package_list:
            Message.show_warning(self._multi_lingual.get_text(MultiLingual.PLEASE_SELECT_AT_LEAST_ONE_PACKAGE_TO_UNINSTALL), parent=self._view)
            return

        package_list_string = " ".join(package_list)

        if not Message.ask_ok_cancel("%s: %s?" % (self._multi_lingual.get_text(MultiLingual.UNINSTALL_THESE_PACKAGES), package_list_string), parent=self._view):
            Message.show_info(self._multi_lingual.get_text(MultiLingual.CANCELLED), parent=self._view)
            return

        status_list = self._model.uninstall_packages(device, package_list)
        success_list_string, failure_list_string = self._do(package_list, status_list)

        if success_list_string:
            Message.show_info("%s %s!" % (success_list_string, self._multi_lingual.get_text(MultiLingual.DONE)), parent=self._view)
        if failure_list_string:
            Message.show_error("Uninstallation Failed for %s" % failure_list_string, parent=self._view)

        self._refresh_installed_package_list()

    def install_packages(self):
        initialdir = "/netdisk/app-files"
        device = self._device

        toplevel = Toplevel()

        directory_utils = DirectoryUtils()
        ask_open_filenames_frame = AskOpenFilenamesFrame(toplevel)
        ask_open_filenames_manager = AskOpenFilenamesManager(directory_utils, ask_open_filenames_frame, self._multi_lingual, initialdir)

        package_filename_list_string = ask_open_filenames_manager.show()
        package_filename_list_string = str(package_filename_list_string)
        package_filename_list = package_filename_list_string.splitlines()

        if not package_filename_list:
            Message.show_info(self._multi_lingual.get_text(MultiLingual.CANCELLED), parent=self._view)
            return

        name_list = map(FileUtils.extract_filename, package_filename_list)
        name_list_string = "    ".join(name_list)

        if not Message.ask_ok_cancel("%s? %s" % (self._multi_lingual.get_text(MultiLingual.INSTALL_THESE_PACKAGES), name_list_string), parent=self._view):
            Message.show_info(self._multi_lingual.get_text(MultiLingual.CANCELLED), parent=self._view)
            return

        package_path_filename_list = []

        for filename in package_filename_list:
            package_path_filename_list.append(initialdir+"/"+filename)

        status_list = self._model.install_packages(device, package_path_filename_list)

        success_list_string, failure_list_string = self._do(name_list, status_list)

        if success_list_string:
            Message.show_info("%s %s!" % (success_list_string, self._multi_lingual.get_text(MultiLingual.DONE)), parent=self._view)
        if failure_list_string:
            Message.show_error("%s %s" % (self._multi_lingual.get_text(MultiLingual.FAILED), failure_list_string), parent=self._view)

        self._refresh_installed_package_list()

    def refresh_installed_package_list(self):
        self._refresh_installed_package_list()
        Message.show_info(self._multi_lingual.get_text(MultiLingual.DONE), parent=self._view)

    def _do(self, name_list, status_list):
        assert len(name_list) == len(status_list)

        success_list = []
        failure_list = []

        for status in status_list:
            item = name_list.pop(0)
            if status == Shell.SUCCESS:
                success_list.append(item)
            elif status == Shell.FAILED:
                failure_list.append(item)

        success_list_string = " ".join(success_list)
        failure_list_string = " ".join(failure_list)

        return success_list_string, failure_list_string

    def _set_texts(self):
        self._view.search_button.config(text=self._multi_lingual.get_text(MultiLingual.SEARCH))
        self._view.refresh_button.config(text=self._multi_lingual.get_text(MultiLingual.REFRESH_INSTALLED_PACKAGE_LIST))
        self._view.install_button.config(text=self._multi_lingual.get_text(MultiLingual.INSTALL))
        self._view.uninstall_button.config(text=self._multi_lingual.get_text(MultiLingual.UNINSTALL))

    def _refresh_installed_package_list(self, third_party=True, search=""):
        installed_package_list = self._model.get_installed_package_list(self._device, third_party, search)
        Debug.debug(("installed_package_list[0: 3]: ", installed_package_list[0: 3]))

        self._view.installed_package_listbox.update_options(installed_package_list)

    def _set_device_info(self):
        device_info = "%s : %s" % (self._multi_lingual.get_text(MultiLingual.DEVICE_SELECTED), self._device if self._device else "No Device is Selected")
        self._view.device_info.set(device_info)


class MainFrame(Frame):
    def __init__(self, master, lan):
        Frame.__init__(self, master)

        self.lan = lan

        self.device_administration_frame = DeviceAdministrationFrame(self, self.lan)
        self.device_selection_frame = DeviceSelectionFrame(self, self.lan)

        self.debug_button = None

        self._init_debug_frame()

    def _init_debug_frame(self):
        if not Debug.DEBUG:
            return

        def __debug():
            pass

        debug_frame = UI.create_left(UI.FRAME, self)
        self.debug_button = UI.create(UI.BUTTON, debug_frame, text="Debug", command=__debug)


class ConnectToServerFrame(Frame):
    def __init__(self, master, lan):
        Frame.__init__(self, master)

        self._lan = lan

        frame = UI.create(UI.FRAME, self)
        parent = UI.create_left(UI.FRAME, frame)
        self.server_address_banner = UI.create(UI.LABEL, parent)
        self.server_address = UI.create(UI.ENTRY, parent)

        parent = UI.create_left(UI.FRAME, frame)
        self.port_banner = UI.create(UI.LABEL, parent)
        self.port = UI.create(UI.ENTRY, parent)

        frame = UI.create(UI.FRAME, self)
        self.connect = UI.create_left(UI.BUTTON, frame)

        self._set_text()

    def _set_text(self):
        self.server_address_banner.config(text=self._lan.get_text(MultiLingual.SERVER_ADDRESS))
        self.port_banner.config(text=self._lan.get_text(MultiLingual.PORT))
        self.connect.config(text=self._lan.get_text(MultiLingual.CONNECT))


class MultiLingual(object):
    EN = "en"
    CH = "ch"

    LANGUAGES = (EN, CH)

    TEXTS = \
    DEVICE_ADMINISTRATION, \
    CREATE_TEMPLATE, \
    RUN_TEMPLATE, \
    REBOOT_DEVICE, \
    \
    PACKAGE_MANAGEMENT, \
    SELECT, \
    REFRESH, \
    LIST_OF_DEVICES, \
    \
    SEARCH, \
    REFRESH_INSTALLED_PACKAGE_LIST, \
    INSTALL, \
    UNINSTALL, \
    \
    DONE, \
    \
    PLEASE_SELECT_A_DEVICE, \
    \
    PLEASE_SELECT_AT_LEAST_ONE_PACKAGE_TO_UNINSTALL, \
    \
    UNINSTALL_THESE_PACKAGES, \
    CANCELLED, \
    INSTALL_THESE_PACKAGES, \
    FAILED, \
    DEVICE_SELECTED, \
    \
    SERVER_ADDRESS, \
    PORT, \
    CONNECT, \
    \
    LIST_OF_FILE \
        = range(24)  # Increase this number everytime when adding new items to the list.

    NAMES = (
        range(len(TEXTS))
    )

    def __init__(self, language):
        assert language in MultiLingual.LANGUAGES

        self._language = language

    def get_text(self, name):
        assert name in MultiLingual.NAMES

        return {
            MultiLingual.LIST_OF_FILE: {
                MultiLingual.EN: "List of file",
                MultiLingual.CH: "文件列表"
            },
            MultiLingual.CONNECT: {
                MultiLingual.EN: "Connect",
                MultiLingual.CH: "选择"
            },
            MultiLingual.SERVER_ADDRESS: {
                MultiLingual.EN: "Server Address",
                MultiLingual.CH: "服务器地址"
            },
            MultiLingual.PORT: {
                MultiLingual.EN: "Port",
                MultiLingual.CH: "端口号"
            },
            MultiLingual.DEVICE_ADMINISTRATION: {
                MultiLingual.EN: "Device Administration",
                MultiLingual.CH: "设备管理"
            },
            MultiLingual.CREATE_TEMPLATE: {
                MultiLingual.EN: "Create Template",
                MultiLingual.CH: "制作模板"
            },
            MultiLingual.RUN_TEMPLATE: {
                MultiLingual.EN: "Run Template",
                MultiLingual.CH: "运行模版"
            },
            MultiLingual.REBOOT_DEVICE: {
                MultiLingual.EN: "Reboot Device",
                MultiLingual.CH: "重启设备"
            },
            MultiLingual.PACKAGE_MANAGEMENT : {
                MultiLingual.EN: "Package management",
                MultiLingual.CH: "软件包管理器"
            },
            MultiLingual.SELECT : {
                MultiLingual.EN: "Select",
                MultiLingual.CH: "选择"
            },
            MultiLingual.REFRESH : {
                MultiLingual.EN: "Refresh",
                MultiLingual.CH: "刷新"
            },
            MultiLingual.LIST_OF_DEVICES : {
                MultiLingual.EN: "List of Devices",
                MultiLingual.CH: "设备列表"
            },
            MultiLingual.INSTALL : {
                MultiLingual.EN: "Install",
                MultiLingual.CH: "安装"
            },
            MultiLingual.SEARCH: {
                MultiLingual.EN: "Search",
                MultiLingual.CH: "搜索"
            },
            MultiLingual.REFRESH_INSTALLED_PACKAGE_LIST : {
                MultiLingual.EN: "Refresh Installed Package List",
                MultiLingual.CH: "刷新已安装程序列表"
            },
            MultiLingual.UNINSTALL : {
                MultiLingual.EN: "Uninstall",
                MultiLingual.CH: "卸载"
            },
            MultiLingual.DONE: {
                MultiLingual.EN: "Done",
                MultiLingual.CH: "完成"
            },
            MultiLingual.PLEASE_SELECT_A_DEVICE: {
                MultiLingual.EN: "Please Select a Device",
                MultiLingual.CH: "请选择一个设备"
            },
            MultiLingual.PLEASE_SELECT_AT_LEAST_ONE_PACKAGE_TO_UNINSTALL: {
                MultiLingual.EN: "Please Select at Least One Package to Uninstall",
                MultiLingual.CH: "请至少选择一个包"
            },
            MultiLingual.UNINSTALL_THESE_PACKAGES: {
                MultiLingual.EN: "Uninstall These Packages",
                MultiLingual.CH: "卸载这些包"
            },
            MultiLingual.CANCELLED: {
                MultiLingual.EN: "Cancelled",
                MultiLingual.CH: "已取消"
            },
            MultiLingual.INSTALL_THESE_PACKAGES : {
                MultiLingual.EN: "Install These Packages",
                MultiLingual.CH: "安装这些包"
            },
            MultiLingual.FAILED: {
                MultiLingual.EN: "Failed",
                MultiLingual.CH: "失败"
            },
            MultiLingual.DEVICE_SELECTED: {
                MultiLingual.EN: "Device Selected",
                MultiLingual.CH: "已选择设备"
            },
        }.get(name).get(self._language)


class ConnectToServerManager(object):
    def __init__(self, connect_to_server_frame, lan):
        self._view = connect_to_server_frame
        self._lan= lan
        self._set_default_values()
        self._set_commands()

    def _set_default_values(self):
        self._view.server_address.insert(0, "localhost")
        self._view.port.insert(0, get_default_port())

    def _set_commands(self):
        self._view.connect.config(command=self._start_client)

    def _start_client(self):
        address = self._view.server_address.get()
        port = self._view.port.get()
        port = int(port)

        root = self._view.master
        root.destroy()

        global client
        client = Client(address, port)

        app = App(self._lan)
        app.run()


def client_main():
    root = tk.Tk()

    # Multiple-Language support
    lan = MultiLingual.EN if "--english" in sys.argv else MultiLingual.CH
    multi_lingual = MultiLingual(lan)

    connect_to_server_frame = ConnectToServerFrame(root, multi_lingual)
    connect_to_server_manager = ConnectToServerManager(connect_to_server_frame, multi_lingual)
    root.mainloop()


def server_main():
    server = Server()
    server.serve()


def get_default_port():
    DEFAULT_PORT = 8909
    return DEFAULT_PORT


def get_max_buffersize():
    MAX_BUFFERSIZE = 1024 * 4
    return MAX_BUFFERSIZE


class AMessage(object):
    GRETTING       = "00000000"
    COMMAND_OUTPUT = "00000001"
    COMMAND_STATUS = "00000002"

    OK             = "00000010"

    TYPE_LEN = len(GRETTING)
    LEN_LEN = 4
    COMMAND_START = TYPE_LEN + LEN_LEN
    TYPES = (GRETTING, OK, COMMAND_OUTPUT, COMMAND_STATUS)

    @staticmethod
    def create_message(type, length=0, command=""):
        assert type in AMessage.TYPES
        assert length >= 0
        message = "%s%4d%s" % (type, length, command)
        message += " " * (get_max_buffersize() - len(message))
        assert len(message) == get_max_buffersize()

        return message

    @staticmethod
    def create_ok_message():
        return AMessage.create_message(AMessage.OK)

    @staticmethod
    def create_command_message(command, output=True):
        assert command
        command_type = AMessage.COMMAND_OUTPUT if output else AMessage.COMMAND_STATUS
        return AMessage.create_message(command_type, len(command), command)

    @staticmethod
    def create_greeting_message():
        return AMessage.create_message(AMessage.GRETTING, len(PROTOCOL_VERSION), PROTOCOL_VERSION)

    @staticmethod
    def get_type_and_length(message):
        type = message[: AMessage.TYPE_LEN]
        assert type in AMessage.TYPES
        length = int(message[AMessage.TYPE_LEN:])
        assert length >= 0

        return type, length

    @staticmethod
    def get_command_and_type_from_message(message):
        type = message[: AMessage.TYPE_LEN]
        assert type in (AMessage.COMMAND_STATUS, AMessage.COMMAND_OUTPUT)

        l = message[AMessage.TYPE_LEN: AMessage.COMMAND_START]
        l = int(l)

        assert l > 0

        command = message[AMessage.COMMAND_START: AMessage.COMMAND_START+l]

        return command, type

    @staticmethod
    def get_version_from_message(message):
        type = message[: AMessage.TYPE_LEN]
        assert type == AMessage.GRETTING

        l = message[AMessage.TYPE_LEN: AMessage.TYPE_LEN+AMessage.LEN_LEN]
        l = int(l)
        version = message[AMessage.COMMAND_START: AMessage.COMMAND_START+l]

        return version

    @staticmethod
    def is_ok_message(message):
        type = message[: AMessage.TYPE_LEN]
        assert type == AMessage.OK

        return True


class APayload(object):
    WRITE = "ffffffff"
    CLOSE = "fffffff0"

    TYPES = (WRITE, CLOSE)

    TYPE_LEN = len(CLOSE)
    ACTUAL_LEN_LEN = 4      # We use 4 digits to represent the length of the actual payload.
    ACTUAL_PAYLOAD_START = TYPE_LEN + ACTUAL_LEN_LEN
    MAX_ACTUAL_PAYLOAD_LEN = get_max_buffersize() - TYPE_LEN - ACTUAL_LEN_LEN

    @staticmethod
    def create_payload(data):
        """
        :return: a list of strings to be sent over socket
        """
        l = len(data)
        where = 0
        payload_list = []
        payload_template = "%s%4d%s"    # 4 for the length of actual payload

        while l > 0:
            if l > APayload.MAX_ACTUAL_PAYLOAD_LEN:
                actual_len = APayload.MAX_ACTUAL_PAYLOAD_LEN
            else:
                actual_len = l

            payload = payload_template % (APayload.WRITE, actual_len, data[where: where+actual_len])
            where += actual_len
            l -= actual_len

            ll = len(payload)
            payload = payload + " " * (get_max_buffersize() - ll) if ll < get_max_buffersize() else payload
            assert len(payload) == get_max_buffersize()

            payload_list.append(payload)

        payload = payload_template % (APayload.CLOSE, 0, "")
        payload = payload + " " * (get_max_buffersize() - len(payload)) if len(payload) < get_max_buffersize() else payload
        payload_list.append(payload)

        return payload_list

    @staticmethod
    def get_data_from_payload_list(payload_list):
        data = ""

        if not payload_list:
            return data

        assert payload_list[-1][:len(APayload.CLOSE)] == APayload.CLOSE
        payload_list = payload_list[:-1]

        for payload in payload_list:
            assert payload[:len(APayload.WRITE)] == APayload.WRITE
            l = int(payload[APayload.TYPE_LEN: APayload.TYPE_LEN+APayload.ACTUAL_LEN_LEN])
            assert 0 < l <= APayload.MAX_ACTUAL_PAYLOAD_LEN
            data += payload[APayload.ACTUAL_PAYLOAD_START: APayload.ACTUAL_PAYLOAD_START+l]

        return data


def do_send(sock, data):
    l = len(data)
    if l == 0:
        return

    l_total_sent = 0

    while l_total_sent < l:
        l_sent = sock.send(data[l_total_sent:])
        l_total_sent += l_sent

    assert l == l_total_sent


def do_recv(sock, length):
    data = ""
    assert length >= 0

    l_total_recv = 0
    while l_total_recv < length:
        rec = sock.recv(length-l_total_recv)
        l_recv = len(rec)
        l_total_recv += l_recv
        data += rec

    assert l_total_recv == length

    return data


ssl_certfile = "server.crt"
ssl_keyfile = "server.key"


class Server(object):
    ADDRESS = ""
    PORT = get_default_port()
    MAX_BUFFERSIZE = get_max_buffersize()

    def __init__(self, port=None):
        self._listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = Server.ADDRESS
        port = Server.PORT if not port else port

        self._listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

        self._listen_socket.bind((host, port))
        self._listen_socket.listen(5)

    def serve(self):
        while True:
            (_client_socket, address) = self._listen_socket.accept()
            client_socket = ssl.wrap_socket(_client_socket,
                                            server_side=True,
                                            certfile=ssl_certfile,
                                            keyfile=ssl_keyfile,
                                            )
            try:
                self.deal_with_client(client_socket)
            finally:
                client_socket.shutdown(socket.SHUT_RDWR)
                client_socket.close()

    def deal_with_client(self, client_socket):
        message = self.receive(client_socket)

        reply_greetting_message = AMessage.create_greeting_message()
        self.send(client_socket, reply_greetting_message)

        if not AMessage.get_version_from_message(message) == PROTOCOL_VERSION:
            return

        command_message = self.receive(client_socket)
        command, command_type = AMessage.get_command_and_type_from_message(command_message)

        execute = Shell.execute_output if command_type == AMessage.COMMAND_OUTPUT else Shell.execute_status

        data = execute(command)

        if type(data) is int:
            data = str(data)

        payload_list = APayload.create_payload(data)
        for payload in payload_list:
            self.send(client_socket, payload)

    @staticmethod
    def receive(client_sock):
        return do_recv(client_sock, get_max_buffersize())

    @staticmethod
    def send(client_socket, data):
        return do_send(client_socket, data)


class Client(object):
    SERVER_PORT = get_default_port()
    SERVER_ADDRESS = "localhost"

    def __init__(self, address=None, port=None):
        self._server_hostname = Client.SERVER_ADDRESS if not address else address
        self._port = Client.SERVER_PORT if not port else port

    def execute_status(self, command):
        status = self.execute(command, output=False)
        status = int(status)
        return status

    def execute_output(self, command):
        return self.execute(command, output=True)

    def execute(self, command, output=True):
        _sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock = ssl.wrap_socket(_sock, ca_certs=ssl_certfile,
                               cert_reqs=ssl.CERT_REQUIRED)
        try:
            sock.connect((self._server_hostname, self._port))
        except socket.error as e:
            if e.errno == errno.ECONNREFUSED:
                Message.show_error("Connection to the server refused.")

            exit(1)

        greeting_message = AMessage.create_greeting_message()
        self.send(sock, greeting_message)

        reply_message = self.recv(sock)
        version = AMessage.get_version_from_message(reply_message)

        if version != PROTOCOL_VERSION:
            raise

        command_message = AMessage.create_command_message(command, output)
        self.send(sock, command_message)

        payload_list = []
        while True:
            payload = self.recv(sock)
            payload_list.append(payload)

            type = payload[:APayload.TYPE_LEN]
            if type == APayload.CLOSE:
                break

        data = APayload.get_data_from_payload_list(payload_list)

        sock.shutdown(socket.SHUT_RDWR)
        sock.close()

        return data

    @staticmethod
    def send(sock, message):
        return do_send(sock, message)

    @staticmethod
    def recv(sock):
        return do_recv(sock, get_max_buffersize())


if __name__ == "__main__":
    if "--server" in sys.argv:
        server_main()
    else:
        client_main()
