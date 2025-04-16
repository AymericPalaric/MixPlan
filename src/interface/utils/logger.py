from PyQt5.QtCore import QObject, pyqtSignal

__all__ = ["gui_logger"]

class GuiLogger(QObject):
    log_signal = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()

    def log(self, *messages, level="INFO"):
        """Log messages to the GUI console."""
        message = " ".join(map(str, messages))
        self.log_signal.emit(message, level.upper())

# Instance globale
gui_logger = GuiLogger()