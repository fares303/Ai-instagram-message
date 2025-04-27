"""
Sample configuration file for Instagram Data Processor.

Copy this file to instagram_data_processor/config.py and modify as needed.
"""

# User configuration
TARGET_USER = "friend_username"  # The specific user to analyze
MY_NAME = "your_username"  # Your name for statistics

# Path configuration
DATA_ROOT_PATH = "path/to/instagram/data"  # Path to the Instagram data folder
OUTPUT_PATH = "output"  # Path where output files will be saved

# Analysis configuration
GOOD_MORNING_PHRASES = [
    "gm", "good morning", "morning", "bonjour", "ohayo",
    "buenos dias", "guten morgen"
]

# Custom phrases to detect
CUSTOM_PHRASES = [
    "happy birthday", "congratulations", "thank you", "thanks",
    "lol", "haha", "wow", "awesome", "cool", "nice"
]

# Output configuration
DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M:%S"
DATETIME_FORMAT = f"{DATE_FORMAT} {TIME_FORMAT}"

# PDF styling
PDF_TITLE = f"Conversation with {TARGET_USER}"
PDF_AUTHOR = MY_NAME
PDF_FONT = "Helvetica"
PDF_TITLE_SIZE = 24
PDF_HEADING_SIZE = 16
PDF_TEXT_SIZE = 10
PDF_LINE_HEIGHT = 14
