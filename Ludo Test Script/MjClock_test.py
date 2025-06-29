import RPi.GPIO as GPIO
import time
from time import sleep
import threading

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

setpPerHr = 1200 #steps per hour
setpPerMin = 720 #steps per minute

###############################################################################################################
delayMotor = 0.035370 #0.151 * 1.02 = 1/[(0.396rpm * 1000ppr) / 60] change this for speed of both motors
delayMotorFast = 0.001 #fast setting used for set up
deltaMin = delayMotor * 0.00 #2% change every time theres a difference in the time
hrBounce = 200000 #200000 = delay time to stop switch activating
minBounce = 36000 #12000 = delay time to stop switch activating
minRatio = 1238 # 12 hours including 0, change this to configure the ratio between disc
hrRatio = 100 #Ratio multiplier
###############################################################################################################


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

def minSearch():
    if GPIO.input(switchMin) == GPIO.HIGH:
        while GPIO.input(switchMin) == GPIO.HIGH:
            minuteFast() #moving the minute hand to the home position
    else:
        for _ in range(50):
            minuteFast()
        while GPIO.input(switchMin) == GPIO.HIGH:
            minuteFast()
        print("Minute hand found home position")

def hrSearch():
    if GPIO.input(switchHr) == GPIO.HIGH:
        while GPIO.input(switchHr) == GPIO.HIGH:
            hourFast()
        print("Hour hand found home position")
    else:
        for _ in range(50):
            hourFast()
        while GPIO.input(switchHr) == GPIO.HIGH:
            hourFast()
        print("Hour hand found home position")

def SetClockTo1200():
    minSearch()
    hrSearch()
    print("Clock set to start time 12:00")

def SetClockToCurrentTime():
    current_time = time.localtime()
    current_hour = current_time.tm_hour % 12
    if current_hour == 0:
        current_hour = 12
    current_minute = current_time.tm_min
    print(f"Setting clock to current time: {current_hour}:{current_minute:02d}")

    minSearch()
    hrSearch()

    minute_steps = current_minute * 12
    print(f"Moving minute hand to {current_minute} ({minute_steps} steps)")
    for _ in range(current_minute):
        minuteFast()

    hour_steps = (current_hour * 100) + (current_minute * 100 // 60)
    print(f"Moving hour hand to position {current_hour} ({hour_steps} steps)")
    for _ in range(hour_steps):
        hourFast()
    hourFast()
    print("Clock set to current time")

def advance_minute():
    for x in range(12):
        minuteFast()

def advance_hour_fraction():
    for x in range(100 // 60):
        hourFast()

    if time.time() % 3 < 2:
        hourFast()
 
def verify_clock_position():
    print("Verifying clock position...")

    #store time
    current_time = time.localtime()
    current_hour = current_time.tm_hour % 12
    if current_hour == 0:
        current_hour = 12
    current_minute = current_time.tm_min

    minSearch()
    hrSearch()

    minute_steps = current_minute * 12
    print(f"Reposition minute hand to: {current_minute} minutes ({minute_steps} steps)")
    for _ in range(minute_steps):
        minuteFast()

    hour_steps = (current_hour * 100) + (current_minute * 100 // 60)
    print(f"Reposition hour hand to: {current_hour} hours ({hour_steps} steps)")
    for _ in range(hour_steps):
        hourFast()
    
    print("Clock position verified")



###### added code #######
def minute_step():
    GPIO.output(stepMin, GPIO.HIGH)
    sleep(delayMotor)
    GPIO.output(stepMin, GPIO.LOW)
    sleep(delayMotor)

def hour_step():
    GPIO.output(stepHr, GPIO.HIGH)
    sleep(delayMotor)
    GPIO.output(stepHr, GPIO.LOW)
    sleep(delayMotor)

def advance_minute():
    for _ in range(minRatio // 100):  # Using minRatio to determine steps per minute
        minuteFast()

def advance_hour_fraction():
    for _ in range(hrRatio // 60):  # Using hrRatio for hour movement
        hourFast()
    
    # Add occasional extra step to account for rounding
    if time.time() % 3 < 2:
        hourFast()
###### added code #######

    
def run_clock():
    #keep clock running
    last_minute = int(time.strftime("%M"))
    last_hour = int(time.strftime("%H"))

    while True:
        current_time = time.localtime()
        current_minute = current_time.tm_min
        current_hour = current_time.tm_hour

        if current_time != last_minute and current_hour != last_hour:
            advance_minute()
            advance_hour_fraction()
            last_minute = current_minute
        
        if current_hour != last_hour:
            verify_clock_position()
            last_hour = current_hour
        
        sleep(1)  # Sleep for a second to avoid busy waiting

def minSearch():
    # Use bouncetime concept from the variables
    if GPIO.input(switchMin) == GPIO.HIGH:
        print("Finding minute hand home position...")
        while GPIO.input(switchMin) == GPIO.HIGH:
            minuteFast()
        # Add small delay to account for bounce
        sleep(minBounce / 1000000.0)
        print("Minute hand found home position")

def hrSearch():
    if GPIO.input(switchHr) == GPIO.HIGH:
        print("Finding hour hand home position...")
        while GPIO.input(switchHr) == GPIO.HIGH:
            hourFast()
        # Add small delay to account for bounce
        sleep(hrBounce / 1000000.0)
        print("Hour hand found home position")

def main():
    try:
        print("Starting clock setup...")
        SetClockTo1200()
        input("\nClock is set to 12:00. Press Enter to continue...")
        SetClockToCurrentTime()
        print("Clock setup complete.")
        clock_thread = threading.Thread(target=run_clock)
        clock_thread.start()

        while True:
            sleep(1)
    
    except KeyboardInterrupt:
        print("\n\nPROCESS INTERRUPTED!!!! Cleaning up...")

    finally:
        GPIO.output(enaMin, GPIO.HIGH)
        GPIO.output(enaHr, GPIO.HIGH)
        GPIO.cleanup()
        print("GPIO cleaned up")
    
if __name__ == "__main__":
    main()


