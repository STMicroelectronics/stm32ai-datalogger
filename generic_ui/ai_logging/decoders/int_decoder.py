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
# from ai_logging.core import constants as C
from ai_logging.core.ai_logging_api_wrapper import AILoggingPayloadType

#TODO: Standard interface for decoders
class IntDecoder():
	def decode(self, data:dict):
		if data['data_type'] == AILoggingPayloadType.AI_UINT8:
			byte_for_type = 1
			signed = False
		elif data['data_type'] == AILoggingPayloadType.AI_INT8:
			byte_for_type = 1
			signed = True
		elif data['data_type'] == AILoggingPayloadType.AI_UINT16:
			byte_for_type = 2
			signed = False
		elif data['data_type'] == AILoggingPayloadType.AI_INT16:
			byte_for_type = 2
			signed = True
		elif data['data_type'] == AILoggingPayloadType.AI_UINT32:
			byte_for_type = 4
			signed = False
		elif data['data_type'] == AILoggingPayloadType.AI_INT32:
			byte_for_type = 4
			signed = True
		else:
			raise Exception("IntDecoder: Unable to decode, data not supported")

		shape = None
		if data['data_shape']:
			shape = data['data_shape']
		else:
			print("IntDecoder: No shape detected, assuming 1-dim array")
			shape = None

		data_array = data['data']

		return self._decode_int(data_array, byte_for_type, signed, shape)

	
	def _decode_int(self, data, byte_for_type:int, signed:bool, shape):
		nb_element = int(len(data)/byte_for_type)
		# if len(shape) != 3:
		# 	raise Exception("Missing shape information while decoding int")
		output_data = np.zeros(nb_element)

		for i in range(nb_element):
			output_data[i] = int.from_bytes(data[i*byte_for_type:i*byte_for_type+byte_for_type], 
								byteorder='little', signed=signed)

		output_data = output_data.reshape(shape) if shape is not None else output_data
		return output_data
			
