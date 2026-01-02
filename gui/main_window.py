"""
Main application window using CustomTkinter.
Integrated with all modules: file browser, metadata editor, organizer, duplicate finder, and JSON export.
"""

import customtkinter as ctk
from pathlib import Path
import json
import threading
import os
from typing import Optional, List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import core modules
from core.metadata import MetadataHandler
from core.database import MusicDatabase
from core.file_organizer import FileOrganizer
from core.duplicate_detector import DuplicateDetector

# Import GUI components
from gui.file_browser import FileBrowser
from gui.metadata_editor import MetadataEditor
from gui.organizer_panel import OrganizerPanel
from gui.duplicate_panel import DuplicatePanel

# Import utilities
from utils.json_export import JSONExporter


class MainWindow(ctk.CTk):
    """Main application window with full feature integration."""

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

        # Initialize core components
        self.db = MusicDatabase(self.settings.get('database_path'))
        self.metadata_handler = MetadataHandler()
        self.file_organizer = FileOrganizer()
        self.duplicate_detector = DuplicateDetector(
            tolerance=self.settings.get('duplicate_detection', {}).get('metadata_tolerance', 0.9)
        )
        self.json_exporter = JSONExporter()

        # State variables
        self.current_view = "library"
        self.current_folder = None
        self.all_files = []
        self.selected_files = []

        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Create UI components
        self._create_header()
        self._create_sidebar()
        self._create_main_content()
        self._create_status_bar()

        # Initialize with library view
        self._switch_view("library")

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

        # Refresh button
        self.refresh_btn = ctk.CTkButton(
            header_frame,
            text="🔄 Refresh",
            command=self._refresh_library,
            width=150
        )
        self.refresh_btn.grid(row=0, column=2, padx=10, pady=15)

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
            self.current_folder = folder_path
            self.update_status(f"Selected: {folder_path}")

    def _scan_library(self):
        """Scan library in background thread with parallel processing."""
        if not self.current_folder:
            self.update_status("Please select a folder first")
            return

        self.update_status("Scanning library...")
        self.scan_btn.configure(state="disabled")

        def scan_thread():
            try:
                # Scan directory for music files
                files = self.metadata_handler.scan_directory(self.current_folder, recursive=True)
                total_files = len(files)

                self.update_status(f"Found {total_files} files, reading metadata...")

                # Read metadata in parallel using ThreadPoolExecutor
                metadata_list = []
                processed_count = 0

                # Use number of CPU cores for parallel processing
                max_workers = min(8, os.cpu_count() or 4)

                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    # Submit all tasks
                    future_to_file = {
                        executor.submit(self.metadata_handler.read_metadata, file_path): file_path
                        for file_path in files
                    }

                    # Process results as they complete
                    for future in as_completed(future_to_file):
                        try:
                            metadata = future.result()
                            if metadata:
                                metadata_list.append(metadata)

                            processed_count += 1

                            # Update progress more frequently
                            if processed_count % 5 == 0 or processed_count == total_files:
                                percentage = int((processed_count / total_files) * 100)
                                self.update_status(
                                    f"Processing {processed_count} of {total_files} files ({percentage}%)..."
                                )

                        except Exception as e:
                            print(f"Error reading metadata: {e}")
                            processed_count += 1

                # Add to database
                count = self.db.add_files_batch(metadata_list)

                self.update_status(f"Scan complete: {count} files added to library")

                # Refresh library view
                self.after(100, self._refresh_library)

            except Exception as e:
                self.update_status(f"Error scanning: {str(e)}")
            finally:
                self.after(100, lambda: self.scan_btn.configure(state="normal"))

        thread = threading.Thread(target=scan_thread, daemon=True)
        thread.start()

    def _refresh_library(self):
        """Refresh the library view."""
        self.all_files = self.db.get_all_files()
        self.update_file_count(len(self.all_files))

        if self.current_view == "library":
            self._show_library_view()

        self.update_status(f"Library refreshed: {len(self.all_files)} files")

    def _switch_view(self, view_name: str):
        """Switch between different views."""
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

    def _show_library_view(self):
        """Show library view with file browser."""
        self.file_browser = FileBrowser(
            self.content_frame,
            on_selection_changed=self._on_file_selection_changed
        )
        self.file_browser.pack(fill="both", expand=True)

        # Load files
        self.file_browser.load_files(self.all_files)

    def _show_tags_view(self):
        """Show tags editor view."""
        self.metadata_editor = MetadataEditor(
            self.content_frame,
            on_save=self._on_metadata_save
        )
        self.metadata_editor.pack(fill="both", expand=True)

        # Load selected files
        if self.selected_files:
            self.metadata_editor.load_files(self.selected_files)

    def _show_organize_view(self):
        """Show organize view."""
        self.organizer_panel = OrganizerPanel(
            self.content_frame,
            on_organize=self._on_organize_action
        )
        self.organizer_panel.pack(fill="both", expand=True)

        # Load selected files or all files
        files_to_organize = self.selected_files if self.selected_files else self.all_files
        self.organizer_panel.load_files(files_to_organize)

    def _show_duplicates_view(self):
        """Show duplicates finder view."""
        self.duplicate_panel = DuplicatePanel(
            self.content_frame,
            on_find=self._on_find_duplicates,
            on_action=self._on_duplicate_action
        )
        self.duplicate_panel.pack(fill="both", expand=True)

        self.duplicate_panel.load_files(self.all_files)

    def _show_export_view(self):
        """Show export view."""
        export_frame = ctk.CTkFrame(self.content_frame)
        export_frame.pack(fill="both", expand=True, padx=20, pady=20)

        title = ctk.CTkLabel(
            export_frame,
            text="Export Library Data",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title.pack(pady=10)

        # Export JSON button
        json_btn = ctk.CTkButton(
            export_frame,
            text="💾 Export to JSON",
            command=self._export_to_json,
            width=200
        )
        json_btn.pack(pady=10)

        # Export CSV button
        csv_btn = ctk.CTkButton(
            export_frame,
            text="📄 Export to CSV",
            command=self._export_to_csv,
            width=200
        )
        csv_btn.pack(pady=10)

        # Create backup button
        backup_btn = ctk.CTkButton(
            export_frame,
            text="📦 Create Backup",
            command=self._create_backup,
            width=200
        )
        backup_btn.pack(pady=10)

    def _on_file_selection_changed(self, selected_files: List[Dict[str, Any]]):
        """Handle file selection changes."""
        self.selected_files = selected_files

    def _on_metadata_save(self, files: List[Dict[str, Any]], metadata: Dict[str, Any]):
        """Handle metadata save."""
        try:
            success_count = 0

            for file_data in files:
                file_path = file_data.get('file_path')

                # Write to file
                if self.metadata_handler.write_metadata(file_path, metadata):
                    # Update database
                    self.db.update_file(file_data.get('id'), metadata)
                    success_count += 1

            self.update_status(f"Updated {success_count} files")
            self._refresh_library()

        except Exception as e:
            self.update_status(f"Error saving metadata: {str(e)}")

    def _on_organize_action(self, action: str, data: Any, pattern: Optional[str] = None):
        """Handle file organization actions."""
        if action == 'preview':
            # Generate preview
            return self.file_organizer.preview_organization(data, pattern)

        elif action == 'dry_run':
            # Perform dry run
            return self.file_organizer.organize_files(data, dry_run=True)

        elif action == 'execute':
            # Execute organization
            results = self.file_organizer.organize_files(data, dry_run=False)

            # Update database with new paths
            for result in results:
                if result.get('status') == 'success':
                    file_id = result.get('id')
                    new_path = result.get('new_path')
                    self.db.update_file(file_id, {'file_path': new_path})

            self._refresh_library()
            return results

    def _on_find_duplicates(self, method: str, tolerance: float):
        """Handle duplicate finding."""
        try:
            if method == "Metadata":
                groups = self.duplicate_detector.find_duplicates_by_metadata(self.all_files)
            elif method == "File Hash":
                groups = self.duplicate_detector.find_duplicates_by_hash(self.all_files)
            elif method == "Size & Duration":
                groups = self.duplicate_detector.find_duplicates_by_size_and_duration(self.all_files)
            else:  # Combined
                groups = self.duplicate_detector.find_duplicates_combined(self.all_files)

            self.update_status(f"Found {len(groups)} duplicate groups")
            return groups

        except Exception as e:
            self.update_status(f"Error finding duplicates: {str(e)}")
            return []

    def _on_duplicate_action(self, action: str, files: List[Dict[str, Any]]):
        """Handle duplicate removal action."""
        if action == 'remove':
            try:
                for file_data in files:
                    file_path = file_data.get('path')
                    file_id = file_data.get('id')

                    # Delete file
                    if os.path.exists(file_path):
                        os.remove(file_path)

                    # Remove from database
                    self.db.delete_file(file_id)

                self.update_status(f"Removed {len(files)} duplicate files")
                self._refresh_library()
                return True

            except Exception as e:
                self.update_status(f"Error removing files: {str(e)}")
                return False

    def _export_to_json(self):
        """Export library to JSON."""
        file_path = ctk.filedialog.asksaveasfilename(
            title="Save JSON Export",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if file_path:
            success, error = self.json_exporter.export_to_json(self.all_files, file_path)

            if success:
                self.update_status(f"Exported {len(self.all_files)} files to JSON")
            else:
                self.update_status(f"Export failed: {error}")

    def _export_to_csv(self):
        """Export library to CSV."""
        file_path = ctk.filedialog.asksaveasfilename(
            title="Save CSV Export",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if file_path:
            success, error = self.json_exporter.export_csv(self.all_files, file_path)

            if success:
                self.update_status(f"Exported {len(self.all_files)} files to CSV")
            else:
                self.update_status(f"Export failed: {error}")

    def _create_backup(self):
        """Create a backup of library data."""
        backup_dir = self.settings.get('json_backup_path', str(Path.home() / '.music_manager' / 'backups'))

        success, backup_path, error = self.json_exporter.create_backup(self.all_files, backup_dir)

        if success:
            self.update_status(f"Backup created: {backup_path}")
        else:
            self.update_status(f"Backup failed: {error}")

    def update_status(self, message: str):
        """Update the status bar message."""
        self.status_label.configure(text=message)

    def update_file_count(self, count: int):
        """Update the file count display."""
        self.file_count_label.configure(text=f"Files: {count}")

    def on_closing(self):
        """Handle window closing."""
        self.db.close()
        self.destroy()
