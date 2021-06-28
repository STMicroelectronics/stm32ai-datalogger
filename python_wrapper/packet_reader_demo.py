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


"""!
    Simple example reading data on channel specified

    First question, on which communication channel are you trying to read the data from ? 
    Configure below the commmunication interface you need (serial/usb, ComPort/VID:PID)    
"""

from ai_logging import AILoggingAPI
from ai_logging.decoders.decoder import get_decoder_for_data


api = AILoggingAPI('serial', 'COM29', read_size=0) # Serial connection
# api = AILoggingAPI('usb', '0x0483:0x5743', read_endpoint=0x81) # USB WCID connection using USB 'VID:PID' syntax

while True:
    packet = api.wait_for_packet()
    
    if packet is not None:
        if packet.get('message', None) is not None:
            print("Message: {}".format(packet.get('message')))

        if packet.get('data', None) is not None:        
            decoder_to_use = get_decoder_for_data(packet)
            decoded_data = decoder_to_use.decode(packet)
            print("Packet received: {}".format(decoded_data), flush=True)
