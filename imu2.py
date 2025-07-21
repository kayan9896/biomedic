import threading
import time
import keyboard  # You'll need to install this: pip install keyboard

class IMU2:
    def __init__(self, port, ApplyTarget, CarmRangeTilt = [-10, 10], CarmRangeRotation = [-25, -10, 10, 25], CarmTargetTilt = None, CarmTargetRot = [None, None, None], scale = 10/20, tol = 0.2):
        self.tilt_angle = 0
        self.rotation_angle = 0
        self.is_connected = False
        self.battery_level = 100
        self.tiltl = CarmRangeTilt[0]
        self.tiltr = CarmRangeTilt[1]
        self.rangel = CarmRangeRotation[0]
        self.apl = CarmRangeRotation[1]
        self.apr = CarmRangeRotation[2]
        self.ranger = CarmRangeRotation[3]
        self.scale = scale #actual angle/UI angle
        self.tol = tol
        self.EPSILON = 1e-9

        self.tmp_tilttarget = self.tilt_angle
        self.tmp_aptarget = self.rotation_angle
        self.tmp_obtarget1 = None
        self.tmp_obtarget2 = None
        self.tmp_used_ob = None
        self.tilttarget = CarmTargetTilt
        self.aptarget = CarmTargetRot[0]
        self.obtarget1 = CarmTargetRot[1]
        self.obtarget2 = CarmTargetRot[2]
        self.used_ob = None
        self.applytarget = ApplyTarget

        # Initialize ob_min and ob_max with None checks
        self.ob_min = min(self.obtarget1, self.obtarget2) if self.obtarget1 is not None and self.obtarget2 is not None else None
        self.ob_max = max(self.obtarget1, self.obtarget2) if self.obtarget1 is not None and self.obtarget2 is not None else None

        self.iscupreg = False

        # Timing and stability tracking
        self.last_stable_time = 0
        self.prev_angle = 0
        self.prev_rotation_angle = 0
        self.icon_shown = False
        self.window_shown = not (self.is_rot_valid(0) and self.is_tilt_valid(0))

    def set_tilt(self, a):
        self.prev_angle = self.tilt_angle
        self.tilt_angle = a
        self.last_stable_time = time.time()

    def set_rotation(self, a):
        self.prev_rotation_angle = self.rotation_angle
        self.rotation_angle = a
        self.last_stable_time = time.time()

    def activeside(self, stage=0):
        if stage == 0:
            if self.rangel < self.rotation_angle <= self.ranger:
                if self.apl < self.rotation_angle <= self.apr:
                    return 'ap'
                return 'ob'
        if stage == 1:
            if self.rangel < self.rotation_angle <= self.ranger:
                if self.apl < self.rotation_angle <= self.apr:
                    return 'ap'
                if self.obtarget1 is not None and self.rotation_angle * self.obtarget1 > 0:
                    return None
                return 'ob'
        if stage == 2 or (stage ==3 and not self.iscupreg):
            if self.rangel < self.rotation_angle <= self.ranger:
                if self.aptarget is not None and self.ob_min is not None and self.ob_max is not None:
                    if (self.ob_min + self.aptarget) / 2 < self.rotation_angle <= (self.ob_max + self.aptarget) / 2:
                        return 'ap'
                return 'ob'
        if stage == 3 and self.iscupreg:
            if self.rangel < self.rotation_angle < self.ranger:
                if self.aptarget is not None and self.ob_min is not None and self.ob_max is not None:
                    if (self.ob_min + self.aptarget) / 2 < self.rotation_angle <= (self.ob_max + self.aptarget) / 2:
                        return 'ap'
                if self.used_ob is not None and self.rotation_angle * self.used_ob < 0:
                    return None
                return 'ob'
        return None

    def is_tilt_valid(self, stage):
        active = self.activeside(stage)
        if stage == 0 and active == 'ap':
            if self.tilttarget is not None and self.applytarget:
                return abs(self.tilt_angle - self.tilttarget) < self.tol + self.EPSILON
            
            return self.tiltl < self.tilt_angle <= self.tiltr
        if (stage == 0 and active == 'ob') or stage > 0:
            return abs(self.tilt_angle - self.tilttarget) < self.tol + self.EPSILON if self.tilttarget is not None else abs(self.tilt_angle - self.tmp_tilttarget) < self.tol + self.EPSILON
        return False

    def is_rot_valid(self, stage):
        active = self.activeside(stage)
        if stage == 0:
            if active == 'ap'and self.aptarget is not None:
                return abs(self.rotation_angle - self.aptarget) < self.tol + self.EPSILON
            if active == 'ob':
                if self.obtarget1 is not None and self.rotation_angle * self.obtarget1 > 0:
                    return abs(self.rotation_angle - self.obtarget1) < self.tol + self.EPSILON
                if self.obtarget2 is not None and self.rotation_angle * self.obtarget2 > 0:
                    return abs(self.rotation_angle - self.obtarget2) < self.tol + self.EPSILON
            return self.rangel < self.rotation_angle <= self.ranger
        if stage == 1:
            if active == 'ap':
                return self.aptarget is not None and abs(self.rotation_angle - self.aptarget) < self.tol + self.EPSILON
            if active == 'ob':
                if self.obtarget2 is not None:
                    return abs(self.rotation_angle - self.obtarget2) < self.tol + self.EPSILON
                return self.obtarget1 is not None and self.rotation_angle * self.obtarget1 < 0
        if stage == 2 or (stage ==3 and not self.iscupreg):
            if active == 'ap':
                return self.aptarget is not None and abs(self.rotation_angle - self.aptarget) < self.tol + self.EPSILON
            if active == 'ob':
                return self.obtarget1 is not None and self.obtarget2 is not None and \
                       (abs(self.rotation_angle - self.obtarget1) < self.tol + self.EPSILON or abs(self.rotation_angle - self.obtarget2) < self.tol + self.EPSILON)
        if stage == 3 and self.iscupreg:
            if active == 'ap':
                return self.aptarget is not None and abs(self.rotation_angle - self.aptarget) < self.tol + self.EPSILON
            if active == 'ob':
                return self.used_ob is not None and abs(self.rotation_angle - self.used_ob) < self.tol + self.EPSILON
        return False

    def show_icon(self, stage):
        current_time = time.time()
        is_tilt_valid = self.is_tilt_valid(stage)  # Assuming stage 0 for icon, adjust if needed
        is_rot_valid = self.is_rot_valid(stage)    # Assuming stage 0 for icon, adjust if needed
        is_stable = abs(self.prev_angle - self.tilt_angle) < self.tol + self.EPSILON and abs(self.prev_rotation_angle - self.rotation_angle) < self.tol + self.EPSILON

        if is_tilt_valid and is_rot_valid and is_stable:
            if current_time - self.last_stable_time >= 3:
                self.icon_shown = True
        else:
            self.icon_shown = False

        
        return self.icon_shown

    def show_window(self, stage):
        current_time = time.time()
        is_tilt_valid = self.is_tilt_valid(stage)  # Assuming stage 0 for window, adjust if needed
        is_rot_valid = self.is_rot_valid(stage)    # Assuming stage 0 for window, adjust if needed
        has_changed = abs(self.prev_angle - self.tilt_angle) > self.tol + self.EPSILON or abs(self.prev_rotation_angle - self.rotation_angle) > self.tol + self.EPSILON
        is_stable = abs(self.prev_angle - self.tilt_angle) < self.tol + self.EPSILON and abs(self.prev_rotation_angle - self.rotation_angle) < self.tol + self.EPSILON

        if has_changed:
            self.window_shown = True
        elif self.window_shown and is_tilt_valid and is_rot_valid and is_stable:
            if current_time - self.last_stable_time >= 5:
                self.window_shown = False

        self.prev_angle = self.tilt_angle
        self.prev_rotation_angle = self.rotation_angle
        return self.window_shown

    def handle_window_close(self, stage):
        if stage == 0:
            self.tmp_tilttarget = self.tilt_angle
            if not self.applytarget: self.tilttarget = self.tilt_angle
            if self.activeside(stage) == 'ap':
                self.tmp_aptarget = self.rotation_angle
            if self.activeside(stage) == 'ob':
                if self.obtarget2 and abs(self.obtarget2 - self.rotation_angle) < self.tol + self.EPSILON:
                    self.tmp_obtarget2 = self.obtarget1
                self.tmp_obtarget1 = self.rotation_angle
        elif stage == 1:
            if self.activeside(stage) == 'ob':
                self.tmp_obtarget2 = self.rotation_angle
        elif stage == 2:
            if abs(self.rotation_angle - self.obtarget1) < self.tol + self.EPSILON:
                self.tmp_used_ob = self.obtarget1
            elif abs(self.rotation_angle - self.obtarget2) < self.tol + self.EPSILON:
                self.tmp_used_ob = self.obtarget2

    def confirm_save(self):
        if self.tmp_tilttarget is not None and self.tilttarget is None:
            self.tilttarget = self.tmp_tilttarget
        if self.tmp_aptarget is not None and self.aptarget is None:
            self.aptarget = self.tmp_aptarget
        if self.tmp_obtarget1 is not None and self.obtarget1 is None:
            self.obtarget1 = self.tmp_obtarget1
        if self.tmp_obtarget2 == self.obtarget1:
            self.obtarget1, self.obtarget2 = self.obtarget2, self.obtarget1
        if self.tmp_obtarget2 is not None and self.obtarget2 is None:
            self.obtarget2 = self.tmp_obtarget2
        if self.tmp_used_ob is not None:
            self.used_ob = self.tmp_used_ob
        # Update ob_min and ob_max
        if self.obtarget1 is not None and self.obtarget2 is not None:
            self.ob_min = min(self.obtarget1, self.obtarget2)
            self.ob_max = max(self.obtarget1, self.obtarget2)

    def get_all(self, stage):
        return {
            'applytarget': self.applytarget,
            'tilttarget': self.tilttarget,
            'aptarget': self.aptarget,
            'obtarget1': self.obtarget1,
            'obtarget2': self.obtarget2,
            'used_ob': self.used_ob,
            'ob_min': self.ob_min,
            'ob_max': self.ob_max,
            'is_tilt_valid': self.is_tilt_valid(stage),  
            'is_rot_valid': self.is_rot_valid(stage),  
            'show_icon': self.show_icon(stage),
            'show_window': self.show_window(stage),
            'tiltl': self.tiltl,
            'tiltr': self.tiltr,
            'rangel': self.rangel,
            'apl': self.apl,
            'apr': self.apr,
            'ranger': self.ranger,
            'scale': self.scale
        }

    def check_tilt_sensor(self):        
        if not self.is_connected:
            message = "Tilt sensor disconnected. Please check the connection."
        elif self.battery_level < 30:
            message = "Tilt sensor connected but battery is low. Consider replacing batteries soon."
        else:
            message = "Tilt sensor connected successfully."
        return {
            "connected": self.is_connected,
            "battery_low": self.battery_level < 30,
            "message": message
        }

    def set_cupreg(self):
        self.iscupreg = True