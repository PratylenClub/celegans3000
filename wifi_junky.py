import time
import robot_manager.robot as robot
import sensors_manager.wifi_manager as wifi_manager
import random
LEFT_TRIM   = 0
RIGHT_TRIM  = 0

MAX_ANGULAR_SPEED = 255
MIN_ANGULAR_SPEED = 0
MAX_LINEAR_SPEED = 255
MIN_LINEAR_SPEED = 0

MOVEMENT_TIME = 1

def random_movement(self):
	angular_speed = random.randint(-MAX_ANGULAR_SPEED-1,MAX_ANGULAR_SPEED)
	angular_time = MOVEMENT_TIME
	linear_speed = random.randint(-MAX_ANGULAR_SPEED-1,MAX_ANGULAR_SPEED)
	linear_time = MOVEMENT_TIME	
	return angular_speed, angular_time, linear_speed, linear_time

def reverse_movement(self, angular_speed, angular_time, linear_speed, linear_time):
	return -1*angular_speed, angular_time, -1* linear_speed, linear_time

def execute_movement(self, robot, angular_speed, angular_time, linear_speed, linear_time):
	if angular_speed < 0:
		robot.left(-1*angular_speed, angular_time)
	else:
		robot.write(angular_speed, angular_time)
	if linear_speed < 0:
		robot.backward(-1*linear_speed, linear_time)
	else:
		robot.forward(linear_speed, linear_time)


def search_wifi(self, robot, nb_iterations=20):
	for i in xrange(nb_iterations):
		previous_wifi_signal = wifi_manager.get_wifi_quality()
		random_step = random_movement()
		execute_movement(robot, *random_step)
		new_wifi_signal = wifi_manager.get_wifi_quality()
		if new_wifi_signal < previous_wifi_signal:
			reverse_random_step = reverse_movement(*random_step)
			execute_movement(robot, *reverse_random_step)



robot = Robot.Robot(left_trim=LEFT_TRIM, right_trim=RIGHT_TRIM)
search_wifi(robot)	