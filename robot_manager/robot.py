# Simple two DC motor robot class.  Exposes a simple LOGO turtle-like API for
# moving a robot forward, backward, and turning.  See RobotTest.py for an
# example of using this class.
# Author: Tony DiCola
# License: MIT License https://opensource.org/licenses/MIT
import time
import atexit

from Adafruit_MotorHAT import Adafruit_MotorHAT


class Robot(object):
    def __init__(self, addr=0x60, left_id=1, right_id=2, left_trim=0, right_trim=0,
                 stop_at_exit=True):
        """Create an instance of the robot.  Can specify the following optional
        parameters:
         - addr: The I2C address of the motor HAT, default is 0x60.
         - left_id: The ID of the left motor, default is 1.
         - right_id: The ID of the right motor, default is 2.
         - left_trim: Amount to offset the speed of the left motor, can be positive
                      or negative and use useful for matching the speed of both
                      motors.  Default is 0.
         - right_trim: Amount to offset the speed of the right motor (see above).
         - stop_at_exit: Boolean to indicate if the motors should stop on program
                         exit.  Default is True (highly recommended to keep this
                         value to prevent damage to the bot on program crash!).
        """
        # Initialize motor HAT and left, right motor.
        self._mh = Adafruit_MotorHAT(addr)
        self._left = self._mh.getMotor(left_id)
        self._right = self._mh.getMotor(right_id)
        self._left_trim = left_trim
        self._right_trim = right_trim
        # Start with motors turned off.
        self._left.run(Adafruit_MotorHAT.RELEASE)
        self._right.run(Adafruit_MotorHAT.RELEASE)
        # Configure all motors to stop at program exit if desired.
        if stop_at_exit:
            atexit.register(self.stop)

    def _left_speed(self, speed):
        """Set the speed of the left motor, taking into account its trim offset.
        """
        speed = max(self._left_trim, min(255, self._left_trim+abs(speed)))  # Constrain speed to 0-255 after trimming.
        self._left.setSpeed(speed)

    def _right_speed(self, speed):
        """Set the speed of the right motor, taking into account its trim offset.
        """
        speed = max(self._right_trim, min(255, self._right_trim+abs(speed)))  # Constrain speed to 0-255 after trimming.
        self._right.setSpeed(speed)

    def stop(self):
        """Stop all movement."""
        self._left.run(Adafruit_MotorHAT.RELEASE)
        self._right.run(Adafruit_MotorHAT.RELEASE)

    def forward(self, speed, seconds=None):
        """Move forward at the specified speed (0-255).  Will start moving
        forward and return unless a seconds value is specified, in which
        case the robot will move forward for that amount of time and then stop.
        """
        # Set motor speed and move both forward.
        self._left_speed(speed)
        self._right_speed(speed)
        self._left.run(Adafruit_MotorHAT.FORWARD)
        self._right.run(Adafruit_MotorHAT.FORWARD)
        # If an amount of time is specified, move for that time and then stop.
        if seconds is not None:
            time.sleep(seconds)
            self.stop()

    def backward(self, speed, seconds=None):
        """Move backward at the specified speed (0-255).  Will start moving
        backward and return unless a seconds value is specified, in which
        case the robot will move backward for that amount of time and then stop.
        """
        # Set motor speed and move both backward.
        self._left_speed(speed)
        self._right_speed(speed)
        self._left.run(Adafruit_MotorHAT.BACKWARD)
        self._right.run(Adafruit_MotorHAT.BACKWARD)
        # If an amount of time is specified, move for that time and then stop.
        if seconds is not None:
            time.sleep(seconds)
            self.stop()

    def right(self, speed, seconds=None):
        """Spin to the right at the specified speed.  Will start spinning and
        return unless a seconds value is specified, in which case the robot will
        spin for that amount of time and then stop.
        """
        # Set motor speed and move both forward.
        self._left_speed(speed)
        self._right_speed(speed)
        self._left.run(Adafruit_MotorHAT.FORWARD)
        self._right.run(Adafruit_MotorHAT.BACKWARD)
        # If an amount of time is specified, move for that time and then stop.
        if seconds is not None:
            time.sleep(seconds)
            self.stop()

    def only_right(self, speed, seconds=None):
        """Spin only right motor at the specified speed.  Will start spinning and
        return unless a seconds value is specified, in which case the robot will
        spin for that amount of time and then stop.
        """
        # Set motor speed and move both forward.
        self._right_speed(abs(speed))
        if speed < 0:
            self._right.run(Adafruit_MotorHAT.BACKWARD)
        else:
            self._right.run(Adafruit_MotorHAT.FORWARD)
        # If an amount of time is specified, move for that time and then stop.
        if seconds is not None:
            time.sleep(seconds)
            self.stop()

    def run_motors_forward(self,speed_right,speed_left,seconds=None):
        self._right_speed(speed_right)
        self._right.run(Adafruit_MotorHAT.FORWARD)
        self._left_speed(speed_left)
        self._left.run(Adafruit_MotorHAT.FORWARD)
        if seconds is not None:
            time.sleep(seconds)
            self.stop()


    def left(self, speed, seconds=None):
        """Spin to the left at the specified speed.  Will start spinning and
        return unless a seconds value is specified, in which case the robot will
        spin for that amount of time and then stop.
        """
        # Set motor speed and move both forward.
        self._left_speed(speed)
        self._right_speed(speed)
        self._left.run(Adafruit_MotorHAT.BACKWARD)
        self._right.run(Adafruit_MotorHAT.FORWARD)
        # If an amount of time is specified, move for that time and then stop.
        if seconds is not None:
            time.sleep(seconds)
            self.stop()

    def only_left(self, speed, seconds=None):
        """Spin only left motor at the specified speed.  Will start spinning and
        return unless a seconds value is specified, in which case the robot will
        spin for that amount of time and then stop.
        """
        # Set motor speed and move both forward.
        self._left_speed(abs(speed))
        if speed < 0:
            self._left.run(Adafruit_MotorHAT.BACKWARD)
        else: 
           self._left.run(Adafruit_MotorHAT.FORWARD)
        # If an amount of time is specified, move for that time and then stop.
        if seconds is not None:
            time.sleep(seconds)
            self.stop()