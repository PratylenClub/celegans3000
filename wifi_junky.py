import time
import robot_manager.robot as Robot
import sensors_manager.wifi_manager as wifi_manager
import random
LEFT_TRIM   = 0
RIGHT_TRIM  = 0

MAX_ANGULAR_SPEED = 100
MIN_ANGULAR_SPEED = 50
MAX_LINEAR_SPEED = 200
MIN_LINEAR_SPEED = 100

MOVEMENT_TIME = 3

def random_movement():
	if random.random() < 0.5:
		angular_speed = random.randint(-MAX_ANGULAR_SPEED-1,MAX_ANGULAR_SPEED)
		angular_time = MOVEMENT_TIME
		linear_speed = random.randint(-MAX_LINEAR_SPEED-1,MAX_LINEAR_SPEED)
		linear_time = MOVEMENT_TIME	
	else:
		angular_speed = 0
                angular_time = MOVEMENT_TIME
                linear_speed = random.randint(-MAX_LINEAR_SPEED-1,MAX_LINEAR_SPEED)
                linear_time = MOVEMENT_TIME
	return angular_speed, angular_time, linear_speed, linear_time

def execute_reverse_movement(robot, angular_speed, angular_time, linear_speed, linear_time):
        print "entering reverse move"
	linear_speed *= -1
	angular_speed *= -1
	if linear_speed < 0:
                robot.backward(-1*linear_speed, linear_time)
        else:
                robot.forward(linear_speed, linear_time)
	if angular_speed < 0:
                robot.left(-1*angular_speed, angular_time)
        else:
                robot.right(angular_speed, angular_time)

def execute_movement(robot, angular_speed, angular_time, linear_speed, linear_time):
        print angular_speed, angular_time, linear_speed, linear_time
	if angular_speed < 0:
		robot.left(-1*angular_speed, angular_time)
	else:
		robot.right(angular_speed, angular_time)
	if linear_speed < 0:
		robot.backward(-1*linear_speed, linear_time)
	else:
		robot.forward(linear_speed, linear_time)


def search_wifi(robot, nb_iterations=20):
	for i in xrange(nb_iterations):
                print "_____"
                previous_wifi_signal = wifi_manager.get_wifi_quality()
                print previous_wifi_signal
		random_step = random_movement()
		execute_movement(robot, *random_step)
		new_wifi_signal = wifi_manager.get_wifi_quality()
                print new_wifi_signal
		if new_wifi_signal < previous_wifi_signal:
			execute_reverse_movement(robot, *random_step)
		time.sleep(2)


robot = Robot.Robot(left_trim=LEFT_TRIM, right_trim=RIGHT_TRIM)
search_wifi(robot)	
#robot.right(100,2)
