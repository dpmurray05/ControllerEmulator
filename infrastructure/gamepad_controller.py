"""
Core gamepad controller that handles input processing and gamepad emulation.
"""
import time
import math
import threading
from typing import Optional

import vgamepad as vg

from config.config import Config
from infrastructure.cursor_manager import CursorManager


class GamepadController:
    """Main controller for gamepad emulation and input processing."""
    
    def __init__(self):
        """Initialize the gamepad controller."""
        # Core state
        self._gamepad: Optional[vg.VX360Gamepad] = None
        self._active = False
        self._lock = threading.RLock()
        
        # Cursor management
        self.cursor_manager = CursorManager()
        
        # Mouse state
        self.mouse_dx = 0.0
        self.mouse_dy = 0.0
        
        # Input state
        self.keys = {k: False for k in Config.KEY_MAPPINGS.keys()}
        self.l_joystick_keys = {k: False for k in Config.L_JOYSTICK_KEYS}
        self.r_joystick_keys = {k: False for k in Config.R_JOYSTICK_KEYS}

        
        # Gamepad state
        self.last_lx = 0.0
        self.last_ly = 0.0
        self.last_rx = 0.0
        self.last_ry = 0.0
        self.r2_held = False  # Right mouse (ADS)
        self.l2_held = False  # Left mouse (Fire)
        
        # Timing
        self._last_update = time.time()
        self._update_interval = 1.0 / Config.UPDATE_RATE_HZ
        
        # Input listeners (set externally)
        self.mouse_listener = None
        self.keyboard_listener = None
        
        print("[CONTROLLER] Initialized")
        
        # Initialize virtual gamepad immediately so games can detect it
        self.initialize_gamepad()
    
    @property
    def active(self) -> bool:
        """Check if controller is currently active."""
        return self._active
    
    def initialize_gamepad(self) -> bool:
        """Initialize the virtual gamepad."""
        try:
            if self._gamepad is None:
                self._gamepad = vg.VX360Gamepad()
                print("[CONTROLLER] Virtual gamepad created")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to initialize gamepad: {e}")
            return False
    
    def activate(self) -> bool:
        """Activate controller mode with input blocking."""
        with self._lock:
            if self._active:
                return True
            
            print("\n=== ACTIVATING CONTROLLER MODE ===")
            
            if not self.initialize_gamepad():
                return False
            
            # Send wake-up signal FIRST, before blocking keyboard
            # This ensures controller input is detected before any keyboard suppression happens
            if self._gamepad:
                # Send multiple signals: joystick movement + button press
                # This combo forces even stubborn games to recognize controller mode
                for i in range(2):
                    # Right joystick movement (camera)
                    self._gamepad.right_joystick_float(x_value_float=0.5, y_value_float=0.0)
                    # Press and release a button (BACK button is least intrusive)
                    self._gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK)
                    self._gamepad.update()
                    time.sleep(0.03)
                    
                    # Reset everything
                    self._gamepad.right_joystick_float(x_value_float=0.0, y_value_float=0.0)
                    self._gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK)
                    self._gamepad.update()
                    time.sleep(0.03)
                print("[CONTROLLER] Sent wake-up signal to force controller mode")
            
            # NOW enable input suppression (after controller wake-up)
            if self.mouse_listener and hasattr(self.mouse_listener, 'suppress_events'):
                self.mouse_listener.suppress_events(True)
            if self.keyboard_listener and hasattr(self.keyboard_listener, 'suppress_events'):
                self.keyboard_listener.suppress_events(True)
            
            # Lock and hide cursor
            self.cursor_manager.lock_to_center()
            self.cursor_manager.hide_cursor()
            
            self._active = True
            
            print("[CONTROLLER] Activated - Input blocking enabled")
            return True
    
    def deactivate(self):
        """Deactivate controller mode and restore normal input."""
        with self._lock:
            if not self._active:
                return
            
            print("\n=== DEACTIVATING CONTROLLER MODE ===")
            
            self._active = False
            
            # Reset all gamepad inputs
            self._reset_gamepad()
            
            # Clear all key states
            for key in self.l_joystick_keys:
                self.l_joystick_keys[key] = False
            for key in self.r_joystick_keys:
                self.r_joystick_keys[key] = False
            for key in self.keys:
                self.keys[key] = False
            
            # Disable input suppression
            if self.mouse_listener and hasattr(self.mouse_listener, 'suppress_events'):
                self.mouse_listener.suppress_events(False)
            if self.keyboard_listener and hasattr(self.keyboard_listener, 'suppress_events'):
                self.keyboard_listener.suppress_events(False)
            
            # Show cursor again
            self.cursor_manager.show_cursor()
            
            print("[CONTROLLER] Deactivated - Normal input restored")
    
    def _reset_gamepad(self):
        """Reset all gamepad controls to neutral state."""
        if not self._gamepad:
            return
        
        try:
            self._gamepad.left_joystick_float(x_value_float=0.0, y_value_float=0.0)
            self._gamepad.right_joystick_float(x_value_float=0.0, y_value_float=0.0)
            for button in Config.KEY_MAPPINGS.values():
                self._gamepad.release_button(button=button)
            self._gamepad.left_trigger_float(0.0)
            self._gamepad.right_trigger_float(0.0)
            self._gamepad.update()
        except Exception as e:
            print(f"[ERROR] Failed to reset gamepad: {e}")
    
    def process_inputs(self):
        """Process all inputs and update gamepad state."""
        current_time = time.time()
        if current_time - self._last_update < self._update_interval:
            return
        
        self._last_update = current_time
        
        with self._lock:
            if self._gamepad is None:
                return
            
            # Keep gamepad connected even when inactive
            # Only process actual inputs when active
            if self._active:
                self._process_left_joystick()
                self._process_right_joystick()
                self._process_buttons()
                self._process_triggers()
            
            # Always update gamepad to maintain connection
            self._gamepad.update()
    
    # Precomputed unit vectors for each 30° segment
    _SEG_30 = math.cos(math.radians(30))   # ≈ 0.866
    _SEG_60 = math.cos(math.radians(60))   # = 0.500

    def _process_left_joystick(self):
        """
        Process left joystick for BG3's 12-way radial Action Wheel.

        Key layout and segment angles (clock positions):
        q   w   e       q=10:00  w=12:00  e= 2:00
        a       d       a= 9:00           d= 3:00
        z   s   c       z= 8:00  s= 6:00  c= 4:00
                            
        Single keys snap to 0°/90°/180°/270° and the 2:00/4:00/8:00/10:00 positions.
        Two-key combos (w+e, s+c, w+q, s+z) snap to the 1:00/5:00/7:00/11:00 positions.
        Conflicting opposites (w+s, a+d) cancel to neutral.
        """

        key = self.l_joystick_keys

        w = key.get('w', False)
        a = key.get('a', False)
        s = key.get('s', False)
        d = key.get('d', False)
        q = key.get('q', False)
        e = key.get('e', False)
        z = key.get('z', False)
        c = key.get('c', False)

        lx, ly = 0.0, 0.0

        # --- Cardinals (single keys, 0/90/180/270°) ---
        if w and not s:  ly += 1.0
        if s and not w:  ly -= 1.0
        if d and not a:  lx += 1.0
        if a and not d:  lx -= 1.0

        # --- Off-axis singles: 2:00 (30°), 4:00 (330°), 8:00 (210°), 10:00 (150°) ---
        # These override cardinals when pressed — they are their own dedicated segment keys.
        if e and not (w or s or a or d):  lx =  _SEG_30; ly =  _SEG_60   #  2:00  30° off right
        if c and not (w or s or a or d):  lx =  _SEG_30; ly = -_SEG_60   #  4:00  30° off right
        if z and not (w or s or a or d):  lx = -_SEG_30; ly = -_SEG_60   #  8:00  30° off left
        if q and not (w or s or a or d):  lx = -_SEG_30; ly =  _SEG_60   # 10:00  30° off left

        # --- Two-key combos: 1:00 (60°), 5:00 (300°), 7:00 (240°), 11:00 (120°) ---
        if w and e:  lx =  _SEG_60; ly =  _SEG_30   #  1:00
        if s and c:  lx =  _SEG_60; ly = -_SEG_30   #  5:00
        if s and z:  lx = -_SEG_60; ly = -_SEG_30   #  7:00
        if w and q:  lx = -_SEG_60; ly =  _SEG_30   # 11:00
        
        self._gamepad.left_joystick_float(x_value_float=lx, y_value_float=ly)
        self.last_lx, self.last_ly = lx, ly
    
    def _process_right_joystick(self):
        """Process  for right joystick."""
        
        rx, ry = 0.0, 0.0
        
        any_key = False
        
        for key in Config.R_JOYSTICK_KEYS:
            if self.r_joystick_keys.get(key, False):
                any_key = True
                if key == 'right':
                    lx += 1.0
                elif key == 'left':
                    lx -= 1.0
                elif key == 'up':
                    ly += 1.0
                elif key == 'down':
                    ly -= 1.0
        
        # Normalize diagonal movement
        if lx != 0 and ly != 0:
            magnitude = math.sqrt(lx * lx + ly * ly)
            lx /= magnitude
            ly /= magnitude
        
        # Reset if no keys pressed
        if not any_key:
            lx, ly = 0.0, 0.0
        
        self._gamepad.right_joystick_float(x_value_float=rx, y_value_float=ry)
        self.last_rx, self.last_ry = rx, ry
    
    def _process_buttons(self):
        """Process button states."""
        for key, button in Config.KEY_MAPPINGS.items():
            current_state = self.keys.get(key, False)
            if current_state:
                self._gamepad.press_button(button=button)
            else:
                self._gamepad.release_button(button=button)
    
    def _process_triggers(self):
        """Process trigger states."""
        if self.l2_held:
            self._gamepad.right_trigger_float(1.0)
        else:
            self._gamepad.right_trigger_float(0.0)
        
        if self.r2_held:
            self._gamepad.left_trigger_float(1.0)
        else:
            self._gamepad.left_trigger_float(0.0)
    
    def update_rate(self, new_rate: int):
        """Update the processing rate."""
        Config.UPDATE_RATE_HZ = new_rate
        self._update_interval = 1.0 / new_rate
    
    def shutdown(self):
        """Clean shutdown of the gamepad controller."""
        self.deactivate()
        if self._gamepad:
            try:
                self._gamepad.reset()
                self._gamepad.update()
            except:
                pass
            self._gamepad = None
        print("[CONTROLLER] Shutdown complete")
