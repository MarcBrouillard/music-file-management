"""
Metadata editor panel for editing music file tags.
"""

import customtkinter as ctk
from typing import List, Dict, Any, Optional, Callable
from pathlib import Path


class MetadataEditor(ctk.CTkFrame):
    """Editor panel for music file metadata."""

    def __init__(self, parent, on_save: Optional[Callable] = None):
        """
        Initialize the metadata editor.

        Args:
            parent: Parent widget
            on_save: Callback when save is clicked
        """
        super().__init__(parent)

        self.on_save = on_save
        self.current_files = []
        self.is_batch_mode = False

        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Create title
        self._create_title()

        # Create editor form
        self._create_editor_form()

        # Create buttons
        self._create_buttons()

        # Initially disabled
        self._set_enabled(False)

    def _create_title(self):
        """Create title section."""
        title_frame = ctk.CTkFrame(self)
        title_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        self.title_label = ctk.CTkLabel(
            title_frame,
            text="Metadata Editor",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.title_label.pack(pady=5)

        self.file_info_label = ctk.CTkLabel(
            title_frame,
            text="No files selected",
            font=ctk.CTkFont(size=12)
        )
        self.file_info_label.pack(pady=2)

    def _create_editor_form(self):
        """Create the editor form."""
        # Scrollable frame for form
        self.form_frame = ctk.CTkScrollableFrame(self)
        self.form_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        self.form_frame.grid_columnconfigure(1, weight=1)

        # Artist
        artist_label = ctk.CTkLabel(self.form_frame, text="Artist:")
        artist_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)

        self.artist_entry = ctk.CTkEntry(self.form_frame, placeholder_text="Artist name")
        self.artist_entry.grid(row=0, column=1, sticky="ew", padx=10, pady=5)

        # Title
        title_label = ctk.CTkLabel(self.form_frame, text="Title:")
        title_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)

        self.title_entry = ctk.CTkEntry(self.form_frame, placeholder_text="Song title")
        self.title_entry.grid(row=1, column=1, sticky="ew", padx=10, pady=5)

        # Album
        album_label = ctk.CTkLabel(self.form_frame, text="Album:")
        album_label.grid(row=2, column=0, sticky="w", padx=10, pady=5)

        self.album_entry = ctk.CTkEntry(self.form_frame, placeholder_text="Album name")
        self.album_entry.grid(row=2, column=1, sticky="ew", padx=10, pady=5)

        # Year
        year_label = ctk.CTkLabel(self.form_frame, text="Year:")
        year_label.grid(row=3, column=0, sticky="w", padx=10, pady=5)

        self.year_entry = ctk.CTkEntry(self.form_frame, placeholder_text="YYYY")
        self.year_entry.grid(row=3, column=1, sticky="ew", padx=10, pady=5)

        # Genre
        genre_label = ctk.CTkLabel(self.form_frame, text="Genre:")
        genre_label.grid(row=4, column=0, sticky="w", padx=10, pady=5)

        self.genre_entry = ctk.CTkEntry(self.form_frame, placeholder_text="Genre")
        self.genre_entry.grid(row=4, column=1, sticky="ew", padx=10, pady=5)

        # Track Number
        track_label = ctk.CTkLabel(self.form_frame, text="Track #:")
        track_label.grid(row=5, column=0, sticky="w", padx=10, pady=5)

        self.track_entry = ctk.CTkEntry(self.form_frame, placeholder_text="Track number")
        self.track_entry.grid(row=5, column=1, sticky="ew", padx=10, pady=5)

        # File info (read-only)
        separator = ctk.CTkLabel(self.form_frame, text="─" * 50)
        separator.grid(row=6, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

        info_label = ctk.CTkLabel(
            self.form_frame,
            text="File Information",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        info_label.grid(row=7, column=0, columnspan=2, sticky="w", padx=10, pady=5)

        # Format
        format_label = ctk.CTkLabel(self.form_frame, text="Format:")
        format_label.grid(row=8, column=0, sticky="w", padx=10, pady=5)

        self.format_value = ctk.CTkLabel(self.form_frame, text="-")
        self.format_value.grid(row=8, column=1, sticky="w", padx=10, pady=5)

        # Duration
        duration_label = ctk.CTkLabel(self.form_frame, text="Duration:")
        duration_label.grid(row=9, column=0, sticky="w", padx=10, pady=5)

        self.duration_value = ctk.CTkLabel(self.form_frame, text="-")
        self.duration_value.grid(row=9, column=1, sticky="w", padx=10, pady=5)

        # Bitrate
        bitrate_label = ctk.CTkLabel(self.form_frame, text="Bitrate:")
        bitrate_label.grid(row=10, column=0, sticky="w", padx=10, pady=5)

        self.bitrate_value = ctk.CTkLabel(self.form_frame, text="-")
        self.bitrate_value.grid(row=10, column=1, sticky="w", padx=10, pady=5)

        # File size
        size_label = ctk.CTkLabel(self.form_frame, text="Size:")
        size_label.grid(row=11, column=0, sticky="w", padx=10, pady=5)

        self.size_value = ctk.CTkLabel(self.form_frame, text="-")
        self.size_value.grid(row=11, column=1, sticky="w", padx=10, pady=5)

        # File path
        path_label = ctk.CTkLabel(self.form_frame, text="Path:")
        path_label.grid(row=12, column=0, sticky="w", padx=10, pady=5)

        self.path_value = ctk.CTkLabel(
            self.form_frame,
            text="-",
            wraplength=300,
            justify="left"
        )
        self.path_value.grid(row=12, column=1, sticky="w", padx=10, pady=5)

    def _create_buttons(self):
        """Create action buttons."""
        button_frame = ctk.CTkFrame(self)
        button_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        button_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # Auto-fill from filename button
        self.autofill_btn = ctk.CTkButton(
            button_frame,
            text="🔧 Auto-fill from Filename",
            command=self._autofill_from_filename
        )
        self.autofill_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        # Save button
        self.save_btn = ctk.CTkButton(
            button_frame,
            text="💾 Save Changes",
            command=self._save_changes,
            fg_color="green",
            hover_color="darkgreen"
        )
        self.save_btn.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Cancel button
        self.cancel_btn = ctk.CTkButton(
            button_frame,
            text="✕ Cancel",
            command=self._cancel_changes,
            fg_color="gray",
            hover_color="darkgray"
        )
        self.cancel_btn.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

    def load_files(self, files: List[Dict[str, Any]]):
        """
        Load files for editing.

        Args:
            files: List of file metadata dictionaries
        """
        self.current_files = files

        if not files:
            self._clear_form()
            self._set_enabled(False)
            self.file_info_label.configure(text="No files selected")
            return

        self._set_enabled(True)

        if len(files) == 1:
            # Single file mode
            self.is_batch_mode = False
            self._load_single_file(files[0])
            filename = Path(files[0].get('file_path', '')).name
            self.file_info_label.configure(text=f"Editing: {filename}")
        else:
            # Batch edit mode
            self.is_batch_mode = True
            self._load_batch_files(files)
            self.file_info_label.configure(text=f"Batch editing {len(files)} files")

    def _load_single_file(self, file_data: Dict[str, Any]):
        """
        Load single file data into form.

        Args:
            file_data: File metadata dictionary
        """
        # Load editable fields
        self.artist_entry.delete(0, 'end')
        self.artist_entry.insert(0, file_data.get('artist', ''))

        self.title_entry.delete(0, 'end')
        self.title_entry.insert(0, file_data.get('title', ''))

        self.album_entry.delete(0, 'end')
        self.album_entry.insert(0, file_data.get('album', ''))

        self.year_entry.delete(0, 'end')
        if file_data.get('year'):
            self.year_entry.insert(0, str(file_data.get('year')))

        self.genre_entry.delete(0, 'end')
        self.genre_entry.insert(0, file_data.get('genre', ''))

        self.track_entry.delete(0, 'end')
        if file_data.get('track_number'):
            self.track_entry.insert(0, str(file_data.get('track_number')))

        # Load read-only fields
        self.format_value.configure(text=file_data.get('format', '-').upper())

        duration = file_data.get('duration', 0)
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        self.duration_value.configure(text=f"{minutes}:{seconds:02d}")

        bitrate = file_data.get('bitrate', 0)
        if bitrate:
            self.bitrate_value.configure(text=f"{bitrate // 1000} kbps")
        else:
            self.bitrate_value.configure(text="-")

        file_size = file_data.get('file_size', 0)
        size_mb = file_size / (1024 * 1024)
        self.size_value.configure(text=f"{size_mb:.2f} MB")

        self.path_value.configure(text=file_data.get('file_path', '-'))

    def _load_batch_files(self, files: List[Dict[str, Any]]):
        """
        Load multiple files for batch editing.

        Args:
            files: List of file metadata dictionaries
        """
        # Clear form
        self._clear_form()

        # Set placeholders for batch mode
        self.artist_entry.configure(placeholder_text="Leave empty to keep existing")
        self.title_entry.configure(placeholder_text="Leave empty to keep existing")
        self.album_entry.configure(placeholder_text="Leave empty to keep existing")
        self.year_entry.configure(placeholder_text="Leave empty to keep existing")
        self.genre_entry.configure(placeholder_text="Leave empty to keep existing")
        self.track_entry.configure(placeholder_text="Leave empty to keep existing")

        # Hide file info in batch mode
        self.format_value.configure(text="Multiple files")
        self.duration_value.configure(text="-")
        self.bitrate_value.configure(text="-")
        self.size_value.configure(text="-")
        self.path_value.configure(text="-")

    def _clear_form(self):
        """Clear all form fields."""
        self.artist_entry.delete(0, 'end')
        self.title_entry.delete(0, 'end')
        self.album_entry.delete(0, 'end')
        self.year_entry.delete(0, 'end')
        self.genre_entry.delete(0, 'end')
        self.track_entry.delete(0, 'end')

        self.format_value.configure(text="-")
        self.duration_value.configure(text="-")
        self.bitrate_value.configure(text="-")
        self.size_value.configure(text="-")
        self.path_value.configure(text="-")

    def _set_enabled(self, enabled: bool):
        """
        Enable or disable form controls.

        Args:
            enabled: Whether to enable controls
        """
        state = "normal" if enabled else "disabled"

        self.artist_entry.configure(state=state)
        self.title_entry.configure(state=state)
        self.album_entry.configure(state=state)
        self.year_entry.configure(state=state)
        self.genre_entry.configure(state=state)
        self.track_entry.configure(state=state)

        btn_state = "normal" if enabled else "disabled"
        self.autofill_btn.configure(state=btn_state)
        self.save_btn.configure(state=btn_state)
        self.cancel_btn.configure(state=btn_state)

    def _autofill_from_filename(self):
        """Auto-fill metadata from filename."""
        if not self.current_files or self.is_batch_mode:
            return

        file_data = self.current_files[0]
        filename = Path(file_data.get('file_path', '')).stem

        # Try to parse common patterns
        # Pattern: Artist - Title
        if ' - ' in filename:
            parts = filename.split(' - ', 1)
            if len(parts) == 2:
                self.artist_entry.delete(0, 'end')
                self.artist_entry.insert(0, parts[0].strip())
                self.title_entry.delete(0, 'end')
                self.title_entry.insert(0, parts[1].strip())

        # Pattern: Track - Artist - Title
        elif filename[0].isdigit():
            parts = filename.split(' - ', 2)
            if len(parts) >= 2:
                track = ''.join(filter(str.isdigit, parts[0]))
                if track:
                    self.track_entry.delete(0, 'end')
                    self.track_entry.insert(0, track)
                if len(parts) == 3:
                    self.artist_entry.delete(0, 'end')
                    self.artist_entry.insert(0, parts[1].strip())
                    self.title_entry.delete(0, 'end')
                    self.title_entry.insert(0, parts[2].strip())

    def _save_changes(self):
        """Save metadata changes."""
        if not self.current_files:
            return

        # Collect changed data
        metadata = {}

        artist = self.artist_entry.get().strip()
        if artist:
            metadata['artist'] = artist

        title = self.title_entry.get().strip()
        if title:
            metadata['title'] = title

        album = self.album_entry.get().strip()
        if album:
            metadata['album'] = album

        year = self.year_entry.get().strip()
        if year and year.isdigit():
            metadata['year'] = int(year)

        genre = self.genre_entry.get().strip()
        if genre:
            metadata['genre'] = genre

        track = self.track_entry.get().strip()
        if track and track.isdigit():
            metadata['track_number'] = int(track)

        # Call save callback
        if self.on_save and metadata:
            self.on_save(self.current_files, metadata)

    def _cancel_changes(self):
        """Cancel changes and reload original data."""
        if self.current_files:
            self.load_files(self.current_files)

    def get_metadata(self) -> Dict[str, Any]:
        """
        Get current metadata from form.

        Returns:
            dict: Current metadata values
        """
        metadata = {}

        artist = self.artist_entry.get().strip()
        if artist:
            metadata['artist'] = artist

        title = self.title_entry.get().strip()
        if title:
            metadata['title'] = title

        album = self.album_entry.get().strip()
        if album:
            metadata['album'] = album

        year = self.year_entry.get().strip()
        if year and year.isdigit():
            metadata['year'] = int(year)

        genre = self.genre_entry.get().strip()
        if genre:
            metadata['genre'] = genre

        track = self.track_entry.get().strip()
        if track and track.isdigit():
            metadata['track_number'] = int(track)

        return metadata
