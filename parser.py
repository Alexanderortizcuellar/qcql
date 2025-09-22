"""
PGN Table Widget for PyQt5
- Input: raw PGN text (string)
- Output: a table of headers with sorting + simple filter
- Double-click emits a Python dict with the row's data (including full PGN)

Dependencies:
    pip install PyQt5 python-chess
"""

import io
from typing import List, Dict

from PyQt5 import QtCore, QtWidgets
import chess.pgn as chess_pgn


class PgnTableModel(QtCore.QAbstractTableModel):
    """
    Read-only table model for PGN headers.
    Columns: Event, Site, Date, Round, White, Black, Result, ECO, Moves (hidden in view)
    """

    HEADERS = [
        "Event",
        "Site",
        "Date",
        "Round",
        "White",
        "Black",
        "WhiteElo",
        "BlackElo",
        "Result",
        "ECO",
        "Moves",
    ]

    def __init__(self, rows: List[Dict[str, str]] = None, parent=None):
        super().__init__(parent)
        self._rows: List[Dict[str, str]] = rows or []

    # --- Required model overrides ---
    def rowCount(self, parent=QtCore.QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self._rows)

    def columnCount(self, parent=QtCore.QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self.HEADERS)

    def data(self, index: QtCore.QModelIndex, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None
        if role in (QtCore.Qt.DisplayRole, QtCore.Qt.EditRole):
            row = self._rows[index.row()]
            col_name = self.HEADERS[index.column()]
            return row.get(col_name, "")
        return None

    def headerData(
        self,
        section: int,
        orientation: QtCore.Qt.Orientation,
        role=QtCore.Qt.DisplayRole,
    ):
        if role != QtCore.Qt.DisplayRole:
            return None
        if orientation == QtCore.Qt.Horizontal:
            return self.HEADERS[section]
        return section + 1  # 1-based row number

    def flags(self, index: QtCore.QModelIndex):
        if not index.isValid():
            return QtCore.Qt.NoItemFlags
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    # --- Helpers ---
    def set_rows(self, rows: List[Dict[str, str]]):
        self.beginResetModel()
        self._rows = rows
        self.endResetModel()

    def row_dict(self, row_idx: int) -> Dict[str, str]:
        """Full dict for the given row, including extra keys like '_pgn'."""
        if 0 <= row_idx < len(self._rows):
            return self._rows[row_idx]
        return {}


class PgnTableWidget(QtWidgets.QWidget):
    """
    Composite widget:
      - QLineEdit filter
      - QTableView with QSortFilterProxyModel
      - Double-click emits gameSelected(dict)

    Public API:
      - load_pgn_text(pgn_text: str)
      - clear()
      - gameSelected(dict) signal
    """

    gameSelected = QtCore.pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)

        # --- UI ---
        self.filter_edit = QtWidgets.QLineEdit(self)
        self.filter_edit.setPlaceholderText("Filter (searches all columns)...")

        self.table = QtWidgets.QTableView(self)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.setSortingEnabled(True)

        self.info_label = QtWidgets.QLabel(self)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(1, 5, 1, 1)
        #layout.setSpacing(6)
        layout.addWidget(self.filter_edit)
        layout.addWidget(self.table, 1)
        layout.addWidget(self.info_label)

        # --- Model / Proxy ---
        self.model = PgnTableModel([])
        self.proxy = QtCore.QSortFilterProxyModel(self)
        self.proxy.setSourceModel(self.model)
        self.proxy.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.proxy.setFilterKeyColumn(-1)  # search across all columns
        self.table.setModel(self.proxy)

        # Hide Moves column by default
        self._hide_moves_column()

        # --- Signals ---
        self.filter_edit.textChanged.connect(self._on_filter_text_changed)
        self.table.doubleClicked.connect(self._on_double_clicked)

    # --- Public methods ---
    def load_pgn_text(self, pgn_text: str):
        """Parse raw PGN text and populate the table."""
        rows = self._parse_pgn_text_to_rows(pgn_text)
        self.model.set_rows(rows)
        # Re-hide Moves after model reset (safeguard)
        self._hide_moves_column()
        # Stretch columns to content minimally (no heavy styling)
        self.table.resizeColumnsToContents()

    def clear(self):
        """Clear the table."""
        self.model.set_rows([])

    def set_info_text(self, text: str):
        self.info_label.setText(text)

    # --- Internal slots / helpers ---
    def _hide_moves_column(self):
        try:
            moves_col = PgnTableModel.HEADERS.index("Moves")
            self.table.setColumnHidden(moves_col, True)
        except ValueError:
            pass

    def _on_filter_text_changed(self, text: str):
        # Use wildcard to get "contains" behavior
        # e.g., "Carlsen" matches "Magnus Carlsen" anywhere
        # Compatible across PyQt5 versions
        self.proxy.setFilterWildcard(f"*{text}*")

    def _on_double_clicked(self, proxy_index: QtCore.QModelIndex):
        if not proxy_index.isValid():
            return
        source_index = self.proxy.mapToSource(proxy_index)
        row_idx = source_index.row()
        row_data = self.model.row_dict(row_idx)

        # Build emitted payload: visible headers + extras
        payload = {h: row_data.get(h, "") for h in PgnTableModel.HEADERS}
        # Also include full raw PGN for consumer display
        payload["PGN"] = row_data.get("_pgn", "")
        self.gameSelected.emit(payload)

    # --- Parsing ---
    @staticmethod
    def _normalize_pgn_date(tag_value: str) -> str:
        """
        Normalize PGN Date tag 'YYYY.MM.DD' -> 'YYYY-MM-DD'.
        Keep unknown parts as '??' if present.
        """
        if not tag_value:
            return ""
        # Common PGN uses '.' separators; we just swap to '-' for lexicographic sorting.
        return tag_value.replace(".", "-")

    @staticmethod
    def _game_moves_san(game: chess_pgn.Game) -> str:
        """
        Generate a flat SAN string for mainline moves.
        Useful to keep moves around but hidden in the table.
        """
        board = game.board()
        sans = []
        for mv in game.mainline_moves():
            sans.append(board.san(mv))
            board.push(mv)
        return " ".join(sans)

    @staticmethod
    def _parse_pgn_text_to_rows(pgn_text: str) -> List[Dict[str, str]]:
        """
        Convert PGN text into a list of rows (dicts). Each row includes:
          - Event, Site, Date, Round, White, Black, Result, ECO, Moves
          - _pgn: the full PGN for the game
        """
        rows: List[Dict[str, str]] = []
        stream = io.StringIO(pgn_text)

        # Keep reading until no more games
        while True:
            game = chess_pgn.read_game(stream)
            if game is None:
                break

            H = game.headers  # chess.pgn.Headers
            if len(list(game.mainline_moves())) == 0:
                continue
            row = {
                "Event": H.get("Event", ""),
                "Site": H.get("Site", ""),
                "Date": PgnTableWidget._normalize_pgn_date(H.get("Date", "")),
                "Round": H.get("Round", ""),
                "White": H.get("White", ""),
                "Black": H.get("Black", ""),
                "WhiteElo": H.get("WhiteElo", ""),
                "BlackElo": H.get("BlackElo", ""),
                "Result": H.get("Result", ""),
                "ECO": H.get("ECO", ""),
                # Keep moves for later use (hidden column)
                "Moves": PgnTableWidget._game_moves_san(game),
                # Extras not shown as columns:
                "_pgn": str(game).strip(),
            }
            rows.append(row)
        return rows


class PGNWorker(QtCore.QThread):
    finished = QtCore.pyqtSignal(list)

    def __init__(self, parent=None, pgn_text: str = ""):
        self.pgn_text = pgn_text
        super().__init__(parent)

    def run(self):
        rows = self._parse_pgn_text_to_rows(self.pgn_text)
        self.finished.emit(rows)

    def _parse_pgn_text_to_rows(pgn_text: str) -> List[Dict[str, str]]:
        """
        Convert PGN text into a list of rows (dicts). Each row includes:
          - Event, Site, Date, Round, White, Black, Result, ECO, Moves
          - _pgn: the full PGN for the game
        """
        rows: List[Dict[str, str]] = []
        stream = io.StringIO(pgn_text)

        # Keep reading until no more games
        while True:
            game = chess_pgn.read_game(stream)
            if game is None:
                break

            H = game.headers  # chess.pgn.Headers
            if len(list(game.mainline_moves())) == 0:
                continue
            row = {
                "Event": H.get("Event", ""),
                "Site": H.get("Site", ""),
                "Date": PgnTableWidget._normalize_pgn_date(H.get("Date", "")),
                "Round": H.get("Round", ""),
                "White": H.get("White", ""),
                "Black": H.get("Black", ""),
                "WhiteElo": H.get("WhiteElo", ""),
                "BlackElo": H.get("BlackElo", ""),
                "Result": H.get("Result", ""),
                "ECO": H.get("ECO", ""),
                # Keep moves for later use (hidden column)
                "Moves": PgnTableWidget._game_moves_san(game),
                # Extras not shown as columns:
                "_pgn": str(game).strip(),
            }
            rows.append(row)

        return rows


# --- Minimal manual test runner (optional) ---
if __name__ == "__main__":
    import sys

    SAMPLE_PGN = """
[Event "Test Open"]
[Site "Somewhere"]
[Date "2021.??.??"]
[Round "3"]
[White "Alice"]
[Black "Bob"]
[Result "1/2-1/2"]

1.d4 d5 2.c4 e6 3.Nc3 Nf6 4.Bg5 Be7 5.e3 O-O 6.Nf3 Nbd7 1/2-1/2
"""

    app = QtWidgets.QApplication(sys.argv)
    w = PgnTableWidget()
    w.resize(1000, 400)

    # Connect the signal to show what gets emitted
    def on_game_selected(game_dict: Dict[str, str]):
        print("\n--- gameSelected payload ---")
        for k, v in game_dict.items():
            if k == "PGN":
                print(f"{k}: (full PGN, {len(v)} chars)")
            else:
                print(f"{k}: {v}")

    w.gameSelected.connect(on_game_selected)
    w.load_pgn_text(SAMPLE_PGN)
    w.show()
    sys.exit(app.exec_())
