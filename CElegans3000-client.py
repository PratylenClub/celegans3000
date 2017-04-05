#!/usr/bin/env python

import socket
import time
import pickle
import robot_manager.robot as Robot
import sensors_manager.wifi_manager as wifi_manager
LEFT_TRIM   = 0
RIGHT_TRIM  = 0
TCP_IP = '192.168.43.156'
TCP_PORT = 5005
BUFFER_SIZE = 1024
END_TASK_SIGNAL = "END_TASK"

def print_me(*a):
	print a

class Body:
	def __init__(self,tcp_id=TCP_IP,tcp_port=TCP_PORT):
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.connect((tcp_id, tcp_port))
		#self.motor_actions = {'MOTOR_RIGHT':print_me, 'MOTOR_LEFT':print_me}
		self.motor_actions = {'MOTOR_RIGHT':self.run_right_motor, 'MOTOR_LEFT':self.run_left_motor}
		self.body = Robot.Robot(left_trim=LEFT_TRIM, right_trim=RIGHT_TRIM)

	def run_right_motor(self,weight,signal):
		angular_time = signal*weight*20
		if angular_speed>200: angular_speed = 200
		if angular_speed<80: angular_speed = 80
		angular_time=0.5
		self.body.right(int(angular_speed), angular_time)

	def run_left_motor(self,weight,signal):
		angular_speed = signal*weight*20
		if angular_speed>200: angular_speed = 200
		if angular_speed<80: angular_speed = 80
		angular_time=0.5
		self.body.left(int(angular_speed), angular_time)

	def get_sensory_signals(self):
		wifi_signal = wifi_manager.get_wifi_quality()
		return {"ULTRA_SOUND":wifi_signal}

	def run(self):
		while 1:
			time.sleep(1)
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