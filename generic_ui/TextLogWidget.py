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


from PySide2.QtWidgets import QPlainTextEdit, QWidget, QVBoxLayout
from PySide2.QtCore import Slot, qDebug
from PacketFilterWidget import PacketFilterWidget
from ai_logging.core.ai_logging_api_wrapper import AILoggingPayloadType
from ai_logging.decoders import decoder

class TextLogWidget(QWidget):
    
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.currentFilter = None
        self.acceptedData = [
            AILoggingPayloadType.AI_COMMAND,
            AILoggingPayloadType.AI_STR
        ]

        mainLayout = QVBoxLayout(self)
        self.setLayout(mainLayout)

        self.filterWidget = PacketFilterWidget(self.controller, self)
        self.filterWidget.sig_filterApplied.connect(self.filterUpdated)
        mainLayout.addWidget(self.filterWidget)

        self.textArea = QPlainTextEdit()
        mainLayout.addWidget(self.textArea)

        self.controller.sig_newRawData.connect(self.s_appendRaw)


    @Slot(dict)
    def s_appendRaw(self, data:dict):
        if data.get('data_type', None) and data.get('data_type') in self.acceptedData:
            if self.currentFilter is not None and self.controller.is_data_fitting_filter(data, self.currentFilter):
                dec = decoder.get_decoder_for_data(data)
                decoded_data = dec.decode(data)
                self.textArea.appendPlainText(str(decoded_data))
        
    @Slot()
    def filterUpdated(self):
        self.currentFilter = self.filterWidget.getCurrentFilter()

    def closeEvent(self, closeEvent):
        qDebug("Closing RawTextWidget")
        self.controller.sig_newRawData.disconnect(self.s_appendRaw)
        closeEvent.accept()
