from Cells import LIF_neuron, muscle
import pickle
import pandas as pd
import numpy as np
from parameters.params import *
import socket
import matplotlib.animation as animation
import matplotlib.pyplot as plt
MUSCLE_TYPE = "Muscle"
LIST_NEURONS_OUTPUT = "LIST_NEURONS_OUTPUT"
AGGREGATION_FUNCTION = "AGGREGATION_FUNCTION"

class neural_network:
        def __init__(self, dt, model_file, monitoring_period_size = 20, monitoring_neurons = []):
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
                self.monitoring = monitoring_period_size>0
                self.monitoring_period_size = monitoring_period_size
                self.monitoring_memory_size = int(monitoring_period_size * 1./self.dt)
                self.monitoring_memory = pd.DataFrame(np.zeros((self.monitoring_memory_size,len(self.neural_network))),columns = self.activity.index)

                if self.monitoring:
                        self.monitoring_neurons = monitoring_neurons
                        if len(self.monitoring_neurons):
                                self.ax = plt.axes(xlim=(0,self.monitoring_memory_size), ylim=(-1,10))
                                plt.ion()
                                self.lines = [0 for i in self.monitoring_neurons]
                                for i,neuron_name in enumerate(self.monitoring_neurons):
                                        self.lines[i], = self.ax.plot(self.monitoring_memory.index,self.monitoring_memory[neuron_name],"-")
                                plt.pause(0.5)

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
                                self.monitoring_memory.loc[self.monitoring_memory_index] = self.activity
                                self.monitoring_memory_index += 1
                                if self.monitoring_memory_index > self.monitoring_memory.shape[0]:
                                        self.monitoring_memory_index = 0
                                if len(self.monitoring_neurons):
                                        for i,neuron_name in enumerate(self.monitoring_neurons):
                                                self.lines[i].set_data(self.monitoring_memory.index, self.monitoring_memory[neuron_name])
                                        plt.pause(0.01)
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
        celegans_nn = neural_network(0.01,celegans_file)#,monitoring_neurons = ['VA'+str(i) for i in range(1,12)])
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

        nose_sensitive_neurons = ['ALML','ALMR','AVM','IL1VR','IL1VL','IL1DR','IL1DL','IL1R','IL1L']
        tail_sensitive_neurons  = ['PLML','PLMR','PVM']
        food = ['ADER', 'ADEL']
        chemosensory = ['ASEL','ASKL','ASKR','PHAL','PHAR','PHBL','PHBR']

        VA = ['VA'+str(i) for i in range(1,12)]
        DA = ['DA'+str(i) for i in range(1,10)]
        VB = ['VB'+str(i) for i in range(1,12)]
        DB = ['DB'+str(i) for i in range(1,8)]

        nose_excitation = {neuron: 1.5 for neuron in nose_sensitive_neurons}
        tail_excitation = {neuron: 1.5 for neuron in tail_sensitive_neurons}
        food_excitation = {neuron: 1.5 for neuron in food}
        chemosensory_excitation = {neuron: 1.5 for neuron in chemosensory}
        #output_formats = [{LIST_NEURONS_OUTPUT: nose_sensitive_neurons, AGGREGATION_FUNCTION: np.sum}]
        output_formats = [{LIST_NEURONS_OUTPUT: tail_sensitive_neurons, AGGREGATION_FUNCTION: np.sum}]

        print celegans_nn.activate_system(nose_excitation, time_activation=20, output_formats = output_formats, final_aggregation_function=None)

        for i,neuron_name in enumerate(VA):
                plt.plot(celegans_nn.monitoring_memory.index,celegans_nn.monitoring_memory[neuron_name],"r-")
        for i,neuron_name in enumerate(VB):
                plt.plot(celegans_nn.monitoring_memory.index,celegans_nn.monitoring_memory[neuron_name],"b-")

        for i,neuron_name in enumerate(DA):
                plt.plot(celegans_nn.monitoring_memory.index,celegans_nn.monitoring_memory[neuron_name],"y-")
        for i,neuron_name in enumerate(DB):
                plt.plot(celegans_nn.monitoring_memory.index,celegans_nn.monitoring_memory[neuron_name],"c-")

        plt.show()