from Cells import LIF_neuron, muscle
import pickle
import pandas as pd
import numpy as np
from parameters.params import *
import socket

MUSCLE_TYPE = "Muscle"
LIST_NEURONS_OUTPUT = "LIST_NEURONS_OUTPUT"
AGGREGATION_FUNCTION = "AGGREGATION_FUNCTION"

class neural_network:
        def __init__(self, dt, model_file, monitoring_memory_size = 1000):
                self.dt = dt
                self.model = self.load_model(model_file)
                self.neural_network = {}
                for neuron_name,neuron_type in self.model["Cells_types"].iteritems():
                        if neuron_type == MUSCLE_TYPE:
                                self.neural_network[neuron_name] = muscle(dt=dt)
                        else:
                                self.neural_network[neuron_name] = LIF_neuron(dt=dt)
                for neuron_name,n in self.model["Neural Network"].iteritems():
                        for neuron_name_2,weight in n.iteritems():
                                self.neural_network[neuron_name].append_neighbor({neuron_name_2:{"Cell":self.neural_network[neuron_name_2],"Weight":weight}})
                self.activity = pd.Series(index = self.neural_network.keys())
                self.nb_neurons_firing = {type_neuron: 0 for type_neuron in np.unique(self.model["Cells_types"].values())}

                self.monitoring_memory_index = 0
                self.monitoring = monitoring_memory_size>0
                self.monitoring_memory_size = monitoring_memory_size
                self.monitoring_memory = np.zeros((self.monitoring_memory_size,len(self.neural_network)))

        def load_model(self, model_file):
                return pickle.load(open(model_file,"rb"))

        def update_neural_network(self):
                for neuron_name in self.neural_network:
                        nb_neurons_firing_local = self.neural_network[neuron_name].update()
                        self.activity[neuron_name] = self.neural_network[neuron_name].Vm
                        self.nb_neurons_firing[self.model["Cells_types"][neuron_name]] += nb_neurons_firing_local

        def reset(self):
                for neuron_name in self.neural_network:
                        self.activity[neuron_name] = 0
                        self.neural_network[neuron_name].Vm = 0
                        self.neural_network[neuron_name].I_local *= 0
                        self.neural_network[neuron_name].t_res = 0
                        self.neural_network[neuron_name].current_I_index = 0
                self.nb_neurons_firing = {type_neuron: 0 for type_neuron in np.unique(self.model["Cells_types"].values())}

        def activate_system(self, input_activation, time_activation, output_formats = None, final_aggregation_function=None):
                if output_formats is not None: output = [[] for output_format in output_formats]
                for _ in range(int(time_activation*1./self.dt)):
                        for neuron_name,I in input_activation.iteritems():
                                self.neural_network[neuron_name].update_I(I)
                        self.update_neural_network()
                        if self.monitoring:
                                self.monitoring_memory[self.monitoring_memory_index,:] = self.activity
                                self.monitoring_memory_index += 1
                                if self.monitoring_memory_index > self.monitoring_memory.shape[1]:
                                        self.monitoring_memory_index = 0
                        if output_formats is not None:
                                for i,output_format in enumerate(output_formats):
                                        output[i].append(output_format[AGGREGATION_FUNCTION](self.activity[output_format[LIST_NEURONS_OUTPUT]]))
                
                if output_formats is not None:
                        if final_aggregation_function is not None:
                                final_output = [[] for output_format in output_formats]
                                for i,output_format in enumerate(output):
                                        final_output[i] = final_aggregation_function(output[i])
                                return final_output
                        else:
                                return output
                return self.activity
                

class neural_network_server(neural_network):                
        def __init__(self, dt, model_file, tcp_ip=TCP_IP, tcp_port=TCP_PORT):
                neural_network.__init__(self,dt,model_file)

                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.bind((tcp_ip,tcp_port))
                self.socket.listen(1)
                self.conn, self.addr = self.socket.accept()



        def run(self):
                while 1:
                        data_pickle = self.conn.recv(BUFFER_SIZE)
                        if not data_pickle:
                                return 1
                        sensory_data = pickle.loads(data_pickle)
                        result = self.activate_system(**sensory_data)
                        self.conn.send(pickle.dumps(result,-1))


if __name__ == "__main__":
        celegans_file = "connectome_manager/models/celegans3000_full_neuroml.pickle"
        celegans_nn = neural_network(0.01,celegans_file)
        I = np.ones(100)*3
        dt = 0.01
        results = {}
        for neuron in celegans_nn.neural_network.keys()[0:2]:
                for i in range(10):
                        celegans_nn.neural_network[neuron].update_I(I)
                        celegans_nn.update_neural_network()
                        celegans_nn.update_neural_network()
                results[neuron] = celegans_nn.nb_neurons_firing 
        print results
        
        output_formats = [{LIST_NEURONS_OUTPUT:['VA'+str(i) for i in range(1,12)] , AGGREGATION_FUNCTION: np.sum}]
        print celegans_nn.activate_system({'ALML':1.5}, time_activation=4, output_formats = output_formats, final_aggregation_function=None)


