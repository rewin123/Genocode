from itertools import product

import pyglet
import pymunk.pyglet_util
import argparse

from asyncio import events

from mechanic.game import Game
from mechanic.strategy import KeyboardClient, FileClient
from cell import Cell

from dense import Input, Dense, Relu



parser = argparse.ArgumentParser(description='LocalRunner for MadCars')

parser.add_argument('-f', '--fp', type=str, nargs='?',
                    help='Path to executable with strategy for first player', default='keyboard')
parser.add_argument('--fpl', type=str, nargs='?', help='Path to log for first player')

parser.add_argument('-s', '--sp', type=str, nargs='?',
                    help='Path to executable with strategy for second player', default='keyboard')
parser.add_argument('--spl', type=str, nargs='?', help='Path to log for second player')


maps = ['PillMap']
cars = ['Buggy']
games = [','.join(t) for t in product(maps, cars)]


parser.add_argument('-m', '--matches', nargs='+', help='List of pairs(map, car) for games', default=games)

args = parser.parse_args()

first_player = args.fp
second_player = args.sp


fc = Cell()
sc = fc.Mutate()


game = Game([fc, sc], args.matches, extended_save=False)

loop = events.new_event_loop()
events.set_event_loop(loop)

while not game.game_complete:
    game.tick()
    if not game.game_complete:
        future_message = loop.run_until_complete(game.tick())

winner = game.get_winner()
if winner:
    print(str(winner.id) + " win");

