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


from PySide2.QtWidgets import QWidget, QLabel, QComboBox, QHBoxLayout, QPushButton, QLineEdit, QSpinBox, QTabWidget
from PySide2.QtCore import qDebug, Qt, Slot, Signal
from PySide2.QtSerialPort import QSerialPortInfo


class ConnectionWidget(QWidget):
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        # self.controller.sig_connected.connect(self.s_isConnected)

        self.setWindowTitle("Connection")
        self.isConnected = False

        mainLayout = QHBoxLayout()
        self.setLayout(mainLayout)

        self.tabWidget = QTabWidget(self)
        mainLayout.addWidget(self.tabWidget)

        self.serialConnectionWidget = SerialConnectionWidget(self.controller, self)
        self.usbConnectionWidget = USBConnectionWidget(self.controller, self)

        self.tabWidget.addTab(self.serialConnectionWidget, "Serial")
        self.tabWidget.addTab(self.usbConnectionWidget, "USB")

    def saveSettings(self, settings):
        settings.setValue("connectionwidget/tab", self.tabWidget.currentIndex())
        self.serialConnectionWidget.saveSettings(settings)
        self.usbConnectionWidget.saveSettings(settings)

    def restoreSettings(self, settings):
        try:
            self.tabWidget.setCurrentIndex(int(settings.value("connectionwidget/tab")))
        except:
            pass

        self.serialConnectionWidget.restoreSettings(settings)
        self.usbConnectionWidget.restoreSettings(settings)


class SerialConnectionWidget(QWidget):
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.controller.sig_connected.connect(self.s_isConnected)

        self.setWindowTitle("Serial")
        self.isConnected = False

        mainLayout = QHBoxLayout()
        self.setLayout(mainLayout)

        portLabel = QLabel("Port: ")
        portLabel.setMaximumWidth(50)
        mainLayout.addWidget(portLabel)
        self.portWidget = QComboBox(self)
        self.portWidget.setMaximumWidth(200)
        mainLayout.addWidget(self.portWidget)

        self.baudrate = QSpinBox(self)
        self.baudrate.setMinimum(0)
        self.baudrate.setMaximum(4000000)
        self.baudrate.setValue(115200)
        self.baudrate.setMaximumWidth(100)
        mainLayout.addWidget(self.baudrate)
        

        self.connectButton = QPushButton("Connect")
        self.connectButton.setMaximumWidth(100)
        mainLayout.addWidget(self.connectButton)
        self.connectButton.clicked.connect(self.s_connect)

        self.refreshButton = QPushButton("Refresh")
        self.refreshButton.setMaximumWidth(100)
        mainLayout.addWidget(self.refreshButton)
        self.refreshButton.clicked.connect(self.updateSerialPortList)


        mainLayout.addWidget(QWidget()) #Extensible widget
        self.setMaximumHeight(100)

        self.updateSerialPortList()

    @Slot(bool)
    def s_isConnected(self, state:bool):
        if state:
            self.connectButton.setText("Disconnect")
        else:
            self.connectButton.setText("Connect")


    @Slot()
    def s_connect(self):
        if self.controller.is_connected:
            self.controller.disconnect()
        else:            
            kwargs = {}
            interface_string = self.portWidget.currentText()
            kwargs['baudrate'] = int(self.baudrate.value())
            
            self.controller.connectTo("serial", interface_string, **kwargs)
           
    def updateSerialPortList(self):
        self.portWidget.clear()
        portList = QSerialPortInfo.availablePorts()
        for port in portList:
            self.portWidget.addItem(port.portName())

    def saveSettings(self, settings):
        settings.setValue("serialconnectionwidget/port", self.portWidget.currentText())
        settings.setValue("serialconnectionwidget/baudrate", self.baudrate.value())

    def restoreSettings(self, settings):
        try:
            self.baudrate.setValue(int(settings.value("serialconnectionwidget/baudrate")))
        except:
            pass
        
        self.updateSerialPortList()
        try:
            self.portWidget.setCurrentText(str(settings.value("serialconnectionwidget/port")))
        except:
            pass


class USBConnectionWidget(QWidget):
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.controller.sig_connected.connect(self.s_isConnected)

        self.setWindowTitle("USB")
        self.isConnected = False

        mainLayout = QHBoxLayout()
        self.setLayout(mainLayout)

        portLabel = QLabel("Port: ")
        portLabel.setMaximumWidth(50)
        mainLayout.addWidget(portLabel)
        self.portWidget = QLineEdit()
        self.portWidget.setMaximumWidth(200)
        mainLayout.addWidget(self.portWidget)
        

        self.connectButton = QPushButton("Connect")
        self.connectButton.setMaximumWidth(100)
        mainLayout.addWidget(self.connectButton)
        self.connectButton.clicked.connect(self.s_connect)

        mainLayout.addWidget(QWidget()) #Extensible widget
        self.setMaximumHeight(100)

    @Slot(bool)
    def s_isConnected(self, state:bool):
        if state:
            self.connectButton.setText("Disconnect")
            self.isConnected = True
        else:
            self.connectButton.setText("Connect")
            self.isConnected = False

    @Slot()
    def s_connect(self):
        if self.controller.is_connected:
            self.controller.disconnect()
        else:
            if self.portWidget.text():
                kwargs = {}

                connection_string = self.portWidget.text().split(" ")
                interface_string = connection_string[0]
                connection_string = connection_string[1:]

                for param in connection_string:
                    if len(param.split("=")) == 2:
                        pkey, pvalue = param.split("=")
                        kwargs[pkey] = pvalue
                    else:
                        qDebug("Malformed parameter (key=value) "+str(param))
                
                self.controller.connectTo("usb", interface_string, **kwargs)
            else:
                qDebug("Can't connect with empty connection info")


    def saveSettings(self, settings):
        settings.setValue("usbconnectionwidget/connectionstring", self.portWidget.text())

    def restoreSettings(self, settings):
        try:
            self.portWidget.setText(str(settings.value("usbconnectionwidget/connectionstring")))
        except:
            pass