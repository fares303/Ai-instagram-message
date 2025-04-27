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
        inbox_path = os.path.join(self.data_path, "inbox")

        if not os.path.exists(inbox_path):
            logger.error(f"Inbox path does not exist: {inbox_path}")
            return []

        json_files = []

        # Look specifically for the nailabelaidi folder first
        naila_folder = os.path.join(inbox_path, "nailabelaidi_435947657788262")
        if os.path.exists(naila_folder) and os.path.isdir(naila_folder):
            for file in os.listdir(naila_folder):
                if file.endswith(".json"):
                    json_files.append(os.path.join(naila_folder, file))
                    logger.info(f"Found conversation file: {os.path.join(naila_folder, file)}")

            # If we found files in the specific folder, return them
            if json_files:
                self.conversation_files = json_files
                logger.info(f"Found {len(json_files)} conversation files for {self.target_user}")
                return json_files

        # If the specific folder wasn't found or had no JSON files, try the general approach
        for folder_name in os.listdir(inbox_path):
            folder_path = os.path.join(inbox_path, folder_name)

            # Check if it's a directory
            if os.path.isdir(folder_path):
                # Look for JSON files in this directory
                for file in os.listdir(folder_path):
                    if file.endswith(".json"):
                        json_path = os.path.join(folder_path, file)

                        # Check if this JSON file contains the target user
                        try:
                            with open(json_path, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                                if "participants" in data:
                                    participant_names = [p.get("name", "") for p in data["participants"]]

                                    # If the target user is in participants, add this file
                                    if any(self.target_user.lower() in name.lower() for name in participant_names) or \
                                       any(name.lower() in self.target_user.lower() for name in participant_names):
                                        json_files.append(json_path)
                                        logger.info(f"Found conversation file: {json_path}")
                                        break  # Found a match, no need to check other files in this folder
                        except Exception as e:
                            logger.error(f"Error checking JSON file {json_path}: {str(e)}")

        self.conversation_files = json_files
        logger.info(f"Found {len(json_files)} conversation files for {self.target_user}")
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
            return []

        all_messages = []

        for file_path in self.conversation_files:
            try:
                # First try with utf-8 encoding
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        data = json.load(file)
                except UnicodeDecodeError:
                    # If utf-8 fails, try with latin1 encoding and convert to utf-8
                    with open(file_path, 'r', encoding='latin1') as file:
                        file_content = file.read()
                        # Convert latin1 to utf-8 to fix encoding issues
                        file_content = file_content.encode('latin1').decode('utf-8')
                        data = json.loads(file_content)

                # Extract participants
                if "participants" in data:
                    for participant in data["participants"]:
                        self.participants.add(participant.get("name", ""))

                # Process messages
                if "messages" in data:
                    for msg in data["messages"]:
                        processed_msg = self._process_message(msg)
                        if processed_msg:
                            all_messages.append(processed_msg)

            except Exception as e:
                logger.error(f"Error processing file {file_path}: {str(e)}")

        # Sort messages by timestamp (oldest first)
        all_messages.sort(key=lambda x: x["timestamp"])

        self.messages = all_messages
        logger.info(f"Processed {len(all_messages)} messages")

        return all_messages

    def _process_message(self, message):
        """
        Process a single message.

        Args:
            message (dict): Raw message data

        Returns:
            dict: Processed message or None if should be skipped
        """
        sender = message.get("sender_name", "")

        timestamp_ms = message.get("timestamp_ms", 0)
        content = message.get("content", "")

        # Process timestamp
        dt = utils.convert_timestamp(timestamp_ms)

        # Process content
        if content:
            # First fix any broken encoding, then unescape
            content = utils.fix_broken_text(content)
            content = utils.unescape_text(content)

        # Extract reactions
        reactions = []
        if "reactions" in message:
            for reaction in message["reactions"]:
                reactions.append({
                    "reaction": utils.unescape_text(reaction.get("reaction", "")),
                    "actor": reaction.get("actor", "")
                })

        # Check for photos, videos, audio
        photos = []
        if "photos" in message:
            for photo in message["photos"]:
                if "uri" in photo:
                    photos.append(photo["uri"])

        videos = []
        if "videos" in message:
            for video in message["videos"]:
                if "uri" in video:
                    videos.append(video["uri"])

        audio = []
        if "audio_files" in message:
            for audio_file in message["audio_files"]:
                if "uri" in audio_file:
                    audio.append(audio_file["uri"])

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
