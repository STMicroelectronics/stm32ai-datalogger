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


from PySide2.QtCore import qDebug, Slot, Signal, QTimer
from PySide2.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
import pyqtgraph as pg
import numpy as np
from collections import deque
from ai_logging.decoders import decoder
from ai_logging.core.ai_logging_api_wrapper import AILoggingPayloadType
from PacketFilterWidget import PacketFilterWidget
from ComboCheckBox import ComboCheckBox


class PlotWidget(QWidget):
    def __init__(self, controller, nb_line=1, parent=None):
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

        self._window_size = 200
        self.colors = ['r','g','b']

        mainLayout = QVBoxLayout(self)
        mainLayout.setMargin(0)
        self.setLayout(mainLayout)

        controlLayout = QHBoxLayout() # Managing the top bar
        mainLayout.addLayout(controlLayout)

        self.filterWidget = PacketFilterWidget(self.controller, self)
        self.filterWidget.sig_filterApplied.connect(self.s_updateFilter)
        controlLayout.addWidget(self.filterWidget)

        # controlLayout.addWidget(QLabel("Selected lines:"))
        self.selectedLines = ComboCheckBox(self)
        self.selectedLines.sig_hasUpdate.connect(self.s_updateLines)
        controlLayout.addWidget(self.selectedLines)

        self._plot = pg.PlotWidget()
        self._plot.getPlotItem().hideAxis('bottom')
        self._plot.getPlotItem().showButtons()

        mainLayout.addWidget(self._plot)
        
        self._lines = []
        self.reset(nb_lines=nb_line)

        self.updateTimer = QTimer(self) # Setting up the timer to update UI
        self.updateTimer.timeout.connect(self.update_plot)
        self.updateTimer.start(50)
    
        self.controller.sig_newRawData.connect(self.s_rawDataReceived)




    @Slot(dict) 
    def s_rawDataReceived(self, data:dict):
        if data.get('data_type',None) and data.get('data_type') in self.acceptedData:
            if self.currentFilter is not None and self.controller.is_data_fitting_filter(data, self.currentFilter):
                if data.get('data_shape', None) is not None and len(data.get('data_shape')) == 1:
                    # Only accept 1 dimensions to be plotted for now
                    dec = decoder.get_decoder_for_data(data)
                    decoded_data = dec.decode(data)
                    data_to_display = decoded_data

                    if self.currentMask is None or len(self.currentMask) != len (decoded_data):
                        for i in range(len(data_to_display)): # Updating Lines selection in UI
                            self.selectedLines.setCheckedItem("Line:"+str(i+1))

                    if self.currentMask is not None and len(self.currentMask) == len(decoded_data):
                        data_to_display = [decoded_data[i] for i in range(len(decoded_data)) if self.currentMask[i] != 0]
                    
                    if len(data_to_display) != len(self._lines):
                        self.reset(len(data_to_display)) # Updating graph with correct number of line
                    self.add_data(data_to_display)


    @Slot()
    def s_updateFilter(self):
        self.currentFilter = self.filterWidget.getCurrentFilter()


    @Slot()
    def s_updateLines(self):
        self.currentMask = self.selectedLines.getCheckedMask()


    def reset(self, nb_lines=1):
            self._data = deque(maxlen=self._window_size)
            self._data.append([0]*nb_lines) # First value to avoid crashing

            for line in self._lines:
                self._plot.removeItem(line)

            self._lines = []
            
            for i in range(nb_lines):
                self._lines.append(self._plot.plot(pen=self.colors[i%len(self.colors)], symbol='o'))


    def update_plot(self):
        for i in range(len(self._lines)):
            y_to_plot = list(self._data)#[-(self._window_size+1):]
            ydata = np.array(y_to_plot)
            ydata = ydata[:,i]
            self._lines[i].setData(ydata)


    def add_data(self, data:[]):
        if len(data) == len(self._lines) and len(data) > 0:
            self._data.append(data)
        else:
            qDebug("Error data size not equal lines size: "+str(len(data))+","+str(len(self._lines)))


    def closeEvent(self, event):
        qDebug("Closing PlotWidget")
        self.controller.sig_newRawData.disconnect(self.s_rawDataReceived)
        event.accept()
