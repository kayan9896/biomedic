import sys
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPainterPath, QColor

class AngleBracketFrame(QFrame):
    def __init__(self, text, is_completed=False):
        super().__init__()
        self.text = text
        self.is_completed = is_completed
        self.setMinimumHeight(40)  # Fixed height

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        width = self.width()
        height = self.height()
        bracket_depth = 20  # The depth of the angle

        # Define the path for the angle bracket shape
        path = QPainterPath()
        path.moveTo(0, 0)
        path.lineTo(width - bracket_depth, 0)
        path.lineTo(width, height/2)
        path.lineTo(width - bracket_depth, height)
        path.lineTo(0, height)
        path.lineTo(bracket_depth, height/2)
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
        self.current_step = 0
        self.steps = ['Preparation', 'Image Taking', 'Adjustment', 'Report', 'Completion']
        self.initUI()
    
    def initUI(self):
        # Main vertical layout
        main_layout = QVBoxLayout()
        
        # Horizontal layout for process steps
        self.process_layout = QHBoxLayout()
        self.process_layout.setSpacing(0)  # Remove spacing between frames
        self.process_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        
        self.step_frames = []
        for step in self.steps:
            step_frame = AngleBracketFrame(step)
            self.step_frames.append(step_frame)
            self.process_layout.addWidget(step_frame, 1)  # Equal stretch factor

        process_widget = QWidget()
        process_widget.setLayout(self.process_layout)
        main_layout.addWidget(process_widget)
        
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

        # Next button
        next_button = QPushButton("Next Step")
        next_button.clicked.connect(self.next_step)
        main_layout.addWidget(next_button)
        
        self.setLayout(main_layout)
        self.setWindowTitle('Surgeon Software View')
        self.setGeometry(100, 100, 800, 600)
        self.update_steps()
        self.show()

    def next_step(self):
        if self.current_step < len(self.steps):
            self.current_step += 1
            self.update_steps()

    def update_steps(self):
        for i, frame in enumerate(self.step_frames):
            frame.is_completed = i < self.current_step
            frame.update()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    view = SurgeonSoftwareView()
    sys.exit(app.exec_())
