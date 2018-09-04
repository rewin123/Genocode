from itertools import product
from cell import Cell
import cell
import random
from mechanic.game import Game
from asyncio import events
import pickle

def Match(p1,p2):
    game = Game([p1, p1], games, extended_save=False)
    while not game.game_complete:
        game.tick()
        if not game.game_complete:
            future_message = loop.run_until_complete(game.tick())

    winner = game.get_winner()
    if winner:
        return winner.id
    else:
        return 0

loop = events.new_event_loop()
events.set_event_loop(loop)
maps = ['PillMap']
cars = ['Buggy']
games = [','.join(t) for t in product(maps, cars)]

genepool = []
pool_size = 1000
bottle_size = 500
match_count = 3
gen_steps = 10


for i in range(0,pool_size):
    genepool.append(Cell())
g = 0
while True:
    for c in genepool:
        c.mass = 0
        c.matches = 0
    index = 0
    for c in genepool:
        print(str(g) + ":" + str(index))
        index += 1
        for m in range(c.matches, match_count):
            enemy = random.choice(genepool)
            tryes = 0
            while(enemy.matches >= match_count and tryes < 10):
                enemy = random.choice(genepool)
                tryes += 1
            c.matches += 1
            enemy.matches += 1
            if random.randint(0,1) == 0:
                result = Match(c, enemy)
                if result == 1:
                    c.mass += 1
                    enemy.mass -= 1
                else:
                    if(result == 2):
                        c.mass -= 1
                        enemy.mass += 1
            else:
                result = Match(enemy, c)
                if result == 1:
                    c.mass -= 1
                    enemy.mass += 1
                else:
                    if(result == 2):
                        c.mass += 1
                        enemy.mass -= 1
    genepool.sort(key= lambda x: -x.mass / x.matches)
    genepool = genepool[:bottle_size]
    for i in range(bottle_size,pool_size):
        pos = random.randint(0,i - 1)
        pos2 = random.randint(0,i - 1)
        genepool.append(cell.Child(genepool[pos], genepool[pos2]))

    #Сохраняем наилучшую особь
    with open(str(g) + "_gen.pkl","wb") as output:
        pickle.dump(genepool[0],output,pickle.HIGHEST_PROTOCOL)
    g += 1
