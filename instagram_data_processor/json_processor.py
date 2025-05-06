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

    def __init__(self, data_path, target_user, my_name, is_group_chat=False):
        """
        Initialize the processor.

        Args:
            data_path (str): Path to Instagram data folder
            target_user (str): Name of the target user or group to analyze
            my_name (str): Your name
            is_group_chat (bool): Whether this is a group chat
        """
        self.data_path = data_path
        self.target_user = target_user
        self.my_name = my_name
        self.is_group_chat = is_group_chat
        self.messages = []
        self.participants = set()
        self.conversation_files = []

        logger.info(f"Initialized processor for {'group' if is_group_chat else 'user'}: {target_user}")
        print(f"Initialized processor for {'group' if is_group_chat else 'user'}: {target_user}")

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
                                    # For group chats, we accept all conversation files
                                    if self.is_group_chat:
                                        print(f"Group chat mode: File contains messages, adding to list: {json_path}")
                                        json_files.append(json_path)
                                        break  # Found a valid encoding, no need to try others
                                    # For individual chats, check if the target user is in the participants
                                    elif "participants" in data:
                                        participant_names = [p.get("name", "") for p in data["participants"]]
                                        print(f"File participants: {participant_names}")

                                        # Check if target user is in participants - with special handling for emojis
                                        target_found = False

                                        # Print all participants for debugging
                                        print(f"Checking if target user '{self.target_user}' is in participants: {participant_names}")

                                        # Special handling for emoji usernames
                                        # First, try to fix any broken encoding in participant names
                                        fixed_participant_names = []
                                        for name in participant_names:
                                            try:
                                                # Try to fix broken encoding
                                                fixed_name = utils.fix_broken_text(name)
                                                fixed_participant_names.append(fixed_name)
                                                print(f"Fixed participant name: '{name}' -> '{fixed_name}'")
                                            except Exception as e:
                                                print(f"Error fixing participant name: {e}")
                                                fixed_participant_names.append(name)

                                        # Try different matching approaches for emojis and special characters
                                        for name in fixed_participant_names:
                                            # Direct comparison (case insensitive)
                                            try:
                                                if self.target_user.lower() == name.lower():
                                                    target_found = True
                                                    print(f"Exact match found for target user: {name}")
                                                    break
                                            except Exception as e:
                                                print(f"Error in exact match comparison: {e}")

                                            # Partial match (for emojis and special characters)
                                            try:
                                                if self.target_user.lower() in name.lower() or name.lower() in self.target_user.lower():
                                                    target_found = True
                                                    print(f"Partial match found for target user: {name}")
                                                    break
                                            except Exception as e:
                                                print(f"Error in partial match comparison: {e}")

                                            # Character by character comparison (for emoji issues)
                                            try:
                                                if len(self.target_user) > 0 and len(name) > 0:
                                                    # If first few characters match, consider it a match
                                                    first_chars_target = self.target_user[:min(3, len(self.target_user))].lower()
                                                    first_chars_name = name[:min(3, len(name))].lower()
                                                    if first_chars_target == first_chars_name:
                                                        target_found = True
                                                        print(f"First characters match for target user: {name}")
                                                        break
                                            except Exception as e:
                                                print(f"Error in character comparison: {e}")

                                        # If all else fails, just accept the file if it has the right structure
                                        if not target_found and "messages" in data and len(data["messages"]) > 0:
                                            print(f"No match found, but file has messages. Adding file: {json_path}")
                                            target_found = True

                                        if target_found:
                                            print(f"Found target user {self.target_user} in participants, adding file: {json_path}")
                                            json_files.append(json_path)
                                            break  # Found a valid encoding, no need to try others
                                        else:
                                            print(f"Target user {self.target_user} not found in participants, skipping file")
                                    else:
                                        # If no participants field, add the file anyway
                                        print(f"No participants field found, adding file: {json_path}")
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

    def _extract_emojis(self, text):
        """
        Extract emojis from text.

        Args:
            text (str): Text to extract emojis from

        Returns:
            list: List of emojis found in the text
        """
        if not text:
            return []

        # Use the utils function to extract emojis
        return utils.extract_emojis(text)

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

        # Print the entire message for debugging
        print(f"Full message structure: {json.dumps(message, indent=2, default=str)}")

        # Check for photos with improved error handling
        photos = []

        # Check standard Instagram format
        if "photos" in message and isinstance(message["photos"], list):
            print(f"Found photos array with {len(message['photos'])} items")
            for photo in message["photos"]:
                if isinstance(photo, dict):
                    print(f"Photo item: {photo}")
                    if "uri" in photo:
                        photos.append(photo["uri"])
                        print(f"Added photo URI: {photo['uri']}")
                    elif "path" in photo:
                        photos.append(photo["path"])
                        print(f"Added photo path: {photo['path']}")
                    elif "filename" in photo:
                        photos.append(photo["filename"])
                        print(f"Added photo filename: {photo['filename']}")

        # Check for photo_data field
        if "photo_data" in message and isinstance(message["photo_data"], list):
            print(f"Found photo_data array with {len(message['photo_data'])} items")
            for photo in message["photo_data"]:
                if isinstance(photo, dict):
                    print(f"Photo data item: {photo}")
                    if "uri" in photo:
                        photos.append(photo["uri"])
                        print(f"Added photo URI from photo_data: {photo['uri']}")
                    elif "path" in photo:
                        photos.append(photo["path"])
                        print(f"Added photo path from photo_data: {photo['path']}")

        # Check for image field
        if "image" in message and isinstance(message["image"], dict):
            print(f"Found image field: {message['image']}")
            if "uri" in message["image"]:
                photos.append(message["image"]["uri"])
                print(f"Added photo URI from image field: {message['image']['uri']}")

        # Check alternative formats - attachments
        if "attachments" in message and isinstance(message["attachments"], list):
            print(f"Found attachments array with {len(message['attachments'])} items")
            for attachment in message["attachments"]:
                if isinstance(attachment, dict):
                    print(f"Attachment item: {attachment}")
                    # Check for photos in attachments
                    if attachment.get("type") == "photo" or "photo" in str(attachment).lower() or "image" in str(attachment).lower():
                        print(f"Found photo attachment: {attachment}")
                        if "uri" in attachment:
                            photos.append(attachment["uri"])
                            print(f"Added photo URI from attachment: {attachment['uri']}")
                        elif "path" in attachment:
                            photos.append(attachment["path"])
                            print(f"Added photo path from attachment: {attachment['path']}")
                        elif "url" in attachment:
                            photos.append(attachment["url"])
                            print(f"Added photo URL from attachment: {attachment['url']}")
                        elif "filename" in attachment:
                            photos.append(attachment["filename"])
                            print(f"Added photo filename from attachment: {attachment['filename']}")
                        elif "data" in attachment and isinstance(attachment["data"], dict):
                            print(f"Attachment data: {attachment['data']}")
                            if "uri" in attachment["data"]:
                                photos.append(attachment["data"]["uri"])
                                print(f"Added photo URI from attachment data: {attachment['data']['uri']}")
                            elif "url" in attachment["data"]:
                                photos.append(attachment["data"]["url"])
                                print(f"Added photo URL from attachment data: {attachment['data']['url']}")

        # Check for files field
        if "files" in message and isinstance(message["files"], list):
            print(f"Found files array with {len(message['files'])} items")
            for file_item in message["files"]:
                if isinstance(file_item, dict):
                    print(f"File item: {file_item}")
                    file_type = file_item.get("file_type", "").lower()
                    if "image" in file_type or "photo" in file_type or file_type.endswith(('.jpg', '.jpeg', '.png', '.gif')):
                        if "uri" in file_item:
                            photos.append(file_item["uri"])
                            print(f"Added photo URI from files: {file_item['uri']}")
                        elif "path" in file_item:
                            photos.append(file_item["path"])
                            print(f"Added photo path from files: {file_item['path']}")
                        elif "url" in file_item:
                            photos.append(file_item["url"])
                            print(f"Added photo URL from files: {file_item['url']}")
                        elif "filename" in file_item:
                            photos.append(file_item["filename"])
                            print(f"Added photo filename from files: {file_item['filename']}")

        # Check for videos with improved error handling
        videos = []

        # Check standard Instagram format
        if "videos" in message and isinstance(message["videos"], list):
            print(f"Found videos array with {len(message['videos'])} items")
            for video in message["videos"]:
                if isinstance(video, dict):
                    print(f"Video item: {video}")
                    if "uri" in video:
                        videos.append(video["uri"])
                        print(f"Added video URI: {video['uri']}")
                    elif "path" in video:
                        videos.append(video["path"])
                        print(f"Added video path: {video['path']}")
                    elif "filename" in video:
                        videos.append(video["filename"])
                        print(f"Added video filename: {video['filename']}")

        # Check for video_data field
        if "video_data" in message and isinstance(message["video_data"], list):
            print(f"Found video_data array with {len(message['video_data'])} items")
            for video in message["video_data"]:
                if isinstance(video, dict):
                    print(f"Video data item: {video}")
                    if "uri" in video:
                        videos.append(video["uri"])
                        print(f"Added video URI from video_data: {video['uri']}")
                    elif "path" in video:
                        videos.append(video["path"])
                        print(f"Added video path from video_data: {video['path']}")

        # Check alternative formats - attachments
        if "attachments" in message and isinstance(message["attachments"], list):
            for attachment in message["attachments"]:
                if isinstance(attachment, dict):
                    # Check for videos in attachments
                    if attachment.get("type") == "video" or "video" in str(attachment).lower():
                        print(f"Found video attachment: {attachment}")
                        if "uri" in attachment:
                            videos.append(attachment["uri"])
                            print(f"Added video URI from attachment: {attachment['uri']}")
                        elif "path" in attachment:
                            videos.append(attachment["path"])
                            print(f"Added video path from attachment: {attachment['path']}")
                        elif "url" in attachment:
                            videos.append(attachment["url"])
                            print(f"Added video URL from attachment: {attachment['url']}")
                        elif "filename" in attachment:
                            videos.append(attachment["filename"])
                            print(f"Added video filename from attachment: {attachment['filename']}")
                        elif "data" in attachment and isinstance(attachment["data"], dict):
                            print(f"Video attachment data: {attachment['data']}")
                            if "uri" in attachment["data"]:
                                videos.append(attachment["data"]["uri"])
                                print(f"Added video URI from attachment data: {attachment['data']['uri']}")
                            elif "url" in attachment["data"]:
                                videos.append(attachment["data"]["url"])
                                print(f"Added video URL from attachment data: {attachment['data']['url']}")

        # Check for files field for videos
        if "files" in message and isinstance(message["files"], list):
            for file_item in message["files"]:
                if isinstance(file_item, dict):
                    file_type = file_item.get("file_type", "").lower()
                    if "video" in file_type or file_type.endswith(('.mp4', '.mov', '.avi', '.wmv')):
                        print(f"Found video file: {file_item}")
                        if "uri" in file_item:
                            videos.append(file_item["uri"])
                            print(f"Added video URI from files: {file_item['uri']}")
                        elif "path" in file_item:
                            videos.append(file_item["path"])
                            print(f"Added video path from files: {file_item['path']}")
                        elif "url" in file_item:
                            videos.append(file_item["url"])
                            print(f"Added video URL from files: {file_item['url']}")
                        elif "filename" in file_item:
                            videos.append(file_item["filename"])
                            print(f"Added video filename from files: {file_item['filename']}")

        # Check for audio with improved error handling
        audio = []

        # Check standard Instagram format
        if "audio_files" in message and isinstance(message["audio_files"], list):
            print(f"Found audio_files array with {len(message['audio_files'])} items")
            for audio_file in message["audio_files"]:
                if isinstance(audio_file, dict):
                    print(f"Audio item: {audio_file}")
                    if "uri" in audio_file:
                        audio.append(audio_file["uri"])
                        print(f"Added audio URI: {audio_file['uri']}")
                    elif "path" in audio_file:
                        audio.append(audio_file["path"])
                        print(f"Added audio path: {audio_file['path']}")
                    elif "filename" in audio_file:
                        audio.append(audio_file["filename"])
                        print(f"Added audio filename: {audio_file['filename']}")

        # Check for audio_data field
        if "audio_data" in message and isinstance(message["audio_data"], list):
            print(f"Found audio_data array with {len(message['audio_data'])} items")
            for audio_item in message["audio_data"]:
                if isinstance(audio_item, dict):
                    print(f"Audio data item: {audio_item}")
                    if "uri" in audio_item:
                        audio.append(audio_item["uri"])
                        print(f"Added audio URI from audio_data: {audio_item['uri']}")
                    elif "path" in audio_item:
                        audio.append(audio_item["path"])
                        print(f"Added audio path from audio_data: {audio_item['path']}")

        # Check alternative formats - attachments
        if "attachments" in message and isinstance(message["attachments"], list):
            for attachment in message["attachments"]:
                if isinstance(attachment, dict):
                    # Check for audio in attachments
                    if attachment.get("type") == "audio" or "audio" in str(attachment).lower() or "voice" in str(attachment).lower():
                        print(f"Found audio attachment: {attachment}")
                        if "uri" in attachment:
                            audio.append(attachment["uri"])
                            print(f"Added audio URI from attachment: {attachment['uri']}")
                        elif "path" in attachment:
                            audio.append(attachment["path"])
                            print(f"Added audio path from attachment: {attachment['path']}")
                        elif "url" in attachment:
                            audio.append(attachment["url"])
                            print(f"Added audio URL from attachment: {attachment['url']}")
                        elif "filename" in attachment:
                            audio.append(attachment["filename"])
                            print(f"Added audio filename from attachment: {attachment['filename']}")
                        elif "data" in attachment and isinstance(attachment["data"], dict):
                            print(f"Audio attachment data: {attachment['data']}")
                            if "uri" in attachment["data"]:
                                audio.append(attachment["data"]["uri"])
                                print(f"Added audio URI from attachment data: {attachment['data']['uri']}")
                            elif "url" in attachment["data"]:
                                audio.append(attachment["data"]["url"])
                                print(f"Added audio URL from attachment data: {attachment['data']['url']}")

        # Check for files field for audio
        if "files" in message and isinstance(message["files"], list):
            for file_item in message["files"]:
                if isinstance(file_item, dict):
                    file_type = file_item.get("file_type", "").lower()
                    if "audio" in file_type or "voice" in file_type or file_type.endswith(('.mp3', '.wav', '.ogg', '.m4a')):
                        print(f"Found audio file: {file_item}")
                        if "uri" in file_item:
                            audio.append(file_item["uri"])
                            print(f"Added audio URI from files: {file_item['uri']}")
                        elif "path" in file_item:
                            audio.append(file_item["path"])
                            print(f"Added audio path from files: {file_item['path']}")
                        elif "url" in file_item:
                            audio.append(file_item["url"])
                            print(f"Added audio URL from files: {file_item['url']}")
                        elif "filename" in file_item:
                            audio.append(file_item["filename"])
                            print(f"Added audio filename from files: {file_item['filename']}")

        # Check for voice_messages field
        if "voice_messages" in message and isinstance(message["voice_messages"], list):
            print(f"Found voice_messages array with {len(message['voice_messages'])} items")
            for voice_msg in message["voice_messages"]:
                if isinstance(voice_msg, dict):
                    print(f"Voice message item: {voice_msg}")
                    if "uri" in voice_msg:
                        audio.append(voice_msg["uri"])
                        print(f"Added audio URI from voice_messages: {voice_msg['uri']}")
                    elif "path" in voice_msg:
                        audio.append(voice_msg["path"])
                        print(f"Added audio path from voice_messages: {voice_msg['path']}")
                    elif "url" in voice_msg:
                        audio.append(voice_msg["url"])
                        print(f"Added audio URL from voice_messages: {voice_msg['url']}")
                    elif "filename" in voice_msg:
                        audio.append(voice_msg["filename"])
                        print(f"Added audio filename from voice_messages: {voice_msg['filename']}")

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
            "mentions_target_name": False,  # Will be updated below
            "has_custom_phrase": any(utils.contains_phrase(content, [phrase]) for phrase in config.CUSTOM_PHRASES),
            "is_from_me": sender.lower() == self.my_name.lower(),
            "is_from_target": False  # Will be updated below
        }

        # For group chats, we need to handle mentions differently
        if self.is_group_chat:
            # In group chats, check if the message mentions any participant
            processed_message["mentions_target_name"] = False
            processed_message["is_from_target"] = False

            # Add all participants to the message for group chat analysis
            processed_message["all_participants"] = list(self.participants)
        else:
            # For individual chats, check if the message mentions the target user
            # Special handling for emojis in usernames
            mentions_target = False
            if content:
                # Try different matching approaches for target user mentions
                if self.target_user.lower() in content.lower():
                    mentions_target = True
                # For emoji usernames, check if first few characters match
                elif len(self.target_user) > 0:
                    first_chars = self.target_user[:min(3, len(self.target_user))].lower()
                    if first_chars in content.lower():
                        mentions_target = True

            processed_message["mentions_target_name"] = mentions_target

            # Check if message is from target user - with special handling for emojis
            is_from_target = False

            # Direct comparison (case insensitive)
            if sender.lower() == self.target_user.lower():
                is_from_target = True
            # Partial match (for emojis and special characters)
            elif self.target_user.lower() in sender.lower() or sender.lower() in self.target_user.lower():
                is_from_target = True
            # Character by character comparison (for emoji issues)
            elif len(self.target_user) > 0 and len(sender) > 0:
                # If first few characters match, consider it a match
                first_chars_target = self.target_user[:min(3, len(self.target_user))].lower()
                first_chars_sender = sender[:min(3, len(sender))].lower()
                if first_chars_target == first_chars_sender:
                    is_from_target = True

            processed_message["is_from_target"] = is_from_target

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

        # Count messages by date for timeline chart
        messages_by_date = {}
        for msg in self.messages:
            date = msg["date"]
            messages_by_date[date] = messages_by_date.get(date, 0) + 1

        # Count messages by hour for activity chart
        messages_by_hour = {}
        for msg in self.messages:
            try:
                # Extract hour from timestamp
                if isinstance(msg["timestamp"], datetime):
                    hour = msg["timestamp"].hour
                    messages_by_hour[hour] = messages_by_hour.get(hour, 0) + 1
            except Exception as e:
                print(f"Error extracting hour from timestamp: {e}")

        # Count emoji usage for emoji chart
        emoji_counts = {}
        for msg in self.messages:
            for emoji in msg["emojis"]:
                emoji_counts[emoji] = emoji_counts.get(emoji, 0) + 1

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
            "is_group_chat": self.is_group_chat,
            "participants_count": len(self.participants),
            "participants": list(self.participants),
            # Add chart data
            "messages_by_date": messages_by_date,
            "messages_by_hour": messages_by_hour,
            "emoji_counts": emoji_counts
        }

        # Add group chat specific statistics
        if self.is_group_chat:
            # Calculate who talks to whom
            interactions = {}
            for participant in self.participants:
                interactions[participant] = {}
                for other in self.participants:
                    if participant != other:
                        interactions[participant][other] = 0

            # Count messages where one participant mentions another
            for msg in self.messages:
                sender = msg["sender"]
                content = msg["content"].lower() if msg["content"] else ""

                for participant in self.participants:
                    if sender != participant and participant.lower() in content:
                        if sender in interactions and participant in interactions[sender]:
                            interactions[sender][participant] += 1

            stats["participant_interactions"] = interactions

            # Find most active participants
            sorted_participants = sorted(
                messages_by_sender.items(),
                key=lambda x: x[1],
                reverse=True
            )
            stats["most_active_participants"] = sorted_participants

        return stats
