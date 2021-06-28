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


import numpy as np
from ai_logging.core.ai_logging_api_wrapper import AILoggingPayloadType
import struct

class FloatDecoder():
    def decode(self, data:dict):
        if data['data_type'] == AILoggingPayloadType.AI_FLOAT:
            byte_for_type = 4
        else:
            raise Exception("FloatDecoder: Unable to decode, data not supported")

        shape = None
        if data['data_shape']:
            shape = data['data_shape']
        else:
            print("FloatDecoder: No shape detected, assuming 1-dim array")
            shape = None

        data_array = data['data']

        return self._decode_float(data_array, byte_for_type, shape)


    def _decode_float(self, data, byte_for_type:int, shape):
        nb_element = int(len(data)/byte_for_type)
        output_data = np.zeros(nb_element)
        
        for i in range(nb_element):
            output_data[i] = struct.unpack('f', bytes(data[i*byte_for_type:i*byte_for_type+byte_for_type]))[0]

        output_data = output_data.reshape(shape) if shape is not None else output_data
        return output_data
            
