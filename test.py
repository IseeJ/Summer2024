#Ver 1

import serial
import time
from datetime import datetime as dt
serial_port = '/dev/cu.usbserial-110' 
baud_rate = 38400 
hex_data = [0x01, 0x16, 0x7B, 0x28, 0x48, 0x4C, 0x45, 0x48, 0x54, 0x43, 0x34, 0x30, 0x39, 0x35, 0x67, 0x71, 0x29, 0x7D, 0x7E, 0x04]
byte_data = bytearray(hex_data)

ser = serial.Serial(serial_port, baud_rate, timeout=1)


def readtemp(ser, byte_data):
    ser.write(byte_data)
    print(f"Write: {byte_data.hex()}")     
    time.sleep(0.1) 
    print(ser.in_waiting)
    if ser.in_waiting == 37:
        response = ser.readline()
        if response:
            response_hex = response.hex()        
            print(f"Read:  {response_hex}")

            T1 = int(response_hex[34:36] + response_hex[32:34], 16) / 10  # T1                                 
            T2 = int(response_hex[38:40] + response_hex[36:38], 16) / 10  # T2                                 
            T3 = int(response_hex[42:44] + response_hex[40:42], 16) / 10  # T3                                 
            T4 = int(response_hex[46:48] + response_hex[44:46], 16) / 10  # T4
            
            T5 = int(response_hex[50:52] + response_hex[48:50], 16) / 10  # T5                                 
            T6 = int(response_hex[54:56] + response_hex[52:54], 16) / 10  # T6                                 
            T7 = int(response_hex[58:60] + response_hex[56:58], 16) / 10  # T7                                
            T8 = int(response_hex[62:64] + response_hex[60:62], 16) / 10  # T8
    
            print(f"T1: {T1}, T2: {T2}, T3: {T3}, T4: {T4}\nT5: {T5}, T6: {T6}, T7: {T7}, T8: {T8}\n")
    
start_time = time.time()
while (time.time() - start_time) <= 5:
    try:
        now = dt.now()
        nowstr = now.strftime('%Y%m%dT%H%M%S')
        print(nowstr)
        readtemp(ser, byte_data)

    except KeyboardInterrupt:

        ser.close()
        exit()
ser.close()
