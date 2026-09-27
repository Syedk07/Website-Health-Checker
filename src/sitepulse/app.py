"""
Main application entry point and initialization.
"""

from .database import init_database
from .ui import MainWindow


class SitePulseApp:
    """Main application class for SitePulse."""
    
    def __init__(self):
        """Initialize the SitePulse application."""
        # Initialize database
        self.db_manager = init_database()
        
        # Create main window
        self.main_window = MainWindow(self.db_manager)
    
    def run(self):
        """Run the application."""
        try:
            self.main_window.run()
        finally:
            self.main_window.cleanup()


def main():
    """Application entry point."""
    app = SitePulseApp()
    app.run()


if __name__ == "__main__":
    main()
