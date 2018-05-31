import logging
import random

import backend
import renju
import util


def choose_move(board):
    positions = util.list_positions(board, renju.Player.NONE)
    model = load_model('modelusual.h5')
    model_graph = tf.get_default_graph()
    model_graph_2 = tf.get_default_graph()
    model_2 = load_model('modelsuper.h5')
    SUMEKENOV = CnnAgent(color = 'black', name = 'SUMEKENOV', model = (model, model_graph))
    SUMEKENOV_2 = CnnAgent(color = 'black', name = 'SUMEKENOV_2', model = (model_2, model_graph_2))
    arr = SUMEKENOV.policy(game)
    arr_2 = SUMEKENOV_2.policy(game)
    arr_final = arr + arr_2
    mv = numpy.argmax(arr_final, axis=1)
    return util.to_move(mv)

def main():
    logging.basicConfig(filename='dummy.log', level=logging.DEBUG)
    logging.debug("Start dummy backend...")
    
    try:
        while True:
            logging.debug("Wait for game update...")
            game = backend.wait_for_game_update()
            logging.debug('Board:\n' + str(game.board()))

            move = choose_random_move(game.board())
            backend.move(move)
            logging.debug('make move: ' + move)
    except:
        logging.error('Error!', exc_info=True, stack_info=True)


if __name__ == "__main__":
    main()
