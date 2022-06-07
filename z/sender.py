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

blink = False
green = False
red = False
pairingmode = False
pass_val = True
gas = False
message = ""
obj = AESCipher('key')

wiringpi.wiringPiSetupGpio()
wiringpi.pinMode(redlight,1)
wiringpi.pinMode(greenlight,1)
wiringpi.pinMode(buttonsend,0)
wiringpi.pinMode(buttonreset,0)

def lights(threadName, pass_val):
    print("This message is from", threadName)
    global red, green, blink
    while 1:
        if green:
            wiringpi.digitalWrite(greenlight,1)
        else:
            wiringpi.digitalWrite(greenlight,0)
        if red:
            wiringpi.digitalWrite(redlight,1)
        else: 
            wiringpi.digitalWrite(redlight,0)
            
        time.sleep(1)
        
        if pairingmode:
            red = True
            green = True
        time.sleep(1)
        
# def communication(threadName, pass_val):
#     while 1 and pairingmode is False:
#         while ser.inWaiting():
#             info = ser.inWaiting()
#             response = ser.read(info).decode("utf-8")
#             print(response)
           

        
def buttons(threadName, pass_val):
    print("This message is from", threadName,)
    global blink, red, green, pairingmode, message, gas
    while 1:
        if wiringpi.digitalRead(buttonreset) == 1: #not pressed
            if wiringpi.digitalRead(buttonsend) == 1: #not pressed
                green = True
                red = False
                message = "$proper$"
            else:
                red = True
                green = False
                gas = True
        else:
            pairingmode = True
            red = True
            green = True
        time.sleep(1)
        
def sender(threadName, pass_val):
    print("This message is from", threadName)
    encrypted = ''
    global gas, pairingmode, obj
    while 1:
        if pairingmode:
            text_file_1 = open("/media/pi/USB-1/key.txt", "r")
            password = text_file_1.read()
            text_file_1.close()
            ser.write(password.encode('utf-8'))
            time.sleep(2)
            while ser.inWaiting():
                info = ser.inWaiting()
                response = ser.read(info).decode('utf-8')
                if response == 'success':
                    print('authentication succeeded')
                    obj = AESCipher(password)
                    pairingmode = False
                else:
                    print(response)
        else:
            if gas and pairingmode is False:
                encrypted = (obj.toEncryption("$gas$"))
                encrypted = "$" + encrypted + "$"
                for i in range(len(encrypted)):
                    print(encrypted[i])
                    ser.write(encrypted[i].encode('utf-8'))  
            else:
                if message == "$proper$" and pairingmode is False and gas is False:
                    encrypted = (obj.toEncryption(message))
                    encrypted = "$" + encrypted + "$"
                    for i in range(len(encrypted)):
                        time.sleep(0.1)
                        print(encrypted[i])
                        ser.write(encrypted[i].encode('utf-8'))
       
try:
   _thread.start_new_thread(lights, ("Lights Thread", pass_val))
   _thread.start_new_thread(buttons, ("Buttons Thread", pass_val))
   _thread.start_new_thread(sender, ("Sender Thread", pass_val))
#    _thread.start_new_thread(communication, ("Communication Thread", pass_val))

except:
   print ("Error: unable to start thread")

while 1:
   pass


#luces, sending, botones, 
# print(encrypted)
# decrypted = obj.toDecryption(encrypted)
# print(decrypted)
# time.sleep(2)