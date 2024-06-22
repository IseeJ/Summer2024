import time
import serial
def openSerial():
    ser = serial.Serial(
        port='COM5',
        baudrate = 19200,
        parity='N',
        stopbits=1,
        bytesize=8,
        timeout=1
    )
    return ser

def IG_on():
    ser = openSerial()
    ser.write(bytearray(b'#01IG1\r'))

def IG_off():
    ser = openSerial()
    ser.write(bytearray(b'#01IG0\r'))
    
def IG_stat():
    ser = openSerial()
    ser.write(bytearray(b'#01IGS\r'))
    value = ser.readline()
    return value
    
def getConvectronP():
    ser = openSerial()
    ser.write(bytearray(b'#01RDCG1\r'))
    value = ser.readline()
    pressure = value[4:-1]
    ser.close()
    return float(pressure)

def getIonP():
    ser=openSerial()
    ser.write(bytearray(b'#01RD\r'))
    value = ser.readline()
    pressure = value[4:-1]

    ser.close()
    return float(pressure)

def getIonEcurrent():
    ser=openSerial()
    ser.write(bytearray(b'#01RDIGE\r'))
    value = ser.readline()
    return str(value)
    
    
def getUnit():
    ser=openSerial()
    ser.write(bytearray(b'#01RU\r'))
    value = ser.readline()
    ser.close()
    return value[4:-1]
