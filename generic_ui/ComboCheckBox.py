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


from PySide2.QtWidgets import QComboBox, QCheckBox
from PySide2.QtGui import QStandardItemModel, QStandardItem
from PySide2.QtCore import Signal, Slot, Qt, QTimer

class ComboCheckBox(QComboBox):
    sig_hasUpdate = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.displayedText = ""
        self.model = QStandardItemModel()
        self.setEditable(True)
        self.lineEdit().setReadOnly(True)

        self.s_updateText()
        self.model.itemChanged.connect(self.s_update)

    def addItem(self, text:str, checked=False):
        row = self.model.rowCount()

        item = QStandardItem()
        item.setText(text)
        item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
        if checked:
            item.setData(Qt.Checked, Qt.CheckStateRole)
        else:    
            item.setData(Qt.Unchecked, Qt.CheckStateRole)
        self.model.setItem(row, 0, item)
        self.setModel(self.model)

    def addItems(self, textList:list):
        for text in textList:
            self.addItem(text)

    def getCheckedItems(self):
        out = []
        for i in range(self.model.rowCount()):
            if self.model.item(i, 0).checkState() == Qt.Checked:
                out.append(self.model.item(i, 0).text())
        return out

    def setCheckedItem(self, text):
        idx = self.findText(text)
        if idx != -1:
            self.model.item(idx).setData(Qt.Checked, Qt.CheckStateRole)
        else:
            self.addItem(text, checked=True)
        self.s_update()

    def getCheckedMask(self):
        out = []
        for i in range(self.model.rowCount()):
            if self.model.item(i, 0).checkState() == Qt.Checked:
                out.append(1)
            else:
                out.append(0)
        return out

    @Slot()
    def s_updateText(self):
        if self.lineEdit():
            self.lineEdit().setText(self.displayedText)

    @Slot()
    def s_update(self):
        self.displayedText = ""
        for i in range(self.model.rowCount()):
            if self.model.item(i, 0).checkState() == Qt.Checked:
                self.displayedText += self.model.item(i,0).text()+"; "
        
        QTimer.singleShot(0, self.s_updateText)
        self.sig_hasUpdate.emit()