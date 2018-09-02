import json
import random
from dense import Input
from sys import stdin
import json

inp = Input(1)
f = open('data.txt', 'w')
while True:
	ch = stdin.readline(1)
	f.write(ch)
	f.flush()
    #z = input()
    #commands = ['left', 'right', 'stop']
    #cmd = random.choice(commands)
    #print(json.dumps({"command": cmd, 'debug': cmd}))