from PyQt5.QtCore import QThread, pyqtSignal, QTimer
import cv2
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication
import sys
from model import CameraModel
from gui import HipOperationSoftware

class CameraController(QThread):
    frame_ready = pyqtSignal(QImage)
    validation_failed = pyqtSignal(str)
    validation_passed = pyqtSignal()
    waiting_for_change = pyqtSignal()
    show_default_view = pyqtSignal(int)  # Signal to show default view with image number
    show_capture_view = pyqtSignal()
    show_grid_view = pyqtSignal(list)
    show_result_view = pyqtSignal() 

    def __init__(self, model):
        super().__init__()
        self.model = model
        self.is_running = False
        self.is_capturing = False

    def run(self):
        while self.is_running:
            if self.is_capturing:
                if self.model.read_camera():
                    if self.model.has_frame_changed():
                        if self.model.validate_frame():
                            self._process_valid_frame()
                            self.stop_capture()  # Stop capturing after valid frame
                        else:
                            self._process_invalid_frame()
                    else:
                        if self.model.last_frame is None:
                            self.waiting_for_change.emit()
            self.msleep(30)

    def start_image_sequence(self):
        self.model.current_image_num = 1
        self.show_default_view.emit(1)
        QTimer.singleShot(3000, self.start_capture)

    def handle_successful_capture(self):
        self.model.store_current_image()
        self.stop_capture()
        
        if self.model.current_image_num < 4:
            QTimer.singleShot(5000, lambda: self.prepare_next_image())
        else:
            self.is_running = False
            self.show_result_view.emit()

    def prepare_next_image(self):
        self.model.current_image_num += 1
        self.show_default_view.emit(self.model.current_image_num)
        QTimer.singleShot(3000, self.start_capture)

    def start_capture(self):
        self.show_capture_view.emit()
        self.is_capturing = True
        if not self.isRunning():
            self.is_running = True
            self.start()

    def redo_image_sequence(self):
        self.model.reset_images()
        self.start_image_sequence()

    def stop_capture(self):
        self.is_capturing = False

    def stop(self):
        self.is_running = False
        self.is_capturing = False
        self.wait()

    def _process_valid_frame(self):
        frame = self.model.get_current_frame()
        qimage = self._convert_cv_to_qimage(frame)
        self.frame_ready.emit(qimage)
        self.validation_passed.emit()

    def _process_invalid_frame(self):
        frame = self.model.get_current_frame()
        cv2.putText(frame, "Validation Failed", (50, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        qimage = self._convert_cv_to_qimage(frame)
        self.frame_ready.emit(qimage)
        self.validation_failed.emit("Image validation failed")

    def _convert_cv_to_qimage(self, cv_img):
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        height, width, channel = rgb_image.shape
        bytes_per_line = 3 * width
        return QImage(rgb_image.data, width, height, bytes_per_line, QImage.Format_RGB888)
    
def main():
    app = QApplication(sys.argv)
    
    model = CameraModel()
    controller = CameraController(model)
    
    ex = HipOperationSoftware(controller)
    ex.setGeometry(100, 100, 1000, 600)
    ex.setWindowTitle('Hip Operation Software')
    ex.show()
    
    # The controller thread will start only when needed
    result = app.exec_()
    controller.stop()  # Ensure controller is stopped when app closes
    sys.exit(result)

if __name__ == '__main__':
    main()