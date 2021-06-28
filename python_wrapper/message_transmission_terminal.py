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
    Simple example that is demonstrating how you can transfer messages from Host to STM32 and vice versa.
    Send is done classically and reception is done in a separate Thread.

    Note: 
    Here you can see that we are settings 'read_size=0'. In the serial context, this option is useful to 
    tell the underlying serial driver to read as much as he can (and return) to avoid reading the packet 
    T at T+1 when the next packet is received (realtime communication).
    You can leave this option with the default value otherwise.

"""

import ai_logging as ail
import threading
import sys
import time


com_port = input("Enter you com port name: ")

device = ail.AILoggingAPI('serial', com_port, read_size=0)


def reception_thread():
    print("Starting reception thread", flush=True)
    while True:
        packet = device.wait_for_packet()
        print("Message from STM32 [{}]\n".format(packet['message'], flush=True), flush=True)

t1 = threading.Thread(target=reception_thread)
#t1.daemon = True
t1.start()

while True: 
    time.sleep(1)
    message_to_send = input("Message:")
    if message_to_send == "quit":
        sys.exit(0)
    print("Sending:[{}]\n".format(message_to_send))
    device.send_message(message_to_send)

