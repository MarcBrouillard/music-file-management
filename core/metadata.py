"""
Metadata reading and writing module using Mutagen.
Supports MP3, FLAC, M4A, OGG, WAV formats.
"""

import os
from pathlib import Path
from typing import Dict, Optional, Any
from mutagen import File as MutagenFile
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB, TDRC, TCON, TRCK
from mutagen.flac import FLAC, Picture
from mutagen.mp4 import MP4, MP4Cover
import hashlib


class MetadataHandler:
    """Handler for reading and writing music file metadata."""

    SUPPORTED_FORMATS = {'.mp3', '.flac', '.m4a', '.mp4', '.ogg', '.wav'}

    def __init__(self):
        """Initialize the metadata handler."""
        pass

    @staticmethod
    def is_supported(file_path: str) -> bool:
        """
        Check if the file format is supported.

        Args:
            file_path: Path to the audio file

        Returns:
            bool: True if format is supported
        """
        ext = Path(file_path).suffix.lower()
        return ext in MetadataHandler.SUPPORTED_FORMATS

    @staticmethod
    def read_metadata(file_path: str) -> Optional[Dict[str, Any]]:
        """
        Read metadata from an audio file.

        Args:
            file_path: Path to the audio file

        Returns:
            dict: Metadata dictionary or None if error
        """
        if not os.path.exists(file_path):
            return None

        if not MetadataHandler.is_supported(file_path):
            return None

        try:
            audio = MutagenFile(file_path)
            if audio is None:
                return None

            metadata = {
                'file_path': file_path,
                'filename': Path(file_path).name,
                'file_size': os.path.getsize(file_path),
                'file_hash': MetadataHandler.calculate_file_hash(file_path),
                'format': Path(file_path).suffix.lower()[1:],
                'artist': '',
                'title': '',
                'album': '',
                'year': None,
                'genre': '',
                'track_number': None,
                'duration': 0.0,
                'bitrate': 0,
                'sample_rate': 0,
                'channels': 0,
                'has_artwork': False
            }

            # Get duration
            if hasattr(audio.info, 'length'):
                metadata['duration'] = round(audio.info.length, 2)

            # Get bitrate
            if hasattr(audio.info, 'bitrate'):
                metadata['bitrate'] = audio.info.bitrate

            # Get sample rate
            if hasattr(audio.info, 'sample_rate'):
                metadata['sample_rate'] = audio.info.sample_rate

            # Get channels
            if hasattr(audio.info, 'channels'):
                metadata['channels'] = audio.info.channels

            # Extract tags based on format
            if audio.tags:
                metadata.update(MetadataHandler._extract_tags(audio, file_path))

            return metadata

        except Exception as e:
            print(f"Error reading metadata from {file_path}: {e}")
            return None

    @staticmethod
    def _extract_tags(audio: MutagenFile, file_path: str) -> Dict[str, Any]:
        """
        Extract tags from audio file based on format.

        Args:
            audio: Mutagen audio object
            file_path: Path to the audio file

        Returns:
            dict: Extracted tags
        """
        tags = {}
        ext = Path(file_path).suffix.lower()

        try:
            if ext == '.mp3':
                # ID3 tags for MP3
                if 'TIT2' in audio.tags:
                    tags['title'] = str(audio.tags['TIT2'])
                if 'TPE1' in audio.tags:
                    tags['artist'] = str(audio.tags['TPE1'])
                if 'TALB' in audio.tags:
                    tags['album'] = str(audio.tags['TALB'])
                if 'TDRC' in audio.tags:
                    tags['year'] = int(str(audio.tags['TDRC'])[:4]) if str(audio.tags['TDRC']) else None
                if 'TCON' in audio.tags:
                    tags['genre'] = str(audio.tags['TCON'])
                if 'TRCK' in audio.tags:
                    track = str(audio.tags['TRCK']).split('/')[0]
                    tags['track_number'] = int(track) if track.isdigit() else None
                if 'APIC:' in audio.tags:
                    tags['has_artwork'] = True

            elif ext in {'.m4a', '.mp4'}:
                # MP4 tags
                if '©nam' in audio.tags:
                    tags['title'] = str(audio.tags['©nam'][0])
                if '©ART' in audio.tags:
                    tags['artist'] = str(audio.tags['©ART'][0])
                if '©alb' in audio.tags:
                    tags['album'] = str(audio.tags['©alb'][0])
                if '©day' in audio.tags:
                    year_str = str(audio.tags['©day'][0])
                    tags['year'] = int(year_str[:4]) if year_str else None
                if '©gen' in audio.tags:
                    tags['genre'] = str(audio.tags['©gen'][0])
                if 'trkn' in audio.tags:
                    tags['track_number'] = audio.tags['trkn'][0][0]
                if 'covr' in audio.tags:
                    tags['has_artwork'] = True

            elif ext in {'.flac', '.ogg'}:
                # Vorbis comments
                if 'title' in audio.tags:
                    tags['title'] = str(audio.tags['title'][0])
                if 'artist' in audio.tags:
                    tags['artist'] = str(audio.tags['artist'][0])
                if 'album' in audio.tags:
                    tags['album'] = str(audio.tags['album'][0])
                if 'date' in audio.tags:
                    year_str = str(audio.tags['date'][0])
                    tags['year'] = int(year_str[:4]) if year_str else None
                if 'genre' in audio.tags:
                    tags['genre'] = str(audio.tags['genre'][0])
                if 'tracknumber' in audio.tags:
                    track = str(audio.tags['tracknumber'][0]).split('/')[0]
                    tags['track_number'] = int(track) if track.isdigit() else None

                # Check for artwork
                if ext == '.flac' and hasattr(audio, 'pictures') and audio.pictures:
                    tags['has_artwork'] = True

        except Exception as e:
            print(f"Error extracting tags: {e}")

        return tags

    @staticmethod
    def write_metadata(file_path: str, metadata: Dict[str, Any]) -> bool:
        """
        Write metadata to an audio file.

        Args:
            file_path: Path to the audio file
            metadata: Dictionary of metadata to write

        Returns:
            bool: True if successful, False otherwise
        """
        if not os.path.exists(file_path):
            return False

        if not MetadataHandler.is_supported(file_path):
            return False

        try:
            audio = MutagenFile(file_path)
            if audio is None:
                return False

            ext = Path(file_path).suffix.lower()

            # Ensure tags exist
            if audio.tags is None:
                if ext == '.mp3':
                    audio.add_tags()
                elif ext in {'.m4a', '.mp4'}:
                    audio = MP4(file_path)
                elif ext == '.flac':
                    audio = FLAC(file_path)

            # Write tags based on format
            if ext == '.mp3':
                MetadataHandler._write_id3_tags(audio, metadata)
            elif ext in {'.m4a', '.mp4'}:
                MetadataHandler._write_mp4_tags(audio, metadata)
            elif ext in {'.flac', '.ogg'}:
                MetadataHandler._write_vorbis_tags(audio, metadata)

            audio.save()
            return True

        except Exception as e:
            print(f"Error writing metadata to {file_path}: {e}")
            return False

    @staticmethod
    def _write_id3_tags(audio, metadata: Dict[str, Any]):
        """Write ID3 tags for MP3 files."""
        if 'title' in metadata:
            audio.tags['TIT2'] = TIT2(encoding=3, text=metadata['title'])
        if 'artist' in metadata:
            audio.tags['TPE1'] = TPE1(encoding=3, text=metadata['artist'])
        if 'album' in metadata:
            audio.tags['TALB'] = TALB(encoding=3, text=metadata['album'])
        if 'year' in metadata and metadata['year']:
            audio.tags['TDRC'] = TDRC(encoding=3, text=str(metadata['year']))
        if 'genre' in metadata:
            audio.tags['TCON'] = TCON(encoding=3, text=metadata['genre'])
        if 'track_number' in metadata and metadata['track_number']:
            audio.tags['TRCK'] = TRCK(encoding=3, text=str(metadata['track_number']))

    @staticmethod
    def _write_mp4_tags(audio, metadata: Dict[str, Any]):
        """Write MP4 tags for M4A files."""
        if 'title' in metadata:
            audio.tags['©nam'] = [metadata['title']]
        if 'artist' in metadata:
            audio.tags['©ART'] = [metadata['artist']]
        if 'album' in metadata:
            audio.tags['©alb'] = [metadata['album']]
        if 'year' in metadata and metadata['year']:
            audio.tags['©day'] = [str(metadata['year'])]
        if 'genre' in metadata:
            audio.tags['©gen'] = [metadata['genre']]
        if 'track_number' in metadata and metadata['track_number']:
            audio.tags['trkn'] = [(metadata['track_number'], 0)]

    @staticmethod
    def _write_vorbis_tags(audio, metadata: Dict[str, Any]):
        """Write Vorbis comments for FLAC/OGG files."""
        if 'title' in metadata:
            audio.tags['title'] = metadata['title']
        if 'artist' in metadata:
            audio.tags['artist'] = metadata['artist']
        if 'album' in metadata:
            audio.tags['album'] = metadata['album']
        if 'year' in metadata and metadata['year']:
            audio.tags['date'] = str(metadata['year'])
        if 'genre' in metadata:
            audio.tags['genre'] = metadata['genre']
        if 'track_number' in metadata and metadata['track_number']:
            audio.tags['tracknumber'] = str(metadata['track_number'])

    @staticmethod
    def calculate_file_hash(file_path: str, algorithm: str = 'md5') -> str:
        """
        Calculate hash of a file.

        Args:
            file_path: Path to the file
            algorithm: Hash algorithm ('md5' or 'sha256')

        Returns:
            str: Hex digest of the file hash
        """
        hash_func = hashlib.md5() if algorithm == 'md5' else hashlib.sha256()

        try:
            with open(file_path, 'rb') as f:
                while chunk := f.read(8192):
                    hash_func.update(chunk)
            return hash_func.hexdigest()
        except Exception as e:
            print(f"Error calculating hash for {file_path}: {e}")
            return ''

    @staticmethod
    def scan_directory(directory: str, recursive: bool = True) -> list:
        """
        Scan a directory for supported audio files.

        Args:
            directory: Path to directory to scan
            recursive: Whether to scan subdirectories

        Returns:
            list: List of file paths
        """
        audio_files = []

        try:
            path = Path(directory)
            if not path.exists():
                return audio_files

            pattern = '**/*' if recursive else '*'

            for file_path in path.glob(pattern):
                if file_path.is_file() and MetadataHandler.is_supported(str(file_path)):
                    audio_files.append(str(file_path))

        except Exception as e:
            print(f"Error scanning directory {directory}: {e}")

        return audio_files
