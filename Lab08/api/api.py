from dataclasses import asdict

from flask import Flask, jsonify, request
from hex_engine.engine import Engine
from hex_engine.player import HumanPlayer, AIPlayer
from hex_engine.board import Move

class API:
    def __init__(self, host: str = "127.0.0.1", port: int = 5000, debug: bool = True):
        self.host = host
        self.port = port
        self.debug = debug
        self.app = Flask(__name__)
        self.game_lists = {}
        self.last_game_id = 0
        self._register_routes()

    def _register_routes(self):
        
        @self.app.get("/")
        def index():
            return jsonify({"message": "API działa!", "status": "ok"})
        
        @self.app.get("/get/id")
        def get_id():
            self.last_game_id += 1
            return jsonify({"id": self.last_game_id})
        
        @self.app.post("/game/<int:game_id>/start")
        def game_start(game_id):
            print("/game/start")
            body = request.get_json()

            if not game_id:
                return jsonify({"status": "error", "message": "Brak game_id"}), 400

            player_1 = HumanPlayer(id=body["player_1"]["id"], name=body["player_1"]["name"])
            if body["player_2"]["is_ai"]:
                player_2 = AIPlayer(id=body["player_2"]["id"], name=body["player_2"]["name"])
            else:
                player_2 = HumanPlayer(id=body["player_2"]["id"], name=body["player_2"]["name"])

            if body["move_list"]:
                move_list = [Move(move["player"], move["row"], move["col"]) for move in body["move_list"]]
            else:
                move_list = None

            try:
                engine = Engine(player_1=player_1,
                                     player_2=player_2,
                                     size=body["size"],
                                     starting_player_index=body["starting_player_index"],
                                     move_list=move_list)
                
                self.game_lists[game_id] = engine
            except Exception:
                return jsonify({"status": "NOK"})

            # Zwroc game state jezeli wszytsko jest ok
            return jsonify(engine.start_game())
        
        @self.app.post("/game/delete/<int:game_id>")
        def game_delete(game_id):
            game = self.game_lists.pop(game_id, None)
    
            if game:
                return jsonify({"status": "ok", "message": f"Gra {game_id} usunięta"})
            return jsonify({"status": "error", "message": "Nie ma takiej gry"}), 404
        
        @self.app.post("/move/<int:game_id>")
        def move(game_id):
            body = request.get_json()
            move = Move(body["player"], body["row"], body["col"])

            try:
                game = self.game_lists.get(game_id)
                if not game:
                    raise Exception
                
                response = game.move(row=move.row, col=move.col)
            except Exception:
                return jsonify({"status": "NOK"})
            
            return jsonify(response)
        
        @self.app.post("/move/<int:game_id>/ai")
        def move_ai(game_id):
            try:
                game = self.game_lists.get(game_id)
                if not game:
                    raise Exception
                
                response = game.move()
            except Exception:
                return jsonify({"status": "NOK"})
            
            return jsonify(response)
            

        

    def run(self):
        self.app.run(host=self.host, port=self.port, debug=self.debug)