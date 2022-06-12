import sys, math
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
        
class OutlinedLabel(QLabel):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.w = 1 / 25
        self.line_space = 1
        self.max_lines = 3
        self.mode = True
        self.setBrush(Qt.white)
        self.setPen(Qt.black)

    def scaledOutlineMode(self):
        return self.mode

    def setScaledOutlineMode(self, state):
        self.mode = state

    def outlineThickness(self):
        return self.w * self.font().pointSize() if self.mode else self.w

    def setOutlineThickness(self, value):
        self.w = value

    def setLineSpace(self, value):
        self.line_space = value

    def setMaxLines(self, value):
        self.max_lines = value

    def setBrush(self, brush):
        if not isinstance(brush, QBrush):
            brush = QBrush(brush)
        self.brush = brush

    def setPen(self, pen):
        if not isinstance(pen, QPen):
            pen = QPen(pen)
        pen.setJoinStyle(Qt.RoundJoin)
        self.pen = pen

    def sizeHint(self):
        w = math.ceil(self.outlineThickness() * 2)
        return super().sizeHint() + QSize(w, w)
    
    def minimumSizeHint(self):
        w = math.ceil(self.outlineThickness() * 2)
        return super().minimumSizeHint() + QSize(w, w)
    
    def paintEvent(self, event):
        w = self.outlineThickness()
        rect = self.rect()
        metrics = QFontMetrics(self.font())
        tr = metrics.boundingRect(self.text()).adjusted(0, 0, w, w)
        if self.indent() == -1:
            if self.frameWidth():
                indent = (metrics.boundingRect('x').width() + w * 2) / 2
            else:
                indent = w
        else:
            indent = self.indent()

        if self.alignment() & Qt.AlignLeft:
            x = rect.left() + indent - min(metrics.leftBearing(self.text()[0]), 0)
        elif self.alignment() & Qt.AlignRight:
            x = rect.x() + rect.width() - indent - tr.width()
        else:
            x = (rect.width() - tr.width()) / 2
            
        if self.alignment() & Qt.AlignTop:
            y = rect.top() + indent + metrics.ascent()
        elif self.alignment() & Qt.AlignBottom:
            y = rect.y() + rect.height() - indent - metrics.descent()
        else:
            y = (rect.height() + metrics.ascent() - metrics.descent()) / 2

        self.x = x
        self.y = y
        self.pen.setWidthF(w * 2)
        if self.wordWrap() and len(self.getTextLines()) > 1:
            self.paintTextLines(w)
        else:
            path = QPainterPath()
            path.addText(x, y, self.font(), self.text())
            qp = QPainter(self)
            qp.setRenderHint(QPainter.RenderHint.Antialiasing)

            qp.strokePath(path, self.pen)
            #if 1 < self.brush.style() < 15:
                #qp.fillPath(path, self.palette().window())
            qp.fillPath(path, self.brush)

    def getTextLines(self):
        return self.text().splitlines()

    def paintTextLines(self, w):
        lines = self.getTextLines()
        fm = QFontMetrics(self.font())
        if len(lines) <= self.max_lines:
            y = self.y - ((len(lines) - 1) / 2 * fm.height()) - self.line_space
        else:
            y = self.y - ((self.max_lines - 1) / 2 * fm.height()) - self.line_space
        qp = QPainter(self)
        qp.setRenderHint(QPainter.RenderHint.Antialiasing)

        for line in lines:
            x = self.x
            path = QPainterPath()
            path.addText(x, y, self.font(), line)

            qp.strokePath(path, self.pen)
            #if 1 < self.brush.style() < 15:
                #qp.fillPath(path, self.palette().window())
            qp.fillPath(path, self.brush)

            y += fm.height() + self.line_space