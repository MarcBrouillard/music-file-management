"""
Music File Management Application
Main entry point for the application.
"""

import sys
from gui.main_window import MainWindow


def main():
    """Run the application."""
    try:
        app = MainWindow()
        app.mainloop()
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
