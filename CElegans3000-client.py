#!/usr/bin/env python

import socket
import time
import pickle
import robot_manager.robot as Robot
import sensors_manager.wifi_manager as wifi_manager
import sensors_manager.ultra_sound as ultra_sound
LEFT_TRIM   = 0
RIGHT_TRIM  = 0
TCP_IP = '192.168.43.156'
TCP_PORT = 5005
BUFFER_SIZE = 1024
END_TASK_SIGNAL = "END_TASK"
NB_TRIALS_ULTRASOUND = 4
DELTA_TIME_ULTRASOUND = 0.1
def print_me(*a):
	print a

class Body:
	def __init__(self,tcp_id=TCP_IP,tcp_port=TCP_PORT):
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.connect((tcp_id, tcp_port))
		#self.motor_actions = {'MOTOR_RIGHT':print_me, 'MOTOR_LEFT':print_me}
		self.motor_actions = {'MOTOR_RIGHT':self.run_right_motor, 'MOTOR_LEFT':self.run_left_motor, 'MOTORS':self.run_motors}
		self.body = Robot.Robot(left_trim=LEFT_TRIM, right_trim=RIGHT_TRIM)

	def run_right_motor(self,weight,signal):
		angular_speed = signal*weight*20
		if angular_speed>200: angular_speed = 200
		if angular_speed<80: angular_speed = 80
		angular_time=0.5
		self.body.only_right(int(angular_speed), angular_time)

	def run_left_motor(self,weight,signal):
		angular_speed = signal*weight*20
		if angular_speed>200: angular_speed = 200
		if angular_speed<80: angular_speed = 80
		angular_time=0.5
		self.body.only_left(int(angular_speed), angular_time)

	def run_motors(self,weight_right,weight_left):
		print "RUN MOTORS",weight_right,weight_left
		angular_time=3
		angular_speed_right = weight_right
		angular_speed_left = weight_left
		if angular_speed_left>250: angular_speed_left = 250
		if angular_speed_left<10: angular_speed_left = 10
		if angular_speed_right>250: angular_speed_right = 250
		if angular_speed_right<10: angular_speed_right = 10
		self.body.run_motors_forward(angular_speed_right, angular_speed_left,angular_time)

	def get_sensory_signals(self):
		#wifi_signal = wifi_manager.get_wifi_quality()
		ultra_sound_signal = ultra_sound.return_distance_to_obstacle(NB_TRIALS_ULTRASOUND ,DELTA_TIME_ULTRASOUND )
		print "ULTRA SOUND",ultra_sound_signal
		return {"ULTRA_SOUND":ultra_sound_signal}

	def run(self):
		while 1:
			#time.sleep(0.5)
			sensorial_signal = self.get_sensory_signals()
			sensorial_signal_pickle = pickle.dumps(sensorial_signal,-1)
			print "sending: ", sensorial_signal
			self.socket.send(sensorial_signal_pickle)
			while 1:
				order_pickle = self.socket.recv(BUFFER_SIZE)
				order = pickle.loads(order_pickle)
				print "receving: ",order
				if END_TASK_SIGNAL == order[0]:
					break
				self.motor_actions[order[0]](*order[1])
			die = order[1]
			print die
			if die[0]:
				self.socket.close()
				break
b = Body()
b.run()