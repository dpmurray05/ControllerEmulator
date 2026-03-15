"""
Input listener classes with conditional suppression support.
"""
from pynput import keyboard, mouse


class ConditionalSuppressMouseListener(mouse.Listener):
    """Mouse listener with conditional event suppression."""
    
    def __init__(self, on_click=None, on_scroll=None):
        super().__init__(
            on_click=on_click,
            on_scroll=on_scroll,
            suppress=False
        )
        self._suppress = False
    
    def suppress_events(self, suppress: bool):
        """Enable or disable event suppression."""
        self._suppress = suppress
        print(f"[INPUT] Mouse suppression {'ENABLED' if suppress else 'DISABLED'}")
    
    def _suppress_event(self, event):
        """Determine if event should be suppressed."""
        return self._suppress


class ConditionalSuppressKeyboardListener(keyboard.Listener):
    """Keyboard listener with conditional event suppression."""
    
    def __init__(self, on_press=None, on_release=None, toggle_key='t'):
        super().__init__(
            on_press=on_press,
            on_release=on_release,
            suppress=False
        )
        self._suppress = False
        self._toggle_key = toggle_key
    
    def suppress_events(self, suppress: bool):
        """Enable or disable event suppression."""
        self._suppress = suppress
        print(f"[INPUT] Keyboard suppression {'ENABLED' if suppress else 'DISABLED'}")
    
    def set_toggle_key(self, key: str):
        """Update the toggle key."""
        self._toggle_key = key
    
    def _suppress_event(self, event):
        """Determine if event should be suppressed."""
        # Never suppress toggle key
        try:
            if hasattr(event, 'char') and event.char:
                if event.char.lower() == self._toggle_key:
                    return False
        except:
            pass
        
        return self._suppress
