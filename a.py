import sys
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPainterPath, QColor

class AngleBracketFrame(QFrame):
    def __init__(self, text, is_completed=False):
        super().__init__()
        self.text = text
        self.is_completed = is_completed
        self.setFixedSize(100, 40)  # Fixed size to ensure width > height

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Define the path for the angle bracket shape
        path = QPainterPath()
        path.moveTo(0, 0)
        path.lineTo(80, 0)
        path.lineTo(100, 20)
        path.lineTo(80, 40)
        path.lineTo(0, 40)
        path.lineTo(20, 20)
        path.lineTo(0, 0)

        # Fill with blue if completed, otherwise just stroke
        if self.is_completed:
            painter.fillPath(path, QColor("#3498db"))
        painter.strokePath(path, painter.pen())

        # Draw text
        painter.drawText(self.rect(), Qt.AlignCenter, self.text)

class SurgeonSoftwareView(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        # Main vertical layout
        main_layout = QVBoxLayout()
        
        # Process steps
        steps = ['Preparation', 'Image Taking', 'Adjustment', 'Report', 'Completion']
        completed_steps = 2  # Assuming first two steps are completed
        
        # Horizontal layout for process steps
        process_layout = QHBoxLayout()
        process_layout.setSpacing(0)  # Remove spacing between frames
        
        for i, step in enumerate(steps):
            step_frame = AngleBracketFrame(step, i < completed_steps)
            process_layout.addWidget(step_frame)

        process_layout.addStretch()
        main_layout.addLayout(process_layout)
        
        # Content area (text and image placeholders)
        content_layout = QHBoxLayout()
        
        # Text placeholder
        text_placeholder = QFrame()
        text_placeholder.setFrameShape(QFrame.StyledPanel)
        text_placeholder.setStyleSheet("background-color: #ecf0f1;")
        text_label = QLabel("Text Content Placeholder")
        text_label.setAlignment(Qt.AlignCenter)
        text_layout = QVBoxLayout()
        text_layout.addWidget(text_label)
        text_placeholder.setLayout(text_layout)
        content_layout.addWidget(text_placeholder)
        
        # Image placeholder
        image_placeholder = QFrame()
        image_placeholder.setFrameShape(QFrame.StyledPanel)
        image_placeholder.setStyleSheet("background-color: #bdc3c7;")
        image_label = QLabel("Image Placeholder")
        image_label.setAlignment(Qt.AlignCenter)
        image_layout = QVBoxLayout()
        image_layout.addWidget(image_label)
        image_placeholder.setLayout(image_layout)
        content_layout.addWidget(image_placeholder)
        
        main_layout.addLayout(content_layout)
        
        self.setLayout(main_layout)
        self.setWindowTitle('Surgeon Software View')
        self.setGeometry(100, 100, 800, 600)
        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    view = SurgeonSoftwareView()
    sys.exit(app.exec_())
