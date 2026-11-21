"""Exercise actual game-loop events with rendering mocked out."""
import contextlib
import io
from pathlib import Path
import random
import sys
import types
import unittest
from unittest.mock import MagicMock, patch
import numpy as np


def play(filename, board, columns, turn=0):
    pygame = MagicMock()
    pygame.QUIT, pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN = 1, 2, 3
    events = [types.SimpleNamespace(type=3, pos=(col * 100 + 10, 100)) for col in columns]
    pygame.event.get.side_effect = [events, [types.SimpleNamespace(type=1)]]
    namespace = {'__name__': '__test__'}
    source = Path(__file__).with_name(filename).read_text()
    with patch.dict(sys.modules, {'pygame': pygame}), patch.object(np, 'zeros', return_value=board), \
            patch.object(random, 'randint', return_value=turn), contextlib.redirect_stdout(io.StringIO()):
        try:
            exec(compile(source, filename, 'exec'), namespace)
        except SystemExit:
            pass
    return namespace


class MoveTests(unittest.TestCase):
    def test_full_column_does_not_consume_turn(self):
        board = np.zeros((6, 7))
        board[:, 0] = 1
        state = play('connect4.py', board, [0, 1])
        self.assertEqual(board[0, 1], 1)
        self.assertEqual(state['turn'], 1)

    def test_last_move_draw_in_both_modes(self):
        for filename in ('connect4.py', 'connect4_with_ai.py'):
            with self.subTest(filename=filename):
                board = np.array([[1, 1, 2, 2, 1, 1, 2], [2, 2, 1, 1, 2, 2, 1]] * 3)
                board[5, 2] = 0
                state = play(filename, board, [2])
                self.assertTrue(state['game_over'])
                self.assertFalse(state['winning_move'](board, 1))
                self.assertFalse(state['winning_move'](board, 2))
                for col in (-1, 7, None):
                    self.assertFalse(state['is_valid_location'](board, col))

    def test_ai_final_move_draw(self):
        board = np.array([[1, 1, 2, 2, 1, 1, 2], [2, 2, 1, 1, 2, 2, 1]] * 3)
        board[5, 0] = 0
        state = play('connect4_with_ai.py', board, [], turn=1)
        self.assertTrue(state['game_over'])
        self.assertEqual(board[5, 0], 2)


if __name__ == '__main__':
    unittest.main()
