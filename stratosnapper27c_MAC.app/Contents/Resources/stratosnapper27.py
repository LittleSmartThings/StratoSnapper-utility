# STRATOSNAPPER CONFIGURATION UTILITY
# All rights reserved LittleSmartThings 2011

import time
import sys
import serial
import glob
import threading


from PyQt4 import QtCore, QtGui
from ui_stratosnapper import Ui_MainWindow
from DataBase import DataBase

def connectToSerial(port):
    if (len(form.ports) > 0):
        global ser
        try:
            ser = serial.Serial(form.ports[form.ui.portSelect.currentIndex()], 57600, timeout=0)
        
            time.sleep(1.8)
            ser.write("#?!".encode('ascii'))
            time.sleep(0.4)
            serialIn = (ser.read(20))
            print(serialIn)
            if (serialIn[0:2].decode('utf-8') == 'OK'):
                    print("connected!")
                    form.connected = True
                    #form.ui.textEdit.setText("Connected!")
                    form.serialPortFree = True
                    if (serialIn[2:5].decode('utf-8') != '63'):
                        version = serialIn[2:5].decode('utf-8')
                    else:
                        version = "1.0"
                    form.ui.comPortLabel.setText("Connected firmware: "+version)
                    
                    servoCheck.start()
                    try:
                        restoreLastUserUI()
                    except:
                        pass
                    
            else:
                    form.popMessage("StratoSnapper is not responding on this com-port...")
    
        except:
            form.popMessage("Com-port is no longer available...")
            form.ui.portSelect.clear()
            form.ports = scan()
    else:
        form.popMessage("No com-ports detected. Make sure the StratoSnapper is connected and that you installed the FTDI driver")
      
def scan():
    if (sys.platform == 'darwin'):  # IF MAC
        print('mac')
        portsAvailable = (glob.glob('/dev/tty.usbserial*'))
        if (len(portsAvailable) > 0):
            form.ui.portSelect.clear()
            i = 0
            for port in portsAvailable:
                form.ui.portSelect.insertItem(i, port)
                i = i + 1
            return(portsAvailable);
        else:
            form.ui.portSelect.clear()
            return(portsAvailable)
    
    if (sys.platform == 'win32'): # IF WINDOWS
        import _winreg as winreg
        import itertools
        path = 'HARDWARE\\DEVICEMAP\\SERIALCOMM'
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
            print(key)
        except WindowsError:
            print('Error getting comports...')
        
        portsAvailable = []
        form.ui.portSelect.clear()
        for i in itertools.count():
            try:
                val = winreg.EnumValue(key, i)
                portsAvailable.append(val[1])
                form.ui.portSelect.insertItem(i, val[1])
            #yield str(val[1])
            except EnvironmentError:
                return(portsAvailable)
                break    
        
def updateServoValue():
    
    if (form.serialPortFree):
        try:
            ser.write("s".encode('ascii'))
            time.sleep(0.1)
            serialIn = (ser.read(200))
            serialString = (serialIn.decode("utf-8"))
            
            serialValues = (serialString.split(','))
            
            if (serialValues[0] == "#s" and serialValues[3] == "!"):
                print(serialValues);
                
                servoInput1 = int(serialValues[1])
                if (servoInput1 < servoMax):
                    OldRange = servoMax - servoMin
                    NewRange = (255 - 0)
                    byteServo1 = int((((servoInput1 - servoMin) * NewRange) / OldRange) + 0)
                    if (byteServo1 < 0):
                        byteServo1 = 0;
                    form.ui.progressBar1.setValue(int(byteServo1))
                    form.ui.progressText1.setText(str(byteServo1))  
                      
                servoInput2 = int(serialValues[2])    
                if (servoInput2 < servoMax):
                    OldRange = servoMax - servoMin
                    NewRange = (255 - 0)
                    byteServo2 = int((((servoInput2 - servoMin) * NewRange) / OldRange) + 0)
                    if (byteServo2 < 0):
                        byteServo2 = 0;
                    form.ui.progressBar2.setValue(int(byteServo2))
                    form.ui.progressText2.setText(str(byteServo2))
                    

        except:
            form.serialPortFree = False
            form.connected = False
            form.ui.comPortLabel.setText("Not connected")   
            form.ui.progressBar1.setValue(0)
            form.ui.progressText1.setText(str(0))
            form.ui.progressBar2.setValue(0)
            form.ui.progressText2.setText(str(0))
            form.popMessage("StratoSnapper disconnected...")
    
class TaskThread(QtCore.QThread):
    """Thread that executes a task every N seconds"""
    
    def __init__(self):
        QtCore.QThread.__init__(self)
        self._finished = threading.Event()
        self._interval = 0.5
    
    def setInterval(self, interval):
        """Set the number of seconds we sleep between executing our task"""
        self._interval = interval
    
    def shutdown(self):
        """Stop this thread"""
        self._finished.set()
    
    def run(self):
        while 1:
            if self._finished.isSet(): return
            self.task()
            
            # sleep for interval or until shutdown
            self._finished.wait(self._interval)
    
    def task(self):
        #print("task");
        self.emit(QtCore.SIGNAL('update(QString)'), "from work thread ")
        pass

class StratGUI(QtGui.QMainWindow):
    
    def __init__(self, parent=None):
        self.currentBrand = 'None'
        self.currentModel = 'None'
        self.serialPortFree = True
        self.actionList = []
        self.cameraSelected = False
        self.ports = []
        self.connected = False
        QtGui.QMainWindow.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        QtCore.QObject.connect(self.ui.connectBtn, QtCore.SIGNAL("released()"), self.connect) # signal/slot connection
        QtCore.QObject.connect(self.ui.reloadBtn, QtCore.SIGNAL("released()"), self.reloadBtn) # signal/slot connection

        QtCore.QObject.connect(self.ui.brandCB, QtCore.SIGNAL("currentIndexChanged(QString)"), self.brandSelected)
        QtCore.QObject.connect(self.ui.triggerPointSlider1, QtCore.SIGNAL("sliderMoved(int)"), self.triggerSliderChanged1)
        QtCore.QObject.connect(self.ui.triggerPointSlider2, QtCore.SIGNAL("sliderMoved(int)"), self.triggerSliderChanged2)
        QtCore.QObject.connect(self.ui.triggerPointSlider3, QtCore.SIGNAL("sliderMoved(int)"), self.triggerSliderChanged3)
        QtCore.QObject.connect(self.ui.triggerPointSlider4, QtCore.SIGNAL("sliderMoved(int)"), self.triggerSliderChanged4)
        QtCore.QObject.connect(self.ui.triggerPointSlider1, QtCore.SIGNAL("sliderPressed()"), self.triggerSliderChanged1)
        QtCore.QObject.connect(self.ui.triggerPointSlider2, QtCore.SIGNAL("sliderPressed()"), self.triggerSliderChanged2)
        QtCore.QObject.connect(self.ui.triggerPointSlider3, QtCore.SIGNAL("sliderPressed()"), self.triggerSliderChanged3)
        QtCore.QObject.connect(self.ui.triggerPointSlider4, QtCore.SIGNAL("sliderPressed()"), self.triggerSliderChanged4)
        QtCore.QObject.connect(self.ui.uploadBtn, QtCore.SIGNAL("released()"), self.uploadBtn)
        #QtCore.QObject.connect(self.ui.selectBtn, QtCore.SIGNAL("released()"), self.selectBtn)
        QtCore.QObject.connect(self.ui.standAloneCB, QtCore.SIGNAL("clicked()"), self.standAloneBtn)
    
    def standAloneBtn(self):
        print("click")
        if (self.ui.standAloneCB.isChecked()):
            print("")
            self.ui.enable1CB.setChecked(1)
            self.ui.enable2CB.setChecked(0)
            self.ui.enable3CB.setChecked(0)
            self.ui.enable4CB.setChecked(0)
    
    def reloadBtn(self):
        self.ports = scan()
    
    def popMessage(self, message):
        #QtGui.QMainWindow.addWidget(self.hello_edit)
        QtGui.QMessageBox.information(self,"Hello!", message, QtGui.QMessageBox.Ok)
        #QtCore.QObject.connect(self.ui.selectBtn, QtCore.SIGNAL("released()"), self.selectBtn)
   
    def closeEvent(self, event):
        servoCheck.shutdown()
        event.accept()
    
    def uploadMethod(self):
        serialIn = (ser.readline())
        print(serialIn)
        self.ui.textEdit.setText(serialIn.decode('utf-8'))
        
    def connect(self):
        connectToSerial(self.ui.portSelect.currentIndex())
        #print(dataBase.getAllCams(dataBase))
        
    
    def updateInterface(self):    
        modelList = dataBase.getAllCamModels(dataBase)
        for model in reversed(modelList):
                form.ui.brandCB.insertItem(1, model)
        
    def brandSelected(self):
        self.currentBrand = (self.ui.brandCB.itemData(self.ui.brandCB.currentIndex(), 2)) 
        self.ui.modelCB.clear()
        camList = dataBase.getAllCams(dataBase)
        for cam in camList:
            if cam.brand == self.currentBrand:
                form.ui.modelCB.insertItem(1, cam.name)
        self.selectBtn()
    
    def triggerSliderChanged1(self):
        self.ui.triggerValueText1.setText(str(self.ui.triggerPointSlider1.value()))
    def triggerSliderChanged2(self):
        self.ui.triggerValueText2.setText(str(self.ui.triggerPointSlider2.value()))
    def triggerSliderChanged3(self):
        self.ui.triggerValueText3.setText(str(self.ui.triggerPointSlider3.value()))
    def triggerSliderChanged4(self):
        self.ui.triggerValueText4.setText(str(self.ui.triggerPointSlider4.value()))

        
    def uploadBtn(self):
        
        if (self.cameraSelected & self.connected):
            configurations = []
    
            if self.ui.enable1CB.checkState() == 2:
                channelAction = []
                channelAction.append(self.actionList[form.ui.action1CB.currentIndex()])
                print("---")
                print(self.actionList[form.ui.action1CB.currentIndex()]) #DEBUG
                print(self.actionList[form.ui.action1CB.currentIndex()].name)
                print(form.ui.action1CB.currentIndex())
                print(self.actionList[form.ui.action1CB.currentIndex()].action)
                print(self.actionList[form.ui.action1CB.currentIndex()].IRHighSeq)
                
                print(form.ui.action1CB.itemData(form.ui.action1CB.currentIndex(), 2))
                
                print("---")
                channelAction.append(1) #channel
                
                OldRange = 255
                NewRange = (servoMax - servoMin)
                byteTriggerPoint = int((((form.ui.triggerPointSlider1.value() - 0) * NewRange) / OldRange) + servoMin)
                channelAction.append(byteTriggerPoint)

                
                channelAction.append(form.ui.repeat1SB.value())
                
                if (self.ui.trigger1DirRB.isChecked()):
                    channelAction.append(0)
                else:
                    channelAction.append(1)
                
                if (self.ui.standAloneCB.isChecked()): #check if stand alone is active. Uses only channel one
                    channelAction.append(1)
                else:
                    channelAction.append(0)
                
                configurations.append(channelAction)
            
            if self.ui.enable2CB.checkState() == 2:
                channelAction = []
                channelAction.append(self.actionList[form.ui.action2CB.currentIndex()])
                channelAction.append(2) #channel
                OldRange = 255
                NewRange = (servoMax - servoMin)
                byteTriggerPoint = int((((form.ui.triggerPointSlider2.value() - 0) * NewRange) / OldRange) + servoMin)
                channelAction.append(byteTriggerPoint)
                channelAction.append(form.ui.repeat2SB.value())
                if (self.ui.trigger2DirRB.isChecked()):
                    channelAction.append(0)
                else:
                    channelAction.append(1)
                
                if (self.ui.standAloneCB.isChecked()): #check if stand alone is active. Uses only channel one
                    channelAction.append(1)
                else:
                    channelAction.append(0)
                
                configurations.append(channelAction)
            
            if self.ui.enable3CB.checkState() == 2:
                channelAction = []
                channelAction.append(self.actionList[form.ui.action3CB.currentIndex()])
                channelAction.append(3) #channel
                OldRange = 255
                NewRange = (servoMax - servoMin)
                byteTriggerPoint = int((((form.ui.triggerPointSlider3.value() - 0) * NewRange) / OldRange) + servoMin)
                channelAction.append(byteTriggerPoint)
                channelAction.append(form.ui.repeat3SB.value())
                if (self.ui.trigger3DirRB.isChecked()):
                    channelAction.append(0)
                else:
                    channelAction.append(1)
                    
                if (self.ui.standAloneCB.isChecked()): #check if stand alone is active. Uses only channel one
                    channelAction.append(1)
                else:
                    channelAction.append(0)
                    
                configurations.append(channelAction)
            
            if self.ui.enable4CB.checkState() == 2:
                channelAction = []
                channelAction.append(self.actionList[form.ui.action4CB.currentIndex()])
                channelAction.append(4) #channel
                OldRange = 255
                NewRange = (servoMax - servoMin)
                byteTriggerPoint = int((((form.ui.triggerPointSlider4.value() - 0) * NewRange) / OldRange) + servoMin)
                channelAction.append(byteTriggerPoint)
                channelAction.append(form.ui.repeat4SB.value())
                if (self.ui.trigger4DirRB.isChecked()):
                    channelAction.append(0)
                else:
                    channelAction.append(1)
                    
                if (self.ui.standAloneCB.isChecked()): #check if stand alone is active. Uses only channel one
                    channelAction.append(1)
                else:
                    channelAction.append(0)
                    
                configurations.append(channelAction)
            print(self.ui.standAloneCB.isChecked())
            if ((len(configurations) > 1) & (self.ui.standAloneCB.isChecked())):
                self.popMessage("Only channel one can be enabled in stand-alone mode")
            else:
                if ((len(configurations) > 0)):
                    
                    uploadConfiguration(configurations)
                else:
                    self.popMessage("No configurations enabled!")
            
                
            
        else:
            self.popMessage("Please connect the StratoSnapper and select your camera first")
        
    def selectBtn(self):
        self.cameraSelected = True
        self.currentModel = self.ui.modelCB.itemData(self.ui.modelCB.currentIndex(), 2)
        cam = dataBase.getCamFromName(dataBase, self.currentModel)
        camCapabilities = cam[0].capabilities
        
        form.ui.action1CB.clear()
        form.ui.action2CB.clear()
        form.ui.action3CB.clear()
        form.ui.action4CB.clear()
        
        self.actionList = []
        i = 0
        for cap in camCapabilities:
            curCap = dataBase.getDefFromName(dataBase, cap)
            print(curCap.action)
            print(curCap.name)
            self.actionList.append(curCap)
        
        #for action in self.actionList:
            form.ui.action1CB.insertItem(i, curCap.action)
            form.ui.action2CB.insertItem(i, curCap.action)
            form.ui.action3CB.insertItem(i, curCap.action)
            form.ui.action4CB.insertItem(i, curCap.action)
            i = i+1
        #saveUIConfiguration() #debug 
                
def uploadConfiguration(configuration):
    
    form.serialPortFree = False
    print(len(configuration))
    uploadCommand("","d","") #disable all triggers

    for conf in configuration:
        burstHigh = str(conf[0].burstHigh)
        burstLow = str(conf[0].burstLow)
        
        repeatDelay = str(conf[3]*100) # *100 to lift from 1/10 sec til millisec + "000" # REPEATDELAY convert from sec to millisec
        repeats = str(conf[0].repeats) # number of times to seq will be sent imidiatly efter one another
        triggerAbove = str(conf[4])
        triggerPoint = str(conf[2])
        standAlone = str(conf[5])
        genChannelConfigString = "1," + burstHigh + "," + burstLow +"," + repeatDelay + "," + triggerPoint +"," + triggerAbove +"," + repeats +","+standAlone
        print(genChannelConfigString)
        IRHighSeq = str(conf[0].IRHighSeq)
        IRLowSeq = str(conf[0].IRLowSeq)
        IRHighSeq = IRHighSeq.replace(' ', '')
        IRLowSeq = IRLowSeq.replace(' ', '')
        IRHighSeq = IRHighSeq[1:-1] #remove brackets
        IRLowSeq = IRLowSeq[1:-1] #remove brackets
        channel = str(conf[1]-1) #convert to zero index
        adrHigh = channel +"0"
        adrLow = channel + "1"
        uploadCommand(IRHighSeq,"c", adrHigh)    
        uploadCommand(IRLowSeq,"c", adrLow)
        uploadCommand(genChannelConfigString,"g", channel)
    
    ser.write("#w!".encode('ascii')) #write config to epromm
    time.sleep(0.5)

    saveUIConfiguration()
    flush = ser.read(200)
    form.serialPortFree = True
    form.popMessage("Succes! Configuration uploaded to StratoSnapper. You may disconnect if you like.")
    

 
    
    
def uploadCommand(command, cmd, adr):
    stratoBoardMaxBuffer = 55 #break commands in pieces if above this value 55
    commandLine = "#" + cmd + adr + "," + command +"!"
    print("command line: " + commandLine)
    if (len(commandLine) > stratoBoardMaxBuffer):
        chunks = int(len(commandLine) / stratoBoardMaxBuffer) 
        i = 0
        while i < chunks:
            curChunk = commandLine[(i*stratoBoardMaxBuffer):(i+1)*stratoBoardMaxBuffer]
            ser.write(curChunk.encode('ascii')) 
            #print(curChunk.encode('ascii'))
            ser.write(">".encode('ascii'))
            time.sleep(0.5)
            i=i+1
        lastChunk = commandLine[(i*stratoBoardMaxBuffer):]
        ser.write(lastChunk.encode('ascii'))
        #print(lastChunk.encode('ascii')) #debug
    else:
        print("small")
        ser.write(commandLine.encode('ascii'))
    time.sleep(0.8)
    response = ser.read(300)
    print(response.decode('utf-8'))
    
def saveUIConfiguration():
    UIConfig = {}
    UIConfig['camBrand'] = form.ui.brandCB.itemData(form.ui.brandCB.currentIndex(), 2)
    UIConfig['camModel'] = form.ui.modelCB.itemData(form.ui.modelCB.currentIndex(), 2)
    UIConfig['enable1'] = form.ui.enable1CB.checkState()
    UIConfig['enable2'] = form.ui.enable2CB.checkState()
    UIConfig['enable3'] = form.ui.enable3CB.checkState()
    UIConfig['enable4'] = form.ui.enable4CB.checkState()
    UIConfig['triggerValue1'] = form.ui.triggerPointSlider1.value()
    UIConfig['triggerValue2'] = form.ui.triggerPointSlider2.value()
    UIConfig['triggerValue3'] = form.ui.triggerPointSlider3.value()
    UIConfig['triggerValue4'] = form.ui.triggerPointSlider4.value()
    UIConfig['repeatValue1'] = form.ui.repeat1SB.value()
    UIConfig['repeatValue2'] = form.ui.repeat2SB.value()
    UIConfig['repeatValue3'] = form.ui.repeat3SB.value()
    UIConfig['repeatValue4'] = form.ui.repeat4SB.value()
    UIConfig['triggerDir1'] = form.ui.trigger1DirRB.isChecked()
    UIConfig['triggerDir2'] = form.ui.trigger2DirRB.isChecked()
    UIConfig['triggerDir3'] = form.ui.trigger3DirRB.isChecked()
    UIConfig['triggerDir4'] = form.ui.trigger4DirRB.isChecked()
    UIConfig['action1'] = form.actionList[form.ui.action1CB.currentIndex()].action
    UIConfig['action2'] = form.actionList[form.ui.action2CB.currentIndex()].action
    UIConfig['action3'] = form.actionList[form.ui.action3CB.currentIndex()].action
    UIConfig['action4'] = form.actionList[form.ui.action4CB.currentIndex()].action
    UIConfig['standAlone'] = form.ui.standAloneCB.checkState()
    dataBase.writePickle(dataBase,'userconfig.pkl',UIConfig )
    print(UIConfig)
    
def restoreLastUserUI():
    UIConfig = dataBase.readPickle(dataBase,'userconfig.pkl')
    curBrandIndex = (form.ui.brandCB.findText(UIConfig['camBrand']))
    form.ui.brandCB.setCurrentIndex(curBrandIndex)
    curCamIndex = (form.ui.modelCB.findText(UIConfig['camModel']))
    form.selectBtn()
    form.ui.modelCB.setCurrentIndex(curCamIndex)
    form.ui.enable1CB.setCheckState(UIConfig['enable1'])
    form.ui.enable2CB.setCheckState(UIConfig['enable2'])
    form.ui.enable3CB.setCheckState(UIConfig['enable3'])
    form.ui.enable4CB.setCheckState(UIConfig['enable4'])
    form.ui.triggerPointSlider1.setValue(UIConfig['triggerValue1']) 
    form.triggerSliderChanged1()
    form.ui.triggerPointSlider2.setValue(UIConfig['triggerValue2']) 
    form.triggerSliderChanged2()
    form.ui.triggerPointSlider3.setValue(UIConfig['triggerValue3']) 
    form.triggerSliderChanged3()
    form.ui.triggerPointSlider4.setValue(UIConfig['triggerValue4']) 
    form.triggerSliderChanged4()
    form.ui.repeat1SB.setValue(UIConfig['repeatValue1'])
    form.ui.repeat2SB.setValue(UIConfig['repeatValue2'])
    form.ui.repeat3SB.setValue(UIConfig['repeatValue3'])
    form.ui.repeat4SB.setValue(UIConfig['repeatValue4'])
    
    if (UIConfig['triggerDir1']): # For some reason setChecked will not uncheck a radiobtn in a group 
        form.ui.trigger1DirRB.setChecked(True)
    else:
        form.ui.trigger1DirRB_2.setChecked(True)
    if (UIConfig['triggerDir2']):
        form.ui.trigger2DirRB.setChecked(True)
    else:
        form.ui.trigger2DirRB_2.setChecked(True)
    if (UIConfig['triggerDir3']):
        form.ui.trigger3DirRB.setChecked(True)
    else:
        form.ui.trigger3DirRB_2.setChecked(True)
    if (UIConfig['triggerDir4']):
        form.ui.trigger4DirRB.setChecked(True)
    else:
        form.ui.trigger4DirRB_2.setChecked(True)
    
    curAction1 = (form.ui.action1CB.findText(UIConfig['action1']))
    form.ui.action1CB.setCurrentIndex(curAction1)
    curAction2 = (form.ui.action2CB.findText(UIConfig['action2']))
    form.ui.action2CB.setCurrentIndex(curAction2)
    curAction3 = (form.ui.action3CB.findText(UIConfig['action3']))
    form.ui.action3CB.setCurrentIndex(curAction3)
    curAction4 = (form.ui.action4CB.findText(UIConfig['action4']))
    form.ui.action4CB.setCurrentIndex(curAction4)
    
    form.ui.standAloneCB.setCheckState(UIConfig['standAlone'])
    
servoMin = 650
servoMax = 2350
app = QtGui.QApplication(sys.argv)
dataBase = DataBase
form = StratGUI()
form.show()
form.connected = False
form.ports = scan()

servoCheck = TaskThread()
servoCheck.setInterval(0.5)
QtCore.QObject.connect(servoCheck, QtCore.SIGNAL("update(QString)"), updateServoValue)
form.updateInterface()
app.exec_()

