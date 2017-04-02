import pickle as p

class NN:
    def __init__(self,model_file):
        model = p.load(open(model_file,"rb"))
        self.Neural_Network = model["Neural_Network"]
        self.Cells_state = model["Cells_state"]
        