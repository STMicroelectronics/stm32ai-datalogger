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


from PySide2.QtWidgets import QPlainTextEdit
from PySide2.QtCore import Slot, qDebug

class RawTextWidget(QPlainTextEdit):
    
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.controller.sig_newRawData.connect(self.s_appendRaw)

    @Slot(dict)
    def s_appendRaw(self, data:dict):
        self.appendPlainText(str(data)+"\n")
        
    def closeEvent(self, closeEvent):
        qDebug("Closing RawTextWidget")
        self.controller.sig_newRawData.disconnect(self.s_appendRaw)
        closeEvent.accept()
