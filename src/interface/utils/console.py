from PyQt5.QtWidgets import QTextEdit

class SmartConsole(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)

        base_style = """
            QTextEdit {
                background-color: #1e1e1e;
                color: white;
                font-family: Consolas;
                border: none;
            }
        """

        self.scrollbar_style_hidden = base_style + """
            QScrollBar:vertical {
                background: black;
                width: 0px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: black;
                border-radius: 3px;
            }
        """

        self.scrollbar_style_visible = base_style + """
            QScrollBar:vertical {
                background: black;
                width: 6px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #888;
                min-height: 20px;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical:hover {
                background: #888;
                min-height: 20px;
                border-radius: 3px;
                width: 10px;
            }
            QScrollBar::handle:vertical:hover {
                background: #555;
            }
        """

        self.setStyleSheet(self.scrollbar_style_hidden)

    def enterEvent(self, event):
        self.setStyleSheet(self.scrollbar_style_visible)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setStyleSheet(self.scrollbar_style_hidden)
        super().leaveEvent(event)
