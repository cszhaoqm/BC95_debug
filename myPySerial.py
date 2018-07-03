# -*- coding: utf-8 -*-
import binascii
import re
import sys
import time

from PyQt5.Qt import *
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtWidgets import *

class PyQt_Serial(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.CreateItems()
        self.CreateLayout()
        self.CreateSignalSlot()

        self.setWindowTitle('Quectel BC95 NB-IoT Tester')
        self.setWindowIcon(QIcon('./icon.ico'))
        self.setFont(QFont('Courier New', 9))

        self.sendCount = 0
        self.receiveCount = 0
        self.encoding = 'utf-8'
        self.updateTimer.start(100)

    def CreateItems(self):
        self.com = QSerialPort()

        self.comNameLabel = QLabel('COM Port')
        self.comNameLabel.setFixedWidth(70)
        self.comNameCombo = QComboBox()
        self.on_refreshCom()

        self.comNameCombo.setFixedWidth(70)
        self.baudLabel = QLabel('Baud Rate')
        self.baudLabel.setFixedWidth(70)
        self.baudCombo = QComboBox()
        self.baudCombo.addItems(
            ('9600', '19200', '115200', '250000', '1000000'))
        self.baudCombo.setEditable(True)
        self.baudCombo.setCurrentIndex(0)
        self.baudCombo.setFixedWidth(70)
        self.bupt = QLabel('')  # BUPT
        self.bupt.setFont(QFont('Arial', 40, italic=True))

        self.encodingGroup = QButtonGroup()
        self.openButton = QPushButton('Open COM')
        self.openButton.setFixedWidth(80)
        self.closeButton = QPushButton('Close COM')
        self.closeButton.setFixedWidth(80)
        self.clearReceivedButton = QPushButton('Clear Rcv Buffer')
        self.clearReceivedButton.setFixedWidth(165)
        self.hexShowingCheck = QCheckBox('HEX')
        self.hexShowingCheck.setFixedWidth(165)
        self.saveReceivedButton = QPushButton('Save Data')
        self.saveReceivedButton.setFixedWidth(165)
        self.openButton = QPushButton('Open COM')
        self.openButton.setFocus()
        self.openButton.setFixedWidth(70)
        self.closeButton = QPushButton('Close COM')
        self.closeButton.setFixedWidth(70)
        self.refreshComButton = QPushButton('Update COM')
        self.refreshComButton.setFixedWidth(165)

        self.receivedDataEdit = QPlainTextEdit()
        self.receivedDataEdit.setReadOnly(True)
        self.receivedDataEdit.setFont(QFont('Courier New', 11))

        self.startUdpButton = QPushButton('Start UDP')
        self.startUdpButton.setFixedWidth(80)

        self.stopUdpButton = QPushButton('Stop UDP')
        self.stopUdpButton.setFixedWidth(80)

        self.atCmdEdit = QPlainTextEdit()
        self.atCmdEdit.setFont(QFont('Courier New', 11))

        self.sendEdit = QPlainTextEdit()
        self.sendEdit.setFont(QFont('Courier New', 11))

        self.initButton = QPushButton('Init BC95')
        self.initButton.setFixedWidth(165)

        self.sendAtButton = QPushButton('Send AT Cmd')
        self.sendAtButton.setFixedWidth(165)

        self.sendButton = QPushButton('CoAP Send')
        self.sendButton.setFixedWidth(165)
        
        self.sendUdpButton = QPushButton('UDP Send')
        self.sendUdpButton.setFixedWidth(165)

        self.timerSendCheck = QCheckBox('Send Timer   Period(ms)')
        self.timerPeriodEdit = QLineEdit('1000')
        self.clearInputButton = QPushButton('Clear Input')
        self.clearCouterButton = QPushButton('Clear Cnt')

        self.comStatus = QLabel('Status：COM OFF')
        self.sendCountLabel = QLabel('Send：0')
        self.receiveCountLabel = QLabel('Recv：0')

        self.sendTimer = QTimer()
        self.updateTimer = QTimer()

        self.sendAtButton.setEnabled(False)
        self.closeButton.setEnabled(False)
        self.sendButton.setEnabled(False)
        self.sendUdpButton.setEnabled(False)
        self.initButton.setEnabled(False)
        self.startUdpButton.setEnabled(False)
        self.stopUdpButton.setEnabled(False)

    def CreateLayout(self):
        self.grid = QGridLayout()

        self.grid.addWidget(self.receivedDataEdit, 0, 0, 8, 5)

        self.grid.addWidget(self.comNameLabel, 0, 5)
        self.grid.addWidget(self.comNameCombo, 0, 6)
        self.grid.addWidget(self.baudLabel, 1, 5)
        self.grid.addWidget(self.baudCombo, 1, 6)
        self.grid.addWidget(self.openButton, 2, 5)
        self.grid.addWidget(self.closeButton, 2, 6)
        self.grid.addWidget(self.refreshComButton, 3, 5, 1, 2)
        self.grid.addWidget(self.clearReceivedButton, 4, 5, 1, 2)
        self.grid.addWidget(self.saveReceivedButton, 6, 5, 1, 2)
        self.grid.addWidget(self.hexShowingCheck, 7, 5, 1, 2)

        self.grid.addWidget(self.atCmdEdit, 8, 0, 10, 5)

        self.grid.addWidget(self.initButton, 10, 5, 1, 2)
        self.grid.addWidget(self.startUdpButton, 11, 5)
        self.grid.addWidget(self.stopUdpButton, 11, 6)

        self.grid.addWidget(self.sendAtButton, 12, 5, 1, 2)

        self.grid.addWidget(self.clearInputButton, 13, 5)
        self.grid.addWidget(self.clearCouterButton, 13, 6)

        self.grid.addWidget(self.sendEdit, 18, 0, 2, 5)
        self.grid.addWidget(self.sendButton, 18, 5, 1, 5)
        self.grid.addWidget(self.sendUdpButton, 19, 5,1, 5)

        self.grid.addWidget(self.timerSendCheck, 20, 0)
        self.grid.addWidget(self.timerPeriodEdit, 20, 1)
        self.grid.addWidget(self.comStatus, 20, 2, 1, 2)
        self.grid.addWidget(self.sendCountLabel, 20, 5, 1, 2)
        self.grid.addWidget(self.receiveCountLabel, 20, 6, 1, 2)

        self.grid.setSpacing(5)
        self.setLayout(self.grid)
        self.setFixedSize(700, self.height())
        self.move(0,0)

#       read command flow from txt file    
        filename = 'CommandFlow_only'
        cmdFlow=open(filename,'r').read()
        self.atCmdEdit.insertPlainText(cmdFlow)

    def CreateSignalSlot(self):
        self.openButton.clicked.connect(self.on_openSerial)  # 打开串口
        self.closeButton.clicked.connect(self.on_closeSerial)  # 关闭串口
        self.com.readyRead.connect(self.on_receiveData)  # 接收数据
        self.initButton.clicked.connect(self.on_initModule)  # 发送模块初始化数据
        self.startUdpButton.clicked.connect(self.on_startUdp)  # 启动UDP
        self.stopUdpButton.clicked.connect(self.on_stopUdp)  # 关闭UDP

        self.sendButton.clicked.connect(self.on_sendCoapData)  # 发送CoAP数据
        self.sendAtButton.clicked.connect(self.on_sendAtCmd)  # 发送CoAP数据
        self.sendUdpButton.clicked.connect(self.on_sendUdpData)  # 发送UDP数据
        self.refreshComButton.clicked.connect(self.on_refreshCom)  # 刷新串口状态
        self.clearInputButton.clicked.connect(self.atCmdEdit.clear)  # 清空输入
        self.clearReceivedButton.clicked.connect(
            self.receivedDataEdit.clear)  # 清空接收
        self.clearCouterButton.clicked.connect(self.on_clearCouter)  # 清空计数

        self.saveReceivedButton.clicked.connect(
            self.on_saveReceivedData)  # 保存数据

        self.timerSendCheck.clicked.connect(self.on_timerSendChecked)  # 定时发送开关
        self.sendTimer.timeout.connect(self.on_sendCoapData)  # 定时发送

        self.updateTimer.timeout.connect(self.on_updateTimer)  # 界面刷新
        self.hexShowingCheck.stateChanged.connect(self.on_hexShowingChecked)  # 十六进制显示
        self.timerPeriodEdit.textChanged.connect(self.on_timerSendChecked)

    def on_refreshCom(self):
        self.comNameCombo.clear()
        com = QSerialPort()
        for info in QSerialPortInfo.availablePorts():
            com.setPort(info)
            if com.open(QSerialPort.ReadWrite):
                self.comNameCombo.addItem(info.portName())
                com.close()

    def on_setEncoding(self):
        if self.encodingGroup.checkedId() == 0:
            self.encoding = 'utf-8'
        else:
            self.encoding = 'gbk'

    def on_openSerial(self):
        comName = self.comNameCombo.currentText()
        comBaud = int(self.baudCombo.currentText())
        self.com.setPortName(comName)

        try:
            if self.com.open(QSerialPort.ReadWrite) == False:
                QMessageBox.critical(self, '严重错误', '串口打开失败')
                return
        except:
            QMessageBox.critical(self, '严重错误', '串口打开失败')
            return

        self.com.setBaudRate(comBaud)
        if self.timerSendCheck.isChecked():
            self.sendTimer.start(int(self.timerPeriodEdit.text()))

        self.openButton.setEnabled(False)
        self.closeButton.setEnabled(True)
        self.comNameCombo.setEnabled(False)
        self.baudCombo.setEnabled(False)
        self.sendAtButton.setEnabled(True)
        self.initButton.setEnabled(True)
        self.startUdpButton.setEnabled(False)
        self.stopUdpButton.setEnabled(False)
        self.sendButton.setEnabled(True)
        self.sendUdpButton.setEnabled(True)
        self.refreshComButton.setEnabled(False)
        self.comStatus.setText('Status：%s  ON   Baud Rate %s' % (comName, comBaud))

    def on_closeSerial(self):
        self.com.close()
        self.openButton.setEnabled(True)
        self.closeButton.setEnabled(False)
        self.comNameCombo.setEnabled(True)
        self.baudCombo.setEnabled(True)
        self.initButton.setEnabled(False)
        self.startUdpButton.setEnabled(False)
        self.stopUdpButton.setEnabled(False)
        self.sendButton.setEnabled(False)
        self.sendUdpButton.setEnabled(False)
        self.comStatus.setText('Status：%s  OFF' % self.com.portName())
        if self.sendTimer.isActive():
            self.sendTimer.stop()

    def on_timerSendChecked(self):
        if self.com.isOpen():
            if self.timerSendCheck.isChecked():
                self.sendTimer.start(int(self.timerPeriodEdit.text()))
            else:
                self.sendTimer.stop()
        return

    def on_clearCouter(self):
        self.sendCount = 0
        self.receiveCount = 0
        pass

    def on_updateTimer(self):
        self.sendCountLabel.setText('Send：%d' % self.sendCount)
        self.receiveCountLabel.setText('Recv：%d' % self.receiveCount)
        pass

    def sendRawCmd(self,txCmd):
        if len(txCmd) == 0:
            return
        txData = txCmd +'\r\n'
        n = self.com.write(txData.encode(self.encoding, "ignore"))
        self.sendCount += n
        self.receivedDataEdit.insertPlainText(txData)

    def sendCmd(self,txCmd):
        if len(txCmd) == 0:
            return
        txData ='AT+' + txCmd +'\r\n'
        self.sendRawCmd(txData)

    def on_sendAtCmd(self):
        cursor = self.atCmdEdit.textCursor()
        layOut = cursor.block().layout()
        curPos = cursor.position() - cursor.block().position()
        line = layOut.lineForTextPosition(curPos).lineNumber() + cursor.block().firstLineNumber()
        txData = self.atCmdEdit.document().findBlockByLineNumber(line).text();
        self.sendRawCmd(txData)

        self.atCmdEdit.setFocus()
        cursor.movePosition(QTextCursor.Down)
        self.atCmdEdit.setTextCursor(cursor)
 

    def on_initModule(self):
#        self.sendCmd('NRB')
        self.sendCmd('CMEE=1')
#        self.sendCmd('CGMI')
#        self.sendCmd('CGMM')
#        self.sendCmd('CGMR')
#        self.sendCmd('NBAND?')
#        self.sendCmd('NCONFIG?')
        self.sendCmd('CGSN=1')
        self.sendCmd('CFUN=1')
        self.sendCmd('CIMI')
        self.sendCmd('CGATT=1')
        self.sendCmd('CGATT?')
        self.sendCmd('CFUN?')
        self.sendCmd('CSQ')
#        self.sendCmd('COPS?')
        self.sendCmd('CEREG?')
        self.sendCmd('CSCON?')
        self.sendCmd('NSMI=1')
        self.sendCmd('NNMI=1')
#        self.sendCmd('CGPADDR=1')
        self.sendCmd('NUESTATS')

        self.sendCmd('NCDP=115.29.240.46,5683')
        self.sendCmd('NCDP?')

        self.sendButton.setEnabled(True)
        self.startUdpButton.setEnabled(True)
        self.stopUdpButton.setEnabled(True)

    def on_startUdp(self):
        self.sendCmd('NSOCR=DGRAM,17,10000,1')
        self.sendCmd('NSOST=0,115.29.240.46,6000,28,65703d3836333730333033363539333731382670773d313233343536')
        self.startUdpButton.setEnabled(False)
        self.stopUdpButton.setEnabled(True)
        self.sendUdpButton.setEnabled(True)
        
    def on_stopUdp(self):
        self.sendCmd('NSOCL=0')
        self.startUdpButton.setEnabled(True)
        self.stopUdpButton.setEnabled(False)

    def on_sendCoapData(self):
        txData = self.sendEdit.toPlainText()
        if len(txData) == 0:
            return
        txMesg = binascii.b2a_hex(txData.encode()).decode('ascii')
        txSend = 'NMGS=' + str(int(len(txMesg)/2)) + ',' + txMesg
        self.sendCmd(txSend)

    def on_sendUdpData(self):
#        self.sendCmd('NSOST=0,115.29.240.46,6000,28,65703d3836333730333033363539333731382670773d313233343536')

        txData = self.sendEdit.toPlainText()
        if len(txData) == 0:
            return
        txMesg = binascii.b2a_hex(txData.encode()).decode('ascii')
        txSend = 'NSOST=0,115.29.240.46,6000,' + str(int(len(txMesg)/2)) + ',' + txMesg
        self.sendCmd(txSend)
        

    def on_receiveData(self):
        try:
            '''将串口接收到的QByteArray格式数据转为bytes,并用gkb或utf8解码'''
            receivedData = bytes(self.com.readAll())
        except:
            QMessageBox.critical(self, '严重错误', '串口接收数据错误')
        if len(receivedData) > 0:
            self.receiveCount += len(receivedData)

            if self.hexShowingCheck.isChecked() == False:
                receivedData = receivedData.decode(self.encoding, 'ignore')
                self.receivedDataEdit.insertPlainText(receivedData)
            else:
                data = binascii.b2a_hex(receivedData).decode('ascii')
                pattern = re.compile('.{2,2}')
                hexStr = ' '.join(pattern.findall(data)) + ' '
                self.receivedDataEdit.insertPlainText(hexStr.upper())

        scrollbar = self.receivedDataEdit.verticalScrollBar()
        if scrollbar != 0:
            scrollbar.setSliderPosition(scrollbar.maximum())
            
    def on_hexShowingChecked(self):
        self.receivedDataEdit.insertPlainText('\n')

    def on_saveReceivedData(self):
        fileName, fileType = QFileDialog.getSaveFileName(
            self, '保存数据', 'data', "文本文档(*.txt);;所有文件(*.*)")
        print('Save file', fileName, fileType)

        writer = QTextDocumentWriter(fileName)
        writer.write(self.receivedDataEdit.document())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = PyQt_Serial()
    win.show()
    app.exec_()
    app.exit()
