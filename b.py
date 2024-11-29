import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                             QFrame, QSizePolicy, QSpacerItem)
from PyQt5.QtGui import QPainter, QPainterPath, QColor, QPen, QFont
from PyQt5.QtCore import Qt, QRect

class ChevronProgressBar(QWidget):
    def __init__(self, steps):
        super().__init__()
        self.steps = steps
        self.current_step = 0
        self.initUI()

    def initUI(self):
        self.setMinimumHeight(50)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        width = self.width()
        height = self.height()
        step_width = width / len(self.steps)
        chevron_width = 20  # Width of the chevron point

        for i, step in enumerate(self.steps):
            # Define colors
            if i <= self.current_step:
                color = QColor("#2196F3")  # Blue for completed steps
                text_color = Qt.white
            else:
                color = QColor("#e0e0e0")  # Gray for incomplete steps
                text_color = Qt.black

            # Create chevron shape
            path = QPainterPath()
            x_start = i * step_width
            
            if i == 0:  # First step
                path.moveTo(x_start, 0)
                path.lineTo(x_start + step_width, 0)
                path.lineTo(x_start + step_width + chevron_width, height / 2)
                path.lineTo(x_start + step_width, height)
                path.lineTo(x_start, height)
                path.lineTo(x_start, 0)  # Straight left edge
            elif i == len(self.steps) - 1:  # Last step
                path.moveTo(x_start, 0)
                path.lineTo(x_start + step_width, 0)
                path.lineTo(x_start + step_width, height)  # Straight right edge
                path.lineTo(x_start, height)
                path.lineTo(x_start + chevron_width, height / 2)
            else:  # Middle steps
                path.moveTo(x_start, 0)
                path.lineTo(x_start + step_width, 0)
                path.lineTo(x_start + step_width + chevron_width, height / 2)
                path.lineTo(x_start + step_width, height)
                path.lineTo(x_start, height)
                path.lineTo(x_start + chevron_width, height / 2)

            # Fill chevron
            painter.fillPath(path, color)

            # Draw text
            text_rect = QRect(x_start, 0, step_width, height)
            painter.setPen(text_color)
            painter.drawText(text_rect, Qt.AlignCenter, step)
            
class HipOperationSoftware(QWidget):
    def __init__(self):
        super().__init__()
        self.steps = ['Preparation', 'Image Taking', 'Adjustment', 'Report', 'Completion']
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()
        
        # Progress bar
        self.progress_bar = ChevronProgressBar(self.steps)
        self.progress_bar.setFixedHeight(80)  # Set fixed height
        main_layout.addWidget(self.progress_bar)

        # Central content widget
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        
        # Title
        title_label = QLabel("Hip Operation Software")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(16)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(title_label)

        # Image placeholder
        image_placeholder = QLabel()
        image_placeholder.setFixedSize(300, 200)  # Set a fixed size for the image
        image_placeholder.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc;")
        image_placeholder.setAlignment(Qt.AlignCenter)
        image_placeholder.setText("Image Placeholder")
        content_layout.addWidget(image_placeholder, alignment=Qt.AlignCenter)

        # Content area
        self.content_label = QLabel()
        self.content_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(self.content_label)

        # Next button
        self.next_button = QPushButton('Complete & Proceed to Next Step')
        self.next_button.clicked.connect(self.handleNextStep)
        content_layout.addWidget(self.next_button, alignment=Qt.AlignCenter)

        # Add vertical spacers to center the content vertically
        main_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        main_layout.addWidget(content_widget, alignment=Qt.AlignCenter)
        main_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.setLayout(main_layout)
        self.updateContent()

        self.setStyleSheet("""
            ChevronProgressBar { font-size: 14px; }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QLabel {
                font-size: 16px;
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
        self.content_label.setText(f"Content for {self.steps[current_step]} step goes here.")
        
        if current_step == len(self.steps) - 1:
            self.next_button.hide()
            completion_label = QLabel("All steps completed!")
            completion_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
            self.layout().itemAt(2).widget().layout().addWidget(completion_label, alignment=Qt.AlignCenter)

def main():
    app = QApplication(sys.argv)
    ex = HipOperationSoftware()
    ex.setGeometry(100, 100, 800, 600)
    ex.setWindowTitle('Hip Operation Software')
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
