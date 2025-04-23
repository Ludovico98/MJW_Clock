import RPi.GPIO as GPIO
from time import sleep
import sys

# GPIO Pin Definitions
stepMin = 31      # Step pin for minute hand motor
dirMin = 33       # Direction pin for minute hand motor
stepHour = 15     # Step pin for hour hand motor
dirHour = 13      # Direction pin for hour hand motor
switchMin = 32    # Switch for minute hand home position
switchHour = 12   # Switch for hour hand home position

# Timing constants
delayMotorFast = 0.001  # Fast movement delay (1ms)
minBounce = 50000      # Debounce time for minute switch in microseconds
hourBounce = 50000     # Debounce time for hour switch in microseconds

def setup():
    # Initialize GPIO
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    
    # Set up output pins
    GPIO.setup(stepMin, GPIO.OUT)
    GPIO.setup(dirMin, GPIO.OUT)
    GPIO.setup(stepHour, GPIO.OUT)
    GPIO.setup(dirHour, GPIO.OUT)
    
    # Set up input pins with pull-down resistors
    GPIO.setup(switchMin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(switchHour, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    
    # Initialize motor directions
    GPIO.output(dirMin, GPIO.HIGH)  # Set minute direction
    GPIO.output(dirHour, GPIO.HIGH) # Set hour direction

def minuteFast():
    """Move minute hand one step at fast speed"""
    GPIO.output(stepMin, GPIO.HIGH)
    sleep(delayMotorFast)
    GPIO.output(stepMin, GPIO.LOW)
    sleep(delayMotorFast)

def hourFast():
    """Move hour hand one step at fast speed"""
    GPIO.output(stepHour, GPIO.HIGH)
    sleep(delayMotorFast)
    GPIO.output(stepHour, GPIO.LOW)
    sleep(delayMotorFast)

def minSearch():
    """Find minute hand home position"""
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
    
    # Add small delay to account for switch bounce
    sleep(minBounce / 1000000.0)
    print("✓ Minute hand home position found!")

def hourSearch():
    """Find hour hand home position"""
    print("Finding hour hand home position...")
    
    # If switch is already activated, move until it's not
    if GPIO.input(switchHour) == GPIO.HIGH:
        print("- Switch already activated, moving until deactivated")
        while GPIO.input(switchHour) == GPIO.HIGH:
            hourFast()
    
    # Now move until switch is activated again
    print("- Moving until switch activates")
    while GPIO.input(switchHour) == GPIO.LOW:
        hourFast()
    
    # Add small delay to account for switch bounce
    sleep(hourBounce / 1000000.0)
    print("✓ Hour hand home position found!")

def calibrate():
    """Calibrate both clock hands"""
    try:
        print("Starting clock hands calibration...")
        minSearch()
        hourSearch()
        print("Calibration complete! Both hands are now at home positions.")
    except KeyboardInterrupt:
        print("\nCalibration interrupted by user")
    except Exception as e:
        print(f"Error during calibration: {str(e)}")
    finally:
        GPIO.cleanup()
        print("GPIO pins cleaned up")

if __name__ == "__main__":
    setup()
    calibrate()