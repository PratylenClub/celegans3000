import numpy as np

class cell:
        def __init__(self,
                dt,
                I_dt,
                Vm0     = None):
                self.dt = dt
                self.I_dt = I_dt
                self.I_local = np.ones(self.I_dt * 1.0 / self.dt)*1.5
                self.current_I_index = 0
                self.neighbors = {}
                self.Vm = 0
                if Vm0 is not None: self.Vm = Vm0

        def update_I(self,I,set_value=False):
                I = np.asarray(I)
                if len(I.shape) == 0:
                        I = np.asarray([float(I)])
                if I.size > self.I_local.size:
                        I = I[:self.I_local.size - 1]
                next_I_index = self.current_I_index+1
                if next_I_index >= self.I_local.size: next_I_index = 0
                right_index_boundary = min(next_I_index + I.size, self.I_local.size)
                right_piece_size = right_index_boundary - next_I_index
                left_index_boundary = I.size - right_piece_size

                if set_value:
                        self.I_local[next_I_index:right_index_boundary] = I[:right_piece_size]
                        self.I_local[:left_index_boundary] = I[right_piece_size:]
                else:
                        self.I_local[next_I_index:right_index_boundary] += I[:right_piece_size]
                        self.I_local[:left_index_boundary] += I[right_piece_size:]
              
        def update(self):
                self.Vm = self.I_local[self.current_I_index]
                self.I_local[self.current_I_index] = 0
                self.current_I_index += 1
                if self.current_I_index == self.I_local.size:
                        self.current_I_index = 0
                return int(np.abs(self.Vm)>0)

        def append_neighbor(self, neighbor):
                self.neighbors[neighbor.keys()[0]] = neighbor[neighbor.keys()[0]]


class muscle(cell):
        def __init__(self, 
                dt = 0.01,
                I_dt = 1.0):
                cell.__init__(self,dt,I_dt)                


class neuron(cell):
        def __init__(self,
                dt = 1,
                Vth = 1,
                tau_ref = 1,
                I_dt = 2,
                Vm0 = None,
                ):
                self.dt = dt
                self.Vth = Vth
                self.I_dt = I_dt
                self.tau_ref = tau_ref
                self.t_res = 0
                self.I_local = np.ones(self.I_dt * 1.0 / self.dt)*1.5
                self.current_I_index = 0
                self.neighbors = {}
                if Vm0 is not None: self.Vm = Vm0


        def update(self,I=None):
                has_fired = 0
                if I is not None:
                        self.update_I(I)
                if self.t_res <= 0:
                        self.Vm += self.I_local[self.current_I_index]
                        if self.Vm >= self.Vth:
                                self.Vm += self.V_spike
                                self.t_res = self.tau_ref
                                for key,neighbor_info in self.neighbors.iteritems():
                                        neighbor = neighbor_info["Cell"]
                                        weight = neighbor_info["Weight"]
                                        self.neighbors[key]["Cell"].update_I(np.ones(neighbor.I_local.size - 1)*weight*self.Vm)
                                has_fired = 1
                else:
                        self.t_res -= self.dt
                        self.Vm = 0
                self.I_local[self.current_I_index] = 0
                self.current_I_index += 1
                if self.current_I_index == self.I_local.size:
                        self.current_I_index = 0
                return has_fired


        def update_time_duration(self, I,set_value=False):
                Vm = np.zeros(I.size)
                for i in range(I.size-self.I_local.size):
                        Vm[i] = self.Vm
                        self.update_I(I[i:i+self.I_local.size],set_value)
                        self.update()
                return np.asarray(range(0,Vm.size)) * self.dt, Vm







class LIF_neuron(neuron):
        def __init__(self,
                dt      = 0.01,               
                Rm      = 1,
                Cm      = 10,
                tau_ref = 4,
                Vth     = 1,
                V_spike = 0.5,
                U_res   = 0,
                I_dt    = 1.0,
                Vm0     = None):
                """
                dt simulation time step (msec) Procesor
                t_rest initial refractory time
                Vm potential (V) trace over time
                Rm resistance (kOhm)
                Cm capacitance (uF)
                tau_ref refractory period (msec)
                Vth  spike threshold (V)
                V_spike spike delta (V)
                U_res rest state
                """
                self.dt      = dt             
                self.Rm      = Rm
                self.Cm      = Cm
                self.tau_ref = tau_ref
                self.Vth     = Vth
                self.V_spike = V_spike
                self.U_res   = U_res
                self.t_res   = 0
                self.tau_m   = Rm*Cm
                self.I_dt    = I_dt
                self.I_local = np.ones(self.I_dt * 1.0 / self.dt)*1.5
                self.Vm      = self.U_res
                self.current_I_index = 0
                self.neighbors = {}
                if Vm0 is not None: self.Vm = Vm0

        def update(self,I=None):
                has_fired = 0
                if I is not None:
                        self.update_I(I)
                if self.t_res <= 0:
                        self.Vm += (self.U_res - self.Vm + self.I_local[self.current_I_index]*self.Rm) / self.tau_m * self.dt
                        if self.Vm >= self.Vth:
                                self.Vm += self.V_spike
                                self.t_res = self.tau_ref
                                for key,neighbor_info in self.neighbors.iteritems():
                                        neighbor = neighbor_info["Cell"]
                                        weight = neighbor_info["Weight"]
                                        self.neighbors[key]["Cell"].update_I(np.ones(neighbor.I_local.size - 1)*weight*self.Vm*1./self.Rm)
                                has_fired = 1
                else:
                        self.t_res -= self.dt
                        self.Vm = 0
                self.I_local[self.current_I_index] = 0
                self.current_I_index += 1
                if self.current_I_index == self.I_local.size:
                        self.current_I_index = 0
                return has_fired

if __name__ == "__main__":
        n = LIF_neuron()
        n2 = LIF_neuron()
        m  = muscle()
        print n.neighbors
        n.append_neighbor({"n2":n2})
        n.append_neighbor({"m":m})
        print n.neighbors
        print n.I_local
        n.update_I(2)
        print n.I_local
