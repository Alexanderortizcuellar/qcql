from PyQt5.QtWidgets import (
    QApplication,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QHBoxLayout,
    QDialog,
    QFileDialog,
)
from PyQt5.QtCore import QUrl, QSize, Qt
from PyQt5.QtGui import QFont
import re
import sys
from io import StringIO
import chess.pgn
from chesboard import ChessBoard
from movemanager import MoveManager
import qtawesome as qta

from pgn_browser import PGNBrowser as PGN_Browser
from viewer import PGNHeaderWidget
from analysis_widget import AnalysisWidget
from bar import EvalBar
from engine import ChessEngine

text = """[Event "?"]
[Site "?"]
[Date "????.??.??"]
[Round "?"]
[White "?"]
[Black "?"]
[Result "*"]
[Link "https://www.chess.com/analysis/game/pgn/4HSfSCP8L6/analysis"]

1. e4 { nada to show } e5 2. Nf3 Nc6 3. Bc4 Nf6 4. d3 (4. Ng5 d5 5. exd5 Nxd5 (5... Na5 6. Bb5+
c6 7. dxc6 bxc6 8. Bd3 (8. Be2 h6 9. Nf3) 8... Nd5) 6. Nxf7 Kxf7 7. Qf3+ Ke6 8.
Nc3 Nb4 9. O-O c6) 4... Bc5 5. O-O *"""


class VariationsDialog(QDialog):
    def __init__(self, variations: dict):
        super().__init__()
        self.setWindowTitle("Variations")
        self.setGeometry(100, 100, 300, 200)

        layout = QVBoxLayout()
        self.setLayout(layout)
        self.selected_index = None

        for index, item in variations.items():
            button = QPushButton(f"{item['san']}")
            button.setFont(QFont("Noto Sans", 16))
            button.clicked.connect(
                lambda _, i=index, m=item["san"]: self.select_variation(m, i)
            )
            layout.addWidget(button)

    def select_variation(self, _, index):
        # Handle the selection of a variation
        self.selected_index = index
        self.accept()


class PGNBrowser(QWidget):
    def __init__(self, game_info: dict, html_style=False):
        super().__init__()
        self.setWindowTitle("Chess App")

        # Create a central widget

        # Create a vertical layout
        layout = QHBoxLayout()

        self.setLayout(layout)
        self.move_manager = MoveManager(game_info.get("PGN"))
        self.set_html_style(html_style)
        chess_bar_layout = QHBoxLayout()
        chess_bar_layout.setContentsMargins(0, 0, 0, 0)
        self.bar = EvalBar()
        layout.addLayout(chess_bar_layout)
        self.chessboard = ChessBoard(self, size=650)
        chess_bar_layout.addWidget(self.bar)
        chess_bar_layout.addWidget(self.chessboard)
        pgn_area_layout = QVBoxLayout()
        layout.addLayout(pgn_area_layout)
        self.analysis_widget = AnalysisWidget(self)
        self.analysis_widget.setFixedHeight(100)
        self.header_widget = PGNHeaderWidget(game_info)
        self.browser = PGN_Browser(self, self.move_manager)

        self.navigation_layout = QHBoxLayout()
        self.jump_to_start_button = QPushButton()
        self.jump_to_start_button.setCursor(Qt.PointingHandCursor)
        icon = qta.icon("ph.caret-double-left-fill")
        self.jump_to_start_button.setIconSize(QSize(32, 32))
        self.jump_to_start_button.setIcon(icon)
        self.backward_button = QPushButton()
        self.backward_button.setCursor(Qt.PointingHandCursor)
        icon = qta.icon("mdi.skip-previous")
        self.backward_button.setIconSize(QSize(32, 32))
        self.backward_button.setIcon(icon)
        self.backward_button.setShortcut("Left")
        self.forward_button = QPushButton()
        icon = qta.icon("mdi.skip-next")
        self.forward_button.setIconSize(QSize(32, 32))
        self.forward_button.setIcon(icon)
        self.forward_button.setCursor(Qt.PointingHandCursor)
        self.forward_button.setShortcut("Right")
        self.jump_to_end_button = QPushButton()
        self.jump_to_end_button.setCursor(Qt.PointingHandCursor)
        icon = qta.icon("ph.caret-double-right-fill")
        self.jump_to_end_button.setIconSize(QSize(32, 32))
        self.jump_to_end_button.setIcon(icon)
        flip_button = QPushButton()
        flip_button.setCursor(Qt.PointingHandCursor)
        icon = qta.icon("ei.refresh")
        flip_button.setIconSize(QSize(32, 32))
        flip_button.setIcon(icon)
        self.navigation_layout.addWidget(self.jump_to_start_button)
        self.navigation_layout.addWidget(self.backward_button)
        self.navigation_layout.addWidget(self.forward_button)
        self.navigation_layout.addWidget(self.jump_to_end_button)
        self.navigation_layout.addWidget(flip_button)
        actions_layout = QHBoxLayout()
        save_pgn_btn = QPushButton()
        save_pgn_btn.setToolTip("Save Pgn")
        save_pgn_btn.setIcon(qta.icon("fa5s.save"))
        save_pgn_btn.setIconSize(QSize(32, 32))
        save_pgn_btn.setCursor(Qt.PointingHandCursor)
        copy_pgn_btn = QPushButton()
        copy_pgn_btn.setToolTip("Copy Pgn")
        copy_pgn_btn.setIcon(qta.icon("fa5s.copy"))
        copy_pgn_btn.setIconSize(QSize(32, 32))
        copy_pgn_btn.setCursor(Qt.PointingHandCursor)
        actions_layout.addWidget(save_pgn_btn)
        actions_layout.addWidget(copy_pgn_btn)
        pgn_area_layout.addWidget(self.analysis_widget)
        pgn_area_layout.addWidget(self.header_widget)
        pgn_area_layout.addWidget(self.browser)
        pgn_area_layout.addLayout(self.navigation_layout)
        pgn_area_layout.addLayout(actions_layout)

        self.engine = ChessEngine("stockfish", self)
        self.display_pgn()
        self.analysis_widget.check_analysis.toggled.connect(self.toggle_analysis)
        self.chessboard.moveMade.connect(self.handle_move)
        # self.chessboard.GameOver.connect(self.on_game_over)
        self.forward_button.clicked.connect(self.forward)
        self.backward_button.clicked.connect(self.backward)
        self.jump_to_start_button.clicked.connect(self.jump_to_start)
        self.jump_to_end_button.clicked.connect(self.jump_to_end)
        flip_button.clicked.connect(self.flip_board)
        save_pgn_btn.clicked.connect(self.save_pgn)
        copy_pgn_btn.clicked.connect(
            lambda _: self.copy_text(self.move_manager.get_pgn())
        )
        self.move_manager.pgnChanged.connect(lambda _: self.display_pgn())
        self.browser.anchorClicked.connect(self.on_anchor_clicked)
        self.chessboard.fenChanged.connect(self.send_position)
        self.engine.cpScoreFound.connect(self.get_score)
        self.engine.depthChanged.connect(
            lambda depth: self.analysis_widget.set_depth(f"depth={depth}")
        )
        self.engine.lineFound.connect(self.on_lines_found)
        self.engine.mateFound.connect(self.get_mate)

    def flip_board(self):
        self.chessboard.flip()
        self.bar.setFlipped(not self.bar._flipped)

    def on_anchor_clicked(self, url: QUrl):
        match = re.match(r"move\((\d+)\)", url.toString())
        if match:
            idx = int(match.group(1))
            self.move_manager.jump_to(idx)
            fen = self.move_manager.current_node.board().fen()
            self.chessboard.update_board(fen, self.move_manager.current_node.move)

    def handle_move(self, move_uci):
        """Handle a move made on the chessboard."""
        self.move_manager.make_move(move_uci)
        # self.chessboard.update_board(self.move_manager.get_board())
        self.display_pgn()

    def forward(self):
        """Go forward in the move variations."""
        if self.move_manager.has_variations():
            variations = self.move_manager.get_current_node_variations()
            if len(variations) > 1:
                dialog = VariationsDialog(variations)
                if dialog.exec_() != QDialog.Accepted:
                    return
                if dialog.selected_index is None:
                    return
                self.move_manager.redo(dialog.selected_index)
            else:
                self.move_manager.redo()
            self.chessboard.update_board(
                self.move_manager.get_board().fen(), self.move_manager.current_node.move
            )
            self.display_pgn()

    def backward(self):
        """Go backward in the move variations."""
        self.move_manager.undo()
        self.chessboard.update_board(
            self.move_manager.get_board().fen(), self.move_manager.current_node.move
        )
        self.display_pgn()

    def jump_to_start(self):
        self.move_manager.jump_to_start()
        self.chessboard.update_board(self.move_manager.get_board().fen())
        self.display_pgn()

    def set_html_style(self, html_style: bool):
        """Set the HTML style to either light or dark. (True for dark, False for light)"""
        self.move_manager.change_html_style(html_style)

    def jump_to_end(self):
        self.move_manager.jump_to_end()
        self.chessboard.update_board(
            self.move_manager.get_board().fen(), self.move_manager.current_node.move
        )
        self.display_pgn()

    def display_pgn(self):
        """Display the current PGN in the text browser."""
        html = self.move_manager.html
        self.browser.setHtml(html)

    """ def on_game_over(self):
        self.engine.send_command("stop")
     """

    def send_position(self):
        self.engine.send_command("stop")
        self.engine.send_position(self.chessboard.fen(), "depth", options={"depth": 60})

    def show_variations(self):
        variations = self.move_manager.get_current_node_variations()
        print(self.move_manager.current_node.move, variations)

    def normalize_score(self, score):
        score = max(-10, min(10, score))
        return int((score + 10) / 20 * 1000)

    def on_lines_found(self, lines: list[str]):
        board = chess.Board(self.chessboard.fen())
        if len(lines) >= 1:
            move1_uci = lines[0]
            move1 = chess.Move.from_uci(move1_uci)
            if move1 not in board.legal_moves:
                return
        header = f'[FEN "{self.chessboard.fen()}"]\n\n'
        pgn = header + " ".join(lines)
        move1_uci = lines[0]
        move1 = chess.Move.from_uci(move1_uci)
        game = chess.pgn.read_game(StringIO(pgn))
        self.analysis_widget.set_line_text(str(game.mainline_moves()))

    def get_score(self, score: int):
        if self.chessboard.turn:
            if score < 0:
                score = score
            else:
                score = score
        else:
            if score > 0:
                score = -score
            else:
                score = abs(score)
        self.bar.setEngineScore({"type": "cp", "value": score})
        self.bar.setToolTip(str(score / 100))
        self.analysis_widget.set_score(str(score / 100))
    
    def get_mate(self, matein: int):
        if matein > 0:
            if self.chessboard.turn:
                self.bar.setEngineScore({"type": "mate", "value": matein})
            else:
                self.bar.setEngineScore({"type": "mate", "value": -matein})
            self.bar.setToolTip(f"M{matein}")
            self.analysis_widget.set_score(f"M{matein}")

    def toggle_analysis(self, toggle: bool):
        if toggle:
            if self.engine.is_running():
                self.bar.show()
                self.send_position()
                return
            self.engine.start()
            self.bar.show()
            self.send_position()
        else:
            self.engine.send_command("stop")
            self.bar.hide()

    def save_pgn(self):
        file, ok = QFileDialog.getSaveFileName(
            self, "Save", ".", "Pgn Files (*.pgn);;All (*)"
        )
        if ok:
            with open(file) as f:
                f.write(self.move_manager.get_pgn())

    def copy_text(self, text: str):
        clipboard = QApplication.clipboard()
        clipboard.setText(text)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PGNBrowser(
        {
            "PGN": text,
            "White": "Magnus Carlsen",
            "Black": "Bobby Fischer",
            "Result": "1-0",
        }
    )
    window.show()
    sys.exit(app.exec_())
