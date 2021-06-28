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

import os
import ctypes
import enum
import numpy as np
from numpy import ctypeslib
import array

AI_LOGGING_MAX_N_SHAPES = 8


def _wrap_api(lib, funcname, restype, argtypes):
    """Simplify wrapping CTypes functions."""
    func = getattr(lib, funcname)
    func.restype = restype
    func.argtypes = argtypes
    return func

def get_data_info(data):
    if isinstance(data, str):
        a = array.array('B')
        a.fromstring(data)
        address, length = a.buffer_info()
        length *= a.itemsize
        return address,length,a

    elif isinstance(data, np.ndarray):
        if data.dtype == np.float64:
            data = np.array(data, dtype=np.float32)
        
        a = array.array('B')
        a.frombytes(data.tobytes())
        address, length = a.buffer_info()
        length *= a.itemsize
        return address,length,a

    elif isinstance(data, bytes):
        a = array.array('B')
        a.frombytes(data)
        address, length = a.buffer_info()
        length *= a.itemsize
        return address,length,a
    else:
        print("Can't get address of type:",type(data))
        return None,None,None



class ai_logging_device_t(ctypes.Structure):
        """!
            Structure used to wrap Python data with C compiled dyamic library
            ai_logging_device_t is the structure holding data about send/receive function and various internal data
        """
        _fields_ = [
            ('send_buffer',ctypes.POINTER(ctypes.c_uint8)),
            ('send_buffer_max_size', ctypes.c_uint32),
            ('send_buffer_position', ctypes.c_uint32),
            ('send_all_buffer', ctypes.c_uint8),

            ('receive_buffer', ctypes.POINTER(ctypes.c_uint8)),
            ('receive_buffer_position', ctypes.c_uint32),
            ('receive_buffer_read_from', ctypes.c_uint32),
            ('receive_buffer_max_size', ctypes.c_uint32),
            ('receive_fptr_size_to_read', ctypes.c_uint32),
            
            ('send_fptr', ctypes.CFUNCTYPE(
                ctypes.c_uint32,
                ctypes.POINTER(ctypes.c_uint8),
                ctypes.c_uint32)),
            ('receive_fptr', ctypes.CFUNCTYPE(
                ctypes.c_uint32, 
                ctypes.POINTER(ctypes.c_uint8),
                ctypes.c_uint32)),
            
            ('copy_next_byte_in_user_buffer', ctypes.c_int32),
            ('user_raw_buffer', ctypes.POINTER(ctypes.c_uint8)),
            ('user_buffer_position', ctypes.c_uint32),

            ('send_function_ctx', ctypes.c_void_p),
            ('receive_function_ctx', ctypes.c_void_p),
            ('send_ctx_fptr', ctypes.CFUNCTYPE(
                ctypes.c_uint32,
                ctypes.c_void_p,
                ctypes.POINTER(ctypes.c_uint8),
                ctypes.c_uint32)),
            ('receive_ctx_fptr', ctypes.CFUNCTYPE(
                ctypes.c_uint32,
                ctypes.c_void_p,
                ctypes.POINTER(ctypes.c_uint8),
                ctypes.c_uint32)),

            ('error_callback', ctypes.CFUNCTYPE(None)),

            ('enable_auto_prepare_next_packet', ctypes.c_uint8)
        ]
        

class AILoggingPayloadType:
    """!
        Class holding mapping between data types and their values
    """
    AI_NONE =0x00
    AI_COMMAND=0x01
    AI_SHAPE=0x02
    AI_TIMESTAMP=0x03
    AI_INT16=0x5
    AI_UINT16=0x6
    AI_INT32=0x7
    AI_UINT32=0x8
    AI_STR=0x9
    AI_INT8=0xA
    AI_UINT8=0xB
    AI_FLOAT=0xC

    @staticmethod
    def string(value):
        if value == 0x00:
            return "AI_NONE"
        elif value == 0x01:
            return "AI_COMMAND"
        elif value == 0x02:
            return "AI_SHAPE"
        elif value == 0x03:
            return "AI_TIMESTAMP"
        elif value == 0x05:
            return "AI_INT16"
        elif value == 0x06:
            return "AI_UINT16"
        elif value == 0x07:
            return "AI_INT32"
        elif value == 0x08:
            return "AI_UINT32"
        elif value == 0x09:
            return "AI_STR"
        elif value == 0x0A:
            return "AI_INT8"
        elif value == 0x0B:
            return "AI_UINT8"
        elif value == 0x0C:
            return "AI_FLOAT"
        else:
            return "AI_UNKNOWN"


class ai_logging_shape(ctypes.Structure):
    """!
        Structure used to wrap Python data with C compiled dyamic library
        ai_logging_shape hold the shape of data
    """
    _fields_ = [
        ('n_shape', ctypes.c_uint16),
        ('shapes', ctypes.c_uint16*AI_LOGGING_MAX_N_SHAPES)
    ]



class ai_logging_packet_t(ctypes.Structure):
    """!
        Structure used to wrap Python data with C compiled dyamic library
        ai_logging_packet_t structure holds user data that has to be sent or that have been received 
    """
    _fields_ = [
        ('packet_size', ctypes.c_uint32),
        ('payload_type', ctypes.c_uint8),
        ('payload', ctypes.POINTER(ctypes.c_uint8)),
        ('payload_size', ctypes.c_uint32),
        ('shape', ai_logging_shape),
        ('message', ctypes.POINTER(ctypes.c_uint8)),
        ('message_size', ctypes.c_uint8),
        ('timestamp', ctypes.c_int32)
    ]



class ai_logging_buffer(ctypes.Structure):
    """!
        Structure used to wrap Python data with C compiled dyamic library
        ai_logging_buffer structure holds data buffer of user
    """
    _fields_ = [
        ('size', ctypes.c_uint32),
        ('buffer', ctypes.POINTER(ctypes.c_uint8))
    ]



class ai_logging_message(ctypes.Structure):
    """!
        Structure used to wrap Python data with C compiled dyamic library
        ai_logging_message structure holds message buffer of user
    """
    _fields_ = [
        ('size', ctypes.c_uint8),
        ('buffer', ctypes.POINTER(ctypes.c_uint8))
    ]



class ai_logging_tensor(ctypes.Structure):
    """!
        Structure used to wrap Python data with C compiled dyamic library
        ai_logging_tensor structure holds metadata of user data
    """
    _fields_ = [
        ('data_type', ctypes.c_uint8),
        ('shape', ctypes.POINTER(ai_logging_shape))
    ]



class AILoggingBackend:
    """!
        Class that is wrapping dynamic library functions ni Python
        User should not use those functions directly
    """
    def __init__(self):
        self._shared_lib = None
        library_folder = os.path.dirname(__file__)
        try:
            self._shared_lib = ctypeslib.load_library('libai_logging', library_folder)
        except Exception as e:
            self._shared_lib = None
            print("Error: Unable to load the library file in {}: {}".format(library_folder, e))


        self.ai_logging_init = _wrap_api(
            self._shared_lib,
            'ai_logging_init',
            None,
            [ctypes.POINTER(ai_logging_device_t)])

        # Just ctypes's function prototype
        self.callback_func_prototype = ctypes.CFUNCTYPE(
                ctypes.c_uint32, 
                ctypes.POINTER(ctypes.c_uint8),
                ctypes.c_uint32)
        
        self.ai_logging_init_send = _wrap_api(
            self._shared_lib,
            'ai_logging_init_send',
            None,
            [ctypes.POINTER(ai_logging_device_t),
            self.callback_func_prototype,
            ctypes.POINTER(ctypes.c_uint8),
            ctypes.c_uint32])
        
        self.ai_logging_init_receive = _wrap_api(
            self._shared_lib,
            'ai_logging_init_receive',
            None,
            [ctypes.POINTER(ai_logging_device_t),
            self.callback_func_prototype,
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_uint8),
            ctypes.c_uint32])

        self.ai_logging_init_raw_data_buffer = _wrap_api(
            self._shared_lib,
            'ai_logging_init_raw_data_buffer',
            None,
            [ctypes.POINTER(ai_logging_device_t),
            ctypes.POINTER(ctypes.c_uint8)])

        self.ai_logging_send_message_with_data = _wrap_api(
            self._shared_lib,
            'ai_logging_send_message_with_data',
            None,
            [
                ctypes.POINTER(ai_logging_device_t),
                ai_logging_message,
                ai_logging_buffer,
                ai_logging_tensor
            ])

        self.ai_logging_send_data = _wrap_api(
            self._shared_lib,
            'ai_logging_send_data',
            None,
            [
                ctypes.POINTER(ai_logging_device_t),
                ai_logging_buffer,
                ai_logging_tensor
            ])

        self.ai_logging_send_message = _wrap_api(
            self._shared_lib,
            'ai_logging_send_message',
            None,
            [
                ctypes.POINTER(ai_logging_device_t),
                ai_logging_message
            ])


        self.ai_logging_data_received_callback = _wrap_api(
            self._shared_lib,
            'ai_logging_data_received_callback',
            None,
            [
                ctypes.POINTER(ai_logging_device_t),
                ctypes.POINTER(ctypes.c_uint8),
                ctypes.c_uint32
            ])

        self.ai_logging_check_for_received_packet = _wrap_api(
            self._shared_lib,
            'ai_logging_check_for_received_packet',
            ctypes.c_int32,
            [
                ctypes.POINTER(ai_logging_device_t),
                ctypes.POINTER(ai_logging_packet_t)
            ])

        self.ai_logging_wait_for_data = _wrap_api(
            self._shared_lib,
            'ai_logging_wait_for_data',
            ctypes.c_int32,
            [
                ctypes.POINTER(ai_logging_device_t),
                ctypes.POINTER(ai_logging_packet_t)
            ])

        self.ai_logging_prepare_next_packet = _wrap_api(
            self._shared_lib,
            'ai_logging_prepare_next_packet',
            None,
            [
                ctypes.POINTER(ai_logging_device_t)
            ])
        
        self.ai_logging_send_header_for_raw_data = _wrap_api(
            self._shared_lib,
            'ai_logging_send_header_for_raw_data',
            None,
            [
                ctypes.POINTER(ai_logging_device_t),
                ctypes.c_uint8, # data_type
                ctypes.c_uint32 # total data size
            ])
        
        self.ai_logging_send_raw_data = _wrap_api(
            self._shared_lib,
            'ai_logging_send_raw_data',
            None,
            [
                ctypes.POINTER(ai_logging_device_t),
                ctypes.POINTER(ctypes.c_uint8), # Buffer
                ctypes.c_uint32 # bufer size
            ])

        self.ai_logging_purge = _wrap_api(
            self._shared_lib,
            'ai_logging_purge',
            None,
            [
                ctypes.POINTER(ai_logging_device_t),
                ctypes.c_uint32
            ])
        self.ai_logging_send_packet = _wrap_api(
            self._shared_lib,
            'ai_logging_send_packet',
            None,
            [
                ctypes.POINTER(ai_logging_device_t),
                ctypes.POINTER(ai_logging_packet_t)
            ])


class AILoggingAPIWrapper:
    """!
        Wrapper class that wraps low level functions from AILoggingBackend to 'Python' level functions
        providing the C library services from a more 'Pythonic' point of view.
        This class also wraps send/receive functions and buffers directly into itself to avoid manually declaring 
        them in Python.
        User can use this middle-level API to suits their needs.
        @param send_function the send function that will be used to send the data. Function need to have 1 parameter that is the data to send
        @param receive_function function that will be used to receive data. This function take a size to read as parameter and returns the data received
        @param receive_fptr_read_length the default size to read data from receive function
        @param send_buffer_size the default size of send_buffer (if data is bigger than buffer_size, the packet will be send directly, not copied internally)
        @param receive_buffer_max_size size of the reception buffer
        @param raw_buffer_size size of the reception buffer for raw type packets
    """
    def __init__(self, send_function, receive_function, receive_fptr_read_length=16, send_buffer_size=512, receive_buffer_max_size=1000000, raw_buffer_size=1000000):
        self.send_function = send_function
        self.receive_function = receive_function

        self.backend = AILoggingBackend()

        self.send_buffer = np.zeros(send_buffer_size, dtype=np.uint8)
        self.receive_buffer = np.zeros(receive_buffer_max_size, dtype=np.uint8)
        self.raw_buffer = np.zeros(raw_buffer_size, dtype=np.uint8)
        self.c_device = ai_logging_device_t()
        self.receive_packet = ai_logging_packet_t()


        self.backend.ai_logging_init(ctypes.byref(self.c_device))
        
        @ctypes.CFUNCTYPE(ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint8),ctypes.c_uint32)
        def ghosted_send_function(data, size):
            #print("Ghosted send function:",data,size)
            if self.send_function is not None:
                byte_data = bytes(bytearray(data[:size])) # We need to convert data from ctypes to python's bytes
                res = self.send_function(byte_data)
                if res is None:
                    print("Error: send function return None, did you returned the number of byte sent ?")
                return res
            return 0
        self.ghosted_send_function = ghosted_send_function
        
        self.backend.ai_logging_init_send(ctypes.byref(self.c_device), \
            self.ghosted_send_function, \
            self.send_buffer.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8)),\
            send_buffer_size)


        @ctypes.CFUNCTYPE(ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint8),ctypes.c_uint32)
        def ghosted_receive_function(data, size_to_read):
            #print("Ghosted receive function")
            if self.receive_function is not None:
                data_received = self.receive_function(size_to_read)
                self.data_received_callback(data_received)
            return 0 # Here we always return 0 to not change internal buffer position because it is already updated in data_received_callback
        self.ghosted_receive_function = ghosted_receive_function

        self.backend.ai_logging_init_receive(ctypes.byref(self.c_device), \
            self.ghosted_receive_function, \
            receive_fptr_read_length, \
            self.receive_buffer.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8)),\
            receive_buffer_max_size)
        
        self.backend.ai_logging_init_raw_data_buffer(ctypes.byref(self.c_device), \
            self.raw_buffer.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8)))


        print("[INFO] Wrapping and init of API: DONE")
        

    def send_data(self, data, payload_type, shape:list):
        """!
            Send data using the send function defined, specifying the data, the payload_type and shape
            @param data data to be sent, can be numpy array, string or bytes
            @param payload_type the type of data to be sent referenced in AILoggingPayloadType class
            @param shape a list containing the data shapes. Ex [2, 3] to specify a 2 by 3 data array
            @return returns None
        """
        address, length, arr = get_data_info(data) # Need to get arr otherwise python delete this object from memory
        if address is None or length is None:
            print("Error with data format")
            return

        data_buffer = ai_logging_buffer()
        data_buffer.buffer = ctypes.cast(address, ctypes.POINTER(ctypes.c_ubyte)) 
        data_buffer.size = length
        
        s = ai_logging_shape()
        s.n_shape = (ctypes.c_uint16)(len(shape))
        s.shapes = (ctypes.c_uint16 * AI_LOGGING_MAX_N_SHAPES)(*shape)
        
        data_info = ai_logging_tensor()
        data_info.shape = ctypes.pointer(s)
        data_info.data_type = ctypes.c_uint8(payload_type)

        self.backend.ai_logging_send_data(ctypes.byref(self.c_device), 
            data_buffer, data_info)

    
    def send_message_with_data(self, message, data, payload_type, shape:list):
        """!
            Send data with a message in the same packet
            @param message the message to be sent, can be numpy array, string ot bytes
            @param data data to be sent, can be numpy array, string or bytes
            @param payload_type the type of data to be sent referenced in AILoggingPayloadType class
            @param shape a list containing the data shapes. Ex [2, 3] to specify a 2 by 3 data array
            @return returns None
        """
        msg_address, msg_length, msg_arr = get_data_info(message) # Need to get arr otherwise python delete this object from memory
        if msg_address is None or msg_length is None:
            print("Error with message format")
            return
        msg_data_addr = ctypes.cast(msg_address, ctypes.POINTER(ctypes.c_ubyte))

        message_struct = ai_logging_message()
        message_struct.size = msg_length
        message_struct.buffer = msg_data_addr
        
        s = ai_logging_shape()
        s.n_shape = (ctypes.c_uint16)(len(shape))
        s.shapes = (ctypes.c_uint16 * AI_LOGGING_MAX_N_SHAPES)(*shape)
        
        data_address, data_length, data_arr = get_data_info(data)
        if data_address is None or data_length is None:
            print("Error with data format")
            return

        data_buffer = ai_logging_buffer()
        data_buffer.buffer = ctypes.cast(data_address, ctypes.POINTER(ctypes.c_ubyte)) 
        data_buffer.size = data_length

        data_info = ai_logging_tensor()
        # data_info.shape = s
        data_info.shape = ctypes.cast(ctypes.byref(s), ctypes.POINTER(ai_logging_shape))

        data_info.data_type = ctypes.c_uint8(payload_type)

        self.backend.ai_logging_send_message_with_data(ctypes.byref(self.c_device), 
            message_struct, data_buffer, data_info)


    def send_message(self, message):
        """!
            Send simple message
            @param message the message to be sent, can be numpy array, string ot bytes
            @return returns None
        """
        address, length, arr, = get_data_info(message)
        if address is None or length is None:
            print("Error with data format")
            return
        
        message = ai_logging_message()
        message.buffer = ctypes.cast(address, ctypes.POINTER(ctypes.c_uint8))
        message.size = ctypes.c_uint8(length) 
        
        self.backend.ai_logging_send_message(ctypes.byref(self.c_device), message)


    def data_received_callback(self, data):
        """!
            The callback used to set data received into the internal API data structures
            @param data the data to be added into the buffer, can be numpy, string, or bytes
        """
        address, length, arr = get_data_info(data)
        if address is None or length is None:
            print("Error with data format")
            return
        data_addr = ctypes.cast(address, ctypes.POINTER(ctypes.c_ubyte))
        self.backend.ai_logging_data_received_callback(ctypes.byref(self.c_device),
            data_addr, length)


    def check_for_received_packet(self):
        """!
            Non blocking function that is checking if a packet has been received.
            @return a dictionnary representing the packet if a packet has been received, otherwise return None 
        """
        ret = self.backend.ai_logging_check_for_received_packet(
            ctypes.byref(self.c_device),
            ctypes.byref(self.receive_packet)
        )
        #print("CheckForPacket Ret: ", ret)
        if ret > 0:
            json_packet = {
                'message':None,
                'data':None,
                'data_type':None,
                'data_shape':None,
                'timestamp':None
            }
            json_packet['data_type'] = self.receive_packet.payload_type
            json_packet['data_shape'] = self.receive_packet.shape.shapes[:self.receive_packet.shape.n_shape]
            json_packet['timestamp'] = self.receive_packet.timestamp

            if self.receive_packet.payload_size > 0:
                json_packet['data'] = self.receive_packet.payload[0:self.receive_packet.payload_size]
            if self.receive_packet.message_size > 0:
                json_packet['message'] = self.receive_packet.message[0:self.receive_packet.message_size] 
            #self.backend.ai_logging_prepare_next_packet(ctypes.byref(self.c_device))
            return json_packet
        else:
            if ret == -5:
                print("[CheckForReceivedPacket]: Corrupted packet")
            return None

    def wait_for_data(self):
        """!
            Blocking function that is waiting for a packet to be received to returns, this packet should return
            the packet as a dictionnary. If return None an error occurs during the reception
        """
        ret = self.backend.ai_logging_wait_for_data(
            ctypes.byref(self.c_device),
            ctypes.byref(self.receive_packet)
        )

        if ret > 0:
            json_packet = {
                'message':None,
                'data':None,
                'data_type':None,
                'data_shape':None,
                'timestamp': None
            }
            json_packet['data_type'] = self.receive_packet.payload_type
            json_packet['data_shape'] = self.receive_packet.shape.shapes[:self.receive_packet.shape.n_shape]
            json_packet['timestamp'] = self.receive_packet.timestamp

            if self.receive_packet.payload_size > 0:
                json_packet['data'] = self.receive_packet.payload[0:self.receive_packet.payload_size]
            if self.receive_packet.message_size > 0:
                json_packet['message'] = self.receive_packet.message[0:self.receive_packet.message_size]
                json_packet['message'] = ''.join([chr(x) for x in json_packet['message']])
            #self.backend.ai_logging_prepare_next_packet(ctypes.byref(self.c_device))
            return json_packet
        else:
            if ret == -5:
                print("[CheckForReceivedPacket]: Corrupted packet")
            return None

    
    def send_packet(self, packet:dict):
        """!
            Simple method to send a packet object. The packet object should contains data that represents
            the packet. You can fill this object with fields such as 'timestamp', 'message', 'data', 'data_shape',
            'data_type'. 
            @param packet is a packet object (dictionnary) that is holding packet data
            @return None
        """
        packet_t = ai_logging_packet_t()

        if packet.get('timestamp', None) is not None:
            packet_t.timestamp = packet.get('timestamp', -1)
        else:
            packet_t.timestamp = -1
        
        message_addr = 0
        message_length = 0
        message_arr = None
        if packet.get('message', None) is not None:
            message_addr, message_length, message_arr = get_data_info(packet.get('message'))
            packet_t.message = ctypes.cast(message_addr, ctypes.POINTER(ctypes.c_ubyte))
            packet_t.message_size = message_length

        data_addr = 0, 
        data_length = 0, 
        data_arr = None
        if packet.get('data', None) is not None and packet.get('data_type', None) is not None:
            data_addr, data_length, data_arr = get_data_info(packet.get('data'))
            packet_t.payload = ctypes.cast(data_addr, ctypes.POINTER(ctypes.c_ubyte))
            packet_t.payload_size = data_length
            packet_t.payload_type = packet.get('data_type')

        if packet.get('data_shape', None) is not None:
            # s = ai_logging_shape()
            packet_t.shape.n_shape = (ctypes.c_uint16)(len(packet.get('data_shape')))
            packet_t.shape.shapes = (ctypes.c_uint16 * AI_LOGGING_MAX_N_SHAPES)(*packet.get('data_shape'))
            # packet_t.shape = s
        else:
            # s = ai_logging_shape()
            # s.n_shape = (ctypes.c_uint16)(0)
            # packet_t.shape = s
            packet_t.shape.n_shape = 0
            packet_t.shape.shapes = (ctypes.c_uint16 * AI_LOGGING_MAX_N_SHAPES)(*[])


        self.backend.ai_logging_send_packet(ctypes.byref(self.c_device),ctypes.byref(packet_t))


    def send_raw_data_header(self, data_type, total_data_length):
        """!
            Send header of raw data packet. This is the fonction you have to use if you want to
            use the raw packet feature.
            @param data_type the custom data type you want to use, it can be an AILoggingPayloadType 
            or a custom type that you define
            @param total_data_length the total length of the data that you want to send
        """
        self.backend.ai_logging_send_header_for_raw_data(
            ctypes.byref(self.c_device),
            data_type,
            total_data_length
        )

    def send_raw_data(self, data):
        """!
            Send the data you defined with send_raw_data_header of total_data_length size.
            You can call this function as many time as you want to sent all your data
            @param data the data you want to send, it can be numpy array, string og bytes
        """
        address, length, arr = get_data_info(data)
        if address is None or length is None:
            print("Error with data format")
            return
        data_addr = ctypes.cast(address, ctypes.POINTER(ctypes.c_ubyte))
        self.backend.ai_logging_send_raw_data(
            ctypes.byref(self.c_device),
            data_addr, length)

