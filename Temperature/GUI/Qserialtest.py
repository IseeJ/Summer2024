from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
import time

ser = QSerialPort()
ser.setPortName('/dev/cu.usbserial-110')
ser.setBaudRate(QSerialPort.Baud38400)


hex_data = [0x01, 0x16, 0x7B, 0x28, 0x48, 0x4C, 0x45, 0x48, 0x54, 0x43, 0x34, 0x30, 0x39, 0x35, 0x67,0x71, 0x29, 0x7D, 0x7E, 0x04]
byte_data = bytearray(hex_data)

ser.write(byte_data)
time.sleep(0.1)

if QSerialPort().bytesAvailable() >= 37:
    response = self.serial.readLine()
    if response:
        response_hex = response.hex()
        print(response_hex)
        #temperatures = parse_temp(response_hex)

                        
