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
    This example sends an image from Computer to an STM32, look at the ImageDisplay example running
    on STM32H747 DISCO Board to see this example working
"""

from ai_logging import AILoggingAPI
from ai_logging.core.ai_logging_api_wrapper import AILoggingPayloadType
import numpy as np
import sys
import threading
import time
from PIL import Image

api = AILoggingAPI('usb', '0x0483:0x5743', read_endpoint=0x81, write_endpoint=0x01)

# You can uncomment the code below to send a violet image to STM32
#shape = (180, 134, 3)
#data = np.array([0xFF, 0x00, 0xFF] * shape[0] * shape[1], dtype=np.uint8) # Violet data image

img = Image.open("st_logo.jpg")
data = np.array(img.getdata(), dtype=np.uint8)
shape = (img.size[0], img.size[1], 3)

def reception_thread():
    print("Starting reception thread", flush=True)
    for i in range(100):
        packet = api.wait_for_packet()
        print(packet['message'], flush=True)
    print("End of thread")


t1 = threading.Thread(target=reception_thread)
t1.daemon = True
t1.start()

start_time = time.time()
for i in range(100):
    try:
        api._wrapper.send_data(data, AILoggingPayloadType.AI_UINT8, [shape[0], shape[1], shape[2]])
        print("Image sent",flush=True)
    except KeyboardInterrupt:
        sys.exit()

end_time = time.time()

print("Finished: {}".format(end_time-start_time), flush=True)


