import sys
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPolygon, QColor, QPalette, QPainter
from PyQt5.QtCore import QPoint

class AngleBracketFrame(QFrame):
    def paintEvent(self, event):
        painter = QPainter(self)
        color = QColor("#3498db") if self.property("completed") else QColor("#ffffff")
        painter.fillRect(self.rect(), color)
        
        polygon = QPolygon([
            QPoint(0, 0),
            QPoint(self.width() - 10, 0),
            QPoint(self.width(), self.height() / 2),
            QPoint(self.width() - 10, self.height()),
            QPoint(0, self.height())
        ])
        painter.setPen(Qt.black)
        painter.drawPolygon(polygon)

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
        process_layout.setSpacing(0)  # Remove spacing between steps
        
        for i, step in enumerate(steps):
            step_frame = AngleBracketFrame()
            step_frame.setProperty("completed", i < completed_steps)
            step_frame.setFixedHeight(40)  # Set a fixed height
            
            step_layout = QVBoxLayout()
            step_label = QLabel(step)
            step_label.setAlignment(Qt.AlignCenter)
            step_layout.addWidget(step_label)
            step_frame.setLayout(step_layout)
            
            process_layout.addWidget(step_frame)
        
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
