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


from PySide2.QtCore import qDebug, Signal, Slot, QThread

class StreamReader(QThread):
    sig_packetAvailable = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.apiInstance = None
        self.packets_received = []

    def setApiInstance(self, instance):
        self.apiInstance = instance


    def run(self):
        while self.apiInstance is not None:
            packet = self.apiInstance.wait_for_packet()
            self.sig_packetAvailable.emit(packet)
