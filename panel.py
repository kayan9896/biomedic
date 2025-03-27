import tkinter as tk
from tkinter import ttk
import threading

class IMU3:
    def __init__(self, viewmodel):
        self.viewmodel = viewmodel
        self.angle = 0
        self.rotation_angle = 0
        self._auto_mode = False  # Start in manual mode
        self._running = True
        self.increasing = True
        
        # Initialize the angles in viewmodel
        self.viewmodel.update_state('angle', self.angle)
        self.viewmodel.update_state('rotation_angle', self.rotation_angle)
        
        # Launch the GUI in a separate thread to avoid blocking the main thread
        self.gui_thread = threading.Thread(target=self._run_gui)
        self.gui_thread.daemon = True
        self.gui_thread.start()
    
    def _run_gui(self):
        """Run the GUI in its own thread"""
        # Create the main window
        self.root = tk.Tk()
        self.root.title("IMU Control")
        self.root.protocol("WM_DELETE_WINDOW", self.cleanup)
        
        # Set window to stay on top and make it non-resizable
        self.root.attributes("-topmost", True)
        self.root.resizable(False, False)
        
        # Create UI components
        self._create_ui()
        
        # Position window at bottom right of screen
        self._position_window_bottom_right()
        
        # Set up a periodic task for auto mode updates
        self._setup_auto_mode_update()
        
        # Start the mainloop in this thread
        self.root.mainloop()
    
    def _create_ui(self):
        """Create all the UI components"""
        # Create a main frame with padding
        main_frame = tk.Frame(self.root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create angle display and controls (outside tabs)
        angle_frame = tk.Frame(main_frame)
        angle_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Labels for angle values
        tk.Label(angle_frame, text="Angle:").grid(row=0, column=0, sticky=tk.W)
        self.angle_value = tk.Label(angle_frame, text=str(self.angle))
        self.angle_value.grid(row=0, column=1, sticky=tk.W, padx=(5, 0))
        
        tk.Label(angle_frame, text="Rotation Angle:").grid(row=1, column=0, sticky=tk.W)
        self.rotation_angle_value = tk.Label(angle_frame, text=str(self.rotation_angle))
        self.rotation_angle_value.grid(row=1, column=1, sticky=tk.W, padx=(5, 0))
        
        # Create angle control buttons (outside tabs)
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Angle control
        angle_ctrl_frame = tk.LabelFrame(button_frame, text="Angle Control")
        angle_ctrl_frame.pack(fill=tk.X, pady=(0, 5))
        tk.Button(angle_ctrl_frame, text="−", width=3, command=lambda: self._adjust_angle(-5)).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(angle_ctrl_frame, text="+", width=3, command=lambda: self._adjust_angle(5)).pack(side=tk.RIGHT, padx=5, pady=5)
        
        # Rotation angle control
        rot_ctrl_frame = tk.LabelFrame(button_frame, text="Rotation Control")
        rot_ctrl_frame.pack(fill=tk.X)
        tk.Button(rot_ctrl_frame, text="−", width=3, command=lambda: self._adjust_angle2(-5)).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(rot_ctrl_frame, text="+", width=3, command=lambda: self._adjust_angle2(5)).pack(side=tk.RIGHT, padx=5, pady=5)
        
        # Create tabs
        tab_control = ttk.Notebook(main_frame)
        
        # Create the three tabs
        self.ref_tab = ttk.Frame(tab_control)
        self.cup_tab = ttk.Frame(tab_control)
        self.tri_tab = ttk.Frame(tab_control)
        
        tab_control.add(self.ref_tab, text='ref')
        tab_control.add(self.cup_tab, text='cup')
        tab_control.add(self.tri_tab, text='tri')
        
        tab_control.pack(fill=tk.BOTH, expand=True)
        
        # Create content for each tab
        self._create_tab_content(self.ref_tab)
        self._create_tab_content(self.cup_tab)
        self._create_tab_content(self.tri_tab)
        
        # Auto mode toggle
        auto_button = tk.Button(main_frame, text="Auto Mode: OFF", command=self._toggle_auto_mode_gui)
        self.auto_button = auto_button
        auto_button.pack(fill=tk.X, pady=(10, 0))
    
    def _create_tab_content(self, tab_frame):
        """Create the content for a tab"""
        content_frame = tk.Frame(tab_frame, padx=5, pady=5)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create a frame for the left side (dropdown)
        left_frame = tk.Frame(content_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        tk.Label(left_frame, text="Options:").pack(anchor=tk.W)
        
        # Dropdown with 6 options
        option_var = tk.StringVar()
        options = ['Option 1', 'Option 2', 'Option 3', 'Option 4', 'Option 5', 'Option 6']
        dropdown = ttk.Combobox(left_frame, textvariable=option_var, values=options, state="readonly")
        dropdown.pack(fill=tk.X, pady=5)
        dropdown.current(0)
        
        # Create a frame for the middle (L/R radio buttons)
        middle_frame = tk.Frame(content_frame)
        middle_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=5)
        
        tk.Label(middle_frame, text="Select:").pack(anchor=tk.W)
        
        # Radio buttons for L/R selection
        selection_var = tk.StringVar(value="L")
        
        # Frame to hold radio buttons with circular appearance
        radio_frame = tk.Frame(middle_frame)
        radio_frame.pack(fill=tk.X, pady=5)
        
        r1 = tk.Radiobutton(radio_frame, text="L", variable=selection_var, value="L", indicatoron=0,
                         width=2, height=1, borderwidth=2, relief="raised")
        r1.pack(side=tk.LEFT, padx=2)
        
        r2 = tk.Radiobutton(radio_frame, text="R", variable=selection_var, value="R", indicatoron=0,
                         width=2, height=1, borderwidth=2, relief="raised")
        r2.pack(side=tk.LEFT, padx=2)
        
        # Create a frame for the right side (scrollable list)
        right_frame = tk.Frame(content_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        tk.Label(right_frame, text="Error Codes:").pack(anchor=tk.W)
        
        # Create a frame for the list and scrollbar
        list_frame = tk.Frame(right_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Scrollbar for the list
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create the listbox with error codes
        error_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, height=5)
        
        # Add error codes to the listbox
        for i in range(1, 11):
            error_listbox.insert(tk.END, f"{i:03d}")
        
        error_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=error_listbox.yview)
    
    def _setup_auto_mode_update(self):
        """Set up a periodic task for auto mode updates"""
        if not hasattr(self, 'root') or not self.root.winfo_exists():
            return
            
        if self._auto_mode:
            # Update angle in auto mode
            if self.increasing:
                self.angle += 1
                if self.angle >= 60:
                    self.increasing = False
            else:
                self.angle -= 1
                if self.angle <= -60:
                    self.increasing = True
                    
            # Update the viewmodel and UI
            self.viewmodel.update_state('angle', self.angle)
            self.angle_value.config(text=str(self.angle))
        
        # Schedule the next update if still running
        if self._running:
            self.root.after(100, self._setup_auto_mode_update)
    
    def _position_window_bottom_right(self):
        """Position the window in the bottom right corner of the screen"""
        # Wait for the window to update its size
        self.root.update_idletasks()
        
        # Get screen width and height
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Calculate position (bottom right with padding)
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()
        
        x = screen_width - window_width - 20
        y = screen_height - window_height - 60
        
        # Set window position
        self.root.geometry(f"+{x}+{y}")
    
    def _adjust_angle(self, change):
        """Adjust the main angle value"""
        if not self._auto_mode:
            new_angle = min(max(self.angle + change, -60), 60)
            self.angle = new_angle
            self.viewmodel.update_state('angle', self.angle)
            self.angle_value.config(text=str(self.angle))
            print(f"Current angle: {self.angle}")
    
    def _adjust_angle2(self, change):
        """Adjust the rotation angle value"""
        if not self._auto_mode:
            new_angle = min(max(self.rotation_angle + change, -60), 60)
            self.rotation_angle = new_angle
            self.viewmodel.update_state('rotation_angle', self.rotation_angle)
            self.rotation_angle_value.config(text=str(self.rotation_angle))
            print(f"Current rotation_angle: {self.rotation_angle}")
    
    def _toggle_auto_mode(self):
        """Toggle the auto mode on/off"""
        self._auto_mode = not self._auto_mode
        print(f"Auto mode: {'ON' if self._auto_mode else 'OFF'}")
    
    def _toggle_auto_mode_gui(self):
        """Toggle auto mode and update the UI"""
        self._toggle_auto_mode()
        self.auto_button.config(text=f"Auto Mode: {'ON' if self._auto_mode else 'OFF'}")
    
    def get_angle(self):
        """Get the current angle value"""
        return self.angle
    
    def imuonob(self):
        """Check if IMU is on observation state"""
        return (not self.imuonap()) and (-45 <= self.rotation_angle <= 45)
    
    def imuonap(self):
        """Check if IMU is on AP state"""
        return -15 <= self.rotation_angle <= 15
    
    def cleanup(self):
        """Clean up resources when the IMU is no longer needed"""
        self._running = False
        
        # Safely destroy the GUI if it exists
        if hasattr(self, 'root') and self.root.winfo_exists():
            try:
                self.root.quit()
                self.root.destroy()
            except:
                pass