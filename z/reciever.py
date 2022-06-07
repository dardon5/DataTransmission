#!/usr/bin/python

import _thread
import time
import serial
import wiringpi
from operator import ge
from AESCipher import *

ser = serial.Serial("/dev/ttyS0", baudrate=9600)
redlight=26
greenlight=19
buttonsend=13
buttonreset=2
toner = 3

gas_release_button = False
reset_button = False
pairingmode = False
flag = False
pass_val = True
check_recv = False
message = ''
msg = ''
obj = AESCipher('key')


wiringpi.wiringPiSetupGpio()
wiringpi.pinMode(redlight,1)
wiringpi.pinMode(greenlight,1)
wiringpi.pinMode(toner, 1)

 
def process_input(info):
        character = ''
        message = ''
        current = ser.read(info)
        if current == b'$':
            while character != '$':
                try:
                    character = ser.read(info).decode('utf-8')
                    message = message + character
                except:
                    pass
            return message[:-1]
        else:
            return ""


def lights(threadName, pass_val):
    print("This message is from", threadName)
    global message, pairingmode
    while 1:
        if msg == 'gas':
            wiringpi.digitalWrite(redlight,1)
            wiringpi.digitalWrite(greenlight,0)
            wiringpi.digitalWrite(toner,1)
            time.sleep(10)
            wiringpi.digitalWrite(toner,0)
        else: 
            wiringpi.digitalWrite(redlight,0)
            wiringpi.digitalWrite(greenlight,1)
            wiringpi.digitalWrite(toner,0)
            
        time.sleep(1)
        
        if pairingmode:
            wiringpi.digitalWrite(redlight,1)
            wiringpi.digitalWrite(greenlight,1)
        # else:
        #     print("Blink is off")
        time.sleep(1)
        
# def communication(threadName, pass_val):
#     print("This message is from", threadName)
#     while 1:
#         if check_recv:
#             ser.write('recieved'.encode('utf-8'))
#             time.sleep(2)
           
def recieve(threadName, pass_val):
    print("This message is from", threadName)
    global message, msg, check_recv, obj, pairingmode 
    while 1:
        while pairingmode:
            text_file_2 = open("/media/pi/USB-2/key.txt", "r")
            password = text_file_2.read()
            text_file_2.close()
            while ser.inWaiting():
                info = ser.inWaiting()
                compare = ser.read(info).decode("utf-8")
                if compare == password:
                    obj = AESCipher(password)
                    ser.write('success'.encode('utf-8'))
                    pairingmode = False
                    print('authentication succeeded')
                else:
                    ser.write('passwords do not match and/or USB not connected properly'.encode('utf-8'))
                    print('passwords do not match and/or USB not connected properly')

        while ser.inWaiting():
            check_recv = False
            info = ser.inWaiting()
            character = ''
            message = ''
            message = process_input(info)

            if len(message) == 44:
                message = obj.toDecryption(message)
                if message == "$proper$" or "gas":
                    msg = message
                    check_recv = True
            print(message[1:-1])
            
              
try:
   _thread.start_new_thread(lights, ("Lights Thread", pass_val))
   _thread.start_new_thread(recieve, ("Sender Thread", pass_val))
#    _thread.start_new_thread(communication, ("Communication Thread", pass_val))

except:
   print ("Error: unable to start thread")

while 1:
    pass

