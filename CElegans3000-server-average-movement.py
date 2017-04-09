import socket
import pickle as p
import time
import random

TCP_IP = '192.168.43.156'
TCP_PORT = 5005
BUFFER_SIZE = 1024

SIGNAL=1.0
CURRENT_STATE = 0
NEXT_STATE = 1
UPDATE = 2
LEFT_TRIM   = 0
RIGHT_TRIM  = 0
TIME_STEP = 0.5
THRESHOLD = 50
BASAL_STATE = 0
MAX_INIT_STATE = 10
DELTA_POLARIZATION = 0.1

class NN:
	def __init__(self,model_file,tcp_ip=TCP_IP,tcp_port=TCP_PORT):
		model = p.load(open(model_file,"rb"))
		self.neural_network = model["Neural Network"]
		self.cell_states = model["Cells_state"]
		self.sens = ["ULTRA_SOUND"]
		self.firing_neurons = []
		#self.body = Robot.Robot(left_trim=LEFT_TRIM, right_trim=RIGHT_TRIM)
		self.brain = {}
		self.build_brain()
		self.initialize_brain()
		self.muscles_values = {"MOTOR_RIGHT":0, "MOTOR_LEFT":0}

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
					self.brain[spiking][receptor] = {"function":touch_nose_sensorial_stimulus,"parameters":{"neuron_receptor":receptor,"weight":weight}}
					#self.brain[spiking][receptor] = {"function":self.sensorial_stimulus,"parameters":{"neuron_receptor":receptor,"weight":weight}}
				elif spiking == "WIFI_SIGNAL":
					self.brain[spiking][receptor] = {"function":self.sensorial_stimulus_food,"parameters":{"neuron_receptor":receptor,"weight":weight}}
				elif spiking == "NO_SIGNAL":
					self.brain[spiking][receptor] = {"function":self.sensorial_stimulus,"parameters":{"neuron_receptor":receptor,"weight":weight}}
				else:
					if receptor == "MOTOR_LEFT":
						self.brain[spiking][receptor] = {"function":self.accumulate_motor,"parameters":{"muscle":receptor,"weight":weight}}
					if receptor == "MOTOR_RIGHT":
						self.brain[spiking][receptor] = {"function":self.accumulate_motor,"parameters":{"muscle":receptor,"weight":weight}}
					if receptor is not None and "MOTOR" not in receptor:
						self.brain[spiking][receptor] = {"function":self.depolarize_neuron,"parameters":{"neuron_receptor":receptor,"weight":weight}}

	def accumulate_motor(self,muscle,weight,signal=SIGNAL):
		self.muscles_values[muscle] += weight * signal

	def initialize_brain(self,max_initial_state=MAX_INIT_STATE):
		for cell in self.cell_states:
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

	def depolarize_neuron(self,neuron_receptor,weight,signal=SIGNAL,threshold = THRESHOLD):	
		self.cell_states[neuron_receptor][NEXT_STATE] = self.cell_states[neuron_receptor][CURRENT_STATE] + weight * signal
		self.cell_states[neuron_receptor][UPDATE] = True
		#print self.cell_states[neuron_receptor][NEXT_STATE]
		if self.cell_states[neuron_receptor][NEXT_STATE] >= THRESHOLD:
			self.firing_neurons.append(neuron_receptor)

	def sensorial_stimulus(self,neuron_receptor,weight,signal=SIGNAL,threshold = THRESHOLD):
		sensorial_signal = signal*weight
		self.cell_states[neuron_receptor][NEXT_STATE] = self.cell_states[neuron_receptor][CURRENT_STATE]+sensorial_signal
		self.cell_states[neuron_receptor][UPDATE] = True
		if self.cell_states[neuron_receptor][NEXT_STATE] >= THRESHOLD:
			self.firing_neurons.append(neuron_receptor)

	def touch_nose_sensorial_stimulus(self,neuron_receptor,weight,signal=SIGNAL,threshold=THRESHOLD):
		if signal < threshold: #closer than 7cm
			self.firing_neurons.append(neuron_receptor)

	def sensorial_stimulus_food(self,neuron_receptor,weight,signal=SIGNAL,threshold=THRESHOLD):
		if self.body.energy < 10:
			self.sensorial_stimulus(neuron_receptor,weight,signal=signal,threshold = threshold)

	def excite_muscles(self,):
		order_pickle = p.dumps(["MOTORS",(self.muscles_values["MOTOR_RIGHT"],self.muscles_values["MOTOR_LEFT"])],-1)
		time.sleep(1.2)
		self.conn.send(order_pickle)
		self.muscles_values = {"MOTOR_RIGHT":0, "MOTOR_LEFT":0}

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
		print self.firing_neurons
		data_pickle = self.conn.recv(BUFFER_SIZE)
		if not data_pickle:
			return 1
		sensory_data = p.loads(data_pickle)
		print "receiving: ", sensory_data
		for sens in sensory_data:
			self.fire_action(sens, signal=sensory_data[sens])
		for neuron in self.firing_neurons:
			self.fire_action(neuron)
			self.reset_neuron(neuron)
		for cell in self.cell_states:
			self.update_cell(cell)
			self.polarize_cell(cell)
		time.sleep(0.3)
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
nn.run(10)



