"""
JSON export/import utility for music library metadata.
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime


class JSONExporter:
    """Handles exporting and importing music library data to/from JSON."""

    def __init__(self):
        """Initialize the JSON exporter."""
        pass

    @staticmethod
    def export_to_json(
        files: List[Dict[str, Any]],
        output_path: str,
        pretty: bool = True,
        include_metadata: bool = True
    ) -> Tuple[bool, Optional[str]]:
        """
        Export music files data to JSON.

        Args:
            files: List of file metadata dictionaries
            output_path: Path to output JSON file
            pretty: Whether to format JSON for readability
            include_metadata: Whether to include library metadata

        Returns:
            tuple: (success, error_message)
        """
        try:
            # Prepare export data
            export_data = {
                'metadata': {
                    'export_date': datetime.now().isoformat(),
                    'total_files': len(files),
                    'version': '1.0'
                } if include_metadata else {},
                'files': files
            }

            # Ensure output directory exists
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)

            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                if pretty:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
                else:
                    json.dump(export_data, f, ensure_ascii=False)

            return True, None

        except Exception as e:
            return False, str(e)

    @staticmethod
    def import_from_json(
        input_path: str
    ) -> Tuple[bool, Optional[List[Dict[str, Any]]], Optional[str]]:
        """
        Import music files data from JSON.

        Args:
            input_path: Path to input JSON file

        Returns:
            tuple: (success, files_data, error_message)
        """
        try:
            if not os.path.exists(input_path):
                return False, None, "File not found"

            with open(input_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Extract files data
            if isinstance(data, dict) and 'files' in data:
                files = data['files']
            elif isinstance(data, list):
                files = data
            else:
                return False, None, "Invalid JSON format"

            return True, files, None

        except json.JSONDecodeError as e:
            return False, None, f"JSON decode error: {str(e)}"
        except Exception as e:
            return False, None, str(e)

    @staticmethod
    def export_playlist(
        files: List[Dict[str, Any]],
        output_path: str,
        playlist_name: str = "My Playlist"
    ) -> Tuple[bool, Optional[str]]:
        """
        Export files as a playlist (M3U format).

        Args:
            files: List of file metadata dictionaries
            output_path: Path to output M3U file
            playlist_name: Name of the playlist

        Returns:
            tuple: (success, error_message)
        """
        try:
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w', encoding='utf-8') as f:
                # Write M3U header
                f.write('#EXTM3U\n')
                f.write(f'#PLAYLIST:{playlist_name}\n\n')

                # Write each file
                for file_data in files:
                    duration = int(file_data.get('duration', 0))
                    artist = file_data.get('artist', 'Unknown')
                    title = file_data.get('title', 'Unknown')
                    path = file_data.get('file_path', '')

                    # Write extended info
                    f.write(f'#EXTINF:{duration},{artist} - {title}\n')

                    # Write file path
                    f.write(f'{path}\n')

            return True, None

        except Exception as e:
            return False, str(e)

    @staticmethod
    def export_csv(
        files: List[Dict[str, Any]],
        output_path: str,
        fields: Optional[List[str]] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Export files data to CSV format.

        Args:
            files: List of file metadata dictionaries
            output_path: Path to output CSV file
            fields: List of fields to export (default: all)

        Returns:
            tuple: (success, error_message)
        """
        try:
            import csv

            if not files:
                return False, "No files to export"

            # Default fields
            if fields is None:
                fields = [
                    'file_path', 'filename', 'artist', 'title', 'album',
                    'year', 'genre', 'track_number', 'duration', 'bitrate',
                    'format', 'file_size'
                ]

            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')

                # Write header
                writer.writeheader()

                # Write rows
                for file_data in files:
                    # Only include specified fields
                    row = {field: file_data.get(field, '') for field in fields}
                    writer.writerow(row)

            return True, None

        except Exception as e:
            return False, str(e)

    @staticmethod
    def create_backup(
        files: List[Dict[str, Any]],
        backup_dir: str
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Create a timestamped backup of library data.

        Args:
            files: List of file metadata dictionaries
            backup_dir: Directory to store backups

        Returns:
            tuple: (success, backup_path, error_message)
        """
        try:
            # Create backup directory
            backup_path = Path(backup_dir)
            backup_path.mkdir(parents=True, exist_ok=True)

            # Create timestamped filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'music_library_backup_{timestamp}.json'
            full_path = backup_path / filename

            # Export to JSON
            success, error = JSONExporter.export_to_json(
                files,
                str(full_path),
                pretty=True,
                include_metadata=True
            )

            if success:
                return True, str(full_path), None
            else:
                return False, None, error

        except Exception as e:
            return False, None, str(e)

    @staticmethod
    def list_backups(backup_dir: str) -> List[Dict[str, Any]]:
        """
        List available backups.

        Args:
            backup_dir: Directory containing backups

        Returns:
            list: List of backup info dictionaries
        """
        try:
            backup_path = Path(backup_dir)

            if not backup_path.exists():
                return []

            backups = []

            for file_path in backup_path.glob('music_library_backup_*.json'):
                stat = file_path.stat()

                backups.append({
                    'path': str(file_path),
                    'filename': file_path.name,
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime),
                    'created': datetime.fromtimestamp(stat.st_ctime)
                })

            # Sort by modified date (newest first)
            backups.sort(key=lambda x: x['modified'], reverse=True)

            return backups

        except Exception as e:
            print(f"Error listing backups: {e}")
            return []

    @staticmethod
    def restore_from_backup(
        backup_path: str
    ) -> Tuple[bool, Optional[List[Dict[str, Any]]], Optional[str]]:
        """
        Restore library data from a backup.

        Args:
            backup_path: Path to backup file

        Returns:
            tuple: (success, files_data, error_message)
        """
        return JSONExporter.import_from_json(backup_path)

    @staticmethod
    def cleanup_old_backups(
        backup_dir: str,
        keep_count: int = 10
    ) -> Tuple[bool, int, Optional[str]]:
        """
        Clean up old backups, keeping only the most recent ones.

        Args:
            backup_dir: Directory containing backups
            keep_count: Number of recent backups to keep

        Returns:
            tuple: (success, deleted_count, error_message)
        """
        try:
            backups = JSONExporter.list_backups(backup_dir)

            if len(backups) <= keep_count:
                return True, 0, None

            # Delete old backups
            deleted_count = 0

            for backup in backups[keep_count:]:
                try:
                    os.remove(backup['path'])
                    deleted_count += 1
                except Exception as e:
                    print(f"Error deleting {backup['path']}: {e}")

            return True, deleted_count, None

        except Exception as e:
            return False, 0, str(e)

    @staticmethod
    def validate_json_file(file_path: str) -> Tuple[bool, Optional[str]]:
        """
        Validate a JSON file.

        Args:
            file_path: Path to JSON file

        Returns:
            tuple: (is_valid, error_message)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                json.load(f)

            return True, None

        except json.JSONDecodeError as e:
            return False, f"Invalid JSON: {str(e)}"
        except Exception as e:
            return False, str(e)
