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

class Client(object):
    def get_command(self):
        pass

    def close(self):
        pass

    def send_message(self, t, d):
        pass

    def save_log_to_disk(self, log, path):
        pass

    def get_solution_id(self):
        return random.randint(11000, 12000)

class DenseClient(Client):
    def __init__(self, layers, input_layer):
        self.layers = layers
        self.input_layer = input_layer
        self.inp = np.zeros(20)

    def send_message(self, t, d):
        if t != 'new_match':
            #print('my car ' + str(d['my_car']))
            #print('enemy car ' + str(d['enemy_car']))
            self.my_car = d['my_car']
            self.enemy_car = d['enemy_car']
            #print(type(d))
    def PrepareInput(self): #Подготавливает вход для нейронной сети
        
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

    @asyncio.coroutine
    def get_command(self):
        self.PrepareInput()
        self.input_layer.SetOutput(self.inp)
        for l in self.layers:
            l.Prepare()
        output = self.layers[- 1].GetOutput()
        result = np.argmax(output)
        choises = ['left','right','stop']
        #print(choises[result] + ':' + str(output))
        return  {'command': choises[result] }
        


class KeyboardClient(Client):
    @property
    def KEY_COMMAND_MAP(self):
        return {
            pyglet.window.key.MOTION_LEFT: 'left',
            pyglet.window.key.MOTION_RIGHT: 'right',
            pyglet.window.key.MOTION_DOWN: 'stop',
        }

    def __init__(self, window):
        self.last_pressed_button = pyglet.window.key.MOTION_DOWN

        @window.event
        def on_key_press(symbol, _):
            self.last_pressed_button = symbol

        @window.event
        def on_key_release(symbol, _):
            if symbol in [pyglet.window.key.MOTION_RIGHT, pyglet.window.key.MOTION_LEFT]:
                self.last_pressed_button = pyglet.window.key.MOTION_DOWN

    @asyncio.coroutine
    def get_command(self):
        return {'command': self.KEY_COMMAND_MAP.get(self.last_pressed_button, 'stop')}

    def save_log_to_disk(self, log, path):
        pass


class FileClient(Client):
    def __init__(self, path_to_script, path_to_log=None):
        self.process = Popen(path_to_script, stdout=PIPE, stdin=PIPE)
        self.last_message = None
        if path_to_log is None:
            base_dir = os.getcwd()
            now = datetime.datetime.now().strftime('%Y_%m_%d-%H-%M-%S.log.gz')
            self.path_to_log = os.path.join(base_dir, now)
        else:
            self.path_to_log = path_to_log

    def send_message(self, t, d):
        msg = {
            'type': t,
            'params': d
        }
        msg_bytes = '{}\n'.format(json.dumps(msg)).encode()

        self.process.stdin.write(msg_bytes)
        self.process.stdin.flush()

    @asyncio.coroutine
    def get_command(self):
        try:
            line = self.process.stdout.readline().decode('utf-8')
            state = json.loads(line)
            return state
        except Exception as e:
            return {'debug': str(e)}

    def save_log_to_disk(self, log, _):
        with gzip.open(self.path_to_log, 'w') as f:
            f.write(json.dumps(log).encode())

        return {
            'filename': os.path.basename(self.path_to_log),
            'is_private': True,
            'location': self.path_to_log
        }


class TcpClient(Client):
    EXECUTION_LIMIT = datetime.timedelta(seconds=MAX_EXECUTION_TIME)

    def __init__(self, reader, writer):
        self.reader = reader
        self.writer = writer
        self.execution_time = datetime.timedelta()
        self.solution_id = None

    def save_log_to_disk(self, log, path):
        location = path.format(str(self.solution_id) + '.gz')

        with gzip.open(location, 'wb') as f:
            f.write(json.dumps(log).encode())

        return {
            'filename': os.path.basename(location),
            'is_private': True,
            'location': location
        }

    @asyncio.coroutine
    def set_solution_id(self):
        hello_json = yield from asyncio.wait_for(self.reader.readline(), timeout=REQUEST_MAX_TIME)
        try:
            self.solution_id = json.loads(hello_json.decode('utf-8')).get('solution_id')
        except ValueError:
            pass

        return bool(self.solution_id)

    def send_message(self, t, d):
        msg = {
            'type': t,
            'params': d
        }
        msg_bytes = '{}\n'.format(json.dumps(msg)).encode()
        self.writer.write(msg_bytes)

    @asyncio.coroutine
    def get_command(self):
        try:
            before = datetime.datetime.now()
            z = yield from asyncio.wait_for(self.reader.readline(), timeout=REQUEST_MAX_TIME)
            if not z:
                raise ConnectionError('Connection closed')
            self.execution_time += (datetime.datetime.now() - before)
            if self.execution_time > self.EXECUTION_LIMIT:
                raise Exception('sum timeout error')
        except asyncio.TimeoutError:
            raise asyncio.TimeoutError('read timeout error')
        try:
            z = json.loads(z.decode())
        except ValueError:
            z = {'debug': 'cant pars json'}

        return z

    def close(self):
        self.writer.close()

    def get_solution_id(self):
        return self.solution_id
