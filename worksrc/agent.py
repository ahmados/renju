import abc
import numpy
import subprocess
import util
import renju
import random

class Agent(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def policy(game):
        '''Return probabilty matrix of possible actions'''

    @abc.abstractmethod
    def name():
        '''return name of agent'''


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
        positions = util.list_positions(game.board(), renju.Player.NONE)
    
        for pos in positions:
            available[pos[0] * 15 + pos[1]] = 1
        arr = predictions.T + available * 0.1

        code_move = numpy.argmax(arr)
        print(self._name + ':', util.to_move([code_move // 15, code_move % 15]))
        return arr
        
        
class DoubleAgent(Agent):
    def __init__(self, color, name, model, model_2):
        self._name = name
        self.color = color
        self._model = model[0]
        self._graph = model[1]
        self._model_2 = model_2[0]
        self._graph_2 = model_2[1]
        # self.model = load_model(color + '.h5')

    def name(self):
        return self._name

    def policy(self, game):
        with self._graph.as_default():
            predictions = self._model.predict(-game.board().reshape(1, 15, 15, 1))
        with self._graph_2.as_default():
            predictions_2 = self._model_2.predict(-game.board().reshape(1, 15, 15, 1))

        available = numpy.zeros((225, 1))
        positions = util.list_positions(game.board(), renju.Player.NONE)
    
        for pos in positions:
            available[pos[0] * 15 + pos[1]] = 1
        arr = predictions.T + predictions_2.T + available * 0.1

        code_move = numpy.argmax(arr)
        print(self._name + ':', util.to_move([code_move // 15, code_move % 15]))
        return arr
    
class CnnAgent(Agent):
    def __init__(self, color, name, model=None):
        if (model==None):
            self.flag = 0
        else:
            self.flag = 1
        self._name = name
        self.color = color
        if (self.flag):
            self._model = model[0]
            self._graph = model[1]
        # self.model = load_model(color + '.h5')

    def name(self):
        return self._name

    def policy(self, game):
        if (self.flag):
            newBoard = numpy.zeros((1, 15, 15, 1))
            for i in range(15):
                for j in range(15):
                    if (game.board()[i][j] == -1):
                        newBoard[0][i][j][0] = 0.5
                    if (game.board()[i][j] == 1):
                        newBoard[0][i][j][0] = 1
            with self._graph.as_default():
                predictions = self._model.predict(newBoard)

            available = numpy.zeros((225, 1))
            positions = util.list_positions(game.board(), renju.Player.NONE)

            for pos in positions:
                available[pos[0] * 15 + pos[1]] = 1
            
            arr = predictions.T * available

            code_move = numpy.argmax(arr)
#             maxmove = 0
#             move = 0
#             xy = 0
#             for m in predictions[0]:
#                 if ((m > maxmove) and (available[xy][0])):
#                     move = xy
#                     maxmove = m
#                 xy += 1
#             code_move = maxmove
            print(self._name + ':', util.to_move([code_move // 15, code_move % 15]))
            return arr
        else:
            move = input()
            pos = util.to_pos(move)

            probs = numpy.zeros(game.shape)
            probs[pos] = 1.0

            return probs

    def get_pos(self, game):
        if (self.flag):
            newBoard = numpy.zeros((1, 15, 15, 1))
            for i in range(15):
                for j in range(15):
                    if (game.board()[i][j] == -1):
                        newBoard[0][i][j][0] = 0.5
                    if (game.board()[i][j] == 1):
                        newBoard[0][i][j][0] = 1
            with self._graph.as_default():
                predictions = self._model.predict(newBoard)

            available = numpy.zeros((225, 1))
            positions = util.list_positions(game.board(), renju.Player.NONE)

            for pos in positions:
                available[pos[0] * 15 + pos[1]] = 1
            
            arr = predictions.T * available

            code_move = numpy.argmax(arr)
#             maxmove = 0
#             move = 0
#             xy = 0
#             for m in predictions[0]:
#                 if ((m > maxmove) and (available[xy][0])):
#                     move = xy
#                     maxmove = m
#                 xy += 1
#             code_move = maxmove
            print(self._name + ':', util.to_move([code_move // 15, code_move % 15]))
            return numpy.argmax(probs)
        else:
            move = input()
            pos = util.to_pos(move)

            probs = numpy.zeros(game.shape)
            probs[pos] = 1.0

            return numpy.argmax(probs)

    def is_human(self):
        return (not(self.flag))

class HumanAgent(Agent):
    def __init__(self, color, name='Human'):
        self._name = name
        self.color = color

    def name(self):
        return self._name

    def policy(self, game):
        move = input()
        pos = util.to_pos(move)

        probs = numpy.zeros(game.shape)
        probs[pos] = 1.0

        return probs

    def get_pos(self, game):
        return None

    def is_human(self):
        return True

class BackendAgent(Agent):
    def __init__(self, backend, name='BackendAgent', **kvargs):
        self._name = name
        self._backend = subprocess.Popen(
            backend.split(),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            **kvargs
        )

    def name(self):
        return self._name

    def send_game_to_backend(self, game):
        data = game.dumps().encode()
        self._backend.stdin.write(data + b'\n')
        self._backend.stdin.flush()

    def wait_for_backend_move(self):
        data = self._backend.stdout.readline().rstrip()
        return data.decode()

    def policy(self, game):
        self.send_game_to_backend(game)
        pos = util.to_pos(self.wait_for_backend_move())

        probs = numpy.zeros(game.shape)
        probs[pos] = 1.0

        return probs

class RandomAgent(Agent):
    def __init__(self, color, name='Human'):
        self._name = name
        self.color = color

    def name(self):
        return self._name

    def policy(self, game):
#         move = input()
#         pos = util.to_pos(move)

#         probs = numpy.zeros(game.shape)
#         probs[pos] = 1.0
        available = numpy.zeros((225, 1))
        positions = util.list_positions(game.board(), renju.Player.NONE)

        for pos in positions:
            available[pos[0] * 15 + pos[1]] = 1
        probs_0 = numpy.random.rand(225)
        probs = probs_0 + available
        return probs

    def get_pos(self, game):
        return None

    def is_human(self):
        return False