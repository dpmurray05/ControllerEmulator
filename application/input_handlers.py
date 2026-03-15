"""
Input event handlers for keyboard and mouse events.
"""
from pynput import keyboard, mouse

from config.config import Config


class InputHandler:
    """Handles keyboard and mouse input events."""
    
    def __init__(self, controller):
        """Initialize input handler with controller reference."""
        self.controller = controller
    
    def on_key_press(self, key):
        """Handle key press events."""
        try:
            key_str = self._parse_key(key)
            
            # Handle toggle key
            if key_str == Config.TOGGLE_KEY:
                print(f"[INPUT] Toggle key pressed (Controller: {'ACTIVE' if self.controller.active else 'INACTIVE'})")
                if self.controller.active:
                    self.controller.deactivate()
                else:
                    self.controller.activate()
                return
            
            # Handle joystick keys
            if key_str in Config.L_JOYSTICK_KEYS:
                self.controller.L_joystick_keys[key_str] = True

            if key_str in Config.R_JOYSTICK_KEYS:
                self.controller.R_joystick_keys[key_str] = True
            
            # Handle mapped keys
            elif key_str in Config.KEY_MAPPINGS:
                self.controller.keys[key_str] = True
        
        except Exception as e:
            print(f"[ERROR] Key press error: {e}")
    
    def on_key_release(self, key):
        """Handle key release events."""
        try:
            key_str = self._parse_key(key)
            
            # Handle joystick keys
            if key_str in Config.L_JOYSTICK_KEYS:
                self.controller.l_joystick_keys[key_str] = False

            if key_str in Config.R_JOYSTICK_KEYS:
                self.controller.r_joystick_keys[key_str] = False
            
            # Handle mapped keys
            elif key_str in Config.KEY_MAPPINGS:
                self.controller.keys[key_str] = False
        
        except Exception as e:
            print(f"[ERROR] Key release error: {e}")
    
    
    def on_mouse_click(self, x, y, button, pressed):
        """Handle mouse click events."""
        if button == mouse.Button.left:
            self.controller.l2_held = pressed
        elif button == mouse.Button.right:
            self.controller.r2_held = pressed
    
    @staticmethod
    def _parse_key(key) -> str:
        """Parse key object to string identifier."""
        if hasattr(key, 'char') and key.char:
            return key.char.lower()
        
        # Special keys
        key_str = str(key).replace('Key.', '').lower()
        
        if key_str == 'alt':
            return 'alt_l' if key == keyboard.Key.alt_l else 'alt_r'
        elif key_str in ('shift', 'shift_l', 'shift_r'):
            return 'shift'
        elif key == keyboard.Key.esc:
            return 'esc'
        elif key == keyboard.Key.tab:
            return 'tab'
        elif key == keyboard.Key.space:
            return 'space'
        
        return key_str
