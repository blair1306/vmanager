# coding: utf-8

"""
This module provides an interface for getting text string of a specific language.
Be it chinese, english, etc.
"""


EN = "en"
CH = "ch"
LANS = [EN, CH]

# Default language is chinese.
lan = CH


def init(ch=True):
    """Init this module.
    """
    if ch:
        set_ch()
    else:
        set_en()


def get_text(text, _lan=None):
    if _lan is None:
        return DICT.get(text).get(lan)
    else:
        return DICT.get(text).get(_lan)


def set_lan(_lan):
    global lan

    assert _lan in LANS
    lan = _lan


def set_ch():
    set_lan(CH)


def set_en():
    set()

def set(lan=EN):
    set_lan(lan)


def get_lan():
    """
    Get the current language in use.
    """
    return lan


TEXTS = \
    DEVICE_ADMINISTRATION, \
    CREATE_TEMPLATE, \
    RUN_TEMPLATE, \
    REBOOT_DEVICE, \
    \
    PACKAGE_MANAGEMENT, \
    SELECT, \
    CANCEL, \
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
    PLEASE_SELECT_AT_LEAST_ONE_PACKAGE, \
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
    LIST_OF_FILE, \
    \
    DEVICE_ID, \
    RESOLUTION, \
    RAM_SIZE_IN_GB, \
    STATUS, \
    \
    CHECK_CONNECTION, \
    UNABLE_TO_CONNECT_TO, \
    ERROR_MESSAGE, \
    SERVER_ERROR, \
    DOUBLE_CLICK_ON_DEVICE, \
        = range(34)  # Increase this number everytime when adding new items to the list.
        # TODO: there must be a better way than this.


DICT = {
    LIST_OF_FILE: {
        EN: "List of file",
        CH: "文件列表"
    },
    CONNECT: {
        EN: "Connect",
        CH: "连接"
    },
    SERVER_ADDRESS: {
        EN: "Server Address",
        CH: "服务器地址"
    },
    PORT: {
        EN: "Port",
        CH: "端口号"
    },
    DEVICE_ADMINISTRATION: {
        EN: "Device Administration",
        CH: "设备管理"
    },
    CREATE_TEMPLATE: {
        EN: "Create Template",
        CH: "制作模板"
    },
    RUN_TEMPLATE: {
        EN: "Run Template",
        CH: "运行模版"
    },
    REBOOT_DEVICE: {
        EN: "Reboot Device",
        CH: "重启设备"
    },
    PACKAGE_MANAGEMENT : {
        EN: "Package management",
        CH: "软件包管理器"
    },
    SELECT : {
        EN: "Select",
        CH: "选择"
    },
    CANCEL : {
        EN: "CANCEL",
        CH: "取消"
    },
    REFRESH : {
        EN: "Refresh",
        CH: "刷新"
    },
    LIST_OF_DEVICES : {
        EN: "List of Devices",
        CH: "设备列表"
    },
    INSTALL : {
        EN: "Install",
        CH: "安装"
    },
    SEARCH: {
        EN: "Search",
        CH: "搜索"
    },
    REFRESH_INSTALLED_PACKAGE_LIST : {
        EN: "Refresh Installed Package List",
        CH: "刷新已安装程序列表"
    },
    UNINSTALL : {
        EN: "Uninstall",
        CH: "卸载"
    },
    DONE: {
        EN: "Done",
        CH: "完成"
    },
    PLEASE_SELECT_A_DEVICE: {
        EN: "Please Select a Device",
        CH: "请选择一个设备"
    },
    PLEASE_SELECT_AT_LEAST_ONE_PACKAGE: {
        EN: "Please Select at Least One Package",
        CH: "请至少选择一个包"
    },
    UNINSTALL_THESE_PACKAGES: {
        EN: "Uninstall These Packages",
        CH: "卸载这些包"
    },
    CANCELLED: {
        EN: "Cancelled",
        CH: "已取消"
    },
    INSTALL_THESE_PACKAGES : {
        EN: "Install These Packages",
        CH: "安装这些包"
    },
    FAILED: {
        EN: "Failed",
        CH: "失败"
    },
    DEVICE_SELECTED: {
        EN: "Device Selected",
        CH: "已选择设备"
    },

    DEVICE_ID: {
        EN: "Device ID",
        CH: "设备id"
    },
    RESOLUTION: {
        EN: "Resolution",
        CH: "分辨率"
    },
    RAM_SIZE_IN_GB: {
        EN: "RAM size (GB)",
        CH: "内存大小 (GB)"
    },
    STATUS: {
        EN: "Status",
        CH: "状态"
    },
    CHECK_CONNECTION: {
        EN: "Please Check Your Network Connection.",
        CH: "请检查你的网络"
    },
    UNABLE_TO_CONNECT_TO: {
        EN: "Unable to Connect to",
        CH: "无法连接到"
    },
    ERROR_MESSAGE: {
        EN: "Error Message",
        CH: "错误信息"
    },
    SERVER_ERROR: {
        EN: "Server Error",
        CH: "服务器错误"
    },
    DOUBLE_CLICK_ON_DEVICE: {
        EN: "Duble Click on Device to Open",
        CH: "双击设备来打开"
    },
}