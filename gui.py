from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QFrame, QStackedWidget, QGridLayout)
from PyQt5.QtGui import QPainter, QPainterPath, QColor, QPen, QFont, QPixmap, QMovie, QImage
from PyQt5.QtCore import Qt, QRect, QSize
import cv2

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
        self.current_step = ""
        self.initUI()

    def initUI(self):
        self.main_layout = QVBoxLayout()
        
        # Title
        self.title = QLabel()
        title_font = self.title.font()
        title_font.setPointSize(16)
        title_font.setBold(True)
        self.title.setFont(title_font)
        self.title.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.title)

        # Stacked widget to switch between different content
        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget)

        # Create pages for different steps
        self.create_default_page()
        self.create_image_taking_page()
        self.create_result_page()

        # Content text
        self.content = QLabel()
        self.content.setWordWrap(True)
        self.content.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.content)

        # Next button
        self.next_button = QPushButton('Complete & Proceed to Next Step')
        self.main_layout.addWidget(self.next_button, 0, Qt.AlignHCenter)

        self.setLayout(self.main_layout)

    def create_default_page(self):
        default_page = QWidget()
        default_layout = QVBoxLayout()

        # Title for image number
        self.default_title = QLabel()
        title_font = self.default_title.font()
        title_font.setPointSize(14)
        title_font.setBold(True)
        self.default_title.setFont(title_font)
        self.default_title.setAlignment(Qt.AlignCenter)
        default_layout.addWidget(self.default_title)

        # Single empty placeholder
        self.placeholder = QFrame()
        self.placeholder.setFixedSize(400, 300)
        self.placeholder.setStyleSheet("""
            QFrame {
                background-color: #f0f0f0;
                border: 2px dashed #cccccc;
                border-radius: 5px;
            }
        """)
        default_layout.addWidget(self.placeholder, 0, Qt.AlignHCenter)

        default_page.setLayout(default_layout)
        self.stacked_widget.addWidget(default_page)

    def create_image_taking_page(self):
        image_taking_page = QWidget()
        image_layout = QHBoxLayout()

        # Left image placeholder (heatmap)
        self.heatmap_label = QLabel()
        self.heatmap_label.setFixedSize(400, 300)
        self.heatmap_label.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                border: 2px solid #cccccc;
                border-radius: 5px;
            }
        """)
        # Load the heatmap image
        heatmap = QPixmap('heatmap.png')
        if not heatmap.isNull():
            self.heatmap_label.setPixmap(heatmap.scaled(
                self.heatmap_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        image_layout.addWidget(self.heatmap_label)

        # Right image placeholder (camera feed or gif)
        self.camera_label = QLabel()
        self.camera_label.setFixedSize(400, 300)
        self.camera_label.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                border: 2px solid #cccccc;
                border-radius: 5px;
            }
        """)
        image_layout.addWidget(self.camera_label)

        # Create QMovie for gif
        self.waiting_movie = QMovie('gf.gif')
        self.waiting_movie.setScaledSize(self.camera_label.size())

        image_taking_page.setLayout(image_layout)
        self.stacked_widget.addWidget(image_taking_page)

    def create_result_page(self):
        result_page = QWidget()
        result_layout = QVBoxLayout()

        # Create a 2x2 grid for images
        grid_layout = QGridLayout()
        self.result_labels = []
        for i in range(4):
            label = QLabel()
            label.setFixedSize(300, 225)
            label.setStyleSheet("border: 1px solid black;")
            self.result_labels.append(label)
            grid_layout.addWidget(label, i // 2, i % 2)

        result_layout.addLayout(grid_layout)

        # Redo button
        self.redo_button = QPushButton("Redo Image Capture")
        result_layout.addWidget(self.redo_button, alignment=Qt.AlignCenter)

        result_page.setLayout(result_layout)
        self.stacked_widget.addWidget(result_page)

    def show_grid_view(self, images):
        for i, image in enumerate(images):
            pixmap = QPixmap.fromImage(image).scaled(
                self.grid_labels[i].size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.grid_labels[i].setPixmap(pixmap)
        self.stacked_widget.setCurrentIndex(2)  # Assuming grid view is index 2
    
    def update_camera_image(self, qimage):
        if self.current_step == "Image Taking":
            self.waiting_movie.stop()
            pixmap = QPixmap.fromImage(qimage).scaled(
                self.camera_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.camera_label.setPixmap(pixmap)

    def show_waiting_gif(self):
        if self.current_step == "Image Taking":
            self.camera_label.setMovie(self.waiting_movie)
            self.waiting_movie.start()

    def set_step(self, step):
        self.current_step = step
        if step == "Image Taking":
            self.stacked_widget.setCurrentIndex(1)  # Show image taking page
            self.show_waiting_gif()  # Start with waiting gif
        else:
            self.stacked_widget.setCurrentIndex(0)  # Show default page
            self.waiting_movie.stop()

    def show_default_view(self, image_num):
        self.default_title.setText(f"Collect Image {image_num}")
        self.stacked_widget.setCurrentIndex(0)

    def show_capture_view(self):
        self.stacked_widget.setCurrentIndex(1)
        self.show_waiting_gif()

    def show_result_view(self, images):
        for i, image in enumerate(images):
            if image is not None:
                qimage = self.convert_cv_to_qimage(image)
                pixmap = QPixmap.fromImage(qimage).scaled(
                    self.result_labels[i].size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.result_labels[i].setPixmap(pixmap)
        self.stacked_widget.setCurrentIndex(2)

    def convert_cv_to_qimage(self, cv_img):
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        return QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)


class HipOperationSoftware(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.steps = ['Preparation', 'Image Taking', 'Adjustment', 'Report', 'Completion']
        self.initUI()
        
        # Connect signals
        self.controller.frame_ready.connect(self.content_area.update_camera_image)
        self.controller.validation_failed.connect(self.show_validation_error)
        self.controller.validation_passed.connect(self.handle_validation_passed)
        self.controller.waiting_for_change.connect(self.content_area.show_waiting_gif)
        self.controller.show_default_view.connect(self.content_area.show_default_view)
        self.controller.show_capture_view.connect(self.content_area.show_capture_view)
        self.controller.show_result_view.connect(self.show_result_view)
        
        self.content_area.redo_button.clicked.connect(self.controller.redo_image_sequence)



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

    def updateContent(self):
        current_step = self.progress_bar.current_step
        step_name = self.steps[current_step]
        self.content_area.set_step(step_name)
        self.content_area.title.setText(step_name)
        
        if step_name == "Image Taking":
            self.controller.start_image_sequence()
        else:
            self.controller.stop()
        
        if current_step == len(self.steps) - 1:
            self.controller.stop()  # Completely stop the controller
            self.content_area.next_button.hide()
            completion_label = QLabel("All steps completed!")
            completion_label.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 16px;")
            self.content_area.layout().addWidget(completion_label, 0, Qt.AlignHCenter)


    def handleNextStep(self):
        if self.progress_bar.current_step < len(self.steps) - 1:
            self.progress_bar.current_step += 1
            self.progress_bar.update()
            self.updateContent()

    def show_validation_error(self, message):
        self.content_area.content.setText(message)

    def handle_validation_passed(self):
        self.controller.handle_successful_capture()

    def show_result_view(self):
        images = self.controller.model.get_stored_images()
        self.content_area.show_result_view(images)
       
