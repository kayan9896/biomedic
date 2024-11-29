import sys
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPainterPath, QColor

class AngleBracketFrame(QFrame):
    def __init__(self, text, is_completed=False, total_steps=5, step_index=0):
        super().__init__()
        self.text = text
        self.is_completed = is_completed
        self.total_steps = total_steps
        self.step_index = step_index
        self.setSizePolicy(self.sizePolicy().Expanding, self.sizePolicy().Fixed)
        self.setFixedHeight(40)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        width = self.width()
        height = self.height()
        
        # Define the path for the angle bracket shape
        path = QPainterPath()
        if self.step_index == 0:  # First step
            path.moveTo(0, 0)
            path.lineTo(width - 20, 0)
        else:
            path.moveTo(20, 0)
            path.lineTo(width - 20, 0)
        
        path.lineTo(width, height / 2)
        path.lineTo(width - 20, height)
        
        if self.step_index == 0:  # First step
            path.lineTo(0, height)
            path.lineTo(0, 0)
        else:
            path.lineTo(20, height)
            path.lineTo(0, height / 2)
            path.lineTo(20, 0)

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
        self.initUI()
    
    def initUI(self):
        # Main vertical layout
        main_layout = QVBoxLayout()
        
        # Process steps
        self.steps = ['Preparation', 'Image Taking', 'Adjustment', 'Report', 'Completion']
        
        # Horizontal layout for process steps
        self.process_layout = QHBoxLayout()
        self.process_layout.setSpacing(0)  # Remove spacing between frames
        self.process_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        
        self.update_process_steps()
        
        main_layout.addLayout(self.process_layout)
        
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
        next_button = QPushButton('Next Step')
        next_button.clicked.connect(self.next_step)
        main_layout.addWidget(next_button)
        
        self.setLayout(main_layout)
        self.setWindowTitle('Surgeon Software View')
        self.setGeometry(100, 100, 800, 600)
        self.show()
    
    def update_process_steps(self):
        # Clear existing widgets
        for i in reversed(range(self.process_layout.count())): 
            self.process_layout.itemAt(i).widget().setParent(None)
        
        # Add new widgets
        for i, step in enumerate(self.steps):
            step_frame = AngleBracketFrame(step, 
                                           i <= self.current_step, 
                                           len(self.steps), 
                                           i)
            self.process_layout.addWidget(step_frame)
    
    def next_step(self):
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            self.update_process_steps()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    view = SurgeonSoftwareView()
    sys.exit(app.exec_())
