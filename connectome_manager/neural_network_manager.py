import pandas as pd
import pickle as p
import numpy as np
INPUT_INDEX = 0
OUTPUT_INDEX = 1
INITIAL_CELL_STATE = []

NEURON_TYPE = "Neuron"
SENSORIAL_INPUT_TYPE = "Sensorial"
SENSORIAL_NEURON_TYPE = "Sensorial_Neuron"
MOTOR_NEURONS_TYPE = "Motor_Neuron"
MUSCLE_TYPE = "Muscle"

def connectome_data_to_NN_model(connectome_file,
								muscles_file, 
								sensor_file, 
								neurotransmitters_pickle=None, 
								muscle_2_motor_pickle=None, 
								sensory_cells_2_sensors_pickle=None,
								model_file="model.pickle"):
	"""
	Receives three datasets describing a connectome and pickle file names containing dictionnaries to build the neural network model
	:param connectome_file: Connectome CSV file with 4 columns: (Origin neuron, Target neuron, Number of connections, Neurotransmitter) 
	:param muscles_file: Connections between neurons and muscles CSV file with 4 columns: (Origin neuron, Target muscule, Number of connections, Neurotransmitter) 
	:param sensor_file: Connections between sensorial information and neurons CSV file with 4 columns: (Origin sensorial function, Target neuron, Weight of the connection, Neurotransmitter) 	
	:param neurotransmitters_pickle: Name of pickle file containing a dictionary with (keys : neurotransmitter type, values: corresponding weight)
	:param muscle_2_motor_pickle: Name of pickle file containing a dictionary with (keys : muscles, values: motor action)
	:param sensory_cells_2_sensors_pickle: Name of pickle file containing a dictionary with (keys : sensorial function, values: robot sensorial information)
	:param model_file: Name of the neural network model pickle file
	type connectome_file: String
	:type muscles_file: String
	:type sensory_file: String
	:type neurotransmitters_pickle: String
	:type muscle_2_motor_pickle: String
	:type sensory_cells_2_sensors_pickle: String
	:type model_file: String
	"""

	connectome = pd.read_csv(connectome_file,index_col=0).fillna("nan")
	muscles = pd.read_csv(muscles_file,index_col=0).fillna("nan")
	sensor = pd.read_csv(sensor_file,index_col=0).fillna("nan")

	
	# Initialize weights
	muscles["Weight"] = 1
	connectome["Weight"] = 1
	# Take neurotransmitter into accound
	if neurotransmitters_pickle is not None:
		neurotransmitters = p.load(open(neurotransmitters_pickle,"rb"))
		if "Neurotransmitter" in muscles.columns:
			muscle_neurotransmitter_values = np.asarray(map(neurotransmitters.get,muscles["Neurotransmitter"]))
			muscles["Weight"] = muscle_neurotransmitter_values
		if "Neurotransmitter" in connectome.columns:
			connectome_neurotransmitter_values = np.asarray(map(neurotransmitters.get,connectome["Neurotransmitter"]))
			connectome["Weight"] = connectome_neurotransmitter_values
	# Take number of connections into account
	if "Number of Connections" in muscles.columns:
		muscles["Weight"] *= muscles["Number of Connections"]
	if "Number of Connections" in connectome.columns:
		connectome["Weight"] *= connectome["Number of Connections"]
	# Convert muscles names to motor actions
	if muscle_2_motor_pickle is not None:
		muscle_2_motor = p.load(open(muscle_2_motor_pickle,"rb"))
		muscles.iloc[:,OUTPUT_INDEX] = np.asarray(map(muscle_2_motor.get,muscles.iloc[:,OUTPUT_INDEX]))
	# Convert sensorial signals to sensors
	if 	sensory_cells_2_sensors_pickle is not None:
		sensory_cells_2_sensors = p.load(open(sensory_cells_2_sensors_pickle,"rb"))
		sensor.iloc[:,INPUT_INDEX] = np.asarray(map(sensory_cells_2_sensors.get,sensor.iloc[:,INPUT_INDEX]))

	Neural_Network = {}
	Cells_state = {}
	Cells_types = {}
	for neuron in set(connectome.iloc[:,INPUT_INDEX]).union(set(connectome.iloc[:,OUTPUT_INDEX])):
		Neural_Network[neuron] = {}
		Cells_state[neuron] = INITIAL_CELL_STATE 
		Cells_types[neuron] = NEURON_TYPE
	for cell in set(muscles.iloc[:,OUTPUT_INDEX]):
		Neural_Network[cell] = {}
		Cells_state[cell] = INITIAL_CELL_STATE 
		Cells_types[cell] = MUSCLE_TYPE
	for cell in set(muscles.iloc[:,INPUT_INDEX]):
		Neural_Network[cell] = {}
		Cells_state[cell] = INITIAL_CELL_STATE 
		Cells_types[cell] = MOTOR_NEURONS_TYPE
	for cell in set(sensor.iloc[:,INPUT_INDEX]):
		Neural_Network[cell] = {}
		Cells_state[cell] = INITIAL_CELL_STATE 
		Cells_types[cell] = SENSORIAL_INPUT_TYPE
	for cell in set(set(sensor.iloc[:,OUTPUT_INDEX])):
		Neural_Network[cell] = {}
		Cells_state[cell] = INITIAL_CELL_STATE 
		Cells_types[cell] = SENSORIAL_NEURON_TYPE 		

	for i in xrange(connectome.index.size):
		Neural_Network[connectome.iloc[i,INPUT_INDEX]][connectome.iloc[i,OUTPUT_INDEX]] = connectome.iloc[i,:]["Weight"]
	for i in xrange(muscles.index.size):
		Neural_Network[muscles.iloc[i,INPUT_INDEX]][muscles.iloc[i,OUTPUT_INDEX]] = muscles.iloc[i,:]["Weight"]
	for i in xrange(sensor.index.size):
		Neural_Network[sensor.iloc[i,INPUT_INDEX]][sensor.iloc[i,OUTPUT_INDEX]] = sensor.iloc[i,:]["Weight"]
	p.dump({"Neural Network":Neural_Network, "Cells_state":Cells_state, "Cells_types":Cells_types} ,open(model_file,"wb"))

if __name__ == "__main__":
	"""
	connectome_file = "data/connectome_clean_data/Connectome.csv"
	muscles_file = "data/connectome_clean_data/Neurons_to_Muscles.csv"
	sensor_file = "data/connectome_clean_data/Sensory.csv"
	neurotransmitters_pickle = "data/connectome_clean_data/Neurotransmiters_2_coefficient.pickle"
	muscle_2_motor_pickle = "data/connectome_clean_data/muscle_2_motor.pickle"
	sensory_cells_2_sensors_pickle = "data/connectome_clean_data/sensory_2_sensors.pickle"
	model_file = "models/celegans3000.pickle"
	connectome_data_to_NN_model(connectome_file,muscles_file,sensor_file,neurotransmitters_pickle,muscle_2_motor_pickle,sensory_cells_2_sensors_pickle,model_file)
	
	connectome_file = "data/connectome_clean_data/Connectome.csv"
	muscles_file = "data/connectome_clean_data/Neurons_to_Muscles.csv"
	sensor_file = "data/connectome_clean_data/Sensory.csv"
	model_file = "models/celegans3000_full.pickle"
	connectome_data_to_NN_model(connectome_file,muscles_file,sensor_file,model_file=model_file)
	"""
	connectome_file = "data/connectome_neuroml/Connectome.csv"
	muscles_file = "data/connectome_neuroml/Neurons_to_Muscles.csv"
	sensor_file = "data/connectome_neuroml/Sensory.csv"
	neurotransmitters_pickle = "data/connectome_neuroml/Neurotransmiters_2_coefficient.pickle"
	muscle_2_motor_pickle = "data/connectome_neuroml/muscle_2_motor.pickle"
	sensory_cells_2_sensors_pickle = "data/connectome_neuroml/sensory_2_sensors.pickle"
	model_file = "models/celegans3000_neuroml.pickle"
	connectome_data_to_NN_model(connectome_file,muscles_file,sensor_file,neurotransmitters_pickle,muscle_2_motor_pickle,sensory_cells_2_sensors_pickle,model_file)
	
	connectome_file = "data/connectome_neuroml/Connectome.csv"
	muscles_file = "data/connectome_neuroml/Neurons_to_Muscles.csv"
	sensor_file = "data/connectome_neuroml/Sensory.csv"
	model_file = "models/celegans3000_full_neuroml.pickle"
	connectome_data_to_NN_model(connectome_file,muscles_file,sensor_file,model_file=model_file)	
