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


import sys, os
from PySide2.QtWidgets import QMainWindow, QMdiArea, QLabel, QMenuBar, QMenu, QDockWidget, QToolBar, QAction, QHBoxLayout, QWidget, QMessageBox, QMdiSubWindow
from PySide2.QtGui import QPixmap, QIcon
from PySide2.QtCore import Qt, qDebug, Slot, QSettings
from Controller import Controller
from ConnectionWidget import ConnectionWidget
from RawTextWidget import RawTextWidget
from PlotWidget import PlotWidget
from TextLogWidget import TextLogWidget
from RecorderWidget import RecorderWidget
from InputWidget import InputWidget
from ImageWidget import ImageWidget

import res

class MainWindow(QMainWindow):

    connectionWidgetName = "Connection"
    plotWidgetName = "PlotWidget"
    rawTextWidgetName = "RawTextWidget"
    textLogWidgetName = "TextLogWidget"
    recorderWidgetName = "RecorderWidget"
    inputWidgetName = "InputWidget"
    imageWidgetName = "ImageWidget"
    GenericUiConfigFileName = "GenericDataLogger_GenericUI.ini"
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.widgetList = []
        self.actionList = []
        self.controller = Controller(parent) # Main  component to interact with Logging API

        self.setWindowTitle("GenericUI")
        self.setMinimumSize(600, 400)
        self.setWindowIcon(QIcon(":/x-cube-ai"))

        self.widgetNameCreatorMapping = { # Mainly used for the reopening of widgets
            self.plotWidgetName: self.s_addNewPlotWindow,
            self.rawTextWidgetName: self.s_addNewRawTextWindow,
            self.textLogWidgetName: self.s_addNewTextLogWidget,
            self.recorderWidgetName: self.s_addNewRecorderWidget,
            self.inputWidgetName: self.s_addNewInputWidget,
            self.imageWidgetName: self.s_addNewImageWidget
        }

        # self.setDockNestingEnabled(True)

        imgCentralWidget = QLabel()
        imgCentralWidget.setAlignment(Qt.AlignCenter)
       
        self.setCentralWidget(imgCentralWidget)

        # self.mdiArea = QMdiArea(self)
        # self.setCentralWidget(self.mdiArea)
        # self.mdiArea.setViewMode(QMdiArea.TabbedView)

        # External Widget declaration
        self.connectionWidget = ConnectionWidget(self.controller)

        # Creating UI with panels
        self.addWidgetToDisplay(self.connectionWidget, self.connectionWidgetName, display='panel', position='top')

        
        actionNewPlotWidget = QAction("Add new Plot Widget", self)
        self.actionList.append(actionNewPlotWidget)
        actionNewPlotWidget.triggered.connect(self.s_addNewPlotWindow)

        actionNewRawTextWidget = QAction("Add new Raw Text Widget", self)
        self.actionList.append(actionNewRawTextWidget)
        actionNewRawTextWidget.triggered.connect(self.s_addNewRawTextWindow)

        actionNewTextLogWidget = QAction("Add new Text Log Widget", self)
        self.actionList.append(actionNewTextLogWidget)
        actionNewTextLogWidget.triggered.connect(self.s_addNewTextLogWidget)

        actionNewRecorderWidget = QAction("Add new Recorder Widget", self)
        self.actionList.append(actionNewRecorderWidget)
        actionNewRecorderWidget.triggered.connect(self.s_addNewRecorderWidget)

        actionNewInputWidget = QAction("Add new Input Widget", self)
        self.actionList.append(actionNewInputWidget)
        actionNewInputWidget.triggered.connect(self.s_addNewInputWidget)

        actionNewImageWidget = QAction("Add new Image Widget", self)
        self.actionList.append(actionNewImageWidget)
        actionNewImageWidget.triggered.connect(self.s_addNewImageWidget)

        # Top menu bar definition
        # self.setMenuBar(self.createMenuBar())
        # ToolBar declaration
        self.addToolBar(self.createToolBar())        

        self.restoreWorkspace()
        self.welcomeMessageCheck()

        

    def quit(self):
        sys.exit(0)

    def addWidgetToDisplay(self, widget, name, display='window', position='top'):
        if display == 'panel':
            position = None
            if position == 'top':
                position = Qt.TopDockWidgetArea
            elif position == 'bottom':
                position = Qt.BottomDockWidgetArea
            elif position == 'left':
                position = Qt.LeftDockWidgetArea
            elif position == 'right':
                position = Qt.RightDockWidgetArea
            else:
                position = Qt.LeftDockWidgetArea
                    
            dockWidget = self.createDockWidgetFromWidget(widget)
            dockWidget.setObjectName(name)
            dockWidget.setFeatures(QDockWidget.DockWidgetFloatable | 
                QDockWidget.DockWidgetMovable | 
                #QDockWidget.DockWidgetVerticalTitleBar |
                QDockWidget.DockWidgetClosable)
            dockWidget.setWindowTitle(name)
            dockWidget.setWindowIcon(QIcon(":/x-cube-ai"))
            

            self.addDockWidget(position, dockWidget)
        else:
            # Adding new to the view
            mdiSubWindow = QMdiSubWindow(self.mdiArea)
            mdiSubWindow.setWidget(widget)
            mdiSubWindow.setWindowTitle(name)
            self.mdiArea.addSubWindow(mdiSubWindow)
            mdiSubWindow.show()

        self.widgetList.append({
            'name':name,
            'widget':widget,
            'display':display,
            'position':position,
            'state':'displayed',
        })

    def createMenuBar(self):
        menuBar = QMenuBar()
        fileMenu = menuBar.addMenu("File")
        fileMenu.addAction("Quit", self.quit)
        
        viewMenu = menuBar.addMenu("View")

        for action in self.actionList:
            viewMenu.addAction(action)    
    
        aboutMenu = menuBar.addMenu("Help")
        aboutMenu.addAction("About", self.showAbout)
        aboutMenu.addAction("Quick help", self.showWelcomeMessage)

        return menuBar

    def createToolBar(self):
        toolBar = QToolBar("Toolbar")
        toolBar.setObjectName("mainwindow_toolbar")
        for action in self.actionList:
            toolBar.addAction(action)
        return toolBar

    def createDockWidgetFromWidget(self, child_widget):
        dockWidget = QDockWidget(self)
        dockWidget.setWidget(child_widget)
        return dockWidget


    # Trampoline slots
    def s_addNewPlotWindow(self):
        qDebug("Adding new PlotWidget window")
        newPlotWidget = PlotWidget(self.controller)
        self.addWidgetToDisplay(newPlotWidget, self.plotWidgetName, display='panel', position='right')

    
    def s_addNewRawTextWindow(self):
        qDebug("Adding new RawTextWidget window")
        newRawTextWidget = RawTextWidget(self.controller)
        self.addWidgetToDisplay(newRawTextWidget, self.rawTextWidgetName, display='panel', position='bottom')


    def s_addNewTextLogWidget(self):
        qDebug("Adding new TextLogWidget window")
        new_widget = TextLogWidget(self.controller)
        self.addWidgetToDisplay(new_widget, self.textLogWidgetName, display='panel', position='left')

    def s_addNewRecorderWidget(self):
        qDebug("Adding new RecorderWidget")
        new_widget = RecorderWidget(self.controller)
        self.addWidgetToDisplay(new_widget, self.recorderWidgetName, display='panel', position='right')

    def s_addNewInputWidget(self):
        qDebug("Adding new InputWidget")
        new_widget = InputWidget(self.controller)
        self.addWidgetToDisplay(new_widget, self.inputWidgetName, display='panel', position='bottom')

    def s_addNewImageWidget(self):
        qDebug("Adding new ImageWidget")
        new_widget = ImageWidget(self.controller)
        self.addWidgetToDisplay(new_widget, self.imageWidgetName, display='panel', position='left')

 
    def showAbout(self):
        QMessageBox.about(self, "About",
                            """<b>GenericUI</b> is a free and open source application aiming at 
                             interfacing with <b>GenericDataLogger</b> API which was developped by <i>STMicroelectronics</i>
                             to respond to AI purpose logging usecases.""")
 

    def saveWorkspace(self):
        settings = QSettings(self.GenericUiConfigFileName, QSettings.IniFormat)
        settings.setValue("mainwindow/geometry", self.saveGeometry())
        settings.setValue("mainwindow/windowState", self.saveState())

        childWidget = []
        for child in self.findChildren(QDockWidget):
            childWidget.append(str(child.objectName()))
        settings.setValue("mainwindow/widgets",childWidget)

        self.connectionWidget.saveSettings(settings)


    def restoreWorkspace(self):
        settings = QSettings("GenericDataLogger_GenericUI.ini", QSettings.IniFormat)
        
        if settings.value("mainwindow/widgets"):
            for child in settings.value("mainwindow/widgets"):
                if self.widgetNameCreatorMapping.get(child, None):
                    self.widgetNameCreatorMapping.get(child)() # Calling the creator

        self.restoreGeometry(settings.value("mainwindow/geometry"))
        self.restoreState(settings.value("mainwindow/windowState"))
        self.connectionWidget.restoreSettings(settings)


    def closeEvent(self, event):
        self.saveWorkspace()
        event.accept()
        
    def welcomeMessageCheck(self):
        if not os.path.exists(self.GenericUiConfigFileName):
            self.showWelcomeMessage()
    
    def showWelcomeMessage(self):
        msgBox = QMessageBox(self)
        msgBox.setWindowTitle("GenericUI: Quick help")
        msgBox.setText("<b>Welcome</b> in GenericUI !")
        msgBox.setInformativeText("Interface details:\n- You can show/widget as you want\n- You can move/resize widgets to create your own workspace\n- You workspace is saved when you click X")
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.setDefaultButton(QMessageBox.Ok)
        msgBox.exec_()