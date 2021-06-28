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


from ai_logging import AILoggingAPI
from ai_logging.core.ai_logging_api_wrapper import AILoggingPayloadType
from PySide2.QtCore import QObject, Signal, Slot, qDebug, QSettings, QTimer
from StreamReader import StreamReader

class Controller(QObject):
    # Signals
    sig_connected = Signal(bool)
    sig_newRawData = Signal(dict)
    sig_filterUpdated = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.api = None
        self.id_channels = [] # Store the list of different channel based on their ID (COMMAND + DATA)
        self.type_channels = [] # Store the list of channels based on their types
        self.dimension_channels = []

        self._must_check_value = 10 # Counter to know how many samples have to be tested to updated channel list

        self.slowUpdateTimer = QTimer(self)
        self.slowUpdateTimer.timeout.connect(self.s_slowTimerTimeout)
        self.slowUpdateTimer.start(1000)

        self.is_connected = False


    def connectTo(self, interface:str, *args, **kwargs):  
        qDebug("[Controller] Connecting to {} using {} and {}".format(interface, args, kwargs))
        try:
            self.api = AILoggingAPI(interface, *args, **kwargs)
            self.is_connected = True
            self.sig_connected.emit(True)

            self.streamReader = StreamReader(self)
            self.streamReader.setApiInstance(self.api)
            self.streamReader.sig_packetAvailable.connect(self.s_dataReceived)
            self.streamReader.start()
            qDebug("Connected")
        except Exception as e:
                qDebug("Error: "+str(e))
                self.is_connected = False
                self.sig_connected.emit(False)


    def disconnect(self):
        self.streamReader.terminate()
        self.api = None
        self.is_connected = False
        self.sig_connected.emit(False)


    @Slot(dict)
    def s_dataReceived(self, data:dict):
        if self._must_check_value > 0:
            # Case if data + message (ID)
            if data.get('data', None) and data.get('message', None) and data.get('message') not in self.id_channels:
                self.id_channels.append(data.get('message'))

            # Case if data with dimensions
            if data.get('data_shape', None) and len(data.get('data_shape')) not in self.dimension_channels:
                self.dimension_channels.append(len(data.get('data_shape')))

            # Case by data type
            if data.get('data_type') and data.get('data_type') not in self.type_channels:
                self.type_channels.append(data.get('data_type')) 

            if self._must_check_value == 10:
                self.sig_filterUpdated.emit()
                #qDebug("Filter detected: "+str(self.get_filters_name()))
            self._must_check_value -= 1

        self.sig_newRawData.emit(data)

    @Slot()
    def s_slowTimerTimeout(self):
        if self._must_check_value <= 0: # Update only if reached 0
            self._must_check_value = 10

    def get_filters_name(self):
        """
        Provide the list of string to use as filter
        """
        out = ["(default)"]
        for a in self.id_channels:
            out.append("ID:"+str(a))

        for a in self.type_channels:
            out.append("Type:"+str(AILoggingPayloadType.string(a)))

        for a in self.dimension_channels:
            out.append("Dim:"+str(a))
        
        return out


    def is_data_fitting_filter(self, data:dict, filter:str):
        if filter == '(default)':
            return True
        elif filter.startswith('ID:'):
            if data.get('message', None) and data.get('data',None):
                if 'ID:' + str(data.get('message')) == filter:
                    return True
                else:
                    return False
        elif filter.startswith('Type:'):
            if data.get('data_type', None) and 'Type:'+str(AILoggingPayloadType.string(data.get('data_type'))) == filter:
                return True
            else:
                return False
        elif filter.startswith('Dim:'):
            if data.get('data_shape', None) and 'Dim:'+str(len(data.get('data_shape'))) == filter:
                return True
            else:
                return False
        else:
            return False


    def sendMessage(self, message):
        self.api.send_message(message)

    def sendTextData(self, textData):
        self.api.send_packet(data, AI_STR, data_shape=[len(textData)])

    def sendData(self, data, dataType, shape):
        self.api.send_packet(data, dataType, data_shape=shape)

    