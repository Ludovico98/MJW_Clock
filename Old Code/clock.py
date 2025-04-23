#!/usr/bin/python
import RPi.GPIO as GPIO
import time
import threading
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

running = False
minCount = -1
hrCount = -1

###############################################################################################################
delayMotor = 0.03499565 #0.151 * 1.02 = 1/[(0.396rpm * 1000ppr) / 60] change this for speed of both motors
delayMotorFast = 0.001 #fast setting used for set up
deltaMin = delayMotor * 0.00 #2% change every time theres a difference in the time
hrBounce = 200000 #200000 = delay time to stop switch activating
minBounce = 36000 #12000 = delay time to stop switch activating
hrMinRatio = 12 # 60 states 0-58=minute tick, 59=hour tick, change this to configure the ratio between disc
startHour = 6 #change start hour
endHour = 18 # change end hour
###############################################################################################################

def startupMin():
    GPIO.output(enaMin, GPIO.LOW)
    while GPIO.input(switchMin) == GPIO.HIGH:
        minuteFast()

def startupHr():
    GPIO.output(enaMin, GPIO.LOW)
    while GPIO.input(switchHr) == GPIO.HIGH:
        hourFast()

def minuteFwd():
    for x in range (hrMinRatio):
        GPIO.output(stepMin, GPIO.HIGH)
        sleep(delayMotor)
        GPIO.output(stepMin, GPIO.LOW)
        sleep(delayMotor)
    
def hourFwd():
    GPIO.output(stepHr, GPIO.HIGH)
    sleep(delayMotor)
    GPIO.output(stepHr, GPIO.LOW)
    sleep(delayMotor)

def minuteFast():
    GPIO.output(stepMin, GPIO.HIGH)
    sleep(delayMotorFast)
    GPIO.output(stepMin, GPIO.LOW)
    sleep(delayMotorFast)
    
def hourFast():    
    GPIO.output(stepHr, GPIO.HIGH)
    sleep(delayMotorFast)
    GPIO.output(stepHr, GPIO.LOW)
    sleep(delayMotorFast)

def switchMinDetect(channel):
    global switchMin
    global minCount
    global running
    
    if GPIO.input(switchMin) == GPIO.LOW:
        print("mindetect")
        if running == True:
            minCount += 1
            print(minCount)
            minCompare()
    
def switchHrDetect(channel):
    global switchHr
    global hrCount
    
    if GPIO.input(switchHr) == GPIO.LOW:
        print("hrdetect")
        if running == True:
            hrCount += 1
            print(hrCount)
            hrCompare()

def minCompare():
    global minCount
    global delayMotor
    global deltamin
    minuteStamp = int(time.strftime('%M'))
    secondStamp = int(time.strftime('%S'))
    
    if minCount < minuteStamp:
        delayMotor = delayMotor - deltaMin
        print("speed up")
    elif minCount > minuteStamp & secondStamp > 30 :
        delayMotor = delayMotor + deltaMin
        print("speed down")
        
def hrCompare():
    global hrCount
    global hrMinRatio
    hourStamp = int(time.strftime('%H'))
    minuteStamp = int(time.strftime('%M'))
    if hrCount + 11 < hourStamp:
        hrMinRatio -= 1
        print("ratio down")
    elif hrCount + 11 > hourStamp & minuteStamp > 5 :
        hrMinRatio += 1
        print("ratio up")

startupMin()
startupHr()

GPIO.add_event_detect(switchMin, GPIO.FALLING, callback=switchMinDetect, bouncetime = minBounce)
GPIO.add_event_detect(switchHr, GPIO.FALLING, callback=switchHrDetect, bouncetime = hrBounce)

def main():
    global hrCount
    global minCount
    global running
    global hrBounce
    global minBounce
    
    try:
        while True:
            hourStamp = int(time.strftime('%H'))
            minuteStamp = int(time.strftime('%M'))
            secondStamp = int(time.strftime('%S'))


            while startHour<hourStamp<endHour:#in between 11am and 5pm
                running = True
                GPIO.output(enaMin, GPIO.LOW)
                GPIO.output(enaHr, GPIO.LOW)
                
                hourStamp = int(time.strftime('%H'))
                minuteStamp = int(time.strftime('%M'))
                secondStamp = int(time.strftime('%S'))
                
                minuteFwd()
                hourFwd()

            while not startHour<hourStamp<endHour:       
                running = False
                while GPIO.input(switchMin) == GPIO.HIGH:
                    minuteFast()
                minCount = -1
                
                while GPIO.input(switchHr) == GPIO.HIGH:
                    hourFast()                
                hrCount = -1
                
                GPIO.output(enaMin, GPIO.HIGH)
                GPIO.output(enaHr, GPIO.HIGH)
                
    except KeyboardInterrupt:
        GPIO.output(enaMin, GPIO.HIGH)
        GPIO.output(enaHr, GPIO.HIGH)
        GPIO.cleanup()
        
if __name__ == "__main__":
    main()
