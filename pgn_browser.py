import re

from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWidgets import (QAction, QApplication, QDialog, QDialogButtonBox,
                             QMenu, QTextBrowser, QTextEdit, QVBoxLayout)

from movemanager import MoveManager


class CommentDialog(QDialog):
    def __init__(self, parent, comment: str = ""):
        super().__init__(parent)
        self.comment = comment
        self.setWindowTitle("Comments")
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.textedit = QTextEdit()
        self.textedit.setPlainText(comment)
        layout.addWidget(self.textedit)
        buttonbox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(buttonbox)
        buttonbox.accepted.connect(self.on_accepted)
        buttonbox.rejected.connect(self.close)

    def on_accepted(self):
        self.comment = self.textedit.toPlainText()
        self.accept()


class PGNBrowser(QTextBrowser):
    def __init__(self, parent, movemanager: MoveManager):
        super().__init__(parent)
        self.movemanager = movemanager
        self.setOpenLinks(False)
        self.setStyleSheet("QTextBrowser {font-size:20px;font-family: Noto Sans;}")
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.on_custom_context)
        #self.anchorClicked.connect(self.on_anchor_clicked)
        self.setHtml(
            """<p>
            <a href="move(1)">e4</a> 
            <a href="move(2)">e5</a>
            </p>"""
        )

    def on_custom_context(self, point):
        anchor = self.anchorAt(point)
        if not anchor:
            return
        menu = QMenu(self)

        actions = [
            ("Promote to Main..", callable),
            ("Promote..", self.on_promote),
            ("Demote..", callable),
            ("Delete from here..", callable),
            ("Add Comment..", self.on_add_comment),
        ]

        for name, func in actions:
            act = QAction(name, self)
            act.triggered.connect(lambda _, f=func: f(anchor))
            menu.addAction(act)

        menu.exec_(self.mapToGlobal(point))

    def on_add_comment(self, anchor):
        node_index = self.match_node(anchor)
        if node_index is not None:
            node = self.movemanager.get_node_by_index(node_index)
            dlg = CommentDialog(self, node.comment)
            if dlg.exec_() != QDialog.Accepted:
                return
            self.movemanager.add_comment(node_index, dlg.comment)

    def on_promote(self, anchor):
        pass

    def demote(self, anchor):
        pass

    def on_delete(self, anchor):
        pass

    def match_node(self, anchor: str) -> int | None:
        match = re.match(r"move\((\d+)\)", anchor)
        if match:
            try:
                index = int(match.group(1))
                return index
            except ValueError:
                return None
        return None

    def on_anchor_clicked(self, url: QUrl):
        match = re.match(r"move\((\d+)\)", url.toString())
        if match:
            print("Clicked move:", match.group(1))


if __name__ == "__main__":
    app = QApplication([])
    browser = PGNBrowser(None, MoveManager())
    browser.show()
    app.exec_()
