"""
"""


from setuptools import setup

description = """

"""

setup(
    name = 'ADManager',
    description = 'A simple GUI frontend for android adb',
    long_description = description,
    author = 'vmplay',
    install_requires = [
        'python-tk',
    ],
    scripts = [
        "android_device_manager.py",
    ],
)
