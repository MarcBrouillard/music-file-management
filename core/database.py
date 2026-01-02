"""
Database management module using SQLite.
Handles storage and retrieval of music file metadata.
"""

import sqlite3
import os
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime


class MusicDatabase:
    """SQLite database manager for music library."""

    def __init__(self, db_path: str = None):
        """
        Initialize the database connection.

        Args:
            db_path: Path to the SQLite database file
        """
        if db_path is None:
            # Default to user's home directory
            db_dir = Path.home() / '.music_manager'
            db_dir.mkdir(parents=True, exist_ok=True)
            db_path = db_dir / 'library.db'

        self.db_path = str(db_path)
        self.conn = None
        self._connect()
        self._create_tables()

    def _connect(self):
        """Establish database connection."""
        try:
            # Allow connection to be used across threads
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row  # Enable column access by name
        except Exception as e:
            print(f"Error connecting to database: {e}")
            raise

    def _create_tables(self):
        """Create database tables if they don't exist."""
        try:
            cursor = self.conn.cursor()

            # Music files table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS music_files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT UNIQUE NOT NULL,
                    filename TEXT NOT NULL,
                    file_size INTEGER,
                    file_hash TEXT,
                    format TEXT,
                    artist TEXT,
                    title TEXT,
                    album TEXT,
                    year INTEGER,
                    genre TEXT,
                    track_number INTEGER,
                    duration REAL,
                    bitrate INTEGER,
                    sample_rate INTEGER,
                    channels INTEGER,
                    has_artwork INTEGER DEFAULT 0,
                    audio_fingerprint TEXT,
                    date_added DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_modified DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Duplicate groups table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS duplicate_groups (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    detection_method TEXT NOT NULL,
                    created_date DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Duplicate files junction table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS duplicate_files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    group_id INTEGER NOT NULL,
                    file_id INTEGER NOT NULL,
                    FOREIGN KEY (group_id) REFERENCES duplicate_groups(id) ON DELETE CASCADE,
                    FOREIGN KEY (file_id) REFERENCES music_files(id) ON DELETE CASCADE,
                    UNIQUE(group_id, file_id)
                )
            ''')

            # Create indexes for faster queries
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_artist ON music_files(artist)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_album ON music_files(album)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_file_hash ON music_files(file_hash)
            ''')

            self.conn.commit()

        except Exception as e:
            print(f"Error creating tables: {e}")
            raise

    def add_file(self, metadata: Dict[str, Any]) -> Optional[int]:
        """
        Add a music file to the database.

        Args:
            metadata: Dictionary containing file metadata

        Returns:
            int: ID of the inserted record, or None if error
        """
        try:
            cursor = self.conn.cursor()

            cursor.execute('''
                INSERT OR REPLACE INTO music_files (
                    file_path, filename, file_size, file_hash, format,
                    artist, title, album, year, genre, track_number,
                    duration, bitrate, sample_rate, channels, has_artwork,
                    last_modified
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metadata.get('file_path'),
                metadata.get('filename'),
                metadata.get('file_size'),
                metadata.get('file_hash'),
                metadata.get('format'),
                metadata.get('artist', ''),
                metadata.get('title', ''),
                metadata.get('album', ''),
                metadata.get('year'),
                metadata.get('genre', ''),
                metadata.get('track_number'),
                metadata.get('duration', 0.0),
                metadata.get('bitrate', 0),
                metadata.get('sample_rate', 0),
                metadata.get('channels', 0),
                int(metadata.get('has_artwork', False)),
                datetime.now()
            ))

            self.conn.commit()
            return cursor.lastrowid

        except Exception as e:
            print(f"Error adding file to database: {e}")
            self.conn.rollback()
            return None

    def add_files_batch(
        self,
        metadata_list: List[Dict[str, Any]],
        batch_size: Optional[int] = None,
        min_batch: int = 100,
        max_batch: int = 1000
    ) -> int:
        """
        Add multiple files to the database in batches with incremental commits.

        Args:
            metadata_list: List of metadata dictionaries
            batch_size: Fixed batch size (overrides min/max if provided)
            min_batch: Minimum records per commit
            max_batch: Maximum records per commit

        Returns:
            int: Number of files successfully added
        """
        count = 0
        total_files = len(metadata_list)

        try:
            cursor = self.conn.cursor()

            # Calculate optimal batch size if not provided
            if batch_size is None:
                # Commit every 1% with min/max constraints
                batch_size = min(max_batch, max(min_batch, total_files // 100))

            # Process in batches
            for i, metadata in enumerate(metadata_list):
                try:
                    cursor.execute('''
                        INSERT OR REPLACE INTO music_files (
                            file_path, filename, file_size, file_hash, format,
                            artist, title, album, year, genre, track_number,
                            duration, bitrate, sample_rate, channels, has_artwork,
                            last_modified
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        metadata.get('file_path'),
                        metadata.get('filename'),
                        metadata.get('file_size'),
                        metadata.get('file_hash'),
                        metadata.get('format'),
                        metadata.get('artist', ''),
                        metadata.get('title', ''),
                        metadata.get('album', ''),
                        metadata.get('year'),
                        metadata.get('genre', ''),
                        metadata.get('track_number'),
                        metadata.get('duration', 0.0),
                        metadata.get('bitrate', 0),
                        metadata.get('sample_rate', 0),
                        metadata.get('channels', 0),
                        int(metadata.get('has_artwork', False)),
                        datetime.now()
                    ))
                    count += 1

                    # Commit every batch_size records
                    if (i + 1) % batch_size == 0:
                        self.conn.commit()
                        print(f"Committed batch: {count}/{total_files} files")

                except Exception as e:
                    print(f"Error adding file {metadata.get('file_path')}: {e}")
                    continue

            # Final commit for any remaining records
            self.conn.commit()
            print(f"Final commit: {count}/{total_files} files total")

        except Exception as e:
            print(f"Error in batch insert: {e}")
            self.conn.rollback()

        return count

    def get_file(self, file_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a file by its ID.

        Args:
            file_id: Database ID of the file

        Returns:
            dict: File metadata or None if not found
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM music_files WHERE id = ?', (file_id,))
            row = cursor.fetchone()

            if row:
                return dict(row)
            return None

        except Exception as e:
            print(f"Error getting file: {e}")
            return None

    def get_file_by_path(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Get a file by its file path.

        Args:
            file_path: Path to the file

        Returns:
            dict: File metadata or None if not found
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM music_files WHERE file_path = ?', (file_path,))
            row = cursor.fetchone()

            if row:
                return dict(row)
            return None

        except Exception as e:
            print(f"Error getting file by path: {e}")
            return None

    def get_all_files(self, limit: int = None, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get all files from the database.

        Args:
            limit: Maximum number of records to return
            offset: Number of records to skip

        Returns:
            list: List of file metadata dictionaries
        """
        try:
            cursor = self.conn.cursor()

            query = 'SELECT * FROM music_files ORDER BY artist, album, track_number'
            if limit:
                query += f' LIMIT {limit} OFFSET {offset}'

            cursor.execute(query)
            rows = cursor.fetchall()

            return [dict(row) for row in rows]

        except Exception as e:
            print(f"Error getting all files: {e}")
            return []

    def search_files(self, search_term: str, fields: List[str] = None) -> List[Dict[str, Any]]:
        """
        Search for files matching a search term.

        Args:
            search_term: Text to search for
            fields: List of fields to search in (default: artist, title, album, genre)

        Returns:
            list: List of matching file metadata dictionaries
        """
        if fields is None:
            fields = ['artist', 'title', 'album', 'genre']

        try:
            cursor = self.conn.cursor()

            # Build WHERE clause
            conditions = ' OR '.join([f"{field} LIKE ?" for field in fields])
            query = f'SELECT * FROM music_files WHERE {conditions} ORDER BY artist, album, track_number'

            # Execute with search term for each field
            params = [f'%{search_term}%'] * len(fields)
            cursor.execute(query, params)

            rows = cursor.fetchall()
            return [dict(row) for row in rows]

        except Exception as e:
            print(f"Error searching files: {e}")
            return []

    def update_file(self, file_id: int, metadata: Dict[str, Any]) -> bool:
        """
        Update a file's metadata.

        Args:
            file_id: Database ID of the file
            metadata: Dictionary of fields to update

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            cursor = self.conn.cursor()

            # Build UPDATE query dynamically
            fields = []
            values = []

            for key, value in metadata.items():
                if key not in ['id', 'date_added']:  # Skip these fields
                    fields.append(f"{key} = ?")
                    values.append(value)

            if not fields:
                return False

            # Add last_modified timestamp
            fields.append("last_modified = ?")
            values.append(datetime.now())
            values.append(file_id)

            query = f"UPDATE music_files SET {', '.join(fields)} WHERE id = ?"
            cursor.execute(query, values)

            self.conn.commit()
            return cursor.rowcount > 0

        except Exception as e:
            print(f"Error updating file: {e}")
            self.conn.rollback()
            return False

    def delete_file(self, file_id: int) -> bool:
        """
        Delete a file from the database.

        Args:
            file_id: Database ID of the file

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM music_files WHERE id = ?', (file_id,))
            self.conn.commit()
            return cursor.rowcount > 0

        except Exception as e:
            print(f"Error deleting file: {e}")
            self.conn.rollback()
            return False

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get library statistics.

        Returns:
            dict: Statistics about the music library
        """
        try:
            cursor = self.conn.cursor()

            stats = {}

            # Total files
            cursor.execute('SELECT COUNT(*) FROM music_files')
            stats['total_files'] = cursor.fetchone()[0]

            # Total artists
            cursor.execute('SELECT COUNT(DISTINCT artist) FROM music_files WHERE artist != ""')
            stats['total_artists'] = cursor.fetchone()[0]

            # Total albums
            cursor.execute('SELECT COUNT(DISTINCT album) FROM music_files WHERE album != ""')
            stats['total_albums'] = cursor.fetchone()[0]

            # Total duration
            cursor.execute('SELECT SUM(duration) FROM music_files')
            stats['total_duration'] = cursor.fetchone()[0] or 0

            # Total size
            cursor.execute('SELECT SUM(file_size) FROM music_files')
            stats['total_size'] = cursor.fetchone()[0] or 0

            return stats

        except Exception as e:
            print(f"Error getting statistics: {e}")
            return {}

    def create_duplicate_group(self, detection_method: str) -> Optional[int]:
        """
        Create a new duplicate group.

        Args:
            detection_method: Method used to detect duplicates

        Returns:
            int: Group ID or None if error
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO duplicate_groups (detection_method)
                VALUES (?)
            ''', (detection_method,))
            self.conn.commit()
            return cursor.lastrowid

        except Exception as e:
            print(f"Error creating duplicate group: {e}")
            return None

    def add_to_duplicate_group(self, group_id: int, file_ids: List[int]) -> bool:
        """
        Add files to a duplicate group.

        Args:
            group_id: Duplicate group ID
            file_ids: List of file IDs to add

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            cursor = self.conn.cursor()

            for file_id in file_ids:
                cursor.execute('''
                    INSERT OR IGNORE INTO duplicate_files (group_id, file_id)
                    VALUES (?, ?)
                ''', (group_id, file_id))

            self.conn.commit()
            return True

        except Exception as e:
            print(f"Error adding to duplicate group: {e}")
            self.conn.rollback()
            return False

    def get_duplicate_groups(self) -> List[Dict[str, Any]]:
        """
        Get all duplicate groups with their files.

        Returns:
            list: List of duplicate groups with file information
        """
        try:
            cursor = self.conn.cursor()

            cursor.execute('''
                SELECT dg.id, dg.detection_method, dg.created_date,
                       GROUP_CONCAT(mf.id) as file_ids,
                       GROUP_CONCAT(mf.file_path, '|') as file_paths
                FROM duplicate_groups dg
                JOIN duplicate_files df ON dg.id = df.group_id
                JOIN music_files mf ON df.file_id = mf.id
                GROUP BY dg.id
            ''')

            rows = cursor.fetchall()
            groups = []

            for row in rows:
                group = dict(row)
                group['file_ids'] = [int(id) for id in group['file_ids'].split(',')]
                group['file_paths'] = group['file_paths'].split('|')
                groups.append(group)

            return groups

        except Exception as e:
            print(f"Error getting duplicate groups: {e}")
            return []

    def clear_duplicate_groups(self) -> bool:
        """
        Clear all duplicate groups.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM duplicate_files')
            cursor.execute('DELETE FROM duplicate_groups')
            self.conn.commit()
            return True

        except Exception as e:
            print(f"Error clearing duplicate groups: {e}")
            self.conn.rollback()
            return False

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
