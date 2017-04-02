import pickle as p
import time
import robot_manager.robot as Robot
import sensors_manager.wifi_manager as wifi_manager
import random
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
	def __init__(self,model_file):
		model = p.load(open(model_file,"rb"))
		self.neural_network = model["Neural Network"]
		self.cell_states = model["Cells_state"]
		self.sens = ["ULTRA_SOUND"]
		self.firing_neurons = []
		self.body = Robot.Robot(left_trim=LEFT_TRIM, right_trim=RIGHT_TRIM)
		self.brain = {}
		self.build_brain()
		self.initialize_brain()

	def build_brain(self):
		self.brain = {}
		for spiking in self.neural_network:
			self.brain[spiking] = {}
			for receptor,weight in self.neural_network[spiking].iteritems():
				if spiking == "ULTRA_SOUND":
					self.brain[spiking][receptor] = {"function":self.sensorial_stimulus,"parameters":{"neuron_receptor":receptor,"weight":weight}}
				else:
					if receptor == "MOTOR_LEFT":
						self.brain[spiking][receptor] = {"function":self.excite_muscle_left,"parameters":{"muscle":receptor,"weight":weight}}
					if receptor == "MOTOR_RIGHT":
						self.brain[spiking][receptor] = {"function":self.excite_muscle_right,"parameters":{"muscle":receptor,"weight":weight}}
					if receptor is not None and "MOTOR" not in receptor:
						self.brain[spiking][receptor] = {"function":self.depolarize_neuron,"parameters":{"neuron_receptor":receptor,"weight":weight}}

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
		sensorial_signal = wifi_manager.get_wifi_quality()*weight+signal
		#sensorial_signal = 70
		self.cell_states[neuron_receptor][NEXT_STATE] = self.cell_states[neuron_receptor][CURRENT_STATE]+sensorial_signal
		self.cell_states[neuron_receptor][UPDATE] = True
		if self.cell_states[neuron_receptor][NEXT_STATE] >= THRESHOLD:
			self.firing_neurons.append(neuron_receptor)

	def excite_muscle_right(self,muscle,weight,signal=SIGNAL):
		angular_speed = weight*signal*10
		if angular_speed > 200: angular_speed = 200
		if angular_speed < 50: angular_speed = 50
		angular_time = TIME_STEP
		#print angular_speed
		self.body.right(int(angular_speed), angular_time)

	def excite_muscle_left(self,muscle,weight,signal=SIGNAL):
		angular_speed = weight*signal*10
		if angular_speed > 200: angular_speed = 200
		if angular_speed < 50: angular_speed = 50
		angular_time = TIME_STEP
		#print angular_speed
		self.body.left(int(angular_speed), angular_time)

	def fire_action(self,neuron_firing):
		for neuron_receptor in self.brain[neuron_firing]:
			synapse = self.brain[neuron_firing][neuron_receptor]
			synapse["function"](**synapse["parameters"])

	def reset_neuron(self, neuron):
		self.cell_states[neuron][CURRENT_STATE] = BASAL_STATE
		self.cell_states[neuron][NEXT_STATE] = BASAL_STATE
		self.cell_states[neuron][UPDATE] = False
		self.firing_neurons.remove(neuron)

	def update_neural_network(self):
		print self.firing_neurons
		for sens in self.sens:
			self.fire_action(sens)
		for neuron in self.firing_neurons:
			self.fire_action(neuron)
			self.reset_neuron(neuron)
		for cell in self.cell_states:
			self.update_cell(cell)
			self.polarize_cell(cell)

	def run(self,nb_steps):
		for t in xrange(nb_steps):
			self.update_neural_network()

nn = NN("connectome_manager/models/celegans3000.pickle")
nn.run(100)



