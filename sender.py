
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

#lights conditions
green = False
red = False
#pairingmode variable condition
pairingmode = True
#ignore, this just to make threads work
pass_val = True
#variable for gas condition
gas = False
start_checking = False
#message to be sent 
message = ""
#variable to get password
password = ''

#necessary to enable GPIO pins
wiringpi.wiringPiSetupGpio()

#setting each component to output (a 1 in the second field indicates output, a 0 indicates an input)
wiringpi.pinMode(redlight,1)
wiringpi.pinMode(greenlight,1)
wiringpi.pinMode(buttonsend,0)
wiringpi.pinMode(buttonreset,0)

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
       
def communication(threadName, pass_val):
    print("This message if from", threadName)
    while 1:
#         if start_checking:
#             print('here')
#             while ser.inWaiting():
#                 info = ser.inWaiting()
#                 verification = process_input(info)
#                 if verification == 'recieved':
#                     print('yes')
#                 else:
#                     print('no!')
#         else:
            pass
           

#thread in charge of buttons. If gas release button is pressed, then message is updated and light conditions change
#if not, light conditions remain the same, message is unchanged. reset button puts system into pairing mode.               
def buttons(threadName, pass_val):
    print("This message is from", threadName,)
    global blink, red, green, pairingmode, message, gas
    while 1:
        if wiringpi.digitalRead(buttonreset) == 1: #not pressed
            if wiringpi.digitalRead(buttonsend) == 1: #not pressed
                green = True
                red = False
                message = "proper"
            else:
                red = True
                green = False
                gas = True
               
        else:
            pairingmode = True
            red = True
            green = True
        time.sleep(1)

#this is the thread in charge of the main things of the program, the program starts in pairing mode, this is how pairingmode works:
#1. read password from USB(sender)
#2. encrypt this password
#3. send this password to reciever(sender)
#4. read password from USB(reciever)
#5. get password on serial connection sent from sender(reciever)
#6. compare password
#7a. if they match then a message is sent back saying all good and pairing mode is no longer true
#7b. if they do not match then a message is displayed saying that the passwords are not a match or the USBs are not connected properly.     

def sender(threadName, pass_val):
    print("This message is from", threadName)
    encrypted = ''
    stay = True
    global gas, pairingmode, password, start_checking
    while 1:
        if pairingmode:
            text_file_1 = open("/media/pi/USB-1/key.txt", "r")
            password = text_file_1.read()
            text_file_1.close()
            password = "$" + password + "$"
            for i in range(len(password)):
                time.sleep(0.1)
                ser.write(password[i].encode('utf-8'))
            ser.flush()
            password = password[1:-1]
            while stay:
                while ser.inWaiting():
                    info = ser.inWaiting()
                    response = process_input(info)
                    compare = 'verified'
                    if response == compare:
                        print('Authentication Succeeded')
                        pairingmode = False
                        start_checking = True
                        stay = False
                        time.sleep(2)
                        break
                    else:
                        print('Passwords do not match and/or USB not connected properly')
        else:
            #password assignment for encryption
            obj = AESCipher(password)
            #the following code sends the message to the reciever depending on gas condition.
            if gas is True and pairingmode is False:
                encrypted = (obj.toEncryption("gas"))
                encrypted = "$" + encrypted + "$"
                ser.flush()
                for i in range(len(encrypted)):
                    time.sleep(0.1)
#                     print(encrypted[i])
                    ser.write(encrypted[i].encode('utf-8'))
                time.sleep(5)
                ser.flush()
            else:
                if pairingmode is False and gas is False:
                    encrypted = (obj.toEncryption(message))
                    encrypted = "$" + encrypted + "$"
                    ser.flush()
                    for i in range(len(encrypted)):
                        time.sleep(0.1)
#                         print(encrypted[i])
                        ser.write(encrypted[i].encode('utf-8'))
                    time.sleep(5)
                    ser.flush()
                    
#threads initialization        
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