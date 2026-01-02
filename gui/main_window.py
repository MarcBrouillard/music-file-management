"""
Main application window using CustomTkinter.
"""

import customtkinter as ctk
from pathlib import Path
import json
from typing import Optional


class MainWindow(ctk.CTk):
    """Main application window."""

    def __init__(self):
        """Initialize the main window."""
        super().__init__()

        # Load settings
        self.settings = self._load_settings()

        # Configure window
        self.title("Music File Management")
        width = self.settings.get('window', {}).get('width', 1200)
        height = self.settings.get('window', {}).get('height', 800)
        self.geometry(f"{width}x{height}")

        # Set theme
        ctk.set_appearance_mode(self.settings.get('theme', 'dark'))
        ctk.set_default_color_theme("blue")

        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Create UI components
        self._create_header()
        self._create_sidebar()
        self._create_main_content()
        self._create_status_bar()

        # Initialize state
        self.current_view = "library"

    def _load_settings(self) -> dict:
        """Load application settings."""
        try:
            settings_path = Path(__file__).parent.parent / 'config' / 'settings.json'
            with open(settings_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading settings: {e}")
            return {}

    def _create_header(self):
        """Create the header toolbar."""
        header_frame = ctk.CTkFrame(self, height=60, corner_radius=0)
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=0, pady=0)
        header_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # Browse folder button
        self.browse_btn = ctk.CTkButton(
            header_frame,
            text="📂 Browse Folder",
            command=self._browse_folder,
            width=150
        )
        self.browse_btn.grid(row=0, column=0, padx=10, pady=15)

        # Scan library button
        self.scan_btn = ctk.CTkButton(
            header_frame,
            text="🔍 Scan Library",
            command=self._scan_library,
            width=150
        )
        self.scan_btn.grid(row=0, column=1, padx=10, pady=15)

        # Settings button
        self.settings_btn = ctk.CTkButton(
            header_frame,
            text="⚙️ Settings",
            command=self._open_settings,
            width=150
        )
        self.settings_btn.grid(row=0, column=2, padx=10, pady=15)

    def _create_sidebar(self):
        """Create the sidebar navigation."""
        sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        sidebar_frame.grid(row=1, column=0, sticky="nsw", padx=0, pady=0)
        sidebar_frame.grid_rowconfigure((0, 1, 2, 3, 4, 5), weight=0)
        sidebar_frame.grid_propagate(False)

        # App title
        title_label = ctk.CTkLabel(
            sidebar_frame,
            text="Music Manager",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=(20, 30))

        # Navigation buttons
        self.library_btn = ctk.CTkButton(
            sidebar_frame,
            text="📂 Library",
            command=lambda: self._switch_view("library"),
            width=160,
            anchor="w"
        )
        self.library_btn.grid(row=1, column=0, padx=20, pady=10)

        self.tags_btn = ctk.CTkButton(
            sidebar_frame,
            text="🏷️  Tags",
            command=lambda: self._switch_view("tags"),
            width=160,
            anchor="w"
        )
        self.tags_btn.grid(row=2, column=0, padx=20, pady=10)

        self.organize_btn = ctk.CTkButton(
            sidebar_frame,
            text="📁 Organize",
            command=lambda: self._switch_view("organize"),
            width=160,
            anchor="w"
        )
        self.organize_btn.grid(row=3, column=0, padx=20, pady=10)

        self.duplicates_btn = ctk.CTkButton(
            sidebar_frame,
            text="🔍 Find Duplicates",
            command=lambda: self._switch_view("duplicates"),
            width=160,
            anchor="w"
        )
        self.duplicates_btn.grid(row=4, column=0, padx=20, pady=10)

        self.export_btn = ctk.CTkButton(
            sidebar_frame,
            text="💾 Export",
            command=lambda: self._switch_view("export"),
            width=160,
            anchor="w"
        )
        self.export_btn.grid(row=5, column=0, padx=20, pady=10)

    def _create_main_content(self):
        """Create the main content area."""
        self.content_frame = ctk.CTkFrame(self, corner_radius=0)
        self.content_frame.grid(row=1, column=1, sticky="nsew", padx=0, pady=0)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

        # Welcome message
        self.welcome_label = ctk.CTkLabel(
            self.content_frame,
            text="Welcome to Music File Management\n\nClick 'Browse Folder' to select your music library",
            font=ctk.CTkFont(size=16),
            justify="center"
        )
        self.welcome_label.grid(row=0, column=0, padx=20, pady=20)

    def _create_status_bar(self):
        """Create the status bar."""
        self.status_frame = ctk.CTkFrame(self, height=30, corner_radius=0)
        self.status_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=0, pady=0)

        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Ready",
            anchor="w"
        )
        self.status_label.pack(side="left", padx=10, pady=5)

        self.file_count_label = ctk.CTkLabel(
            self.status_frame,
            text="Files: 0",
            anchor="e"
        )
        self.file_count_label.pack(side="right", padx=10, pady=5)

    def _browse_folder(self):
        """Handle browse folder action."""
        folder_path = ctk.filedialog.askdirectory(title="Select Music Folder")
        if folder_path:
            self.status_label.configure(text=f"Selected: {folder_path}")
            # TODO: Implement folder scanning

    def _scan_library(self):
        """Handle scan library action."""
        self.status_label.configure(text="Scanning library...")
        # TODO: Implement library scanning

    def _open_settings(self):
        """Handle settings action."""
        self.status_label.configure(text="Settings opened")
        # TODO: Implement settings dialog

    def _switch_view(self, view_name: str):
        """
        Switch between different views.

        Args:
            view_name: Name of the view to switch to
        """
        self.current_view = view_name

        # Clear current content
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Show view-specific content
        if view_name == "library":
            self._show_library_view()
        elif view_name == "tags":
            self._show_tags_view()
        elif view_name == "organize":
            self._show_organize_view()
        elif view_name == "duplicates":
            self._show_duplicates_view()
        elif view_name == "export":
            self._show_export_view()

        self.status_label.configure(text=f"Switched to {view_name.title()} view")

    def _show_library_view(self):
        """Show library view."""
        label = ctk.CTkLabel(
            self.content_frame,
            text="Library View\n\nYour music files will appear here",
            font=ctk.CTkFont(size=16)
        )
        label.pack(expand=True, pady=20)

    def _show_tags_view(self):
        """Show tags editor view."""
        label = ctk.CTkLabel(
            self.content_frame,
            text="Tags Editor\n\nSelect files to edit their metadata",
            font=ctk.CTkFont(size=16)
        )
        label.pack(expand=True, pady=20)

    def _show_organize_view(self):
        """Show organize view."""
        label = ctk.CTkLabel(
            self.content_frame,
            text="File Organization\n\nAutomatically organize your music files",
            font=ctk.CTkFont(size=16)
        )
        label.pack(expand=True, pady=20)

    def _show_duplicates_view(self):
        """Show duplicates finder view."""
        label = ctk.CTkLabel(
            self.content_frame,
            text="Duplicate Finder\n\nFind and manage duplicate files",
            font=ctk.CTkFont(size=16)
        )
        label.pack(expand=True, pady=20)

    def _show_export_view(self):
        """Show export view."""
        label = ctk.CTkLabel(
            self.content_frame,
            text="Export Data\n\nExport your library metadata to JSON",
            font=ctk.CTkFont(size=16)
        )
        label.pack(expand=True, pady=20)

    def update_status(self, message: str):
        """
        Update the status bar message.

        Args:
            message: Status message to display
        """
        self.status_label.configure(text=message)

    def update_file_count(self, count: int):
        """
        Update the file count display.

        Args:
            count: Number of files
        """
        self.file_count_label.configure(text=f"Files: {count}")
