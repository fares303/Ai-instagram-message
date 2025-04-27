"""
PDF exporter for Instagram conversation data.
"""

import os
import logging
from datetime import datetime
from fpdf import FPDF
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import numpy as np
import tempfile
import re
from PIL import Image
import io
import emoji
import instagram_data_processor.utils as utils

logger = logging.getLogger(__name__)

class ConversationPDF(FPDF):
    """
    Custom PDF class for conversation export with enhanced styling.
    """

    def __init__(self, title, author):
        super().__init__()
        self.title = title
        self.author = author
        self.set_author(author)
        self.set_title(title)
        self.set_margins(15, 15, 15)
        self.set_auto_page_break(True, margin=15)

        # Set default colors (R, G, B)
        self.primary_r, self.primary_g, self.primary_b = 41, 128, 185  # Blue
        self.secondary_r, self.secondary_g, self.secondary_b = 231, 76, 60  # Red
        self.bg_r, self.bg_g, self.bg_b = 245, 245, 245  # Light gray
        self.text_r, self.text_g, self.text_b = 52, 73, 94  # Dark blue-gray

        # Page counter for alternating background colors
        self.page_count = 0

    def header(self):
        # Increment page counter
        self.page_count += 1

        # Add a light background color to header
        self.set_fill_color(self.bg_r, self.bg_g, self.bg_b)
        self.rect(0, 0, 210, 20, 'F')

        # Add a colored line under the header
        self.set_draw_color(self.primary_r, self.primary_g, self.primary_b)
        self.set_line_width(0.5)
        self.line(10, 20, 200, 20)

        # Set font for header
        self.set_font('Arial', 'B', 14)
        self.set_text_color(self.primary_r, self.primary_g, self.primary_b)

        # Title
        self.cell(0, 15, self.title, 0, 1, 'C')

        # Reset text color
        self.set_text_color(self.text_r, self.text_g, self.text_b)

        # Line break
        self.ln(5)

    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-20)

        # Add a light background color to footer
        self.set_fill_color(self.bg_r, self.bg_g, self.bg_b)
        self.rect(0, self.h - 20, 210, 20, 'F')

        # Add a colored line above the footer
        self.set_draw_color(self.primary_r, self.primary_g, self.primary_b)
        self.set_line_width(0.5)
        self.line(10, self.h - 20, 200, self.h - 20)

        # Set font for footer
        self.set_font('Arial', 'I', 8)
        self.set_text_color(self.primary_r, self.primary_g, self.primary_b)

        # Page number
        self.cell(0, 10, f'Page {self.page_no()} | Generated with Instagram Data Processor', 0, 0, 'C')

        # Reset text color
        self.set_text_color(self.text_r, self.text_g, self.text_b)

    def add_message_bubble(self, sender, date_time, content, reactions=None, media_info=None, is_me=False):
        """
        Add a message bubble with styling.

        Args:
            sender (str): Message sender
            date_time (str): Formatted date and time
            content (str): Message content
            reactions (list, optional): List of reactions
            media_info (str, optional): Media information
            is_me (bool): Whether the message is from me
        """
        # Calculate bubble width (80% of page width)
        bubble_width = self.w * 0.8

        # Set alignment and colors based on sender
        if is_me:
            align = 'R'
            bubble_r, bubble_g, bubble_b = self.primary_r, self.primary_g, self.primary_b
            text_r, text_g, text_b = 255, 255, 255  # White
            x_offset = self.w - bubble_width - 15
        else:
            align = 'L'
            bubble_r, bubble_g, bubble_b = self.secondary_r, self.secondary_g, self.secondary_b
            text_r, text_g, text_b = 255, 255, 255  # White
            x_offset = 15

        # Save current position
        x, y = self.get_x(), self.get_y()

        # Check if we need to add a page
        if y > self.h - 40:
            self.add_page()
            y = self.get_y()

        # Draw sender and timestamp
        self.set_font('Arial', 'B', 8)
        self.set_text_color(bubble_r, bubble_g, bubble_b)
        self.set_x(x_offset)
        self.cell(bubble_width, 5, f"{sender} - {date_time}", 0, 1, align)

        # Calculate content height
        self.set_font('Arial', '', 10)
        content_lines = self.get_multi_cell_lines(bubble_width, 5, content)
        content_height = len(content_lines) * 5

        # Add extra height for reactions and media info
        extra_height = 0
        if reactions:
            extra_height += 5
        if media_info:
            extra_height += 5

        # Draw message bubble with gradient-like effect
        # Draw main bubble
        self.set_fill_color(bubble_r, bubble_g, bubble_b)
        self.rect(x_offset, y + 5, bubble_width, content_height + extra_height + 5, 'F', True, 3)

        # Add a lighter shade at the top for a gradient effect
        lighter_r = min(255, bubble_r + 40)
        lighter_g = min(255, bubble_g + 40)
        lighter_b = min(255, bubble_b + 40)
        self.set_fill_color(lighter_r, lighter_g, lighter_b)
        self.rect(x_offset + 2, y + 7, bubble_width - 4, 8, 'F', True, 3)

        # Draw message content
        self.set_text_color(text_r, text_g, text_b)
        self.set_xy(x_offset, y + 7)
        self.multi_cell(bubble_width, 5, content)

        # Draw media info if any
        if media_info:
            self.set_font('Arial', 'I', 8)
            self.set_xy(x_offset, y + 7 + content_height)
            self.cell(bubble_width, 5, media_info, 0, 1, align)

        # Draw reactions if any
        if reactions:
            reaction_y = y + 7 + content_height + (5 if media_info else 0)
            self.set_font('Arial', 'B', 8)
            self.set_xy(x_offset, reaction_y)
            self.cell(bubble_width, 5, reactions, 0, 1, align)

        # Move to position after the bubble
        self.set_y(y + 10 + content_height + extra_height)

        # Add some space between messages
        self.ln(3)

    def get_multi_cell_lines(self, w, h, txt):
        """
        Calculate how many lines a multi_cell will use.

        Args:
            w (float): Width of the cell
            h (float): Height of the cell
            txt (str): Text to calculate

        Returns:
            list: List of lines
        """
        # Store starting position
        x = self.get_x()
        y = self.get_y()

        # Store current font settings
        font_family = self.font_family
        font_style = self.font_style
        font_size = self.font_size_pt

        # Create a temporary PDF to calculate lines
        temp_pdf = FPDF()
        temp_pdf.add_page()
        temp_pdf.set_font(font_family, font_style, font_size)

        # Split text into lines
        lines = []
        words = txt.split(' ')
        line = ""

        for word in words:
            test_line = line + word + " "
            test_width = temp_pdf.get_string_width(test_line)

            if test_width > w:
                lines.append(line)
                line = word + " "
            else:
                line = test_line

        if line:
            lines.append(line)

        return lines


class PDFExporter:
    """
    Export conversation data to a PDF file.
    """

    def __init__(self, output_dir):
        """
        Initialize the PDF exporter.

        Args:
            output_dir (str): Directory to save the output file
        """
        self.output_dir = output_dir
        logger.info(f"Initialized PDF exporter with output directory: {output_dir}")

    def export(self, messages, target_user, my_name, stats=None):
        """
        Export messages to a PDF file.

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
        filename = f"conversation_with_{target_user}_{timestamp}.pdf"
        filepath = os.path.join(self.output_dir, filename)

        try:
            # Initialize PDF
            pdf = ConversationPDF(f"Conversation with {target_user}", my_name)

            # Add cover page
            pdf.add_page()

            # Title with large font
            pdf.set_font('Arial', 'B', 24)
            pdf.set_text_color(pdf.primary_r, pdf.primary_g, pdf.primary_b)
            pdf.cell(0, 20, "Instagram Memory Book", 0, 1, 'C')

            # Subtitle
            pdf.set_font('Arial', 'B', 18)
            pdf.cell(0, 15, f"Conversation with {target_user}", 0, 1, 'C')

            # Add a decorative line
            pdf.set_draw_color(pdf.primary_r, pdf.primary_g, pdf.primary_b)
            pdf.set_line_width(1)
            pdf.line(40, pdf.get_y() + 5, pdf.w - 40, pdf.get_y() + 5)
            pdf.ln(15)

            # Add generation info
            pdf.set_font('Arial', 'I', 12)
            pdf.set_text_color(pdf.text_r, pdf.text_g, pdf.text_b)
            pdf.cell(0, 10, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1, 'C')
            pdf.ln(10)

            # Add a brief description
            pdf.set_font('Arial', '', 12)
            pdf.multi_cell(0, 8, "This memory book contains your Instagram conversation history, including messages, media, and statistics. It's designed to help you preserve and revisit your meaningful conversations.", 0, 'C')
            pdf.ln(20)

            # Add conversation summary
            if stats:
                pdf.set_font('Arial', 'B', 14)
                pdf.cell(0, 10, "Conversation Summary", 0, 1, 'C')
                pdf.ln(5)

                # Create a summary box
                summary_y = pdf.get_y()
                box_width = pdf.w * 0.7
                box_x = (pdf.w - box_width) / 2

                # Draw summary box
                pdf.set_fill_color(245, 245, 245)  # Light gray
                pdf.rect(box_x, summary_y, box_width, 60, 'F')

                # Add summary content
                pdf.set_font('Arial', 'B', 12)
                pdf.set_xy(box_x + 10, summary_y + 10)
                pdf.cell(box_width - 20, 10, f"Total Messages: {stats['total_messages']}", 0, 1, 'L')

                pdf.set_xy(box_x + 10, summary_y + 25)
                pdf.cell(box_width - 20, 10, f"Conversation Period: {stats['first_message_date']} to {stats['last_message_date']}", 0, 1, 'L')

                pdf.set_xy(box_x + 10, summary_y + 40)
                pdf.cell(box_width - 20, 10, f"Duration: {stats['conversation_duration_days']} days", 0, 1, 'L')

            # Add statistics page
            if stats:
                pdf.add_page()

                # Statistics header
                pdf.set_font('Arial', 'B', 18)
                pdf.set_text_color(pdf.primary_r, pdf.primary_g, pdf.primary_b)
                pdf.cell(0, 15, "Conversation Statistics", 0, 1, 'C')
                pdf.ln(5)

                # Reset text color
                pdf.set_text_color(pdf.text_r, pdf.text_g, pdf.text_b)

                # Create a two-column layout for statistics
                col_width = pdf.w / 2 - 20
                left_col_x = 15
                right_col_x = pdf.w / 2 + 5

                # Left column - Message counts
                pdf.set_font('Arial', 'B', 12)
                pdf.set_xy(left_col_x, pdf.get_y())
                pdf.cell(col_width, 10, "Message Counts", 0, 1, 'L')
                pdf.ln(2)

                pdf.set_font('Arial', '', 10)
                y_pos = pdf.get_y()

                # Draw a light background for the stats
                pdf.set_fill_color(245, 245, 245)  # Light gray
                pdf.rect(left_col_x, y_pos, col_width, 70, 'F')

                # Add message count stats
                pdf.set_xy(left_col_x + 5, y_pos + 5)
                pdf.cell(col_width - 10, 8, f"Total messages: {stats['total_messages']}", 0, 1)

                for sender, count in stats['messages_by_sender'].items():
                    pdf.set_x(left_col_x + 5)
                    pdf.cell(col_width - 10, 8, f"From {sender}: {count}", 0, 1)

                pdf.set_x(left_col_x + 5)
                pdf.cell(col_width - 10, 8, f"'Good morning' messages: {stats['good_morning_count']}", 0, 1)

                pdf.set_x(left_col_x + 5)
                pdf.cell(col_width - 10, 8, f"Algerian slang: {stats['algerian_slang_count']}", 0, 1)

                # Right column - Emoji stats
                pdf.set_font('Arial', 'B', 12)
                pdf.set_xy(right_col_x, y_pos - 12)
                pdf.cell(col_width, 10, "Emoji Statistics", 0, 1, 'L')
                pdf.ln(2)

                # Draw a light background for the emoji stats
                pdf.set_fill_color(245, 245, 245)  # Light gray
                pdf.rect(right_col_x, y_pos, col_width, 70, 'F')

                # Add emoji stats
                pdf.set_font('Arial', '', 10)
                pdf.set_xy(right_col_x + 5, y_pos + 5)
                pdf.cell(col_width - 10, 8, f"Total emojis used: {stats['total_emojis']}", 0, 1)

                pdf.set_x(right_col_x + 5)
                pdf.cell(col_width - 10, 8, f"Unique emojis: {stats['unique_emojis_count']}", 0, 1)

                # Top emojis
                if stats['unique_emojis']:
                    pdf.set_x(right_col_x + 5)
                    pdf.cell(col_width - 10, 8, "Top emojis:", 0, 1)

                    # Display up to 10 emojis
                    emojis_to_show = stats['unique_emojis'][:10]
                    emoji_text = " ".join(emojis_to_show)

                    pdf.set_x(right_col_x + 5)
                    pdf.cell(col_width - 10, 8, emoji_text, 0, 1)

                # Add charts if there are enough messages
                if stats['total_messages'] > 10:
                    pdf.ln(80)  # Move down for the chart
                    pdf.set_font('Arial', 'B', 12)
                    pdf.cell(0, 10, "Message Distribution", 0, 1, 'C')

                    # Create a pie chart for message distribution
                    self._add_message_distribution_chart(pdf, stats)

                # Add timeline information
                pdf.ln(10)
                pdf.set_font('Arial', 'B', 12)
                pdf.cell(0, 10, "Conversation Timeline", 0, 1, 'C')

                # Create a timeline box
                timeline_y = pdf.get_y()
                timeline_width = pdf.w * 0.8
                timeline_x = (pdf.w - timeline_width) / 2

                # Draw timeline box
                pdf.set_fill_color(245, 245, 245)  # Light gray
                pdf.rect(timeline_x, timeline_y, timeline_width, 50, 'F')

                # Add timeline content
                pdf.set_font('Arial', '', 10)
                pdf.set_xy(timeline_x + 10, timeline_y + 5)
                pdf.cell(timeline_width - 20, 8, f"First message: {stats['first_message_date']}", 0, 1)

                pdf.set_xy(timeline_x + 10, timeline_y + 15)
                pdf.cell(timeline_width - 20, 8, f"Last message: {stats['last_message_date']}", 0, 1)

                pdf.set_xy(timeline_x + 10, timeline_y + 25)
                pdf.cell(timeline_width - 20, 8, f"Conversation duration: {stats['conversation_duration_days']} days", 0, 1)

                pdf.set_xy(timeline_x + 10, timeline_y + 35)
                pdf.cell(timeline_width - 20, 8, f"Most active day: {stats['most_active_day']} ({stats['most_active_day_count']} messages)", 0, 1)

            # Conversation section
            pdf.add_page()
            pdf.set_font('Arial', 'B', 16)
            pdf.set_text_color(pdf.primary_r, pdf.primary_g, pdf.primary_b)
            pdf.cell(0, 10, "Conversation Messages", 0, 1, 'C')
            pdf.ln(5)

            # Reset text color
            pdf.set_text_color(pdf.text_r, pdf.text_g, pdf.text_b)

            # Set font for messages
            pdf.set_font('Arial', '', 10)

            # Add a date separator for the first message
            current_date = None

            # Write messages
            for msg in messages:
                # Format date and time
                date_str = msg['date']
                time_str = msg['time']
                date_time = f"{time_str}"
                # Fix any broken text in sender name
                sender = utils.fix_broken_text(msg['sender'])

                # Check if we need to add a date separator
                if date_str != current_date:
                    current_date = date_str

                    # Add some space before the date separator
                    pdf.ln(5)

                    # Add date separator
                    pdf.set_font('Arial', 'B', 10)
                    pdf.set_text_color(pdf.text_r, pdf.text_g, pdf.text_b)
                    pdf.set_fill_color(230, 230, 230)  # Light gray
                    pdf.cell(0, 8, f"--- {date_str} ---", 0, 1, 'C', True)
                    pdf.ln(5)

                # Prepare content - sanitize for PDF
                content = msg['content'] if msg['content'] else ""
                # First fix any broken text encoding, then sanitize for PDF
                content = utils.fix_broken_text(content)
                content = utils.sanitize_for_pdf(content)

                # Prepare media info
                media_indicators = []
                if msg['photos']:
                    media_indicators.append(f"[PHOTO: {len(msg['photos'])}]")
                if msg['videos']:
                    media_indicators.append(f"[VIDEO: {len(msg['videos'])}]")
                if msg['audio']:
                    media_indicators.append(f"[AUDIO: {len(msg['audio'])}]")

                # Add emoji count if there are emojis
                if msg['emoji_count'] > 0:
                    media_indicators.append(f"[EMOJIS: {msg['emoji_count']}]")

                media_info = " ".join(media_indicators) if media_indicators else None

                # Prepare reactions
                reaction_str = None
                if msg['reactions']:
                    # Format reactions in a more readable way
                    reaction_parts = []
                    for r in msg['reactions']:
                        reaction_emoji = r['reaction']
                        actor = r['actor']
                        # Format: "Reacted [EMOJI] to your message" or "You reacted [EMOJI]"
                        # Replace emoji with [EMOJI] to avoid font issues
                        if actor == my_name:
                            reaction_parts.append(f"You reacted [EMOJI]")
                        else:
                            reaction_parts.append(f"Reacted [EMOJI]")

                    reaction_str = " | ".join(reaction_parts)

                # Add message bubble
                pdf.add_message_bubble(
                    sender=sender,
                    date_time=date_time,
                    content=content,
                    reactions=reaction_str,
                    media_info=media_info,
                    is_me=(sender == my_name)
                )

            # Save the PDF
            pdf.output(filepath)

            logger.info(f"Exported conversation to PDF file: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Error exporting to PDF file: {str(e)}")
            return None

    def _add_message_distribution_chart(self, pdf, stats):
        """
        Add a pie chart showing message distribution.

        Args:
            pdf (FPDF): PDF object
            stats (dict): Statistics dictionary
        """
        try:
            # Create a temporary file for the chart
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                temp_filename = tmp.name

            # Create the pie chart
            fig, ax = plt.subplots(figsize=(6, 4))

            # Data for the pie chart
            labels = list(stats['messages_by_sender'].keys())
            sizes = list(stats['messages_by_sender'].values())

            # Create pie chart
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
            ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle

            plt.title('Message Distribution')

            # Save the chart to the temporary file
            plt.savefig(temp_filename, bbox_inches='tight')
            plt.close()

            # Add the chart to the PDF
            pdf.image(temp_filename, x=10, w=180)

            # Clean up the temporary file
            os.unlink(temp_filename)

        except Exception as e:
            logger.error(f"Error creating message distribution chart: {str(e)}")
            # Continue without the chart
