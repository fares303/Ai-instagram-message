"""
JSON processing module for Instagram data.
"""

import os
import json
import logging
from datetime import datetime
import pandas as pd
from . import utils
from . import config

logger = logging.getLogger(__name__)

class InstagramDataProcessor:
    """
    Process Instagram JSON data files.
    """

    def __init__(self, data_path, target_user, my_name):
        """
        Initialize the processor.

        Args:
            data_path (str): Path to Instagram data folder
            target_user (str): Name of the target user to analyze
            my_name (str): Your name
        """
        self.data_path = data_path
        self.target_user = target_user
        self.my_name = my_name
        self.messages = []
        self.participants = set()
        self.conversation_files = []

        logger.info(f"Initialized processor for user: {target_user}")

    def find_conversation_files(self):
        """
        Find all JSON conversation files for the target user.

        Returns:
            list: List of JSON file paths
        """
        print(f"Looking for conversation files in {self.data_path}")
        logger.info(f"Looking for conversation files in {self.data_path}")

        # Check if the data path exists
        if not os.path.exists(self.data_path):
            logger.error(f"Data path does not exist: {self.data_path}")
            print(f"Data path does not exist: {self.data_path}")
            return []

        json_files = []

        # First, try to find all JSON files in the data path
        for root, _, files in os.walk(self.data_path):
            for file in files:
                if file.endswith(".json"):
                    json_path = os.path.join(root, file)
                    print(f"Found JSON file: {json_path}")

                    # Try to read the file with different encodings
                    for encoding in ['utf-8', 'latin1', 'cp1252']:
                        try:
                            with open(json_path, 'r', encoding=encoding) as f:
                                data = json.load(f)

                                # Check if this is a conversation file
                                if isinstance(data, dict) and "messages" in data:
                                    print(f"File contains messages, adding to list: {json_path}")
                                    json_files.append(json_path)
                                    break  # Found a valid encoding, no need to try others
                        except Exception:
                            continue  # Try next encoding

        if not json_files:
            print("No valid JSON files found containing messages")
            logger.warning("No valid JSON files found containing messages")
        else:
            print(f"Found {len(json_files)} JSON files containing messages")
            logger.info(f"Found {len(json_files)} JSON files containing messages")

        self.conversation_files = json_files
        return json_files

    def process_json_files(self):
        """
        Process all JSON files and extract messages.

        Returns:
            list: List of processed messages
        """
        if not self.conversation_files:
            self.find_conversation_files()

        if not self.conversation_files:
            logger.error(f"No conversation files found for {self.target_user}")
            print(f"No conversation files found for {self.target_user}")
            return []

        all_messages = []
        print(f"Found {len(self.conversation_files)} conversation files to process")

        for file_path in self.conversation_files:
            print(f"\nProcessing file: {file_path}")
            try:
                # Try different encodings
                encodings_to_try = ['utf-8', 'latin1', 'cp1252', 'utf-16']
                data = None

                for encoding in encodings_to_try:
                    try:
                        print(f"Trying to read with {encoding} encoding")
                        with open(file_path, 'r', encoding=encoding) as file:
                            file_content = file.read()
                            data = json.loads(file_content)
                            print(f"Successfully read file with {encoding} encoding")
                            break
                    except UnicodeDecodeError:
                        print(f"Failed to decode with {encoding} encoding")
                        continue
                    except json.JSONDecodeError:
                        print(f"Failed to parse JSON with {encoding} encoding")
                        continue

                if data is None:
                    # If all encodings failed, try the special latin1->utf8 conversion
                    try:
                        print("Trying special latin1->utf8 conversion")
                        with open(file_path, 'r', encoding='latin1') as file:
                            file_content = file.read()
                            # Convert latin1 to utf-8 to fix encoding issues
                            file_content = file_content.encode('latin1').decode('utf-8')
                            data = json.loads(file_content)
                            print("Successfully read file with special conversion")
                    except Exception as e:
                        print(f"Special conversion failed: {e}")

                if data is None:
                    print(f"Could not read file {file_path} with any encoding")
                    continue

                # Print file structure for debugging
                if isinstance(data, dict):
                    print(f"File structure keys: {data.keys()}")
                else:
                    print(f"Data is not a dictionary, type: {type(data)}")

                # Extract participants
                if isinstance(data, dict) and "participants" in data:
                    print(f"Found participants: {[p.get('name', '') for p in data['participants']]}")
                    for participant in data["participants"]:
                        self.participants.add(participant.get("name", ""))

                # Process messages
                if isinstance(data, dict) and "messages" in data:
                    print(f"Found {len(data['messages'])} messages in the file")
                    for msg in data["messages"]:
                        processed_msg = self._process_message(msg)
                        if processed_msg:
                            all_messages.append(processed_msg)
                else:
                    print("No messages found in the expected format")

            except Exception as e:
                logger.error(f"Error processing file {file_path}: {str(e)}")
                print(f"Error processing file {file_path}: {str(e)}")

        # Sort messages by timestamp (oldest first)
        all_messages.sort(key=lambda x: x["timestamp"])

        self.messages = all_messages
        logger.info(f"Processed {len(all_messages)} messages")
        print(f"\nTotal processed messages: {len(all_messages)}")

        return all_messages

    def _process_message(self, message):
        """
        Process a single message.

        Args:
            message (dict): Raw message data

        Returns:
            dict: Processed message or None if should be skipped
        """
        # Print message structure for debugging
        print(f"Processing message: {message.keys()}")

        # Extract sender name with fallback options
        sender = message.get("sender_name", "")
        if not sender:
            sender = message.get("sender", "")

        # Fix any encoding issues in sender name
        sender = utils.fix_broken_text(sender)

        # Extract timestamp with fallback options
        timestamp_ms = message.get("timestamp_ms", 0)
        if not timestamp_ms:
            timestamp_ms = message.get("timestamp", 0)

        # Extract content with fallback options
        content = message.get("content", "")
        if not content and "text" in message:
            content = message.get("text", "")

        # Process timestamp
        dt = utils.convert_timestamp(timestamp_ms)

        # Process content
        if content:
            # First fix any broken encoding, then unescape
            content = utils.fix_broken_text(content)
            content = utils.unescape_text(content)

        # Extract reactions with improved error handling
        reactions = []
        if "reactions" in message and isinstance(message["reactions"], list):
            for reaction in message["reactions"]:
                if isinstance(reaction, dict):
                    reaction_text = utils.unescape_text(reaction.get("reaction", ""))
                    actor = reaction.get("actor", "")
                    if reaction_text:
                        reactions.append({
                            "reaction": reaction_text,
                            "actor": actor
                        })

        # Check for photos with improved error handling
        photos = []
        # Check standard Instagram format
        if "photos" in message and isinstance(message["photos"], list):
            for photo in message["photos"]:
                if isinstance(photo, dict) and "uri" in photo:
                    photos.append(photo["uri"])

        # Check alternative formats
        if "attachments" in message and isinstance(message["attachments"], list):
            for attachment in message["attachments"]:
                if isinstance(attachment, dict):
                    # Check for photos in attachments
                    if attachment.get("type") == "photo" or "photo" in str(attachment).lower():
                        if "uri" in attachment:
                            photos.append(attachment["uri"])
                        elif "path" in attachment:
                            photos.append(attachment["path"])
                        elif "url" in attachment:
                            photos.append(attachment["url"])
                        elif "data" in attachment and isinstance(attachment["data"], dict):
                            if "uri" in attachment["data"]:
                                photos.append(attachment["data"]["uri"])

        # Check for videos with improved error handling
        videos = []
        # Check standard Instagram format
        if "videos" in message and isinstance(message["videos"], list):
            for video in message["videos"]:
                if isinstance(video, dict) and "uri" in video:
                    videos.append(video["uri"])

        # Check alternative formats
        if "attachments" in message and isinstance(message["attachments"], list):
            for attachment in message["attachments"]:
                if isinstance(attachment, dict):
                    # Check for videos in attachments
                    if attachment.get("type") == "video" or "video" in str(attachment).lower():
                        if "uri" in attachment:
                            videos.append(attachment["uri"])
                        elif "path" in attachment:
                            videos.append(attachment["path"])
                        elif "url" in attachment:
                            videos.append(attachment["url"])
                        elif "data" in attachment and isinstance(attachment["data"], dict):
                            if "uri" in attachment["data"]:
                                videos.append(attachment["data"]["uri"])

        # Check for audio with improved error handling
        audio = []
        # Check standard Instagram format
        if "audio_files" in message and isinstance(message["audio_files"], list):
            for audio_file in message["audio_files"]:
                if isinstance(audio_file, dict) and "uri" in audio_file:
                    audio.append(audio_file["uri"])

        # Check alternative formats
        if "attachments" in message and isinstance(message["attachments"], list):
            for attachment in message["attachments"]:
                if isinstance(attachment, dict):
                    # Check for audio in attachments
                    if attachment.get("type") == "audio" or "audio" in str(attachment).lower():
                        if "uri" in attachment:
                            audio.append(attachment["uri"])
                        elif "path" in attachment:
                            audio.append(attachment["path"])
                        elif "url" in attachment:
                            audio.append(attachment["url"])
                        elif "data" in attachment and isinstance(attachment["data"], dict):
                            if "uri" in attachment["data"]:
                                audio.append(attachment["data"]["uri"])

        # Create processed message
        processed_message = {
            "sender": sender,
            "timestamp": dt,
            "date": utils.format_datetime(dt, config.DATE_FORMAT),
            "time": utils.format_datetime(dt, config.TIME_FORMAT),
            "content": content,
            "reactions": reactions,
            "photos": photos,
            "videos": videos,
            "audio": audio,
            "has_emoji": utils.count_emojis(content) > 0,
            "emoji_count": utils.count_emojis(content),
            "emojis": utils.extract_emojis(content),
            "is_good_morning": utils.contains_phrase(content, config.GOOD_MORNING_PHRASES),
            "mentions_my_name": self.my_name.lower() in content.lower() if content else False,
            "mentions_target_name": self.target_user.lower() in content.lower() if content else False,
            "has_custom_phrase": any(utils.contains_phrase(content, [phrase]) for phrase in config.CUSTOM_PHRASES)
        }

        # Print processed message for debugging
        print(f"Processed message: sender={sender}, date={processed_message['date']}, has_photos={len(photos)}, has_videos={len(videos)}, has_audio={len(audio)}")

        return processed_message

    def get_dataframe(self):
        """
        Convert processed messages to a pandas DataFrame.

        Returns:
            DataFrame: Pandas DataFrame with all messages
        """
        if not self.messages:
            self.process_json_files()

        return pd.DataFrame(self.messages)

    def get_conversation_stats(self):
        """
        Generate statistics about the conversation.

        Returns:
            dict: Dictionary with statistics
        """
        if not self.messages:
            self.process_json_files()

        # Count total messages
        total_messages = len(self.messages)

        # Count messages by sender
        messages_by_sender = {}
        for msg in self.messages:
            sender = msg["sender"]
            messages_by_sender[sender] = messages_by_sender.get(sender, 0) + 1

        # Count total emojis
        total_emojis = sum(msg["emoji_count"] for msg in self.messages)

        # Count unique emojis
        all_emojis = []
        for msg in self.messages:
            all_emojis.extend(msg["emojis"])
        unique_emojis = set(all_emojis)

        # Count good morning messages
        good_morning_count = sum(1 for msg in self.messages if msg["is_good_morning"])

        # Count name mentions
        my_name_mentions = sum(1 for msg in self.messages if msg["mentions_my_name"])
        target_name_mentions = sum(1 for msg in self.messages if msg["mentions_target_name"])

        # Count active conversation days
        conversation_days = set(msg["date"] for msg in self.messages)

        # Count custom phrases
        custom_phrases_count = sum(1 for msg in self.messages if msg["has_custom_phrase"])

        # Most active day
        days_count = {}
        for msg in self.messages:
            days_count[msg["date"]] = days_count.get(msg["date"], 0) + 1

        most_active_day = max(days_count.items(), key=lambda x: x[1]) if days_count else ("N/A", 0)

        # Create stats dictionary
        stats = {
            "total_messages": total_messages,
            "messages_by_sender": messages_by_sender,
            "total_emojis": total_emojis,
            "unique_emojis_count": len(unique_emojis),
            "unique_emojis": list(unique_emojis),
            "good_morning_count": good_morning_count,
            "my_name_mentions": my_name_mentions,
            "target_name_mentions": target_name_mentions,
            "active_conversation_days": len(conversation_days),
            "first_message_date": self.messages[0]["date"] if self.messages else "N/A",
            "last_message_date": self.messages[-1]["date"] if self.messages else "N/A",
            "conversation_duration_days": (
                (datetime.strptime(self.messages[-1]["date"], config.DATE_FORMAT) -
                 datetime.strptime(self.messages[0]["date"], config.DATE_FORMAT)).days + 1
            ) if self.messages else 0,
            "custom_phrases_count": custom_phrases_count,
            "most_active_day": most_active_day[0],
            "most_active_day_count": most_active_day[1],
        }

        return stats
