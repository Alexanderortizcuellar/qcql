# eval_bar.py
import math
from PyQt5.QtCore import QEasingCurve, QPropertyAnimation, QRectF, Qt, pyqtProperty
from PyQt5.QtGui import QColor, QFont, QPainter, QLinearGradient
from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout
import sys

class EvalBar(QWidget):
    """
    Vertical chess evaluation bar.

    - setEngineScore({'type': 'cp', 'value': int})   # + = white better, - = black better
    - setEngineScore({'type': 'mate', 'value': int}) # +N white mates in N, -N black mates in N
    - setFlipped(True/False)                         # swap which color is on top/bottom (visual only)

    Visual model:
        self._white_share ∈ [0,1] denotes how much of the bar is white.
        Flipping swaps top/bottom colors but does not change _white_share.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._white_share = 0.5         # fraction of bar that is white (0=all black, 1=all white)
        self._flipped = False           # False: bottom=white, top=black ; True: bottom=black, top=white
        self._score_text = "+0.00"      # label shown; white POV by convention
        self._cp_scale = 300.0          # logistic scale (centipawns) controlling how fast it saturates
        self._anim = QPropertyAnimation(self, b"whiteShare")
        self._anim.setDuration(700)
        self._anim.setEasingCurve(QEasingCurve.InOutCubic)

        self.setFixedWidth(46)          # narrow, but a bit wider to accommodate text nicely

    # --- sizing -----------------------------------------------------------------
    def sizeHint(self):
        return self.minimumSizeHint()

    def minimumSizeHint(self):
        # Provide a sane default footprint
        from PyQt5.QtCore import QSize
        return QSize(46, 240)

    # --- property to animate ----------------------------------------------------
    def getWhiteShare(self):
        return self._white_share

    def setWhiteShare(self, v: float):
        v = 0.0 if v < 0.0 else 1.0 if v > 1.0 else v
        if abs(v - self._white_share) > 1e-6:
            self._white_share = v
            self.update()

    whiteShare = pyqtProperty(float, fget=getWhiteShare, fset=setWhiteShare)

    # --- public configuration ---------------------------------------------------
    def setAnimationDuration(self, ms: int):
        self._anim.setDuration(int(ms))

    def setCpScale(self, cp_scale: float):
        """Smaller values saturate faster (e.g., 250 for snappier bar)."""
        self._cp_scale = float(cp_scale)

    def setFlipped(self, flipped: bool):
        """Swap which color is on top/bottom (visual only)."""
        self._flipped = bool(flipped)
        self.update()

    # --- scoring API ------------------------------------------------------------
    def setEngineScore(self, score: dict):
        """
        Expected inputs:
          - {'type': 'cp', 'value': int}    # + => white better, - => black better
          - {'type': 'mate', 'value': int}  # +N => white mates in N, -N => black mates in N
        """
        stype = score.get("type")
        sval = int(score.get("value", 0))

        if stype == "cp":
            # Clamp and map with a smooth logistic so motion is pleasing
            cp = max(-2000, min(2000, sval))
            white_share = 1.0 / (1.0 + math.exp(-cp / self._cp_scale))
            self._score_text = f"{cp/100:+.2f}"  # show from white's POV, "+0.75" etc.
        elif stype == "mate":
            print(score)
            # "All inclined" to the mating color, as requested
            if sval > 0:
                white_share = 1.0
                self._score_text = f"+M{abs(sval)}"
            elif sval < 0:
                white_share = 0.0
                self._score_text = f"-M{abs(sval)}"
            else:
                white_share = 0.5
                self._score_text = "M0"
        else:
            white_share = 0.5
            self._score_text = "+0.00"

        self._animateTo(white_share)

    # --- animation helper -------------------------------------------------------
    def _animateTo(self, v: float):
        v = 0.0 if v < 0.0 else 1.0 if v > 1.0 else v
        self._anim.stop()
        self._anim.setStartValue(self._white_share)
        self._anim.setEndValue(v)
        self._anim.start()

    # --- painting ---------------------------------------------------------------
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, False)

        r = self.rect()
        total_h = r.height()
        white_h = total_h * self._white_share

        white_on_bottom = not self._flipped

        # Background (optional subtle glass gradient just to make it "nice")
        g = QLinearGradient(r.topLeft(), r.bottomLeft())
        g.setColorAt(0.00, QColor(255, 255, 255, 12))
        g.setColorAt(0.35, QColor(0, 0, 0, 10))
        g.setColorAt(0.65, QColor(0, 0, 0, 10))
        g.setColorAt(1.00, QColor(255, 255, 255, 12))
        p.fillRect(r, g)

        # Main split (crisp, solid colors)
        if white_on_bottom:
            # top = black, bottom = white
            black_h = total_h - white_h
            if black_h > 0:
                p.fillRect(QRectF(0, 0, r.width(), black_h), QColor("#000000"))
            if white_h > 0:
                p.fillRect(QRectF(0, total_h - white_h, r.width(), white_h), QColor("#FFFFFF"))
            split_y = int(black_h)
        else:
            # top = white, bottom = black
            if white_h > 0:
                p.fillRect(QRectF(0, 0, r.width(), white_h), QColor("#FFFFFF"))
            black_h = total_h - white_h
            if black_h > 0:
                p.fillRect(QRectF(0, white_h, r.width(), black_h), QColor("#000000"))
            split_y = int(white_h)

        # Divider line for clarity
        p.setPen(QColor(180, 180, 180, 140))
        p.drawLine(0, split_y, r.width(), split_y)

        # Border
        p.setPen(QColor(120, 120, 120))
        p.drawRect(r.adjusted(0, 0, -1, -1))

        # Score text: put it near the bottom edge; adjust color for contrast
        bottom_is_white = white_on_bottom
        text_color = QColor(30, 30, 30) if bottom_is_white else QColor(230, 230, 230)
        p.setPen(text_color)
        p.setFont(QFont("Arial", 9, QFont.DemiBold))
        p.drawText(r.adjusted(0, 0, 0, -2), Qt.AlignHCenter | Qt.AlignBottom, self._score_text)


# Demo
if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = QWidget()
    layout = QVBoxLayout(w)

    evalbar = EvalBar()
    layout.addWidget(evalbar)

    w.show()

    # Demo animation: fake engine scores
    import random

    from PyQt5.QtCore import QTimer

    def update_score():
        if random.random() > 0.2:
            score = {"type": "cp", "value": random.randint(-800, 800)}
        else:
            score = {"type": "mate", "value": random.choice([3, -3, 5, -5])}
        evalbar.setEngineScore(score)

    timer = QTimer()
    timer.timeout.connect(update_score)
    timer.start(2000)

    sys.exit(app.exec_())
