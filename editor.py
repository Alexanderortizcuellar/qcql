from PyQt5.QtCore import Qt, QRegularExpression, QSize, QRect
from PyQt5.QtGui import (
    QSyntaxHighlighter,
    QTextCharFormat,
    QColor,
    QFont,
    QPainter,
)
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QPlainTextEdit,
    QCompleter,
    QMessageBox,
    QTextEdit,
    QApplication,
)
from sqlfmt.core import format as sqlfmt_format
import sys
import re


# ===================================================
#                Syntax Highlighter
# ===================================================
class SqlHighlighter(QSyntaxHighlighter):
    """
    SQL Syntax Highlighter supporting:
    - Keywords, functions
    - Strings (single & double)
    - Numbers
    - Operators & punctuation
    - Single-line and multi-line comments
    Theme-aware colors.
    """

    def __init__(self, document, theme: str = "light"):
        super().__init__(document)
        self.rules: list[tuple[QRegularExpression, QTextCharFormat]] = []
        self.commentStart = QRegularExpression(r"/\*")
        self.commentEnd = QRegularExpression(r"\*/")
        self.multiLineCommentFormat = QTextCharFormat()
        self.multiLineCommentFormat.setForeground(QColor("#6A9955"))  # green-ish

        self._keyword_regex = None
        self._function_regex = None

        self._init_formats(theme)
        self._compile_rules()

    # ---------- Theme handling ----------
    def _init_formats(self, theme: str):
        # VS Code-ish palette that works in both themes
        # Adjusted foreground colors based on theme to ensure contrast
        def color(hex_light, hex_dark):
            return QColor(hex_dark if theme == "dark" else hex_light)

        self.fmt_keyword = QTextCharFormat()
        self.fmt_keyword.setForeground(color("#0B5CAD", "#4FC1FF"))
        self.fmt_keyword.setFontWeight(QFont.Bold)

        self.fmt_function = QTextCharFormat()
        self.fmt_function.setForeground(color("#9C27B0", "#C792EA"))
        self.fmt_function.setFontWeight(QFont.DemiBold)

        self.fmt_string = QTextCharFormat()
        self.fmt_string.setForeground(color("#228B22", "#CE9178"))

        self.fmt_number = QTextCharFormat()
        self.fmt_number.setForeground(color("#B22222", "#D19A66"))

        self.fmt_comment = QTextCharFormat()
        self.fmt_comment.setForeground(color("#6B7280", "#6A9955"))  # gray/green

        self.fmt_operator = QTextCharFormat()
        self.fmt_operator.setForeground(color("#8B008B", "#C586C0"))

        self.fmt_piece_designator = QTextCharFormat()
        self.fmt_piece_designator.setForeground(color("#950BB1", "#2FDBD3"))
        self.fmt_piece_designator.setFontWeight(QFont.Bold)

    def setTheme(self, theme: str):
        """Call this when toggling theme; then rehighlight."""
        self._init_formats(theme)
        self.rules.clear()
        self._compile_rules()
        self.rehighlight()

    # ---------- Patterns ----------
    def _compile_rules(self):
        keywords = [
            "abs",
            "Aa",
            "and",
            "ascii",
            "assert",
            "atomic",
            "between",
            "black",
            "btm",
            "castle",
            "check",
            "child",
            "child",
            "comment",
            "connectedpawns",
            "consecutivemoves",
            "countmoves",
            "currentmove",
            "currentposition",
            "currenttransform",
            "dark",
            "date",
            "depth",
            "dictionary",
            "distance",
            "doubledpawns",
            "down",
            "echo",
            "eco",
            "elo",
            "event",
            "eventdate",
            "false",
            "fen",
            "file",
            "find",
            "flip",
            "flipcolor",
            "fliphorizontal",
            "flipvertical",
            "from",
            "function",
            "gamenumber",
            "hascomment",
            "idealmate",
            "idealstalemate",
            "if",
            "in",
            "in",
            "indexof",
            "initial",
            "initialposition",
            "int",
            "isbound",
            "isolatedpawns",
            "isunbound",
            "lastgamenumber",
            "lca",
            "legal",
            "left",
            "pseudolegal",
            "light",
            "local",
            "loop",
            "lowercase",
            "mainline",
            "makesquare",
            "mate",
            "message",
            "modelmate",
            "modelstalemate",
            "movenumber",
            "northeast",
            "northwest",
            "not",
            "notransform",
            "nullmove",
            "o-o",
            "o-o-o",
            "or",
            "originalcomment",
            "parent",
            "passedpawns",
            "path",
            "pathcount",
            "pathcountunfocused",
            "pathlastposition",
            "pathstatus",
            "persistent",
            "piece",
            "piecename",
            "piece",
            "pieceid",
            "pin",
            "player",
            "ply",
            "position",
            "positionid",
            "power",
            "primary",
            "pseudolegal",
            "puremate",
            "purestalemate",
            "rank",
            "ray",
            "readfile",
            "removecomment",
            "result",
            "reversecolor",
            "right",
            "rotate45",
            "rotate90",
            "secondary",
            "shift",
            "shifthorizontal",
            "shiftvertical",
            "sidetomove",
            "site",
            "sort",
            "sqrt",
            "square",
            "stalemate",
            "tag",
            "terminal",
            "to",
            "true",
            "try",
            "type",
            "typename",
            "unbind",
            "up",
            "uppercase",
            "variation",
            "virtualmainline",
            "while",
            "white",
            "wtm",
            "year",
        ]
        functions = ["cql", "writefile", "readfile", "settag", "str", "max", "min"]
        piece_designators = [
            "A",
            "a",
            "B",
            "b",
            "K",
            "k",
            "N",
            "n",
            "P",
            "p",
            "Q",
            "q",
            "R",
            "r",
        ]
        files = ["c", "d", "e", "f", "g", "h"]
        squares = [
            f"{chr(file)}{column}" for file in range(97, 105) for column in range(1, 9)
        ]
        piece_designators.extend(squares)
        piece_designators.extend(files)
        # Keywords
        kw_pattern = r"\b(" + "|".join(keywords) + r")\b"
        self._keyword_regex = QRegularExpression(kw_pattern)
        self._keyword_regex.setPatternOptions(QRegularExpression.CaseInsensitiveOption)
        self.rules.append((self._keyword_regex, self.fmt_keyword))

        # Functions (before functions' '(' )
        fn_pattern = r"\b(" + "|".join(functions) + r")(?=\s*\()"
        self._function_regex = QRegularExpression(fn_pattern)
        self._function_regex.setPatternOptions(QRegularExpression.CaseInsensitiveOption)
        self.rules.append((self._function_regex, self.fmt_function))

        # Parameters (everything inside parentheses)
        param_pattern = r"\(([^)]*)\)"
        self._param_regex = QRegularExpression(param_pattern)
        self.rules.append((self._param_regex, self.fmt_string))

        # Strings: single & double quotes (per-line)
        self.rules.append(
            (QRegularExpression(r"'[^'\\]*(\\.[^'\\]*)*'"), self.fmt_string)
        )
        self.rules.append(
            (QRegularExpression(r'"[^"\\]*(\\.[^"\\]*)*"'), self.fmt_string)
        )

        # Numbers
        self.rules.append((QRegularExpression(r"\b\d+(\.\d+)?\b"), self.fmt_number))

        # /* */ comments
        self.rules.append(
            (
                QRegularExpression(
                    r"/\*.*?\*/", QRegularExpression.DotMatchesEverythingOption
                ),
                self.fmt_comment,
            )
        )
        # inside brackets
        self.rules.append(
            (
                QRegularExpression(r"\[.*?\]"),
                self.fmt_keyword,
            )
        )
        # Piece designators
        pi_pattern = r"\b(" + "|".join(piece_designators) + r")\b"
        self._pi_regex = QRegularExpression(pi_pattern)
        self._pi_regex.setPatternOptions(QRegularExpression.CaseInsensitiveOption)
        self.rules.append((self._pi_regex, self.fmt_piece_designator))

        # Operators & punctuation
        self.rules.append((QRegularExpression(r"[+\-*/=<>\|!&_]+"), self.fmt_operator))
        self.rules.append((QRegularExpression(r"[(),;]"), self.fmt_operator))
        self.rules.append((QRegularExpression(r"[.]"), self.fmt_keyword))

    # ---------- Highlight ----------
    def highlightBlock(self, text: str):
        # Apply single-line rules
        for regex, fmt in self.rules:
            it = regex.globalMatch(text)
            while it.hasNext():
                m = it.next()
                start = m.capturedStart()
                length = m.capturedLength()
                if start >= 0 and length > 0:
                    self.setFormat(start, length, fmt)

        # Handle multi-line comments /* ... */
        self.setCurrentBlockState(0)

        start_idx = 0
        if self.previousBlockState() != 1:
            start_match = self.commentStart.match(text, 0)
            start_idx = start_match.capturedStart()
        else:
            start_idx = 0

        while start_idx >= 0:
            end_match = self.commentEnd.match(text, start_idx)
            end_idx = end_match.capturedStart()

            if end_idx == -1:
                # Comment continues to next line
                self.setFormat(
                    start_idx, len(text) - start_idx, self.multiLineCommentFormat
                )
                self.setCurrentBlockState(1)
                break
            else:
                length = end_idx - start_idx + end_match.capturedLength()
                self.setFormat(start_idx, length, self.multiLineCommentFormat)
                start_match = self.commentStart.match(text, start_idx + length)
                start_idx = start_match.capturedStart()


# ===================================================
#              Autocomplete Editor
# ===================================================


class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.code_editor: "AutoCompleteTextEdit" = editor
        self.setObjectName("LineNumberArea")

    def sizeHint(self):
        return QSize(self.code_editor.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        self.code_editor.lineNumberAreaPaintEvent(event)


class AutoCompleteTextEdit(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._completer = None

        # line number area
        self.lineNumberArea = LineNumberArea(self)
        font = self.font()
        # font.setPointSize(17)
        self.setFont(font)
        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)

        self.updateLineNumberAreaWidth(0)
        self.highlightCurrentLine()

    # ---- LINE NUMBER AREA ----
    def lineNumberAreaWidth(self):
        digits = len(str(max(1, self.blockCount())))
        space = 3 + self.fontMetrics().horizontalAdvance("9") * digits
        return space

    def updateLineNumberAreaWidth(self, _):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def updateLineNumberArea(self, rect: QRect, dy):
        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(
                0, rect.y(), self.lineNumberArea.width(), rect.height()
            )

        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(
            QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height())
        )

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.lineNumberArea)
        bg_palette_color = self.palette().color(self.backgroundRole())

        # Decide light vs dark
        brightness = (
            bg_palette_color.red() + bg_palette_color.green() + bg_palette_color.blue()
        ) / 3
        is_dark = brightness < 128

        # Set colors dynamically
        if is_dark:
            bg_color = QColor(30, 30, 30)  # dark background
            fg_color = QColor(200, 200, 200)  # light text
        else:
            bg_color = QColor(254, 254, 254)  # light background
            fg_color = QColor(25, 25, 25)  # dark text

        painter.fillRect(event.rect(), bg_color)
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(
            self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        )
        bottom = top + int(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(fg_color)
                painter
                painter.drawText(
                    0,
                    top,
                    self.lineNumberArea.width() - 4,
                    self.fontMetrics().height(),
                    Qt.AlignRight,
                    number,
                )

            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            block_number += 1

    def highlightCurrentLine(self):
        extraSelections = []
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            lineColor = QColor(232, 242, 254)  # light blue
            selection.format.setBackground(lineColor)
            # selection.format.setProperty(QTextEdit.ExtraSelection.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)
        self.setExtraSelections(extraSelections)

    # ---- AUTOCOMPLETE ----
    def setCompleter(self, completer: QCompleter):
        if self._completer:
            self._completer.activated.disconnect()
        self._completer = completer
        completer.setWidget(self)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setFilterMode(Qt.MatchContains)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        completer.activated.connect(self.insertCompletion)

    def completer(self):
        return self._completer

    def insertCompletion(self, completion: str):
        tc = self.textCursor()
        prefix = self.textUnderCursor()
        for _ in range(len(prefix)):
            tc.deletePreviousChar()
        tc.insertText(completion)
        self.setTextCursor(tc)

    def textUnderCursor(self) -> str:
        tc = self.textCursor()
        tc.select(tc.WordUnderCursor)
        return tc.selectedText()

    def keyPressEvent(self, e):
        if self._completer and self._completer.popup().isVisible():
            if e.key() in (Qt.Key_Enter, Qt.Key_Return, Qt.Key_Tab):
                e.ignore()
                return
            if e.key() == Qt.Key_Escape:
                self._completer.popup().hide()
                e.ignore()
                return

        super().keyPressEvent(e)

        if not self._completer:
            return

        prefix = self.textUnderCursor()
        if len(prefix) < 1:
            self._completer.popup().hide()
            return

        self._completer.setCompletionPrefix(prefix)
        cr = self.cursorRect()
        cr.setWidth(
            self._completer.popup().sizeHintForColumn(0)
            + self._completer.popup().verticalScrollBar().sizeHint().width()
        )
        self._completer.complete(cr)


# ===================================================
#                Main Widget / UI
# ===================================================
LIGHT_QSS = """
/* ===== Base ===== */
QWidget {
    background-color: #F5F7FB;
    color: #1F2937;
    font-family: Segoe UI, "Helvetica Neue", Arial, sans-serif;
    font-size: 13px;
}

/* Emphasis label example */
QLabel#Header {
    font-size: 18px;
    font-weight: 700;
    color: #0B5CAD;
}

/* ===== Text Editors ===== */
QPlainTextEdit, QTextEdit {
    background-color: #FFFFFF;
    color: #1F2937;
    border: 1px solid #D1D5DB;
    border-radius: 8px;
    padding: 10px;
    selection-background-color: #CCE4FF;
    selection-color: #111827;
    font-family: Consolas, "Fira Code", "DejaVu Sans Mono", monospace;
    font-size: 24px;
}

/* ===== Inputs ===== */
QLineEdit, QSpinBox, QDoubleSpinBox, QDateEdit, QTimeEdit, QDateTimeEdit {
    background-color: #FFFFFF;
    color: #1F2937;
    border: 1px solid #D1D5DB;
    border-radius: 6px;
    padding: 6px 8px;
    selection-background-color: #CCE4FF;
    selection-color: #111827;
}
QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus,
QDateEdit:focus, QTimeEdit:focus, QDateTimeEdit:focus {
    border-color: #0078D7;
}

/* ComboBox */
QComboBox {
    background-color: #FFFFFF;
    color: #1F2937;
    border: 1px solid #D1D5DB;
    border-radius: 6px;
    padding: 6px 8px;
}
QComboBox::drop-down {
    border-left: 1px solid #D1D5DB;
    width: 24px;
}
QComboBox QAbstractItemView {
    background-color: #FFFFFF;
    color: #1F2937;
    selection-background-color: #CCE4FF;
    selection-color: #111827;
    border: 1px solid #D1D5DB;
}

/* ===== Buttons ===== */
QPushButton {
    background-color: #0078D7;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 14px;
    font-weight: 600;
}
QPushButton:hover { background-color: #005A9E; }
QPushButton:pressed { background-color: #004578; }
QPushButton:disabled { background-color: #9CA3AF; color: #F3F4F6; }

QToolButton {
    background: transparent;
    color: #1F2937;
    border-radius: 6px;
    padding: 6px 10px;
}
QToolButton:hover { background-color: rgba(0,0,0,0.06); }
QToolButton:pressed, QToolButton:checked { background-color: rgba(0,0,0,0.10); }

QCheckBox, QRadioButton { font-weight: 600; }

/* ===== Tooltips ===== */
QToolTip {
    background-color: #111827;
    color: #F9FAFB;
    border: 1px solid #374151;
    padding: 6px 8px;
    border-radius: 6px;
}

/* ===== Scrollbars ===== */
QScrollBar:vertical {
    background: #F5F7FB;
    width: 12px;
    margin: 4px 0;
    border-radius: 6px;
}
QScrollBar::handle:vertical {
    background: #D1D5DB;
    min-height: 20px;
    border-radius: 6px;
}
QScrollBar::handle:vertical:hover { background: #A0AEC0; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; background: none; }
QScrollBar:horizontal {
    background: #F5F7FB;
    height: 12px;
    margin: 0 4px;
    border-radius: 6px;
}
QScrollBar::handle:horizontal {
    background: #D1D5DB;
    min-width: 20px;
    border-radius: 6px;
}
QScrollBar::handle:horizontal:hover { background: #A0AEC0; }

/* ===== Menubar & Menus ===== */
QMenuBar {
    background-color: #FFFFFF;
    color: #1F2937;
}
QMenuBar::item {
    background: transparent;
    padding: 6px 10px;
    margin: 0 2px;
    border-radius: 6px;
}
QMenuBar::item:selected { background: #E5E7EB; }
QMenuBar::item:pressed { background: #D1D5DB; }

QMenu {
    background-color: #FFFFFF;
    color: #1F2937;
    border: 1px solid #D1D5DB;
    padding: 6px;
}
QMenu::separator {
    height: 1px;
    background: #D1D5DB;
    margin: 6px 8px;
}
QMenu::item {
    padding: 6px 12px;
    border-radius: 6px;
}
QMenu::item:selected { background-color: #E5E7EB; }
QMenu::item:disabled { color: #9CA3AF; }

/* ===== Toolbars & Statusbar ===== */
QToolBar {
    background-color: #FFFFFF;
    border-bottom: 1px solid #E5E7EB;
    spacing: 6px;
    padding: 4px;
}
QStatusBar {
    background-color: #FFFFFF;
    color: #1F2937;
    border-top: 1px solid #E5E7EB;
}
QStatusBar::item { border: none; }

/* ===== Dock Widgets ===== */
QDockWidget {
    border: 1px solid #E5E7EB;
    border-radius: 6px;
}
QDockWidget::title {
    text-align: left;
    padding: 6px 10px;
    background: #FFFFFF;
    color: #1F2937;
    border-bottom: 1px solid #E5E7EB;
}

/* ===== Tabs ===== */
QTabWidget::pane {
    border: 1px solid #E5E7EB;
    border-radius: 6px;
    top: -1px;
    background: #FFFFFF;
}
QTabBar::tab {
    background: #FFFFFF;
    color: #1F2937;
    padding: 6px 12px;
    border: 1px solid #E5E7EB;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 2px;
}
QTabBar::tab:selected { background: #F5F7FB; }
QTabBar::tab:hover { background: #E5E7EB; }

/* ===== Splitter ===== */
QSplitter::handle {
    background: #E5E7EB;
}
QSplitter::handle:hover {
    background: #CBD5E1;
}

/* ===== Views (Tables/Lists/Trees) ===== */
QTableWidget, QTableView, QListView, QTreeView {
    background-color: #FFFFFF;
    color: #1F2937;
    gridline-color: #D1D5DB;
    border: 1px solid #D1D5DB;
    border-radius: 6px;
    selection-background-color: #CCE4FF;
    selection-color: #111827;
}
QHeaderView::section {
    background-color: #E5E7EB;
    color: #1F2937;
    font-weight: 600;
    padding: 6px;
    border: 1px solid #D1D5DB;
}
QTableCornerButton::section {
    background-color: #E5E7EB;
    border: 1px solid #D1D5DB;
}

/* ===== GroupBox ===== */
QGroupBox {
    border: 1px solid #E5E7EB;
    border-radius: 6px;
    margin-top: 12px;
    padding: 6px 8px 8px 8px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    background-color: transparent;
    padding: 0 4px;
    color: #0B5CAD;
    font-weight: 600;
}

/* ===== ProgressBar ===== */
QProgressBar {
    border: 1px solid #D1D5DB;
    border-radius: 6px;
    text-align: center;
    background: #FFFFFF;
    color: #1F2937;
}
QProgressBar::chunk {
    background-color: #0078D7;
    border-radius: 6px;
}
"""
DARK_QSS = """
/* ===== Base ===== */
QWidget {
    background-color: #0F172A;
    color: #E5E7EB;
    font-family: Segoe UI, "Helvetica Neue", Arial, sans-serif;
    font-size: 13px;
}

/* Emphasis label example: QLabel with objectName 'Header' */
QLabel#Header {
    font-size: 18px;
    font-weight: 700;
    color: #93C5FD;
}

/* ===== Text Editors ===== */
QPlainTextEdit, QTextEdit {
    background-color: #1E1E1E;
    color: #DCDCDC;
    border: 1px solid #374151;
    border-radius: 8px;
    padding: 10px;
    selection-background-color: #264F78;
    selection-color: #FFFFFF;
    font-family: Consolas, "Fira Code", "DejaVu Sans Mono", monospace;
    font-size: 24px;
}

/* ===== Inputs ===== */
QLineEdit, QSpinBox, QDoubleSpinBox, QDateEdit, QTimeEdit, QDateTimeEdit {
    background-color: #0F172A;
    color: #E5E7EB;
    border: 1px solid #374151;
    border-radius: 6px;
    padding: 6px 8px;
    selection-background-color: #264F78;
    selection-color: #FFFFFF;
}

QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus,
QDateEdit:focus, QTimeEdit:focus, QDateTimeEdit:focus {
    border-color: #3B82F6;
}
QIcon {
    color:white;
    background-color:white;
}

/* ComboBox (and popup list) */
QComboBox {
    background-color: #0F172A;
    color: #E5E7EB;
    border: 1px solid #374151;
    border-radius: 6px;
    padding: 6px 8px;
}
QComboBox::drop-down {
    border-left: 1px solid #374151;
    width: 24px;
}
QComboBox QAbstractItemView {
    background-color: #111827;
    color: #E5E7EB;
    selection-background-color: #264F78;
    selection-color: #FFFFFF;
    border: 1px solid #374151;
}

/* ===== Buttons & Checkables ===== */
QPushButton {
    background-color: #2563EB;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 14px;
    font-weight: 600;
}
QPushButton:hover { background-color: #1D4ED8; }
QPushButton:pressed { background-color: #1E40AF; }
QPushButton:disabled { background-color: #4B5563; color: #9CA3AF; }

QToolButton {
    background: transparent;
    color: #E5E7EB;
    border-radius: 6px;
    padding: 6px 10px;
}
QToolButton:hover { background-color: rgba(255,255,255,0.06); }
QToolButton:pressed, QToolButton:checked { background-color: rgba(255,255,255,0.10); }

QCheckBox, QRadioButton { font-weight: 600; }

/* ===== Tooltips ===== */
QToolTip {
    background-color: #111827;
    color: #F9FAFB;
    border: 1px solid #374151;
    padding: 6px 8px;
    border-radius: 6px;
}

/* ===== Scrollbars ===== */
QScrollBar:vertical {
    background: #1E1E1E;
    width: 12px;
    margin: 4px 0 4px 0;
    border-radius: 6px;
}
QScrollBar::handle:vertical {
    background: #374151;
    min-height: 20px;
    border-radius: 6px;
}
QScrollBar::handle:vertical:hover { background: #4B5563; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; background: none; }
QScrollBar:horizontal {
    background: #1E1E1E;
    height: 12px;
    margin: 0 4px 0 4px;
    border-radius: 6px;
}
QScrollBar::handle:horizontal {
    background: #374151;
    min-width: 20px;
    border-radius: 6px;
}
QScrollBar::handle:horizontal:hover { background: #4B5563; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; background: none; }

/* ===== Menubar & Menus ===== */
QMenuBar {
    background-color: #0B1220;
    color: #E5E7EB;
}
QMenuBar::item {
    background: transparent;
    padding: 6px 10px;
    margin: 0 2px;
    border-radius: 6px;
}
QMenuBar::item:selected { background: rgba(255,255,255,0.08); }
QMenuBar::item:pressed { background: rgba(255,255,255,0.12); }

QMenu {
    background-color: #111827;
    color: #E5E7EB;
    border: 1px solid #374151;
    padding: 6px;
}
QMenu::separator {
    height: 1px;
    background: #374151;
    margin: 6px 8px;
}
QMenu::item {
    padding: 6px 12px;
    border-radius: 6px;
}
QMenu::item:selected { background-color: #1F2937; }
QMenu::item:disabled { color: #9CA3AF; }

/* ===== Toolbars & Statusbar ===== */
QToolBar {
    background-color: #0B1220;
    border-bottom: 1px solid #1F2937;
    spacing: 6px;
    padding: 4px;
}
QStatusBar {
    background-color: #0B1220;
    color: #E5E7EB;
    border-top: 1px solid #1F2937;
}
QStatusBar::item {
    border: none;
}

/* ===== Dock Widgets ===== */
QDockWidget {
    titlebar-close-icon: none;   /* Let QtAwesome buttons blend if you add custom titlebars */
    titlebar-normal-icon: none;
    border: 1px solid #1F2937;
    border-radius: 6px;
}
QDockWidget::title {
    text-align: left;
    padding: 6px 10px;
    background: #0B1220;
    color: #E5E7EB;
    border-bottom: 1px solid #1F2937;
}

/* ===== Tabs ===== */
QTabWidget::pane {
    border: 1px solid #1F2937;
    border-radius: 6px;
    top: -1px;
    background: #0F172A;
}
QTabBar::tab {
    background: #0B1220;
    color: #E5E7EB;
    padding: 6px 12px;
    border: 1px solid #1F2937;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 2px;
}
QTabBar::tab:selected { background: #111827; }
QTabBar::tab:hover { background: #162134; }
QTabBar::tab:!selected { color: #C7D2FE; }

/* ===== Splitter ===== */
QSplitter::handle {
    background: #1F2937;
}
QSplitter::handle:hover {
    background: #374151;
}

/* ===== Views (Tables/Lists/Trees) ===== */
QTableWidget, QTableView, QListView, QTreeView {
    background-color: #1E1E1E;
    color: #E5E7EB;
    gridline-color: #374151;
    border: 1px solid #374151;
    border-radius: 6px;
    selection-background-color: #264F78;
    selection-color: #FFFFFF;
}
QTableWidget::item, QTableView::item, QListView::item, QTreeView::item {
    selection-background-color: #264F78;
    selection-color: #FFFFFF;
}
QHeaderView::section {
    background-color: #111827;
    color: #E5E7EB;
    font-weight: 600;
    padding: 6px;
    border: 1px solid #374151;
}
QTableCornerButton::section {
    background-color: #111827;
    border: 1px solid #374151;
}

/* ===== GroupBox ===== */
QGroupBox {
    border: 1px solid #1F2937;
    border-radius: 6px;
    margin-top: 12px;
    padding: 6px 8px 8px 8px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    background-color: transparent;
    padding: 0 4px;
    color: #93C5FD;
    font-weight: 600;
}

/* ===== ProgressBar ===== */
QProgressBar {
    border: 1px solid #374151;
    border-radius: 6px;
    text-align: center;
    background: #111827;
    color: #E5E7EB;
}
QProgressBar::chunk {
    background-color: #2563EB;
    border-radius: 6px;
}

/* ===== Calendar (if used) ===== */
QCalendarWidget QWidget { background: #111827; color: #E5E7EB; }
QCalendarWidget QAbstractItemView:enabled
{ selection-background-color: #264F78; selection-color: #FFFFFF; }
"""
SQL_KEYWORDS_FOR_COMPLETER = [
    "A",
    "a",
    "abs",
    "and",
    "ascii",
    "assert",
    "atomic",
    "B",
    "b",
    "between",
    "black",
    "btm",
    "castle",
    "check",
    "child",
    "child",
    "comment",
    "connectedpawns",
    "consecutivemoves",
    "countmoves",
    "currentmove",
    "currentposition",
    "currenttransform",
    "dark",
    "date",
    "depth",
    "dictionary",
    "distance",
    "doubledpawns",
    "down",
    "echo",
    "eco",
    "elo",
    "event",
    "eventdate",
    "false",
    "fen",
    "file",
    "find",
    "flip",
    "flipcolor",
    "fliphorizontal",
    "flipvertical",
    "from",
    "function",
    "gamenumber",
    "hascomment",
    "idealmate",
    "idealstalemate",
    "if",
    "in",
    "in",
    "indexof",
    "initial",
    "initialposition",
    "int",
    "isbound",
    "isolatedpawns",
    "isunbound",
    "K",
    "k",
    "lastgamenumber",
    "lca",
    "legal",
    "left",
    "pseudolegal",
    "light",
    "local",
    "loop",
    "lowercase",
    "mainline",
    "makesquare",
    "mate",
    "max",
    "message",
    "min",
    "modelmate",
    "modelstalemate",
    "movenumber",
    "N",
    "n",
    "northeast",
    "northwest",
    "not",
    "notransform",
    "nullmove",
    "o-o",
    "o-o-o",
    "or",
    "originalcomment",
    "P",
    "p",
    "parent",
    "passedpawns",
    "path",
    "pathcount",
    "pathcountunfocused",
    "pathlastposition",
    "pathstatus",
    "persistent",
    "piece",
    "piecename",
    "piece",
    "pieceid",
    "pin",
    "player",
    "ply",
    "position",
    "positionid",
    "power",
    "primary",
    "pseudolegal",
    "puremate",
    "purestalemate",
    "Q",
    "q",
    "R",
    "r",
    "rank",
    "ray",
    "readfile",
    "removecomment",
    "result",
    "reversecolor",
    "right",
    "rotate45",
    "rotate90",
    "secondary",
    "settag",
    "shift",
    "shifthorizontal",
    "shiftvertical",
    "sidetomove",
    "site",
    "sort",
    "sqrt",
    "square",
    "stalemate",
    "str",
    "tag",
    "terminal",
    "to",
    "true",
    "try",
    "type",
    "typename",
    "unbind",
    "up",
    "uppercase",
    "variation",
    "virtualmainline",
    "while: standard form",
    "while: ~~ form",
    "white",
    "writefile",
    "wtm",
    "year",
]


class SqlEditorWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SQLite Query Editor")
        self.resize(800, 520)

        # --- Layouts
        root = QVBoxLayout(self)
        controls = QHBoxLayout()

        # --- Editor
        self.editor = AutoCompleteTextEdit(self)
        root.addWidget(self.editor, 1)

        # --- Highlighter (theme-aware)
        self.highlighter = SqlHighlighter(self.editor.document(), theme="dark")

        # --- Completer
        completer = QCompleter(sorted(SQL_KEYWORDS_FOR_COMPLETER, key=str.lower))
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setFilterMode(Qt.MatchContains)
        self.editor.setCompleter(completer)

        # --- Buttons / Controls
        self.btn_format = QPushButton("Format CQL")
        self.btn_format.clicked.connect(self.format_sql)
        self.btn_format.setCursor(Qt.PointingHandCursor)
        controls.addWidget(self.btn_format)
        controls.setAlignment(self.btn_format, Qt.AlignRight)
        root.addLayout(controls)

        # --- Shortcuts (simple approach)
        self.btn_format.setShortcut("Ctrl+B")

    # ---------- Theme ----------

    # ---------- Formatting ----------
    def format_sql(self):
        raw_sql = self.editor.toPlainText()
        if not raw_sql.strip():
            return
        if sqlfmt_format is None:
            # Fallback: soft message and simple uppercase keywords
            reply = QMessageBox.question(
                self,
                "sqlfmt not available",
                "The 'sqlfmt' package is not installed.\n\n"
                "Would you like a quick fallback (uppercase keywords only)?\n\n"
                "To enable full formatting:\n"
                "    pip install sqlfmt",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes,
            )
            if reply == QMessageBox.Yes:
                self.editor.setPlainText(self._fallback_uppercase_keywords(raw_sql))
            return
        try:
            formatted = sqlfmt_format(raw_sql)
            self.editor.setPlainText(formatted)
        except Exception as e:
            QMessageBox.warning(self, "Formatting error", f"Could not format SQL:\n{e}")

    def _fallback_uppercase_keywords(self, sql: str) -> str:
        # Minimal, non-invasive fallback: uppercase known tokens when bounded by word boundaries

        def repl(m: re.Match[str]):
            return m.group(0).upper()

        tokens = sorted(set(SQL_KEYWORDS_FOR_COMPLETER), key=len, reverse=True)
        pattern = r"\b(" + "|".join(map(re.escape, tokens)) + r")\b"
        return re.sub(pattern, repl, sql, flags=re.IGNORECASE)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_QSS)
    editor = SqlEditorWidget()
    editor.show()
    sys.exit(app.exec_())