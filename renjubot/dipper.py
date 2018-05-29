#!/usr/bin/python3.4

import concurrent.futures
import enum
import itertools
import logging
import numpy
import sys
import time
import traceback
import os
import logging
import random


POS_TO_LETTER = 'abcdefghjklmnop'
LETTER_TO_POS = {letter: pos for pos, letter in enumerate(POS_TO_LETTER)}

def to_move(pos):
    # print(pos)
    return POS_TO_LETTER[pos[1]] + str(pos[0] + 1)

def to_pos(move):
    return int(move[1:]) - 1, LETTER_TO_POS[move[0]]

def list_positions(board, player):
    return numpy.vstack(numpy.nonzero(board == player)).T

def sequence_length(board, I, J, value):
    length = 0

    for i, j in zip(I, J):
        if board[i, j] != value:
            break
        length += 1

    return length


def check_horizontal(board, pos):
    player = board[pos]
    if not player:
        return False

    i, j = pos
    length = 1

    length += sequence_length(
        board,
        itertools.repeat(i),
        range(j + 1, min(j + Game.line_length, Game.width)),
        player
    )

    length += sequence_length(
        board,
        itertools.repeat(i),
        range(j - 1, max(j - Game.line_length, -1), -1),
        player
    )

    return length >= Game.line_length

def check_vertical(board, pos):
    player = board[pos]
    if not player:
        return False

    i, j = pos
    length = 1

    length += sequence_length(
        board,
        range(i + 1, min(i + Game.line_length, Game.height)),
        itertools.repeat(j),
        player
    )

    length += sequence_length(
        board,
        range(i - 1, max(i - Game.line_length, -1), -1),
        itertools.repeat(j),
        player
    )

    return length >= Game.line_length

def check_main_diagonal(board, pos):
    player = board[pos]
    if not player:
        return False

    i, j = pos
    length = 1

    length += sequence_length(
        board,
        range(i + 1, min(i + Game.line_length, Game.height)),
        range(j + 1, min(j + Game.line_length, Game.width)),
        player
    )

    length += sequence_length(
        board,
        range(i - 1, max(i - Game.line_length, -1), -1),
        range(j - 1, max(j - Game.line_length, -1), -1),
        player
    )

    return length >= Game.line_length

def check_side_diagonal(board, pos):
    player = board[pos]
    if not player:
        return False

    i, j = pos
    length = 1

    length += sequence_length(
        board,
        range(i - 1, max(i - Game.line_length, -1), -1),
        range(j + 1, min(j + Game.line_length, Game.width)),
        player
    )

    length += sequence_length(
        board,
        range(i + 1, min(i + Game.line_length, Game.height)),
        range(j - 1, max(j - Game.line_length, -1), -1),
        player
    )

    return length >= Game.line_length

def check(board, pos):
    if not board[pos]:
        return False

    return check_vertical(board, pos) \
        or check_horizontal(board, pos) \
        or check_main_diagonal(board, pos) \
        or check_side_diagonal(board, pos)


class Player(enum.IntEnum):
    NONE = 0
    BLACK = -1
    WHITE = 1

    def another(self):
        return Player(-self)

    def __repr__(self):
        if self == Player.BLACK:
            return 'black'
        elif self == Player.WHITE:
            return 'white'
        else:
            return 'none'

    def __str__(self):
        return self.__repr__()


class Game:
    width, height = 15, 15
    shape = (width, height)
    line_length = 5

    def __init__(self):
        self._result = Player.NONE
        self._player = Player.BLACK
        self._board = numpy.full(self.shape, Player.NONE, dtype=numpy.int8)
        self._positions = list()

    def __bool__(self):
        return self.result() == Player.NONE and \
            len(self._positions) < self.width * self.height

    def move_n(self):
        return len(self._positions)

    def player(self):
        return self._player

    def result(self):
        return self._result

    def board(self):
        return self._board

    def positions(self, player=Player.NONE):
        if not player:
            return self._positions

        begin = 0 if player == Player.BLACK else 1
        return self._positions[begin::2]

    def dumps(self):
        return ' '.join(map(to_move, self._positions))

    @staticmethod
    def loads(dump):
        game = Game()
        for pos in map(to_pos, dump.split()):
            game.move(pos)
        return game


    def is_posible_move(self, pos):
        return 0 <= pos[0] < self.height \
            and 0 <= pos[1] < self.width \
            and not self._board[pos]

    def move(self, pos):
        assert self.is_posible_move(pos), 'impossible pos: {pos}'.format(pos=pos)

        self._positions.append(pos)
        self._board[pos] = self._player

        if not self._result and check(self._board, pos):
            self._result = self._player
            return

        self._player = self._player.another()



def loop(game, black, white, max_move_n=Game.width*Game.height, timeout=None):
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        for agent in itertools.cycle([black, white]):
            if not game or game.move_n() >= max_move_n:
                break

            future = executor.submit(lambda game: agent.move(game), game)
            pos = to_pos(future.result(timeout=timeout))
            game.move(pos)

            yield game


def run(black, white, max_move_n=60, timeout=5):
    game = Game()

    try:
        for game in loop(game, black, white, max_move_n=max_move_n, timeout=timeout):
            logging.debug(game.dumps())

    except:
        logging.error('Error!', exc_info=True, stack_info=True)
        return game.player().another(), game.dumps()

    return game.result(), game.dumps()








import abc
import numpy
import subprocess


class Agent():
    # @abc.abstractmethod
    def move(game):
        '''Return next move'''

    # @abc.abstractmethod
    def name():
        '''return name of agent'''

class HumanAgent(Agent):
    def __init__(self, name='Human'):
        self._name = name

    def name(self):
        return self._name

    def move(self, game):
        return input()

class BackendAgent(Agent):
    def __init__(self, cmd, name, **kvargs):
        self._name = name
        self._backend = subprocess.Popen(
            cmd.split(),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            **kvargs
        )

    def name(self):
        return self._name

    def send_game_to_backend(self, game):
        data = game.dumps()
        self._backend.stdin.write(data.encode() + b'\n')
        self._backend.stdin.flush()

    def wait_for_backend_move(self):
        data = self._backend.stdout.readline().rstrip()
        return data.decode()

    def move(self, game):
        self.send_game_to_backend(game)
        return self.wait_for_backend_move()






import sys

def wait_for_game_update():
    if not sys.stdin.closed:
        game_dumps = sys.stdin.readline()
        history = []
        if game_dumps:
            for pos in game_dumps.split():
                history.append(pos)
            return Game.loads(game_dumps), history
        else:
            game_dumps_2 = sys.stdin.readline()
            if game_dumps_2:
                for pos in game_dumps.split():
                    history.append(pos)
                return Game.loads(game_dumps_2), history

    return None, None

def set_move(move, history):
    if sys.stdout.closed:
        return False
    sys.stdout.write(move + '\n')
    sys.stdout.flush()

    return True


import abc
import numpy
import logging
import random
import subprocess
import random
import tensorflow as tf
from keras.models import load_model

class CnnAgent_2(Agent):
    def __init__(self, color, name, model):
        self._name = name
        self.color = color
        self._model = model[0]
        self._graph = model[1]
        # self.model = load_model(color + '.h5')

    def name(self):
        return self._name

    def policy(self, game):
        with self._graph.as_default():
            predictions = self._model.predict(-game.board().reshape(1, 15, 15, 1))

        available = numpy.zeros((225, 1))
        positions = list_positions(game.board(), Player.NONE)
    
        for pos in positions:
            available[pos[0] * 15 + pos[1]] = 1
        arr = predictions + available

        code_move = numpy.argmax(arr)
        # print(self._name + ':', util.to_move([code_move // 15, code_move % 15]))
        return arr


def choose_random_move(board):
    positions = list_positions(board, Player.NONE)
    return to_move(random.choice(positions))


def choose_move(board, game):
    # rnd = random.randrange(0, 9)
    # if (rnd == 2):
    #     return choose_random_move(board)
    positions = list_positions(board, Player.NONE)
    model = load_model('comp.h5')
    model_graph = tf.get_default_graph()
    # model_graph_2 = tf.get_default_graph()
    # model_2 = load_model('colab.h5')
    SUMEKENOV = CnnAgent_2(color = 'black', name = 'SUMEKENOV', model = (model, model_graph))
    # SUMEKENOV_2 = CnnAgent_2(color = 'white', name = 'SUMEKENOV_2', model = (model_2, model_graph_2))
    arr = SUMEKENOV.policy(game)
    # arr_2 = SUMEKENOV_2.policy(game)
    arr_final = arr
    # print(arr_final)
    # print(arr_final)
    # print(arr_final.shape)
    mv = numpy.argmax(arr_final)
    tt = [mv // 15, mv % 15]
    return to_move(tt)

LOG_FORMAT = '%(levelname)s:%(asctime)s: dipper-{0}: %(message)s'.format(os.getpid())

def main():
    pid = os.getpid()
    logging.basicConfig(format=LOG_FORMAT, level=logging.DEBUG)
    # logging.debug("Start dummy backend...")

    try:
        while True:
            logging.debug("Wait for game update...")
            game, history = wait_for_game_update()

            if not game:
                logging.debug("Game is over!")
                return

            logging.debug('Game: %s', game.dumps())
            move = choose_move(game.board(), game)

            if not set_move(move, history):
                logging.error("Impossible set move!")
                return

            logging.debug('Reasonable move: %s', move)

    except:
        logging.error('Error!', exc_info=True, stack_info=True)


if __name__ == "__main__":
    main()






