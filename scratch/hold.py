import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

slp_pin = 5
GPIO.setup(slp_pin, GPIO.OUT)

try:
    last = False
    while True:
        input(f"Currently {'holding' if last else 'not holding'}")
        last = not last
        GPIO.output(slp_pin, last)
finally:
    GPIO.cleanup()
