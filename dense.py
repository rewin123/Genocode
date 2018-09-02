import numpy as np

class Layer(object):
    def __init__(self, output_size):
        self.output_size = output_size
        self.output = np.zeros((output_size,))
    
    def Prepare(self): #Выполняет все необходимые действия, для получения выхода слоя
        pass
    
    def GetOutput(self): #Возращает вычисленный выход слоя
        return self.output

class Input(Layer):
    def __init__(self, output_size):
        super().__init__(output_size)
        
    def SetOutput(self,input):
        self.output = input

class Dense(Layer):
    
    def __init__(self, inp, output_size):
        self.inp = inp
        self.input_size = inp.output_size
        self.output_size = output_size
        self.size = inp.output_size * output_size
        self.ws = np.zeros((self.input_size,self.output_size))
        super().__init__(output_size)
    def AddNoise(self):
        noise = np.random.normal(size=self.ws.shape)
        self.ws = self.ws+noise
        
    def Prepare(self):
        in_arr = self.inp.GetOutput()
        self.output = np.dot(in_arr, self.ws)

inp = Input(10)
d1 = Dense(inp, 11)
d2 = Dense(d1, 12)

print("inp out: " + str(inp.output_size))
print("d1 out: " + str(d1.output_size))
print("d2 out: " + str(d2.output_size))

print("d1 size: " + str(d1.size))
print("d2 size: " + str(d2.size))

d1.Prepare()
print(d1.GetOutput())

inp.SetOutput(np.ones(inp.output_size))
print(inp.GetOutput())

d1.Prepare()
print(d1.GetOutput())

d1.AddNoise()

d1.Prepare()
print(d1.GetOutput())

