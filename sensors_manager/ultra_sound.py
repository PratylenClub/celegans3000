#!/usr/bin/python
# -*- coding: utf-8 -*-
import numpy as np
import RPi.GPIO as GPIO    #Importamos la librería GPIO
import time                #Importamos time (time.sleep)

def return_distance_to_obstacle(nb_trials,delta_time):
    GPIO.setmode(GPIO.BCM)     #Ponemos la placa en modo BCM
    GPIO_TRIGGER = 25          #Usamos el pin GPIO 25 como TRIGGER
    GPIO_ECHO    = 5           #Usamos el pin GPIO 5 como ECHO
    GPIO.setup(GPIO_TRIGGER,GPIO.OUT)  #Configuramos Trigger como salida
    GPIO.setup(GPIO_ECHO,GPIO.IN)      #Configuramos Echo como entrada
    GPIO.output(GPIO_TRIGGER,False)    #Ponemos el pin 25 como LOW
    measures = []
    for trial in xrange(nb_trials):
        GPIO.output(GPIO_TRIGGER,True)   #Enviamos un pulso de ultrasonidos
        time.sleep(0.00001)              #Una pequeñña pausa
        GPIO.output(GPIO_TRIGGER,False)  #Apagamos el pulso
        start = time.time()              #Guarda el tiempo actual mediante time.time()
        while GPIO.input(GPIO_ECHO)==0:  #Mientras el sensor no reciba señal...
            start = time.time()          #Mantenemos el tiempo actual mediante time.time()
        while GPIO.input(GPIO_ECHO)==1:  #Si el sensor recibe señal...
            stop = time.time()           #Guarda el tiempo actual mediante time.time() en otra variable
        elapsed = stop-start             #Obtenemos el tiempo transcurrido entre envío y recepción
        distance = (elapsed * 34300)*0.5 #Distancia es igual a tiempo por velocidad partido por 2   D = (T x V)/2
        measures.append(distance)        #Devolvemos la distancia (en centímetros) por pantalla
        time.sleep(delta_time)           #Pequeña pausa para no saturar el procesador de la Raspberry
    GPIO.cleanup()                       #Limpiamos los pines GPIO y salimos
    return np.median(np.asarray(measures))
"""    
for i in range(30):
    print return_distance_to_obstacle(10,0.1)
"""