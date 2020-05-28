# -*- coding: utf-8 -*-

from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor
import time, atexit

# motor's number used
NUM_MOTOR = 1

# led' number used
NUM_LED = 2

# create a default object, no changes to I2C address or frequency
mh = Adafruit_MotorHAT(addr=0x60)
myMotor = mh.getMotor(NUM_MOTOR)
myLed = mh.getMotor(NUM_LED)

# recommended for auto-disabling motors on shutdown!
def turnOffMotors():
    mh.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(4).run(Adafruit_MotorHAT.RELEASE)

atexit.register(turnOffMotors)

################ Functions to control the motor
# Speed goes from 0 (no movement) to 255 (max voltage/speed)
def move(way, speed):
    'Moves the motor clockwise or counterclockwise at given speed'
    myMotor.setSpeed(speed)
    myMotor.run(way)

def stop():
    'Stops the motor'
    myMotor.run(Adafruit_MotorHAT.RELEASE)

def tense(speed):
    'Simple function to tense the string at given speed'
    move(Adafruit_MotorHAT.FORWARD, speed)

def relax(speed):
    'Simple function to relax the string at given speed'
    move(Adafruit_MotorHAT.BACKWARD, speed)

################ Functions to control de LED
def turnOnLed():
    'Turns on the LED'
    myLed.setSpeed(255)
    myLed.run(Adafruit_MotorHAT.FORWARD)

def turnOffLed():
    'Turns off the LED'
    myLed.run(Adafruit_MotorHAT.RELEASE)
    
