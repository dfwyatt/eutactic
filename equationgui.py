import io
import sys

import numpy as np
import pyqtgraph as pg
from PySide.QtCore import *
from PySide.QtGui import *
from pydot import Dot, Node, Edge

from InfiniteRangeSlider import InfiniteRangeSlider
from equationsolver import ScalarVariable, Context
from parsedproblem import ParsedProblem, testfilename

__author__ = 'David Wyatt'

# Code from StackOverflow
# To capture stdout and redirect to a text field
# http://stackoverflow.com/questions/8356336/how-to-capture-output-of-pythons-interpreter-and-show-in-a-text-widget
class EmittingStream(QObject):

    textWritten = Signal(str)

    def write(self, text):
        self.textWritten.emit(str(text))

    def flush(self):
        pass

class EquationGui(QMainWindow):
    def __init__(self, probFileName):
        super(EquationGui, self).__init__()
        self.probfilename = probFileName

        # Install the custom output stream
        sys.stdout = EmittingStream()
        sys.stdout.textWritten.connect(self.normalOutputWritten)

        self.initUI()
        self.loadProblem()
        self.show()


    def __del__(self):
        # Restore sys.stdout
        sys.stdout = sys.__stdout__

    def initUI(self):
        self.setWindowTitle("eutactic GUI")

        # Actions
        quitAction = QAction(QIcon('exit.png'), '&Quit', self)
        quitAction.setShortcut('Ctrl+Q')
        quitAction.setStatusTip('Quit eutactic GUI')
        quitAction.triggered.connect(qApp.quit)

        openAction = QAction(QIcon('open.png'), '&Open problem file', self)
        openAction.setShortcut('Ctrl+O')
        openAction.setStatusTip('Open problem file')
        openAction.triggered.connect(self.loadProblemFromFile)

        reloadProblemAction = QAction('&Reload problem', self)
        reloadProblemAction.setShortcut('Ctrl+R')
        reloadProblemAction.triggered.connect(self.loadProblem)

        drawProblemAction = QAction('&Show problem structure', self)
        drawProblemAction.triggered.connect(self.onDrawButtonPressed)

        # Menu bar
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(openAction)
        fileMenu.addAction(quitAction)

        problemMenu = menubar.addMenu('&Problem')
        problemMenu.addAction(reloadProblemAction)
        problemMenu.addAction(drawProblemAction)

        # Central widget
        self.mainPanel = QWidget()
        self.setCentralWidget(self.mainPanel)

        # Widget layouts
        topLevelLayout = QHBoxLayout()
        self.mainPanel.setLayout(topLevelLayout)

        topLevelSplitter = QSplitter(Qt.Horizontal)
        topLevelLayout.addWidget(topLevelSplitter)

        #######
        # Column on the left for problem-solving controls
        # Split into a top half for variables and a bottom half for messages from the parser/solver
        inputSplitter = QSplitter(Qt.Vertical)
        topLevelSplitter.addWidget(inputSplitter)

        # Container for the variable table etc.
        varTableContainerWidget = QWidget()
        problemControlLayout = QVBoxLayout()
        varTableContainerWidget.setLayout(problemControlLayout)
        inputSplitter.addWidget(varTableContainerWidget)

        #####
        # File chooser
        #fileChooserLayout = QHBoxLayout()
        #problemControlLayout.addLayout(fileChooserLayout)

        # Current location text
        #self.fileLocText = QLineEdit(self.probfilename, self)
        #self.fileLocText.setReadOnly(True)
        #fileChooserLayout.addWidget(self.fileLocText)

        # Choose file button
        #self.openButton = QPushButton("Choose problem file", self)
        #fileChooserLayout.addWidget(self.openButton)
        #self.openButton.pressed.connect(self.loadProblemFromFile)
        #####

        # Reload problem button
        #reloadButton = QPushButton("Reset problem", self)
        #problemControlLayout.addWidget(reloadButton)
        #reloadButton.pressed.connect(self.loadProblem)

        # Button to show network
        #drawButton = QPushButton("Show problem structure", self)
        #problemControlLayout.addWidget(drawButton)
        #drawButton.pressed.connect(self.onDrawButtonPressed)

        # Table of variables
        problemControlLayout.addWidget(QLabel("Variables:"))
        self.varTable = QTableWidget(self)
        problemControlLayout.addWidget(self.varTable)
        header = self.varTable.horizontalHeader()
        # header.setStretchLastSection(True) # Makes the last column stretch to fill space
        #header.setStretchLastSection(False)
        #header.setResizeMode(0, QHeaderView.Interactive)
        #header.setResizeMode(2, QHeaderView.Interactive)
        #header.setResizeMode(QHeaderView.Interactive)
        #header.setResizeMode(QHeaderView.Fixed)
        #header.setResizeMode(0, QHeaderView.Stretch)
        #header.setResizeMode(1, QHeaderView.Stretch)
        header.setResizeMode(2, QHeaderView.Stretch)
        # TODO make the variable table stretch the slider to fill the table space

        # Layouts for solver controls
        solveControlLayout = QHBoxLayout()
        problemControlLayout.addLayout(solveControlLayout)

        # Solve button
        solveButton = QPushButton("Solve", self)
        solveControlLayout.addWidget(solveButton)
        solveButton.pressed.connect(self.solveProblem)

        # Enable autosolving checkbox
        self.autosolveCB = QCheckBox("Autosolve?", self)
        self.autosolveCB.setCheckState(Qt.Checked)
        self.autosolveCB.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
        solveControlLayout.addWidget(self.autosolveCB)

        ######
        # Parser/solver outputs, captured in a widget
        outputWidget = QWidget()
        outputLayout = QVBoxLayout()
        outputWidget.setLayout(outputLayout)
        inputSplitter.addWidget(outputWidget)

        # Label
        outputLayout.addWidget(QLabel("Parser/solver output:"))

        # Text output from parser and solver (or anything via stdout!)
        self.outputPane = QTextEdit()
        #self.outputPane.setFlags(self.outputPane.flags() & ~Qt.ItemIsEditable)
        self.outputPane.setReadOnly(True)
        outputLayout.addWidget(self.outputPane)

        #####
        # Column on the right for results display/logging
        rightContainerWidget = QWidget()
        resultsDisplayLayout = QVBoxLayout()
        rightContainerWidget.setLayout(resultsDisplayLayout)
        topLevelSplitter.addWidget(rightContainerWidget)


        # First, a table of all the solutions that have been found
        resultsDisplayLayout.addWidget(QLabel("Results:"))
        # A resultsSplitter to adjust between results display and graphs
        resultsSplitter = QSplitter(Qt.Vertical)
        resultsDisplayLayout.addWidget(resultsSplitter)
        self.solnsTable = QTableWidget(self)
        #resultsDisplayLayout.addWidget(self.solnsTable)
        resultsSplitter.addWidget(self.solnsTable)

        # Outer layout
        graphContainerWidget = QWidget()
        graphOuterLayout = QVBoxLayout()
        graphContainerWidget.setLayout(graphOuterLayout)
        resultsSplitter.addWidget(graphContainerWidget)

        # Dropdowns to choose X and Y variables
        varChoiceLayout = QHBoxLayout()
        graphOuterLayout.addLayout(varChoiceLayout)

        self.varPlotXAxisMenu = QComboBox()
        self.varPlotXAxisMenu.setEditable(False)
        self.varPlotXAxisMenu.activated[str].connect(lambda x: self.updateSolnsGraph())

        self.varPlotYAxisMenu = QComboBox()
        self.varPlotYAxisMenu.setEditable(False)
        self.varPlotYAxisMenu.activated[str].connect(lambda x: self.updateSolnsGraph())

        varChoiceLayout.addWidget(QLabel("Variables: X axis:"))
        varChoiceLayout.addWidget(self.varPlotXAxisMenu)
        varChoiceLayout.addWidget(QLabel("Y axis:"))
        varChoiceLayout.addWidget(self.varPlotYAxisMenu)

        # Plot widget
        self.varPlotWidget = pg.PlotWidget()
        self.varPlot = self.varPlotWidget.plot()
        graphOuterLayout.addWidget(self.varPlotWidget)


    def normalOutputWritten(self, text):
        """Append text to the QTextEdit."""
        # Maybe QTextEdit.append() works as well, but this is how I do it:
        cursor = self.outputPane.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.outputPane.setTextCursor(cursor)
        self.outputPane.ensureCursorVisible()


    def loadProblemFromFile(self):
        fname = QFileDialog.getOpenFileName(parent=self, caption='Open file', dir=self.probfilename, filter="*.prob")
        #print(fname)
        if fname[0]:
            self.probfilename = fname[0]
            self.loadProblem()

    def loadProblem(self):
        # Update the UI display
        #self.fileLocText.setText(self.probfilename)
        # Update the title bar
        self.setWindowTitle("Equation GUI - " + self.probfilename)

        # Parse the file into a Problem
        self.problem = ParsedProblem(self.probfilename)

        # Construct a dict of all variables in problem, sorted by name
        # Filter by the ones that are actually variables
        self.varDict = {expr.name: expr for expr in filter(lambda expr: isinstance(expr, ScalarVariable), self.problem.exprs)}
        # And a list of all the variable names, sorted alphabetically case-insensitively
        self.varNameList = sorted(self.varDict.keys(), key=lambda s: s.lower())

        # Update bits of the UI with details of the Problem's variables
        self.populateVarTable(self.problem.defaultContext)
        self.updateTableInputState(None)

        # Reset the stored database of solutions
        self.solutionVals = []
        self.populateSolutionsTable()

        # Reset the graph
        self.varPlot.setData(np.array([]), np.array([]))
        # Set the variable lists
        self.varPlotXAxisMenu.clear()
        self.varPlotXAxisMenu.addItems(self.varNameList)
        self.varPlotYAxisMenu.clear()
        self.varPlotYAxisMenu.addItems(self.varNameList)

    def populateVarTable(self, context):
        # Set table model etc.
        self.varTable.setColumnCount(3)
        self.varTable.setRowCount(len(self.varNameList))
        self.varTable.setHorizontalHeaderLabels(["Variable", "Input?", "Value"])
        # Go through variables in problem
        for i in range(len(self.varNameList)):
            # Var name
            # Not editable
            varnameitem = QTableWidgetItem(self.varNameList[i])
            varnameitem.setFlags(varnameitem.flags() & ~Qt.ItemIsEditable)
            self.varTable.setItem(i, 0, varnameitem)

            # Checkbox for whether it's an input
            chkBoxItem = QTableWidgetItem()
            chkBoxItem.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            # Set initial checkbox state based on whether the variable has a default value
            if self.varDict[self.varNameList[i]].getValue(context):
                chkBoxItem.setCheckState(Qt.Checked)
            else:
                chkBoxItem.setCheckState(Qt.Unchecked)
            self.varTable.setItem(i, 1, chkBoxItem)
            # Set row height
            self.varTable.setRowHeight(i, 50)

            # Var value
            # Original: just an ordinary item
            #self.varTable.setItem(i, 1, QTableWidgetItem(str(self.varDict[self.varNameList[i]].getValue(context))))
            # Display a widget in the cell instead, and don't use the item at all!
            varValue = self.varDict[self.varNameList[i]].getValue(context)
            if varValue == None:
                varValue = 0 #np.nan
            spinner = InfiniteRangeSlider(varValue) #ScientificDoubleSpinBox()
            self.varTable.setCellWidget(i, 2, spinner)
            # Set initial spinner value
            #self.varTable.cellWidget(i, 1).setValue(varValue)
            # Set up table to resolve if value is changed
            spinner.valueChanged.connect(lambda x: self.solveProblem() if self.autosolveCB.isChecked() else None)

        # Connect events from the whole table to update the editability of entries in the table
        self.varTable.itemClicked.connect(self.updateTableInputState)

        #self.varTable.resizeRowsToContents()
        self.varTable.resizeColumnsToContents()

    def updateTableInputState(self, clickedItem):
        # Only make the "value" column editable if a row is marked as an input
        # In theory we could just use the clickedItem directly...
        for i in range(self.varTable.rowCount()):
            isInput = self.varTable.item(i,1).checkState()
            #print(isInput)
            #flags = self.varTable.item(i, 1).flags()
            if isInput == Qt.CheckState.Checked:
                #flags |= Qt.ItemIsEditable
                #flags |= Qt.ItemIsEnabled
                #print("Editable")
                pass
            else:
                #flags &= ~Qt.ItemIsEditable
                #flags &= ~Qt.ItemIsEnabled
                #print("Uneditable")
                pass
            #self.varTable.item(i, 1).setFlags(flags)
            #print(bool(flags & Qt.ItemIsEnabled), bool(flags & Qt.ItemIsEditable))
        self.show()

    def solveProblem(self):
        #print("Solving...")
        # Create a new context with values from value table
        solveContext = Context()
        for i in range(self.varTable.rowCount()):
            # Only use those variables marked as "Input"
            if self.varTable.item(i, 1).checkState() == Qt.CheckState.Checked:
                varName = self.varTable.item(i, 0).text()
                #varValStr = self.varTable.item(i, 1).text()
                #if varValStr == "None":
                #    varVal = None
                #else:
                #    varVal = float(varValStr)
                varVal = self.varTable.cellWidget(i, 2).value()
                if varVal == np.nan:
                    varVal = None
                #print(str(self.exprs[varName]))
                self.varDict[varName].setValue(varVal, solveContext)
        #print(solveContext)
        # Solve
        self.problem.solve(solveContext)
        # Re-update table with values after solution
        self.storeSolutionVals(solveContext)
        #print("Solved, in theory")

    def storeSolutionVals(self, context):
        # Temporarily disable events from table while we update its contents
        #self.varTable.blockSignals(True)
        # Update the table of variables in the problem
        for i in range(self.varTable.rowCount()):
            varName = self.varTable.item(i, 0).text()
            #self.varTable.item(i, 1).setText(str(self.varDict[varName].getValue(context)))
            # Temporarily disable events from table while we update its contents
            self.varTable.cellWidget(i, 2).blockSignals(True)
            self.varTable.cellWidget(i, 2).setValue(self.varDict[varName].getValue(context))
            # Reenable events
            self.varTable.cellWidget(i, 2).blockSignals(False)
        # Reenable events
        #self.varTable.blockSignals(False)
        # Store the variable values in a "database"
        solnDict = {varName: self.varDict[varName].getValue(context) for varName in self.varNameList}
        self.solutionVals.append(solnDict)
        self.updateSolutionsTable()
        self.updateSolnsGraph()

    def updateSolnsGraph(self):
        # Update solutions graph
        # First extract variables we want to use
        xAxisVarName = self.varPlotXAxisMenu.currentText()  # self.varNameList[0]
        yAxisVarName = self.varPlotYAxisMenu.currentText()  # self.varNameList[1]
        #print("Plotting x:", xAxisVarName, ", y:", yAxisVarName)
        # Now get the values as numpy arrays
        xs = np.array([soln[xAxisVarName] for soln in self.solutionVals])
        ys = np.array([soln[yAxisVarName] for soln in self.solutionVals])
        # And add to the plot
        self.varPlot.setData(xs, ys, pen=None, symbol='+')
        # Set axis titles
        self.varPlotWidget.setLabel('bottom', xAxisVarName) # , units='s')
        self.varPlotWidget.setLabel('left', yAxisVarName)

    def populateSolutionsTable(self):
        # Set the table model to include all the variable names
        self.solnsTable.setColumnCount(len(self.varNameList))
        self.solnsTable.setRowCount(0)
        self.solnsTable.setHorizontalHeaderLabels(self.varNameList)

        self.solnsTable.resizeRowsToContents()
        self.solnsTable.resizeColumnsToContents()

    def updateSolutionsTable(self):
        # Number of rows = number of solutions found so far
        self.solnsTable.setRowCount(len(self.solutionVals))
        # Number of cols = number of variables = len(self.varNameList)
        # Iterate over columns in last row
        for i in range(len(self.varNameList)):
            #print(len(self.solutionVals) - 1, i)
            valueItem = QTableWidgetItem(str(self.solutionVals[-1][self.varNameList[i]]))
            valueItem.setFlags(valueItem.flags() & ~Qt.ItemIsEditable)
            self.solnsTable.setItem(len(self.solutionVals) - 1, i, valueItem)
        self.solnsTable.resizeColumnsToContents()

    def onDrawButtonPressed(self):
        buff = io.BytesIO()
        self.draw(self.problem, buff)
        img = QImage.fromData(buff.getvalue())

        # Using plain QT:
        # The problem with this is that the image is not zoomable
        #pixmap = QPixmap(img)
        #self.label = QLabel() # Have to make this a member variable so it doesn't go out of scope when this function returns!
        #self.label.setPixmap(pixmap)
        #self.label.show()

        # Using Pytqtgraph image viewer:
        # From http://stackoverflow.com/questions/19902183/qimage-to-numpy-array-using-pyside
        img = img.convertToFormat(QImage.Format.Format_RGB32)
        width = img.width()
        height = img.height()
        ptr = img.constBits()
        arr = np.array(ptr).reshape(height, width, 4)

        # The above makes the image come out the wrong way round => transpose
        # No longer needed with ViewBox!
        #arr = np.transpose(arr, [1, 0, 2])
        # Except we *do* meed to rotate the image by 90deg...
        arr = np.rot90(arr, 3)

        # Simplest way:
        #pg.image(arr)
        # This has an image popup with ROI controls, though...

        # Another go:
        # This also has excess ROI gubbins
        #self.imv = pg.ImageView()
        #self.imv.setImage(arr)
        #self.imv.show()

        # Try again...
        # This is now not zoomable any longer!
        #self.gv = pg.GraphicsView()
        #ii = pg.ImageItem(arr)
        #self.gv.addItem(ii)
        #self.gv.show()

        self.glw = pg.GraphicsLayoutWidget()
        self.vb = self.glw.addViewBox(lockAspect=1.0)
        ii = pg.ImageItem(arr)
        self.vb.addItem(ii)
        self.glw.show()

    def addNodesForChildren(self, g, expr, parent):
        if expr.isComposite():
            # If it's its own composite expression
            # Add a node
            #exprNode = Node(expr.name, shape="box", style="filled", fillcolor="#aaffaa")
            #g.add_node(exprNode)
            # Add nodes for children recursively...
            for childexpr in expr.getChildren():
                self.addNodesForChildren(g, childexpr, parent)
        else: # Not composite - just a variable
            # Add a node for a value
            # Colour depending on type
            if isinstance(expr,ScalarVariable):
                exprNode = Node(expr.name, shape="box", style="filled")
                exprNode.set_fillcolor("#ffaaaa")
                g.add_node(exprNode)
                # Lastly, add an edge to the expression node
                g.add_edge(Edge(expr.name, parent.name))
            else:
                #exprNode.set_fillcolor("#ffffaa")
                pass

    def draw(self, prob, targetFile):
        # Do the graphing stuff here...
        # Root graph
        g = Dot(graph_type="digraph", nodesep=2, overlap=False)
        #g.set_edge_defaults(weight="0", minlen="10")
        # Organise by adding constraints (adds edges too)
        for constr in prob.constrs:
            # Node for constraint
            constrNode = Node(constr.name, shape="ellipse", style="filled", fillcolor = "#aaaaff")
            constrNode.set_label(constr.name + ": " + constr.getTextFormula())
            g.add_node(constrNode)
            # Associated expressions
            for expr in constr.exprs:
                self.addNodesForChildren(g, expr, constr)
        # Finally, render
        #g.write_png("problem_structure.png", prog="dot")
        g.write_png(targetFile, prog="neato")



if __name__=="__main__":
    # Create a Qt application
    app = QApplication(sys.argv)
    # Create a GUI and show it
    gui = EquationGui(testfilename)
    # Enter Qt application main loop
    app.exec_()
    sys.exit()