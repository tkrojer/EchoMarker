from __future__ import division

import os, sys, glob
import math
import time

from PyQt4 import QtGui, QtCore, QtWebKit

class xtalViewer(QtGui.QApplication):
    def __init__(self,args):
        QtGui.QApplication.__init__(self,args)

        # x_max = 979 -> x_centre = 489
        # y_max = 819 -> y_centre = 409
        # 800 pixels == 2200um

        self.barcode = ''
        self.imageFolder = ''
        self.volume = '30'
        self.imageList = []
        self.index = 0
        self.centre_x = 489
        self.centre_y = 409
        self.pixel_to_um = float(800/2200)

        self.csv_template = 'PlateBatch,Source well,Destination well,Transfer Volume,Destination Well X Offset,Destination Well Y Offset\n'
        # CI067337,A3,G1,80,0,0'

        self.wellID = ''

        self.wellID_dict = {
            'A01a': 'A1', 'A01c': 'B1', 'A01d': 'B2',
            'A02a': 'A3', 'A02c': 'B3', 'A02d': 'B4'
        }

#        print QtGui.QImageReader.supportedImageFormats()

        self.startGUI()
        self.exec_()

    def startGUI(self):

        # GUI setup
        self.window=QtGui.QWidget()
        self.window.setWindowTitle("ECHO marker")
#        self.window.setFixedSize(500,500)
        vbox = QtGui.QVBoxLayout()

        menuBar = QtGui.QMenuBar()
        file = menuBar.addMenu("&File")
        load=QtGui.QAction("Open Folder", self.window)
        load.setShortcut('Ctrl+O')
        load.triggered.connect(self.openFolder)
#        save=QtGui.QAction("Save Config File", self.window)
#        save.setShortcut('Ctrl+S')
#        save.triggered.connect(self.save_config_file)
        quit=QtGui.QAction("Quit", self.window)
        quit.setShortcut('Ctrl+Q')
        quit.triggered.connect(self.quitApp)
        file.addAction(load)
#        file.addAction(save)
        file.addAction(quit)
        vbox.addWidget(menuBar)

        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(QtGui.QLabel('Barcode'))
        self.barcodeEntry = QtGui.QLineEdit("")
        self.barcodeEntry.setFixedWidth(200)
        hbox.addWidget(self.barcodeEntry)
        goButton = QtGui.QPushButton("Load")
        goButton.clicked.connect(self.loadPlate)
        hbox.addWidget(goButton)
        hbox.addWidget(QtGui.QLabel('Volume (nl)'))
        self.volumeEntry = QtGui.QLineEdit(self.volume)
        self.volumeEntry.setFixedWidth(30)
        hbox.addWidget(self.volumeEntry)
        hbox.addStretch(1)
        self.plateWell = QtGui.QLabel('')
        hbox.addWidget(self.plateWell)
        vbox.addLayout(hbox)

        hbox = QtGui.QHBoxLayout()
        self.reverse = QtGui.QPushButton("<<<")
        self.forward = QtGui.QPushButton(">>>")
        self.reverse.clicked.connect(self.previousImage)
        self.forward.clicked.connect(self.nextImage)
        hbox.addWidget(self.reverse)
        hbox.addWidget(self.forward)
        vbox.addLayout(hbox)

        frame=QtGui.QFrame()
        frame.setFrameShape(QtGui.QFrame.StyledPanel)
        hbox = QtGui.QHBoxLayout()
        self.canvas = QtGui.QLabel()
        self.pixmap = QtGui.QPixmap()
        self.canvas.setPixmap(self.pixmap)
        self.canvas.mousePressEvent = self.getPos
        hbox.addWidget(self.canvas)
        frame.setLayout(hbox)
        vbox.addWidget(frame)


        self.window.setLayout(vbox)
        self.window.show()


#    def openFile(self):
#        fileName = tuple(QtGui.QFileDialog.getOpenFileNameAndFilter(self.window,'Open file', os.getcwd(),'*.*'))[0]
#        print 'here',fileName
#        self.pixmap = QtGui.QPixmap(fileName)
#        self.canvas.setPixmap(self.pixmap)
##        self.drawGrid()

    def showImage(self):
        if self.imageList != []:
            print self.imageList[self.index]
            self.pixmap = QtGui.QPixmap(self.imageList[self.index])
            self.canvas.setPixmap(self.pixmap)
            fileName = self.imageList[self.index].replace('\\','/')
            self.wellID = fileName[fileName.rfind('/')+1:].replace('.png','')
            self.plateWell.setText(self.wellID)


    def openFolder(self):
        folder = QtGui.QFileDialog.getExistingDirectory(None, 'Select a folder:', os.getcwd(), QtGui.QFileDialog.ShowDirsOnly)
        self.imageFolder = str(folder).replace('\\','/')
        self.barcode=str(self.imageFolder)[str(self.imageFolder).rfind('/')+1:]
        self.barcodeEntry.setText(self.barcode)

    def drawGrid(self):
        pen = QtGui.QPen(QtCore.Qt.black, 1.5)
        pen.setStyle(QtCore.Qt.DotLine)
        qp = QtGui.QPainter()
        for x in range(0,400,20):
            qp.begin(self.pixmap)
            qp.setPen(pen)
            qp.drawLine(x, 0, x, 400)
            qp.end()
            self.canvas.setPixmap(self.pixmap)
        for y in range(0,400,20):
            qp.begin(self.pixmap)
            qp.setPen(pen)
            qp.drawLine(0, y, 400, y)
            qp.end()
            self.canvas.setPixmap(self.pixmap)

    def getPos(self , event):
        x = event.pos().x()
        y = event.pos().y()
        print 'mouse position',x,y
        self.paintEvent(x,y)
        print self.centre_x - x
        print self.centre_y - y
        distance_from_centre = math.sqrt(math.pow(self.centre_x-x,2)+math.pow(self.centre_y - y,2))/self.pixel_to_um
        print distance_from_centre
        offset_x=(x -self.centre_x)/self.pixel_to_um
        offset_y=(self.centre_y -
                  y)/self.pixel_to_um
        print 'x offset =',offset_x,'y offset =',offset_y
        self.writeCSV(str(offset_x),str(offset_y))
        time.sleep(0.5)
        self.nextImage()

    def paintEvent(self,x,y):
        qp = QtGui.QPainter()
        qp.begin(self.pixmap)
        qp.setPen(QtCore.Qt.red)
        qp.setBrush(QtCore.Qt.red)
        qp.drawEllipse(x,y,20,20)
        qp.end()
        self.canvas.setPixmap(self.pixmap)

    def quitApp(self):
        QtGui.qApp.quit()

    def loadPlate(self):
        self.index = 0  # reset index
        self.imageList = []
        for image in sorted(glob.glob(os.path.join(self.imageFolder,'*png'))):
            print image
            self.imageList.append(image)
        self.showImage()

    def nextImage(self):
        if self.index < len(self.imageList)-1:
            print self.index,len(self.imageList)
            self.index+=1
        else:
            self.index = 0
        self.showImage()

    def previousImage(self):
        if self.index > 0:
            print self.index,len(self.imageList)
            self.index+=-1
        else:
            self.index = len(self.imageList)-1
        self.showImage()

    def writeCSV(self,offset_x,offset_y):
        inLine = ''
        if os.path.isfile(self.barcode+'.csv'):
            for line in open(self.barcode+'.csv'):
                inLine += line
        else:
            inLine += self.csv_template
        inLine += self.barcode+',A1,'+self.wellID_dict[self.wellID]+','+self.volume+','+offset_x+','+offset_y+'\n'
        f = open(self.barcode+'.csv','w')
        f.write(inLine)
        f.close()

if __name__ == "__main__":
    app=xtalViewer(sys.argv[1:])
	

