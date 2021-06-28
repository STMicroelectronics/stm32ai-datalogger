###################################################################################
#   Copyright (c) 2020-2021 STMicroelectronics.
#   All rights reserved.
#   This software is licensed under terms that can be found in the LICENSE file in
#   the root directory of this software component.
#   If no LICENSE file comes with this software, it is provided AS-IS.
###################################################################################

__author__ = "Romain LE DONGE"
__copyright__ = "Copyright (c) 2021 STMicroelectronics"
__license__ = """
    Copyright (c) 2020-2021 STMicroelectronics.
    All rights reserved.
    This software is licensed under terms that can be found in the LICENSE file in
    the root directory of this software component.
    If no LICENSE file comes with this software, it is provided AS-IS.
"""

class DriverInterface:
    """ connect to the device """
    def connect(self, *args, **kwargs):
        print("Error: connect has not been overriden")

    """ disconnect the interface from the device to allow other do connect """
    def disconnect(self, *args, **kwargs):
        print("Error: disconnect has not been overriden")
    
    """ write byte through the driver and return number of byte written"""
    def write(self, data:bytes, *args, **kwargs) -> int:
        print("Error: write has not been overriden")

    """ read and return nb_byte bytes from the driver """
    def read(self, nb_byte, *args, **kwargs) -> bytes:
        print("Error: read has not been overriden")

    """ Indicates the number of byte available to be read from the driver """
    def byte_available(self, *args, **kwargs) -> int:
        print("Error: byte_available has not been overriden")

    def is_connected(self, *args, **kwargs):
        print("Error: is_connected has not been overriden")
