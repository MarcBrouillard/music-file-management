"""
Duplicate detection module for finding duplicate music files.
Supports metadata comparison, file hash, and audio fingerprinting.
"""

from typing import List, Dict, Any, Tuple, Set
from difflib import SequenceMatcher
import os


class DuplicateDetector:
    """Detector for finding duplicate music files."""

    def __init__(self, tolerance: float = 0.9):
        """
        Initialize the duplicate detector.

        Args:
            tolerance: Similarity threshold (0.0-1.0) for fuzzy matching
        """
        self.tolerance = tolerance
        self.duplicate_groups = []

    @staticmethod
    def calculate_similarity(str1: str, str2: str) -> float:
        """
        Calculate similarity ratio between two strings.

        Args:
            str1: First string
            str2: Second string

        Returns:
            float: Similarity ratio (0.0-1.0)
        """
        if not str1 or not str2:
            return 0.0

        return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()

    def find_duplicates_by_metadata(
        self,
        files: List[Dict[str, Any]],
        compare_fields: List[str] = None
    ) -> List[List[Dict[str, Any]]]:
        """
        Find duplicates by comparing metadata.

        Args:
            files: List of file metadata dictionaries
            compare_fields: Fields to compare (default: artist, title, album)

        Returns:
            list: List of duplicate groups, each group is a list of files
        """
        if compare_fields is None:
            compare_fields = ['artist', 'title', 'album']

        duplicate_groups = []
        processed_ids = set()

        for i, file1 in enumerate(files):
            if file1.get('id') in processed_ids:
                continue

            duplicates = [file1]

            for file2 in files[i + 1:]:
                if file2.get('id') in processed_ids:
                    continue

                # Compare fields
                is_duplicate = True

                for field in compare_fields:
                    val1 = str(file1.get(field, '')).strip().lower()
                    val2 = str(file2.get(field, '')).strip().lower()

                    if not val1 or not val2:
                        is_duplicate = False
                        break

                    # Fuzzy matching
                    similarity = self.calculate_similarity(val1, val2)

                    if similarity < self.tolerance:
                        is_duplicate = False
                        break

                # Also compare duration (within 5 seconds)
                if is_duplicate and 'duration' in file1 and 'duration' in file2:
                    duration1 = file1.get('duration', 0)
                    duration2 = file2.get('duration', 0)

                    if abs(duration1 - duration2) > 5:  # 5 second tolerance
                        is_duplicate = False

                if is_duplicate:
                    duplicates.append(file2)
                    processed_ids.add(file2.get('id'))

            # Only add if there are duplicates
            if len(duplicates) > 1:
                processed_ids.add(file1.get('id'))
                duplicate_groups.append(duplicates)

        return duplicate_groups

    def find_duplicates_by_hash(
        self,
        files: List[Dict[str, Any]]
    ) -> List[List[Dict[str, Any]]]:
        """
        Find duplicates by comparing file hashes.

        Args:
            files: List of file metadata dictionaries

        Returns:
            list: List of duplicate groups
        """
        # Group files by hash
        hash_groups = {}

        for file_data in files:
            file_hash = file_data.get('file_hash')

            if not file_hash:
                continue

            if file_hash not in hash_groups:
                hash_groups[file_hash] = []

            hash_groups[file_hash].append(file_data)

        # Filter groups with more than one file
        duplicate_groups = [
            group for group in hash_groups.values()
            if len(group) > 1
        ]

        return duplicate_groups

    def find_duplicates_by_size_and_duration(
        self,
        files: List[Dict[str, Any]]
    ) -> List[List[Dict[str, Any]]]:
        """
        Find duplicates by comparing file size and duration.

        Args:
            files: List of file metadata dictionaries

        Returns:
            list: List of duplicate groups
        """
        # Group files by size and duration
        groups = {}

        for file_data in files:
            file_size = file_data.get('file_size', 0)
            duration = file_data.get('duration', 0)

            # Round duration to nearest second
            duration_key = round(duration)

            key = (file_size, duration_key)

            if key not in groups:
                groups[key] = []

            groups[key].append(file_data)

        # Filter groups with more than one file
        duplicate_groups = [
            group for group in groups.values()
            if len(group) > 1
        ]

        return duplicate_groups

    def find_duplicates_combined(
        self,
        files: List[Dict[str, Any]],
        use_metadata: bool = True,
        use_hash: bool = True,
        use_size: bool = False
    ) -> List[List[Dict[str, Any]]]:
        """
        Find duplicates using multiple methods.

        Args:
            files: List of file metadata dictionaries
            use_metadata: Use metadata comparison
            use_hash: Use file hash comparison
            use_size: Use size and duration comparison

        Returns:
            list: List of duplicate groups
        """
        all_groups = []

        # Collect duplicates from each method
        if use_metadata:
            metadata_groups = self.find_duplicates_by_metadata(files)
            all_groups.extend(metadata_groups)

        if use_hash:
            hash_groups = self.find_duplicates_by_hash(files)
            all_groups.extend(hash_groups)

        if use_size:
            size_groups = self.find_duplicates_by_size_and_duration(files)
            all_groups.extend(size_groups)

        # Merge overlapping groups
        merged_groups = self._merge_duplicate_groups(all_groups)

        return merged_groups

    def _merge_duplicate_groups(
        self,
        groups: List[List[Dict[str, Any]]]
    ) -> List[List[Dict[str, Any]]]:
        """
        Merge overlapping duplicate groups.

        Args:
            groups: List of duplicate groups

        Returns:
            list: Merged duplicate groups
        """
        if not groups:
            return []

        # Convert groups to sets of file IDs for easier merging
        id_groups = []
        for group in groups:
            ids = set(file_data.get('id') for file_data in group if file_data.get('id'))
            if ids:
                id_groups.append(ids)

        # Merge overlapping sets
        merged = []
        while id_groups:
            current = id_groups.pop(0)
            merged_any = True

            while merged_any:
                merged_any = False
                remaining = []

                for other in id_groups:
                    if current & other:  # If sets overlap
                        current |= other  # Merge them
                        merged_any = True
                    else:
                        remaining.append(other)

                id_groups = remaining

            merged.append(current)

        # Convert back to file data groups
        result_groups = []

        for id_set in merged:
            group = []

            for file_list in groups:
                for file_data in file_list:
                    if file_data.get('id') in id_set and file_data not in group:
                        group.append(file_data)

            if len(group) > 1:
                result_groups.append(group)

        return result_groups

    def get_best_quality_file(
        self,
        duplicate_group: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Get the best quality file from a duplicate group.

        Args:
            duplicate_group: List of duplicate files

        Returns:
            dict: Best quality file
        """
        if not duplicate_group:
            return {}

        # Sort by bitrate (highest first), then file size (largest first)
        sorted_files = sorted(
            duplicate_group,
            key=lambda f: (f.get('bitrate', 0), f.get('file_size', 0)),
            reverse=True
        )

        return sorted_files[0]

    def get_duplicate_statistics(
        self,
        duplicate_groups: List[List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """
        Get statistics about duplicates.

        Args:
            duplicate_groups: List of duplicate groups

        Returns:
            dict: Statistics dictionary
        """
        total_duplicates = sum(len(group) for group in duplicate_groups)
        total_groups = len(duplicate_groups)

        # Calculate wasted space (keep one file per group, rest is wasted)
        wasted_space = 0

        for group in duplicate_groups:
            # Sort by size, keep largest
            sorted_group = sorted(group, key=lambda f: f.get('file_size', 0), reverse=True)

            # Add up size of all but the largest
            for file_data in sorted_group[1:]:
                wasted_space += file_data.get('file_size', 0)

        return {
            'total_groups': total_groups,
            'total_duplicates': total_duplicates,
            'total_files': total_duplicates - total_groups,  # Excludes one from each group
            'wasted_space_bytes': wasted_space,
            'wasted_space_mb': wasted_space / (1024 * 1024)
        }

    def filter_duplicates_by_quality(
        self,
        duplicate_group: List[Dict[str, Any]],
        keep_highest: bool = True
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Filter duplicate group into files to keep and files to remove.

        Args:
            duplicate_group: List of duplicate files
            keep_highest: If True, keep highest quality, else keep lowest

        Returns:
            tuple: (files_to_keep, files_to_remove)
        """
        if not duplicate_group:
            return [], []

        # Sort by quality
        sorted_files = sorted(
            duplicate_group,
            key=lambda f: (f.get('bitrate', 0), f.get('file_size', 0)),
            reverse=keep_highest
        )

        # Keep the first one, remove the rest
        return [sorted_files[0]], sorted_files[1:]

    def auto_select_duplicates_for_removal(
        self,
        duplicate_groups: List[List[Dict[str, Any]]],
        keep_highest_quality: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Automatically select duplicate files for removal.

        Args:
            duplicate_groups: List of duplicate groups
            keep_highest_quality: Keep highest quality file from each group

        Returns:
            list: List of files to remove
        """
        files_to_remove = []

        for group in duplicate_groups:
            _, remove_files = self.filter_duplicates_by_quality(group, keep_highest_quality)
            files_to_remove.extend(remove_files)

        return files_to_remove
