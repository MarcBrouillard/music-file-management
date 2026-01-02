"""
File organization panel for organizing and renaming music files.
"""

import customtkinter as ctk
from tkinter import ttk
from typing import List, Dict, Any, Optional, Callable
from pathlib import Path


class OrganizerPanel(ctk.CTkFrame):
    """Panel for organizing and renaming music files."""

    def __init__(self, parent, on_organize: Optional[Callable] = None):
        """
        Initialize the organizer panel.

        Args:
            parent: Parent widget
            on_organize: Callback when organize is executed
        """
        super().__init__(parent)

        self.on_organize = on_organize
        self.preview_data = []
        self.selected_files = []

        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Create UI components
        self._create_title()
        self._create_pattern_selector()
        self._create_preview_area()
        self._create_buttons()

    def _create_title(self):
        """Create title section."""
        title_frame = ctk.CTkFrame(self)
        title_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        title_label = ctk.CTkLabel(
            title_frame,
            text="File Organization",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=5)

        info_label = ctk.CTkLabel(
            title_frame,
            text="Organize and rename your music files based on metadata",
            font=ctk.CTkFont(size=12)
        )
        info_label.pack(pady=2)

    def _create_pattern_selector(self):
        """Create pattern selection controls."""
        pattern_frame = ctk.CTkFrame(self)
        pattern_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        pattern_frame.grid_columnconfigure(1, weight=1)

        # Pattern label
        pattern_label = ctk.CTkLabel(pattern_frame, text="Pattern:")
        pattern_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)

        # Pattern dropdown
        self.pattern_var = ctk.StringVar(value="artist_album_track")

        pattern_options = [
            "Artist/Album/Track - Title",
            "Artist/Year - Album/Track - Title",
            "Genre/Artist/Album/Track - Title",
            "Artist - Album/Track - Title",
            "Artist - Title",
            "Track - Title"
        ]

        self.pattern_dropdown = ctk.CTkOptionMenu(
            pattern_frame,
            variable=self.pattern_var,
            values=pattern_options,
            command=self._on_pattern_changed
        )
        self.pattern_dropdown.grid(row=0, column=1, sticky="ew", padx=10, pady=5)

        # Preview button
        self.preview_btn = ctk.CTkButton(
            pattern_frame,
            text="🔍 Preview",
            command=self._preview_organization,
            width=100
        )
        self.preview_btn.grid(row=0, column=2, padx=10, pady=5)

        # Custom pattern frame
        custom_frame = ctk.CTkFrame(pattern_frame)
        custom_frame.grid(row=1, column=0, columnspan=3, sticky="ew", padx=10, pady=5)
        custom_frame.grid_columnconfigure(1, weight=1)

        custom_label = ctk.CTkLabel(custom_frame, text="Custom Pattern:")
        custom_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)

        self.custom_pattern_entry = ctk.CTkEntry(
            custom_frame,
            placeholder_text="{artist}/{album}/{track:02d} - {title}"
        )
        self.custom_pattern_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        help_label = ctk.CTkLabel(
            custom_frame,
            text="Available: {artist}, {title}, {album}, {year}, {genre}, {track}",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        help_label.grid(row=1, column=0, columnspan=2, sticky="w", padx=5, pady=2)

    def _create_preview_area(self):
        """Create preview tree view."""
        preview_frame = ctk.CTkFrame(self)
        preview_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        preview_frame.grid_columnconfigure(0, weight=1)
        preview_frame.grid_rowconfigure(0, weight=1)

        # Label
        label = ctk.CTkLabel(
            preview_frame,
            text="Preview (Before → After)",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        label.grid(row=0, column=0, sticky="w", padx=10, pady=5)

        # Tree view frame
        tree_frame = ctk.CTkFrame(preview_frame)
        tree_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)

        # Create tree view
        columns = ('old_name', 'new_name', 'old_dir', 'new_dir')

        self.preview_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show='headings',
            selectmode='browse'
        )

        # Define headings
        self.preview_tree.heading('old_name', text='Old Filename')
        self.preview_tree.heading('new_name', text='New Filename')
        self.preview_tree.heading('old_dir', text='Old Directory')
        self.preview_tree.heading('new_dir', text='New Directory')

        # Define column widths
        self.preview_tree.column('old_name', width=200)
        self.preview_tree.column('new_name', width=200)
        self.preview_tree.column('old_dir', width=200)
        self.preview_tree.column('new_dir', width=200)

        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.preview_tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.preview_tree.xview)
        self.preview_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Grid layout
        self.preview_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        # Configure style
        style = ttk.Style()
        style.configure("Treeview",
                       background="#2b2b2b",
                       foreground="white",
                       fieldbackground="#2b2b2b")
        style.map('Treeview', background=[('selected', '#1f538d')])

        # Status label
        self.preview_status_label = ctk.CTkLabel(
            preview_frame,
            text="No preview generated",
            font=ctk.CTkFont(size=12)
        )
        self.preview_status_label.grid(row=2, column=0, sticky="w", padx=10, pady=5)

    def _create_buttons(self):
        """Create action buttons."""
        button_frame = ctk.CTkFrame(self)
        button_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=10)
        button_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # Dry run button
        self.dry_run_btn = ctk.CTkButton(
            button_frame,
            text="🧪 Dry Run",
            command=self._dry_run,
            fg_color="orange",
            hover_color="darkorange"
        )
        self.dry_run_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        # Execute button
        self.execute_btn = ctk.CTkButton(
            button_frame,
            text="✓ Execute Organization",
            command=self._execute_organization,
            fg_color="green",
            hover_color="darkgreen"
        )
        self.execute_btn.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Cancel button
        self.cancel_btn = ctk.CTkButton(
            button_frame,
            text="✕ Clear Preview",
            command=self._clear_preview,
            fg_color="gray",
            hover_color="darkgray"
        )
        self.cancel_btn.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

    def load_files(self, files: List[Dict[str, Any]]):
        """
        Load files for organization.

        Args:
            files: List of file metadata dictionaries
        """
        self.selected_files = files

        if not files:
            self._clear_preview()
            self.preview_status_label.configure(text="No files selected")
        else:
            self.preview_status_label.configure(text=f"{len(files)} files ready for organization")

    def _get_pattern_key(self, pattern_name: str) -> str:
        """
        Get pattern key from display name.

        Args:
            pattern_name: Display name of pattern

        Returns:
            str: Pattern key
        """
        pattern_map = {
            "Artist/Album/Track - Title": "artist_album_track",
            "Artist/Year - Album/Track - Title": "artist_year_album_track",
            "Genre/Artist/Album/Track - Title": "genre_artist_album",
            "Artist - Album/Track - Title": "artist_album",
            "Artist - Title": "simple",
            "Track - Title": "track_title"
        }
        return pattern_map.get(pattern_name, "artist_album_track")

    def _on_pattern_changed(self, pattern_name: str):
        """
        Handle pattern selection change.

        Args:
            pattern_name: Selected pattern name
        """
        # Clear custom pattern when preset is selected
        self.custom_pattern_entry.delete(0, 'end')

    def _preview_organization(self):
        """Generate preview of organization."""
        if not self.selected_files:
            self.preview_status_label.configure(text="No files to preview")
            return

        # Get pattern
        custom_pattern = self.custom_pattern_entry.get().strip()

        if custom_pattern:
            pattern = custom_pattern
        else:
            pattern_name = self.pattern_var.get()
            pattern_key = self._get_pattern_key(pattern_name)

            # Pattern templates
            patterns = {
                'artist_album_track': '{artist}/{album}/{track:02d} - {title}',
                'artist_year_album_track': '{artist}/{year} - {album}/{track:02d} - {title}',
                'genre_artist_album': '{genre}/{artist}/{album}/{track:02d} - {title}',
                'artist_album': '{artist} - {album}/{track:02d} - {title}',
                'simple': '{artist} - {title}',
                'track_title': '{track:02d} - {title}',
            }

            pattern = patterns.get(pattern_key, patterns['artist_album_track'])

        # Generate preview using callback
        if self.on_organize:
            self.preview_data = self.on_organize('preview', self.selected_files, pattern)
            self._display_preview(self.preview_data)

    def _display_preview(self, preview_data: List[Dict[str, str]]):
        """
        Display preview in tree view.

        Args:
            preview_data: List of preview dictionaries
        """
        # Clear existing items
        for item in self.preview_tree.get_children():
            self.preview_tree.delete(item)

        if not preview_data:
            self.preview_status_label.configure(text="No changes needed")
            return

        # Add preview items
        for item in preview_data:
            values = (
                Path(item['old_path']).name,
                Path(item['new_path']).name,
                str(Path(item['old_path']).parent),
                str(Path(item['new_path']).parent)
            )

            self.preview_tree.insert('', 'end', values=values)

        self.preview_status_label.configure(
            text=f"Preview: {len(preview_data)} files will be changed"
        )

    def _dry_run(self):
        """Perform dry run without actually moving files."""
        if not self.preview_data:
            self.preview_status_label.configure(text="Generate preview first")
            return

        if self.on_organize:
            results = self.on_organize('dry_run', self.preview_data, None)
            self._show_results(results, dry_run=True)

    def _execute_organization(self):
        """Execute the file organization."""
        if not self.preview_data:
            self.preview_status_label.configure(text="Generate preview first")
            return

        # Confirm with user
        if self.on_organize:
            results = self.on_organize('execute', self.preview_data, None)
            self._show_results(results, dry_run=False)
            self._clear_preview()

    def _show_results(self, results: List[Dict[str, Any]], dry_run: bool = False):
        """
        Show organization results.

        Args:
            results: List of result dictionaries
            dry_run: Whether this was a dry run
        """
        success_count = sum(1 for r in results if r.get('status') in ['success', 'dry_run_ok'])
        error_count = sum(1 for r in results if r.get('status') == 'error')
        skipped_count = sum(1 for r in results if r.get('status') == 'skipped')

        mode = "Dry run" if dry_run else "Organization"
        message = f"{mode} complete: {success_count} successful, {error_count} errors, {skipped_count} skipped"

        self.preview_status_label.configure(text=message)

    def _clear_preview(self):
        """Clear the preview."""
        for item in self.preview_tree.get_children():
            self.preview_tree.delete(item)

        self.preview_data = []
        self.preview_status_label.configure(text="Preview cleared")
