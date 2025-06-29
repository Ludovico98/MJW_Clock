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
delayMotor = 0.035370 #0.151 * 1.02 = 1/[(0.396rpm * 1000ppr) / 60] change this for speed of both motors
delayMotorFast = 0.001 #fast setting used for set up
deltaMin = delayMotor * 0.02 #2% change every time theres a difference in the time
hrBounce = 200000 #200000 = delay time to stop switch activating
minBounce = 36000 #12000 = delay time to stop switch activating
minRatio = 1238 # 12 hours including 0, change this to configure the ratio between disc
hrRatio = 100 #Ratio multiplier
startHour = 12 #change start hour
endHour = startHour + 12 # 12 hours run time
endMinute = 45
# Auto-sync settings
lastSyncTime = 0 #timestamp of last sync check
syncInterval = 300 #sync check every 5 minutes (300 seconds)
maxTimeDrift = 2 #maximum allowed drift in minutes before correction
###############################################################################################################



def startupMin():
    GPIO.output(enaMin, GPIO.LOW)
    while GPIO.input(switchMin) == GPIO.HIGH:
        minuteFast()

def startupHr():
    GPIO.output(enaHr, GPIO.LOW)
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
    elif minCount > minuteStamp and secondStamp > 30:
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
    elif hrCount + startHour > hourStamp and minuteStamp > 5:
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

def calculateTimeDifference():
    """Calculate the difference between computer time and clock time"""
    global minCount, hrCount, startHour
    
    # Get current computer time
    current_time = time.localtime()
    computer_hour = current_time.tm_hour % 12
    if computer_hour == 0:
        computer_hour = 12
    computer_minute = current_time.tm_min
    
    # Calculate clock time based on counts
    clock_hour = (hrCount + startHour) % 12
    if clock_hour == 0:
        clock_hour = 12
    clock_minute = minCount
    
    # Calculate differences
    hour_diff = computer_hour - clock_hour
    minute_diff = computer_minute - clock_minute
    
    # Handle hour rollover
    if hour_diff > 6:
        hour_diff -= 12
    elif hour_diff < -6:
        hour_diff += 12
    
    # Convert total difference to minutes
    total_diff_minutes = (hour_diff * 60) + minute_diff
    
    print(f"Computer time: {computer_hour:02d}:{computer_minute:02d}")
    print(f"Clock time: {clock_hour:02d}:{clock_minute:02d}")
    print(f"Difference: {total_diff_minutes} minutes")
    
    return total_diff_minutes

def autoSyncClock():
    """Automatically synchronize clock with computer time"""
    global minCount, hrCount, lastSyncTime, syncInterval, maxTimeDrift
    global minRatio, delayMotor, deltaMin
    
    current_timestamp = time.time()
    
    # Check if it's time for a sync check
    if current_timestamp - lastSyncTime < syncInterval:
        return
    
    lastSyncTime = current_timestamp
    
    # Only sync if we have valid counts (clock has been running)
    if minCount < 0 or hrCount < 0:
        print("Clock counts not initialized, skipping sync")
        return
    
    time_diff = calculateTimeDifference()
    
    # If difference is small, make minor speed adjustments
    if abs(time_diff) <= maxTimeDrift:
        if time_diff > 0:
            # Clock is behind, speed up slightly
            delayMotor = max(delayMotor - (deltaMin * 2), delayMotor * 0.9)
            print(f"Clock behind by {time_diff} min, speeding up")
        elif time_diff < 0:
            # Clock is ahead, slow down slightly
            delayMotor = delayMotor + (deltaMin * 2)
            print(f"Clock ahead by {abs(time_diff)} min, slowing down")
        else:
            print("Clock is synchronized")
    else:
        # Large difference - need major correction
        print(f"Large time difference detected: {time_diff} minutes")
        print("Performing major time correction...")
        
        # Calculate correction steps needed
        if abs(time_diff) > 30:  # More than 30 minutes off
            print("Clock severely out of sync - consider manual reset")
            # You could add logic here to do a complete reset
            # resetClockToCurrentTime()
        else:
            # Moderate correction - adjust ratios more aggressively
            if time_diff > 0:
                # Clock behind - increase minute ratio temporarily
                minRatio += int(abs(time_diff) * 2)
                print(f"Temporarily increasing minute ratio to {minRatio}")
            else:
                # Clock ahead - decrease minute ratio temporarily  
                minRatio -= int(abs(time_diff) * 2)
                print(f"Temporarily decreasing minute ratio to {minRatio}")

def resetClockToCurrentTime():
    """Reset clock to current computer time (use when severely out of sync)"""
    global minCount, hrCount, running
    
    print("Performing complete clock reset to current time...")
    
    # Temporarily stop normal operation
    was_running = running
    running = False
    
    # Move to home positions
    minSearch()
    hrSearch()
    
    # Get current time
    current_time = time.localtime()
    target_hour = current_time.tm_hour % 12
    if target_hour == 0:
        target_hour = 12
    target_minute = current_time.tm_min
    
    print(f"Setting clock to {target_hour:02d}:{target_minute:02d}")
    
    # Move minute hand to current minute
    for _ in range(target_minute):
        minuteFast()
    minCount = target_minute
    
    # Move hour hand to current hour (approximate)
    hour_steps = target_hour * (hrRatio // 12)  # Approximate steps per hour
    for _ in range(hour_steps):
        hourFast()
    hrCount = target_hour - startHour
    
    # Restore running state
    running = was_running
    print("Clock reset complete")

def main():
    global hrCount
    global minCount
    global running
    global hrBounce
    global minBounce
    global startHour
    global endHour
    
    try:
        print("Starting MJW Clock with Auto-Sync functionality")
        print(f"Running hours: {startHour}:00 to {endHour-1}:{endMinute}")
        print(f"Auto-sync will check every {syncInterval//60} minutes")
        
        while True:
            hourStamp = int(time.strftime('%H'))
            minuteStamp = int(time.strftime('%M'))

            if startHour<=hourStamp<endHour:  #Running Mode
                if not (hourStamp == endHour - 1 and minuteStamp > endMinute):
                    running = True
                    GPIO.output(enaMin, GPIO.LOW) #Enable min motor
                    GPIO.output(enaHr, GPIO.LOW) #Enable hr motor
                    
                    # Perform auto-sync check
                    autoSyncClock()
                    
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
        print("\nShutting down clock...")
        GPIO.output(enaMin, GPIO.HIGH)
        GPIO.output(enaHr, GPIO.HIGH)
        GPIO.cleanup()
        print("GPIO cleanup complete")
        
if __name__ == "__main__":
    print("MJW Clock Control System")
    print("1. Normal startup (use existing clock position)")
    print("2. Reset clock to current computer time")
    
    try:
        choice = input("Select option (1 or 2, default 1): ").strip()
        if choice == "2":
            resetClockToCurrentTime()
        else:
            print("Using existing clock position")
    except:
        print("Using default option 1")
    
    main()

