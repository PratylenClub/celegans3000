# The data should contain the following elements:
+ A file containing the connectome information (here called Connectome.csv): <origin> <target> <number of connections> <neurotransmitter>
+ A file containing the neurons-muscles information (here called Neurons_to_muscles.csv): <Neuron> <muscle> <number of connections> <neurotransmitter>
+ A file containing the sensory information (here called Sensory.csv): <Function> <number of connections> <neurotransmitter>
+ A binary pickle file (called here muscle_2_motor.pickle) that contains a dictionary that maps the muscles to robot motor id
+ A binary pickle file (called here sensory_2_sensors.pickle) that contains a dictionary that maps the sensory function to robot sensor id
+ A binary pickle file (called here Neurotransmiters_2_coefficient.pickle) that contains a dictionary that maps the neurotransmitter name to a coefficient