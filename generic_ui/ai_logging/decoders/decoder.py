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


from enum import Enum
from .int_decoder import IntDecoder
from .str_decoder import StrDecoder
from .float_decoder import FloatDecoder

from ai_logging.core.ai_logging_api_wrapper import AILoggingPayloadType

INT_DECODER = IntDecoder()
STR_DECODER = StrDecoder()
FLOAT_DECODER = FloatDecoder()
# Syntax: str_type: (decoder)
STR_TO_DECODER = {
    AILoggingPayloadType.AI_COMMAND: (STR_DECODER),
    AILoggingPayloadType.AI_INT8: (INT_DECODER),
    AILoggingPayloadType.AI_UINT8: (INT_DECODER),
    AILoggingPayloadType.AI_INT16: (INT_DECODER),
    AILoggingPayloadType.AI_UINT16: (INT_DECODER),
    AILoggingPayloadType.AI_UINT32: (INT_DECODER),
    AILoggingPayloadType.AI_INT32: (INT_DECODER),
    AILoggingPayloadType.AI_STR:(STR_DECODER),
    AILoggingPayloadType.AI_FLOAT:(FLOAT_DECODER)
}

def get_decoder_for_data(packet):
    if packet['data_type'] in STR_TO_DECODER:
        return STR_TO_DECODER[packet['data_type']]
    else:
        return None

class DecoderInterface:
    def decode(self, datatype):
        print("Not implemented")
