import pandas as pd
import pickle as p
import numpy as np
INPUT_INDEX = 0
OUTPUT_INDEX = 1
INITIAL_CELL_STATE = 0

def connectome_data_to_NN_model(connectome_file,
								muscles_file, 
								sensor_file, 
								neurotransmitters_pickle, 
								muscle_2_motor_pickle, 
								sensory_cells_2_sensors_pickle,
								model_file):
	connectome = pd.read_csv(connectome_file,index_col=0).fillna("nan")
	muscles = pd.read_csv(muscles_file,index_col=0).fillna("nan")
	sensor = pd.read_csv(sensor_file,index_col=0).fillna("nan")

	neurotransmitters = p.load(open(neurotransmitters_pickle,"rb"))
	muscle_2_motor = p.load(open(muscle_2_motor_pickle,"rb"))
	sensory_cells_2_sensors = p.load(open(sensory_cells_2_sensors_pickle,"rb"))

	muscle_neurotransmitter_values = np.asarray(map(neurotransmitters.get,muscles["Neurotransmitter"]))
	muscles["Weight"] = muscle_neurotransmitter_values * muscles["Number of Connections"]
	muscles.iloc[:,OUTPUT_INDEX] = np.asarray(map(muscle_2_motor.get,muscles.iloc[:,OUTPUT_INDEX]))

	sensory_neurotransmitter_values = np.asarray(map(neurotransmitters.get,connectome["Neurotransmitter"]))
	connectome["Weight"] = sensory_neurotransmitter_values * connectome["Number of Connections"]
	sensor.iloc[:,INPUT_INDEX] = np.asarray(map(sensory_cells_2_sensors.get,sensor.iloc[:,INPUT_INDEX]))


	Neural_Network = {}
	Cells_state = {}
	for neuron in set(connectome.iloc[:,INPUT_INDEX]).union(set(connectome.iloc[:,OUTPUT_INDEX])):
		Neural_Network[neuron] = {}
		Cells_state[neuron] = INITIAL_CELL_STATE 
	for cell in set(muscles.iloc[:,INPUT_INDEX]).union(set(muscles.iloc[:,OUTPUT_INDEX])):
		Neural_Network[cell] = {}
		Cells_state[cell] = INITIAL_CELL_STATE 
	for cell in set(sensor.iloc[:,INPUT_INDEX]).union(set(sensor.iloc[:,OUTPUT_INDEX])):
		Neural_Network[cell] = {}
		Cells_state[cell] = INITIAL_CELL_STATE 

	for i in xrange(connectome.index.size):
		Neural_Network[connectome.iloc[i,INPUT_INDEX]][connectome.iloc[i,OUTPUT_INDEX]] = connectome.iloc[i,:]["Weight"]
	for i in xrange(muscles.index.size):
		Neural_Network[muscles.iloc[i,INPUT_INDEX]][muscles.iloc[i,OUTPUT_INDEX]] = muscles.iloc[i,:]["Weight"]
	for i in xrange(sensor.index.size):
		Neural_Network[sensor.iloc[i,INPUT_INDEX]][sensor.iloc[i,OUTPUT_INDEX]] = sensor.iloc[i,:]["Weight"]
	p.dump({"Neural Network":Neural_Network, "Cells_state":Cells_state},open(model_file,"wb"))

connectome_file = "data/connectome_clean_data/Connectome.csv"
muscles_file = "data/connectome_clean_data/Neurons_to_Muscles.csv"
sensor_file = "data/connectome_clean_data/Sensory.csv"
neurotransmitters_pickle = "data/connectome_clean_data/Neurotransmiters_2_coefficient.pickle"
muscle_2_motor_pickle = "data/connectome_clean_data/muscle_2_motor.pickle"
sensory_cells_2_sensors_pickle = "data/connectome_clean_data/sensory_2_sensors.pickle"
model_file = "models/celegans3000.pickle"
connectome_data_to_NN_model(connectome_file,muscles_file,sensor_file,neurotransmitters_pickle,muscle_2_motor_pickle,sensory_cells_2_sensors_pickle,model_file)

