import socket
import pickle as p
import time
import random
from parameters.params import *

class NN:
	def __init__(self,model_file,tcp_ip=TCP_IP,tcp_port=TCP_PORT,synchronous=True):
		model = p.load(open(model_file,"rb"))
		self.neural_network = model["Neural Network"]
		self.cell_states = model["Cells_state"]
		self.sens = ["ULTRA_SOUND","WIFI_SIGNAL"]
		self.firing_neurons = []
		self.brain = {}
		self.muscles_values = {"MOTOR_RIGHT":0, "MOTOR_LEFT":0}
		self.synchronous = synchronous
		self.build_brain()
		self.initialize_brain()

		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.bind((tcp_ip,tcp_port))
		self.socket.listen(1)
		self.conn, self.addr = self.socket.accept()
		print 'Connection address:', self.addr

	def build_brain(self):
		self.brain = {}
		for spiking in self.neural_network:
			self.brain[spiking] = {}
			for receptor,weight in self.neural_network[spiking].iteritems():
				if spiking == "ULTRA_SOUND":
					self.brain[spiking][receptor] = {"function":self.touch_nose_sensorial_stimulus,"parameters":{"neuron_receptor":receptor,"weight":weight}}
					#self.brain[spiking][receptor] = {"function":self.sensorial_stimulus,"parameters":{"neuron_receptor":receptor,"weight":weight}}
				elif spiking == "WIFI_SIGNAL":
					self.brain[spiking][receptor] = {"function":self.sensorial_stimulus_food,"parameters":{"neuron_receptor":receptor,"weight":weight}}
				elif spiking == "NO_SIGNAL":
					self.brain[spiking][receptor] = {"function":self.sensorial_stimulus,"parameters":{"neuron_receptor":receptor,"weight":weight}}
				else:
					if self.synchronous:
						if receptor == "MOTOR_LEFT":
							self.brain[spiking][receptor] = {"function":self.accumulate_motor,"parameters":{"muscle":receptor,"weight":weight}}
						if receptor == "MOTOR_RIGHT":
							self.brain[spiking][receptor] = {"function":self.accumulate_motor,"parameters":{"muscle":receptor,"weight":weight}}
						if receptor == "MOTOR_FORWARD":
							self.brain[spiking][receptor] = {"function":self.accumulate_motor,"parameters":{"muscle":receptor,"weight":weight}}
						if receptor == "MOTOR_BACKWARD":
							self.brain[spiking][receptor] = {"function":self.accumulate_motor,"parameters":{"muscle":receptor,"weight":weight}}
					else:
						if receptor == "MOTOR_LEFT":
							self.brain[spiking][receptor] = {"function":self.excite_muscle_left,"parameters":{"muscle":receptor,"weight":weight}}
						if receptor == "MOTOR_RIGHT":
							self.brain[spiking][receptor] = {"function":self.excite_muscle_right,"parameters":{"muscle":receptor,"weight":weight}}
						if receptor == "MOTOR_FORWARD":
							self.brain[spiking][receptor] = {"function":self.excite_muscles_forward,"parameters":{"muscle":receptor,"weight":weight}}
						if receptor == "MOTOR_BACKWARD":
							self.brain[spiking][receptor] = {"function":self.excite_muscles_backward,"parameters":{"muscle":receptor,"weight":weight}}

					if receptor is not None and "MOTOR" not in receptor:
						self.brain[spiking][receptor] = {"function":self.depolarize_neuron,"parameters":{"neuron_receptor":receptor,"weight":weight}}

	def accumulate_motor(self,muscle,weight,signal=STANDARD_SIGNAL_VALUE):
		self.muscles_values[muscle] += weight * signal

	def initialize_brain(self,max_initial_state=MAX_INIT_STATE):
		for cell in self.cell_states.keys():
			self.cell_states[cell] = []
			self.cell_states[cell].append(random.randint(0,max_initial_state)) #initial state chosen randomly 
			self.cell_states[cell].append(0) # next state at zero
			self.cell_states[cell].append(False) # not updated

	def update_cell(self,cell):
		if self.cell_states[cell][UPDATE]:
			self.cell_states[cell][CURRENT_STATE] = self.cell_states[cell][NEXT_STATE]
			self.cell_states[cell][UPDATE] = False

	def polarize_cell(self,cell):
		if self.cell_states[cell][CURRENT_STATE] > 0:
			self.cell_states[cell][CURRENT_STATE] -= DELTA_POLARIZATION
		else:
			self.cell_states[cell][CURRENT_STATE] = 0

	def depolarize_neuron(self,neuron_receptor,weight,signal=STANDARD_SIGNAL_VALUE,threshold = STANDARD_THRESHOLD_VALUE):	
		#print "DEPOL"+neuron_receptor+str(weight*signal), self.cell_states[neuron_receptor]
		self.cell_states[neuron_receptor][NEXT_STATE] = self.cell_states[neuron_receptor][CURRENT_STATE] + weight * signal
		self.cell_states[neuron_receptor][UPDATE] = True
		#print self.cell_states[neuron_receptor][NEXT_STATE]
		if self.cell_states[neuron_receptor][NEXT_STATE] >= threshold and neuron_receptor not in self.firing_neurons:
			self.firing_neurons.append(neuron_receptor)

	def sensorial_stimulus(self,neuron_receptor,weight,signal=STANDARD_SIGNAL_VALUE,threshold = STANDARD_THRESHOLD_VALUE):
		sensorial_signal = signal*weight
		self.cell_states[neuron_receptor][NEXT_STATE] = self.cell_states[neuron_receptor][CURRENT_STATE]+sensorial_signal
		self.cell_states[neuron_receptor][UPDATE] = True
		if self.cell_states[neuron_receptor][NEXT_STATE] >= threshold:
			self.firing_neurons.append(neuron_receptor)

	def touch_nose_sensorial_stimulus(self,neuron_receptor,weight,signal=STANDARD_SIGNAL_VALUE,threshold=STANDARD_THRESHOLD_VALUE):
		if signal < 20: #closer than 20cm
			self.firing_neurons.append(neuron_receptor)

	def sensorial_stimulus_food(self,neuron_receptor,weight,signal=STANDARD_SIGNAL_VALUE,threshold=STANDARD_THRESHOLD_VALUE):
		self.sensorial_stimulus(neuron_receptor,weight,signal=signal,threshold = threshold)

	def excite_muscles(self,):
		if abs(self.muscles_values["MOTOR_RIGHT"] + self.muscles_values["MOTOR_LEFT"]) > 0:
			order_pickle = p.dumps(["MOTORS",(self.muscles_values["MOTOR_RIGHT"],self.muscles_values["MOTOR_LEFT"])],-1)
			time.sleep(TIME_STEP)
			self.conn.send(order_pickle)
			self.muscles_values = {"MOTOR_RIGHT":0, "MOTOR_LEFT":0}

	def excite_muscles_forward(self,muscle,weight,signal=STANDARD_SIGNAL_VALUE):
		order_pickle = p.dumps(["MOTORS",(weight*signal,weight*signal)],-1)
		time.sleep(TIME_STEP)
		self.conn.send(order_pickle)

	def excite_muscles_backward(self,muscle,weight,signal=STANDARD_SIGNAL_VALUE):
		order_pickle = p.dumps(["MOTORS",(-weight*signal,-weight*signal)],-1)
		time.sleep(TIME_STEP)
		self.conn.send(order_pickle)

	def excite_muscle_right(self,muscle,weight,signal=STANDARD_SIGNAL_VALUE):
		order_pickle = p.dumps(["MOTOR_RIGHT",(weight,signal)],-1)
		time.sleep(TIME_STEP)
		self.conn.send(order_pickle)
		#self.body.right(int(angular_speed), angular_time)

	def excite_muscle_left(self,muscle,weight,signal=STANDARD_SIGNAL_VALUE):
		order_pickle = p.dumps(["MOTOR_LEFT",(weight,signal)],-1)
		time.sleep(TIME_STEP)
		self.conn.send(order_pickle)

	def fire_action(self,neuron_firing,**params):
		for neuron_receptor in self.brain[neuron_firing]:
			synapse = self.brain[neuron_firing][neuron_receptor]
			parameters = synapse["parameters"]
			parameters.update(params)
			synapse["function"](**parameters)

	def reset_neuron(self, neuron):
		self.cell_states[neuron][CURRENT_STATE] = BASAL_STATE
		self.cell_states[neuron][NEXT_STATE] = BASAL_STATE
		self.cell_states[neuron][UPDATE] = False
		self.firing_neurons.remove(neuron)

	def update_neural_network(self,kill_user=0):
		data_pickle = self.conn.recv(BUFFER_SIZE)
		if not data_pickle:
			return 1
		sensory_data = p.loads(data_pickle)
		print "receiving: ", sensory_data
		for sens in sensory_data:
			self.fire_action(sens, signal=sensory_data[sens])
		print self.firing_neurons
		for neuron in self.firing_neurons[:]:
			self.fire_action(neuron)
			self.reset_neuron(neuron)
		print self.firing_neurons
		for cell in self.cell_states:
			self.update_cell(cell)
			self.polarize_cell(cell)
		if self.synchronous:
			self.excite_muscles()
		kill_signal = ["END_TASK",(kill_user,)]
		print "sending ", kill_signal
		self.conn.send(p.dumps(kill_signal,-1))
		return 0

	def run(self,nb_steps):
		for t in xrange(nb_steps):
			error = self.update_neural_network(int(t==nb_steps-1))
			if error:
				break
		self.conn.close()

nn = NN("connectome_manager/models/celegans3000.pickle")
nn.run(100)



