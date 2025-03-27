from PySide6 import QtWidgets, QtCore, QtGui
from ..widgets import PushButton

class PopupDialog(QtWidgets.QDialog):
    """Базовое всплывающее окно поверх родителя.

    Что принимает?
    ------------
    parent: `QWidget`
        Родительский виджет. Необходим для измерения расположения всплывающего окна.
    width: `int`
        Ширина виджета. Если `None`, тогда ширина будет на 10 меньше родительского виджета.
    height: `int`
        Высота виджета. Если `None`, тогда высота будет на 10 меньше родительского виджета.
    addButtons: `bool`
        Кнопки в окне. По умолчанию это `Ok` и `Cancel`
    """
    def __init__(self, 
                 parent: QtWidgets.QWidget, 
                 width = None, 
                 height = None, 
                 addButtons = True
                 ):
        super().__init__(parent)
        self.effect = QtWidgets.QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.effect)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setObjectName("popup")
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.WindowStaysOnTopHint)
        self.setFixedSize(width if width != None else parent.width()-10,
                          height if width != None else parent.height()-10)
        self.previousEvent = None
        size = self.parent().size()
        self.previousSize = size
        self.move(QtCore.QPoint(size.width() // 2  - self.width() // 2,
                    size.height() // 2 - self.height() // 2))
        
        self.showAnimation = QtCore.QPropertyAnimation(self.effect, b"opacity")
        self.showAnimation.setDuration(60)
        self.showAnimation.setStartValue(0.0)
        self.showAnimation.setEndValue(1.0)

        self.hideAnimation = QtCore.QPropertyAnimation(self.effect, b"opacity")
        self.hideAnimation.setDuration(60)
        self.hideAnimation.setStartValue(1.0)
        self.hideAnimation.setEndValue(0.0)

        self.coreLayout = QtWidgets.QVBoxLayout()
        self.widgetsLayout = QtWidgets.QVBoxLayout()
        self.buttonsLayout = QtWidgets.QVBoxLayout()

        self.coreLayout.addLayout(self.widgetsLayout)


        self.setLayout(self.coreLayout)

    def addWidget(self, widget: QtWidgets.QWidget, alignment: QtCore.Qt.AlignmentFlag = QtCore.Qt.AlignmentFlag.AlignCenter):
        """Добавляет виджет в всплывающее окно
        
        Чё принимает?
        -----------------
        widget: `QWidget`
            Виджет, который необходимо добавить в окно
        alignment: `QtCore.Qt.AlignmentFlag`
            Выравнивание. Изначально стоит выравивание по центру
        """
        self.widgetsLayout.addWidget(widget, alignment=alignment)

    def paintEvent(self, a0):
        """Переопределяет СВОё расположение относительно родителя из-за изменения размеров родителя"""
        size = self.parent().size()

        if size == self.previousSize:
            return
        
        self.previousSize = size
        self.move(QtCore.QPoint(size.width() // 2  - self.width() // 2,
                                size.height() // 2 - self.height() // 2))

        return super().paintEvent(a0)
    
    def event(self, a0):
        if a0.type() == a0.Type.Hide and self.previousEvent != a0.Type.WindowDeactivate:
            self.previousEvent = None
            self.close()

        self.previousEvent = a0.type() if a0.type() == a0.Type.WindowDeactivate else None
        
        return super().event(a0)
    
    def close(self):
        """Переопределённый метод `close`\n
        Основная проблема в том, что анимация закрытия окна моментально перекрывается явным закрытием окна, поэтому close был поставлен на таймер
        """
        self.hideAnimation.start()
        return QtCore.QTimer.singleShot(self.hideAnimation.duration()+1, super().close)
  
    def showEvent(self, a0):
        self.showAnimation.start()
        return super().showEvent(a0)
 

