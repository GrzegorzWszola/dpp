from .player import *
from .board import *

class Engine:
    def __init__(self,
                 player_1 : Player,
                 player_2 : Player,
                 size = 6,
                 starting_player_index = 0,
                 move_list : list[Move] | None = None):
        self.player_1 = player_1
        self.player_2 = player_2
        self.players = [self.player_1, self.player_2]
        self.board = Board(size=size, move_list=move_list)
        if move_list is None:
            self.current_player = self.players[starting_player_index]
        else:
            last_player_id = move_list[-1].player
            next_index = last_player_id % 2
            self.current_player = self.players[next_index]
    
    def move(self, row=None, col=None):
        if isinstance(self.current_player, HumanPlayer):
            self.current_player.next_move = Move(self.current_player.id, row, col)

        current_move = self.current_player.get_move(self.board)

        if current_move is None:
            raise Exception("Brak wolnych pól")
 
        if not self.board.update_game_state(current_move):
            raise Exception("Błędny ruch")

        winner = None
        if self.check_winner(current_move):
            winner = self.current_player

        idx = self.players.index(self.current_player)
        self.current_player = self.players[1 - idx]

        return {
            "matrix": self.board.game_state_matrix.tolist(),
            "current_player": self.current_player,
            "winner": winner,
            "move": current_move
        }

    
    def check_winner(self, move : Move):
        player_id = move.player
        size = self.board.size
        matrix = self.board.game_state_matrix

        visited = set()
        stack = [(move.row, move.col)]
        touched = {0: False, 1: False}

        while stack:
            row, col = stack.pop()
            if (row, col) in visited:
                continue
            visited.add((row, col))

            if player_id == 1:
                if row == 0: touched[0] = True
                if row == size - 1: touched[1] = True
            else:
                if col == 0: touched[0] = True
                if col == size - 1: touched[1] = True

            if all(touched.values()):
                return True

            for dr, dc in [(-1,0),(1,0),(0,-1),(0,1),(-1,1),(1,-1)]:
                nr, nc = row + dr, col + dc
                if 0 <= nr < size and 0 <= nc < size:
                    if matrix[nr][nc] == player_id and (nr, nc) not in visited:
                        stack.append((nr, nc))

        return False
    
    def start_game(self):
        winner = None
        if self.board.move_list:
            last_move = self.board.move_list[-1]
            winner = self.check_winner(last_move)
        
        return {
            "matrix": self.board.game_state_matrix.tolist(),
            "current_player": self.current_player,
            "winner": winner,
            "move": self.board.move_list[-1] if self.board.move_list else None,
            "move_list": self.board.move_list
        }
