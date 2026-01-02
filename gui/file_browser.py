"""
File browser widget for displaying and managing music files.
"""

import customtkinter as ctk
from tkinter import ttk
from typing import List, Dict, Any, Callable, Optional
import threading


class FileBrowser(ctk.CTkFrame):
    """File browser with tree view for music library."""

    def __init__(self, parent, on_selection_changed: Optional[Callable] = None):
        """
        Initialize the file browser.

        Args:
            parent: Parent widget
            on_selection_changed: Callback when selection changes
        """
        super().__init__(parent)

        self.on_selection_changed = on_selection_changed
        self.files_data = []

        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Create search bar
        self._create_search_bar()

        # Create tree view
        self._create_tree_view()

        # Create buttons
        self._create_buttons()

    def _create_search_bar(self):
        """Create search/filter bar."""
        search_frame = ctk.CTkFrame(self)
        search_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        search_frame.grid_columnconfigure(1, weight=1)

        # Search label
        search_label = ctk.CTkLabel(search_frame, text="Search:")
        search_label.grid(row=0, column=0, padx=(5, 10), pady=5)

        # Search entry
        self.search_var = ctk.StringVar()
        self.search_var.trace('w', self._on_search_changed)

        self.search_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self.search_var,
            placeholder_text="Filter by artist, title, album, or genre..."
        )
        self.search_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        # Clear button
        self.clear_btn = ctk.CTkButton(
            search_frame,
            text="✕",
            width=30,
            command=self._clear_search
        )
        self.clear_btn.grid(row=0, column=2, padx=5, pady=5)

    def _create_tree_view(self):
        """Create the tree view widget."""
        # Frame for tree view with scrollbar
        tree_frame = ctk.CTkFrame(self)
        tree_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)

        # Create tree view
        columns = ('artist', 'title', 'album', 'year', 'genre', 'duration', 'format')

        self.tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show='headings',
            selectmode='extended'
        )

        # Define headings
        self.tree.heading('artist', text='Artist', command=lambda: self._sort_by('artist'))
        self.tree.heading('title', text='Title', command=lambda: self._sort_by('title'))
        self.tree.heading('album', text='Album', command=lambda: self._sort_by('album'))
        self.tree.heading('year', text='Year', command=lambda: self._sort_by('year'))
        self.tree.heading('genre', text='Genre', command=lambda: self._sort_by('genre'))
        self.tree.heading('duration', text='Duration', command=lambda: self._sort_by('duration'))
        self.tree.heading('format', text='Format', command=lambda: self._sort_by('format'))

        # Define column widths
        self.tree.column('artist', width=150)
        self.tree.column('title', width=200)
        self.tree.column('album', width=150)
        self.tree.column('year', width=60)
        self.tree.column('genre', width=100)
        self.tree.column('duration', width=80)
        self.tree.column('format', width=60)

        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Grid layout
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        # Bind selection event
        self.tree.bind('<<TreeviewSelect>>', self._on_tree_select)

        # Configure tree view style
        style = ttk.Style()
        style.theme_use('default')

        # Configure colors for dark theme
        style.configure("Treeview",
                       background="#2b2b2b",
                       foreground="white",
                       fieldbackground="#2b2b2b",
                       borderwidth=0)
        style.map('Treeview', background=[('selected', '#1f538d')])
        style.configure("Treeview.Heading",
                       background="#1f1f1f",
                       foreground="white",
                       borderwidth=1)

    def _create_buttons(self):
        """Create action buttons."""
        button_frame = ctk.CTkFrame(self)
        button_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(5, 10))
        button_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # Refresh button
        self.refresh_btn = ctk.CTkButton(
            button_frame,
            text="🔄 Refresh",
            command=self._refresh
        )
        self.refresh_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        # Select all button
        self.select_all_btn = ctk.CTkButton(
            button_frame,
            text="☑ Select All",
            command=self._select_all
        )
        self.select_all_btn.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Deselect all button
        self.deselect_btn = ctk.CTkButton(
            button_frame,
            text="☐ Deselect All",
            command=self._deselect_all
        )
        self.deselect_btn.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        # Selection count label
        self.selection_label = ctk.CTkLabel(
            button_frame,
            text="Selected: 0"
        )
        self.selection_label.grid(row=0, column=3, padx=5, pady=5)

    def load_files(self, files: List[Dict[str, Any]]):
        """
        Load files into the browser.

        Args:
            files: List of file metadata dictionaries
        """
        self.files_data = files
        self._populate_tree(files)

    def _populate_tree(self, files: List[Dict[str, Any]]):
        """
        Populate tree view with files.

        Args:
            files: List of file metadata dictionaries
        """
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Add files
        for file_data in files:
            # Format duration as MM:SS
            duration = file_data.get('duration', 0)
            minutes = int(duration // 60)
            seconds = int(duration % 60)
            duration_str = f"{minutes}:{seconds:02d}"

            values = (
                file_data.get('artist', ''),
                file_data.get('title', ''),
                file_data.get('album', ''),
                file_data.get('year', ''),
                file_data.get('genre', ''),
                duration_str,
                file_data.get('format', '').upper()
            )

            # Insert with file data stored in values
            item_id = self.tree.insert('', 'end', values=values, tags=(file_data.get('id', ''),))

        self._update_selection_label()

    def _on_search_changed(self, *args):
        """Handle search text changes."""
        search_term = self.search_var.get().lower()

        if not search_term:
            self._populate_tree(self.files_data)
            return

        # Filter files
        filtered = []
        for file_data in self.files_data:
            # Search in artist, title, album, genre
            if (search_term in file_data.get('artist', '').lower() or
                search_term in file_data.get('title', '').lower() or
                search_term in file_data.get('album', '').lower() or
                search_term in file_data.get('genre', '').lower()):
                filtered.append(file_data)

        self._populate_tree(filtered)

    def _clear_search(self):
        """Clear search field."""
        self.search_var.set('')

    def _sort_by(self, column: str):
        """
        Sort tree view by column.

        Args:
            column: Column name to sort by
        """
        # Get current items
        items = [(self.tree.set(item, column), item) for item in self.tree.get_children('')]

        # Sort items
        try:
            # Try numeric sort for year and duration
            if column in ['year', 'duration']:
                items.sort(key=lambda x: float(x[0]) if x[0] else 0)
            else:
                items.sort(key=lambda x: x[0].lower())
        except:
            items.sort(key=lambda x: str(x[0]).lower())

        # Rearrange items
        for index, (val, item) in enumerate(items):
            self.tree.move(item, '', index)

    def _on_tree_select(self, event):
        """Handle tree selection changes."""
        self._update_selection_label()

        if self.on_selection_changed:
            selected_files = self.get_selected_files()
            self.on_selection_changed(selected_files)

    def _update_selection_label(self):
        """Update the selection count label."""
        count = len(self.tree.selection())
        self.selection_label.configure(text=f"Selected: {count}")

    def _refresh(self):
        """Refresh the file list."""
        # Re-populate with current data
        self._populate_tree(self.files_data)

    def _select_all(self):
        """Select all items."""
        for item in self.tree.get_children():
            self.tree.selection_add(item)

    def _deselect_all(self):
        """Deselect all items."""
        self.tree.selection_remove(self.tree.selection())

    def get_selected_files(self) -> List[Dict[str, Any]]:
        """
        Get selected file data.

        Returns:
            list: List of selected file metadata dictionaries
        """
        selected_items = self.tree.selection()
        selected_files = []

        for item in selected_items:
            # Get the file ID from tags
            tags = self.tree.item(item, 'tags')
            if tags:
                file_id = tags[0]
                # Find the file data
                for file_data in self.files_data:
                    if str(file_data.get('id', '')) == str(file_id):
                        selected_files.append(file_data)
                        break

        return selected_files

    def clear(self):
        """Clear all files from the browser."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.files_data = []
        self._update_selection_label()

    def get_file_count(self) -> int:
        """
        Get total number of files.

        Returns:
            int: Number of files
        """
        return len(self.files_data)
