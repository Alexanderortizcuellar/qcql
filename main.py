import json
import sys
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QAction,
    QDockWidget,
    QTextEdit,
    QToolBar,
    QStatusBar,
    QDialog,
    QVBoxLayout,
    QPushButton,
    QHBoxLayout,
    QLineEdit,
    QListWidget,
    QProgressDialog,
    QFileDialog,
    QMessageBox,
)
from PyQt5.QtCore import Qt, QFile, pyqtSignal
from PyQt5.QtGui import QIcon
import qtawesome as qta
from editor import SqlEditorWidget
from styles import DARK_QSS, LIGHT_QSS
from parser import PgnTableWidget
from browser import PGNBrowser
from process import CQLProcess, CounterProcess


def fa_icon(*names, color="#1F2937"):
    """Helper to safely get QtAwesome icon with fallback."""
    for n in names:
        try:
            return qta.icon(n, color=color)
        except Exception:
            continue
    return qta.icon("fa5s.question")  # fallback icon


class QueryTemplatesDialog(QDialog):
    createQueryRequest = pyqtSignal(str)
    templateSelected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Query Templates")
        self.resize(350, 450)

        layout = QVBoxLayout(self)

        # --- List Widget for Templates ---
        self.template_list = QListWidget(self)
        self.template_list.itemClicked.connect(
            lambda: self.templateSelected.emit(self.get_current_template())
        )
        # self.template_list.currentRowChanged.connect(
        #     lambda: self.templateSelected.emit(self.get_current_template())
        # )
        layout.addWidget(self.template_list)

        # --- Input + Add Button ---
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit(self)
        self.input_field.setPlaceholderText("Enter new template...")
        input_layout.addWidget(self.input_field)

        add_btn = QPushButton("Add", self)
        add_btn.setIcon(fa_icon("fa5s.plus", "fa.plus"))
        add_btn.clicked.connect(
            lambda: self.createQueryRequest.emit(self.input_field.text())
        )
        input_layout.addWidget(add_btn)
        layout.addLayout(input_layout)

        # --- Delete Button ---
        delete_btn = QPushButton("Delete Selected", self)
        delete_btn.setIcon(fa_icon("fa5s.trash", "fa.trash"))
        delete_btn.clicked.connect(self.delete_selected)
        layout.addWidget(delete_btn)

        # --- Close Button ---
        close_btn = QPushButton("Close", self)
        close_btn.setIcon(fa_icon("fa5s.times", "fa.close"))
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        self.templates = []
        self.load_templates()

    def get_current_template(self):
        query_index = self.template_list.currentIndex().row()
        return self.templates[query_index]["query"]

    def load_templates(self):
        file = QFile("data/queries.json")
        if file.exists():
            try:
                with open("data/queries.json", "r") as f:
                    self.templates = json.load(f)
                    template_names = [query["name"] for query in self.templates]
                    self.template_list.clear()
                    self.template_list.addItems(template_names)
            except Exception as e:
                print("Error loading templates.", e)

    def add_template(self, query):
        text = self.input_field.text().strip()
        if text:
            with open("data/queries.json", "w") as f:
                self.templates.append({"name": text, "query": query})
                json.dump(self.templates, f, indent=4)
            self.load_templates()
            self.input_field.clear()

    def delete_selected(self):
        index = self.template_list.currentIndex().row()
        self.templates.pop(index)
        with open("data/queries.json", "w") as f:
            json.dump(self.templates, f, indent=4)
        self.load_templates()


class ChessboardDialog(QDialog):
    def __init__(self, game_info: str, parent=None, html_style=False):
        super().__init__(parent)

        # Enable title bar and close button
        self.setWindowFlags(Qt.Window)

        # Allow resizing
        self.setSizeGripEnabled(True)
        self.setMinimumSize(590, 750)  # Optional: prevent too small size
        self.resize(1260, 620)  # Start bigger for better UX

        self.setWindowTitle("Chessboard Viewer")

        # Layout
        layout = QVBoxLayout(self)

        # Add your PGN browser widget
        self.pgn_browser = PGNBrowser(game_info, html_style=html_style)
        layout.addWidget(self.pgn_browser)

    def closeEvent(self, a0):
        self.pgn_browser.engine.quit()
        a0.accept()


# ---------- Main Window ----------
class ChessCQLApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chess CQL Query Tool")
        self.setWindowIcon(QIcon("images/cql_logo.png"))
        self.resize(1200, 800)
        self.dark_mode = False  # current theme state

        self.pgnfilename = None
        self.game_count = 0
        # Build UI
        self._create_actions()
        self._create_menus()
        self._create_toolbar()
        self._create_central_table()
        self._create_docks()
        self._wire_view_menu_toggles()

        # Status bar
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)

        # Save default dock layout so we can reset later
        self.default_state = self.saveState()

        # Seed table with placeholder rows
        self.setStyleSheet(LIGHT_QSS)
        self.cql = CQLProcess(self)
        self.cql.gamesReceived.connect(self.on_games)
        self.cql.errorReceived.connect(self.on_error_received)
        self.cql.statsReceived.connect(self.on_info_received)
        self.cql.messageReceived.connect(self.log_panel.append)

    def on_info_received(self, cql_info: dict):
        if isinstance(cql_info, dict):
            numbermatches = cql_info.get("numbermatches")
            if numbermatches:
                self.results_table.set_info_text(
                    f"{numbermatches} matches of {self.game_count} games"
                )
                self.status_bar.showMessage(
                    f"{numbermatches} matches of {self.game_count} games"
                )
                self.log_panel.append(
                    f"<span style='color:blue'>Matches: {numbermatches}</span><br>"
                )
            else:
                for k, v in cql_info.items():
                    self.log_panel.append(
                        f"<span style='color:blue'>{k}: {v}</span><br>"
                    )

    def on_error_received(self, error: str):
        self.log_panel.insertHtml(f"<span style='color:red'>{error}</span><br>")

    def show_progress(self):
        dlg = QProgressDialog(
            "Processing games...",
            "Cancel",
            0,
            self.game_count,
            self,
            Qt.WindowCloseButtonHint,
        )
        dlg.setWindowTitle("Processing...")
        self.cql.progressUpdated.connect(dlg.setValue)
        dlg.canceled.connect(self.cql.terminate)
        self.cql.finishedEXecution.connect(dlg.close)

        dlg.setWindowModality(Qt.ApplicationModal)
        dlg.setValue(0)
        dlg.exec_()

    # ----- Actions with Icons -----
    def _create_actions(self):
        # File
        self.act_open_pgn = QAction(
            fa_icon("fa5s.folder-open", "fa.folder-open"), "Open PGN", self
        )
        self.act_open_pgn.setShortcut("Ctrl+O")
        self.act_open_pgn.setStatusTip("Open a PGN file")
        self.act_open_pgn.triggered.connect(self.open_pgn_file)

        self.act_save_query = QAction(
            fa_icon("fa5s.save", "fa.save"), "Save Query", self
        )
        self.act_save_query.setShortcut("Ctrl+S")
        self.act_save_query.setStatusTip("Save current CQL")
        self.act_save_query.triggered.connect(
            lambda: self.log_panel.append("Save Query clicked")
        )

        self.act_export_results = QAction(
            fa_icon("fa5s.file-export", "fa.upload"), "Export Results", self
        )
        self.act_export_results.setShortcut("Ctrl+Shift+E")
        self.act_export_results.setStatusTip("Export search results")
        self.act_export_results.triggered.connect(
            lambda: self.log_panel.append("Export Results clicked")
        )

        # Edit
        self.act_undo = QAction(fa_icon("fa5s.undo", "fa.undo"), "Undo", self)
        self.act_undo.setShortcut("Ctrl+Z")
        self.act_undo.triggered.connect(lambda: self.log_panel.append("Undo clicked"))

        self.act_redo = QAction(fa_icon("fa5s.redo", "fa.repeat"), "Redo", self)
        self.act_redo.setShortcut("Ctrl+Y")
        self.act_redo.triggered.connect(lambda: self.log_panel.append("Redo clicked"))

        # Tools
        self.act_templates = QAction(
            fa_icon("fa5s.list", "fa.list"), "Query Templates…", self
        )
        self.act_templates.setShortcut("Ctrl+T")
        self.act_templates.triggered.connect(self.show_query_templates)

        # View – theme toggle (checkable) + reset layout
        self.act_theme = QAction(self._theme_icon(), "Dark Mode", self)
        self.act_theme.setCheckable(True)
        self.act_theme.setShortcut("Ctrl+D")
        self.act_theme.setStatusTip("Toggle Dark/Light theme")
        self.act_theme.triggered.connect(self.toggle_theme)

        self.act_reset_layout = QAction(
            fa_icon("fa5s.window-restore", "fa.window-restore"), "Reset Layout", self
        )
        self.act_reset_layout
        self.act_reset_layout.setStatusTip("Restore default dock positions")
        self.act_reset_layout.triggered.connect(self.reset_layout)

        # Toolbar actions
        self.act_run = QAction(fa_icon("fa5s.play", "fa.play"), "Run Query", self)
        self.act_run.setShortcut("F5")
        self.act_run.triggered.connect(self.run_query)

        self.act_clear = QAction(
            fa_icon("fa5s.trash", "fa.trash"), "Clear Results", self
        )
        self.act_clear.setShortcut("Ctrl+L")
        self.act_clear.triggered.connect(self.clear_results_placeholder)

        # Optional Stop (placeholder, disabled initially)
        self.act_stop = QAction(fa_icon("fa5s.stop", "fa.stop"), "Stop", self)
        self.act_stop.setEnabled(False)
        self.act_stop.triggered.connect(lambda: self.log_panel.append("Stop clicked"))

    # ----- Menus -----
    def _create_menus(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("File")
        file_menu.addAction(self.act_open_pgn)
        file_menu.addAction(self.act_save_query)
        file_menu.addAction(self.act_export_results)

        edit_menu = menu_bar.addMenu("Edit")
        edit_menu.addAction(self.act_undo)
        edit_menu.addAction(self.act_redo)

        self.view_menu = menu_bar.addMenu("View")
        # (Dock toggle actions added later once docks exist)
        self.view_menu.addSeparator()
        self.view_menu.addAction(self.act_theme)
        self.view_menu.addAction(self.act_reset_layout)

        tools_menu = menu_bar.addMenu("Tools")
        tools_menu.addAction(self.act_templates)

    # ----- Toolbar -----
    def _create_toolbar(self):
        toolbar = QToolBar("Main Toolbar", self)
        toolbar.setObjectName("MainToolbar")
        toolbar.setMovable(True)
        toolbar.addAction(self.act_run)
        toolbar.addAction(self.act_stop)
        toolbar.addSeparator()
        toolbar.addAction(self.act_clear)
        self.addToolBar(toolbar)

    # ----- Central results table -----
    def _create_central_table(self):
        self.results_table = PgnTableWidget()

        self.setCentralWidget(self.results_table)

        # Double-click a row to open the chessboard dialog
        self.results_table.gameSelected.connect(self.show_chessboard_dialog)

    # ----- Docks (CQL editor + Logs) -----
    def _create_docks(self):
        # CQL Editor Dock
        self.cql_dock = QDockWidget("CQL Editor", self)
        self.cql_dock.setObjectName("CQLDock")
        self.cql_editor = SqlEditorWidget()
        self.cql_dock.setWidget(self.cql_editor)
        self.cql_dock.setFeatures(
            QDockWidget.DockWidgetClosable
            | QDockWidget.DockWidgetMovable
            | QDockWidget.DockWidgetFloatable
        )
        self.addDockWidget(Qt.LeftDockWidgetArea, self.cql_dock)

        # Logs Dock
        self.log_dock = QDockWidget("Logs", self)
        self.log_dock.setObjectName("LogsDock")
        self.log_panel = QTextEdit(self)
        self.log_panel.insertHtml(
            "<span style='color:green'>Welcome to Chess CQL!</span><br>"
        )
        self.log_panel.setReadOnly(True)
        self.log_dock.setWidget(self.log_panel)
        self.log_dock.setFeatures(
            QDockWidget.DockWidgetClosable
            | QDockWidget.DockWidgetMovable
            | QDockWidget.DockWidgetFloatable
        )
        self.addDockWidget(Qt.BottomDockWidgetArea, self.log_dock)

    def _wire_view_menu_toggles(self):
        # Add toggle actions for docks into View menu (and give them icons)
        self.cql_toggle = self.cql_dock.toggleViewAction()
        self.cql_toggle.setIcon(fa_icon("fa5s.code", "fa.code"))
        self.view_menu.insertAction(
            self.view_menu.actions()[0] if self.view_menu.actions() else None,
            self.cql_toggle,
        )

        self.log_toggle = self.log_dock.toggleViewAction()
        self.log_toggle.setIcon(fa_icon("fa5s.terminal", "fa.terminal"))
        self.view_menu.insertAction(
            self.view_menu.actions()[1] if len(self.view_menu.actions()) > 1 else None,
            self.log_toggle,
        )

    # ----- View Actions -----
    def _theme_icon(self) -> QIcon:
        # Show moon when the user can switch to dark; show sun when in dark mode.
        return (
            fa_icon("fa5s.moon", "fa.moon-o")
            if not self.dark_mode
            else fa_icon("fa5s.sun", "fa.sun-o")
        )

    def toggle_theme(self, checked: bool):
        self.dark_mode = checked
        if self.dark_mode:
            self.setStyleSheet(DARK_QSS)
        else:
            self.setStyleSheet(LIGHT_QSS)
        self.act_theme.setIcon(self._theme_icon())
        self.act_theme.setText("Dark Mode" if not self.dark_mode else "Light Mode")
        self._update_icons()

    def _update_icons(self):
        if self.dark_mode:
            icon_color = "#E5E7EB"  # Light gray for dark background
        else:
            icon_color = "#1F2937"  # Dark gray for light background

        self.act_run.setIcon(qta.icon("fa5s.play", color=icon_color))
        self.act_clear.setIcon(qta.icon("fa5s.trash", color=icon_color))
        self.act_reset_layout.setIcon(qta.icon("fa5s.window-restore", color=icon_color))
        self.act_open_pgn.setIcon(qta.icon("fa5s.folder-open", color=icon_color))
        self.act_save_query.setIcon(qta.icon("fa5s.save", color=icon_color))
        self.act_export_results.setIcon(qta.icon("fa5s.file-export", color=icon_color))
        self.act_redo.setIcon(qta.icon("fa5s.redo", color=icon_color))
        self.act_undo.setIcon(qta.icon("fa5s.undo", color=icon_color))
        self.cql_toggle.setIcon(qta.icon("fa5s.code", color=icon_color))
        self.log_toggle.setIcon(qta.icon("fa5s.terminal", color=icon_color))
        self.act_theme.setIcon(
            qta.icon(
                "fa5s.moon" if not self.dark_mode else "fa5s.sun", color=icon_color
            )
        )
        self.act_templates.setIcon(qta.icon("fa5s.list", color=icon_color))
        # Add more actions as needed

    def reset_layout(self):
        # Bring docks back to defaults and ensure their toggles reflect visibility
        self.restoreState(self.default_state)
        # Re-wire toggles (if Qt removed/re-created actions internally)
        self._wire_view_menu_toggles()

    # ----- Placeholders to connect logic later -----
    def show_query_templates(self):
        dlg = QueryTemplatesDialog(self)
        dlg.createQueryRequest.connect(
            lambda: dlg.add_template(self.cql_editor.editor.toPlainText())
        )
        dlg.templateSelected.connect(
            lambda template: self.cql_editor.editor.setPlainText(template)
        )
        dlg.exec_()

    def show_chessboard_dialog(self, game: dict):
        ChessboardDialog(game, self, html_style=self.dark_mode).exec_()

    def run_query(self):
        if not self.cql_editor.editor.toPlainText() or not self.pgnfilename:
            QMessageBox.warning(
                self,
                "Missing PGN File",
                "Please open a PGN file before running the query.",
            )
            return
        self.cql.search(self.cql_editor.editor.toPlainText(), self.pgnfilename)
        self.show_progress()

    def open_pgn_file(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Open PGN File", "", "PGN Files (*.pgn)"
        )
        if filename:
            self.pgnfilename = filename
            self.status_bar.showMessage(f"Opening {filename}... Please wait...")
            print(f"Opening {filename}... Please wait...")
            self.act_run.setEnabled(False)
            counter = CounterProcess(self, self.pgnfilename)
            counter.countFinished.connect(self.on_count_finished)
            counter.start()

    def on_count_finished(self, count: int):
        self.status_bar.showMessage(f"games on file {count} games")
        self.results_table.set_info_text(f"{count} games on file")
        self.act_run.setEnabled(True)
        self.game_count = count

    def on_cql_finished(self, exitCode, exitStatus, output: str):
        print("CQL Process finished")

    def save_query(self):
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Query", "", "CQL Files (*.cql)"
        )
        if filename:
            with open(filename, "w") as f:
                f.write(self.cql_editor.editor.toPlainText())
            self.status_bar.showMessage(f"Saved query to {filename}")

    def clear_results_placeholder(self):
        self.results_table.clear()
        self.log_panel.clear()
        self.log_panel.append("Results cleared")

    def on_games(self, games: str):
        self.results_table.clear()
        self.results_table.load_pgn_threaded(games)

    def closeEvent(self, a0):
        ok = QMessageBox.question(
            self,
            "Exit",
            "Are you sure you want to exit?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if ok == QMessageBox.Yes:
            a0.accept()
        else:
            a0.ignore()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChessCQLApp()
    window.show()
    sys.exit(app.exec_())
