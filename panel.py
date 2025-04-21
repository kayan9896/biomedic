import tkinter as tk
from tkinter import ttk
import threading
import os

class IMU3:
    def __init__(self, viewmodel, config=None):
        self.viewmodel = viewmodel
        self.angle = 0
        self.rotation_angle = 0
        self._auto_mode = False
        self._running = True
        self.increasing = True
        
        self.test_image_ready = False
        self.test_image_path = None

        self.current_tab = 'hp1'  # Default tab
        self.test_data = {
            'ap': None, 
            'ob': None, 
            'recons': None, 
            'regs': None
        }
        
        # Get the exam folder path from config
        self.sim_data_path = config.get("model_simdata_path", "exam") if config else "exam"
        
        # Initialize the angles in viewmodel
        self.viewmodel.update_state('angle', self.angle)
        self.viewmodel.update_state('rotation_angle', self.rotation_angle)
        
        # Launch the GUI in a separate thread
        self.gui_thread = threading.Thread(target=self._run_gui)
        self.gui_thread.daemon = True
        self.gui_thread.start()
    
    def _run_gui(self):
        """Run the GUI in its own thread"""
        self.root = tk.Tk()
        self.root.title("IMU Control")
        self.root.protocol("WM_DELETE_WINDOW", self.cleanup)
        
        # Set window attributes
        self.root.attributes("-topmost", True)
        self.root.resizable(False, False)
        
        # Create UI components
        self._create_ui()
        
        # Position window at bottom right
        self._position_window_bottom_right()
        
        # Set up periodic updates
        self._setup_auto_mode_update()
        
        # Start the mainloop
        self.root.mainloop()
    
    def _create_ui(self):
        """Create all the UI components"""
        # Create a main frame with padding
        main_frame = tk.Frame(self.root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create angle display and controls (outside tabs)
        angle_frame = tk.Frame(main_frame)
        angle_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Labels for angle values (same as before)
        tk.Label(angle_frame, text="Angle:").grid(row=0, column=0, sticky=tk.W)
        self.angle_value = tk.Label(angle_frame, text=str(self.angle))
        self.angle_value.grid(row=0, column=1, sticky=tk.W, padx=(5, 0))
        
        tk.Label(angle_frame, text="Rotation Angle:").grid(row=1, column=0, sticky=tk.W)
        self.rotation_angle_value = tk.Label(angle_frame, text=str(self.rotation_angle))
        self.rotation_angle_value.grid(row=1, column=1, sticky=tk.W, padx=(5, 0))
        
        # Create angle control buttons (outside tabs)
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Angle controls (same as before)
        angle_ctrl_frame = tk.LabelFrame(button_frame, text="Angle Control")
        angle_ctrl_frame.pack(fill=tk.X, pady=(0, 5))
        tk.Button(angle_ctrl_frame, text="−", width=3, command=lambda: self._adjust_angle(-5)).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(angle_ctrl_frame, text="+", width=3, command=lambda: self._adjust_angle(5)).pack(side=tk.RIGHT, padx=5, pady=5)
        
        rot_ctrl_frame = tk.LabelFrame(button_frame, text="Rotation Control")
        rot_ctrl_frame.pack(fill=tk.X)
        tk.Button(rot_ctrl_frame, text="−", width=3, command=lambda: self._adjust_angle2(-5)).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(rot_ctrl_frame, text="+", width=3, command=lambda: self._adjust_angle2(5)).pack(side=tk.RIGHT, padx=5, pady=5)
        
        # Create tabs
        tab_control = ttk.Notebook(main_frame)
        tab_control.bind("<<NotebookTabChanged>>", self._on_tab_changed)
        
        # Create the four tabs
        self.hp1_tab = ttk.Frame(tab_control)
        self.hp2_tab = ttk.Frame(tab_control)
        self.cup_tab = ttk.Frame(tab_control)
        self.tri_tab = ttk.Frame(tab_control)
        
        tab_control.add(self.hp1_tab, text='hp1')
        tab_control.add(self.hp2_tab, text='hp2')
        tab_control.add(self.cup_tab, text='cup')
        tab_control.add(self.tri_tab, text='tri')
        
        tab_control.pack(fill=tk.BOTH, expand=True)
        
        # Create content for each tab
        self.tab_widgets = {
            'hp1': self._create_tab_content(self.hp1_tab, 'hp1'),
            'hp2': self._create_tab_content(self.hp2_tab, 'hp2'),
            'cup': self._create_tab_content(self.cup_tab, 'cup'),
            'tri': self._create_tab_content(self.tri_tab, 'tri')
        }
        
        # Update all file lists
        self._update_all_file_lists()
        
        # Single test button
        test_button = tk.Button(main_frame, text="TEST", command=self._test_with_selected_files)
        test_button.pack(fill=tk.X, pady=(10, 5))
        
        # Auto mode toggle
        auto_button = tk.Button(main_frame, text="Auto Mode: OFF", command=self._toggle_auto_mode_gui)
        self.auto_button = auto_button
        auto_button.pack(fill=tk.X)
    
    def _on_tab_changed(self, event):
        """Handle tab change event to update current tab"""
        tab_control = event.widget
        selected_tab_index = tab_control.index(tab_control.select())
        tab_names = ['hp1', 'hp2', 'cup', 'tri']
        self.current_tab = tab_names[selected_tab_index]
        print(f"Current tab changed to: {self.current_tab}")
        
        # Clear test data on tab change
        self.test_data = {
            'ap': None, 
            'ob': None, 
            'recons': None, 
            'regs': None
        }

    def _create_tab_content(self, tab_frame, tab_type):
        """Create the content for a tab with four dropdowns and error lists"""
        content_frame = tk.Frame(tab_frame, padx=5, pady=5)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        tab_widgets = {
            'dropdowns': {},
            'error_lists': {}
        }
        
        # Create four sections: ap, ob, recons, and regs
        for section in ['ap', 'ob', 'recons', 'regs']:
            section_frame = tk.LabelFrame(content_frame, text=section.upper(), padx=5, pady=5)
            section_frame.pack(fill=tk.X, pady=(0, 10))
            
            # File selection dropdown
            dropdown_frame = tk.Frame(section_frame)
            dropdown_frame.pack(fill=tk.X, pady=(0, 5))
            
            tk.Label(dropdown_frame, text="File:").pack(side=tk.LEFT)
            file_var = tk.StringVar()
            dropdown = ttk.Combobox(dropdown_frame, textvariable=file_var, state="readonly", width=30)
            dropdown.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
            
            # Refresh button
            tk.Button(dropdown_frame, text="↻", width=3, 
                    command=lambda t=tab_type, s=section: self._update_file_list_for_tab_section(t, s)).pack(side=tk.LEFT, padx=(5, 0))
            
            # Error listbox with scrollbar
            error_frame = tk.Frame(section_frame)
            error_frame.pack(fill=tk.X)
            
            tk.Label(error_frame, text="Errors:").pack(side=tk.LEFT)
            
            # Create a frame to contain the listbox and scrollbar
            error_list_frame = tk.Frame(error_frame)
            error_list_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
            
            # Create the scrollbar
            scrollbar = tk.Scrollbar(error_list_frame, orient="vertical")
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Create the listbox with scrollbar
            error_listbox = tk.Listbox(error_list_frame, height=3, width=15, 
                                    yscrollcommand=scrollbar.set, selectmode=tk.EXTENDED)
            error_listbox.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            # Configure the scrollbar
            scrollbar.config(command=error_listbox.yview)
            
            # Add default error codes
            for i in range(1, 6):
                error_listbox.insert(tk.END, f"{i:03d}")
            
            # Store widgets
            tab_widgets['dropdowns'][section] = dropdown
            tab_widgets['error_lists'][section] = error_listbox
        
        return tab_widgets
    
    def _test_with_selected_files(self):
        """Collect selected files and error codes for the current tab"""
        # Clear previous test data
        self.test_data = {
            'ap': None, 
            'ob': None, 
            'recons': None, 
            'regs': None
        }
        
        # Get selected files from current tab only
        tab_type = self.current_tab  # hp1, hp2, cup, tri
        
        for section in ['ap', 'ob', 'recons', 'regs']:
            # Get selected file
            dropdown = self.tab_widgets[tab_type]['dropdowns'][section]
            selected_base_name = dropdown.get()
            
            # Get selected errors
            error_listbox = self.tab_widgets[tab_type]['error_lists'][section]
            selected_indices = error_listbox.curselection()
            selected_errors = [error_listbox.get(i) for i in selected_indices]
            
            if selected_base_name:
                # Determine the folder
                if section in ['ap', 'ob']:
                    folder = 'shots'
                else:
                    folder = section
                
                # Construct full paths for both PNG and JSON files
                image_path = os.path.join(self.sim_data_path, folder, f"{selected_base_name}.png")
                json_path = os.path.join(self.sim_data_path, folder, f"{selected_base_name}.json")
                
                self.test_data[section] = {
                    'image_path': image_path if os.path.exists(image_path) else None,
                    'json_path': json_path if os.path.exists(json_path) else None,
                    'file_name': selected_base_name,
                    'errors': selected_errors
                }
        
        # Trigger the test with the first available ap image
        for section in ['ap', 'ob']:
            if self.test_data[section] and self.test_data[section]['image_path']:
                self.test_image_path = self.test_data[section]['image_path']
                self.test_image_ready = True
                print(f"Test initiated with selected files from tab {tab_type}")
                print(f"Starting with {section} file: {self.test_data[section]['file_name']}")
                return
        
        print("No valid image file selected for testing!")
    
    def _get_files_for_tab_section(self, tab_type, section):
        """Get files filtered by tab type and section"""
        files = set()  # Use a set to avoid duplicates
        if not os.path.exists(self.sim_data_path):
            return []
        
        try:
            # Determine which folder to look in based on section
            if section in ['ap', 'ob']:
                folder = 'shots'
            else:
                folder = section  # recons or regs
            
            folder_path = os.path.join(self.sim_data_path, folder)
            if not os.path.exists(folder_path):
                return []
            
            for filename in os.listdir(folder_path):
                if filename.lower().endswith(('.png', '.json')):
                    # Extract base name without extension
                    base_name = os.path.splitext(filename)[0]
                    filename_lower = filename.lower()
                    
                    # Filter by tab type
                    should_include = False
                    
                    if tab_type == 'hp1' and 'hp1' in filename_lower:
                        should_include = True
                    elif tab_type == 'hp2' and 'hp2' in filename_lower:
                        should_include = True
                    elif tab_type == 'cup' and 'cup' in filename_lower:
                        should_include = True
                    elif tab_type == 'tri' and 'tri' in filename_lower:
                        should_include = True
                    
                    # Further filter shots by ap/ob
                    if should_include and folder == 'shots':
                        if section == 'ap' and 'ap' in filename_lower:
                            files.add(base_name)
                        elif section == 'ob' and 'ob' in filename_lower:
                            files.add(base_name)
                    elif should_include and folder == section:
                        files.add(base_name)
            
            # Convert to sorted list
            files = sorted(list(files))
            
        except Exception as e:
            print(f"Error reading folder: {e}")
        
        return files
    
    def _update_file_list_for_tab_section(self, tab_type, section):
        """Update the dropdown list for a specific tab and section"""
        files = self._get_files_for_tab_section(tab_type, section)
        self.tab_widgets[tab_type]['dropdowns'][section]['values'] = files
        if files:
            self.tab_widgets[tab_type]['dropdowns'][section].current(0)
    
    def _update_all_file_lists(self):
        """Update all dropdown lists for all tabs and sections"""
        for tab_type in ['hp1', 'hp2', 'cup', 'tri']:
            for section in ['ap', 'ob', 'recons', 'regs']:
                self._update_file_list_for_tab_section(tab_type, section)
    


    
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