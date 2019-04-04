'''
-------------------------------------------------------
Name:   Drive with bluetooth control
Creator:  Aida Manzano
Date:	20 March 2019
-------------------------------------------------------
This program does the following:
1. Define a number of dance moves / motor movements
2. Connect to bluetooth
3. Trigger dancemoves on in-app button press on mobile device
'''

import pyb
from pyb import Pin, Timer, UART

from motor import DRIVE
d = DRIVE()
#initialise UART communication
uart = UART(6)
uart.init(9600, bits=8, parity = None, stop = 2)
mode = 0

def dancemoves(move, pwm):
    if move == 'f':
        d.right_forward(pwm)
        d.left_forward(pwm)
        #self.duration = 2
    elif move == 'b':
        d.right_back(pwm)
        d.left_back(pwm)
        #self.duration = 2
    elif move == 'l':   #left turn
        d.left_forward(pwm/2)
        d.right_forward(pwm)
        pyb.delay(1700)
        d.left_forward(pwm)
        #self.duration = 3
    elif move == 'r':   #right turn
        d.right_forward(pwm/2)
        d.left_forward(pwm)
        pyb.delay(1700)
        d.right_forward(pwm)
        #self.duration = 3
    elif move == 'c': #left circle
        d.right_forward(pwm)
        d.left_back(pwm)
        #self.duration = 3
    elif move == 'x': #right circle
        d.left_forward(pwm)
        d.right_back(pwm)
        #self.duration = 3
    elif move == 's':
        d.stop()
        #self.duration = 2
    elif move == 'z':
        d.left_forward(pwm)
        d.right_forward(pwm/5)
    else:
        pass

while True:
    if uart.any() >= 10:
        command = uart.read(10)
        if command[2] == ord('5'):
            print(command)
            dancemoves('f', 60)
        elif command[2] == ord('6'):
            dancemoves('b', 60)
        elif command[2] == ord('7'):
            dancemoves('l', 60)
        elif command[2] == ord('8'):
            dancemoves('r', 60)
        elif command[2] == ord('1'):
            dancemoves('c', 60)
        elif command[2] == ord('2'):
            dancemoves('x', 60)
        elif command[2] == ord('3'):
            dancemoves('s', 60)
        else:
            pass
