import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import math

class PointDraggingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Point Dragging Application")
        
        self.canvas = tk.Canvas(root, width=800, height=600)
        self.canvas.pack(expand=tk.YES, fill=tk.BOTH)
        
        self.load_button = tk.Button(root, text="Load Image", command=self.load_image)
        self.load_button.pack()
        
        self.add_default_button = tk.Button(root, text="Add Default Points", command=self.add_default_points)
        self.add_default_button.pack()
        
        self.points = []
        self.lines = []
        self.distance_texts = []
        self.dragging_point = None
        self.start_drag_pos = None
        self.photo = None
        
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
    
    def load_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            image = Image.open(file_path)
            self.photo = ImageTk.PhotoImage(image)
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
    
    def add_default_points(self):
        default_positions = [(100, 100), (200, 200), (300, 150), (400, 250)]
        for pos in default_positions:
            self.add_point(pos[0], pos[1])
        self.update_lines_and_distances()
    
    def add_point(self, x, y):
        point = self.canvas.create_oval(x-5, y-5, x+5, y+5, fill="red")
        self.points.append(point)
        return point
    
    def find_point_at_position(self, x, y):
        for point in self.points:
            coords = self.canvas.coords(point)
            if coords[0] <= x <= coords[2] and coords[1] <= y <= coords[3]:
                return point
        return None

    def on_press(self, event):
        point = self.find_point_at_position(event.x, event.y)
        if point:
            self.dragging_point = point
            self.start_drag_pos = (event.x, event.y)
        else:
            self.add_point(event.x, event.y)
            self.update_lines_and_distances()
    
    def on_drag(self, event):
        if self.dragging_point:
            self.canvas.coords(self.dragging_point, 
                               event.x-5, event.y-5, event.x+5, event.y+5)
            self.update_lines_and_distances()
    
    def on_release(self, event):
        if self.dragging_point:
            if self.start_drag_pos:
                if math.dist(self.start_drag_pos, (event.x, event.y)) < 2:
                    # Point wasn't moved significantly, so remove it
                    self.remove_point(self.dragging_point)
            self.dragging_point = None
            self.start_drag_pos = None
    
    def remove_point(self, point):
        if point in self.points:
            self.points.remove(point)
            self.canvas.delete(point)
            self.update_lines_and_distances()
    
    def update_lines_and_distances(self):
        # Remove existing lines and distance texts
        for line in self.lines:
            self.canvas.delete(line)
        for text in self.distance_texts:
            self.canvas.delete(text)
        self.lines.clear()
        self.distance_texts.clear()
        
        # Redraw lines and distances
        for i in range(len(self.points) - 1):
            coords1 = self.canvas.coords(self.points[i])
            coords2 = self.canvas.coords(self.points[i+1])
            
            x1, y1 = (coords1[0] + coords1[2])/2, (coords1[1] + coords1[3])/2
            x2, y2 = (coords2[0] + coords2[2])/2, (coords2[1] + coords2[3])/2
            
            line = self.canvas.create_line(x1, y1, x2, y2, fill="blue")
            self.lines.append(line)
            
            distance = math.dist((x1, y1), (x2, y2))
            mid_x, mid_y = (x1+x2)/2, (y1+y2)/2
            distance_text = self.canvas.create_text(mid_x, mid_y, 
                                                    text=f"{distance:.1f}", 
                                                    fill="green")
            self.distance_texts.append(distance_text)

root = tk.Tk()
app = PointDraggingApp(root)
root.mainloop()
