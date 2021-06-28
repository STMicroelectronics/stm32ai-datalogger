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


from PySide2.QtCore import qDebug, Slot, Signal, QTimer, Qt
from PySide2.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide2.QtGui import QImage, QPixmap
import numpy as np
from ai_logging.decoders import decoder
from ai_logging.core.ai_logging_api_wrapper import AILoggingPayloadType
from PacketFilterWidget import PacketFilterWidget

class ImageWidget(QWidget):
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller

        self.acceptedData = [
            AILoggingPayloadType.AI_INT16,
            AILoggingPayloadType.AI_INT32,
            AILoggingPayloadType.AI_INT8,
            AILoggingPayloadType.AI_UINT16,
            AILoggingPayloadType.AI_UINT32,
            AILoggingPayloadType.AI_UINT8,
        ]

        self.currentFilter = "(default)"
        self.currentMask = None

        mainLayout = QVBoxLayout(self)
        mainLayout.setMargin(0)
        self.setLayout(mainLayout)

        controlLayout = QHBoxLayout()
        mainLayout.addLayout(controlLayout)

        self.filterWidget = PacketFilterWidget(self.controller, self)
        self.filterWidget.sig_filterApplied.connect(self.s_updateFilter)
        controlLayout.addWidget(self.filterWidget)

        self.imageInfo = QLabel("Image info: -")
        mainLayout.addWidget(self.imageInfo)

        self.imageSpace = QLabel("No image")
        self.imageSpace.setScaledContents(True)
        mainLayout.addWidget(self.imageSpace, Qt.AlignCenter)

        self.controller.sig_newRawData.connect(self.s_rawDataReceived)


    @Slot()
    def s_updateFilter(self):
        self.currentFilter = self.filterWidget.getCurrentFilter() 


    @Slot(dict)
    def s_rawDataReceived(self, data:dict):
        if data.get('data_type',None) and data.get('data_type') in self.acceptedData:
            if self.currentFilter is not None and self.controller.is_data_fitting_filter(data, self.currentFilter):
                qimage_format = None
                dec = decoder.get_decoder_for_data(data)
                decoded_data = None

                if len(data.get('data_shape')) == 3:
                    if data.get('data_type') == AILoggingPayloadType.AI_UINT8 or data.get('data_type') == AILoggingPayloadType.AI_INT8:
                        qimage_format = QImage.Format_RGB888
                        decoded_data = np.array(dec.decode(data), dtype=np.uint8)

                    elif data.get('data_type') == AILoggingPayloadType.AI_UINT16 or data.get('data_type') == AILoggingPayloadType.AI_INT16:
                        qimage_format = QImage.Format_RGB16
                        decoded_data = np.array(dec.decode(data), dtype=np.uint16)

                    elif data.get('data_type') == AILoggingPayloadType.AI_UINT32 or data.get('data_type') == AILoggingPayloadType.AI_INT32:
                        qimage_format = QImage.Format_RGB32
                        decoded_data = np.array(dec.decode(data), dtype=np.uint32)

                    if qimage_format is not None and decoded_data is not None:
                        shape = data.get('data_shape')
                        self.imageInfo.setText("Image dim:{}".format(shape))

                        qImg = QImage(decoded_data.data, shape[0], shape[1], shape[2]*shape[1], qimage_format)
                        self.imageSpace.setPixmap(QPixmap(qImg)) # Qt.KeepAspectRatio
