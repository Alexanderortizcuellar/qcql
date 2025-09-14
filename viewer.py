from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget


class PGNHeaderWidget(QWidget):
    def __init__(self, header_dict: dict):
        super().__init__()
        self.setWindowTitle("PGN Header Viewer")
        self.setStyleSheet(
            """
            QLabel { font-family: Segoe UI, sans-serif; font-size: 14px; }
            .header-box { border: 1px solid #ccc; border-radius: 6px; padding: 8px; background: #f9f9f9; }
            .title { font-weight: bold; }
        """
        )

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        # Extract values safely
        white = header_dict.get("White", "Unknown")
        black = header_dict.get("Black", "Unknown")
        white_elo = header_dict.get("WhiteElo", "")
        black_elo = header_dict.get("BlackElo", "")
        result = header_dict.get("Result", "")
        event = header_dict.get("Event", "Unknown Event")
        date = header_dict.get("Date", "")

        # Format names with Elo if available
        white_display = f"{white} ({white_elo})" if white_elo else white
        black_display = f"{black} ({black_elo})" if black_elo else black

        # First row: [ White (Elo) | Result | Black (Elo) ]
        row1 = QHBoxLayout()
        row1.setSpacing(20)
        white_display_lbl = QLabel(white_display)
        white_display_lbl.setAlignment(Qt.AlignLeft)
        row1.addWidget(white_display_lbl)

        lbl_result = QLabel(result)
        lbl_result.setAlignment(Qt.AlignCenter)
        lbl_result.setObjectName("title")
        row1.addWidget(lbl_result)
        black_display_lbl = QLabel(black_display)
        black_display_lbl.setAlignment(Qt.AlignRight)
        row1.addWidget(black_display_lbl)

        # Second row: [ Event | Date ]
        label_event = QLabel(f"{event} {date}")
        label_event.setAlignment(Qt.AlignCenter)
        for label in (white_display_lbl, black_display_lbl, label_event, lbl_result):
            label.setStyleSheet("font-weight: bold;font-size: 16px;")
        # Wrap in frame for styling
        frame = QFrame()
        frame.setObjectName("header-box")
        frame_layout = QVBoxLayout(frame)
        frame_layout.addLayout(row1)
        frame_layout.addWidget(label_event)

        layout.addWidget(frame)


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    headers = {
        "White": "Magnus Carlsen",
        "Black": "Bobby Fischer",
        "Result": "1-0",
        "Date": "2023.03.31",
        "Event": "Test Event",
        "WhiteElo": "3000",
        "BlackElo": "2900",
    }
    window = PGNHeaderWidget(headers)
    window.show()
    sys.exit(app.exec_())