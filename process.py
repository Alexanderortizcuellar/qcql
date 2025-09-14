from PyQt5.QtCore import pyqtSignal, QProcess
from PyQt5.QtWidgets import QApplication, QMainWindow


class CounterProcess(QProcess):
    countFinished = pyqtSignal(int)

    def __init__(self, parent=None, filename: str = ""):
        super().__init__(parent)
        self.setProgram("./data/counter.exe")
        self.setArguments([f"{filename}"])
        self.finished.connect(self.handle_finished)

    def handle_finished(self, _, __):
        output = self.readAllStandardOutput().data().decode()
        fixed_count = output.split(":")[1]
        self.countFinished.emit(int(fixed_count))
        self.deleteLater()


class CQLProcess(QProcess):
    messageReceived = pyqtSignal(str)
    errorReceived = pyqtSignal(str)
    errorsReceivedFromStderr = pyqtSignal(str)
    progressUpdated = pyqtSignal(int)
    statsReceived = pyqtSignal(dict)
    gamesReceived = pyqtSignal(str)
    finishedEXecution = pyqtSignal(int, int, str)
    finishedSuccessfully = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setProgram("cql")
        self.readyReadStandardOutput.connect(self.read_data)
        self.finished.connect(self.on_finished)
        self.readyReadStandardError.connect(self.read_error)
        self.buffer = []
        self.collectingMessage = None  # "message" | "error" | None
        self.collecting_games = False
        self.gamedata = ""

    def search(self, cqlquery: str, pgnfile: str):
        with open("temp.cql", "w") as f:
            f.write(cqlquery)
        cqlfile = "temp.cql"
        self.setArguments(["-gui", "--guipgnstdout", "-input", pgnfile, cqlfile])
        self.start()

    def paginate_games(self, cqlfile: str, start, end):
        self.setArguments(
            ["-gui", "--guipgnstdout", "-gamenumber", f"{start}", f"{end}", cqlfile]
        )
        self.start()

    def read_error(self):
        errors = self.readAllStandardError()
        self.errorsReceivedFromStderr.emit(errors.data().decode())

    def on_finished(self, exitCode, exitStatus):
        output = self.readAllStandardOutput().data().decode()
        self.finishedEXecution.emit(exitCode, exitStatus, output)

    def read_data(self):
        while self.canReadLine():
            line: str | None = self.readLine().data().decode("utf-8", errors="replace")
            if not line:
                continue

            # Start collecting message
            if line.startswith("<CqlGuiMessage>"):
                self.buffer = []
                self.collectingMessage = "message"
                continue
            if line.startswith("<CqlGuiError>"):
                self.buffer = []
                self.collectingMessage = "error"
                continue

            # End collecting message
            if (
                line.startswith("</CqlGuiMessage>")
                and self.collectingMessage == "message"
            ):
                self.messageReceived.emit("\n".join(self.buffer))
                self.buffer = []
                self.collectingMessage = None
                continue

            if line.startswith("</CqlGuiError>") and self.collectingMessage == "error":
                self.errorReceived.emit("\n".join(self.buffer))
                self.buffer = []
                self.collectingMessage = None
                continue

            # Collect intermediate lines
            if self.collectingMessage in ("message", "error"):
                self.buffer.append(line.strip())
                continue

            # Normal exit
            if line.startswith("<CqlGuiNormalExit>"):
                self.finishedSuccessfully.emit()
                continue

            # Variables
            if line.startswith("<CqlGuiVariable>"):
                parts = line.split(maxsplit=2)
                if len(parts) >= 3:
                    _, name, value = parts
                    self.handle_variable(name, value)
                continue

            if line.startswith("<CqlGuiPgn"):
                self.collecting_games = True  # experimental option disabled for now # TODO improve maybe use rust

            if line.startswith("</CqlGuiPgn>"):
                self.collecting_games = False
                self.gamesReceived.emit(self.gamedata)
                self.gamedata = ""

            if self.collecting_games and not line.strip().startswith("<CqlGuiPgn"):
                self.gamedata += line

    def handle_variable(self, name: str, value: str):
        if name == "currentgamenumber":
            try:
                self.progressUpdated.emit(int(value))
            except ValueError:
                pass
        else:
            # You could keep stats in a dict and emit updates
            self.statsReceived.emit({name: value.strip()})


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        """ self.process = CQLProcess(self)

        self.process.messageReceived.connect(lambda msg: print("MESSAGE:", msg))
        self.process.errorReceived.connect(lambda err: print("ERROR:", err))
        self.process.errorsReceivedFromStderr.connect(lambda err: print("ERROR:", err))
        self.process.progressUpdated.connect(lambda n: print("Progress:", n))
        self.process.statsReceived.connect(lambda d: print("STAT:", d))
        self.process.finished.connect(
            lambda: print("Finished", self.process.exitStatus())
        )
        self.process.finishedSuccessfully.connect(lambda: print("Finished OK"))

        self.process.paginate_games("greek.cql", 100, 2629) """

        counter_process = CounterProcess(self, "lichess.pgn")
        counter_process.start()


if __name__ == "__main__":
    app = QApplication([])
    window = Window()
    window.show()
    app.exec_()
