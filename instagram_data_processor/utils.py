"""
Utility functions for the Instagram Data Processor.
"""

import os
import re
import json
import emoji
import logging
from datetime import datetime
import html

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("instagram_processor.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def setup_directories(base_path):
    """
    Create necessary output directories if they don't exist.

    Args:
        base_path (str): Base path for output directories

    Returns:
        dict: Dictionary with paths to different output directories
    """
    directories = {
        'main': base_path,
        'text': os.path.join(base_path, 'text'),
        'pdf': os.path.join(base_path, 'pdf'),
        'excel': os.path.join(base_path, 'excel'),
        'html': os.path.join(base_path, 'html'),
        'media': os.path.join(base_path, 'media'),
        'photos': os.path.join(base_path, 'media', 'photos'),
        'videos': os.path.join(base_path, 'media', 'videos'),
        'audio': os.path.join(base_path, 'media', 'audio'),
    }

    for path in directories.values():
        os.makedirs(path, exist_ok=True)
        logger.info(f"Created directory: {path}")

    return directories

def fix_broken_text(text):
    """
    Fix broken text encoding, especially for Arabic text.
    Uses the latin1 -> utf-8 conversion method as specified.

    Args:
        text (str): Text to fix

    Returns:
        str: Fixed text
    """
    if not text or not isinstance(text, str):
        return ""

    # Always apply the latin1 -> utf-8 conversion to any text that contains
    # common broken encoding characters like ð, Ã, Ø, etc.
    broken_chars = ['ð', 'Ã', 'Ø', 'Ù', 'Ú', 'Û', 'Ü', 'Ý', 'Þ', 'ß', 'à', 'á', 'â', 'ã', 'ä', 'å',
                    'æ', 'ç', 'è', 'é', 'ê', 'ë', 'ì', 'í', 'î', 'ï', 'ñ', 'ò', 'ó', 'ô', 'õ', 'ö',
                    '˜', '™', 'š', '›', 'œ', '§', '©', '¯', '°', '±', '²', '³', '´', 'µ', '¶', '·', '¸']

    # Check if text contains any of the broken characters
    if any(c in text for c in broken_chars):
        try:
            # Apply the latin1 -> utf-8 conversion as specified
            fixed_text = text.encode('latin1').decode('utf-8')
            return fixed_text
        except (UnicodeEncodeError, UnicodeDecodeError):
            # If conversion fails, return original
            return text

    return text

def unescape_text(text):
    """
    Unescape HTML entities and convert Unicode escape sequences in text.
    Also fixes broken text encoding.

    Args:
        text (str): Text to unescape

    Returns:
        str: Unescaped text
    """
    if not text or not isinstance(text, str):
        return ""

    try:
        # First fix any broken encoding
        text = fix_broken_text(text)

        # Unescape HTML entities
        text = html.unescape(text)

        # Handle Unicode escape sequences
        text = text.encode('utf-8').decode('unicode_escape')

        # Handle directional and invisible characters that might affect display
        # but preserve the actual content
        directional_chars = ['\u200e', '\u200f', '\u202a', '\u202b', '\u202c', '\u202d', '\u202e']
        for char in directional_chars:
            text = text.replace(char, '')

        return text
    except Exception as e:
        logger.warning(f"Error unescaping text: {str(e)}")
        return text  # Return original text if all else fails

def convert_timestamp(timestamp_ms):
    """
    Convert millisecond timestamp to readable datetime.

    Args:
        timestamp_ms (int): Timestamp in milliseconds

    Returns:
        datetime: Converted datetime object
    """
    # Convert to seconds if necessary
    timestamp_sec = timestamp_ms / 1000

    # Convert to datetime
    dt = datetime.fromtimestamp(timestamp_sec)

    return dt

def format_datetime(dt, format_str="%Y-%m-%d %H:%M:%S"):
    """
    Format datetime object to string.

    Args:
        dt (datetime): Datetime object
        format_str (str): Format string

    Returns:
        str: Formatted datetime string
    """
    return dt.strftime(format_str)

def count_emojis(text):
    """
    Count emojis in text.

    Args:
        text (str): Text to analyze

    Returns:
        int: Number of emojis
    """
    if not text or not isinstance(text, str):
        return 0

    # Use emoji_list for more accurate counting
    emoji_list = emoji.emoji_list(text)
    return len(emoji_list)

def extract_emojis(text):
    """
    Extract all emojis from text.

    Args:
        text (str): Text to analyze

    Returns:
        list: List of emojis
    """
    if not text or not isinstance(text, str):
        return []

    # Use emoji_list for more accurate extraction
    emoji_data = emoji.emoji_list(text)
    return [e['emoji'] for e in emoji_data]

def contains_phrase(text, phrases, case_sensitive=False):
    """
    Check if text contains any of the given phrases.

    Args:
        text (str): Text to check
        phrases (list): List of phrases to look for
        case_sensitive (bool): Whether to perform case-sensitive matching

    Returns:
        bool: True if any phrase is found, False otherwise
    """
    if not text or not isinstance(text, str):
        return False

    if not case_sensitive:
        text = text.lower()
        phrases = [p.lower() for p in phrases]

    for phrase in phrases:
        if phrase in text:
            return True

    return False

def safe_file_name(name):
    """
    Convert a string to a safe filename.

    Args:
        name (str): String to convert

    Returns:
        str: Safe filename
    """
    # Replace invalid characters with underscore
    return re.sub(r'[\\/*?:"<>|]', "_", name)

def sanitize_for_pdf(text):
    """
    Sanitize text for PDF output, preserving content while making it compatible with PDF.
    Specifically handles problematic characters that cause issues with the FPDF library.

    Args:
        text (str): Text to sanitize

    Returns:
        str: Sanitized text
    """
    if not text or not isinstance(text, str):
        return ""

    try:
        # Replace emojis with [EMOJI] for PDF compatibility
        text = emoji.replace_emoji(text, replace='[EMOJI]')

        # Remove specific problematic characters that cause issues with FPDF
        problematic_chars = [
            '\u2066',  # Left-to-Right Isolate
            '\u2067',  # Right-to-Left Isolate
            '\u2068',  # First Strong Isolate
            '\u2069',  # Pop Directional Isolate
            '\u202A',  # Left-to-Right Embedding
            '\u202B',  # Right-to-Left Embedding
            '\u202C',  # Pop Directional Formatting
            '\u202D',  # Left-to-Right Override
            '\u202E',  # Right-to-Left Override
            '\u061C',  # Arabic Letter Mark
            '\u200E',  # Left-to-Right Mark
            '\u200F',  # Right-to-Left Mark
            '\u200B',  # Zero Width Space
            '\u200C',  # Zero Width Non-Joiner
            '\u200D',  # Zero Width Joiner
            '\uFEFF',  # Zero Width No-Break Space
        ]

        for char in problematic_chars:
            text = text.replace(char, '')

        # For remaining characters, only keep those that can be encoded in latin1
        # which is what standard PDF fonts support
        result = []
        for c in text:
            try:
                # Try to encode to latin1
                c.encode('latin1')
                result.append(c)
            except UnicodeEncodeError:
                # For non-latin1 characters, use a meaningful replacement
                if '\u0600' <= c <= '\u06FF':  # Arabic range
                    if '[Arabic]' not in result[-5:]:  # Avoid repeated tags
                        result.append('[Arabic]')
                elif '\u0400' <= c <= '\u04FF':  # Cyrillic range
                    if '[Cyrillic]' not in result[-5:]:
                        result.append('[Cyrillic]')
                elif '\u0370' <= c <= '\u03FF':  # Greek range
                    if '[Greek]' not in result[-5:]:
                        result.append('[Greek]')
                else:
                    # Replace with a question mark for other characters
                    result.append('?')

        return ''.join(result)
    except Exception as e:
        logger.warning(f"Error sanitizing text for PDF: {str(e)}")
        # Fallback to ASCII-only text
        return ''.join(c for c in text if ord(c) < 128)
