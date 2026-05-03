from dataclasses import asdict
import json
import os

from hex_engine.board import Move
from hex_engine.player import AIPlayer, HumanPlayer

from .mainWindow import Ui_MainWindow
from .game import GameDTO, GameUI
from hex_engine.engine import Engine
from PyQt5.QtWidgets import QFileDialog, QMainWindow, QMessageBox

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.engine = None
        self.move_dtos = None
        self.game: GameDTO | None = None
        self.game_ui = GameUI(self.ui.graphicsView)
        self.size = 0
        self._connect_buttons()
        self.ui.radioPlayer1.setChecked(True)

    def _connect_buttons(self):
        self.ui.startButton.clicked.connect(self.on_start)
        self.ui.loadConfigButton.clicked.connect(self.on_load)
        self.ui.saveGameState.clicked.connect(self.save_state)
        self.ui.resetButton.clicked.connect(self.reset)

    def on_start(self):
        self.game_ui.view.setEnabled(True)
        player_1_name = self.ui.nameInput1.text()
        player_2_name = self.ui.nameInput2.text()
        if not player_1_name.strip() or not player_2_name.strip():
            QMessageBox.warning(self, "Błąd", "Podaj imię gracza 1 lub 2")
            return
        
        player_1 = HumanPlayer(id=1, name=player_1_name)
        if self.ui.witchComputerCheckbox.isChecked():
            player_2 = AIPlayer(id=2, name=player_2_name)
        else:
            player_2 = HumanPlayer(id=2, name=player_2_name)

        starting_player_index = 0 if self.ui.radioPlayer1.isChecked() else 1

        if self.move_dtos:
            move_list = self.move_dtos
            selected_size = self.size
        else:
            move_list = None
            selected_size = self.ui.sizeSlider.value()

        try:
            self.engine = Engine(player_1=player_1,
                                player_2=player_2,
                                size=selected_size,
                                starting_player_index=starting_player_index,
                                move_list=move_list)
        except ValueError as e:
            QMessageBox.warning(self, "Błąd wczytywania stanu", str(e))
            return
        
        result = self.engine.start_game()
        self.game = GameDTO(**result)
        print(asdict(self.game))

        self.game_ui.on_hex_clicked = self.on_cell_clicked
        self.game_ui.draw_board(self.game.matrix)

    def on_load(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Wczytaj stan gry",
            "",
            "JSON (*.json)"
        )
        
        if path:
            self.size, self.move_dtos = self.load_state(path)

    def load_state(self, path: str) -> list[Move]:
        self.ui.label_input_path.setText(os.path.basename(path))
        with open(path) as f:
            data = json.load(f)

        size = data["size"]
        moves = [Move(player=m["player"], row=m["row"], col=m["col"]) for m in data["moves"]]
        return size, moves

    def on_cell_clicked(self, row, col):
        try:
            result_dict = self.engine.move(row, col)
            self.update_game_state(result_dict)

            while self.game.winner is None and not isinstance(self.game.current_player, HumanPlayer):
                result_ai = self.engine.move()
                self.update_game_state(result_ai)

        except Exception as e:
            print(f"Błąd gry: {e}")

    def update_game_state(self, result_dict):
        current_history = list(self.game.move_list) if self.game and self.game.move_list else []
        self.game = GameDTO(**result_dict)
        
        if self.game.move:
            is_duplicate = (
                len(current_history) > 0 and 
                current_history[-1].row == self.game.move.row and 
                current_history[-1].col == self.game.move.col and
                current_history[-1].player == self.game.move.player
            )
            
            if not is_duplicate:
                current_history.append(self.game.move)
        self.game.move_list = current_history
        
        self.game_ui.update_board(self.game.matrix)
        if self.game.winner is not None:
            QMessageBox.information(self, "Koniec gry", f"Wygrał gracz: {self.game.winner.name} (ID: {self.game.winner.id})")
            self.game_ui.view.setEnabled(False)

    def save_state(self):
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getSaveFileName(
            self, "Zapisz stan gry", "", "JSON Files (*.json);;All Files (*)", options=options
        )

        if filename:
            if not filename.endswith('.json'):
                filename += '.json'
            
            self.save_game_to_json(filename)

    def save_game_to_json(self, filename="savegame.json"):
        size = len(self.game.matrix) if self.game else 0
        moves_strings = []
        if self.game and self.game.move_list:
            for m in self.game.move_list:
                move_str = f'{{"player": {m.player}, "row": {m.row}, "col": {m.col}}}'
                moves_strings.append(move_str)
        
        moves_joined = ",\n        ".join(moves_strings)
        json_content = f'{{\n    "size": {size},\n    "moves": [\n        {moves_joined}\n    ]\n}}'
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(json_content)
            print(f"Gra została zapisana do {filename}")
        except Exception as e:
            print(f"Błąd podczas zapisu: {e}")

    def reset(self):
        self.move_dtos = None
        self.size = 0
        self.ui.label_input_path.setText("")
        QMessageBox.information(self, "Reset", "Wczytany plik został anulowany. Gra wystartuje z czystą planszą.")