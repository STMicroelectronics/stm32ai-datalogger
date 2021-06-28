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


import serial
from ai_logging.core import DriverInterface
from ai_logging.core.exceptions import *

class Serial(DriverInterface):
    def __init__(self ,*args, **kwargs):
        self.ser = None

    def connect(self, *args, **kwargs):
        comPort = None
        baudrate=115200

        if 'port' in kwargs:
            comPort = kwargs['port']
        else:
            if len(args) > 0:
                comPort = args[0]
        
        if comPort is None:
            raise ConnectionException("Error: can't connect, 'port' must be passed as named parameter or as first argument")

        if 'baudrate' in kwargs:
            try:
                baudrate = int(kwargs['baudrate'])
            except Exception as e:
                print("Error while parsing 'baudrate' {}, using default instead {} ({})".format(kwargs['baudrate'], baudrate, e))
        else:
            if len(args) > 1:
                try:
                    baudrate = int(args[1])
                except Exception as e:
                    print("Error while parsing baudrate {}, using default instead {} ({})".format(args[1], baudrate, e))
        

        if self.ser is not None and self.ser.is_open:
            try:
                self.ser.close()
                self.ser = None
            except serial.serialutil.SerialException as e:
                print("Error while closing port {}".format(e))

        if self.ser is None:
            self.ser = serial.Serial(comPort, baudrate)
        else:
            print("Error: serial should be None")
           
        if not self.ser.is_open:
            print("Can't connect right now")
        else:
            print("Connected")

    def byte_available(self, *args, **kwargs):
        try:
            if self.ser is None or not self.ser.is_open:
                raise Exception("COM port is not open")
            return self.ser.in_waiting
        except serial.SerialException:
            return -1

    def read(self, nb_byte, *args, **kwargs):
        if not self.ser.is_open:
            raise Exception("COM port is not open")
        if nb_byte <= 0:
            nb_byte = self.byte_available(args, kwargs)
        data = self.ser.read(size=nb_byte)
        return data

    def write(self, data:bytes, *args, **kwargs):
        try:
            if not self.ser.is_open:
                raise Exception("COM port is not open")
            self.ser.write(data)
            self.ser.flush()
        except:
            return 0
        return len(data)

    def is_connected(self, *args, **kwargs):
        return self.ser.is_open if self.ser is not None else False

    def close(self, *args, **kwargs):
        self.ser.close()
        self.ser = None