from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QSpinBox, QHBoxLayout, QVBoxLayout, QLineEdit, QMessageBox
from PyQt5 import QtCore
import serial
from time import sleep

#you can use "ls -l /dev/serial/by-id/" on ubuntu to find port name port name on ubuntu must be like "/dev/ttyACMx"

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        screen_geo = QApplication.primaryScreen().geometry()

        #ui init
        self.btnSendTemp = QPushButton("Send")
        self.btnGetTemp = QPushButton("Get")
        self.leGetTemp = QLineEdit()
        self.lblPort = QLabel("STM Port:")
        self.lePort = QLineEdit()
        self.sbSendTempValue = QSpinBox()
        self.sbSendTempValue.setRange(20, 40)

        #window settings
        self.setWindowTitle("PID Control Panel")
        self.setGeometry(int(screen_geo.width() * 0.25), int(screen_geo.height() * 0.25), int(screen_geo.width() * 0.25), int(screen_geo.height() * 0.15))

        #layout
        self.master = QVBoxLayout()

        row1 = QHBoxLayout()
        row2 = QHBoxLayout()
        row3 = QHBoxLayout()        

        row2.addWidget(self.sbSendTempValue)
        row2.addWidget(self.btnSendTemp)

        row1.addWidget(self.lblPort)
        row1.addWidget(self.lePort)
        self.lePort.setMaximumWidth(int(self.width()/2.1))#half the window size line edit width is kinda weird so i did it that way


        row3.addWidget(self.leGetTemp)
        self.leGetTemp.setMaximumWidth(int(self.width()/2.1))#half the window size
        self.leGetTemp.setReadOnly(True)
        row3.addWidget(self.btnGetTemp)

        self.lblPort.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        
        self.master.addLayout(row1, 33)
        self.master.addLayout(row2, 33)
        self.master.addLayout(row3, 33)

        self.setLayout(self.master)

        #handling events
        self.btnGetTemp.clicked.connect(self.OnClick_btnGetTemp)
        self.btnSendTemp.clicked.connect(self.OnClick_btnSendTemp)




    def OnClick_btnSendTemp(self):
        #Port not empty check
        port = self.lePort.text().strip()

        if (port == ""):
            QMessageBox.critical(None, "Port Error", "Port text box left empty. Please provide Port name")
            return
        
        temperature = self.sbSendTempValue.text().strip()
        #temperature not empty check; should never happen just checking in case
        if (temperature == ""):
            QMessageBox.critical(None, "Temperature value Error", "Temperature text box left empty. Please provide temperature value")
            return
        
        try:
            with serial.Serial(port, 115200, timeout=1, parity=serial.PARITY_NONE) as con:
                print(f"Connected to {port}")
                
                #clearing buffer cuz why not
                con.reset_input_buffer()
                con.flush()

                con.write(f"s{temperature};".encode('utf-8'))
                print(f"send: {temperature}")

        except serial.SerialException as e:
            QMessageBox.critical(None, "Port Error", f"Could not open serial port {port}. Please check if given port is correct\n {e}")
        
        
    def OnClick_btnGetTemp(self):
        port = self.lePort.text().strip()

        #Port not empty check
        if (port == ""):
            QMessageBox.critical(None, "Port Error", "Port text box left empty. Please provide Port name")
            return
        try:
            with serial.Serial(port, 115200, timeout=1, parity=serial.PARITY_NONE) as con:
                print(f"Connected to {port}")
                
                con.reset_input_buffer()
                con.flush()

                msg = "g;"
                con.write(f"{msg}".encode('utf-8'))
                print(f"{msg}")
                sleep(0.01)# wait for msg to go through and info to come
                
                if (con.in_waiting > 0):
                    msg_rx = con.readline().decode('utf-8', errors='replace').strip()
                    self.leGetTemp.setText(msg_rx)
                    print(msg_rx)
                    
        except serial.SerialException as e:
            print(f"Error: Could not open serial port {port}. {e}")
        
        
if __name__ == "__main__":
    app = QApplication([])
    main = MainWindow()
    main.show()
    app.exec_()

