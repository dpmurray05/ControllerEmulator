"""
Main entry point for the Gamepad Emulator application.
"""
import time
import threading

from config.config import Config
from infrastructure.gamepad_controller import GamepadController
from application.input_listeners import ConditionalSuppressMouseListener, ConditionalSuppressKeyboardListener
from application.input_handlers import InputHandler
from presentation.gui import MainWindow


def main():
    """Main application entry point."""
    print("=" * 60)
    print("  GAMEPAD EMULATOR - CLEAN CODE VERSION")
    print("=" * 60)
    print("[OK] Press 'T' to toggle controller mode")
    print("[OK] Use Ctrl+C or close window to exit")
    print("=" * 60)
    
    # Initialize controller
    controller = GamepadController()
    
    # Initialize input handler
    input_handler = InputHandler(controller)
    
    # Create input listeners
    keyboard_listener = ConditionalSuppressKeyboardListener(
        on_press=input_handler.on_key_press,
        on_release=input_handler.on_key_release,
        toggle_key=Config.TOGGLE_KEY
    )
    
    mouse_listener = ConditionalSuppressMouseListener(
        on_click=input_handler.on_mouse_click
    )
    
    # Store listeners in controller
    controller.keyboard_listener = keyboard_listener
    controller.mouse_listener = mouse_listener
    
    # Start listeners
    print("[OK] Starting input listeners...")
    keyboard_listener.start()
    mouse_listener.start()
    print("[OK] Input listeners started")
    
    # Start processing loop in background thread
    processing_thread = threading.Thread(target=processing_loop, args=(controller,), daemon=True)
    processing_thread.start()
    print("[OK] Processing thread started")
    
    # Initialize and run GUI
    try:
        print("[OK] Starting UI...")
        ui = MainWindow(controller)
        ui.run()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        cleanup(controller, keyboard_listener, mouse_listener)


def processing_loop(controller):
    """Main processing loop for gamepad updates."""
    try:
        while True:
            controller.process_inputs()
            time.sleep(1.0 / Config.UPDATE_RATE_HZ)
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"[ERROR] Processing error: {e}")


def cleanup(controller, keyboard_listener, mouse_listener):
    """Cleanup resources on shutdown."""
    print("\n=== SHUTTING DOWN ===")
    controller.shutdown()
    keyboard_listener.stop()
    mouse_listener.stop()
    print("[OK] Cleanup complete")


if __name__ == "__main__":
    main()
