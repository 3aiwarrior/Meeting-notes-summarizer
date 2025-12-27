"""
Storage service for file operations.

Handles file system operations for uploaded audio files.
"""

import os
import uuid
from pathlib import Path

from app.core.settings import settings


class StorageService:
    """
    Service for managing file storage operations.

    Handles saving, retrieving, and deleting uploaded audio files.
    """

    def __init__(self) -> None:
        """Initialize storage service and ensure upload directory exists."""
        self.upload_dir = Path(settings.upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def save_audio_file(self, file_content: bytes, original_filename: str) -> tuple[str, str]:
        """
        Save uploaded audio file to disk.

        Args:
            file_content: Binary audio file content
            original_filename: Original filename from upload

        Returns:
            Tuple[str, str]: (file_path, generated_filename)

        Raises:
            IOError: If file cannot be saved
        """
        # Generate unique filename
        # Reason: Prevent filename collisions and maintain original extension
        file_extension = Path(original_filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = self.upload_dir / unique_filename

        # Save file
        try:
            with open(file_path, "wb") as f:
                f.write(file_content)
        except Exception as e:
            raise OSError(f"Failed to save audio file: {str(e)}")

        return str(file_path), unique_filename

    def delete_audio_file(self, file_path: str) -> bool:
        """
        Delete audio file from disk.

        Args:
            file_path: Path to file to delete

        Returns:
            bool: True if deleted, False if file not found
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception:
            return False

    def get_file_size(self, file_path: str) -> int:
        """
        Get size of file in bytes.

        Args:
            file_path: Path to file

        Returns:
            int: File size in bytes

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        return os.path.getsize(file_path)

    def file_exists(self, file_path: str) -> bool:
        """
        Check if file exists.

        Args:
            file_path: Path to check

        Returns:
            bool: True if file exists
        """
        return os.path.exists(file_path)
