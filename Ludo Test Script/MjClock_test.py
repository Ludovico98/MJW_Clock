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

stepsPerHr = 1200 #steps per hour
stepsPerMin = 720 #steps per minute

###############################################################################################################
delayMotor = 0.035370 #0.151 * 1.02 = 1/[(0.396rpm * 1000ppr) / 60] change this for speed of both motors
delayMotorFast = 0.001 #fast setting used for set up
deltaMin = delayMotor * 0.02 #2% change every time theres a difference in the time
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
    """Find minute hand home position with proper logic"""
    print("Finding minute hand home position...")
    
    # If switch is already activated, move until it's not
    if GPIO.input(switchMin) == GPIO.HIGH:
        print("- Switch already activated, moving until deactivated")
        while GPIO.input(switchMin) == GPIO.HIGH:
            minuteFast()
    
    # Now move until switch is activated again
    print("- Moving until switch activates")
    while GPIO.input(switchMin) == GPIO.LOW:
        minuteFast()
    
    # Add small delay to account for bounce
    sleep(minBounce / 1000000.0)
    print("✓ Minute hand home position found!")

def hrSearch():
    """Find hour hand home position with proper logic"""
    print("Finding hour hand home position...")
    
    # If switch is already activated, move until it's not
    if GPIO.input(switchHr) == GPIO.HIGH:
        print("- Switch already activated, moving until deactivated")
        while GPIO.input(switchHr) == GPIO.HIGH:
            hourFast()
    
    # Now move until switch is activated again
    print("- Moving until switch activates")
    while GPIO.input(switchHr) == GPIO.LOW:
        hourFast()
    
    # Add small delay to account for bounce
    sleep(hrBounce / 1000000.0)
    print("✓ Hour hand home position found!")

def SetClockTo1200():
    minSearch()
    hrSearch()
    print("Clock set to start time 12:00")

def SetClockToCurrentTime():
    """Set clock hands to current computer time"""
    current_time = time.localtime()
    current_hour = current_time.tm_hour % 12
    if current_hour == 0:
        current_hour = 12
    current_minute = current_time.tm_min
    print(f"Setting clock to current time: {current_hour}:{current_minute:02d}")

    # Move to home positions first
    minSearch()
    hrSearch()

    # Move minute hand to current minute
    print(f"Moving minute hand to {current_minute} minutes")
    for _ in range(current_minute * 12):  # Assuming 12 steps per minute
        minuteFast()

    # Move hour hand to current hour position
    hour_steps = (current_hour * hrRatio) + (current_minute * hrRatio // 60)
    print(f"Moving hour hand to position {current_hour} ({hour_steps} steps)")
    for _ in range(hour_steps):
        hourFast()
    
    print("Clock set to current time")

def advance_minute():
    """Advance minute hand by one minute using proper step calculation"""
    steps_per_minute = minRatio // 60  # Calculate steps needed per minute
    for _ in range(steps_per_minute):
        minute_step()

def advance_hour_fraction():
    """Advance hour hand by a fractional amount for smooth movement"""
    steps_per_minute_fraction = hrRatio // 60  # Steps per minute for hour hand
    for _ in range(steps_per_minute_fraction):
        hour_step()
    
    # Add occasional extra step to account for rounding
    if time.time() % 3 < 1:  # Improved randomization
        hour_step()

def verify_clock_position():
    """Verify and correct clock position if needed"""
    print("Verifying clock position...")

    # Get current time
    current_time = time.localtime()
    current_hour = current_time.tm_hour % 12
    if current_hour == 0:
        current_hour = 12
    current_minute = current_time.tm_min

    print(f"Target time: {current_hour}:{current_minute:02d}")

    # Move to home positions
    minSearch()
    hrSearch()

    # Reposition minute hand
    minute_steps = current_minute * 12
    print(f"Repositioning minute hand to: {current_minute} minutes ({minute_steps} steps)")
    for _ in range(minute_steps):
        minuteFast()

    # Reposition hour hand
    hour_steps = (current_hour * hrRatio) + (current_minute * hrRatio // 60)
    print(f"Repositioning hour hand to: {current_hour} hours ({hour_steps} steps)")
    for _ in range(hour_steps):
        hourFast()
    
    print("Clock position verified and corrected")



###### Motor Control Functions #######
def minute_step():
    """Single step for minute hand at normal speed"""
    GPIO.output(stepMin, GPIO.HIGH)
    sleep(delayMotor)
    GPIO.output(stepMin, GPIO.LOW)
    sleep(delayMotor)

def hour_step():
    """Single step for hour hand at normal speed"""
    GPIO.output(stepHr, GPIO.HIGH)
    sleep(delayMotor)
    GPIO.output(stepHr, GPIO.LOW)
    sleep(delayMotor)
###### End Motor Control Functions #######

    
def run_clock():
    """Main clock running loop with proper time tracking"""
    print("Starting continuous clock operation...")
    last_minute = int(time.strftime("%M"))
    last_hour = int(time.strftime("%H"))

    while True:
        current_time = time.localtime()
        current_minute = current_time.tm_min
        current_hour = current_time.tm_hour

        # Check if minute has changed
        if current_minute != last_minute:
            print(f"Minute changed: {last_minute} -> {current_minute}")
            advance_minute()
            advance_hour_fraction()
            last_minute = current_minute
        
        # Check if hour has changed - verify position every hour
        if current_hour != last_hour:
            print(f"Hour changed: {last_hour} -> {current_hour}")
            verify_clock_position()
            last_hour = current_hour
        
        sleep(1)  # Check every second

def main():
    """Main function to control clock setup and operation"""
    try:
        print("=== MJW Clock Test System ===")
        print("Starting clock setup...")
        
        # Initial setup - move to 12:00 position
        SetClockTo1200()
        input("\nClock is set to 12:00. Press Enter to continue...")
        
        # Set to current time
        SetClockToCurrentTime()
        print("Clock setup complete.")
        
        # Start continuous operation in separate thread
        print("Starting continuous clock operation...")
        clock_thread = threading.Thread(target=run_clock, daemon=True)
        clock_thread.start()

        # Keep main thread alive
        print("Clock is running. Press Ctrl+C to stop.")
        while True:
            sleep(1)
    
    except KeyboardInterrupt:
        print("\n\nPROCESS INTERRUPTED! Cleaning up...")

    finally:
        print("Disabling motors and cleaning up GPIO...")
        GPIO.output(enaMin, GPIO.HIGH)  # Disable minute motor
        GPIO.output(enaHr, GPIO.HIGH)   # Disable hour motor
        GPIO.cleanup()
        print("GPIO cleaned up successfully")
    
if __name__ == "__main__":
    main()


