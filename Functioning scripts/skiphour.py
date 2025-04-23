import RPi.GPIO as GPIO
import time
from time import sleep

stepMin = 31
stepHr = 37
enaMin = 29
enaHr = 35
dirMin = 40
dirHr = 33
switchMin = 32
switchHr = 22

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

GPIO.setup(stepMin, GPIO.OUT)
GPIO.setup(stepHr, GPIO.OUT)
GPIO.setup(enaMin, GPIO.OUT)
GPIO.setup(enaHr, GPIO.OUT)
GPIO.setup(dirMin, GPIO.OUT)
GPIO.setup(dirHr, GPIO.OUT)
GPIO.setup(switchMin, GPIO.IN)
GPIO.setup(switchHr, GPIO.IN)

GPIO.output(dirMin, GPIO.HIGH)
GPIO.output(dirHr, GPIO.HIGH)
GPIO.output(enaMin, GPIO.LOW)
GPIO.output(enaHr, GPIO.LOW)

delayMotorFast = 0.001 #fast setting used for set up

def minuteFast():
    global stepMin
    global delayMotorFast
    GPIO.output(stepMin, GPIO.HIGH)
    sleep(delayMotorFast)
    GPIO.output(stepMin, GPIO.LOW)
    sleep(delayMotorFast)

def minSearch():
    global switchMin
    if GPIO.input(switchMin) == GPIO.HIGH:
        sleep(0.001)
        while GPIO.input(switchMin) == GPIO.HIGH:
            minuteFast()

def hourFast(): 
    global stepHr
    global delayMotorFast   
    GPIO.output(stepHr, GPIO.HIGH)
    sleep(delayMotorFast)
    GPIO.output(stepHr, GPIO.LOW)
    sleep(delayMotorFast)

def hrSearch():
    global switchHr
    if GPIO.input(switchHr) == GPIO.HIGH:
        sleep(0.001)
        while GPIO.input(switchHr) == GPIO.HIGH:
            hourFast()   

def main():
    
    try:
        if GPIO.input(switchMin) == GPIO.HIGH: #if the minute hand is not on the trigger move to home
            minSearch()
    
        if GPIO.input(switchHr) == GPIO.LOW: #If the hour hand is on the trigger move forward by 500 steps
            for x in range(500):
                hourFast()

        if GPIO.input(switchHr) == GPIO.HIGH: # If the hour hand is not on the trigger move to the next
            hrSearch()

        else: #Exit the programme when done
            pass
        
    except KeyboardInterrupt:
        GPIO.output(enaMin, GPIO.HIGH)
        GPIO.output(enaHr, GPIO.HIGH)
        GPIO.cleanup()
        
if __name__ == "__main__":
    main()


