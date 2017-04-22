import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
import socket
import pickle
import sys




RADIUS = 0.1
LENGTH = 0.2
EPSILON = 0.05
LIMITS_X = (-1,1)
LIMITS_Y = (-1,1)
PRECISION = 2 #*10**-precision
MAX_SPEED = 255

class simulator:
    def __init__(self,left_trim, right_trim,x0=0,y0=0,phi0=0):#, obstacles=DEFAULT_OBSTACLES):
        self.x = x0
        self.y = y0
        self.phi = phi0
        self.radius = RADIUS
        self.length = LENGTH
        self.epsilon = EPSILON
        self.limits_x = LIMITS_X
        self.limits_y = LIMITS_Y
        self.precision = PRECISION
        self.step = 10**-self.precision
        self.right_trim = right_trim
        self.left_trim = left_trim

        self.x_vals_grid = np.arange(self.limits_x[0],self.limits_x[1],self.step)
        self.y_vals_grid = np.arange(self.limits_y[0],self.limits_y[1],self.step)

        self.obstacles = np.zeros((self.x_vals_grid.size, self.y_vals_grid.size))
        self.obstacles[25, 5:] = 1
        self.obstacles[85, 5:] = 1
        self.obstacles[110, 5:] = 1
        self.obstacles[5:, 85] = 1
        self.obstacles[5:, 110] = 1

        self.fig = plt.figure()
        self.ax = plt.axes(xlim=self.limits_x, ylim=self.limits_y)
        self.plot_obstacles()
        plt.ion()
        self.line, = self.ax.plot([self.x], [self.y],"o", lw=2)
        plt.pause(1)
        self.obstacle_encountered = 0

    def plot_obstacles(self):
        for i,x_val in enumerate(self.x_vals_grid):
            for j,y_val in enumerate(self.y_vals_grid):
                if self.obstacles[i,j]:
                    self.ax.plot([x_val],[y_val],"k.",alpha=0.4)

    def fix_speed(self,speed,max_val,min_val):
        if speed > max_val : speed = max_val
        if speed < min_val : speed = min_val
        speed *= np.pi/max_val
        return speed

    # animation function.  This is called sequentially
    def animate(self,wr,wl,time_duration):
        wr_sign = np.sign(wr)
        wl_sign = np.sign(wl)
        wr = wr_sign * self.fix_speed(np.abs(wr),MAX_SPEED,self.right_trim)
        wl = wl_sign * self.fix_speed(np.abs(wl),MAX_SPEED,self.left_trim)
        t = 0
        self.obstacle_encountered = 0
        while t < time_duration:
            delta_x = self.epsilon * self.radius * 1./2 * (np.cos(self.phi)*wr +np.cos(self.phi)*wl)
            delta_y = self.epsilon * self.radius * 1./2 * (np.sin(self.phi)*wr +np.sin(self.phi)*wl)
            delta_phi = self.epsilon * self.radius * 1./2 * (wr/self.length - wl/self.length)
            new_x = self.x + delta_x
            new_y = self.y + delta_y
            if new_x < self.limits_x[1] and new_x > self.limits_x[0]:
                if new_y < self.limits_y[1] and new_y > self.limits_y[0]: 
                    if not self.check_obstacle(new_x,new_y):
                        self.x = new_x
                        self.y = new_y
                    else:
                        self.obstacle_encountered = 1
                        return 1
            self.phi += delta_phi
            self.line.set_data(self.x,self.y)
            t += EPSILON
            plt.pause(0.0001)
        return 0

    def only_right(self,wr,time_duration):
        wr_sign = np.sign(wr)
        wr = wr_sign * self.fix_speed(np.abs(wr),MAX_SPEED,self.right_trim)
        wl = 0
        t = 0
        self.obstacle_encountered = 0
        while t < time_duration:
            delta_x = self.epsilon * self.radius * 1./2 * (np.cos(self.phi)*wr +np.cos(self.phi)*wl)
            delta_y = self.epsilon * self.radius * 1./2 * (np.sin(self.phi)*wr +np.sin(self.phi)*wl)
            delta_phi = self.epsilon * self.radius * 1./2 * (wr/self.length - wl/self.length)
            new_x = self.x + delta_x
            new_y = self.y + delta_y
            if new_x < self.limits_x[1] and new_x > self.limits_x[0]:
                if new_y < self.limits_y[1] and new_y > self.limits_y[0]: 
                    if not self.check_obstacle(new_x,new_y):
                        self.x = new_x
                        self.y = new_y
                    else:
                        self.obstacle_encountered = 1
                        return 1
            self.phi += delta_phi
            self.line.set_data(self.x,self.y)
            t += EPSILON
            plt.pause(0.0001)
        return 0

    def only_left(self,wl,time_duration):
        wl_sign = np.sign(wl)
        wl = wl_sign * self.fix_speed(np.abs(wl),MAX_SPEED,self.right_trim)
        wr = 0
        t = 0
        self.obstacle_encountered = 0
        while t < time_duration:
            delta_x = self.epsilon * self.radius * 1./2 * (np.cos(self.phi)*wr +np.cos(self.phi)*wl)
            delta_y = self.epsilon * self.radius * 1./2 * (np.sin(self.phi)*wr +np.sin(self.phi)*wl)
            delta_phi = self.epsilon * self.radius * 1./2 * (wr/self.length - wl/self.length)
            new_x = self.x + delta_x
            new_y = self.y + delta_y
            if new_x < self.limits_x[1] and new_x > self.limits_x[0]:
                if new_y < self.limits_y[1] and new_y > self.limits_y[0]: 
                    if not self.check_obstacle(new_x,new_y):
                        self.x = new_x
                        self.y = new_y
                    else:
                        self.obstacle_encountered = 1
                        return 1
            self.phi += delta_phi
            self.line.set_data(self.x,self.y)
            t += EPSILON
            plt.pause(0.0001)
        return 0

    def check_obstacle(self,x,y):
        if x <= self.limits_x[0] or y <= self.limits_y[0] or x >= self.limits_x[1] or y >= self.limits_y[1]:
            return 1
        index_x = max(min(int((round(x, self.precision)-self.limits_x[0])/self.step),self.x_vals_grid.size - 1),0)
        index_y = max(min(int((round(y, self.precision)-self.limits_y[0])/self.step),self.y_vals_grid.size - 1),0)
        return self.obstacles[index_x][index_y]

    def return_ultra_sound_sensory(self):
        if self.check_obstacle(self.x,self.y):
            return 1
        else:            
            return 100

    def return_wifi_signal(self):
        return 100#1 - (self.x**2 + self.y**2) 

if __name__ == "__main__":
    import random
    s = simulator(left_trim=40, right_trim=40)
    plt.pause(1)
    for i in range(100):
        print i
        s.animate((random.random()-0.5)*255,np.pi*(random.random()-0.5)*255,1)

