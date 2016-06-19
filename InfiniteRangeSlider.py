import math
import sys

from PySide.QtCore import *
from PySide.QtGui import *

from reference.scientificspin import ScientificDoubleSpinBox

__author__ = 'David'

# Number of ticks on slider - only used for UI purposes
NUM_TICKS = 500

class InfiniteRangeSlider(QWidget):
    # Define signal
    valueChanged = Signal(float)

    def __init__(self, startValue):
        super(InfiniteRangeSlider, self).__init__()

        self._value = startValue

        layout = QHBoxLayout()

        self.setLayout(layout)
        self.spinbox = ScientificDoubleSpinBox()
        self.spinbox.setValue(self._value)
        self.spinbox.setMinimumWidth(100)
        layout.addWidget(self.spinbox)
        self.spinbox.valueChanged.connect(self.setNewValue)

        self.slider = QSlider(Qt.Horizontal, self)
        layout.addWidget(self.slider)
        self.slider.setMinimum(-NUM_TICKS/2)
        self.slider.setMaximum(NUM_TICKS/2)
        self.slider.setValue(0)
        self.slider.setTracking(True)
        self.slider.valueChanged.connect(self.updateSpinner)
        self.slider.sliderReleased.connect(lambda: self.setNewValue(self.spinbox.value()))
        self.slider.setMinimumWidth(150)

    def sizeHint(self):
        return QSize(300,20)

    def value(self):
        return self._value

    def setValue(self, value):
        self.setNewValue(value)



    # While the slider is still tracking around, just update the spinner but don't do anything else
    def updateSpinner(self, sliderValue):
        # Compute the actual value corresponding to this slider value
        # We want it so that the centre of the slider is the current value,
        # with -inf and +inf at the ends,
        # and 0 is halfway from the centre to the end in the appropriate direction
        # => use a tan-based function!
        newVal = self._value + abs(self._value) * math.tan((sliderValue/(0.5*NUM_TICKS)) * (math.pi/2))
        # Stop the spinbox from emitting events
        self.spinbox.blockSignals(True)
        self.spinbox.setValue(newVal)
        self.spinbox.blockSignals(False)

    # When the slider is released, jump it back to its centre position, and update the widget's internal value
    # Or if the spinner is updated
    def setNewValue(self, value):
        if value != self._value:
            self._value = value

            # Disable recursive signals and reset slider
            self.slider.blockSignals(True)
            self.slider.setValue(0)
            self.slider.blockSignals(False)

            # Update spinner
            self.spinbox.blockSignals(True)
            self.spinbox.setValue(value)
            self.spinbox.blockSignals(False)

            # Emit signal
            self.valueChanged.emit(value)

    # Set the size hint correctly
    #def sizeHint(self):
    #    width = 100 + self.slider.width()
    #    return QSize(width,self.height())


class InfiniteRangeSliderTest(QWidget):

    def __init__(self):
        super(InfiniteRangeSliderTest, self).__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.islider = InfiniteRangeSlider(10)
        layout.addWidget(self.islider)
        self.val_label = QLabel(self)
        layout.addWidget(self.val_label)

        # Connect signal
        self.islider.valueChanged.connect(self.updateLabel)

        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Infinite Range Slider Test')
        self.show()

    def updateLabel(self, value):
        self.val_label.setText(str(value))

def main():

    app = QApplication(sys.argv)
    ex = InfiniteRangeSliderTest()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()