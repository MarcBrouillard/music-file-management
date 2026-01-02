"""
Duplicate finder panel for detecting and managing duplicate files.
"""

import customtkinter as ctk
from tkinter import ttk
from typing import List, Dict, Any, Optional, Callable
from pathlib import Path


class DuplicatePanel(ctk.CTkFrame):
    """Panel for finding and managing duplicate music files."""

    def __init__(self, parent, on_find: Optional[Callable] = None, on_action: Optional[Callable] = None):
        """
        Initialize the duplicate panel.

        Args:
            parent: Parent widget
            on_find: Callback when find duplicates is clicked
            on_action: Callback when action is performed on duplicates
        """
        super().__init__(parent)

        self.on_find = on_find
        self.on_action = on_action
        self.duplicate_groups = []
        self.selected_for_removal = set()

        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Create UI components
        self._create_title()
        self._create_options()
        self._create_results_area()
        self._create_buttons()

    def _create_title(self):
        """Create title section."""
        title_frame = ctk.CTkFrame(self)
        title_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        title_label = ctk.CTkLabel(
            title_frame,
            text="Duplicate File Finder",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=5)

        info_label = ctk.CTkLabel(
            title_frame,
            text="Find and remove duplicate music files to save space",
            font=ctk.CTkFont(size=12)
        )
        info_label.pack(pady=2)

    def _create_options(self):
        """Create detection options."""
        options_frame = ctk.CTkFrame(self)
        options_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        options_frame.grid_columnconfigure(1, weight=1)

        # Detection method
        method_label = ctk.CTkLabel(options_frame, text="Detection Method:")
        method_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)

        self.method_var = ctk.StringVar(value="Metadata")

        method_options = ["Metadata", "File Hash", "Size & Duration", "Combined"]

        self.method_dropdown = ctk.CTkOptionMenu(
            options_frame,
            variable=self.method_var,
            values=method_options
        )
        self.method_dropdown.grid(row=0, column=1, sticky="w", padx=10, pady=5)

        # Tolerance slider (for metadata comparison)
        tolerance_label = ctk.CTkLabel(options_frame, text="Match Tolerance:")
        tolerance_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)

        self.tolerance_var = ctk.DoubleVar(value=0.9)

        self.tolerance_slider = ctk.CTkSlider(
            options_frame,
            from_=0.5,
            to=1.0,
            variable=self.tolerance_var,
            number_of_steps=50
        )
        self.tolerance_slider.grid(row=1, column=1, sticky="ew", padx=10, pady=5)

        self.tolerance_value_label = ctk.CTkLabel(
            options_frame,
            text="90%"
        )
        self.tolerance_value_label.grid(row=1, column=2, padx=10, pady=5)

        self.tolerance_var.trace('w', self._update_tolerance_label)

        # Find button
        self.find_btn = ctk.CTkButton(
            options_frame,
            text="🔍 Find Duplicates",
            command=self._find_duplicates,
            width=150
        )
        self.find_btn.grid(row=0, column=2, rowspan=2, padx=10, pady=5)

    def _create_results_area(self):
        """Create results tree view."""
        results_frame = ctk.CTkFrame(self)
        results_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        results_frame.grid_columnconfigure(0, weight=1)
        results_frame.grid_rowconfigure(1, weight=1)

        # Label
        label_frame = ctk.CTkFrame(results_frame)
        label_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        label_frame.grid_columnconfigure(1, weight=1)

        label = ctk.CTkLabel(
            label_frame,
            text="Duplicate Groups",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        label.grid(row=0, column=0, sticky="w", padx=5, pady=5)

        self.stats_label = ctk.CTkLabel(
            label_frame,
            text="No duplicates found",
            font=ctk.CTkFont(size=11)
        )
        self.stats_label.grid(row=0, column=1, sticky="e", padx=5, pady=5)

        # Tree view frame
        tree_frame = ctk.CTkFrame(results_frame)
        tree_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)

        # Create tree view
        columns = ('filename', 'artist', 'title', 'bitrate', 'size', 'path')

        self.results_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show='tree headings',
            selectmode='extended'
        )

        # Define headings
        self.results_tree.heading('#0', text='Group')
        self.results_tree.heading('filename', text='Filename')
        self.results_tree.heading('artist', text='Artist')
        self.results_tree.heading('title', text='Title')
        self.results_tree.heading('bitrate', text='Bitrate')
        self.results_tree.heading('size', text='Size')
        self.results_tree.heading('path', text='Path')

        # Define column widths
        self.results_tree.column('#0', width=100)
        self.results_tree.column('filename', width=180)
        self.results_tree.column('artist', width=120)
        self.results_tree.column('title', width=120)
        self.results_tree.column('bitrate', width=80)
        self.results_tree.column('size', width=80)
        self.results_tree.column('path', width=200)

        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.results_tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.results_tree.xview)
        self.results_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Grid layout
        self.results_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        # Configure style
        style = ttk.Style()
        style.configure("Treeview",
                       background="#2b2b2b",
                       foreground="white",
                       fieldbackground="#2b2b2b")
        style.map('Treeview', background=[('selected', '#1f538d')])

        # Bind events
        self.results_tree.bind('<Button-3>', self._show_context_menu)

    def _create_buttons(self):
        """Create action buttons."""
        button_frame = ctk.CTkFrame(self)
        button_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=10)
        button_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # Auto-select lower quality button
        self.auto_select_btn = ctk.CTkButton(
            button_frame,
            text="🎯 Auto-Select Lower Quality",
            command=self._auto_select_lower_quality,
            fg_color="orange",
            hover_color="darkorange"
        )
        self.auto_select_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        # Keep selected button
        self.keep_btn = ctk.CTkButton(
            button_frame,
            text="✓ Keep Selected",
            command=self._keep_selected,
            fg_color="green",
            hover_color="darkgreen"
        )
        self.keep_btn.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Remove selected button
        self.remove_btn = ctk.CTkButton(
            button_frame,
            text="🗑️ Remove Selected",
            command=self._remove_selected,
            fg_color="red",
            hover_color="darkred"
        )
        self.remove_btn.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        # Clear results button
        self.clear_btn = ctk.CTkButton(
            button_frame,
            text="✕ Clear Results",
            command=self._clear_results,
            fg_color="gray",
            hover_color="darkgray"
        )
        self.clear_btn.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

    def _update_tolerance_label(self, *args):
        """Update tolerance percentage label."""
        value = int(self.tolerance_var.get() * 100)
        self.tolerance_value_label.configure(text=f"{value}%")

    def _find_duplicates(self):
        """Trigger duplicate finding."""
        if self.on_find:
            method = self.method_var.get()
            tolerance = self.tolerance_var.get()

            self.duplicate_groups = self.on_find(method, tolerance)
            self._display_results(self.duplicate_groups)

    def _display_results(self, duplicate_groups: List[List[Dict[str, Any]]]):
        """
        Display duplicate groups in tree view.

        Args:
            duplicate_groups: List of duplicate groups
        """
        # Clear existing items
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)

        self.selected_for_removal.clear()

        if not duplicate_groups:
            self.stats_label.configure(text="No duplicates found")
            return

        # Calculate statistics
        total_duplicates = sum(len(group) for group in duplicate_groups)
        wasted_space = 0

        for group_idx, group in enumerate(duplicate_groups, 1):
            # Calculate wasted space (keep largest, rest is wasted)
            sorted_group = sorted(group, key=lambda f: f.get('file_size', 0), reverse=True)
            group_wasted = sum(f.get('file_size', 0) for f in sorted_group[1:])
            wasted_space += group_wasted

            # Add group node
            group_node = self.results_tree.insert(
                '',
                'end',
                text=f"Group {group_idx} ({len(group)} files)",
                open=True
            )

            # Add files in group
            for file_data in group:
                filename = Path(file_data.get('file_path', '')).name
                artist = file_data.get('artist', '')
                title = file_data.get('title', '')
                bitrate = f"{file_data.get('bitrate', 0) // 1000} kbps" if file_data.get('bitrate') else '-'
                size_mb = file_data.get('file_size', 0) / (1024 * 1024)
                size = f"{size_mb:.2f} MB"
                path = file_data.get('file_path', '')

                values = (filename, artist, title, bitrate, size, path)

                self.results_tree.insert(
                    group_node,
                    'end',
                    text='',
                    values=values,
                    tags=(str(file_data.get('id')),)
                )

        # Update statistics
        wasted_mb = wasted_space / (1024 * 1024)
        self.stats_label.configure(
            text=f"{len(duplicate_groups)} groups, {total_duplicates} files, {wasted_mb:.2f} MB wasted space"
        )

    def _auto_select_lower_quality(self):
        """Automatically select lower quality files for removal."""
        # Iterate through groups
        for group_item in self.results_tree.get_children():
            files = self.results_tree.get_children(group_item)

            if not files:
                continue

            # Get file data and sort by quality
            file_items = []

            for file_item in files:
                values = self.results_tree.item(file_item, 'values')
                # Extract bitrate from string like "320 kbps"
                bitrate_str = values[3]  # bitrate column
                try:
                    bitrate = int(bitrate_str.split()[0]) if bitrate_str != '-' else 0
                except:
                    bitrate = 0

                # Extract size from string like "5.23 MB"
                size_str = values[4]  # size column
                try:
                    size = float(size_str.split()[0])
                except:
                    size = 0

                file_items.append((file_item, bitrate, size))

            # Sort by bitrate, then size (highest first)
            file_items.sort(key=lambda x: (x[1], x[2]), reverse=True)

            # Keep the best quality, select others for removal
            for file_item, _, _ in file_items[1:]:
                # Mark as selected for removal (visual indication could be added)
                self.results_tree.selection_add(file_item)

        self._update_selection_status()

    def _keep_selected(self):
        """Mark selected files to keep."""
        # Deselect the selected items
        self.results_tree.selection_remove(self.results_tree.selection())

    def _remove_selected(self):
        """Remove selected duplicate files."""
        selected_items = self.results_tree.selection()

        if not selected_items:
            return

        # Get file IDs to remove
        files_to_remove = []

        for item in selected_items:
            # Skip group items, only get file items
            if not self.results_tree.parent(item):
                continue

            tags = self.results_tree.item(item, 'tags')
            if tags:
                file_id = int(tags[0])
                values = self.results_tree.item(item, 'values')
                path = values[5]  # path column

                files_to_remove.append({
                    'id': file_id,
                    'path': path
                })

        if files_to_remove and self.on_action:
            success = self.on_action('remove', files_to_remove)

            if success:
                # Remove from tree
                for item in selected_items:
                    if self.results_tree.parent(item):
                        self.results_tree.delete(item)

                # Refresh to find duplicates again
                self._find_duplicates()

    def _show_context_menu(self, event):
        """Show context menu on right-click."""
        # TODO: Implement context menu
        pass

    def _update_selection_status(self):
        """Update status based on selection."""
        selected_count = len(self.results_tree.selection())

        if selected_count > 0:
            self.stats_label.configure(
                text=f"{selected_count} files selected for removal"
            )

    def _clear_results(self):
        """Clear all results."""
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)

        self.duplicate_groups = []
        self.stats_label.configure(text="No duplicates found")

    def load_files(self, files: List[Dict[str, Any]]):
        """
        Load files for duplicate detection.

        Args:
            files: List of file metadata dictionaries
        """
        # Clear previous results
        self._clear_results()
