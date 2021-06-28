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

import time
from .interfaces import DriverInterface
from . import ai_logging_api_wrapper

class AILoggingAPI:
    """! @brief AILogging API high level user interface
    """
    
    _drivers = [] # driver list
    types = ai_logging_api_wrapper.AILoggingPayloadType


    def __init__(self, com_driver, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs
        self._driver_instance = None
        self._wrapper = ai_logging_api_wrapper.AILoggingAPIWrapper(
            self._write, 
            self._read,
            receive_fptr_read_length = kwargs.get('read_size', 16)
        )
        
        if isinstance(com_driver, str):
            if com_driver == 'serial':
                from ai_logging.drivers import Serial

                if not self._has_driver_instance(Serial):
                    inst = Serial(*args, **kwargs)
                    AILoggingAPI._drivers.append(inst)
                    self._driver_instance = inst
                else:
                    self._driver_instance = self._get_driver_instance(Serial)
                    
            elif com_driver == 'usb':
                from ai_logging.drivers import UsbWcidDriver

                if not self._has_driver_instance(UsbWcidDriver):
                    inst = UsbWcidDriver(*args, **kwargs)
                    AILoggingAPI._drivers.append(inst)
                    self._driver_instance = inst
                else:
                    self._driver_instance = self._get_driver_instance(UsbWcidDriver)
            else:
                print("Error {} is not a known driver, please provide an instance or a correct string initializer".format(com_driver))

        elif  isinstance(com_driver, DriverInterface):
            if self._has_driver_instance(com_driver.__class__):
                self._driver_instance = com_driver
            else:
                AILoggingAPI._drivers.append(com_driver)
                self._driver_instance = com_driver
        else:
            print("Error can't initialize with an instance that is not a subclass of DriverInterface or a recognized string")
            self._driver_instance = None


        if self._driver_instance is None: # Error when initialising instance => quitting
            print("Error while initializing... no driver instance")
            return
    
        # Assuming driver is correctly connected at this point 
        if not self._driver_instance.is_connected():
            self._driver_instance.connect(*args, **kwargs)
            
    
    def _has_driver_instance(self, i):
        """!
            Helper function that test if an instance of class i is present in the driver list 
        """
        return any([isinstance(x, i) for x in AILoggingAPI._drivers])
    
    
    def _get_driver_instance(self, i):
        """!
        Helper function that returns the instance of a class type specified by i 
        """ 
        out = [x for x in AILoggingAPI._drivers if isinstance(x,i)]
        if len(out) == 0:
            return None
        elif len(out) == 1:
            return out[0]
        else:
            print("Warning: Incoherent state, more than one instance in drivers list")
            return out[0]


    
    def _read(self, nb_byte=None):
        """!
        Wrapper function that make a read on the driver instance
        """
        if nb_byte is None:
            nb_byte = self._driver_instance.byte_available()
        return self._driver_instance.read(nb_byte, *self._args, **self._kwargs)

   
    def _write(self, data):
        """!
        Wrapper function that write data specified to the driver instance 
        """
        return self._driver_instance.write(data, *self._args, **self._kwargs)

    
    def _byte_available(self):
        """!
        Wrapper function that return the number of byte available to be read
        """
        return self._driver_instance.byte_available(*self._args, **self._kwargs)
    

    def data_received_callback(self, data:bytes):
        """!
        Wrapper function to set data received into the AIP buffers
        """
        self._wrapper.data_received_callback(data)


    def check_for_received_packet(self):
        """! Non Blocking API to check if a packet has been received or not
        @return Return an integer greater than 0 if a packet has been received 
        """
        return self._wrapper.check_for_received_packet()


    def wait_for_packet(self):
        """!
        Blocking API that check if data are here
        If header was catched, this function will block until data transfer is complete
        """

        packet = self._wrapper.wait_for_data()
        return packet


    def send_message(self, message:str):
        """!
           @param message send a string message
        """
        return self._wrapper.send_message(message)
        #return self._wrapper.send_data(message, ai_logging_api_wrapper.AILoggingPayloadType.AI_COMMAND, [len(message)])

    def send_packet(self, data, data_type, data_shape=None, message=None, timestamp=None):
        """! Send data packet using API configuration 
        @param data a data to be sent, it can be numpy array, string or bytes
        @param data_type the type to be sent with data
        @param data_shape the shape to be associated with the packet
        @param message a message to be sent with the packet
        @param timestamp a timestamp to be sent with the packet
        """
        packet = {
            'data':None,
            'data_type':None,
            'data_shape':None,
            'timestamp':None,
            'message': None
        }

        if data is not None:
            packet['data'] = data
        
        if data_type is not None:
            packet['data_type'] = data_type
        
        if data_shape is not None:
            packet['data_shape'] = data_shape
        
        if message is not None:
            packet['message'] = message
        
        if timestamp is not None:
            packet['timestamp'] = timestamp

        return self._wrapper.send_packet(packet)