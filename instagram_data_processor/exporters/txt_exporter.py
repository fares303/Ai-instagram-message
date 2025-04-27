"""
Text file exporter for Instagram conversation data.
"""

import os
import logging
from datetime import datetime
import instagram_data_processor.utils as utils

logger = logging.getLogger(__name__)

class TxtExporter:
    """
    Export conversation data to a text file.
    """

    def __init__(self, output_dir):
        """
        Initialize the TXT exporter.

        Args:
            output_dir (str): Directory to save the output file
        """
        self.output_dir = output_dir
        logger.info(f"Initialized TXT exporter with output directory: {output_dir}")

    def export(self, messages, target_user, my_name, stats=None):
        """
        Export messages to a text file.

        Args:
            messages (list): List of processed messages
            target_user (str): Name of the target user
            my_name (str): Your name
            stats (dict, optional): Statistics to include

        Returns:
            str: Path to the exported file
        """
        if not messages:
            logger.warning("No messages to export")
            return None

        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"conversation_with_{target_user}_{timestamp}.txt"
        filepath = os.path.join(self.output_dir, filename)

        try:
            with open(filepath, 'w', encoding='utf-8') as file:
                # Write header
                file.write(f"Conversation with {target_user}\n")
                file.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                file.write("=" * 80 + "\n\n")

                # Write statistics if provided
                if stats:
                    file.write("CONVERSATION STATISTICS\n")
                    file.write("-" * 80 + "\n")
                    file.write(f"Total messages: {stats['total_messages']}\n")

                    for sender, count in stats['messages_by_sender'].items():
                        file.write(f"Messages from {sender}: {count}\n")

                    file.write(f"Total emojis used: {stats['total_emojis']}\n")
                    file.write(f"Unique emojis used: {stats['unique_emojis_count']}\n")
                    file.write(f"'Good morning' messages: {stats['good_morning_count']}\n")
                    file.write(f"Mentions of '{my_name}': {stats['my_name_mentions']}\n")
                    file.write(f"Mentions of '{target_user}': {stats['target_name_mentions']}\n")
                    file.write(f"Active conversation days: {stats['active_conversation_days']}\n")
                    file.write(f"First message date: {stats['first_message_date']}\n")
                    file.write(f"Last message date: {stats['last_message_date']}\n")
                    file.write(f"Conversation duration: {stats['conversation_duration_days']} days\n")
                    file.write(f"Algerian slang expressions: {stats['algerian_slang_count']}\n")
                    file.write(f"Most active day: {stats['most_active_day']} ({stats['most_active_day_count']} messages)\n")
                    file.write("\n" + "=" * 80 + "\n\n")

                # Write messages
                file.write("CONVERSATION\n")
                file.write("-" * 80 + "\n\n")

                for msg in messages:
                    # Format: [Date] [Time] [Sender]: [Content]
                    date_time = f"[{msg['date']} {msg['time']}]"
                    # Fix any broken text in sender name
                    sender = utils.fix_broken_text(msg['sender'])
                    # Fix any broken text in content
                    content = msg['content'] if msg['content'] else ""
                    content = utils.fix_broken_text(content)

                    # Add media indicators
                    media_indicators = []
                    if msg['photos']:
                        media_indicators.append(f"[{len(msg['photos'])} photo(s)]")
                    if msg['videos']:
                        media_indicators.append(f"[{len(msg['videos'])} video(s)]")
                    if msg['audio']:
                        media_indicators.append(f"[{len(msg['audio'])} audio(s)]")

                    # Add emoji count if there are emojis
                    if msg['emoji_count'] > 0:
                        emoji_list = ", ".join(msg['emojis'])
                        media_indicators.append(f"[{msg['emoji_count']} emoji(s): {emoji_list}]")

                    media_str = " ".join(media_indicators)

                    # Format the line
                    line = f"{date_time} {sender}: {content}"
                    if media_str:
                        line += f" {media_str}"

                    file.write(line + "\n")

                    # Add reactions if any
                    if msg['reactions']:
                        reaction_str = "Reactions: " + ", ".join(
                            f"{r['reaction']} by {r['actor']}" for r in msg['reactions']
                        )
                        file.write(f"    {reaction_str}\n")

                    # Add a blank line for readability
                    file.write("\n")

            logger.info(f"Exported conversation to TXT file: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Error exporting to TXT file: {str(e)}")
            return None
