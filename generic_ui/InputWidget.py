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


from PySide2.QtWidgets import QWidget, QLineEdit, QFileDialog, QHBoxLayout, QVBoxLayout, QLabel, QGroupBox, QPushButton
from PySide2.QtCore import Slot, qDebug

class InputWidget(QWidget):
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller

        mainLayout = QVBoxLayout(self)
        
        # Message input
        messageInputGroup = QGroupBox("Send message")
        messageInputGrouLayout = QHBoxLayout(messageInputGroup)
        messageInputGroup.setLayout(messageInputGrouLayout)
        mainLayout.addWidget(messageInputGroup)

        self.messageInput = QLineEdit()
        self.messageInput.setPlaceholderText("Enter message")
        messageInputGrouLayout.addWidget(self.messageInput)

        messageSendButton = QPushButton("Send")
        messageSendButton.clicked.connect(self.s_sendMessage)
        messageInputGrouLayout.addWidget(messageSendButton)

        # File input
        fileInputGroup = QGroupBox("Send text file")
        fileInputGroupLayout = QHBoxLayout(fileInputGroup)
        fileInputGroup.setLayout(fileInputGroupLayout)
        mainLayout.addWidget(fileInputGroup)

        browseButton= QPushButton("Browse text file...")
        fileInputGroupLayout.addWidget(browseButton)
        browseButton.clicked.connect(self.s_browseFile)
        self.selectedFile = None
        self.fileChoosenLabel = QLabel("No file selected")

        fileSendButton = QPushButton("Send text file")
        fileSendButton.clicked.connect(self.s_sendFile)
        fileInputGroupLayout.addWidget(fileSendButton)



    @Slot()
    def s_sendMessage(self):
        qDebug("Sending message: "+str(self.messageInput.text()))
        self.controller.sendMessage(self.messageInput.text())
        self.messageInput.clear()

    @Slot()
    def s_sendFile(self):
        if self.selectedFile is not None:
            with open(self.selectedFile) as f:
                qDebug("Sending file: "+str(self.selectedFile))
                data = f.read()
                self.controller.sendTextData(data)
                f.close()
        else:
            qDebug("You have to choose a file first")


    @Slot()
    def s_browseFile(self):
        fileChoosen = QFileDialog.getOpenFileName(self, "Open a file")
        if fileChoosen is not None and fileChoosen[0] != '':
            self.selectedFile = fileChoosen[0]
            self.fileChoosenLabel.setText(self.selectedFile)
        else:
            self.selectedFile = None
            self.fileChoosenLabel.setText("No file selected")

