#!/usr/bin/python
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

running = False
minCount = -1
hrCount = -1

###############################################################################################################
delayMotor = 0.035374 #0.151 * 1.02 = 1/[(0.396rpm * 1000ppr) / 60] change this for speed of both motors
delayMotorFast = 0.001 #fast setting used for set up
deltaMin = delayMotor * 0.00 #2% change every time theres a difference in the time
hrBounce = 200000 #200000 = delay time to stop switch activating
minBounce = 36000 #12000 = delay time to stop switch activating
minRatio = 2433 # 12 hours including 0, change this to configure the ratio between disc
hrRatio = 200 #Ratio multiplier
startHour = 22 #change start hour
endHour = startHour + 12 # 12 hours run time
endMinute = 30
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
    global minRatio
    global delayMotor
    global stepMin
    for x in range (minRatio):
        GPIO.output(stepMin, GPIO.HIGH)
        sleep(delayMotor)
        GPIO.output(stepMin, GPIO.LOW)
        sleep(delayMotor)
    
def hourFwd():
    global hrRatio
    global delayMotor
    global stepHr
    for i in range (hrRatio):
        GPIO.output(stepHr, GPIO.HIGH)
        sleep(delayMotor)
        GPIO.output(stepHr, GPIO.LOW)
        sleep(delayMotor)

def minuteFast():
    global stepMin
    global delayMotorFast
    GPIO.output(stepMin, GPIO.HIGH)
    sleep(delayMotorFast)
    GPIO.output(stepMin, GPIO.LOW)
    sleep(delayMotorFast)
    
def hourFast(): 
    global stepHr
    global delayMotorFast   
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
    global running

    if GPIO.input(switchHr) == GPIO.LOW:
        print("hrdetect")
        if running == True:
            hrCount += 1
            print(hrCount)
            hrCompare()

def minCompare():
    global minCount
    global delayMotor
    global deltaMin
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
    global minRatio
    global startHour
    hourStamp = int(time.strftime('%H'))
    minuteStamp = int(time.strftime('%M'))

    if hrCount + startHour < hourStamp:
        minRatio -= 1
        print("ratio down")
    elif hrCount + startHour > hourStamp & minuteStamp > 5 :
        minRatio += 1
        print("ratio up")

def minSearch():
    global minCount
    global switchMin

    if GPIO.input(switchMin) == GPIO.HIGH:
        sleep(0.001)
        while GPIO.input(switchMin) == GPIO.HIGH:
            minuteFast()
    minCount = -1

def hrSearch():
    global hrCount
    global switchHr

    if GPIO.input(switchHr) == GPIO.HIGH:
        sleep(0.001)
        while GPIO.input(switchHr) == GPIO.HIGH:
            hourFast()                
    hrCount = -1
    
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
    global startHour
    global endHour
    
    try:
        while True:
            hourStamp = int(time.strftime('%H'))
            minuteStamp = int(time.strftime('%M'))

            if startHour<=hourStamp<endHour:  #Running Mode
                if not (hourStamp == endHour - 1 and minuteStamp > endMinute) :
                    running = True
                    GPIO.output(enaMin, GPIO.LOW) #Enable min motor
                    GPIO.output(enaHr, GPIO.LOW) #Enable hr motor
                    
                    minuteFwd()
                    hourFwd()

                else:
                    sleep(1)

            else:   #Sleep mode    
                running = False
                
                minSearch()
                hrSearch()

                if GPIO.input(switchMin) == GPIO.HIGH:
                    minSearch()

                if GPIO.input(switchHr) == GPIO.HIGH:
                    hrSearch()
                
                if GPIO.input(switchMin) == GPIO.LOW:
                    GPIO.output(enaMin, GPIO.HIGH) #Disable min motor

                if GPIO.input(switchHr) == GPIO.LOW:
                    GPIO.output(enaHr, GPIO.HIGH) #Disable hr motor
                
    except KeyboardInterrupt:
        GPIO.output(enaMin, GPIO.HIGH)
        GPIO.output(enaHr, GPIO.HIGH)
        GPIO.cleanup()
        
if __name__ == "__main__":
    main()

