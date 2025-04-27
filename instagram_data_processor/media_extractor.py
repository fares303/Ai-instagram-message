"""
Media extraction module for Instagram data.
"""

import os
import shutil
import logging
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
        print(f"Starting photo extraction from {len(messages)} messages")

        for msg in messages:
            if not msg["photos"]:
                continue

            sender = msg["sender"]
            date_str = msg["date"].replace("-", "")
            time_str = msg["time"].replace(":", "")

            print(f"Processing {len(msg['photos'])} photos from message at {date_str}_{time_str}")

            for i, photo_uri in enumerate(msg["photos"]):
                try:
                    print(f"Processing photo URI: {photo_uri}")
                    source_path = None

                    # Try multiple approaches to find the photo file

                    # Approach 1: Check if it's a full path
                    if os.path.isabs(photo_uri) and os.path.exists(photo_uri):
                        source_path = photo_uri
                        print(f"Found photo using absolute path: {source_path}")

                    # Approach 2: Check if it's a relative path from data_path
                    if not source_path:
                        rel_path = os.path.join(self.data_path, photo_uri)
                        if os.path.exists(rel_path):
                            source_path = rel_path
                            print(f"Found photo using relative path from data_path: {source_path}")

                    # Approach 3: Check if it's a path relative to inbox folder
                    if not source_path and "inbox/" in photo_uri:
                        relative_path = photo_uri.split("inbox/")[1]
                        inbox_path = os.path.join(self.data_path, "inbox")
                        inbox_rel_path = os.path.join(inbox_path, relative_path)
                        if os.path.exists(inbox_rel_path):
                            source_path = inbox_rel_path
                            print(f"Found photo using inbox relative path: {source_path}")

                    # Approach 4: Try to find the file by filename in any photos directory
                    if not source_path:
                        filename = os.path.basename(photo_uri)
                        print(f"Searching for filename: {filename}")

                        # Search in the entire data path
                        for root, _, files in os.walk(self.data_path):
                            if filename in files:
                                source_path = os.path.join(root, filename)
                                print(f"Found photo by filename: {source_path}")
                                break

                    # Approach 5: Try to find any image file with a similar name
                    if not source_path:
                        # Get the filename without extension
                        filename_no_ext = os.path.splitext(os.path.basename(photo_uri))[0]
                        print(f"Searching for similar filename: {filename_no_ext}.*")

                        # Common image extensions
                        img_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff']

                        # Search in the entire data path
                        for root, _, files in os.walk(self.data_path):
                            for file in files:
                                file_no_ext = os.path.splitext(file)[0]
                                file_ext = os.path.splitext(file)[1].lower()

                                if file_no_ext == filename_no_ext and file_ext in img_extensions:
                                    source_path = os.path.join(root, file)
                                    print(f"Found photo with similar name: {source_path}")
                                    break

                            if source_path:
                                break

                    if not source_path:
                        print(f"Photo file not found for URI: {photo_uri}")
                        logger.warning(f"Photo file not found for URI: {photo_uri}")
                        continue

                    # Construct destination filename
                    file_ext = os.path.splitext(source_path)[1]
                    if not file_ext:
                        file_ext = ".jpg"  # Default to .jpg if no extension

                    dest_filename = f"{date_str}_{time_str}_{sender}_{i+1}{file_ext}"
                    dest_path = os.path.join(self.output_dirs["photos"], dest_filename)

                    print(f"Copying photo from {source_path} to {dest_path}")

                    # Copy file
                    shutil.copy2(source_path, dest_path)
                    logger.info(f"Extracted photo: {dest_path}")
                    print(f"Successfully extracted photo: {dest_path}")
                    count += 1

                except Exception as e:
                    logger.error(f"Error extracting photo {photo_uri}: {str(e)}")
                    print(f"Error extracting photo {photo_uri}: {str(e)}")

        logger.info(f"Extracted {count} photos")
        print(f"Extracted {count} photos")
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
        print(f"Starting video extraction from {len(messages)} messages")

        for msg in messages:
            if not msg["videos"]:
                continue

            sender = msg["sender"]
            date_str = msg["date"].replace("-", "")
            time_str = msg["time"].replace(":", "")

            print(f"Processing {len(msg['videos'])} videos from message at {date_str}_{time_str}")

            for i, video_uri in enumerate(msg["videos"]):
                try:
                    print(f"Processing video URI: {video_uri}")
                    source_path = None

                    # Try multiple approaches to find the video file

                    # Approach 1: Check if it's a full path
                    if os.path.isabs(video_uri) and os.path.exists(video_uri):
                        source_path = video_uri
                        print(f"Found video using absolute path: {source_path}")

                    # Approach 2: Check if it's a relative path from data_path
                    if not source_path:
                        rel_path = os.path.join(self.data_path, video_uri)
                        if os.path.exists(rel_path):
                            source_path = rel_path
                            print(f"Found video using relative path from data_path: {source_path}")

                    # Approach 3: Check if it's a path relative to inbox folder
                    if not source_path and "inbox/" in video_uri:
                        relative_path = video_uri.split("inbox/")[1]
                        inbox_path = os.path.join(self.data_path, "inbox")
                        inbox_rel_path = os.path.join(inbox_path, relative_path)
                        if os.path.exists(inbox_rel_path):
                            source_path = inbox_rel_path
                            print(f"Found video using inbox relative path: {source_path}")

                    # Approach 4: Try to find the file by filename in any videos directory
                    if not source_path:
                        filename = os.path.basename(video_uri)
                        print(f"Searching for filename: {filename}")

                        # Search in the entire data path
                        for root, _, files in os.walk(self.data_path):
                            if filename in files:
                                source_path = os.path.join(root, filename)
                                print(f"Found video by filename: {source_path}")
                                break

                    # Approach 5: Try to find any video file with a similar name
                    if not source_path:
                        # Get the filename without extension
                        filename_no_ext = os.path.splitext(os.path.basename(video_uri))[0]
                        print(f"Searching for similar filename: {filename_no_ext}.*")

                        # Common video extensions
                        video_extensions = ['.mp4', '.mov', '.avi', '.wmv', '.flv', '.mkv', '.webm']

                        # Search in the entire data path
                        for root, _, files in os.walk(self.data_path):
                            for file in files:
                                file_no_ext = os.path.splitext(file)[0]
                                file_ext = os.path.splitext(file)[1].lower()

                                if file_no_ext == filename_no_ext and file_ext in video_extensions:
                                    source_path = os.path.join(root, file)
                                    print(f"Found video with similar name: {source_path}")
                                    break

                            if source_path:
                                break

                    if not source_path:
                        print(f"Video file not found for URI: {video_uri}")
                        logger.warning(f"Video file not found for URI: {video_uri}")
                        continue

                    # Construct destination filename
                    file_ext = os.path.splitext(source_path)[1]
                    if not file_ext:
                        file_ext = ".mp4"  # Default to .mp4 if no extension

                    dest_filename = f"{date_str}_{time_str}_{sender}_{i+1}{file_ext}"
                    dest_path = os.path.join(self.output_dirs["videos"], dest_filename)

                    print(f"Copying video from {source_path} to {dest_path}")

                    # Copy file
                    shutil.copy2(source_path, dest_path)
                    logger.info(f"Extracted video: {dest_path}")
                    print(f"Successfully extracted video: {dest_path}")
                    count += 1

                except Exception as e:
                    logger.error(f"Error extracting video {video_uri}: {str(e)}")
                    print(f"Error extracting video {video_uri}: {str(e)}")

        logger.info(f"Extracted {count} videos")
        print(f"Extracted {count} videos")
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
        print(f"Starting audio extraction from {len(messages)} messages")

        for msg in messages:
            if not msg["audio"]:
                continue

            sender = msg["sender"]
            date_str = msg["date"].replace("-", "")
            time_str = msg["time"].replace(":", "")

            print(f"Processing {len(msg['audio'])} audio files from message at {date_str}_{time_str}")

            for i, audio_uri in enumerate(msg["audio"]):
                try:
                    print(f"Processing audio URI: {audio_uri}")
                    source_path = None

                    # Try multiple approaches to find the audio file

                    # Approach 1: Check if it's a full path
                    if os.path.isabs(audio_uri) and os.path.exists(audio_uri):
                        source_path = audio_uri
                        print(f"Found audio using absolute path: {source_path}")

                    # Approach 2: Check if it's a relative path from data_path
                    if not source_path:
                        rel_path = os.path.join(self.data_path, audio_uri)
                        if os.path.exists(rel_path):
                            source_path = rel_path
                            print(f"Found audio using relative path from data_path: {source_path}")

                    # Approach 3: Check if it's a path relative to inbox folder
                    if not source_path and "inbox/" in audio_uri:
                        relative_path = audio_uri.split("inbox/")[1]
                        inbox_path = os.path.join(self.data_path, "inbox")
                        inbox_rel_path = os.path.join(inbox_path, relative_path)
                        if os.path.exists(inbox_rel_path):
                            source_path = inbox_rel_path
                            print(f"Found audio using inbox relative path: {source_path}")

                    # Approach 4: Try to find the file by filename in any audio directory
                    if not source_path:
                        filename = os.path.basename(audio_uri)
                        print(f"Searching for filename: {filename}")

                        # Search in the entire data path
                        for root, _, files in os.walk(self.data_path):
                            if filename in files:
                                source_path = os.path.join(root, filename)
                                print(f"Found audio by filename: {source_path}")
                                break

                    # Approach 5: Try to find any audio file with a similar name
                    if not source_path:
                        # Get the filename without extension
                        filename_no_ext = os.path.splitext(os.path.basename(audio_uri))[0]
                        print(f"Searching for similar filename: {filename_no_ext}.*")

                        # Common audio extensions
                        audio_extensions = ['.mp3', '.wav', '.ogg', '.m4a', '.aac', '.flac', '.opus']

                        # Search in the entire data path
                        for root, _, files in os.walk(self.data_path):
                            for file in files:
                                file_no_ext = os.path.splitext(file)[0]
                                file_ext = os.path.splitext(file)[1].lower()

                                if file_no_ext == filename_no_ext and file_ext in audio_extensions:
                                    source_path = os.path.join(root, file)
                                    print(f"Found audio with similar name: {source_path}")
                                    break

                            if source_path:
                                break

                    if not source_path:
                        print(f"Audio file not found for URI: {audio_uri}")
                        logger.warning(f"Audio file not found for URI: {audio_uri}")
                        continue

                    # Construct destination filename
                    file_ext = os.path.splitext(source_path)[1]
                    if not file_ext:
                        file_ext = ".mp3"  # Default to .mp3 if no extension

                    dest_filename = f"{date_str}_{time_str}_{sender}_{i+1}{file_ext}"
                    dest_path = os.path.join(self.output_dirs["audio"], dest_filename)

                    print(f"Copying audio from {source_path} to {dest_path}")

                    # Copy file
                    shutil.copy2(source_path, dest_path)
                    logger.info(f"Extracted audio: {dest_path}")
                    print(f"Successfully extracted audio: {dest_path}")
                    count += 1

                except Exception as e:
                    logger.error(f"Error extracting audio {audio_uri}: {str(e)}")
                    print(f"Error extracting audio {audio_uri}: {str(e)}")

        logger.info(f"Extracted {count} audio files")
        print(f"Extracted {count} audio files")
        return count
