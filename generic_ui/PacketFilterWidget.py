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


from PySide2.QtWidgets import QLabel, QComboBox, QWidget, QGroupBox, QHBoxLayout, QPushButton
from PySide2.QtCore import qDebug, Slot, Signal

class PacketFilterWidget(QWidget):
    sig_filterApplied = Signal()

    def __init__(self, controller, parent=None, validation_button=True):
        super().__init__(parent)
        self.controller = controller

        self.setMaximumHeight(100)

        mainLayout = QHBoxLayout(self)
        self.setLayout(mainLayout)

        groupBox = QGroupBox("Filter")
        mainLayout.addWidget(groupBox)

        subLayout = QHBoxLayout()
        groupBox.setLayout(subLayout)
        # mainLayout.addWidget(QLabel("Filter: "))

        self.filterCombo = QComboBox(self)
        self.filterCombo.setMinimumWidth(200)
        subLayout.addWidget(self.filterCombo)

        if validation_button:
            filterButton = QPushButton("Apply")
            filterButton.clicked.connect(self.sig_filterApplied)
            subLayout.addWidget(filterButton)
        else:
            self.filterCombo.currentIndexChanged.connect(self.s_userChangedFilter)
        
        self.controller.sig_filterUpdated.connect(self.filterUpdated)


    @Slot()
    def filterUpdated(self):
        if self.filterCombo.count() != len(self.controller.get_filters_name()):
            self.filterCombo.clear()

            for f in self.controller.get_filters_name():
                self.filterCombo.addItem(f)

    @Slot(int)
    def s_userChangedFilter(self, index):
        self.sig_filterApplied.emit()

    def getCurrentFilter(self):
        return self.filterCombo.currentText()
