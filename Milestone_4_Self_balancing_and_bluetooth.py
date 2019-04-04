'''
-------------------------------------------------------
Name:   Self-balancing and bluetooth control
Creator:  Hannah Imrie
Date:	20 March 2019
-------------------------------------------------------
This program does the following:
1. Set K values to tune balance of robot
2. Balance the robot on two wheels
3. Control movement of the robot using bluetooth, while balancing
'''

import pyb
from pyb import Pin, Timer, ADC, UART, LED, ADC
from oled_938 import OLED_938
import micropython
from mpu6050 import MPU6050
import time

### Final Variables ###
K_p = 6.65
K_i = 0.25
K_d = 0.3
Debug = False

# Setting initial Variables
cumulative_pitch_error = 0
Error = 0
target = -0.3
g_pitch = 0
Error_dot = 0
A = 1 #Motor A Scalar
B = 1 #Motor B Scalar

micropython.alloc_emergency_exception_buf(100)

# Define Motor Pins
A1 = Pin('X3',Pin.OUT_PP)	# A is right motor
A2 = Pin('X4',Pin.OUT_PP)
B1 = Pin('X7',Pin.OUT_PP)	# B is left motor
B2 = Pin('X8',Pin.OUT_PP)
PWMA = Pin('X1')
PWMB = Pin('X2')

# Set up motor timers
tim = Timer(2, freq=1000)
Motor_A = tim.channel(1, Timer.PWM, pin=PWMA)
Motor_B = tim.channel(2, Timer.PWM, pin=PWMB)

# Define OLED
oled = OLED_938(pinout={'sda': 'Y10', 'scl': 'Y9', 'res': 'Y8'}, height=64,
                   external_vcc=False, i2c_devid=61)

# LED and Potentiometer Pins
pot = ADC(Pin('X11'))

# IMU connected to X9 and X10
imu = MPU6050(1, False)    	# Use I2C port 1 on Pyboard

# Start Bluetooth
uart = UART(6)
uart.init(9600, bits= 8, parity= None, stop= 2)

# Starting Program
oled.poweron()
oled.init_display()
oled.draw_text(0,0,'Group 7')
oled.draw_text(0,10,'Self Balance BlueTooth')
oled.draw_text(0,20, 'Press USR button')
oled.display()
print('Self balance Bluetooth')
print('Waiting for button press')

# Button Press to resume
trigger =pyb.Switch()
while not trigger():
	time.sleep(0.001)
while trigger():pass
print('Button pressed - running Self Balance Bluetooth')

def read_imu(dt):
	global g_pitch
	alpha = 0.9    # larger = longer time constant
	pitch = (imu.pitch())
	pitch_dot = imu.get_gy()
	# complementory filter
	g_pitch = alpha*(g_pitch + pitch_dot*dt) + (1-alpha)*pitch
	if Debug == True:
		print ('pitch:',pitch)
		print('g_pitch:', g_pitch)
		print ('Pitch_dot',pitch_dot)
	return (g_pitch, pitch_dot)

def PID_Control(pitch_angle,pitch_dot,target,K_p,K_i,K_d):
	global cumulative_pitch_error
	global Error_dot
	global Error
	Error = pitch_angle - target
	W = K_p*Error + K_d*pitch_dot + K_i*cumulative_pitch_error
	cumulative_pitch_error += Error
	if Debug == True:
		print ('K_p*Error:',K_p*Error)
		print ('K_d*Error_dot:',K_d*pitch_dot)
		print ('K_i*cumulative_pitch_error:',K_i*cumulative_pitch_error)
		print ('W:',W)
	if abs(Error) < 2: # 2 degree error margin
		 return 0
	# Limit W to 100 or -100
	if W > 100:
		return 100
	elif W < -100:
		return -100
	else:
		return W

try:
	if Debug == True:
		print ('P:',K_p)
		print ('I:',K_i)
		print ('D:',K_d)
	tic1 = pyb.micros()
	while True:
		while uart.any() != 10:
			dt = (pyb.micros() - tic1)*0.000001 # seconds
			if dt > 20000*0.000001:
				# update values
				pitch, pitch_dot = read_imu(dt)
				tic1 = pyb.micros()
				#calculate motor value
				Value = PID_Control(pitch,pitch_dot,target,K_p,K_i,K_d)
				if Debug == True:
					print ('Motor Value:', Value)
				if Value > 0:
					# Right forward
					A1.high()
					A2.low()
					Motor_A.pulse_width_percent(abs(Value)+7)
					# Left forward
					B2.high()
					B1.low()
					Motor_B.pulse_width_percent(abs(Value)+5)
					# motor A ran slower than motor B for the same input
					# So we increased its motor offset
				elif Value < -0:
					# Right back
					A1.low()
					A2.high()
					Motor_A.pulse_width_percent(abs(Value)+7)
					# Left back
					B2.low()
					B1.high()
					Motor_B.pulse_width_percent(abs(Value)+5)
				else:
					A2.high()
					A1.high()
					B2.high()
					B1.high()
		command = uart.read(10)

		if command[2] == ord('5'): # Forward faster by increasing tilt
			target = target + 0.2

		elif command[2] == ord('6'): # Backward faster by decreasing tilt
			target = target - 0.2

		elif command[2] == ord('7'): # Turn Left
			A = A + 0.2
			B = B - 0.2

		elif command[2] == ord('8'): #Turn Right
			B = B + 0.2
			A = A - 0.2

		elif command[2] == ord('1'): # reset target to 0
			target = -0.3

		elif command[2] == ord('2'): # reset motor scalars
			A = 1
			B = 1

		elif command [2] == ord('3'): # stop
			A2.high()
			A1.high()
			B2.high()
			B1.high()

finally:
	A1.low()
	A2.low()
	B1.low()
	B2.low()
