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
QPlainTextEdit {
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

QTextEdit {
    background-color: #FFFFFF;
    color: #1F2937;
    border: 1px solid transparent;
    border-radius: 8px;
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
QPlainTextEdit{
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
QTextEdit {
    background-color: #1E1E1E;
    color: #DCDCDC;
    border: 1px solid #374151;
    border-radius: 8px;
    selection-background-color: #264F78;
    selection-color: #FFFFFF;
    font-family: Consolas, "Fira Code", "DejaVu Sans Mono", monospace;
    font-size: 16px;
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
