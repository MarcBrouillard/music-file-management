"""
File organization module for renaming and organizing music files.
"""

import os
import re
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import string


class FileOrganizer:
    """Organizes and renames music files based on metadata patterns."""

    # Predefined naming patterns
    PATTERNS = {
        'artist_album_track': '{artist}/{album}/{track:02d} - {title}',
        'artist_year_album_track': '{artist}/{year} - {album}/{track:02d} - {title}',
        'genre_artist_album': '{genre}/{artist}/{album}/{track:02d} - {title}',
        'artist_album': '{artist} - {album}/{track:02d} - {title}',
        'simple': '{artist} - {title}',
        'track_title': '{track:02d} - {title}',
    }

    PATTERN_NAMES = {
        'artist_album_track': 'Artist/Album/Track - Title',
        'artist_year_album_track': 'Artist/Year - Album/Track - Title',
        'genre_artist_album': 'Genre/Artist/Album/Track - Title',
        'artist_album': 'Artist - Album/Track - Title',
        'simple': 'Artist - Title',
        'track_title': 'Track - Title',
    }

    def __init__(self):
        """Initialize the file organizer."""
        self.dry_run_results = []

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename by removing invalid characters.

        Args:
            filename: Filename to sanitize

        Returns:
            str: Sanitized filename
        """
        # Remove invalid characters for filenames
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '')

        # Replace multiple spaces with single space
        filename = ' '.join(filename.split())

        # Remove leading/trailing spaces and dots
        filename = filename.strip('. ')

        return filename

    @staticmethod
    def format_path(pattern: str, metadata: Dict[str, Any], file_ext: str) -> str:
        """
        Format a file path based on pattern and metadata.

        Args:
            pattern: Naming pattern with placeholders
            metadata: File metadata dictionary
            file_ext: File extension (with dot)

        Returns:
            str: Formatted path
        """
        # Prepare metadata with defaults
        data = {
            'artist': metadata.get('artist', 'Unknown Artist'),
            'title': metadata.get('title', 'Unknown Title'),
            'album': metadata.get('album', 'Unknown Album'),
            'year': metadata.get('year', ''),
            'genre': metadata.get('genre', 'Unknown Genre'),
            'track': metadata.get('track_number', 0),
        }

        # Clean up values
        for key in data:
            if isinstance(data[key], str):
                data[key] = FileOrganizer.sanitize_filename(data[key])

        try:
            # Format the pattern
            formatted = pattern.format(**data)

            # Add file extension
            formatted += file_ext

            return formatted

        except (KeyError, ValueError) as e:
            print(f"Error formatting pattern: {e}")
            # Fallback to simple format
            return f"{data['artist']} - {data['title']}{file_ext}"

    def preview_organization(
        self,
        files: List[Dict[str, Any]],
        pattern: str,
        base_directory: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        Preview how files will be organized without moving them.

        Args:
            files: List of file metadata dictionaries
            pattern: Naming pattern to use
            base_directory: Base directory for new paths (default: same as current)

        Returns:
            list: List of dictionaries with 'old_path' and 'new_path'
        """
        preview = []

        for file_data in files:
            old_path = file_data.get('file_path', '')
            if not old_path or not os.path.exists(old_path):
                continue

            # Get file extension
            file_ext = Path(old_path).suffix

            # Determine base directory
            if base_directory is None:
                base_dir = Path(old_path).parent
            else:
                base_dir = Path(base_directory)

            # Format new relative path
            new_relative_path = self.format_path(pattern, file_data, file_ext)

            # Create full new path
            new_path = str(base_dir / new_relative_path)

            # Check if paths are different
            if os.path.normpath(old_path) != os.path.normpath(new_path):
                preview.append({
                    'id': file_data.get('id'),
                    'old_path': old_path,
                    'new_path': new_path,
                    'old_name': Path(old_path).name,
                    'new_name': Path(new_path).name,
                    'old_dir': str(Path(old_path).parent),
                    'new_dir': str(Path(new_path).parent),
                    'status': 'pending'
                })

        return preview

    def organize_files(
        self,
        preview_items: List[Dict[str, str]],
        dry_run: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Organize files according to preview.

        Args:
            preview_items: List of preview dictionaries from preview_organization
            dry_run: If True, don't actually move files

        Returns:
            list: Results with status for each file
        """
        results = []

        for item in preview_items:
            old_path = item['old_path']
            new_path = item['new_path']

            result = {
                'id': item.get('id'),
                'old_path': old_path,
                'new_path': new_path,
                'status': 'pending',
                'error': None
            }

            try:
                # Check if source exists
                if not os.path.exists(old_path):
                    result['status'] = 'error'
                    result['error'] = 'Source file not found'
                    results.append(result)
                    continue

                # Check if destination already exists
                if os.path.exists(new_path) and os.path.normpath(old_path) != os.path.normpath(new_path):
                    result['status'] = 'error'
                    result['error'] = 'Destination already exists'
                    results.append(result)
                    continue

                # Skip if paths are the same
                if os.path.normpath(old_path) == os.path.normpath(new_path):
                    result['status'] = 'skipped'
                    result['error'] = 'Source and destination are the same'
                    results.append(result)
                    continue

                if not dry_run:
                    # Create destination directory
                    new_dir = Path(new_path).parent
                    new_dir.mkdir(parents=True, exist_ok=True)

                    # Move the file
                    shutil.move(old_path, new_path)

                result['status'] = 'success' if not dry_run else 'dry_run_ok'

            except Exception as e:
                result['status'] = 'error'
                result['error'] = str(e)

            results.append(result)

        return results

    def rename_file(
        self,
        file_path: str,
        new_name: str,
        keep_extension: bool = True
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Rename a single file.

        Args:
            file_path: Current file path
            new_name: New filename
            keep_extension: Whether to keep the original extension

        Returns:
            tuple: (success, new_path, error_message)
        """
        try:
            old_path = Path(file_path)

            if not old_path.exists():
                return False, None, "File not found"

            # Get extension if needed
            if keep_extension:
                ext = old_path.suffix
                if not new_name.endswith(ext):
                    new_name += ext

            # Sanitize new name
            new_name = self.sanitize_filename(new_name)

            # Create new path
            new_path = old_path.parent / new_name

            # Check if already exists
            if new_path.exists() and new_path != old_path:
                return False, None, "File with that name already exists"

            # Rename
            old_path.rename(new_path)

            return True, str(new_path), None

        except Exception as e:
            return False, None, str(e)

    def batch_rename(
        self,
        files: List[Dict[str, Any]],
        find_text: str,
        replace_text: str,
        field: str = 'filename'
    ) -> List[Dict[str, Any]]:
        """
        Batch rename files by finding and replacing text.

        Args:
            files: List of file metadata dictionaries
            find_text: Text to find
            replace_text: Text to replace with
            field: Which field to use ('filename', 'artist', 'title', 'album')

        Returns:
            list: Results for each file
        """
        results = []

        for file_data in files:
            file_path = file_data.get('file_path', '')

            if not file_path or not os.path.exists(file_path):
                results.append({
                    'id': file_data.get('id'),
                    'status': 'error',
                    'error': 'File not found'
                })
                continue

            # Get current name based on field
            if field == 'filename':
                old_name = Path(file_path).stem
            else:
                old_name = file_data.get(field, '')

            # Replace text
            new_name = old_name.replace(find_text, replace_text)

            if new_name == old_name:
                results.append({
                    'id': file_data.get('id'),
                    'old_path': file_path,
                    'new_path': file_path,
                    'status': 'skipped',
                    'error': 'No changes needed'
                })
                continue

            # Rename
            success, new_path, error = self.rename_file(
                file_path,
                new_name,
                keep_extension=True
            )

            results.append({
                'id': file_data.get('id'),
                'old_path': file_path,
                'new_path': new_path or file_path,
                'status': 'success' if success else 'error',
                'error': error
            })

        return results

    @staticmethod
    def get_pattern_list() -> List[Tuple[str, str]]:
        """
        Get list of available patterns.

        Returns:
            list: List of (pattern_key, pattern_name) tuples
        """
        return [(key, FileOrganizer.PATTERN_NAMES[key])
                for key in FileOrganizer.PATTERNS.keys()]

    @staticmethod
    def get_pattern(pattern_key: str) -> Optional[str]:
        """
        Get pattern string by key.

        Args:
            pattern_key: Pattern key

        Returns:
            str: Pattern string or None
        """
        return FileOrganizer.PATTERNS.get(pattern_key)

    def validate_pattern(self, pattern: str) -> Tuple[bool, Optional[str]]:
        """
        Validate a custom pattern.

        Args:
            pattern: Pattern string to validate

        Returns:
            tuple: (is_valid, error_message)
        """
        try:
            # Test format with sample data
            sample_data = {
                'artist': 'Test Artist',
                'title': 'Test Title',
                'album': 'Test Album',
                'year': 2024,
                'genre': 'Test Genre',
                'track': 1
            }

            formatted = pattern.format(**sample_data)
            return True, None

        except (KeyError, ValueError) as e:
            return False, str(e)
