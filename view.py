import sys
import math
import time
from PyQt5.QtWidgets import (QApplication, QGraphicsTextItem, QGraphicsView, QGraphicsScene, QGraphicsItem, 
                             QGraphicsEllipseItem, QGraphicsLineItem, QMainWindow, 
                             QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QTabBar,
                             QTabWidget, QProgressBar, QToolButton, QStyleOptionTab, QStylePainter)
from PyQt5.QtGui import QImage, QPixmap, QPen, QTransform, QIcon, QPainterPath, QPainter, QPolygon
from PyQt5.QtCore import Qt, QRectF, QPointF, QTimer, QSize, QPoint

class PointItem(QGraphicsEllipseItem):
    """Custom QGraphicsEllipseItem to represent a point with drag and click behavior."""
    def __init__(self, v, x, y, radius=5):
        super().__init__(x - radius, y - radius, radius * 2, radius * 2)
        self.setBrush(Qt.red)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setCursor(Qt.PointingHandCursor)
        self.radius = radius
        self.viewer = v
        self.click = 1

    def mousePressEvent(self, event):
        """Handle mouse press event to add a point."""
        if self.click == 0:
            return
        if event.button() == Qt.LeftButton:
            self.viewer.eventFilter(self.viewer, event)

    def mouseReleaseEvent(self, event):
        if self.click == 0:
            self.click = 1
            return
        if event.button() == Qt.LeftButton:
            if event.scenePos() == event.buttonDownScenePos(Qt.LeftButton):
                self.viewer.remove_point(self)
            self.viewer.update_lines()
            # Notify controller to update distances
            if hasattr(self.viewer, 'controller'):
                self.viewer.controller.update_distances()
            super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        self.setPos(self.mapToScene(event.pos()))
        self.viewer.update_lines()
        # Notify controller to update distances
        if hasattr(self.viewer, 'controller'):
            self.viewer.controller.update_distances()


class ImageViewer(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.curves = []
        self.lines=[]
        self.distance_labels=[]

    def update_progress_bar(self):
        current_value = self.progress_bar.value()
        if current_value < self.progress_bar.maximum():
           self.progress_bar.setValue(current_value + 10)

    def hide_progress_bar(self):
        self.progress_bar.hide()
        self.timer.stop()

    def load_image(self, image_path):
        if isinstance(image_path,str):
            self.scene.clear()
            self.progress_bar = QProgressBar()
            self.progress_bar.setMaximum(100)
            self.scene.addWidget(self.progress_bar)
            self.progress_bar.setValue(0)
            self.progress_bar.show()
            self.timer = QTimer()
            self.timer.timeout.connect(self.update_progress_bar)
            self.timer.start(100)
            image = QImage(image_path)
        else:
            image=QImage(image_path, image_path.shape[1], image_path.shape[0], QImage.Format_BGR888)
        
        def load(image):
            pixmap = QPixmap.fromImage(image)
            self.hide_progress_bar()
            pixmap_item = self.scene.addPixmap(pixmap)
            pixmap_item.setZValue(-1)
            self.setSceneRect(QRectF(pixmap.rect()))

        QTimer.singleShot(3000, lambda:load(image))

    
    def switch_image(self, image_path):  # New method to switch images
        self.scene.clear()  # Clear the current scene
        self.load_image(image_path)


    def clear_all_points(self):
        """Clear all points, lines and labels from the scene."""
        for curve in self.curves:
            for point in curve:
                self.scene.removeItem(point)
        for line in self.lines:
            self.scene.removeItem(line)
        for label in self.distance_labels:
            self.scene.removeItem(label)
        self.curves.clear()
        self.lines.clear()
        self.distance_labels.clear()

    def add_curve_points(self, coords):
        """Add a new curve with its points."""
        curve_points = []
        for x, y in coords:
            point = PointItem(self, 0, 0)
            self.scene.addItem(point)
            point.setPos(x, y)
            point.installSceneEventFilter(point)
            curve_points.append(point)
        self.curves.append(curve_points)
        self.update_lines()

    def get_curve_coordinates(self):
        """Return the coordinates of all curves for the controller."""
        all_coords = []
        for curve in self.curves:
            curve_coords = []
            for point in curve:
                pos = point.scenePos()
                curve_coords.append((pos.x(), pos.y()))
            all_coords.append(curve_coords)
        return all_coords

    def update_distance_labels(self, all_distances):
        """Update distance labels using distances calculated by controller."""
        # Clear existing labels
        for label in self.distance_labels:
            self.scene.removeItem(label)
        self.distance_labels.clear()

        # Create new labels
        for curve_index, curve in enumerate(self.curves):
            if len(curve) >= 2:
                curve_distances = all_distances[curve_index]
                for i, distance in enumerate(curve_distances):
                    p1 = curve[i].scenePos()
                    p2 = curve[i+1].scenePos()
                    
                    # Calculate middle point for label placement
                    mid_x = (p1.x() + p2.x()) / 2
                    mid_y = (p1.y() + p2.y()) / 2
                    
                    # Create and position label
                    label = QGraphicsTextItem(f"{distance:.1f}")
                    label.setDefaultTextColor(Qt.blue)
                    label.setPos(mid_x, mid_y)
                    self.scene.addItem(label)
                    self.distance_labels.append(label)

    def update_lines(self):
        """Update all curve lines."""
        # Remove existing lines
        for line in self.lines:
            self.scene.removeItem(line)
        self.lines.clear()

        # Create new lines for each curve
        for curve in self.curves:
            if len(curve) >= 2:
                for i in range(len(curve) - 1):
                    line = QGraphicsLineItem()
                    pen = QPen(Qt.blue, 2)
                    line.setPen(pen)
                    
                    p1 = curve[i].scenePos()
                    p2 = curve[i + 1].scenePos()
                    
                    line.setLine(p1.x(), p1.y(), p2.x(), p2.y())
                    self.scene.addItem(line)
                    self.lines.append(line)

    def remove_point(self, point):
        """Remove a point and update its curve."""
        for curve in self.curves:
            if point in curve:
                curve.remove(point)
                self.scene.removeItem(point)
                if len(curve) == 0:
                    self.curves.remove(curve)
                break
        self.update_lines()
        # Notify controller to update distances
        if hasattr(self, 'controller'):
            self.controller.update_distances()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            scene_pos = self.mapToScene(event.pos())
            items_at_pos = self.scene.items(QPointF(scene_pos))
            for i in items_at_pos:
                if isinstance(i, PointItem):
                    super().mousePressEvent(event)
                    return
            # Create a new curve with this point
            new_point = PointItem(self, 0, 0)
            self.scene.addItem(new_point)
            new_point.setPos(scene_pos.x(), scene_pos.y())
            new_point.installSceneEventFilter(new_point)
            self.curves.append([new_point])
        super().mousePressEvent(event)

    def zoom_in(self):
        """Zoom in on the image."""
        self.scale(1.2, 1.2)

    def zoom_out(self):
        """Zoom out of the image."""
        self.scale(0.8, 0.8)

class ControlPanel(QWidget):
    def __init__(self, viewer, controller): #Add controller as an argument
        super().__init__()
        self.viewer = viewer
        self.controller = controller #Store the controller instance
        self.setup_ui()

    def setup_ui(self):
        control_layout = QVBoxLayout(self)

        zoom_in_button = QPushButton("Zoom In")
        zoom_in_button.clicked.connect(self.viewer.zoom_in)
        control_layout.addWidget(zoom_in_button)

        zoom_out_button = QPushButton("Zoom Out")
        zoom_out_button.clicked.connect(self.viewer.zoom_out)
        control_layout.addWidget(zoom_out_button)

        self.viewer.viewer_distance_label = QLabel("Distance: N/A")
        control_layout.addWidget(self.viewer.viewer_distance_label)

        button_layout = QHBoxLayout()
        control_layout.addLayout(button_layout)

        self.button1 = QToolButton()
        self.button1.setIcon(QIcon('C:/Users/A4ssg/Downloads/gf.gif'))
        self.button1.setIconSize(QSize(32, 32))
        self.button1.setToolTip("Toggle Image")
        self.button1.setCheckable(True)  # Make it a toggle button
        # Connect button1 to the controller
        self.button1.clicked.connect(self.controller.toggle_image)  
        button_layout.addWidget(self.button1)

        self.button2 = QToolButton()  # Add your button2 and its functionality as needed
        self.button2.setIcon(QIcon("C:/Users/A4ssg/Downloads/heatmap.png"))
        self.button2.setIconSize(QSize(32, 32))
        self.button2.setToolTip("Description for Button 2")  # Add your tooltip
        self.button2.clicked.connect(self.controller.add_sample_curve)
        button_layout.addWidget(self.button2)

class HexagonTabBar(QTabBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDrawBase(False)
        self.setExpanding(False)

    def tabSizeHint(self, index):
        return QSize(100, 40)

    def paintEvent(self, event):
        painter = QStylePainter(self)
        option = QStyleOptionTab()

        for index in range(self.count()):
            self.initStyleOption(option, index)
            tab_rect = self.tabRect(index)
            
            # Define the hexagon shape
            hexagon = QPolygon([
                QPoint(tab_rect.left(), tab_rect.center().y()),
                QPoint(tab_rect.left() + tab_rect.width() * 0.25, tab_rect.top()),
                QPoint(tab_rect.right() - tab_rect.width() * 0.25, tab_rect.top()),
                QPoint(tab_rect.right(), tab_rect.center().y()),
                QPoint(tab_rect.right() - tab_rect.width() * 0.25, tab_rect.bottom()),
                QPoint(tab_rect.left() + tab_rect.width() * 0.25, tab_rect.bottom()),
            ])

            # Draw the hexagon
            painter.setBrush(option.palette.base() if self.currentIndex() == index else option.palette.button())
            painter.drawPolygon(hexagon)

            # Draw the text
            painter.drawText(tab_rect, Qt.AlignCenter | Qt.TextDontClip, self.tabText(index))

class CustomTabWidget(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabBar(HexagonTabBar(self))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        #self.setStyleSheet("background-color: #FFFFFF; color: white;")
        
        # Set up the central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Tab widget
        self.tab_widget = CustomTabWidget()
        main_layout.addWidget(self.tab_widget)

        # Image Tab
        image_tab = QWidget()
        self.tab_widget.addTab(image_tab, "Image")
        image_layout = QHBoxLayout(image_tab)

        # Image viewer area (3/4 of the width)
        self.viewer = ImageViewer()
        image_layout.addWidget(self.viewer, 3)
        
        # Import and instantiate controller
        from image_controller import ImageController #Import here to avoid circular dependency
        self.controller = ImageController(self.viewer)
        self.viewer.controller = self.controller

        # Control Panel
        self.control_panel = ControlPanel(self.viewer, self.controller)  #Pass controller instance here
        image_layout.addWidget(self.control_panel, 1)

        # Report Tab
        report_tab = QWidget()
        self.tab_widget.addTab(report_tab, "Report")  # Add Report tab
        report_layout = QVBoxLayout(report_tab)  # Layout for report content

        # Add your report components here (e.g., text boxes, labels)
        report_label = QLabel("Report content will be displayed here.")
        report_layout.addWidget(report_label)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.resize(500,500)
    window.controller.load_current_image()  # Load the image
    window.setWindowTitle("Biomedical Image Viewer")
    window.show()

    sys.exit(app.exec_())