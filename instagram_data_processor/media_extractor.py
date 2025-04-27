"""
Media extraction module for Instagram data.
"""

import os
import shutil
import logging
from datetime import datetime
from . import utils

logger = logging.getLogger(__name__)

class MediaExtractor:
    """
    Extract media files from Instagram data.
    """

    def __init__(self, data_path, output_path, target_user):
        """
        Initialize the media extractor.

        Args:
            data_path (str): Path to Instagram data folder
            output_path (str): Path to output folder
            target_user (str): Name of the target user
        """
        self.data_path = data_path
        self.output_path = output_path
        self.target_user = target_user

        # Create output directories
        self.output_dirs = utils.setup_directories(output_path)

        logger.info(f"Initialized media extractor for user: {target_user}")

    def extract_all_media(self, messages):
        """
        Extract all media files from messages.

        Args:
            messages (list): List of processed messages

        Returns:
            dict: Dictionary with counts of extracted media
        """
        photo_count = self.extract_photos(messages)
        video_count = self.extract_videos(messages)
        audio_count = self.extract_audio(messages)

        return {
            "photos": photo_count,
            "videos": video_count,
            "audio": audio_count,
            "total": photo_count + video_count + audio_count
        }

    def extract_photos(self, messages):
        """
        Extract photos from messages.

        Args:
            messages (list): List of processed messages

        Returns:
            int: Number of photos extracted
        """
        count = 0

        for msg in messages:
            if not msg["photos"]:
                continue

            sender = msg["sender"]
            date_str = msg["date"].replace("-", "")
            time_str = msg["time"].replace(":", "")

            for i, photo_uri in enumerate(msg["photos"]):
                try:
                    # Construct source path - fix the path format
                    # The URI might contain "your_instagram_activity/messages/inbox/..."
                    # We need to extract just the relative part after "inbox/"
                    if "inbox/" in photo_uri:
                        relative_path = photo_uri.split("inbox/")[1]
                        source_path = os.path.join(self.data_path, "inbox", relative_path)
                    else:
                        # Try direct path
                        source_path = os.path.join(self.data_path, photo_uri)

                        # If that doesn't work, try with just the filename
                        if not os.path.exists(source_path):
                            filename = os.path.basename(photo_uri)
                            inbox_path = os.path.join(self.data_path, "inbox")

                            # Look for the file in the photos directory
                            for root, _, files in os.walk(inbox_path):
                                if "photos" in root and filename in files:
                                    source_path = os.path.join(root, filename)
                                    break

                    if not os.path.exists(source_path):
                        logger.warning(f"Photo file not found: {source_path}")
                        continue

                    # Construct destination filename
                    file_ext = os.path.splitext(source_path)[1]
                    dest_filename = f"{date_str}_{time_str}_{sender}_{i+1}{file_ext}"
                    dest_path = os.path.join(self.output_dirs["photos"], dest_filename)

                    # Copy file
                    shutil.copy2(source_path, dest_path)
                    logger.info(f"Extracted photo: {dest_path}")
                    count += 1

                except Exception as e:
                    logger.error(f"Error extracting photo {photo_uri}: {str(e)}")

        logger.info(f"Extracted {count} photos")
        return count

    def extract_videos(self, messages):
        """
        Extract videos from messages.

        Args:
            messages (list): List of processed messages

        Returns:
            int: Number of videos extracted
        """
        count = 0

        for msg in messages:
            if not msg["videos"]:
                continue

            sender = msg["sender"]
            date_str = msg["date"].replace("-", "")
            time_str = msg["time"].replace(":", "")

            for i, video_uri in enumerate(msg["videos"]):
                try:
                    # Construct source path - fix the path format
                    # The URI might contain "your_instagram_activity/messages/inbox/..."
                    # We need to extract just the relative part after "inbox/"
                    if "inbox/" in video_uri:
                        relative_path = video_uri.split("inbox/")[1]
                        source_path = os.path.join(self.data_path, "inbox", relative_path)
                    else:
                        # Try direct path
                        source_path = os.path.join(self.data_path, video_uri)

                        # If that doesn't work, try with just the filename
                        if not os.path.exists(source_path):
                            filename = os.path.basename(video_uri)
                            inbox_path = os.path.join(self.data_path, "inbox")

                            # Look for the file in the videos directory
                            for root, _, files in os.walk(inbox_path):
                                if "videos" in root and filename in files:
                                    source_path = os.path.join(root, filename)
                                    break

                    if not os.path.exists(source_path):
                        logger.warning(f"Video file not found: {source_path}")
                        continue

                    # Construct destination filename
                    file_ext = os.path.splitext(source_path)[1]
                    dest_filename = f"{date_str}_{time_str}_{sender}_{i+1}{file_ext}"
                    dest_path = os.path.join(self.output_dirs["videos"], dest_filename)

                    # Copy file
                    shutil.copy2(source_path, dest_path)
                    logger.info(f"Extracted video: {dest_path}")
                    count += 1

                except Exception as e:
                    logger.error(f"Error extracting video {video_uri}: {str(e)}")

        logger.info(f"Extracted {count} videos")
        return count

    def extract_audio(self, messages):
        """
        Extract audio files from messages.

        Args:
            messages (list): List of processed messages

        Returns:
            int: Number of audio files extracted
        """
        count = 0

        for msg in messages:
            if not msg["audio"]:
                continue

            sender = msg["sender"]
            date_str = msg["date"].replace("-", "")
            time_str = msg["time"].replace(":", "")

            for i, audio_uri in enumerate(msg["audio"]):
                try:
                    # Construct source path - fix the path format
                    # The URI might contain "your_instagram_activity/messages/inbox/..."
                    # We need to extract just the relative part after "inbox/"
                    if "inbox/" in audio_uri:
                        relative_path = audio_uri.split("inbox/")[1]
                        source_path = os.path.join(self.data_path, "inbox", relative_path)
                    else:
                        # Try direct path
                        source_path = os.path.join(self.data_path, audio_uri)

                        # If that doesn't work, try with just the filename
                        if not os.path.exists(source_path):
                            filename = os.path.basename(audio_uri)
                            inbox_path = os.path.join(self.data_path, "inbox")

                            # Look for the file in the audio directory
                            for root, _, files in os.walk(inbox_path):
                                if "audio" in root and filename in files:
                                    source_path = os.path.join(root, filename)
                                    break

                    if not os.path.exists(source_path):
                        logger.warning(f"Audio file not found: {source_path}")
                        continue

                    # Construct destination filename
                    file_ext = os.path.splitext(source_path)[1]
                    dest_filename = f"{date_str}_{time_str}_{sender}_{i+1}{file_ext}"
                    dest_path = os.path.join(self.output_dirs["audio"], dest_filename)

                    # Copy file
                    shutil.copy2(source_path, dest_path)
                    logger.info(f"Extracted audio: {dest_path}")
                    count += 1

                except Exception as e:
                    logger.error(f"Error extracting audio {audio_uri}: {str(e)}")

        logger.info(f"Extracted {count} audio files")
        return count
