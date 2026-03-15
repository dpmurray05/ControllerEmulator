"""
Configuration module for the Gamepad Emulator.
Contains all configurable settings and key mappings.
"""
import vgamepad as vg


class Config:
    """Central configuration for the gamepad emulator."""
    
    # Performance settings
    UPDATE_RATE_HZ = 120
    
    # Mouse sensitivity settings
    DPI_SCALING = 0.013
    SENS_X = 1.0
    SENS_Y = 1.0
    ADS_SENS_MULTIPLIER = 0.9
    
    # Input settings
    DEADZONE = 0.0012
    SMOOTHING = 0.0  # 0=no smoothing, 1=full smoothing
    
    # Recoil control settings
    RECOIL_CONTROL_ENABLED = True
    RECOIL_COMPENSATION = 1.8
    
    # Key mappings (Xbox controller button values)
    KEY_MAPPINGS = {
        'space': vg.XUSB_BUTTON.XUSB_GAMEPAD_A,
        'b': vg.XUSB_BUTTON.XUSB_GAMEPAD_B,
        'x': vg.XUSB_BUTTON.XUSB_GAMEPAD_X,
        'f': vg.XUSB_BUTTON.XUSB_GAMEPAD_Y,
        '1': vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP,
        '3': vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN,
        '4': vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT,
        '2': vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT,
        'tab': vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER,
        'r': vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER,
        'esc': vg.XUSB_BUTTON.XUSB_GAMEPAD_START,
        '`': vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK,
        'shift': vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB,
        'alt_l': vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_THUMB,
    }
    
    L_JOYSTICK_KEYS = ['w', 'a', 's', 'd', 'q', 'e', 'z', 'c']
    R_JOYSTICK_KEYS = ['up', 'left', 'down', 'right']
    TOGGLE_KEY = '*'
    
    @classmethod
    def reset_to_defaults(cls):
        """Reset all configuration to default values."""
        cls.UPDATE_RATE_HZ = 120
        cls.ADS_SENS_MULTIPLIER = 0.9
        cls.RECOIL_COMPENSATION = 1.8
        cls.TOGGLE_KEY = '*'
        cls.KEY_MAPPINGS = {
            'space': vg.XUSB_BUTTON.XUSB_GAMEPAD_A,
            'b': vg.XUSB_BUTTON.XUSB_GAMEPAD_B,
            'x': vg.XUSB_BUTTON.XUSB_GAMEPAD_X,
            'f': vg.XUSB_BUTTON.XUSB_GAMEPAD_Y,
            '1': vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP,
            '3': vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN,
            '4': vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT,
            '2': vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT,
            'tab': vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER,
            'r': vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER,
            'esc': vg.XUSB_BUTTON.XUSB_GAMEPAD_START,
            '`': vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK,
            'shift': vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB,
            'alt_l': vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_THUMB,
        }
