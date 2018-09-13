from __future__ import division

import os, sys, glob
import math
import time

from PyQt4 import QtGui, QtCore, QtWebKit

#
# see PAGE18-03109 in SCARAB for more details about coordinate conversion
#
# note that this only works if formulatrix images are converted like this: convert -resize 25%
#


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

        self.subwell_dict = {
            'a':    ['1','3','5','7', '9','11','13','15','17','19','21','23'],
            'c':    ['1','3','5','7', '9','11','13','15','17','19','21','23'],
            'd':    ['2','4','6','8','10','12','14','16','18','20','22','24']
                    }
        self.row_dict = {
            'Aa':   'A', 'Ac':  'B', 'Ad':  'B',
            'Ba':   'C', 'Bc':  'D', 'Bd':  'D',
            'Ca':   'E', 'Cc':  'F', 'Cd':  'F',
            'Da':   'G', 'Dc':  'H', 'Dd':  'H',
            'Ea':   'I', 'Ec':  'J', 'Ed':  'J',
            'Fa':   'K', 'Fc':  'L', 'Fd':  'L',
            'Ga':   'M', 'Gc':  'N', 'Gd':  'N',
            'Ha':   'O', 'Hc':  'P', 'Hd':  'P'
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


    def openFile(self):
        fileName = tuple(QtGui.QFileDialog.getOpenFileNameAndFilter(self.window,'Open file', os.getcwd(),'*.*'))[0]
        self.pixmap = QtGui.QPixmap(fileName)
        self.canvas.setPixmap(self.pixmap)
#        self.drawGrid()

    def showImage(self):
        if self.imageList != []:
            print 'current image:',self.imageList[self.index]
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
        qp.begin(self.pixmap)
        qp.setPen(pen)
#        qp.drawLine(306, 0, 306, 512)
#        qp.drawLine(0, 256, 612, 256)
        pen = QtGui.QPen(QtCore.Qt.blue, 1.5)
        qp.setPen(pen)
        if self.wellID.endswith('a'):
#            qp.drawLine(247, 0, 247, 512)
#            qp.drawLine(0, 224, 612, 224)
            qp.drawLine(224, 0, 224, 512)
            qp.drawLine(0, 247, 612, 247)
        elif self.wellID.endswith('c'):
#            qp.drawLine(254, 0, 254, 512)
#            qp.drawLine(0, 225, 612, 225)
            qp.drawLine(225, 0, 225, 512)
            qp.drawLine(0, 254, 612, 254)
        elif self.wellID.endswith('d'):
#            qp.drawLine(254, 0, 254, 512)
#            qp.drawLine(0, 221, 612, 221)
            qp.drawLine(221, 0, 221, 512)
            qp.drawLine(0, 254, 612, 254)
        qp.end()
        self.canvas.setPixmap(self.pixmap)
#        for x in range(0,800,40):
#            qp.begin(self.pixmap)
#            qp.setPen(pen)
#            qp.drawLine(x, 0, x, 800)
#            qp.end()
#            self.canvas.setPixmap(self.pixmap)
#        for y in range(0,800,40):
#            qp.begin(self.pixmap)
#            qp.setPen(pen)
#            qp.drawLine(0, y, 800, y)
#            qp.end()
#            self.canvas.setPixmap(self.pixmap)

    def paintEvent(self,x,y):
        pen = QtGui.QPen(QtCore.Qt.red, 1.5)
        qp = QtGui.QPainter()
        qp.begin(self.pixmap)
        qp.setPen(pen)
        qp.setBrush(QtCore.Qt.red)
        center = QtCore.QPoint(x, y)
        qp.drawEllipse(center,20,20)
        qp.end()
        self.canvas.setPixmap(self.pixmap)

    def getPos(self , event):
        x = event.pos().x()
        y = event.pos().y()
#        print 'mouse position',x,y
        self.paintEvent(x,y)
#        print self.centre_x - x
#        print self.centre_y - y
#        distance_from_centre = math.sqrt(math.pow(self.centre_x-x,2)+math.pow(self.centre_y - y,2))/self.pixel_to_um
#        print distance_from_centre
#        offset_x=(x -self.centre_x)/self.pixel_to_um
#        offset_y=(self.centre_y -
#                  y)/self.pixel_to_um
#        print 'x offset =',offset_x,'y offset =',offset_y
#        self.writeCSV(str(offset_x),str(offset_y))
        self.pixelToECHOcoord(x,y)

    def pixelToECHOcoord(self,x,y):
        if self.wellID.endswith('a'):
#            x = 0.187 * Ex + 247.8
            Ey = int(float(y - 247.8)/0.187)
#            y = -0.1731 * Ey + 223.8
            Ex = int(float(x-223.8)/-0.1731)
        elif self.wellID.endswith('c'):
#            x = 0.1875 * Ex + 253.7
            Ey = int(float(y - 253.7)/0.1875)
#            y = -0.1754 * Ey + 225
            Ex = int(float(x-225)/-0.1754)
        elif self.wellID.endswith('d'):
#            x = 0.187 * Ex + 253.9
            Ey = int(float(y - 253.9) / 0.187)
#            y = -0.1786 * Ey + 221
            Ex = int(float(x-221)/-0.1786)-700
        print 'IMAGE x,y',x,y
        print 'ECHO x,y',Ex,Ey
        self.writeCSV(str(Ex),str(Ey))
        time.sleep(0.2)
        self.nextImage()

    def quitApp(self):
        QtGui.qApp.quit()

    def loadPlate(self):
        self.index = 0  # reset index
        self.imageList = []
        for image in sorted(glob.glob(os.path.join(self.imageFolder,'*png'))):
            print 'loading',image
            self.imageList.append(image)
        self.showImage()
        self.drawGrid()

#        row_order = ['A','B','C','D','E','F','G','H']
#        column_order = ['01','02','03','04','05','06','07','08','09','10','11','12']
#        subwell_order = ['a','c','d']
#
#        t = []
#        for l in self.imageList:
#            row = l[0][l[0].rfind('/')+1:l[0].rfind('/')+2]
#            column = l[0][l[0].rfind('/')+2:l[0].rfind('/')+4]
#            subwell = l[0][l[0].rfind('/')+4:l[0].rfind('/')+5]
#            for i,m in enumerate(t):



    def nextImage(self):
        if self.index < len(self.imageList)-1:
#            print self.index,len(self.imageList)
            self.index+=1
        else:
            self.index = 0
        self.showImage()
        self.drawGrid()

    def previousImage(self):
        if self.index > 0:
#            print self.index,len(self.imageList)
            self.index+=-1
        else:
            self.index = len(self.imageList)-1
        self.showImage()
        self.drawGrid()

    def writeCSV(self,offset_x,offset_y):
        inLine = ''
        if os.path.isfile(self.barcode+'_RI1000-0276-3drop_targets.csv'):
            for line in open(self.barcode+'_RI1000-0276-3drop_targets.csv'):
                inLine += line
#        else:
#            inLine += self.csv_template

        row = self.row_dict[self.wellID[0]+self.wellID[3]]
        column = self.subwell_dict[self.wellID[3]][int(self.wellID[1:3])-1]
#        inLine += self.barcode+',A1,'+row+column+','+self.volume+','+offset_x+','+offset_y+'\n'
#        inLine += self.barcode+','+self.wellID+','+row+column+','+self.volume+','+offset_x+','+offset_y+'\n'
        inLine += self.wellID+','+offset_x+','+offset_y+'\n'
        f = open(self.barcode+'_RI1000-0276-3drop_targets.csv','w')
        f.write(inLine)
        f.close()

if __name__ == "__main__":
    app=xtalViewer(sys.argv[1:])
	

