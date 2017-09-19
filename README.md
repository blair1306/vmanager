Android Virtual Machine Manager
===========================

This is a simple GUI program for managing android virtual device (works on physical devices as well) running on a host machine.

Usage: On the server side, before starting server for the first time, you have to run the script to generate the private and public keys needed by the server. By

> make

After those keys are generated, start the server.

> python android_device_manager.py server

Then you can start the GUI client.

> python android_device_manager.py
