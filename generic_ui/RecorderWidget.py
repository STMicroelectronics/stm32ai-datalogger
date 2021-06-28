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


from PySide2.QtWidgets import QWidget, QPushButton, QGroupBox, QHBoxLayout,QLineEdit, QVBoxLayout, QLabel, QComboBox, QCheckBox, QFileDialog
from PySide2.QtCore import Signal, Slot, qDebug
from PacketFilterWidget import PacketFilterWidget
from ComboCheckBox import ComboCheckBox
from Exporter import Exporter
from ai_logging.decoders import decoder
from ai_logging.core.ai_logging_api_wrapper import AILoggingPayloadType

class RecorderWidget(QWidget):

    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        
        self.currentFilter = "(default)"
        self.currentMask = None
        self.saved_data = []
        self.current_data = []
        self.isRecording = False


        mainLayout = QVBoxLayout(self)

        topLayout = QHBoxLayout()
        mainLayout.addLayout(topLayout)

        self.filterWidget = PacketFilterWidget(self.controller, self, validation_button=False)
        self.filterWidget.sig_filterApplied.connect(self.s_updateFilter)
        topLayout.addWidget(self.filterWidget)

        topLayout.addWidget(QWidget())

        self.labelWidget = LabelWidget(self)
        topLayout.addWidget(self.labelWidget)

        middleLayout = QHBoxLayout()
        mainLayout.addLayout(middleLayout)

        self.startButton = QPushButton("Start")
        middleLayout.addWidget(self.startButton)
        self.startButton.clicked.connect(self.s_changeRecordingState)

        self.recordingCounter = QLabel("Current data recorded: -")
        middleLayout.addWidget(self.recordingCounter)

        clearButton = QPushButton("Clear")
        clearButton.clicked.connect(self.s_clearData)
        middleLayout.addWidget(clearButton)

        saveCurrentCapture = QPushButton("Save capture")
        saveCurrentCapture.clicked.connect(self.s_saveCurrentCapture)
        middleLayout.addWidget(saveCurrentCapture)

        bottomLayout = QHBoxLayout()
        mainLayout.addLayout(bottomLayout)

        self.dataSavedLabel = QLabel("Data saved: -")
        bottomLayout.addWidget(self.dataSavedLabel)

        bottomLayout.addWidget(QLabel("Export data to:"))

        self.exportCombo = QComboBox(self)
        self.exportCombo.addItems([Exporter.EXPORT_TO_CSV, Exporter.EXPORT_TO_NUMPY_NPY, Exporter.EXPORT_TO_RAW])
        bottomLayout.addWidget(self.exportCombo)

        exportButton = QPushButton("Export")
        exportButton.clicked.connect(self.s_exportData)
        bottomLayout.addWidget(exportButton)


        self.controller.sig_newRawData.connect(self.s_rawDataReceived)

    @Slot(dict) 
    def s_rawDataReceived(self, data:dict):
        if data.get('data_type',None):
            if self.currentFilter is not None and self.controller.is_data_fitting_filter(data, self.currentFilter) and self.isRecording:
                if self.labelWidget.hasLabel():
                    data['label'] = self.labelWidget.getLabel()
                self.add_data(data)

    @Slot()
    def s_updateFilter(self):
        self.currentFilter = self.filterWidget.getCurrentFilter()

    @Slot()
    def s_changeRecordingState(self):
        if self.isRecording: # Switching from record to stop
            self.startButton.setText("Start")
            self.isRecording = False
        else: # Switching from stop to start mode
            self.startButton.setText("Stop")
            self.isRecording = True

    @Slot()
    def s_clearData(self):
        self.current_data.clear()
        self.recordingCounter.setText("Recorded data: "+str(len(self.current_data)))

    def add_data(self, data):
        self.current_data.append(data)
        self.recordingCounter.setText("Recorded data: "+str(len(self.current_data)))


    def closeEvent(self, event):
        qDebug("Closing RecorcderWidget")
        self.controller.sig_newRawData.disconnect(self.s_rawDataReceived)
        event.accept()

    @Slot()
    def s_saveCurrentCapture(self):
        self.saved_data.extend(self.current_data)
        self.dataSavedLabel.setText("Data saved: "+str(len(self.saved_data)))
        self.current_data.clear()

    @Slot()
    def s_exportData(self):
        if len(self.saved_data) > 0:
            qDebug("Sample of data to save: "+str(self.saved_data[0]))
            folderPath = QFileDialog.getExistingDirectory(self, "Select output folder")
            qDebug("Destination folder: {}".format(folderPath))
            
            e = Exporter(self.exportCombo.currentText(), folderPath)
            e.process(self.saved_data)

            self.saved_data.clear()
        else:
            qDebug("No data to export")



class LabelWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.setMaximumHeight(100)

        mainLayout = QHBoxLayout(self)
        mainLayout.setMargin(0)

        groupBox = QGroupBox("Labelling", self)
        mainLayout.addWidget(groupBox)

        subLayout = QHBoxLayout()
        groupBox.setLayout(subLayout)

        self.labelCheckbox = QCheckBox("Enable label")
        subLayout.addWidget(self.labelCheckbox)
        self.labelCheckbox.stateChanged.connect(self.s_stateChanged)

        self.labelInput = QLineEdit(self)
        self.labelInput.setEnabled(False)
        self.labelInput.setPlaceholderText("Enter label")
        subLayout.addWidget(self.labelInput)

    @Slot(int)
    def s_stateChanged(self, state):
        if state:
            self.labelInput.setEnabled(True)
        else:
            self.labelInput.setEnabled(False)

    def hasLabel(self):
        return self.labelCheckbox.isChecked()

    def getLabel(self):
        if self.hasLabel():
            return self.labelInput.text()
        else:
            return None
    