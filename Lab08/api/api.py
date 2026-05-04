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
        self.engine = None
        self.app = Flask(__name__)
        self._register_routes()

    def _register_routes(self):
        
        @self.app.get("/")
        def index():
            return jsonify({"message": "API działa!", "status": "ok"})
        
        @self.app.post("/game/start")
        def game_start():
            print("/game/start")
            body = request.get_json()
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
                self.engine = Engine(player_1=player_1,
                                     player_2=player_2,
                                     size=body["size"],
                                     starting_player_index=body["starting_player_index"],
                                     move_list=move_list)
            except Exception:
                return jsonify({"status": "NOK"})

            # Zwroc game state jezeli wszytsko jest ok
            return jsonify(self.engine.start_game())
        
        @self.app.post("/move")
        def move():
            body = request.get_json()
            move = Move(body["player"], body["row"], body["col"])

            try:
                response = self.engine.move(row=move.row, col=move.col)
            except Exception:
                return jsonify({"status": "NOK"})
            
            return jsonify(response)
        
        @self.app.post("/move/ai")
        def move_ai():
            try:
                response = self.engine.move()
            except Exception:
                return jsonify({"status": "NOK"})
            
            return jsonify(response)
            

        

    def run(self):
        self.app.run(host=self.host, port=self.port, debug=self.debug)