import tkinter as tk
from tkinter import ttk, filedialog, PhotoImage
from PIL import Image, ImageTk
import math
import threading
import time

class CircularProgressbar:
    def __init__(self, canvas, x, y, radius, **kwargs):
        self.canvas = canvas
        self.x, self.y = x, y
        self.radius = radius
        self.angle = 0
        self.outer_circle = canvas.create_oval(x-radius, y-radius, x+radius, y+radius, 
                                               width=5, outline="blue")
        self.inner_circle = canvas.create_oval(x-radius+5, y-radius+5, 
                                               x+radius-5, y+radius-5, fill="red")
        self.text = canvas.create_text(x, y, text="Loading", fill="white")
    
    def complete(self):
        self.canvas.itemconfig(self.inner_circle, fill="green")
        self.canvas.itemconfig(self.text, text="Done")

class PointDraggingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Multi-tab Application")
        self.root.geometry("1200x800")

        # Initialize attributes
        self.points = []
        self.lines = []
        self.distance_texts = []
        self.dragging_point = None
        self.start_drag_pos = None
        self.photo = None
        self.zoom_factor = 1.0
        self.zoom_increment = 0.1

        # Load icons first
        self.load_icons()

        # Create notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both')

        # Create evaluation tab
        self.eval_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.eval_frame, text='Evaluation')

        # Create report tab
        self.report_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.report_frame, text='Report')

        # Setup evaluation tab
        self.setup_evaluation_tab()

    def load_icons(self):
        try:
            self.zoom_in_icon = PhotoImage(file='C:/Users/A4ssg/Downloads/gf.gif')
            self.zoom_out_icon = PhotoImage(file='C:/Users/A4ssg/Downloads/gf.gif')
        except tk.TclError:
            print("Warning: Could not load zoom icons. Using text instead.")
            self.zoom_in_icon = None
            self.zoom_out_icon = None

    def setup_evaluation_tab(self):
        self.left_frame = ttk.Frame(self.eval_frame)
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        self.right_frame = ttk.Frame(self.eval_frame)
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        self.eval_frame.columnconfigure(0, weight=3)
        self.eval_frame.columnconfigure(1, weight=1)
        self.eval_frame.rowconfigure(0, weight=1)

        self.canvas_frame = ttk.Frame(self.left_frame, borderwidth=2, relief="groove")
        self.canvas_frame.pack(expand=True, fill='both', padx=5, pady=5)
        
        self.canvas = tk.Canvas(self.canvas_frame, width=800, height=600, bg='white')
        self.canvas.pack(expand=True, fill='both')

        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

        self.setup_control_panel()

    def setup_control_panel(self):
        title_label = ttk.Label(self.right_frame, text="Control Panel", font=('Arial', 14, 'bold'))
        title_label.pack(pady=10)

        # Loading indicator canvas
        self.loading_canvas = tk.Canvas(self.right_frame, width=100, height=100, 
                                        highlightthickness=0)
        self.loading_canvas.pack(pady=10)
        self.progress_indicator = CircularProgressbar(self.loading_canvas, 50, 50, 40)

        image_frame = ttk.LabelFrame(self.right_frame, text="Image Controls", padding=10)
        image_frame.pack(fill='x', padx=5, pady=5)

        load_button = ttk.Button(image_frame, text="Load Image", command=self.start_load_image)
        load_button.pack(fill='x', pady=5)

        point_frame = ttk.LabelFrame(self.right_frame, text="Point Controls", padding=10)
        point_frame.pack(fill='x', padx=5, pady=5)

        add_default_button = ttk.Button(point_frame, text="Add Default Points", 
                                       command=self.add_default_points)
        add_default_button.pack(fill='x', pady=5)

        clear_points_button = ttk.Button(point_frame, text="Clear All Points", 
                                        command=self.clear_all_points)
        clear_points_button.pack(fill='x', pady=5)
        # Zoom controls section
        zoom_frame = ttk.LabelFrame(self.right_frame, text="Zoom Controls", padding=10)
        zoom_frame.pack(fill='x', padx=5, pady=5)

        # Create zoom buttons with fallback to text if icons aren't available
        if self.zoom_in_icon:
            zoom_in_button = ttk.Button(zoom_frame, image=self.zoom_in_icon, 
                                        command=self.zoom_in)
        else:
            zoom_in_button = ttk.Button(zoom_frame, text="Zoom In", 
                                        command=self.zoom_in)
        zoom_in_button.pack(side=tk.LEFT, padx=5)
        CreateToolTip(zoom_in_button, "Zoom In")

        if self.zoom_out_icon:
            zoom_out_button = ttk.Button(zoom_frame, image=self.zoom_out_icon, 
                                         command=self.zoom_out)
        else:
            zoom_out_button = ttk.Button(zoom_frame, text="Zoom Out", 
                                         command=self.zoom_out)
        zoom_out_button.pack(side=tk.LEFT, padx=5)
        CreateToolTip(zoom_out_button, "Zoom Out")

    def zoom_in(self):
        self.zoom_factor += self.zoom_increment
        self.apply_zoom()

    def zoom_out(self):
        self.zoom_factor = max(0.1, self.zoom_factor - self.zoom_increment)  # Prevent zooming out too far
        self.apply_zoom()

    def apply_zoom(self):
        if not self.photo:
            return

        # Get original image
        original_image = Image.open(self.current_image_path)
        
        # Calculate new size
        new_width = int(original_image.width * self.zoom_factor)
        new_height = int(original_image.height * self.zoom_factor)
        
        # Resize image
        resized_image = original_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        self.photo = ImageTk.PhotoImage(resized_image)
        
        # Clear canvas and redraw
        self.canvas.delete("all")
        self.canvas.create_image(
            self.canvas.winfo_width()//2, 
            self.canvas.winfo_height()//2, 
            image=self.photo, 
            anchor=tk.CENTER
        )
        
        # Recalculate point positions
        for i, point in enumerate(self.points[:]):
            coords = self.original_point_coords[i]
            new_x = coords[0] * self.zoom_factor
            new_y = coords[1] * self.zoom_factor
            self.canvas.coords(point, 
                               new_x-5, new_y-5, new_x+5, new_y+5)
        
        self.update_lines_and_distances()

    def start_load_image(self):
        # Create progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.canvas, variable=self.progress_var, 
                                            maximum=100, mode='determinate')
        self.progress_bar.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=300)
        
        # Start loading in a separate thread
        threading.Thread(target=self.load_image).start()

    def load_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.current_image_path = file_path
            self.zoom_factor = 1.0  # Reset zoom factor

            # Simulate loading progress
            for i in range(101):
                time.sleep(0.02)  # Simulate processing time
                self.progress_var.set(i)
                self.root.update_idletasks()
            
            # Actually load and process the image
            image = Image.open(file_path)
            self.original_image_size = (image.width, image.height)
            canvas_ratio = self.canvas.winfo_width() / self.canvas.winfo_height()
            image_ratio = image.width / image.height
            
            if image_ratio > canvas_ratio:
                new_width = self.canvas.winfo_width()
                new_height = int(new_width / image_ratio)
            else:
                new_height = self.canvas.winfo_height()
                new_width = int(new_height * image_ratio)
            
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.photo = ImageTk.PhotoImage(image)
            self.canvas.delete("all")
            self.canvas.create_image(
                self.canvas.winfo_width()//2, 
                self.canvas.winfo_height()//2, 
                image=self.photo, 
                anchor=tk.CENTER
            )
            
            # Remove progress bar and update loading indicator
            self.progress_bar.destroy()
            self.progress_indicator.complete()

            self.original_point_coords = []
            for point in self.points:
                coords = self.canvas.coords(point)
                center_x = (coords[0] + coords[2]) / 2
                center_y = (coords[1] + coords[3]) / 2
                self.original_point_coords.append((center_x, center_y))

    def clear_all_points(self):
        for point in self.points:
            self.canvas.delete(point)
        self.points.clear()
        self.update_lines_and_distances()

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
                    self.remove_point(self.dragging_point)
            self.dragging_point = None
            self.start_drag_pos = None
    
    def remove_point(self, point):
        if point in self.points:
            self.points.remove(point)
            self.canvas.delete(point)
            self.update_lines_and_distances()
    
    def update_lines_and_distances(self):
        for line in self.lines:
            self.canvas.delete(line)
        for text in self.distance_texts:
            self.canvas.delete(text)
        self.lines.clear()
        self.distance_texts.clear()
        
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

# Tooltip class for hover text
class CreateToolTip:
    def __init__(self, widget, text='widget info'):
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.id = None
        self.tw = None

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(500, self.showtip)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def showtip(self):
        if self.tw:
            return
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        self.tw = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="#ffffff", relief=tk.SOLID, borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tw
        self.tw = None
        if tw:
            tw.destroy()

root = tk.Tk()
app = PointDraggingApp(root)
root.mainloop()
