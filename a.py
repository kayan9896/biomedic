import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QFrame)
from PyQt5.QtGui import QPainter, QPainterPath, QColor, QPen, QFont
from PyQt5.QtCore import Qt, QRect, QSize

class ChevronProgressBar(QWidget):
    def __init__(self, steps):
        super().__init__()
        self.steps = steps
        self.current_step = 0
        self.initUI()

    def initUI(self):
        self.setFixedHeight(60)  # Fixed height for progress bar

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        width = self.width()
        height = self.height()
        step_width = width / len(self.steps)
        chevron_width = 20

        # Set larger font for step text
        font = painter.font()
        font.setPointSize(12)  # Larger text
        font.setBold(True)     # Bold text
        painter.setFont(font)

        for i, step in enumerate(self.steps):
            if i <= self.current_step:
                color = QColor("#2196F3")
                text_color = Qt.white
            else:
                color = QColor("#e0e0e0")
                text_color = Qt.black

            path = QPainterPath()
            x_start = i * step_width
            
            if i == 0:  # First step
                path.moveTo(x_start, 0)
                path.lineTo(x_start + step_width, 0)
                path.lineTo(x_start + step_width + chevron_width, height / 2)
                path.lineTo(x_start + step_width, height)
                path.lineTo(x_start, height)
                path.lineTo(x_start, 0)
            elif i == len(self.steps) - 1:  # Last step
                path.moveTo(x_start, 0)
                path.lineTo(x_start + step_width, 0)
                path.lineTo(x_start + step_width, height)
                path.lineTo(x_start, height)
                path.lineTo(x_start + chevron_width, height / 2)
            else:  # Middle steps
                path.moveTo(x_start, 0)
                path.lineTo(x_start + step_width, 0)
                path.lineTo(x_start + step_width + chevron_width, height / 2)
                path.lineTo(x_start + step_width, height)
                path.lineTo(x_start, height)
                path.lineTo(x_start + chevron_width, height / 2)

            painter.fillPath(path, color)

            text_rect = QRect(x_start, 0, step_width, height)
            painter.setPen(text_color)
            painter.drawText(text_rect, Qt.AlignCenter, step)

class ContentArea(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        
        # Title
        self.title = QLabel()
        title_font = self.title.font()
        title_font.setPointSize(16)
        title_font.setBold(True)
        self.title.setFont(title_font)
        self.title.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title)

        # Image placeholder
        self.image_placeholder = QFrame()
        self.image_placeholder.setStyleSheet("""
            QFrame {
                background-color: #f0f0f0;
                border: 2px dashed #cccccc;
                border-radius: 5px;
            }
        """)
        self.image_placeholder.setFixedSize(400, 300)
        layout.addWidget(self.image_placeholder, 0, Qt.AlignHCenter)

        # Content text
        self.content = QLabel()
        self.content.setWordWrap(True)
        self.content.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.content)

        # Next button
        self.next_button = QPushButton('Complete & Proceed to Next Step')
        layout.addWidget(self.next_button, 0, Qt.AlignHCenter)

        self.setLayout(layout)

class HipOperationSoftware(QWidget):
    def __init__(self):
        super().__init__()
        self.steps = ['Preparation', 'Image Taking', 'Adjustment', 'Report', 'Completion']
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()
        
        # Progress bar
        self.progress_bar = ChevronProgressBar(self.steps)
        main_layout.addWidget(self.progress_bar)

        # Content area
        self.content_area = ContentArea()
        self.content_area.next_button.clicked.connect(self.handleNextStep)
        
        # Center the content area
        content_container = QHBoxLayout()
        content_container.addStretch()
        content_container.addWidget(self.content_area)
        content_container.addStretch()
        
        main_layout.addLayout(content_container)
        main_layout.addStretch()  # Push everything up

        self.setLayout(main_layout)
        self.updateContent()

        self.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 16px;
                min-width: 250px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QLabel {
                font-size: 14px;
                margin: 10px;
            }
        """)

    def handleNextStep(self):
        if self.progress_bar.current_step < len(self.steps) - 1:
            self.progress_bar.current_step += 1
            self.progress_bar.update()
            self.updateContent()

    def updateContent(self):
        current_step = self.progress_bar.current_step
        self.content_area.title.setText(self.steps[current_step])
        self.content_area.content.setText(f"Content for {self.steps[current_step]} step goes here.")
        
        if current_step == len(self.steps) - 1:
            self.content_area.next_button.hide()
            completion_label = QLabel("All steps completed!")
            completion_label.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 16px;")
            self.content_area.layout().addWidget(completion_label, 0, Qt.AlignHCenter)

def main():
    app = QApplication(sys.argv)
    ex = HipOperationSoftware()
    ex.setGeometry(100, 100, 1000, 600)
    ex.setWindowTitle('Hip Operation Software')
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
