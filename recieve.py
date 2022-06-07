#!/usr/bin/python

#imports needed to operate program
import _thread
import time
import serial
import wiringpi
from operator import ge
from AESCipher import *

#Establishing the serial connection
ser = serial.Serial("/dev/ttyS0", baudrate=9600)

#GPIO pin numbers for respective components
redlight=26
greenlight=19
buttonsend=13
buttonreset=2
toner = 2

#gas release button condition
gas_release_button = False
#button for putting system into pairing mode
reset_button = False
#pairingmode variable condition
pairingmode = True
#ignore, this just to make threads work
pass_val = True
#variable to check if the reciever has recieved
check_recv = False
#message to be recieved
message = ''
msg = ''
#variable to get password
password = ''
trigger = False


#necessary to enable GPIO pins
wiringpi.wiringPiSetupGpio()
#setting each component to output (a 1 in the second field indicates output, a 0 indicates an input)
wiringpi.pinMode(redlight,1)
wiringpi.pinMode(greenlight,1)
wiringpi.pinMode(toner, 1)

#function to process the information on the serial connection. It works the following way:
#if there is a $ encountered it means that a message is being sent over, it then starts reading what is on the serial connection until it finds another $ sign. It then returns the message
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

#thread in charge of the lights, if the message is ever gas then the redlight will be trigerred as well as the gas, if not then the green light will be on only. if in pairing mode both lights will turn on.
def lights(threadName, pass_val):
    print("This message is from", threadName)
    global message, pairingmode
    while 1:
        if trigger:
            wiringpi.digitalWrite(redlight,1)
            wiringpi.digitalWrite(greenlight,0)
            wiringpi.digitalWrite(toner,1)

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
        
def communication(threadName, pass_val):
    print("This message is from", threadName)
    while 1:
#         if start_checking:
#             if check_recv:
#                 verification = "recieved"
#                 verification = "$" + verification + "$"
#                 ser.flush()
#                 for i in range(len(verification)):
#                     ser.write(verification[i].encode('utf-8'))
#                 ser.flush()
#         else:
            pass

#this is the thread in charge of the main things of the program, the program starts in pairing mode, this is how pairingmode works:
#1. read password from USB(sender)
#2. encrypt this password
#3. send this password to reciever(sender)
#4. read password from USB(reciever)
#5. get password on serial connection sent from sender(reciever)
#6. compare password
#7a. if they match then a message is sent back saying all good and pairing mode is no longer true
#7b. if they do not match then a message is displayed saying that the passwords are not a match or the USBs are not connected properly.

           
def recieve(threadName, pass_val):
    print("This message is from", threadName)
    global message, check_recv, password, pairingmode, start_checking, trigger 
    while 1:
        while pairingmode:
            text_file_2 = open("/media/pi/USB-2/key.txt", "r")
            password = text_file_2.read()
            text_file_2.close()
            while ser.inWaiting():
                info = ser.inWaiting()
                compare = process_input(info)
                if compare == password:
                    yes = 'verified'
                    yes = "$" + yes + "$"
                    for i in range(len(yes)):
                        ser.write(yes[i].encode('utf-8'))
                    ser.flush()
                    pairingmode = False
                    start_checking = True
                    print('Authentication Succeeded')
                    break
                else:
                    print('Passwords do not match and/or USB not connected properly')
                    
        obj = AESCipher(password)
#this part handles information being recieved on serial connection, only if the message is length 44 characters (length of encrypted message) then it is determined what should happen.
#this condition is in place because of the noise from the powering of components generated, meaning that many times there will be undesirable characters. 
        while ser.inWaiting():
            check_recv = False
            info = ser.inWaiting()
            character = ''
            message = ''
            message = process_input(info)
                   
            if len(message) == 44:
                try:
                    message = obj.toDecryption(message)
                    if message == 'gas':
                        print ('Inert Gas Injected')
                        check_recv = True
                        trigger = True
                        time.sleep(10)
                        trigger = False
                    else:
                        check_recv = True
                        print('All clear')
                except:
                    message =''
                    pass


#threads initialization              
try:
   _thread.start_new_thread(lights, ("Lights Thread", pass_val))
   _thread.start_new_thread(recieve, ("Sender Thread", pass_val))
#    _thread.start_new_thread(communication, ("Communication Thread", pass_val))

except:
   print ("Error: unable to start thread")

while 1:
    pass


# "$proper$" or
