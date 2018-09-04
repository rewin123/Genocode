import datetime
import gzip
import json

import os
import random

import pyglet
import asyncio
from subprocess import Popen, PIPE

from mechanic.constants import MAX_EXECUTION_TIME, REQUEST_MAX_TIME
import numpy as np

from dense import Input,Dense,Relu
from mechanic.strategy import Client
import numpy as np
import pickle

class Cell(Client):
    def __init__(self):
        self.inp = np.zeros(21)
        self.mass = 0 #êîë-àî ðåéòèíãà
        self.matches = 0 #êîë-âî ñûãðàííûõ ìàò÷åé

        #Íàñðîéêà íåéðîííîé ñåòè
        self.layers = []
        self.input_layer = Input(21)
        l = Dense(self.input_layer, 42)
        l.AddNoise()
        l.AddNoise()
        l.AddNoise()
        l.AddNoise()
        self.layers.append(l)
        l = Relu(l)
        self.layers.append(l)
        l = Dense(l,3)
        l.AddNoise()
        l.AddNoise()
        l.AddNoise()
        l.AddNoise()
        self.layers.append(l)
        self.output = l
    def Mutate(self):
        c = Cell()
        c.layers[0].ws = c.layers[0].ws + self.layers[0].ws
        c.layers[2].ws = c.layers[2].ws + self.layers[2].ws
        return c
    def Clone(): #Создаеь независимую копию клетки
        c = Cell()
        c.layers[0].ws = c.layers[0].ws
        c.layers[2].ws = c.layers[2].ws
        return c        
    def send_message(self, t, d):
        if t != 'new_match':
            #print('my car ' + str(d['my_car']))
            #print('enemy car ' + str(d['enemy_car']))
            self.my_car = d['my_car']
            self.enemy_car = d['enemy_car']
            self.deadline = d['deadline_position']
            #print(type(d))
    def PrepareInput(self): #Ïîäãîòàâëèâàåò âõîä äëÿ íåéðîííîé ñåòè
        
        self.inp[0] = self.my_car[0][0]
        self.inp[1] = self.my_car[0][1]
        self.inp[2] = self.my_car[1]
        self.inp[3] = self.my_car[2]
        self.inp[4] = self.my_car[3][0]
        self.inp[5] = self.my_car[3][1]
        self.inp[6] = self.my_car[3][2]
        self.inp[7] = self.my_car[4][0]
        self.inp[8] = self.my_car[4][1]
        self.inp[9] = self.my_car[4][2]

        self.inp[10] = self.enemy_car[0][0]
        self.inp[11] = self.enemy_car[0][1]
        self.inp[12] = self.enemy_car[1]
        self.inp[13] = self.enemy_car[2]
        self.inp[14] = self.enemy_car[3][0]
        self.inp[15] = self.enemy_car[3][1]
        self.inp[16] = self.enemy_car[3][2]
        self.inp[17] = self.enemy_car[4][0]
        self.inp[18] = self.enemy_car[4][1]
        self.inp[19] = self.enemy_car[4][2]
        self.inp[20] = self.deadline

    @asyncio.coroutine
    def get_command(self):
        self.PrepareInput()
        self.input_layer.SetOutput(self.inp)
        for l in self.layers:
            l.Prepare()
        output = self.layers[-1].GetOutput()
        result = np.argmax(output)
        choises = ['left','right','stop']
        #print(choises[result] + ':' + str(output))
        return  {'command': choises[result] }

def Child(c1,c2):
    k = random.random()
    c = Cell()
    c.layers[0].ws = c.layers[0].ws * 0.01 + c1.layers[0].ws * k + c2.layers[0].ws * (1 - k)
    c.layers[2].ws = c.layers[2].ws * 0.01 + c1.layers[2].ws * k + c2.layers[2].ws * (1 - k)
    return c

def SaveTest():
    c = Cell()
    with open('c.pkl','wb') as output:
        pickle.dump(c,output,pickle.HIGHEST_PROTOCOL)

    del c

    with open('c.pkl', 'rb') as input:
        company1 = pickle.load(input)
        print(company1.input_layer.GetOutput())

def TestChild():
    c1 = Cell()
    c2 = Cell()

    c3 = Child(c1,c2)