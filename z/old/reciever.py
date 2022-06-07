#!/usr/bin/python

#imports needed for system and encryption file import

import _thread 
import time
import serial
import wiringpi
from operator import ge
from AESCipher import *

#defining serial connection, port it will be on, and baudrate for the connection
ser = serial.Serial("/dev/ttyS0", baudrate=9600)

#pin numbers for each component are assigned. Refer to raspberry pi pin layout for details. 
redlight=26
greenlight=19
buttonsend=13
buttonreset=2
toner = 3


#variable for pairing mode between the two pis
pairingmode = False
#placeholder variable for initiating the threads, ignore.
pass_val = True
#variable for keeping track of messages
check_recv = False
#variables for the messages recieved
message = ''
msg = ''

#setup for pins for the pis
wiringpi.wiringPiSetupGpio()
wiringpi.pinMode(redlight,1) # a 1 on the second parameter indicates an output while a 0 would indicate an input
wiringpi.pinMode(greenlight,1)
wiringpi.pinMode(toner, 1)

#function for processing what is on the serial connection, messages recieved are in the form or $message$, 
# the $ character is used for identifaction at the start and end of the message, this is necessary because of the
# noise on the serial connection.  
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

#thread in charge of the lights, these wary depending on where the system is currently. 
def lights(threadName, pass_val):
    print("This message is from", threadName)
    global message, pairingmode
    while 1:
        if msg == 'gas': #conditions for when the gas is triggered
            wiringpi.digitalWrite(redlight,1)
            wiringpi.digitalWrite(greenlight,0)
            wiringpi.digitalWrite(toner,1)
            time.sleep(10)
            wiringpi.digitalWrite(toner,0)
        else: 
            wiringpi.digitalWrite(redlight,0) #conditions for when gas is not triggered / system working properly
            wiringpi.digitalWrite(greenlight,1)
            wiringpi.digitalWrite(toner,0)
            
        time.sleep(1)
        
        if pairingmode: #conditions for pairing mode
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

#reciever thread, the first portion of the code is to handle pairing mode which works as follows:
# 1. Password is read from the USB on the sender pi (sender)
# 2. Password is sent over the serial connection (sender)
# 3. Password is read from the USB on the reciever pi (reciever)
# 4. Password is read from the serial connection (reciever)
# 5. Both passwords are compared to check if they match (reciever)
# 6a. If they both match then an authentication message is sent back to the sender and the password is assigned to the encryption object and pairing mode is no longer in effect(reciever)             
# 6b. If they don't match then a message is sent back to the sender saying this and pairing mode is still in effect until the passwords match and the USBs are plugged in properly(reciever)             
# 7a. If the message recieved is an authentication message the password is assigned to the encryption object and pairing mode is no longer in effect (sender)

def recieve(threadName, pass_val):
    print("This message is from", threadName)
    global message, msg, check_recv, obj, pairingmode 
    while 1:
        while pairingmode: #while in pairing mode do the following
            
            #handling the password being read from the USB
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

