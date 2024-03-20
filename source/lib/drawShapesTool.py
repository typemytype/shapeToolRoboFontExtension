import AppKit
import vanilla

from fontTools.pens.pointPen import ReverseContourPointPen

from mojo.events import BaseEventTool, installTool
from mojo.extensions import ExtensionBundle


# collecting image data for building cursors and toolbar icons

shapeBundle = ExtensionBundle("ShapeTool")
_cursorOval = CreateCursor(shapeBundle.get("cursorOval"), hotSpot=(6, 6))
_cursorRect = CreateCursor(shapeBundle.get("cursorRect"), hotSpot=(6, 6))

toolbarIcon = shapeBundle.get("toolbarIcon")


class GeometricShapesWindow(object):
    """
    The Modal window that allows numbers input to draw basic geometric shapes.
    """

    def __init__(self, glyph, callback, x, y):
        self.glyph = glyph
        self.callback = callback

        self.w = vanilla.Sheet((200, 160), parentWindow=AppKit.NSApp().mainWindow())

        self.w.infoText = vanilla.TextBox((10, 13, -10, 22), "Add shape:")
        # add some text boxes (labels)
        self.w.xText = vanilla.TextBox((10, 43, 100, 22), "x")
        self.w.yText = vanilla.TextBox((10, 73, 100, 22), "y")
        self.w.wText = vanilla.TextBox((100, 43, 100, 22), "w")
        self.w.hText = vanilla.TextBox((100, 73, 100, 22), "h")

        # adding input boxes
        self.w.xInput = vanilla.EditText((30, 40, 50, 22), "%i" % x)
        self.w.yInput = vanilla.EditText((30, 70, 50, 22), "%i" % y)
        self.w.wInput = vanilla.EditText((120, 40, 50, 22))
        self.w.hInput = vanilla.EditText((120, 70, 50, 22))

        # a radio group with shape choices
        # (RadioGroup is not included in dialogKit, this is a vanilla object)
        self.shapes = ["rect", "oval"]
        self.w.shape = vanilla.RadioGroup((10, 100, -10, 22), self.shapes, isVertical=False)
        self.w.shape.set(0)

        self.w.okButton = vanilla.Button((-70, -30, -15, 20), "OK", callback=self.okCallback, sizeStyle="small")
        self.w.setDefaultButton(self.w.okButton)

        self.w.closeButton = vanilla.Button((-150, -30, -80, 20), "Cancel", callback=self.cancelCallback, sizeStyle="small")
        self.w.closeButton.bind(".", ["command"])
        self.w.closeButton.bind(chr(27), [])

        self.w.open()

    def okCallback(self, sender):
        # draw the shape in the glyph
        # get the shape from the radio group
        shape = self.shapes[self.w.shape.get()]
        # try to get some integers from the input fields
        try:
            x = int(self.w.xInput.get())
            y = int(self.w.yInput.get())
            w = int(self.w.wInput.get())
            h = int(self.w.hInput.get())
        # if this fails just do nothing and print a tiny traceback
        except Exception:
            print("A number is required!")
            return
        # draw the shape with the callback given on init
        self.callback(shape, (x, y, w, h), self.glyph)

    def cancelCallback(self, sender):
        # do nothing :)
        self.w.close()


def _roundPoint(x, y):
    return int(round(x)), int(round(y))


class DrawGeometricShapesTool(BaseEventTool):

    strokeColor = (1, 0, 0, 1)
    reversedStrokColor = (0, 0, 1, 1)

    def setup(self):
        # setup is called when the tool becomes active
        # use this to initialize some attributes
        self.minPoint = None
        self.maxPoint = None
        self.shape = "rect"
        self.origin = "corner"
        self.moveShapeShift = None
        self.shouldReverse = False
        self.shouldUseCubic = True

        drawingLayer = self.extensionContainer("com.typemytype.shapeTool")
        self.pathLayer = drawingLayer.appendPathSublayer(
            fillColor=None,
            strokeColor=self.strokeColor,
            strokeWidth=-1
        )
        self.originLayer = drawingLayer.appendSymbolSublayer(
            visible=False,
            imageSettings=dict(
                name="star",
                pointCount=8,
                inner=0.1,
                outer=1,
                size=(15, 15),
                fillColor=self.strokeColor
            )
        )

    def getRect(self):
        # return the rect between mouse down and mouse up
        x = self.minPoint.x
        y = self.minPoint.y
        w = self.maxPoint.x - self.minPoint.x
        h = self.maxPoint.y - self.minPoint.y

        # handle the shift down and equalize width and height
        if self.shiftDown:
            sign = 1
            if abs(w) > abs(h):
                if h < 0:
                    sign = -1
                h = abs(w) * sign
            else:
                if w < 0:
                    sign = -1
                w = abs(h) * sign

        if self.origin == "center":
            # if the origin is centered, subtract the width and height
            x -= w
            y -= h
            w *= 2
            h *= 2

        # optimize the rectangle so that width and height are always positive numbers
        if w < 0:
            w = abs(w)
            x -= w
        if h < 0:
            h = abs(h)
            y -= h

        return x, y, w, h

    def drawShapeWithRectInGlyph(self, shape, rect, glyph):
        # draw the shape into the glyph
        # tell the glyph something is going to happen (undo is going to be prepared)
        glyph.prepareUndo("Drawing Shapes")

        # get the pen to draw with
        pen = glyph.getPointPen()

        if self.shouldReverse:
            pen = ReverseContourPointPen(pen)

        x, y, w, h = rect

        # draw a rectangle in the glyph using the pen
        if shape == "rect":
            pen.beginPath()
            pen.addPoint(_roundPoint(x, y), "line")
            pen.addPoint(_roundPoint(x + w, y), "line")
            pen.addPoint(_roundPoint(x + w, y + h), "line")
            pen.addPoint(_roundPoint(x, y + h), "line")

            pen.endPath()

        # draw an oval in the glyph using the pen
        elif shape == "oval":
            hw = w / 2.
            hh = h / 2.

            if self.shouldUseCubic:
                r = .55
                segmentType = "curve"
            else:
                r = .42
                segmentType = "qcurve"

            pen.beginPath()
            pen.addPoint(_roundPoint(x + hw, y), segmentType, True)
            pen.addPoint(_roundPoint(x + hw + hw * r, y))
            pen.addPoint(_roundPoint(x + w, y + hh - hh * r))

            pen.addPoint(_roundPoint(x + w, y + hh), segmentType, True)
            pen.addPoint(_roundPoint(x + w, y + hh + hh * r))
            pen.addPoint(_roundPoint(x + hw + hw * r, y + h))

            pen.addPoint(_roundPoint(x + hw, y + h), segmentType, True)
            pen.addPoint(_roundPoint(x + hw - hw * r, y + h))
            pen.addPoint(_roundPoint(x, y + hh + hh * r))

            pen.addPoint(_roundPoint(x, y + hh), segmentType, True)
            pen.addPoint(_roundPoint(x, y + hh - hh * r))
            pen.addPoint(_roundPoint(x + hw - hw * r, y))

            pen.endPath()

        # tell the glyph you are done with your actions so it can handle the undo properly
        glyph.performUndo()
        glyph.changed()

    def mouseDown(self, point, clickCount):
        # a mouse down, only save the mouse down point
        self.minPoint = point
        # on double click, pop up a dialog with input fields
        if clickCount == 2:
            # create and open dialog
            GeometricShapesWindow(self.getGlyph(),
                            callback=self.drawShapeWithRectInGlyph,
                            x=self.minPoint.x,
                            y=self.minPoint.y)

    def mouseDragged(self, point, delta):
        # record the dragging point
        self.maxPoint = point
        # if shift the minPoint by the move shift
        if self.moveShapeShift:
            w, h = self.moveShapeShift
            self.minPoint.x = self.maxPoint.x - w
            self.minPoint.y = self.maxPoint.y - h
        # update layer
        self.updateLayer()

    def mouseUp(self, point):
        # mouse up, if you have recorded the rect draw that into the glyph
        if self.minPoint and self.maxPoint:
            self.drawShapeWithRectInGlyph(self.shape, self.getRect(), self.getGlyph())
        # reset the tool
        self.minPoint = None
        self.maxPoint = None
        # update layer
        self.updateLayer()

    def keyDown(self, event):
        # reverse on tab
        if event.characters() == "\t":
            self.shouldReverse = not self.shouldReverse
            if self.shouldReverse:
                self.pathLayer.setStrokeColor(self.reversedStrokColor)

                settings = self.originLayer.getImageSettings()
                settings["fillColor"] = self.reversedStrokColor
                self.originLayer.setImageSettings(settings)
            else:
                self.pathLayer.setStrokeColor(self.strokeColor)

                settings = self.originLayer.getImageSettings()
                settings["fillColor"] = self.strokeColor
                self.originLayer.setImageSettings(settings)

    def modifiersChanged(self):
        # is being called with modifiers changed (shift, alt, control, command)
        self.shape = "rect"
        self.origin = "corner"

        # change the shape when option is down
        if self.optionDown:
            self.shape = "oval"
        # change the origin when command is down
        if self.commandDown:
            self.origin = "center"
        # change cubic <-> quad when caps lock is down
        self.shouldUseCubic = not self.capLockDown
        if self.shouldUseCubic:
            self.pathLayer.setStrokeDash(None)
        else:
            self.pathLayer.setStrokeDash([5, 3])
        # record the current size of the shape and store it
        if self.controlDown and self.moveShapeShift is None and self.minPoint and self.maxPoint:
            w = self.maxPoint.x - self.minPoint.x
            h = self.maxPoint.y - self.minPoint.y
            self.moveShapeShift = w, h
        else:
            self.moveShapeShift = None
        # update layer
        self.updateLayer()

    def updateLayer(self):
        # update the layers with a new path and position for the origing point
        if self.isDragging() and self.minPoint and self.maxPoint:
            x, y, w, h = self.getRect()
            pen = self.pathLayer.getPen()
            if self.shape == "rect":
                pen.rect((x, y, w, h))
            elif self.shape == "oval":
                pen.oval((x, y, w, h))

            if self.origin == "center":
                self.originLayer.setPosition((x + w / 2, y + h / 2))
                self.originLayer.setVisible(True)
            else:
                self.originLayer.setVisible(False)
        else:
            self.pathLayer.setPath(None)
            self.originLayer.setVisible(False)

    def getDefaultCursor(self):
        # returns the cursor
        if self.shape == "rect":
            return _cursorRect
        else:
            return _cursorOval

    def getToolbarIcon(self):
        # return the toolbar icon
        return toolbarIcon

    def getToolbarTip(self):
        # return the toolbar tool tip
        return "Shape Tool"


# install the tool!!
installTool(DrawGeometricShapesTool())
