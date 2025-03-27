from PySide6.QtWidgets import QScrollArea, QWidget, QVBoxLayout, QTextEdit, QHBoxLayout, QBoxLayout
from PySide6 import QtCore
from datetime import datetime
from typing import Union


class ScrollArea(QScrollArea):
    def __init__(self, hideScrollBar: bool = False, layoutType: Union[QVBoxLayout, QHBoxLayout] = QVBoxLayout, isInverted = False):
        super().__init__()
        self.isInverted = isInverted
        self.setWidgetResizable(True)
        self.setObjectName("Channel")
        self.verticalScrollBar().setHidden(hideScrollBar)

        self.scrollWidget = QWidget()
        # self.scrollWidget.setAutoFillBackground(False)
        
        self.scrollLayout: QBoxLayout = layoutType()
        self.scrollWidget.setLayout(self.scrollLayout)
        self.scrollLayout.addStretch(1) if self.isInverted == False else ...
        self.scrollLayout.addSpacing(0)
        self.setWidget(self.scrollWidget)

    def addWidget(self, widget: Union[QWidget, QBoxLayout], alignment = QtCore.Qt.AlignmentFlag.AlignLeft, index = -1):
        if self.isInverted and self.scrollLayout.count() > 1:

            widgetItem = self.scrollLayout.takeAt(self.scrollLayout.count()-1)
            if isinstance(widgetItem, QWidget):
                widgetItem.deleteLater()

        if isinstance(widget, QWidget):
            self.scrollLayout.insertWidget(index, widget, alignment=alignment)
        elif isinstance(widget, QBoxLayout):
            self.scrollLayout.insertLayout(index, widget)
        self.scrollLayout.addStretch(1) if self.isInverted else ...

        QtCore.QTimer.singleShot(5, lambda: self.verticalScrollBar().setValue(self.verticalScrollBar().maximum()+50))

    def delWidget(self, item: QWidget | QBoxLayout):
        self.scrollLayout.removeItem(item)
        if isinstance(item, QWidget):
            item.deleteLater()
        elif isinstance(item, QBoxLayout):
            # Подразумеваю, что первый элемент лэйаута - виджет
            item = item.takeAt(0).widget()
            if item is not None:
                item.deleteLater()
        
    


