import numpy as np
from .board import Move
import random

class Player:
    def __init__(self, id, name):
        self.id = id
        self.name = name
    
    def get_move(self):
        return
    
class HumanPlayer(Player):
    def __init__(self, id, name):
        super().__init__(id, name)
        self.next_move = None

    def get_move(self, board):
        # Zwracamy ruch, który został ustawiony przez GUI
        move = self.next_move
        self.next_move = None
        return move

class AIPlayer(Player):
    def get_move(self, board):
        free_spaces = np.argwhere(board.game_state_matrix == 0)
        if free_spaces.size > 0:
            row, col = random.choice(free_spaces)
            return Move(player=self.id, row=int(row), col=int(col))
        return None