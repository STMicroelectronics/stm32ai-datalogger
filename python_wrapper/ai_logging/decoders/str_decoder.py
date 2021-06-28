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


from ai_logging.core.ai_logging_api_wrapper import AILoggingPayloadType

#TODO: Standard interface for decoders
class StrDecoder:

    def decode(self, data:dict):
        out_str = None
        if data['data_type'] == AILoggingPayloadType.AI_STR:
            data_array = data['data']
            out_str = ''.join(chr(x) for x in data_array)
            #print("StrDecoder: {}".format(out_str))
        elif data['data_type'] == AILoggingPayloadType.AI_COMMAND:
            if data.get('message', None):
                out_str = data.get('message')
            else:
                raise Exception("Trying to decode message as str but no message received")
        else:
            raise Exception("DataType to decode not supported by StrDecoder")
        return out_str
