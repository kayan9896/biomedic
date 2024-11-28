import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor

class SurgeryProcessStep(QWidget):
    def __init__(self, text, completed=False):
        super().__init__()
        self.text = text
        self.completed = completed
        self.initUI()

    def initUI(self):
        layout = QHBoxLayout()
        self.setLayout(layout)
        
        label = QLabel(self.text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        if self.completed:
            palette = self.palette()
            palette.setColor(QPalette.ColorRole.Window, QColor(100, 149, 237))  # Light blue
            self.setAutoFillBackground(True)
            self.setPalette(palette)
        
        layout.addWidget(label)

class AngleBracketSeparator(QLabel):
    def __init__(self):
        super().__init__()
        self.setText(">")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

class SurgeonSoftwareView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Surgeon Software View')
        self.setMinimumSize(800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Process steps at the top
        process_widget = QWidget()
        process_layout = QHBoxLayout(process_widget)
        
        steps = [
            ("Preparation", True),
            ("Image Taking", True),
            ("Adjustment", True),
            ("Report", False),
            ("Completion", False)
        ]
        
        for i, (step_text, completed) in enumerate(steps):
            step = SurgeryProcessStep(step_text, completed)
            process_layout.addWidget(step)
            
            if i < len(steps) - 1:
                separator = AngleBracketSeparator()
                process_layout.addWidget(separator)

        main_layout.addWidget(process_widget)

        # Content area below process steps
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)

        # Left text box
        text_box = QFrame()
        text_box.setFrameShape(QFrame.Shape.Box)
        text_box.setMinimumSize(350, 400)
        text_label = QLabel("Step Details")
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text_layout = QVBoxLayout(text_box)
        text_layout.addWidget(text_label)

        # Right image box
        image_box = QFrame()
        image_box.setFrameShape(QFrame.Shape.Box)
        image_box.setMinimumSize(350, 400)
        image_label = QLabel("Rendered Image")
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_layout = QVBoxLayout(image_box)
        image_layout.addWidget(image_label)

        content_layout.addWidget(text_box)
        content_layout.addWidget(image_box)

        main_layout.addWidget(content_widget)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SurgeonSoftwareView()
    ex.show()
    sys.exit(app.exec())
