import numpy as np
from dataclasses import dataclass, asdict

@dataclass
class Move:
    player: int
    row: int
    col: int

class Board:
    def __init__(self, size, move_list):
        self.size = size
        if move_list is None:
            self.game_state_matrix = np.zeros((size, size))
            self.move_list = []
            self.score = 0
        else:
            self.game_state_matrix = self.generate_matrix_from_list(move_list)
            self.move_list = move_list

    def generate_matrix_from_list(self, move_list) -> np.ndarray:
        matrix = np.zeros((self.size, self.size), dtype=int)
        for move in move_list:
            if matrix[move.row][move.col] != 0:
                raise ValueError(f"Pole ({move.row}, {move.col}) już zajęte!")
            matrix[move.row][move.col] = move.player
        return matrix

    def update_game_state(self, move : Move) -> bool:
        if not (0 <= move.row < self.size and 0 <= move.col < self.size):
            return False
        if self.game_state_matrix[move.row][move.col] != 0:
            return False
        
        self.game_state_matrix[move.row, move.col] = move.player
        self.move_list.append(move)
        return True
    