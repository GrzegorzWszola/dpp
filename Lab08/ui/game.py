from dataclasses import dataclass
import math
from PyQt5.QtWidgets import QGraphicsPolygonItem, QGraphicsRectItem, QGraphicsView, QGraphicsScene
from PyQt5.QtGui import QColor, QPen, QBrush, QPolygonF
from PyQt5.QtCore import QPointF, QRectF, Qt

@dataclass
class MoveDTO:
    player: int
    row: int
    col: int

@dataclass
class PlayerDTO:
    id: int
    name: str
    is_ai: bool

@dataclass
class GameDTO:
    matrix: list
    current_player: PlayerDTO
    winner: PlayerDTO | None
    move: MoveDTO | None
    move_list: list[MoveDTO] = None

class GameUI:
    def __init__(self, graphics_view : QGraphicsView):
        self.view = graphics_view
        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)
        self.hex_items = {}
        self.on_hex_clicked = None

    def draw_board(self, game_matrix):
        self.scene.clear()
        self.hex_items = {}

        R = 30
        dx = R * math.sqrt(3)
        dy = R * 1.5
        offset_x, offset_y = 60, 60
        size = len(game_matrix)
        margin = 10

        board_w = (size - 1) * dx + 2 * R
        board_h = (size - 1) * dy + 2 * R
        shift = (size - 1) * dx / 2

        print(f"R={R} dx={dx:.1f} dy={dy:.1f} board_w={board_w:.1f} board_h={board_h:.1f} shift={shift:.1f}")

        bars = [
            (QPolygonF([  # góra - wyrównany do pierwszego rzędu
                QPointF(offset_x - R,           offset_y - R - margin),
                QPointF(offset_x - R + board_w, offset_y - R - margin),
                QPointF(offset_x - R + board_w, offset_y - R),
                QPointF(offset_x - R,           offset_y - R),
            ]), "#3B8BD4"),
            (QPolygonF([  # dół - wyrównany do ostatniego rzędu
                QPointF(offset_x - R + shift,            offset_y - R + board_h),
                QPointF(offset_x - R + shift + board_w,  offset_y - R + board_h),
                QPointF(offset_x - R + shift + board_w,  offset_y - R + board_h + margin),
                QPointF(offset_x - R + shift,            offset_y - R + board_h + margin),
            ]), "#3B8BD4"),
            (QPolygonF([  # lewo - skośny równoległobok
                QPointF(offset_x - R - margin,         offset_y - R),
                QPointF(offset_x - R,                  offset_y - R),
                QPointF(offset_x - R + shift,          offset_y - R + board_h),
                QPointF(offset_x - R + shift - margin, offset_y - R + board_h),
            ]), "#E24B4A"),
            (QPolygonF([  # prawo - skośny równoległobok
                QPointF(offset_x - R + board_w,                  offset_y - R),
                QPointF(offset_x - R + board_w + margin,          offset_y - R),
                QPointF(offset_x - R + shift + board_w + margin,  offset_y - R + board_h),
                QPointF(offset_x - R + shift + board_w,           offset_y - R + board_h),
            ]), "#E24B4A"),
        ]

        for polygon, color in bars:
            item = QGraphicsPolygonItem(polygon)
            item.setPen(QPen(Qt.NoPen))
            item.setBrush(QBrush(QColor(color)))
            self.scene.addItem(item)

        # Rysowanie hexagonow
        for row in range(size):
            for col in range(size):
                cx = offset_x + col * dx + row * dx / 2
                cy = offset_y + row * dy

                points = []
                for i in range(6):
                    angle = math.radians(60 * i - 30)
                    points.append(QPointF(cx + R * math.cos(angle),
                                        cy + R * math.sin(angle)))

                item = QGraphicsPolygonItem(QPolygonF(points))
                item.setPen(QPen(QColor("black"), 1.5))

                value = game_matrix[row][col]
                if value == 1:
                    item.setBrush(QBrush(QColor("#3B8BD4")))
                elif value == 2:
                    item.setBrush(QBrush(QColor("#E24B4A")))
                else:
                    item.setBrush(QBrush(QColor("#f0f0f0")))

                self.scene.addItem(item)
                self.hex_items[(row, col)] = item

        self.scene.mousePressEvent = self._on_scene_click

    def update_board(self, game_matrix):
        size = len(game_matrix)
        
        for row in range(size):
            for col in range(size):
                value = game_matrix[row][col]
                
                item = self.hex_items.get((row, col))
                
                if item:
                    if value == 1:
                        item.setBrush(QBrush(QColor("#3B8BD4")))
                    elif value == 2:
                        item.setBrush(QBrush(QColor("#E24B4A")))
                    else:
                        item.setBrush(QBrush(QColor("#f0f0f0")))

    def _on_scene_click(self, event):
        pos = event.scenePos()
        for (row, col), item in self.hex_items.items():
            if item.contains(pos):
                if self.on_hex_clicked:
                    self.on_hex_clicked(row, col)
                break
