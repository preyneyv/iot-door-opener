import time

import RPi.GPIO as GPIO
from RpiMotorLib import RpiMotorLib

mode_pins = (22, 23, 24)
dir_pin = 13
stp_pin = 6
slp_pin = 5

motor = RpiMotorLib.A4988Nema(dir_pin, stp_pin, mode_pins, "DRV8825")
GPIO.setup(slp_pin, GPIO.OUT)
GPIO.output(slp_pin, GPIO.LOW)


def wind():
    for _ in range(4):
        GPIO.output(slp_pin, GPIO.HIGH)
        motor.motor_go(False, "Half", 100, .0001, False, .05)
        GPIO.output(slp_pin, GPIO.LOW)
        time.sleep(0.03)


def turn(steps):
    GPIO.output(slp_pin, GPIO.HIGH)
    motor.motor_go(False, "Full", steps, .0002, False, .05)
    time.sleep(4)
    print('1 more second!')
    time.sleep(1)
    motor.motor_go(True, "Full", steps, .0002, False, .05)
    GPIO.output(slp_pin, GPIO.LOW)


if __name__ == "__main__":
    try:
        s = 0
        while True:
            turn(2)
            s += 2
            time.sleep(1)
            print(f"{s} steps!")
            # try:
            #     s = int(input('How many steps?\n> '))
            # except ValueError:
                # print('Invalid number!')
                # continue
            # turn(s)
    finally:
        GPIO.cleanup()
